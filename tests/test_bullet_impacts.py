import array
from pathlib import Path
import unittest
import wave
from omacontra.resources import ASSETS
from omacontra.stages.reaper.combat import Fight
from omacontra.stages.harbor.tidebreaker import Tidebreaker
from omacontra.stages.dragon.foundry import Foundry
from omacontra.audio.reaper_audio import ReaperEffects

class BulletImpactTests(unittest.TestCase):
    def test_actual_reaper_targets_have_different_cues_and_misses_stay_silent(self):
        f=Fight()
        self.assertFalse(f.hit_target(0,0,10,0,1));self.assertFalse(f.sfx_events)
        for role,event in [('eye','eye_hit'),('raven','raven_hit')]:
            x,y=f.node_center(role)
            self.assertTrue(f.hit_target(x-1,y,x+1,y,1))
            self.assertIn(event,f.sfx_events)
        x,y=f.body
        f.hit_target(x-1,y,x+1,y,1);self.assertIn('armor',f.sfx_events)
        for _ in range(20):f.hit_target(x-1,y,x+1,y,1)
        self.assertEqual(f.sfx_events.count('armor'),21)
        f.clock+=.2;f.hit_target(x-1,y,x+1,y,1)
        self.assertEqual(f.sfx_events.count('armor'),22)

    def test_guardian_suit_and_shell_and_dragon_core_have_material_feedback(self):
        f=Tidebreaker();f.advance_guardian()
        for actor in f.guardians:
            x,y=actor.core(f.floor);f.hit_guardians(x-1,y,x+1,y,1)
            self.assertIn('guardian_hit' if actor.kind==1 else 'suit_hit',f.sfx_events)
        f=Foundry();x,y=f.mount_target
        f.hit_target(x-1,y,x+1,y,1);self.assertIn('core_hit',f.sfx_events)
        f.mount_hp=0;x=f.boss_x
        f.hit_target(x-1,400,x+1,400,1);self.assertIn('scale_hit',f.sfx_events)

    def test_metal_tails_finish_before_the_next_round(self):
        for bank,name in [('reaper','armor'),('reaper','eye_hit'),('chase','impact'),('chase','drone_hit'),('tide','suit_hit')]:
            with wave.open(str(ASSETS/'audio'/bank/f'{name}.wav')) as f:
                self.assertLess(f.getnframes()/f.getframerate(),.08)

    def test_material_takes_are_distinct_quiet_and_end_cleanly(self):
        banks={'reaper':['armor','impact','eye_hit','raven_hit'],
               'chase':['armor','impact','heart_hit','drone_hit'],
               'tide':['guardian_hit','suit_hit','water_hit'],
               'wyrm':['core_hit','scale_hit','laser_hit'],
               'finale':['laser_hit','node_hit']}
        for bank,names in banks.items():
            mixer=ReaperEffects(ASSETS/'audio'/bank)
            for name in names:
                takes=[]
                for i in range(3):
                    path=mixer.audio/(f'{name}.wav' if i==0 else f'variants/{name}-{i}.wav')
                    with wave.open(str(path)) as f:
                        self.assertEqual((f.getframerate(),f.getnchannels(),f.getsampwidth()),(44100,1,2))
                        raw=f.readframes(f.getnframes());pcm=array.array('h',raw);takes.append(raw)
                    self.assertEqual(pcm[0],0);self.assertEqual(pcm[-1],0)
                    self.assertLess(max(map(abs,pcm)),600)
                    self.assertGreater(max(map(abs,pcm)),300)
                    mixer.trigger(name)
                self.assertEqual(len(set(takes)),3)
            self.assertFalse(mixer.failed)

import array
import unittest
import wave
from unittest.mock import Mock
from omacontra.stages.harbor.tidebreaker import Tidebreaker
from omacontra.audio.tide_audio import TideEffects, AUDIO
from omacontra.audio.weapon_audio import WeaponAudio

class TideAudioTests(unittest.TestCase):
    def test_surge_is_one_event_and_damage_is_throttled(self):
        f=Tidebreaker();f.spawn_wave('surge')
        self.assertEqual(f.sfx_events,['surge'])
        x,y=f.core
        for _ in range(10):f.hit_target(x-10,y,x+10,y,1)
        self.assertEqual(f.sfx_events.count('water_hit'),1)

    def test_guardian_fire_death_and_survivor_have_distinct_cues(self):
        f=Tidebreaker();f.advance_guardian()
        for a in f.guardians:a.attack='volley';a.queue=[(0,0)]
        f.guardian_step(.02)
        self.assertIn('pistol',f.sfx_events);self.assertIn('orbit',f.sfx_events)
        a=f.guardians[0];x,y=a.core(f.floor)
        f.hit_guardians(x-10,y,x+10,y,999)
        self.assertIn('coat_death',f.sfx_events);self.assertIn('rage_orbit',f.sfx_events)

    def test_bank_selected_and_pause_discards_pending_effects(self):
        s=WeaponAudio();s.device=7;s.lib=Mock();s.burst=bytes(9000)
        s.lib.SDL_GetQueuedAudioSize.return_value=0;s.lib.SDL_QueueAudio.return_value=0
        f=Tidebreaker();f.sound('surge');s.update(f,False,True)
        self.assertIsInstance(s.effects,TideEffects);self.assertTrue(s.effects.voices)
        f.sound('wave_death');s.update(f,False,False)
        self.assertFalse(s.effects.voices);self.assertFalse(f.sfx_events)

    def test_quiet_nonempty_assets_and_soft_edges(self):
        paths=list(AUDIO.glob('*.wav'));self.assertEqual(len(paths),31)
        for path in paths:
            with self.subTest(path=path.name),wave.open(str(path)) as f:
                self.assertEqual((f.getframerate(),f.getnchannels(),f.getsampwidth()),(44100,1,2))
                pcm=array.array('h',f.readframes(f.getnframes()))
                self.assertGreater(max(map(abs,pcm)),0);self.assertLess(max(map(abs,pcm)),1500)
                self.assertLess(abs(pcm[0]),3);self.assertLess(abs(pcm[-1]),3)

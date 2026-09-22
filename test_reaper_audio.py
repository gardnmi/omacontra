import array
import unittest
import wave
from types import SimpleNamespace
from unittest.mock import Mock
from combat import Fight
from foundry import Foundry
from reaper_audio import ReaperEffects,AUDIO,LIMIT
from weapon_audio import WeaponAudio

class ReaperAudioTests(unittest.TestCase):
    def test_actual_attacks_emit_once_per_launch_not_per_projectile(self):
        f=Fight(7)
        f.fire_volley('aimed');f.fire_volley('raven');f.launch_wave('dash')
        self.assertEqual(f.sfx_events,['skull','raven','sweep'])
        self.assertGreater(len(f.shots),len(f.sfx_events))
        f.nodes={'eye':0,'raven':0};f.sfx_events.clear()
        f.fire_volley('aimed');f.fire_volley('raven')
        self.assertEqual(f.sfx_events,[])

    def test_damage_hits_breaks_and_exposure(self):
        f=Fight(7)
        for role in ('eye','raven'):
            x,y=f.node_center(role)
            self.assertTrue(f.hit_target(x,y,x,y,999))
        self.assertEqual(f.sfx_events.count('eye_break'),1)
        self.assertEqual(f.sfx_events.count('raven_break'),1)
        self.assertEqual(f.sfx_events.count('expose'),1)
        f.sfx_events.clear();x,y=f.body
        f.hit_target(x,y,x,y,999)
        self.assertEqual(f.state,'dying');self.assertIn('rupture',f.sfx_events)
        for _ in range(150):f.step(.04)
        self.assertEqual(f.state,'won')
        self.assertEqual(f.sfx_events.count('defeat'),1)
        self.assertIn('death_blast',f.sfx_events)

    def test_damage_and_movement_only_when_action_occurs(self):
        f=Fight(7);f.invuln=0;f.hurt();f.hurt()
        self.assertEqual(f.sfx_events,['hurt'])
        f=Fight(7);f.step(.02,jump=True);f.step(.02,jump=True)
        self.assertEqual(f.sfx_events.count('jump'),1)
        f.step(.02,slide_pressed=True)
        self.assertEqual(f.sfx_events.count('dash'),1)
        f.invuln=0;f.hp=1;f.hurt()
        self.assertEqual(f.sfx_events[-1],'player_death')

    def test_impact_throttling_bounded_queue_and_other_level_scope(self):
        f=Fight(7)
        for _ in range(100):f.sound('impact',.14)
        self.assertEqual(f.sfx_events,['impact'])
        f.clock=.15;f.sound('impact',.14)
        self.assertEqual(len(f.sfx_events),2)
        for _ in range(100):f.sound('jump')
        self.assertEqual(len(f.sfx_events),32)
        class SilentEncounter(Fight):pass
        other=SilentEncounter();other.sound('jump');other.invuln=0;other.hurt()
        self.assertEqual(other.sfx_events,[])

    def test_effects_mix_with_gun_but_do_not_depend_on_firing(self):
        s=WeaponAudio();s.device=7;s.lib=Mock();s.burst=bytes(9000)
        s.lib.SDL_GetQueuedAudioSize.return_value=0;s.lib.SDL_QueueAudio.return_value=0
        f=SimpleNamespace(machine_shots=0,sfx_events=['hurt'])
        s.update(f,False,True)
        self.assertEqual(f.sfx_events,[])
        self.assertTrue(any(s.lib.SDL_QueueAudio.call_args.args[1]))
        self.assertTrue(s.effects.voices)
        f.sfx_events=['sweep'];s.update(f,False,False)
        self.assertFalse(s.effects.voices);self.assertEqual(f.sfx_events,[])
        s.lib.SDL_QueueAudio.reset_mock();s.update(f,False,True)
        s.lib.SDL_QueueAudio.assert_not_called()

    def test_retry_discards_previous_encounter_effect_tails(self):
        s=WeaponAudio();s.device=7;s.lib=Mock();s.burst=bytes(9000)
        s.lib.SDL_GetQueuedAudioSize.return_value=0;s.lib.SDL_QueueAudio.return_value=0
        f=SimpleNamespace(machine_shots=0,sfx_events=['rupture'])
        s.update(f,False,True);self.assertTrue(s.effects.voices)
        s.update(SimpleNamespace(machine_shots=0,sfx_events=[]),False,True)
        self.assertFalse(s.effects.voices)
        s.lib.SDL_ClearQueuedAudio.assert_called_with(7)

    def test_mix_has_bounded_polyphony_and_peak(self):
        m=ReaperEffects()
        for name in ('jump','land','slide','dash','impact','armor','rupture'):
            m.trigger(name)
        self.assertEqual(len(m.voices),6)
        self.assertIn('rupture',[v[0] for v in m.voices])
        m.trigger('rupture')
        self.assertEqual(sum(v[0]=='rupture' for v in m.voices),1)
        output=array.array('h',m.mix(array.array('h',[32000]*882).tobytes()))
        self.assertLessEqual(max(map(abs,output)),LIMIT)
        for _ in range(220):m.mix(bytes(1764))
        self.assertFalse(m.voices)

    def test_all_assets_are_soft_valid_pcm(self):
        paths=list(AUDIO.glob('*.wav'));self.assertEqual(len(paths),21)
        for p in paths:
            with wave.open(str(p)) as w:
                self.assertEqual((w.getframerate(),w.getnchannels(),w.getsampwidth()),(44100,1,2))
                pcm=array.array('h',w.readframes(w.getnframes()))
                self.assertGreater(max(map(abs,pcm)),0)
                self.assertLess(max(map(abs,pcm)),1400)
                self.assertLess(abs(pcm[0]),2);self.assertLess(abs(pcm[-1]),2)

    def test_repeated_effects_cycle_distinct_takes_without_stacking(self):
        m=ReaperEffects();takes=[]
        for _ in range(4):
            m.trigger('eye_break');takes.append(m.mix(bytes(17640)))
            self.assertEqual(len(m.voices),1)
        self.assertEqual(len(set(takes[:3])),3)
        self.assertEqual(takes[0],takes[3])

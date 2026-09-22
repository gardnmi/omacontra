import array
import unittest
import wave
from unittest.mock import Mock
from omacontra.stages.highway.chase import Chase
from omacontra.stages.reaper.combat import Fight, Bullet
from omacontra.stages.highway import chase_robot
from omacontra.audio.chase_audio import ChaseEffects, AUDIO
from omacontra.audio.weapon_audio import WeaponAudio

class ChaseAudioTests(unittest.TestCase):
    def test_volley_one_sound_and_disabled_hardware_stays_silent(self):
        f=Chase();f.attack('spread')
        self.assertEqual(f.sfx_events,['rockets']);self.assertEqual(len(f.shots),3)
        f.parts[1]=0;f.sfx_events.clear();f.attack('mortar');f.attack('spread')
        self.assertEqual(f.sfx_events,[])
        f.attack('drones');self.assertEqual(f.sfx_events,[])

    def test_boost_takeoff_and_landing_are_action_events(self):
        f=Chase();f.next_ramp=999;f.attack_timer=999;f.reinforce_at=999
        f.step(.02,jump=True,slide=True)
        for _ in range(70):f.step(.02,jump=True,slide=True)
        self.assertEqual(f.sfx_events.count('boost'),1)
        self.assertEqual(f.sfx_events.count('takeoff'),1)
        self.assertEqual(f.sfx_events.count('landing'),1)

    def test_transformation_cues_match_art_timing(self):
        f=Chase();f.detach_trailer();self.assertEqual(f.sfx_events,['truck_break'])
        for _ in range(16):f.step(.04)
        self.assertNotIn('unfold',f.sfx_events)
        f.step(.04);self.assertIn('unfold',f.sfx_events)
        while f.transform_age<2.48:f.step(.04)
        self.assertNotIn('lock',f.sfx_events)
        f.step(.04);self.assertIn('lock',f.sfx_events)
        while f.state=='transform':f.step(.04)
        self.assertEqual(f.sfx_events,['truck_break','unfold','lock'])

    def test_cannon_sound_per_fan_and_mine_per_release(self):
        f=Chase();f.encounter_phase=2;f.robot_age=.99
        chase_robot.robot_step(f,.02)
        self.assertEqual(f.sfx_events,['cannon'])
        self.assertEqual(len(f.shots),3)
        chase_robot.robot_step(f,.02);self.assertEqual(f.sfx_events,['cannon'])
        f.robot_age=5.49;chase_robot.robot_step(f,.02)
        self.assertEqual(f.sfx_events[-1],'mine')

    def test_mortar_impact_destruction_and_invulnerable_hits(self):
        f=Chase();f.attack_timer=999
        f.shots=[Bullet(500,569,0,100,True,kind='truck_mortar')]
        f.step(.02);self.assertIn('road_blast',f.sfx_events)
        f=Chase();f.invuln=0;f.hurt();f.hurt()
        self.assertEqual(f.sfx_events,['car_hit'])
        f.invuln=0;f.hp=1;f.hurt()
        self.assertEqual(f.sfx_events[-1],'car_wreck')
        f=Chase();f.begin_destruction()
        self.assertEqual(f.sfx_events,['robot_break'])

    def test_impacts_are_throttled_and_offscreen_impacts_silent(self):
        f=Chase()
        f.sound('road_blast',position=(2000,570))
        self.assertFalse(f.sfx_events)
        for _ in range(30):f.sound('impact',.14)
        self.assertEqual(f.sfx_events,['impact'])
        f.clock=.15;f.sound('impact',.14);self.assertEqual(len(f.sfx_events),2)

    def test_audio_bank_switch_and_pause_drop_previous_tails(self):
        s=WeaponAudio();s.device=7;s.lib=Mock();s.burst=bytes(9000)
        s.lib.SDL_GetQueuedAudioSize.return_value=0;s.lib.SDL_QueueAudio.return_value=0
        first=Fight();first.sound('rupture');s.update(first,False,True)
        self.assertTrue(s.effects.voices)
        f=Chase();f.sound('boost');s.update(f,False,True)
        self.assertIsInstance(s.effects,ChaseEffects)
        self.assertEqual([v[0] for v in s.effects.voices],['boost'])
        f.sound('truck_break');s.update(f,False,False)
        self.assertFalse(s.effects.voices);self.assertFalse(f.sfx_events)
        s.lib.SDL_ClearQueuedAudio.assert_called()
        s.lib.SDL_QueueAudio.reset_mock();s.update(f,False,True)
        s.lib.SDL_QueueAudio.assert_not_called()

    def test_assets_have_quiet_peaks_and_complete_tails(self):
        paths=list(AUDIO.glob('*.wav'));self.assertEqual(len(paths),25)
        for p in paths:
            with wave.open(str(p)) as f:
                self.assertEqual((f.getframerate(),f.getnchannels(),f.getsampwidth()),(44100,1,2))
                pcm=array.array('h',f.readframes(f.getnframes()))
                self.assertGreater(max(map(abs,pcm)),0);self.assertLess(max(map(abs,pcm)),1400)
                self.assertLess(abs(pcm[0]),2);self.assertLess(abs(pcm[-1]),2)
        m=ChaseEffects();m.trigger('robot_break')
        for _ in range(150):m.mix(bytes(1764))
        self.assertTrue(m.voices)
        for _ in range(60):m.mix(bytes(1764))
        self.assertFalse(m.voices)

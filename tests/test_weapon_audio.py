import unittest
from unittest.mock import Mock,patch
from types import SimpleNamespace
from omacontra.audio.weapon_audio import WeaponAudio
from omacontra.stages.reaper.combat import Fight
from omacontra.stages.highway.chase import Chase
from omacontra.stages.dragon.foundry import Foundry

class WeaponAudioTests(unittest.TestCase):
    def player(self):
        s=WeaponAudio();s.device=7;s.lib=Mock();s.burst=bytes(range(256))*400
        s.lib.SDL_GetQueuedAudioSize.return_value=0;s.lib.SDL_QueueAudio.return_value=0
        return s

    @patch('omacontra.audio.weapon_audio.time.monotonic')
    def test_stream_keeps_natural_cadence_between_shots(self,clock):
        clock.return_value=1.;s=self.player();f=SimpleNamespace(machine_shots=0)
        s.update(f,True);s.lib.SDL_QueueAudio.assert_not_called()
        f.machine_shots=1;s.update(f,True)
        self.assertEqual(s.cursor,3528)
        clock.return_value=1.02;s.update(f,True)
        self.assertEqual(s.cursor,7056)
        f.machine_shots=2;s.update(f,True)
        self.assertEqual(s.cursor,10584)
        self.assertEqual(s.lib.SDL_QueueAudio.call_args.args[1],s.burst[8820:10584])

    def test_pause_and_laser_discard_pending_events_without_replaying(self):
        s=self.player();f=SimpleNamespace(machine_shots=1)
        s.update(f,False);s.update(f,True);s.lib.SDL_QueueAudio.assert_not_called()
        f.machine_shots=2;f.laser=True;s.update(f,True)
        s.lib.SDL_QueueAudio.assert_not_called();s.lib.SDL_ClearQueuedAudio.assert_called()

    @patch('omacontra.audio.weapon_audio.time.monotonic')
    def test_stops_on_release_or_when_weapon_cannot_fire(self,clock):
        clock.return_value=1.;s=self.player();f=SimpleNamespace(machine_shots=1)
        s.update(f,True);s.update(f,False)
        self.assertIsNone(s.last_shot);self.assertEqual(s.cursor,0)
        f.machine_shots=2;s.update(f,True)
        clock.return_value=1.16;s.update(f,True)
        self.assertIsNone(s.last_shot);self.assertEqual(s.cursor,0)
        s.lib.SDL_ClearQueuedAudio.assert_called_with(7)

    def test_slow_frame_does_not_stack_a_backlog(self):
        s=self.player();f=SimpleNamespace(machine_shots=1);s.update(f,True)
        s.lib.SDL_GetQueuedAudioSize.return_value=9000
        f.machine_shots=20;s.update(f,True)
        self.assertEqual(s.lib.SDL_QueueAudio.call_count,4)
        s.lib.SDL_ClearQueuedAudio.assert_called_with(7)
        self.assertTrue(all(c.args[2]==1764 for c in s.lib.SDL_QueueAudio.call_args_list))

    def test_burst_wrap_preserves_pcm_order(self):
        s=self.player();f=SimpleNamespace(machine_shots=1)
        s.owner=f;s.cursor=len(s.burst)-100
        expected=s.burst[-100:]+s.burst[:1664]
        s.update(f,True)
        self.assertEqual(s.lib.SDL_QueueAudio.call_args_list[0].args[1],expected)

    def test_actual_shots_increment_events_at_weapon_cadence(self):
        for cls in (Fight,Chase):
            f=cls();f.step(.02,shoot=True)
            self.assertEqual(f.machine_shots,1)
            f.step(.02,shoot=True);self.assertEqual(f.machine_shots,1)
            for _ in range(6):f.step(.02,shoot=True)
            self.assertGreater(f.machine_shots,1)
        f=Foundry();f.laser=True
        for _ in range(10):f.step(.02,shoot=True)
        self.assertEqual(getattr(f,'machine_shots',0),0)

    def test_missing_audio_backend_fails_once_without_affecting_game(self):
        s=WeaponAudio()
        with patch('omacontra.audio.weapon_audio.find_library',return_value=None),patch('builtins.print') as log:
            self.assertFalse(s.open());self.assertFalse(s.open())
            log.assert_called_once()

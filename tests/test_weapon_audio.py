import unittest
from unittest.mock import Mock,patch
from types import SimpleNamespace
from omacontra.audio.weapon_audio import WeaponAudio,SFX_BOOST


class WeaponAudioTests(unittest.TestCase):
    def player(self):
        sound=WeaponAudio();sound.device=7;sound.lib=Mock()
        sound.lib.SDL_GetQueuedAudioSize.return_value=0
        sound.lib.SDL_QueueAudio.return_value=0
        return sound

    def test_machine_gun_never_queues_audio(self):
        sound=self.player();fight=SimpleNamespace(machine_shots=0,sfx_events=[])
        for count in range(100):
            fight.machine_shots=count;sound.update(fight,True,True)
        sound.lib.SDL_QueueAudio.assert_not_called()

    def test_effects_play_with_silent_machine_gun(self):
        sound=self.player();fight=SimpleNamespace(machine_shots=30,sfx_events=['jump'])
        sound.update(fight,True,True)
        self.assertEqual(sound.lib.SDL_QueueAudio.call_count,2)
        self.assertTrue(any(sound.lib.SDL_QueueAudio.call_args_list[0].args[1]))
        self.assertFalse(fight.sfx_events)

    def test_pause_discards_events_without_replaying(self):
        sound=self.player();fight=SimpleNamespace(sfx_events=['jump'])
        sound.update(fight,False,False);sound.update(fight,True,True)
        sound.lib.SDL_QueueAudio.assert_not_called()
        sound.lib.SDL_ClearQueuedAudio.assert_called_with(7)

    def test_slow_frame_does_not_stack_backlog(self):
        sound=self.player();fight=SimpleNamespace(sfx_events=['jump'])
        sound.update(fight,False,True)
        sound.lib.SDL_GetQueuedAudioSize.return_value=9000
        fight.sfx_events=['dash'];sound.update(fight,False,True)
        self.assertEqual(sound.lib.SDL_QueueAudio.call_count,4)
        sound.lib.SDL_ClearQueuedAudio.assert_called_with(7)
        self.assertTrue(all(c.args[2]==1764 for c in sound.lib.SDL_QueueAudio.call_args_list))

    def test_effect_gain_increases_ten_percent_and_zero_still_mutes(self):
        sound=self.player();sound.set_volumes(.8)
        self.assertTrue(all(abs(bank.gain-.8*SFX_BOOST)<1e-8 for bank in sound.banks.values()))
        self.assertAlmostEqual(sound.ui_effects.gain,.88)
        sound.set_volumes(0)
        self.assertTrue(all(bank.gain==0 for bank in sound.banks.values()))
        self.assertEqual(sound.ui_effects.gain,0)

    def test_missing_audio_backend_fails_once_without_affecting_game(self):
        sound=WeaponAudio()
        with patch('omacontra.audio.weapon_audio.find_library',return_value=None),patch('builtins.print') as log:
            self.assertFalse(sound.open());self.assertFalse(sound.open())
            log.assert_called_once()

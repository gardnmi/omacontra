import unittest
from unittest.mock import patch
import cairo
from finale import Finale
from finale_audio import FinaleEffects,AUDIO
from finale_art import FinaleRenderer
from weapon_audio import WeaponAudio


class FinaleAudioTests(unittest.TestCase):
    def test_each_pattern_has_one_event_not_one_per_projectile(self):
        f=Finale();f.skip()
        for phase,events in ((1,('ring','fan')),(2,('spiral','needles','curtain'))):
            if phase==2:f.nodes=[0,0]
            for index,event in enumerate(events):
                f.round=index;f.sfx_events.clear();f.burst()
                self.assertEqual(f.sfx_events,[event])

    def test_dash_and_hurt_respect_recovery(self):
        f=Finale();f.skip();f.invuln=0
        f.hurt();f.hurt();self.assertEqual(f.sfx_events,['hurt'])
        f.sfx_events.clear()
        for _ in range(10):f.step(.02,slide=True)
        self.assertEqual(f.sfx_events.count('thruster'),1)

    def test_laser_start_is_not_repeated_while_held(self):
        f=Finale();f.skip()
        for _ in range(50):f.step(.02,shoot=True)
        self.assertEqual(f.sfx_events.count('laser_start'),1)
        f.step(.02,shoot=False);f.step(.02,shoot=True)
        self.assertEqual(f.sfx_events.count('laser_start'),2)

    def test_release_enrage_and_defeat_fire_once(self):
        f=Finale();f.skip();f.nodes=[0,0];f.step(.02)
        self.assertIn('release',f.sfx_events)
        f.boss_hp=f.final_phase_max;f.step(.02)
        self.assertIn('enrage',f.sfx_events)
        f.boss_hp=0;f.step(.02);f.step(.02)
        self.assertEqual(f.sfx_events.count('defeat'),1)

    def test_bank_loads_all_variants_and_routes_to_shared_device(self):
        bank=FinaleEffects()
        paths=list(AUDIO.glob('*.wav'));self.assertEqual(len(paths),14)
        for path in paths:
            for _ in range(3):bank.trigger(path.stem);bank.mix(bytes(1764))
        self.assertFalse(bank.failed)
        self.assertLessEqual(len(bank.voices),6)
        sound=WeaponAudio();f=Finale();f.sound('ring')
        with patch.object(sound,'open',return_value=False):sound.update(f,False,True)
        self.assertIs(sound.effects,sound.banks['finale'])
        sound.update(f,False,False);self.assertFalse(sound.effects.voices)

    def test_orbital_effects_only_run_in_first_phase(self):
        r=FinaleRenderer();f=Finale();f.skip()
        c=cairo.Context(cairo.ImageSurface(cairo.FORMAT_RGB24,1280,720))
        with patch('orbit_effects.draw') as effects:
            r.draw(c,f);effects.assert_called_once();effects.reset_mock()
            f.nodes=[0,0];r.draw(c,f);effects.assert_not_called()
            f.screensaver_age=10;f.boss_hp=100;r.draw(c,f);effects.assert_not_called()

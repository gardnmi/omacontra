import unittest
from unittest.mock import Mock,patch
import cairo
from omacontra.ui.story import Intro, SECRET_CODE
from omacontra.stages.reaper.combat import Fight
from omacontra.stages.highway.chase import Chase
from omacontra.stages.harbor.tidebreaker import Tidebreaker
from omacontra.stages.dragon.foundry import Foundry
from omacontra.stages.space.finale import Finale
from omacontra.ui.art import Renderer, W, H

class SecretCodeTests(unittest.TestCase):
    def title(self):
        intro=Intro();intro.index=len(intro.beats)-1
        return intro

    def test_code_unlocks_during_every_opening_beat_and_only_once(self):
        for index in range(len(Intro().beats)):
            with self.subTest(beat=index):
                intro=Intro();intro.index=index
                for key in SECRET_CODE[:-1]:self.assertFalse(intro.enter_code(key))
                self.assertTrue(intro.enter_code(SECRET_CODE[-1]))
                self.assertTrue(intro.unlimited_lives)
                for key in SECRET_CODE:self.assertFalse(intro.enter_code(key))

    def test_code_survives_transition_to_title(self):
        intro=Intro();intro.index=len(intro.beats)-2
        for key in SECRET_CODE[:4]:intro.enter_code(key)
        intro.step(intro.beat.duration)
        for key in SECRET_CODE[4:-1]:intro.enter_code(key)
        self.assertTrue(intro.enter_code(SECRET_CODE[-1]))

    def test_code_disabled_after_start_and_during_journey(self):
        intro=self.title();intro.request_start()
        for key in SECRET_CODE:self.assertFalse(intro.enter_code(key))
        intro=Intro(journey=True)
        for key in SECRET_CODE:self.assertFalse(intro.enter_code(key))

    def test_wrong_sequence_resets_but_overlapping_prefix_can_recover(self):
        intro=self.title()
        for key in ('up','up','down','left','right','left','right'):
            intro.enter_code(key)
        self.assertFalse(intro.unlimited_lives)
        intro.enter_code('up')
        for key in SECRET_CODE:intro.enter_code(key)
        self.assertTrue(intro.unlimited_lives)

    def test_hits_preserve_lives_and_reactions_in_all_five_modes(self):
        for cls in (Fight,Chase,Tidebreaker,Foundry,Finale):
            with self.subTest(mode=cls.__name__):
                f=cls();f.state='play';f.unlimited_lives=True;f.hp=1
                for _ in range(20):
                    f.invuln=0;f.hurt()
                    self.assertEqual(f.hp,1);self.assertEqual(f.state,'play')
                    self.assertGreater(f.invuln,0)
                f.unlimited_lives=False;f.invuln=0;f.hurt()
                self.assertEqual(f.hp,0);self.assertEqual(f.state,'dead')

    def test_session_unlock_is_applied_to_every_new_encounter(self):
        from omacontra.boss_app import BossApp
        app=BossApp.__new__(BossApp);app.unlimited_lives=True
        for level,cls in enumerate((Fight,Chase,Tidebreaker,Foundry,Finale),1):
            self.assertTrue(app.prepare_encounter(cls(),level).unlimited_lives)
        app.level=1;app.keyboard=Mock();app.reset_encounter()
        self.assertTrue(app.f.unlimited_lives)

    def test_real_key_handler_confirms_unlock_once(self):
        from omacontra.boss_app import BossApp
        from omacontra.input_state import KeyboardState
        from types import SimpleNamespace
        app=BossApp.__new__(BossApp);app.intro=Intro()
        app.keyboard=KeyboardState();app.f=Fight();app.level=1
        app.unlimited_lives=False;app.unlock_sound=Mock()
        for index,key in enumerate(SECRET_CODE*2):
            event=SimpleNamespace(hardware_keycode=index+20,keyval=0)
            with patch('omacontra.boss_app.Gdk.keyval_name',return_value=key):app.key(None,event)
            app.keyboard.release(event.hardware_keycode)
        self.assertTrue(app.unlimited_lives);self.assertTrue(app.f.unlimited_lives)
        app.unlock_sound.update.assert_called_once_with(True)

    def test_unlock_banner_renders_and_timer_pauses(self):
        intro=self.title()
        for key in SECRET_CODE:intro.enter_code(key)
        intro.paused=True;intro.step(2);self.assertEqual(intro.unlock_age,0)
        intro.paused=False;renderer=Renderer()
        for t in (.05,.7,4.):
            intro.unlock_age=t
            s=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H)
            renderer.draw(cairo.Context(s),intro,W,H)

    def test_opening_beat_shows_unlock_confirmation(self):
        intro=Intro()
        for key in SECRET_CODE:intro.enter_code(key)
        renderer=Renderer()
        surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H)
        with patch.object(renderer,'unlock_banner') as banner:
            renderer.draw(cairo.Context(surface),intro,W,H)
            banner.assert_called_once()
            intro.step(4)
            renderer.draw(cairo.Context(surface),intro,W,H)
            banner.assert_called_once()

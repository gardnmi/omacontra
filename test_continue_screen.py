import unittest
from unittest.mock import Mock,patch
from types import SimpleNamespace
import cairo
from continue_screen import ContinueScreen,ContinueRenderer
from weapon_audio import WeaponAudio


class ContinueTests(unittest.TestCase):
    def test_ten_seconds_and_timeout_sound_only_once(self):
        s=ContinueScreen();self.assertEqual(s.remaining,10)
        for count in range(9,0,-1):
            s.step(1);self.assertEqual(s.remaining,count)
            self.assertEqual(s.state,'countdown')
        s.sfx_events.clear();s.step(1)
        self.assertEqual(s.state,'expired');self.assertFalse(s.accept())
        s.step(20);self.assertEqual(s.sfx_events,['death_blow'])

    def test_accept_at_last_moment_finishes_animation_before_retry(self):
        s=ContinueScreen();s.step(9.99);self.assertTrue(s.accept())
        self.assertFalse(s.accept());s.step(1.3);self.assertFalse(s.finished)
        s.step(.05);self.assertTrue(s.finished)
        self.assertEqual(s.sfx_events.count('accept'),1)
        self.assertNotIn('death_blow',s.sfx_events)

    def test_portrait_states_render_and_reuse_cached_rows(self):
        r=ContinueRenderer();rows=tuple(r.rows)
        c=cairo.Context(cairo.ImageSurface(cairo.FORMAT_RGB24,1280,720))
        s=ContinueScreen();r.draw(c,s);s.accept()
        for t in (0,.2,.5,.65,1.2):s.age=t;r.draw(c,s)
        s=ContinueScreen();s.step(10);r.draw(c,s)
        self.assertEqual(tuple(r.rows),rows)

    def test_continue_sound_bank_and_pause(self):
        audio=WeaponAudio();screen=ContinueScreen()
        with patch.object(audio,'open',return_value=False):audio.update(screen,False,True)
        self.assertIs(audio.effects,audio.banks['continue'])
        for name in ('tick','accept','death_blow'):
            for _ in range(3):audio.effects.trigger(name);audio.effects.mix(bytes(1764))
        self.assertFalse(audio.effects.failed)
        audio.update(screen,False,False);self.assertFalse(audio.effects.voices)

    def test_retry_skips_intros_and_preserves_guardian_checkpoint(self):
        from boss_app import BossApp
        from combat import Fight
        from chase import Chase
        from tidebreaker import Tidebreaker
        from foundry import Foundry
        from finale import Finale
        from campaign_progress import prepare_encounter
        for level,cls in enumerate((Fight,Chase,Tidebreaker,Foundry,Finale),1):
            app=BossApp.__new__(BossApp);app.level=level;app.f=cls()
            if level==3:app.f.advance_guardian()
            app.f.hp=0;app.f.state='dead'
            def reset():
                app.f=prepare_encounter(cls(),level)
                app.continue_screen=None
            app.reset_encounter=reset
            app.continue_encounter()
            self.assertEqual(app.f.hp,app.f.max_hp)
            self.assertEqual(app.f.state,'play')
            self.assertIsNone(app.chase_cinema);self.assertIsNone(app.journey_cinema)
            self.assertIsNone(app.foundry_intro)
            if level==3:self.assertEqual(app.f.stage,1)

    def test_host_opens_continue_only_after_death_animation_and_freezes_hidden(self):
        from boss_app import BossApp
        from input_state import KeyboardState
        from combat import Fight
        app=BossApp.__new__(BossApp)
        app.closed=False;app.last=0;app.placed=True;app.visible=True
        app.intro=None;app.paused=False;app.level=1;app.f=Fight();app.f.state='dead';app.f.hp=0
        app.music=Mock();app.area=Mock();app.keyboard=KeyboardState();app.keys=app.keyboard.keys
        app.shooting=False;app.slide_requested=False;app.chase_cinema=None
        app.continue_screen=None;app.continue_renderer=Mock();app.death_wait=0
        with patch('boss_app.time.monotonic') as now:
            for i in range(29):now.return_value=(i+1)*.04;app.tick()
            self.assertIsNone(app.continue_screen)
            for i in range(3):now.return_value=1.2+i*.04;app.tick()
            self.assertIsNotNone(app.continue_screen)
            age=app.continue_screen.age;app.visible=False
            now.return_value=2;app.tick();self.assertEqual(app.continue_screen.age,age)

    def test_held_jump_must_be_released_before_continuing(self):
        from boss_app import BossApp,Gdk
        from input_state import KeyboardState
        app=BossApp.__new__(BossApp);app.keyboard=KeyboardState()
        app.continue_screen=ContinueScreen();app.continue_blocked_keys={'space'}
        event=SimpleNamespace(hardware_keycode=65,keyval=Gdk.KEY_space)
        app.key(None,event);self.assertEqual(app.continue_screen.state,'countdown')
        app.release(None,event);app.key(None,event)
        self.assertEqual(app.continue_screen.state,'accepted')

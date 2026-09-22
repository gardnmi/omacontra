import array
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import Mock,patch
import cairo
from release_ui import Frontend,Profile,RunRecord
from combat import Fight
from input_state import KeyboardState
from weapon_audio import WeaponAudio
from reaper_audio import ReaperEffects

class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory();self.addCleanup(self.temp.cleanup)
    def app(self,level=1):
        from boss_app import BossApp
        a=BossApp.__new__(BossApp);a.f=Fight();a.level=level;a.intro=None;a.guardian_practice=False
        a.music=Mock();a.game_music=Mock();a.unlock_sound=Mock();a.weapon_audio=WeaponAudio()
        a.keyboard=KeyboardState();a.keys=a.keyboard.keys;a.paused=False;a.shooting=False;a.slide_requested=False
        a.chase_cinema=a.journey_cinema=a.foundry_intro=a.continue_screen=None
        a.closed=False;a.last=0.;a.placed=True;a.visible=True;a.area=Mock();a.chase_outro_seen=a.tide_outro_seen=False
        a.unlimited_lives=False;a.aim=None
        a.frontend=Frontend(a,Profile(Path(self.temp.name)/'profile.json'))
        return a
    def tick(self,a,dt=.02):
        with patch('boss_app.time.monotonic',return_value=a.last+dt),patch.object(a.weapon_audio,'open',return_value=False):a.tick()
    def test_title_selects_hardcore_and_disables_cheat(self):
        from boss_app import Gdk
        from story import Intro
        a=self.app();a.intro=Intro();a.intro.index=len(a.intro.beats)-1
        a.unlimited_lives=a.f.unlimited_lives=a.intro.unlimited_lives=True
        event=SimpleNamespace(hardware_keycode=36,keyval=Gdk.KEY_Return)
        a.key(None,event);self.assertEqual(a.frontend.page,'mode')
        a.release(None,event)
        a.frontend.key('down');a.key(None,event)
        self.assertTrue(a.frontend.record.hardcore)
        self.assertFalse(a.unlimited_lives or a.f.unlimited_lives or a.intro.unlimited_lives)
        self.assertIsNotNone(a.intro.start_age);a.music.play_start.assert_called_once()
        self.assertFalse(a.paused or a.intro.paused)

    def test_mode_back_and_standard_start(self):
        from story import Intro
        a=self.app();a.intro=Intro();a.intro.index=len(a.intro.beats)-1
        a.frontend.open('mode');a.frontend.key('escape')
        self.assertIsNone(a.frontend.page);self.assertIsNone(a.intro.start_age)
        a.frontend.open('mode');a.frontend.key('return')
        self.assertFalse(a.frontend.record.hardcore);self.assertIsNotNone(a.intro.start_age)

    def test_hardcore_death_skips_countdown_and_cannot_restart(self):
        a=self.app();a.frontend.new_run(hardcore=True)
        a.f.hp=0;a.f.state='dead';a.continue_renderer=Mock();a.death_wait=1.19
        self.tick(a)
        self.assertEqual(a.continue_screen.state,'expired')
        self.assertFalse(a.continue_screen.accept())
        self.assertEqual(a.weapon_audio.banks['continue'].takes['death_blow'],1)
        original=a.f
        a.continue_encounter();a.frontend.request('restart');a.frontend.activate('restart')
        self.assertIs(a.f,original);self.assertEqual(a.f.hp,0)
        self.assertEqual(a.frontend.record.continues,0)
        a.frontend.open();self.assertNotIn('Restart encounter',a.frontend.rows())

    def test_hardcore_carries_lives_and_saves_separate_best(self):
        a=self.app();a.chase_renderer=Mock();a.frontend.new_run(hardcore=True);a.f.hp=2
        a.advance_campaign()
        self.assertEqual(a.f.hp,3);self.assertTrue(a.frontend.record.hardcore)
        a.level=5;a.f.state='won';a.frontend.record.cleared={1,2,3,4}
        a.frontend.record.elapsed=321
        for _ in range(160):a.frontend.observe(.02,a.f,a.f.hp,0,False)
        self.assertEqual(a.frontend.profile.best,{'hardcore':321})
        a.frontend.activate('again')
        self.assertEqual(a.level,1);self.assertTrue(a.frontend.record.hardcore)
        self.assertEqual(a.f.hp,5)

    def test_settings_round_trip_and_corrupt_profile(self):
        p=Path(self.temp.name)/'profile.json';profile=Profile(p);profile.settings['music']=35;profile.best['arcade']=123.;profile.save()
        loaded=Profile(p);self.assertEqual(loaded.settings['music'],35);self.assertEqual(loaded.best['arcade'],123.)
        for text in ('bad json','[]','{"settings":{"music":999,"gunfire":"bad"}}'):
            p.write_text(text);loaded=Profile(p);self.assertLessEqual(loaded.settings['music'],150)
    def test_focus_loss_requires_explicit_resume_and_freezes_continue(self):
        from continue_screen import ContinueScreen
        a=self.app();a.continue_screen=ContinueScreen();a.unfocus()
        self.assertEqual(a.frontend.page,'pause');before=a.continue_screen.age
        for _ in range(10):self.tick(a)
        self.assertEqual(a.continue_screen.age,before)
        a.frontend.key('return');self.tick(a);self.assertGreater(a.continue_screen.age,before)
    def test_pause_freezes_combat_and_cinematics(self):
        from story import Intro
        a=self.app();a.intro=Intro(journey=True);a.unfocus();clock=a.intro.age
        self.tick(a);self.assertEqual(a.intro.age,clock)
        a.frontend.resume();a.intro=None;a.frontend.open();clock=a.f.clock
        self.tick(a);self.assertEqual(a.f.clock,clock)
        a.frontend.resume();self.tick(a);self.assertGreater(a.f.clock,clock)
    def test_restart_cancel_then_confirm(self):
        a=self.app();original=a.f;a.frontend.request('restart');a.frontend.key('return')
        self.assertIs(a.f,original);a.frontend.request('restart');a.frontend.key('down');a.frontend.key('return')
        self.assertIsNot(a.f,original);self.assertEqual(a.frontend.record.restarts,1)
    def test_options_apply_and_save_each_audio_bus(self):
        a=self.app();a.frontend.open('options');a.frontend.key('left')
        self.assertEqual(a.frontend.profile.settings['music'],95);a.music.set_volume.assert_called_with(80.75)
        a.frontend.key('down');a.frontend.key('left');self.assertEqual(a.weapon_audio.effects.gain,.95)
        a.frontend.key('down');a.frontend.key('left');self.assertEqual(a.weapon_audio.gun_gain,.95)
        self.assertEqual(Profile(a.frontend.profile.path).settings,a.frontend.profile.settings)
    def test_records_separate_practice_unlimited_and_arcade(self):
        a=self.app();f=a.frontend;f.record.elapsed=123.;f.record.cleared={1,2,3,4};a.level=5;a.f.state='won'
        for _ in range(160):f.observe(.02,a.f,a.f.hp,0,False)
        self.assertEqual(f.page,'results');self.assertEqual(f.profile.best['arcade'],123.)
        self.assertEqual(f.record.clean,5)
        f.new_run(5,True);f.record.elapsed=1.;f.award_age=4
        for _ in range(160):f.observe(.02,a.f,a.f.hp,0,False)
        self.assertNotIn('practice',f.profile.best)
        r=RunRecord();r.cleared=set(range(1,6));r.unlimited=True;self.assertEqual(r.category,'unlimited')
    def test_real_damage_and_continue_are_counted(self):
        a=self.app();a.f.invuln=0;hp=a.f.hp;a.f.hurt();a.frontend.observe(.02,a.f,hp,0,True)
        self.assertEqual(a.frontend.record.losses,1);self.assertEqual(a.frontend.record.hits[1],1)
        a.continue_encounter();self.assertEqual(a.frontend.record.continues,1)
        a.f.invuln=0;a.f.unlimited_lives=True;hp=a.f.hp;a.f.hurt();a.frontend.observe(.02,a.f,hp,0,True)
        self.assertEqual(a.frontend.record.losses,1);self.assertEqual(a.frontend.record.hits[1],2)
    def test_play_again_starts_first_boss(self):
        a=self.app(5);a.frontend.record.cleared=set(range(1,6));a.frontend.open('results');a.frontend.key('return')
        self.assertEqual(a.level,1);self.assertEqual(a.f.state,'play');self.assertFalse(a.frontend.record.cleared)
    def test_all_menu_pages_render(self):
        a=self.app();s=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720);c=cairo.Context(s)
        for page in ('pause','controls','options','results','bosses','credits','confirm','mode'):
            a.frontend.open(page)
            for i in range(3):a.frontend.credits_page=i;a.frontend.draw(c)
        a.frontend.page=None;a.frontend.award=2
        for t in (0,.5,1,2,2.9):a.frontend.award_age=t;a.frontend.draw(c)
    def test_muted_effects_and_gun_have_independent_gain(self):
        e=ReaperEffects();e.gain=0;e.voices=[['test',0,array.array('h',[1000]*4)]]
        original=array.array('h',[100]*4).tobytes();self.assertEqual(e.mix(original),original)
        a=self.app();a.weapon_audio.set_volumes(0,1);self.assertEqual(a.weapon_audio.gun_gain,1)
        self.assertTrue(all(b.gain==0 for b in a.weapon_audio.banks.values()))
    def test_award_does_not_duplicate_or_mutate_health(self):
        a=self.app();hp=a.f.hp;a.f.state='won'
        for _ in range(10):a.frontend.observe(.02,a.f,hp,0,False)
        self.assertEqual(a.frontend.record.cleared,{1});self.assertEqual(a.f.hp,hp)
        self.assertEqual(a.weapon_audio.ui_effects.takes['accept'],1)

    def test_boss_select_launches_every_encounter_as_practice(self):
        for level in range(1,6):
            a=self.app();a.chase_renderer=a.tide_renderer=a.foundry_renderer=Mock()
            with patch('finale_art.FinaleRenderer',return_value=Mock()):
                a.frontend.open('bosses');a.frontend.selection=level-1;a.frontend.key('return')
            self.assertEqual(a.level,level);self.assertEqual(a.frontend.record.category,'practice')
            self.assertIsNone(a.frontend.page);self.assertFalse(a.paused)

    def test_full_campaign_routes_to_results_and_can_return_to_title(self):
        from boss_app import Gdk
        a=self.app();a.chase_renderer=a.tide_renderer=a.foundry_renderer=Mock();a.intro_renderer=None;a.renderer=Mock()
        event=SimpleNamespace(hardware_keycode=36,keyval=Gdk.KEY_Return)
        for level in range(1,6):
            self.assertEqual(a.level,level)
            a.f.hp=2
            a.f.state='won';a.frontend.observe(.02,a.f,a.f.hp,0,False)
            if level==5:break
            if level==2:a.chase_cinema=SimpleNamespace(age=6,kind='outro')
            if level==3:a.journey_cinema=SimpleNamespace(age=6,kind='outro')
            with patch('finale_art.FinaleRenderer',return_value=Mock()):a.key(None,event)
            self.assertEqual(a.f.hp,3)
            a.release(None,event)
        for _ in range(160):a.frontend.observe(.02,a.f,a.f.hp,0,False)
        self.assertEqual(a.frontend.page,'results');self.assertEqual(a.frontend.record.category,'arcade')
        a.frontend.selection=2;a.frontend.key('return')
        self.assertEqual(a.level,1);self.assertEqual(a.intro.beat.kind,'cover');self.assertIsNone(a.frontend.page)

    def test_resume_key_is_blocked_until_released(self):
        from boss_app import Gdk
        a=self.app();a.frontend.open();event=SimpleNamespace(hardware_keycode=36,keyval=Gdk.KEY_Return)
        a.key(None,event);self.assertIn('return',a.frontend.blocked)
        a.release(None,event);self.assertNotIn('return',a.frontend.blocked)

if __name__=='__main__':unittest.main()

import array
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import Mock,patch
import cairo
from omacontra.ui.release_ui import Frontend, Profile, RunRecord
from omacontra.stages.reaper.combat import Fight
from omacontra.input_state import KeyboardState
from omacontra.audio.weapon_audio import WeaponAudio
from omacontra.audio.reaper_audio import ReaperEffects

class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory();self.addCleanup(self.temp.cleanup)
    def app(self,level=1):
        from omacontra.boss_app import BossApp
        a=BossApp.__new__(BossApp);a.f=Fight();a.level=level;a.intro=None;a.guardian_practice=False
        a.music=Mock();a.game_music=Mock();a.unlock_sound=Mock();a.weapon_audio=WeaponAudio()
        a.keyboard=KeyboardState();a.keys=a.keyboard.keys;a.paused=False;a.shooting=False;a.slide_requested=False
        a.chase_cinema=a.journey_cinema=a.foundry_intro=a.continue_screen=None
        a.closed=False;a.last=0.;a.placed=True;a.visible=True;a.area=Mock();a.chase_outro_seen=a.tide_outro_seen=False
        a.unlimited_lives=False;a.aim=None
        a.frontend=Frontend(a,Profile(Path(self.temp.name)/'profile.json'))
        return a
    def tick(self,a,dt=.02):
        with patch('omacontra.boss_app.time.monotonic',return_value=a.last+dt),patch.object(a.weapon_audio,'open',return_value=False):a.tick()
    def test_music_player_transport_and_parent_menu_restore(self):
        from omacontra.ui.story import Intro
        a=self.app();a.intro=Intro();front=a.frontend
        player=front.jukebox;player.audio=Mock()
        front.open('mode');front.selection=front.rows().index('Music player');front.key('return')
        self.assertEqual(front.page,'music');self.assertEqual(front.parent,'mode')
        self.assertEqual(len(player.tracks),6)
        self.assertIn('omacontra-opening-theme.mp3',[t['file'] for t in player.tracks])
        self.assertNotIn('reaper-quattro-lets-go-nerds.mp3',[t['file'] for t in player.tracks])
        front.key('return');self.tick(a)
        self.assertEqual(player.index,0);self.assertFalse(player.paused)
        player.audio.update.assert_called_with(True,False)
        a.music.update.assert_called_with(True,True)
        front.key('return');self.tick(a);player.audio.update.assert_called_with(True,True)
        front.key('right');self.assertEqual(player.index,1);self.assertFalse(player.paused)
        a.visible=False;self.tick(a);player.audio.update.assert_called_with(True,True)
        front.key('escape');self.assertEqual(front.page,'mode');self.assertIsNone(player.index)
        a.visible=True;self.tick(a);a.music.update.assert_called_with(True,False)
        a.game_music.stop.assert_not_called()

    def test_music_player_from_results_pauses_finale_and_restores_it(self):
        a=self.app(5);a.f.state='won';f=a.frontend;f.result_saved=True
        f.open('results');f.selection=f.rows().index('Music player');f.key('return')
        f.jukebox.audio=Mock();f.key('return');self.tick(a)
        a.game_music.update.assert_called_with(True,True)
        f.selection=len(f.jukebox.tracks);f.key('return');self.assertIsNone(f.jukebox.index)
        f.key('escape');self.assertEqual(f.page,'results');self.tick(a)
        a.game_music.update.assert_called_with(True,False)

    def test_title_selects_hardcore_and_disables_cheat(self):
        from omacontra.boss_app import Gdk
        from omacontra.ui.story import Intro
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

    def test_run_selection_keeps_title_music_and_hidden_window_still_pauses(self):
        from omacontra.ui.story import Intro
        a=self.app();a.intro=Intro();a.intro.index=len(a.intro.beats)-1
        a.frontend.open('mode');age=a.intro.age
        self.tick(a);a.music.update.assert_called_with(True,False)
        self.assertEqual(a.intro.age,age)
        a.frontend.key('down');self.tick(a)
        a.music.update.assert_called_with(True,False)
        a.visible=False;self.tick(a);a.music.update.assert_called_with(True,True)
        a.visible=True;a.frontend.key('escape');self.tick(a)
        a.music.update.assert_called_with(True,False)
        a.frontend.open('pause');self.tick(a)
        a.music.update.assert_called_with(True,True)
        a.music.restart.assert_not_called();a.music.stop.assert_not_called()

    def test_mode_back_and_standard_start(self):
        from omacontra.ui.story import Intro
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
        from omacontra.ui.continue_screen import ContinueScreen
        a=self.app();a.continue_screen=ContinueScreen();a.unfocus()
        self.assertEqual(a.frontend.page,'pause');before=a.continue_screen.age
        for _ in range(10):self.tick(a)
        self.assertEqual(a.continue_screen.age,before)
        a.frontend.key('return');self.tick(a);self.assertGreater(a.continue_screen.age,before)
    def test_pause_freezes_combat_and_cinematics(self):
        from omacontra.ui.story import Intro
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
        a.frontend.key('down');a.frontend.key('left');self.assertAlmostEqual(a.weapon_audio.effects.gain,.95*1.1)
        a.frontend.key('down');self.assertEqual(a.frontend.rows()[a.frontend.selection],'Back')
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
        self.assertEqual(a.frontend.record.losses,2);self.assertEqual(a.frontend.record.hits[1],2)
        self.assertEqual(a.f.hp,hp)
    def test_unlimited_losses_count_once_per_accepted_hit_across_all_stages(self):
        from omacontra.stages.highway.chase import Chase
        from omacontra.stages.harbor.tidebreaker import Tidebreaker
        from omacontra.stages.dragon.foundry import Foundry
        from omacontra.stages.space.finale import Finale
        a=self.app()
        for level,cls in enumerate((Fight,Chase,Tidebreaker,Foundry,Finale),1):
            with self.subTest(level=level):
                a.level=level;a.f=cls();a.f.state='play';a.f.unlimited_lives=True
                hp=a.f.hp;a.f.invuln=0
                a.f.hurt()
                a.frontend.observe(.02,a.f,hp,0,True)
                self.assertEqual(a.frontend.record.losses,level)
                self.assertEqual(a.f.hp,hp)
                # A second collision during recovery and a quiet tick add nothing.
                hits=a.f.damage_taken;a.f.hurt()
                a.frontend.observe(.02,a.f,hp,hits,True)
                a.frontend.observe(.02,a.f,hp,hits,True)
                self.assertEqual(a.frontend.record.losses,level)
                self.assertEqual(a.frontend.record.hits[level],1)
        self.assertTrue(a.frontend.record.unlimited)

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
    def test_muted_effects_stay_silent(self):
        e=ReaperEffects();e.gain=0;e.voices=[['test',0,array.array('h',[1000]*4)]]
        original=array.array('h',[100]*4).tobytes();self.assertEqual(e.mix(original),original)
        a=self.app();a.weapon_audio.set_volumes(0)
        self.assertTrue(all(b.gain==0 for b in a.weapon_audio.banks.values()))
    def test_menu_cues_and_mouse_selection_are_deliberate(self):
        a=self.app();f=a.frontend;bank=a.weapon_audio.menu_effects
        with patch('omacontra.ui.release_ui.time.monotonic',side_effect=range(100,200)):
            f.open();self.assertIn('open',bank.takes)
            f.key('down');self.assertIn('move',bank.takes)
            f.key('return');self.assertEqual(f.page,'controls');self.assertIn('confirm',bank.takes)
            f.key('escape');self.assertEqual(f.page,'pause');self.assertIn('back',bank.takes)
            self.assertEqual(f.selection,1)
            f.pointer(100,320);self.assertEqual(f.selection,2)
            takes=dict(bank.takes);f.pointer(101,320);self.assertEqual(bank.takes,takes)
            f.pointer(100,320,True);self.assertEqual(f.page,'options')
            # Clicking labels selects without unexpectedly muting the channel.
            f.pointer(150,240,True);self.assertEqual(f.profile.settings['music'],100)
            f.pointer(118+195,275,True);self.assertEqual(f.profile.settings['music'],75)
            self.assertIn('adjust',bank.takes)
            self.assertEqual(Profile(f.profile.path).settings['music'],75)

    def test_menu_audio_plays_while_combat_is_paused_and_clears_when_hidden(self):
        a=self.app();audio=a.weapon_audio;audio.device=7;audio.lib=Mock()
        audio.lib.SDL_GetQueuedAudioSize.return_value=0;audio.lib.SDL_QueueAudio.return_value=0
        a.frontend.open();a.f.sound('jump');clock=a.f.clock
        a.tick()
        self.assertEqual(a.f.clock,clock)
        self.assertTrue(audio.lib.SDL_QueueAudio.called)
        self.assertFalse(audio.effects.voices)
        a.visible=False;a.tick();self.assertFalse(audio.menu_effects.voices)
        self.assertFalse(audio.ui_effects.voices)
        audio.set_volumes(0);audio.menu_effects.trigger('confirm')
        self.assertEqual(audio.menu_effects.mix(bytes(1764)),bytes(1764))

    def test_new_runs_shuffle_but_continue_and_restart_preserve_music_order(self):
        from omacontra.audio.intro_music import GAME_TRACKS
        a=self.app();f=a.frontend
        first=tuple(reversed(GAME_TRACKS));second=GAME_TRACKS[1:]+GAME_TRACKS[:1]
        with patch('omacontra.audio.intro_music.shuffled_tracks',side_effect=[first,second]) as shuffle:
            f.new_run();self.assertEqual(a.run_playlist,first)
            a.game_music.stop.assert_called_once()
            a.continue_encounter();f.activate('restart')
            self.assertEqual(a.run_playlist,first);self.assertEqual(shuffle.call_count,1)
            f.activate('again');self.assertEqual(a.run_playlist,second)
            self.assertEqual(shuffle.call_count,2)

    def test_award_does_not_duplicate_or_mutate_health(self):
        a=self.app();hp=a.f.hp;a.f.state='won'
        for _ in range(10):a.frontend.observe(.02,a.f,hp,0,False)
        self.assertEqual(a.frontend.record.cleared,{1});self.assertEqual(a.f.hp,hp)
        self.assertEqual(a.weapon_audio.ui_effects.takes['accept'],1)

    def test_boss_select_launches_every_encounter_as_practice(self):
        for level in range(1,6):
            a=self.app();a.chase_renderer=a.tide_renderer=a.foundry_renderer=Mock()
            with patch('omacontra.stages.space.finale_art.FinaleRenderer',return_value=Mock()):
                a.frontend.open('bosses');a.frontend.selection=level-1;a.frontend.key('return')
            self.assertEqual(a.level,level);self.assertEqual(a.frontend.record.category,'practice')
            self.assertIsNone(a.frontend.page);self.assertFalse(a.paused)

    def test_full_campaign_routes_to_results_and_can_return_to_title(self):
        from omacontra.boss_app import Gdk
        a=self.app();a.chase_renderer=a.tide_renderer=a.foundry_renderer=Mock();a.intro_renderer=None;a.renderer=Mock()
        event=SimpleNamespace(hardware_keycode=36,keyval=Gdk.KEY_Return)
        for level in range(1,6):
            self.assertEqual(a.level,level)
            a.f.hp=2
            a.f.state='won';a.frontend.observe(.02,a.f,a.f.hp,0,False)
            if level==5:break
            if level==2:a.chase_cinema=SimpleNamespace(age=6,kind='outro')
            if level==3:a.journey_cinema=SimpleNamespace(age=6,kind='outro')
            with patch('omacontra.stages.space.finale_art.FinaleRenderer',return_value=Mock()):a.key(None,event)
            self.assertEqual(a.f.hp,3)
            a.release(None,event)
        for _ in range(160):a.frontend.observe(.02,a.f,a.f.hp,0,False)
        self.assertEqual(a.frontend.page,'results');self.assertEqual(a.frontend.record.category,'arcade')
        a.frontend.selection=2;a.frontend.key('return')
        self.assertEqual(a.level,1);self.assertEqual(a.intro.beat.kind,'cover');self.assertIsNone(a.frontend.page)

    def test_resume_key_is_blocked_until_released(self):
        from omacontra.boss_app import Gdk
        a=self.app();a.frontend.open();event=SimpleNamespace(hardware_keycode=36,keyval=Gdk.KEY_Return)
        a.key(None,event);self.assertIn('return',a.frontend.blocked)
        a.release(None,event);self.assertNotIn('return',a.frontend.blocked)

if __name__=='__main__':unittest.main()

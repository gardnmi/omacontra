import unittest
from unittest.mock import Mock,patch
from omacontra.audio.intro_music import IntroMusic, TRACK, START_SOUND, GAME_TRACKS, FINALE_TRACK, shuffled_tracks

class IntroMusicTests(unittest.TestCase):
    def test_only_starts_for_visible_opening_and_stops_after_start(self):
        process=Mock();process.poll.return_value=None
        with patch('omacontra.audio.intro_music.subprocess.Popen',return_value=process) as launch:
            music=IntroMusic();music.update(False);music.update(True,True)
            launch.assert_not_called()
            music.update(True);music.update(True)
            self.assertEqual(launch.call_count,1)
            self.assertIn(str(TRACK),launch.call_args.args[0])
            music.update(False);process.terminate.assert_called_once()
            self.assertIsNone(music.process);self.assertIsNone(music.socket)

    def test_pause_resume_and_restart_send_ipc_commands(self):
        music=IntroMusic();music.process=Mock();music.process.poll.return_value=None
        music.paused=False;music.command=Mock()
        music.update(True,True);music.update(True,True)
        music.command.assert_called_once_with('set_property','pause',True)
        music.update(True,False)
        music.command.assert_called_with('set_property','pause',False)
        music.restart();music.command.assert_called_with('seek',0,'absolute')
        music.stop()

    def test_start_impact_replaces_music_once_without_looping(self):
        music=IntroMusic();music.command=Mock()
        music.play_start();count=music.command.call_count;music.play_start()
        self.assertEqual(music.command.call_count,count)
        music.command.assert_any_call('set_property','loop-file','no')
        music.command.assert_any_call('loadfile',str(START_SOUND),'replace')
        music.restart()
        music.command.assert_any_call('loadfile',str(TRACK),'replace')
        self.assertFalse(music.start_effect)

    def test_playlist_plays_whole_tracks_in_order_and_loops_the_list(self):
        process=Mock();process.poll.return_value=None
        with patch('omacontra.audio.intro_music.subprocess.Popen',return_value=process) as launch:
            music=IntroMusic(playlist=GAME_TRACKS);music.update(True)
            args=launch.call_args.args[0]
            self.assertIn('--loop-playlist=inf',args)
            self.assertIn('--loop-file=no',args)
            self.assertEqual(args[args.index('--')+1:],[str(p) for p in GAME_TRACKS])
            self.assertEqual([p.name for p in GAME_TRACKS],[
                'wine-cellar-off-duty-mercenary.mp3',
                'contra.mp3','the-descent.mp3','omacontra-opening-theme.mp3','boss-battle-protocol.mp3'])
            for _ in range(10):music.update(True)
            launch.assert_called_once();music.stop()

    def test_playlist_continues_across_story_levels_death_and_retry(self):
        from omacontra.boss_app import BossApp
        from omacontra.ui.story import Intro
        from omacontra.stages.reaper.combat import Fight
        app=BossApp.__new__(BossApp)
        app.closed=False;app.last=0.;app.placed=False;app.visible=True;app.paused=False
        app.intro=Intro();app.level=1;app.f=Fight()
        app.music=Mock();app.game_music=Mock();app.keyboard=Mock()
        def tick(active):
            with patch('omacontra.boss_app.time.monotonic',return_value=app.last+.02):app.tick()
            app.game_music.update.assert_called_with(active,True)
            app.game_music.select_playlist.assert_called_with(
                (FINALE_TRACK,) if app.level==5 and app.intro is None else GAME_TRACKS)
        tick(False)
        app.intro=Intro(journey=True)
        for index in range(len(app.intro.beats)):
            app.intro.index=index;tick(True)
        app.intro=None
        for level in range(1,6):
            app.level=level
            for state in ('play','dying','dead','won'):
                app.f.state=state;tick(True)
        app.level=5;app.f.state='departure';tick(True)
        app.level=1;app.reset_encounter();tick(True)
        app.game_music.restart.assert_not_called()
        app.game_music.stop.assert_not_called()

    def test_finale_track_switches_once_and_loops_without_restarting_on_retry(self):
        process=Mock();process.poll.return_value=None
        with patch('omacontra.audio.intro_music.subprocess.Popen',return_value=process) as launch:
            music=IntroMusic(playlist=GAME_TRACKS);music.set_volume(63);music.update(True)
            music.select_playlist((FINALE_TRACK,));process.terminate.assert_called_once()
            music.update(True)
            args=launch.call_args.args[0]
            self.assertEqual(args[args.index('--')+1:],[str(FINALE_TRACK)])
            self.assertIn('--loop-playlist=inf',args)
            self.assertIn('--volume=63',args)
            for _ in range(10):
                music.select_playlist((FINALE_TRACK,));music.update(True)
            self.assertEqual(launch.call_count,2)
            music.select_playlist(GAME_TRACKS);music.update(True)
            self.assertEqual(launch.call_count,3)
            music.stop()

    def test_results_and_credits_keep_finale_music_playing_but_hidden_window_pauses(self):
        from types import SimpleNamespace
        from omacontra.boss_app import BossApp
        app=BossApp.__new__(BossApp)
        app.closed=False;app.last=0.;app.placed=True;app.visible=True;app.paused=True
        app.intro=None;app.level=5;app.f=SimpleNamespace(state='won',hp=3)
        app.music=Mock(start_effect=False);app.game_music=Mock();app.area=Mock()
        app.frontend=SimpleNamespace(page='results',result_saved=True,
                                     profile=SimpleNamespace(settings={'music':100,'effects':100}))
        for page in ('results','credits','bosses','confirm'):
            app.frontend.page=page;app.tick()
            app.game_music.update.assert_called_with(True,False)
            app.game_music.select_playlist.assert_called_with((FINALE_TRACK,))
        app.visible=False;app.tick()
        app.game_music.update.assert_called_with(True,True)
        app.visible=True;app.f.state='play';app.frontend.page='pause';app.tick()
        app.game_music.update.assert_called_with(True,True)

    def test_shuffle_contains_every_regular_song_and_excludes_finale(self):
        for _ in range(5):
            tracks=shuffled_tracks()
            self.assertCountEqual(tracks,GAME_TRACKS)
            self.assertEqual(len(tracks),len(set(tracks)))
            self.assertNotIn(FINALE_TRACK,tracks)
        with patch('omacontra.audio.intro_music.random.sample',return_value=list(reversed(GAME_TRACKS))) as shuffle:
            self.assertEqual(shuffled_tracks(),tuple(reversed(GAME_TRACKS)))
            shuffle.assert_called_once_with(GAME_TRACKS,len(GAME_TRACKS))

    def test_missing_player_does_not_break_game_or_retry_every_tick(self):
        with patch('omacontra.audio.intro_music.subprocess.Popen',side_effect=FileNotFoundError),patch('builtins.print'):
            music=IntroMusic();music.update(True);self.assertTrue(music.failed)
            music.update(True);music.stop()

if __name__=='__main__':unittest.main()

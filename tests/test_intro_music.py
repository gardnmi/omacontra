import unittest
from unittest.mock import Mock,patch
from omacontra.audio.intro_music import IntroMusic, TRACK, START_SOUND, GAME_TRACKS

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
                'wine-cellar-off-duty-mercenary.mp3','quattro-run-omarchy-oligarchy.mp3',
                'contra.mp3','the-descent.mp3','omacontra-opening-theme.mp3'])
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
        tick(False)
        app.intro=Intro(journey=True)
        for index in range(len(app.intro.beats)):
            app.intro.index=index;tick(True)
        app.intro=None
        for level in range(1,6):
            app.level=level
            for state in ('play','dying','dead','won'):
                app.f.state=state;tick(True)
        app.level=1;app.reset_encounter();tick(True)
        app.game_music.restart.assert_not_called()
        app.game_music.stop.assert_not_called()

    def test_missing_player_does_not_break_game_or_retry_every_tick(self):
        with patch('omacontra.audio.intro_music.subprocess.Popen',side_effect=FileNotFoundError),patch('builtins.print'):
            music=IntroMusic();music.update(True);self.assertTrue(music.failed)
            music.update(True);music.stop()

if __name__=='__main__':unittest.main()

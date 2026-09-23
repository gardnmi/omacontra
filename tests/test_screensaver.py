import unittest
import cairo
from omacontra.stages.space.screensaver_art import Screensaver, frame_cells, EFFECTS

class ScreensaverTests(unittest.TestCase):
    def test_terminal_rgb_and_block_positions(self):
        frame=' \x1b[38;2;10;20;30m█\x1b[0m\n▀▄'
        self.assertEqual(list(frame_cells(frame)),[
            (1,0,'█',(10,20,30)),(0,1,'▀',(255,255,255)),
            (1,1,'▄',(255,255,255))])

    def test_authentic_effect_frames_and_cycle_boundaries(self):
        s=Screensaver();t=0
        for name in EFFECTS:
            clip=s.clips[name]
            self.assertTrue(clip['engine'].startswith('ttfx'))
            self.assertGreater(len(set(clip['frames'])),20)
            self.assertEqual(s.frame_at(t+.001),(name,0))
            t+=len(clip['frames'])/clip['fps']+.6
        self.assertAlmostEqual(t,s.cycle_duration)
        self.assertEqual(EFFECTS,('beams','rings','blackhole'))
        for cycle in (1,2,10):
            offset=cycle*t
            for name in EFFECTS:
                self.assertEqual(s.frame_at(offset+.001),(name,0))
                clip=s.clips[name]
                offset+=len(clip['frames'])/clip['fps']+.6

    def test_clock_driven_playback_and_frame_cache(self):
        s=Screensaver();surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720)
        c=cairo.Context(surface);s.draw(c,1,1);cached=s.surface;key=s.key
        s.draw(c,1,.5)
        self.assertIs(s.surface,cached);self.assertEqual(s.key,key)
        s.draw(c,1.1,1);self.assertNotEqual(s.key,key)
        s.draw(c,0,1);self.assertEqual(s.key,('beams',0))

    def test_runtime_does_not_parse_or_draw_terminal_text(self):
        from unittest.mock import patch
        s=Screensaver();surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720)
        with patch('omacontra.stages.space.screensaver_art.frame_cells',side_effect=AssertionError('runtime text parsing')):
            for t in (0,1,10,20,50,80):s.draw(cairo.Context(surface),t,1)
        self.assertEqual((s.surface.get_width(),s.surface.get_height()),(576,300))
        self.assertLessEqual(s.prepared_frame.cache_info().currsize,4)

if __name__=='__main__':unittest.main()

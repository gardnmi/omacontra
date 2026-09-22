import unittest
import cairo
from cutscene_review import Review,SCENES

class ReviewTests(unittest.TestCase):
    def test_every_scene_can_seek_forward_and_backward_and_render(self):
        surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720)
        for name in SCENES:
            with self.subTest(scene=name):
                review=Review(name)
                for t in (0,review.duration*.6,review.duration,review.duration*.2):
                    review.seek(t);review.draw(cairo.Context(surface))
                    self.assertAlmostEqual(review.time,t)
    def test_pause_speed_and_end_hold(self):
        review=Review('ending');review.speed=.5;review.step(2)
        self.assertEqual(review.time,1)
        review.playing=False;review.step(2);self.assertEqual(review.time,1)
        review.playing=True;review.seek(review.duration-.1);review.step(1)
        self.assertEqual(review.time,review.duration);self.assertFalse(review.playing)
        self.assertEqual(review.f.state,'ending')

if __name__=='__main__':unittest.main()

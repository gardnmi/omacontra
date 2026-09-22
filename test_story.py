import unittest
import cairo
from story import Intro, BEATS, COVER_AT
from art import Renderer,W,H


class IntroTests(unittest.TestCase):
    def test_order_includes_separate_resolve_before_cover(self):
        intro=Intro()
        kinds=[]
        for _ in BEATS:
            kinds.append(intro.beat.kind)
            intro.advance()
        self.assertEqual(kinds,['story','containment','labs','threat','cellar','resolve','cover'])
        intro.advance()
        self.assertEqual(intro.beat.kind,'cover')

    def test_new_story_plays_after_start_and_finishes(self):
        intro=Intro(journey=True)
        self.assertEqual(intro.beat.kind,'cellar')
        for _ in range(5):intro.advance()
        self.assertTrue(intro.finished)
        intro.reset();self.assertFalse(intro.finished)
        intro.step(100);self.assertTrue(intro.finished)

    def test_wallpaper_arrival_waits_for_walk_before_dialogue(self):
        intro=Intro(journey=True);intro.index=len(intro.beats)-1
        intro.age=2.1;self.assertEqual(intro.typed_lines,('',))
        intro.age=4.5
        self.assertEqual(intro.typed_lines,("DHH: AM I IN AN OMARCHY MACHINE?",))
        renderer=Renderer()
        surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H)
        renderer.draw(cairo.Context(surface),intro,W,H)
        self.assertEqual(renderer.arrival_hero.y,renderer.arrival_hero.floor)
        self.assertFalse(renderer.arrival_hero.moving)

    def test_start_confirmation_runs_once_and_respects_pause(self):
        intro=Intro();self.assertFalse(intro.request_start())
        intro.index=len(intro.beats)-1
        self.assertTrue(intro.request_start());self.assertFalse(intro.request_start())
        intro.step(.5);intro.paused=True;intro.step(2)
        self.assertEqual(intro.start_age,.5);self.assertFalse(intro.start_finished)
        intro.paused=False;intro.step(.7);self.assertFalse(intro.start_finished)
        intro.step(1.3);self.assertTrue(intro.start_finished)
        intro.reset();self.assertIsNone(intro.start_age)

    def test_natural_timing_and_cover_holds(self):
        intro=Intro();intro.step(COVER_AT+.5)
        self.assertEqual(intro.beat.kind,'cover')
        self.assertAlmostEqual(intro.age,.5)
        intro.step(500)
        self.assertEqual(intro.beat.kind,'cover')

    def test_pause_and_restart(self):
        intro=Intro();intro.step(12);intro.paused=True
        state=(intro.index,intro.age);intro.step(20)
        self.assertEqual((intro.index,intro.age),state)
        intro.reset()
        self.assertEqual((intro.index,intro.age,intro.paused),(0,0,False))

    def test_reassurance_punchline_has_its_own_beat(self):
        intro=Intro();intro.index=next(i for i,b in enumerate(BEATS) if b.kind=='resolve');intro.age=1
        self.assertTrue(intro.typed_lines[0]);self.assertFalse(intro.typed_lines[1])
        intro.step(1.5);self.assertEqual(intro.typed_lines[1],'BECAUSE YOU CAN FIX ANYTHING.')

    def test_original_cellar_is_animated(self):
        renderer=Renderer();frames=[]
        for age in (1.,3.5):
            surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H)
            renderer.wine_cellar(cairo.Context(surface),age)
            frames.append(bytes(surface.get_data()))
        self.assertNotEqual(*frames)

    def test_every_scene_renders_at_multiple_sizes(self):
        renderer=Renderer()
        for size in ((W,H),(640,360)):
            surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,*size)
            for index in range(len(BEATS)):
                for age in (.1,2.5,4.5):
                    intro=Intro();intro.index=index;intro.age=age
                    renderer.draw(cairo.Context(surface),intro,*size)


if __name__=='__main__':unittest.main()

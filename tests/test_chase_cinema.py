import unittest
from omacontra.stages.highway.chase import Chase
from omacontra.stages.highway.chase_cinema import ChaseCinema, INTRO_DURATION, PANEL

class CinemaTests(unittest.TestCase):
    def test_intro_expands_to_exact_gameplay_view(self):
        f=Chase();cinema=ChaseCinema()
        self.assertEqual(cinema.framing(f)[0],PANEL)
        cinema.age=INTRO_DURATION
        bounds,zoom,focus=cinema.framing(f)
        self.assertEqual(bounds,(0,0,1280,720));self.assertEqual(zoom,1);self.assertEqual(focus,(640,360))
        self.assertTrue(cinema.finished)
    def test_outro_holds_panel_and_skip_only_finishes_intro(self):
        f=Chase();c=ChaseCinema('outro');c.age=30;c.skip()
        self.assertFalse(c.finished);self.assertEqual(c.framing(f)[0],PANEL)
        c=ChaseCinema();c.skip();self.assertTrue(c.finished)
    def test_rendering_cinema_does_not_advance_combat(self):
        import cairo
        from omacontra.stages.highway.chase_art import ChaseRenderer
        f=Chase();r=ChaseRenderer();initial=(f.clock,f.distance,f.attack_timer,f.hp,f.state)
        s=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720)
        for kind in ('intro','outro'):
            for age in (0,.4,2,3.8,5.8,6.4):
                c=ChaseCinema(kind);c.age=age;c.draw(cairo.Context(s),r,f)
        self.assertEqual((f.clock,f.distance,f.attack_timer,f.hp,f.state),initial)
    def test_car_crests_hill_flies_toward_camera_and_exits_left(self):
        cinema=ChaseCinema('outro');poses=[]
        for age in (0,.95,1.95,2.95,4.2):
            cinema.age=age;poses.append(cinema.rally_pose())
        self.assertLess(poses[0][2],200)
        self.assertLess(poses[2][1],poses[0][1])
        self.assertGreater(poses[3][2],poses[2][2])
        self.assertLess(poses[4][0]+poses[4][2]/2,0)
        for age in (.95,1.45,1.95,2.45,2.95):
            cinema.age=age-.001;before=cinema.rally_pose()
            cinema.age=age+.001;after=cinema.rally_pose()
            self.assertLess(max(abs(a-b) for a,b in zip(before,after)),3)

    def test_host_freezes_combat_and_enters_outro_once(self):
        from unittest.mock import Mock,patch
        from omacontra.boss_app import BossApp
        from omacontra.input_state import KeyboardState
        app=BossApp.__new__(BossApp)
        app.music=Mock()
        app.closed=False;app.last=0.;app.placed=True;app.visible=True;app.intro=None;app.paused=False
        app.chase_cinema=ChaseCinema();app.keyboard=KeyboardState();app.keys=app.keyboard.keys
        app.slide_requested=False;app.shooting=False;app.aim=None;app.area=Mock()
        app.level=2;app.f=Chase();app.chase_outro_seen=False
        with patch('omacontra.boss_app.time.monotonic',return_value=.02):app.tick()
        self.assertEqual(app.f.clock,0);self.assertGreater(app.chase_cinema.age,0)
        app.chase_cinema.skip()
        with patch('omacontra.boss_app.time.monotonic',return_value=.04):app.tick()
        self.assertIsNone(app.chase_cinema)
        app.f.state='won'
        with patch('omacontra.boss_app.time.monotonic',return_value=.06):app.tick()
        self.assertEqual(app.chase_cinema.kind,'outro');cinema=app.chase_cinema
        with patch('omacontra.boss_app.time.monotonic',return_value=.08):app.tick()
        self.assertIs(app.chase_cinema,cinema);self.assertGreater(cinema.age,0)

if __name__=='__main__':unittest.main()

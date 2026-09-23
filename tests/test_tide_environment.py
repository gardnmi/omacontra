import unittest
import cairo
from omacontra.stages.harbor.tidebreaker import Tidebreaker
from omacontra.stages.harbor.tide_environment import TideEnvironment

class TideEnvironmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.env=TideEnvironment()
    def render(self,f):
        s=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720);c=cairo.Context(s)
        self.env.background(c,f);self.env.deck(c,f)
        return bytes(s.get_data())
    def test_motion_uses_simulation_time_and_does_not_mutate_fight(self):
        for stage in (0,1):
            f=Tidebreaker()
            if stage:f.advance_guardian()
            f.clock=1;before=(f.x,f.y,f.hp,f.deck_slope)
            a=self.render(f);self.assertEqual(a,self.render(f))
            f.clock=2;self.assertNotEqual(a,self.render(f))
            self.assertEqual(before,(f.x,f.y,f.hp,f.deck_slope))
    def test_wave_death_is_playable_and_preserves_position_and_deck(self):
        f=Tidebreaker();f.x=640;f.deck_slope=.08;f.deck_roll=3;f.y=f.floor
        before=(f.x,f.y,f.deck_slope,f.deck_roll)
        f.begin_reveal()
        self.assertEqual(f.state,'play');self.assertEqual(f.stage,1)
        self.assertEqual(before,(f.x,f.y,f.deck_slope,f.deck_roll))
        self.assertEqual(len(f.guardians),2);self.assertGreater(f.wave_reveal,0)
        f.step(.02,move=-1);self.assertLess(f.x,640)
        self.assertEqual(f.sfx_events.count('wave_death'),1)
        for _ in range(125):f.step(.02)
        self.assertEqual(f.wave_reveal,0)

    def test_guardian_transition_brings_outside_player_inside_preserving_jump(self):
        for x,expected in ((40,282),(1200,938)):
            f=Tidebreaker();f.x=x;f.deck_slope=.08;f.y=f.floor-90
            f.begin_reveal()
            self.assertEqual(f.x,expected)
            self.assertAlmostEqual(f.floor-f.y,90)
            self.assertEqual(f.respawn_anchor,(expected,f.floor))

    def test_guardian_boundaries_stop_running_sliding_and_air_dash(self):
        for transition in ('begin_reveal','advance_guardian'):
            for move,edge in ((-1,282),(1,938)):
                for motion in ('run','slide','dash'):
                    with self.subTest(transition=transition,move=move,motion=motion):
                        f=Tidebreaker();getattr(f,transition)();f.invuln=999
                        f.x=edge;f.y=f.floor-(100 if motion=='dash' else 0)
                        f.step(.04,move=move,slide=motion!='run',slide_pressed=motion!='run')
                        self.assertEqual(f.x,edge)

    def test_wave_still_allows_full_deck_movement(self):
        for x,move in ((100,-1),(1150,1)):
            f=Tidebreaker();f.x=x;f.invuln=999
            f.step(.04,move=move)
            self.assertGreater((f.x-x)*move,0)

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
        f=Tidebreaker();f.x=1030;f.deck_slope=.08;f.deck_roll=3;f.y=f.floor
        before=(f.x,f.y,f.deck_slope,f.deck_roll,f.rects['arena'])
        f.begin_reveal()
        self.assertEqual(f.state,'play');self.assertEqual(f.stage,1)
        self.assertEqual(before,(f.x,f.y,f.deck_slope,f.deck_roll,f.rects['arena']))
        self.assertEqual(len(f.guardians),2);self.assertGreater(f.wave_reveal,0)
        f.step(.02,move=-1);self.assertLess(f.x,1030)
        self.assertEqual(f.sfx_events.count('wave_death'),1)
        for _ in range(125):f.step(.02)
        self.assertEqual(f.wave_reveal,0)

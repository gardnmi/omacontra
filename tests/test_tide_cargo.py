import unittest
from omacontra.stages.harbor.tidebreaker import Tidebreaker, TideHazard

class CargoTests(unittest.TestCase):
    def test_restraints_release_after_intro_and_tilt_accelerates_crate(self):
        f=Tidebreaker();c=f.cargo;f.deck_slope=.06
        c.step(f,1);self.assertFalse(c.released);self.assertEqual(c.x,650)
        c.age=4.5;c.step(f,.04)
        self.assertTrue(c.released);self.assertGreater(c.vx,0)

    def test_crate_crosses_old_interior_stop(self):
        f=Tidebreaker();c=f.cargo;c.released=True;c.x=710;c.vx=220
        f.deck_slope=.08
        for _ in range(40):c.step(f,.02)
        self.assertGreater(c.x,850)
        c.x=125;c.vx=-220;f.deck_slope=-.08
        for _ in range(10):c.step(f,.02)
        self.assertLess(c.x,100)
        for _ in range(60):c.step(f,.02)
        self.assertGreaterEqual(c.x,c.bounds[0])

    def test_overhead_wave_does_not_brake_cart(self):
        for active in (False,True):
            f=Tidebreaker();c=f.cargo;c.released=True;c.x=640;c.vx=220
            f.deck_slope=.08
            if active:f.hazards=[TideHazard('ceiling',1000)]
            else:f.tide_warning='ceiling'
            for _ in range(40):c.step(f,.02)
            self.assertGreater(c.x,800);self.assertGreater(c.vx,200)

    def test_ceiling_buildup_launches_on_schedule_in_every_phase(self):
        for phase in (1,2,3):
            f=Tidebreaker();f.wave_phase=phase;f.invuln=999
            f.cargo.released=True;f.cargo.x=640;f.cargo.vx=350
            if phase==3:f.combo_index=1;f.combo_wait=0;f.step(.02)
            else:f.start_warning('ceiling')
            for _ in range(60):f.step(.02)
            self.assertIsNone(f.tide_warning)
            self.assertTrue(any(h.kind=='ceiling' for h in f.hazards))
            for _ in range(100):f.step(.02)
            self.assertTrue(any(h.kind=='ceiling' and h.x<640 for h in f.hazards))

    def test_crate_contact_costs_health_but_single_jump_clears_it(self):
        for jump in (False,True):
            f=Tidebreaker();f.x=300;f.y=f.floor;f.invuln=0;f.tide_timer=999
            c=f.cargo;c.released=True;c.x=430;c.vx=-220
            for i in range(30):f.step(.02,jump=jump and i==0,move=1 if jump else 0)
            self.assertEqual(f.hp,6 if jump else 5)

    def test_blood_water_transition_is_gradual(self):
        f=Tidebreaker();f.wave_phase=3;f.invuln=999
        f.step(.02)
        self.assertGreater(f.ocean_rage,0);self.assertLess(f.ocean_rage,.02)
        for _ in range(250):f.step(.02)
        self.assertGreater(f.ocean_rage,.95)

    def test_crate_stops_with_wave_phase(self):
        f=Tidebreaker();f.advance_guardian();old=f.cargo.x
        for _ in range(100):f.step(.02)
        self.assertEqual(f.cargo.x,old)

    def test_second_crate_releases_in_wave_two_and_pair_does_not_overlap(self):
        from omacontra.stages.harbor.tide_cargo import step_pair
        f=Tidebreaker();a,b=f.cargos
        self.assertEqual(len(f.cargos),2)
        b.age=10;b.step(f,.02);self.assertFalse(b.released)
        f.wave_phase=2;b.step(f,.02);self.assertTrue(b.released)
        a.released=True;a.x=600;b.x=695;a.vx=200;b.vx=-150
        step_pair(f,.02)
        self.assertGreaterEqual(b.x-a.x,100)
        self.assertLess(a.vx,0);self.assertGreater(b.vx,0)

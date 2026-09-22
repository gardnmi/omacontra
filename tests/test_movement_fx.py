import math
import unittest

from omacontra.stages.reaper.combat import Fight
from omacontra.rendering.hero_pose import BARREL_LENGTH, muzzle_position, weapon_pose, carry_frame
from omacontra.rendering import movement_fx


class MovementFeedbackTests(unittest.TestCase):
    def test_start_and_reverse_kick_dust_without_continuous_running_cloud(self):
        f=Fight();f.step(.02,move=1)
        self.assertEqual(len(f.motion_dust),6)
        self.assertTrue(all(p.vx<0 for p in f.motion_dust))
        f.step(.02,move=1)
        self.assertEqual(len(f.motion_dust),6)
        f.step(.02,move=-1)
        self.assertEqual(len(f.motion_dust),12)
        self.assertTrue(all(p.vx>0 for p in f.motion_dust[-6:]))

    def test_slide_leaves_trail_and_dust_expires_after_death(self):
        f=Fight();f.step(.02,move=1,slide=True)
        first=len(f.motion_dust)
        for _ in range(8):f.step(.02,move=1,slide=True)
        self.assertGreater(len(f.motion_dust),first)
        self.assertLessEqual(len(f.motion_dust),42)
        f.state='dead'
        for _ in range(30):f.step(.02)
        self.assertFalse(f.motion_dust)

    def test_airborne_movement_emits_no_ground_dust_or_run_steps(self):
        f=Fight();f.step(.02,move=1,jump=True)
        self.assertFalse(f.motion_dust)
        phase=f.run_phase
        for _ in range(8):f.step(.02,move=1)
        self.assertEqual(f.run_phase,phase)
        self.assertFalse(f.motion_dust)

    def test_moving_muzzle_stays_on_weapon_for_every_pose_and_direction(self):
        f=Fight();f.moving=True
        for facing in (-1,1):
            f.facing=facing;f.run_direction=facing
            for frame in range(6):
                f.run_phase=frame+.5
                for aim in (None,(700,100),(50,650)):
                    x,y,a=weapon_pose(f,aim);mx,my=muzzle_position(f,aim)
                    self.assertAlmostEqual(mx,x+math.cos(a)*BARREL_LENGTH)
                    self.assertAlmostEqual(my,y+math.sin(a)*BARREL_LENGTH)

    def test_stationary_player_does_not_spawn_dust(self):
        f=Fight()
        for _ in range(10):f.step(.02)
        self.assertFalse(f.motion_dust)

    def test_running_carry_swings_but_held_fire_stays_steady_between_shots(self):
        f=Fight();frames=set()
        for _ in range(60):
            f.step(.01,move=1)
            frames.add(carry_frame(f))
        self.assertEqual(frames,{0,2,3})
        for _ in range(25):
            f.step(.01,move=1,shoot=True)
            self.assertEqual(weapon_pose(f)[2],0)
            self.assertIsNone(carry_frame(f))
        for _ in range(10):f.step(.01,move=1)
        self.assertIsNotNone(carry_frame(f))

    def test_carry_swing_mirrors_without_detaching_shoulder(self):
        f=Fight();f.moving=True
        for index,phase in enumerate((.5,1.5,2.6,3.5,4.5,5.6)):
            f.run_phase=phase;f.facing=f.run_direction=1
            rx,ry,ra=weapon_pose(f)
            self.assertEqual(carry_frame(f),(3,3,2,0,0,2)[index])
            f.shoot_held=True
            self.assertEqual(weapon_pose(f)[:2],(rx,ry))
            f.shoot_held=False;f.facing=f.run_direction=-1
            lx,ly,la=weapon_pose(f)
            self.assertEqual(carry_frame(f),(3,3,2,0,0,2)[index])
            self.assertAlmostEqual(la,math.pi-ra)
            self.assertAlmostEqual(rx-f.x,f.x-lx)
            self.assertEqual(ry,ly)

    def test_carry_swing_does_not_change_airborne_or_slide_pose(self):
        f=Fight();f.moving=True;f.run_phase=1
        f.y=f.floor-30
        self.assertIsNone(carry_frame(f))
        self.assertEqual(weapon_pose(f)[2],0)
        f.y=f.floor;f.slide_time=.2;f.duck=True
        self.assertIsNone(carry_frame(f))
        self.assertEqual(weapon_pose(f)[2],0)


if __name__=='__main__':unittest.main()

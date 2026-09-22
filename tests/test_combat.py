import unittest
from omacontra.stages.reaper.combat import Fight, Bullet, segment_hit

class CombatTests(unittest.TestCase):
    def test_jump_needs_release_and_lands(self):
        f=Fight();ground=f.y;f.step(.04,jump=True);self.assertLess(f.y,ground)
        for _ in range(80):f.step(.04,jump=True)
        self.assertEqual(f.y,f.floor)
        f.step(.01,jump=False);f.step(.01,jump=True);self.assertLess(f.y,f.floor)

    def test_double_jump_needs_new_press_and_stops_at_two(self):
        f=Fight();f.step(.02,jump=True)
        for _ in range(8):f.step(.02,jump=True)
        self.assertEqual(f.jumps_used,1)
        f.step(.02);f.step(.02,jump=True)
        self.assertEqual(f.jumps_used,2);self.assertLess(f.vy,-400)
        self.assertGreater(f.jump_flash,0)
        f.step(.02);vy=f.vy;f.step(.02,jump=True)
        self.assertEqual(f.jumps_used,2);self.assertGreater(f.vy,vy)
        for _ in range(100):f.step(.02)
        self.assertEqual(f.y,f.floor);self.assertEqual(f.jumps_used,0)
        f.step(.02,jump=True);self.assertEqual(f.jumps_used,1)

    def test_slide_moves_in_input_direction_and_can_fire(self):
        f=Fight();f.facing=1;x=f.x
        f.step(.02,move=-1,slide=True,shoot=True,aim=(1000,100))
        self.assertTrue(f.sliding);self.assertEqual(f.slide_direction,-1)
        self.assertLess(f.x,x-9);self.assertEqual(f.facing,1)
        self.assertEqual(len(f.shots),1)
        self.assertEqual(f.player_center[1],f.y-32)

    def test_held_shift_slides_once_then_release_rearms(self):
        f=Fight();f.invuln=99;f.step(.02,slide=True)
        self.assertTrue(f.sliding)
        for _ in range(180):f.step(.02,slide=True)
        self.assertFalse(f.sliding)
        f.step(.02,slide=False);f.step(.02,slide=True)
        self.assertTrue(f.sliding)

    def test_airborne_hold_does_not_slide_after_buffer_expires(self):
        f=Fight();f.step(.02,jump=True);f.step(.02,slide=True)
        for _ in range(60):f.step(.02,slide=True)
        self.assertEqual(f.y,f.floor);self.assertFalse(f.sliding)

    def test_quick_tap_between_frames_is_preserved_once(self):
        f=Fight();f.step(.02,slide=False,slide_pressed=True)
        self.assertTrue(f.sliding)
        for _ in range(60):f.step(.02)
        self.assertFalse(f.sliding)
        f.step(.02,slide=False,slide_pressed=True)
        self.assertTrue(f.sliding)

    def test_early_slide_tap_is_buffered_until_ready(self):
        f=Fight();f.slide_cooldown=.12
        f.step(.02,slide=True);self.assertFalse(f.sliding)
        for _ in range(6):f.step(.02)
        self.assertTrue(f.sliding)

    def test_slide_cooldown_and_jump_cancel(self):
        f=Fight();f.step(.02,slide=True);f.step(.02,jump=True)
        self.assertFalse(f.sliding);self.assertEqual(f.jumps_used,1)
        # A quick landing doesn't bypass the cooldown.
        f.y=f.floor;f.vy=0;f.step(.02,slide=True)
        self.assertFalse(f.sliding)

    def test_slide_ducks_torso_shots_but_not_scythe(self):
        for kind,y_offset,expected in [('bullet',52,5),('scythe',12,4)]:
            f=Fight();f.invuln=0;f.step(.01,slide=True)
            f.shots=[Bullet(f.x+10,f.floor-y_offset,0,0,True,5,kind=kind)]
            f.step(.02,slide=True)
            self.assertEqual(f.hp,expected)

    def test_slide_stays_inside_arena(self):
        f=Fight();f.x=23;f.step(.04,move=-1,slide=True)
        self.assertEqual(f.x,22)
        reset=Fight();self.assertFalse(reset.sliding);self.assertEqual(reset.jumps_used,0)

    def test_shield_and_exposure_cycle(self):
        f=Fight();x,y=f.body;f.hit_target(x-76,y,x,y,50);self.assertEqual(f.boss_hp,180)
        for role in f.nodes:
            x,y=f.node_center(role);f.hit_target(x,y,x+1,y,100)
        self.assertFalse(f.shielded);x,y=f.body;f.hit_target(x,y,x+1,y,20);self.assertEqual(f.boss_hp,160)
        for _ in range(280):f.step(.04)
        self.assertTrue(f.shielded)

    def test_machine_gun_is_single_shot_without_pickups(self):
        f=Fight();f.step(.01,shoot=True)
        self.assertEqual(len(f.shots),1);self.assertEqual(f.weapon,'machine')
        for _ in range(1000):f.step(.04)
        self.assertFalse(hasattr(f,'pickups'))

    def test_run_and_fire_matches_movement_without_fire(self):
        runner=Fight();shooter=Fight()
        for _ in range(50):
            runner.step(.01,move=1)
            shooter.step(.01,move=1,shoot=True,aim=(0,0))
            self.assertEqual(shooter.facing,-1)
        self.assertAlmostEqual(runner.x,shooter.x)
        self.assertAlmostEqual(runner.run_phase,shooter.run_phase)
        self.assertTrue(shooter.moving)

    def test_upward_aim_keeps_running_legs(self):
        from omacontra.stages.reaper.battle_art import hero_frames
        f=Fight();legs=set()
        for _ in range(50):
            f.step(.01,move=1,shoot=True,aim=(0,0))
            lower,upper=hero_frames(f,(0,0));legs.add(lower)
            self.assertEqual(upper,0)
        self.assertEqual(legs,{1,2,3})

    def test_bullets_start_at_rendered_barrel_in_every_pose(self):
        from omacontra.rendering.hero_pose import muzzle_position
        for direction in (-1,1):
            for pose in ('idle','run','jump','duck','slide','up'):
                with self.subTest(direction=direction,pose=pose):
                    f=Fight();f.facing=direction
                    if pose=='jump':f.y-=80
                    aim=(f.x+direction*500,0 if pose=='up' else f.player_center[1])
                    f.step(.01,move=direction if pose=='run' else 0,
                           duck=pose=='duck',slide=pose=='slide',shoot=True,aim=aim)
                    bullet=f.shots[0];mx,my=muzzle_position(f,f.aim_target)
                    self.assertAlmostEqual(bullet.x-bullet.vx*.01,mx)
                    self.assertAlmostEqual(bullet.y-bullet.vy*.01,my)
                    self.assertGreater((aim[0]-mx)*bullet.vx+(aim[1]-my)*bullet.vy,0)

    def test_barrel_offsets_and_mirror(self):
        from omacontra.rendering.hero_pose import muzzle_position
        f=Fight();x,y=muzzle_position(f)
        self.assertAlmostEqual(x-f.x,38.85);self.assertAlmostEqual(y-f.y,-59.8)
        f.facing=-1;left,ly=muzzle_position(f)
        self.assertAlmostEqual(left-f.x,-38.85);self.assertEqual(ly,y)
        f.slide_time=.3;f.duck=True;x,y=muzzle_position(f)
        self.assertAlmostEqual(x-f.x,-36.25);self.assertAlmostEqual(y-f.y,-31.5)

    def test_jump_arm_stays_at_shoulder_while_aiming_and_moving(self):
        from omacontra.rendering.hero_pose import weapon_pose
        for direction in (-1,1):
            f=Fight();f.facing=direction
            for height in (2,80,180):
                f.y=f.floor-height
                for target_y in (0,f.y,720):
                    x,y,_=weapon_pose(f,(f.x+direction*500,target_y))
                    # The socket follows the shoulder of the tucked body frame.
                    self.assertAlmostEqual(x,f.x-6*direction)
                    self.assertAlmostEqual(y,f.y-43.4)

    def test_weapon_axis_matches_bullets_at_all_angles(self):
        from omacontra.rendering.hero_pose import weapon_pose, muzzle_position, BARREL_LENGTH
        import math
        for angle in (0,.4,1.57,2.5,3.14,-2.5,-1.57,-.4):
            for sliding in (False,True):
                f=Fight();f.invuln=99
                aim=(f.x+math.cos(angle)*300,f.y-50+math.sin(angle)*300)
                f.step(.01,shoot=True,aim=aim,slide=sliding)
                px,py,a=weapon_pose(f,f.aim_target);mx,my=muzzle_position(f,f.aim_target)
                b=f.shots[0]
                self.assertAlmostEqual((mx-px)*b.vy-(my-py)*b.vx,0,places=8)
                self.assertAlmostEqual(math.hypot(mx-px,my-py),BARREL_LENGTH)
                self.assertAlmostEqual(b.vx,math.cos(a)*800)
                self.assertAlmostEqual(b.vy,math.sin(a)*800)

    def test_close_cursor_does_not_reverse_bullet_direction(self):
        f=Fight();f.step(.01,shoot=True,aim=(f.x+1,f.y-63.4))
        self.assertGreater(f.shots[0].vx,0)

    def test_scythe_counter_hitboxes(self):
        from omacontra.stages.reaper.combat import wave_hits
        floor=693
        # Standing and crouching are too tall; sliding fits below the high wave.
        self.assertTrue(wave_hits('high',floor,180,170,180,floor))
        self.assertTrue(wave_hits('high',floor,180,170,180,floor,duck=True))
        self.assertFalse(wave_hits('high',floor,180,170,180,floor,sliding=True))
        self.assertTrue(wave_hits('double',floor,180,170,180,floor-100))
        self.assertFalse(wave_hits('double',floor,180,170,180,floor-165))
        self.assertFalse(wave_hits('low',floor,180,170,180,floor-85))
        self.assertTrue(wave_hits('low',floor,180,170,180,floor,sliding=True))

    def test_scythe_patterns_and_spacing(self):
        f=Fight()
        for expected in [('dash',),('double',),('high',),('low','high','low')]:
            f.prepare_scythe();self.assertEqual(f.scythe_pattern,expected)
        f.attack('scythe')
        self.assertEqual(f.shots[-1].kind,'scythe_low')
        self.assertEqual(len(f.wave_queue),2)
        f.invuln=99
        for _ in range(29):f.step(.04)
        self.assertTrue(any(b.kind=='scythe_high' for b in f.shots))
        self.assertEqual(len(f.wave_queue),1)
        for _ in range(29):f.step(.04)
        self.assertEqual(len(f.wave_queue),0)
        self.assertEqual(f.shots[-1].kind,'scythe_low')
        self.assertGreater(f.shots[-1].x,750)

    def test_sweep_must_be_cleared_from_above(self):
        for airborne,dash in ((False,False),(False,True),(True,False),(True,True)):
            f=Fight();f.invuln=0;f.attack_timer=999
            if airborne:f.y=f.floor-90
            f.shots=[Bullet(f.x+15,f.floor-34,-200,0,True,7,kind='scythe_dash')]
            hp=f.hp
            f.step(.01,move=1,slide_pressed=dash)
            self.assertEqual(f.hp,hp if airborne else hp-1)

    def test_jump_dash_physically_clears_wide_sweep(self):
        for dash in (False,True):
            f=Fight();f.invuln=0;f.attack_timer=999;f.x=280
            f.shots=[Bullet(535,f.floor-34,-200,0,True,7,kind='scythe_dash')]
            for i in range(85):
                f.step(.01,move=1,jump=i==0,slide_pressed=dash and i==27)
            self.assertEqual(f.hp,5 if dash else 4)

    def test_curtain_introduction_and_pair(self):
        f=Fight();f.prepare_scythe();f.attack('scythe')
        self.assertEqual(f.shots[-1].vx,-200)
        self.assertEqual(f.wave_queue,[])
        self.assertIn('AIR DASH OVER',f.notice)
        f.scythe_pattern=('dash','dash');f.attack('scythe')
        self.assertEqual(f.shots[-1].vx,-280)
        self.assertEqual(f.wave_queue,[(2.,'dash')])

    def test_double_jump_physically_clears_tall_wave(self):
        f=Fight();f.step(.02,jump=True)
        for _ in range(18):f.step(.02)
        self.assertLess(f.floor-f.y,140)
        f.step(.02,jump=True)
        for _ in range(17):f.step(.02)
        self.assertGreater(f.floor-f.y,150)

    def test_scythe_sequence_canceled_on_victory(self):
        f=Fight();f.scythe_pattern=('low','high','low');f.attack('scythe')
        f.nodes={'eye':0,'raven':0};f.exposed=11
        x,y=f.body;f.hit_target(x,y,x+1,y,200)
        self.assertFalse(f.wave_queue);self.assertFalse(f.shots)

    def test_projectiles_hit_head_and_legs_not_just_chest(self):
        for height in (7,38,72):
            f=Fight();f.invuln=0
            f.shots=[Bullet(f.x-40,f.y-height,2000,0,True,kind='skull')]
            f.step(.04);self.assertEqual(f.hp,4)

    def test_hitboxes_follow_pose_and_visual_projectile_size(self):
        f=Fight();b=Bullet(f.x+29,f.y-35,0,0,True,kind='skull')
        self.assertTrue(f.projectile_hits_player(b,b.x,b.y))
        b.x=f.x+45;self.assertFalse(f.projectile_hits_player(b,b.x,b.y))
        f.slide_time=.3;f.duck=True
        b.x=f.x;b.y=f.floor-70
        self.assertFalse(f.projectile_hits_player(b,b.x,b.y))
        f.slide_time=0;f.duck=False
        self.assertTrue(f.projectile_hits_player(b,b.x,b.y))
        f.y-=110;b.y=f.floor-12
        self.assertFalse(f.projectile_hits_player(b,b.x,b.y))

    def test_eye_and_raven_fire_multiple_large_volleys(self):
        for kind,projectile,count in [('aimed','skull',3),('raven','raven',4)]:
            f=Fight();f.invuln=99;f.attack(kind)
            self.assertEqual(sum(b.kind==projectile for b in f.shots),count)
            self.assertTrue(f.burst_queue)
            for _ in range(7):f.step(.04)
            self.assertEqual(sum(b.kind==projectile for b in f.shots),count*2)
            self.assertTrue(all(abs(b.vx)+abs(b.vy)>240 for b in f.shots))

    def test_new_attack_cadence_fires_eye_and_ravens_early(self):
        f=Fight();f.invuln=99;seen=set()
        for _ in range(175):
            f.step(.04);seen.update(b.kind for b in f.shots)
        self.assertTrue({'skull','raven'}<=seen)

    def test_scythe_wake_emits_and_expires_with_bounded_particles(self):
        f=Fight(seed=3);f.invuln=99;f.scythe_pattern=('double',);f.attack('scythe')
        for _ in range(20):f.step(.02)
        self.assertTrue(any(p.color=='smoke' for p in f.particles))
        self.assertTrue(any(p.color=='gold' for p in f.particles))
        self.assertLessEqual(len(f.particles),600)
        f.shots=[];f.attack_timer=99
        for _ in range(60):f.step(.02)
        self.assertFalse(f.particles)

    def test_air_dash_once_per_airtime_and_landing_recharges(self):
        f=Fight();f.attack_timer=99;f.invuln=0
        f.step(.02,jump=True);f.step(.02)
        y=f.y;x=f.x
        f.step(.02,move=1,slide_pressed=True)
        self.assertTrue(f.dash_used);self.assertGreater(f.dash_time,0)
        self.assertAlmostEqual(f.y,y);self.assertGreater(f.x-x,10)
        self.assertEqual(f.invuln,0)  # Dash requires an actual clear path.
        for _ in range(12):f.step(.02)
        f.step(.02,slide_pressed=True);self.assertEqual(f.dash_time,0)
        for _ in range(90):f.step(.02)
        self.assertEqual(f.y,f.floor);self.assertFalse(f.dash_used)
        f.step(.02,jump=True);f.step(.02,move=-1,slide_pressed=True)
        self.assertGreater(f.dash_time,0);self.assertEqual(f.dash_direction,-1)

    def test_phase_three_spread_has_jump_escape_but_hits_stationary_player(self):
        for dodge in (False,True):
            f=Fight();f.invuln=0;f.boss_hp=40;f.attack_timer=99;f.attack('aimed')
            for n in range(160):
                f.step(.02,move=-1 if dodge and n>=40 else 0,jump=dodge and n==40)
            self.assertEqual(f.hp,5 if dodge else 4)

    def test_followup_volley_locks_aim_and_destroyed_node_stops_firing(self):
        import math
        f=Fight();f.boss_hp=40;f.attack('aimed')
        first=[math.atan2(b.vy,b.vx) for b in f.shots]
        f.shots=[];f.x+=300;f.fire_volley('aimed')
        self.assertEqual(first,[math.atan2(b.vy,b.vx) for b in f.shots])
        self.assertEqual(len(first),5)
        f.shots=[];f.nodes['eye']=0;f.fire_volley('aimed');self.assertFalse(f.shots)

    def test_scythe_waits_for_existing_spread(self):
        f=Fight();f.attack_number=3;f.attack_timer=0
        f.shots=[Bullet(200,200,1,0,True,kind='skull')]
        f.step(.02);self.assertIsNone(f.warning)
        f.shots=[]
        for _ in range(8):f.step(.02)
        self.assertEqual(f.warning,'scythe')

    def test_patrols_move_and_hitboxes_follow_them(self):
        f=Fight();f.attack_timer=99
        start={k:f.node_center(k) for k in f.nodes};body=f.body
        for _ in range(100):f.step(.02)
        self.assertNotEqual(body,f.body)
        for role in f.nodes:
            x,y=f.node_center(role)
            self.assertGreater(abs(x-start[role][0]),50)
            hp=f.nodes[role]
            self.assertTrue(f.hit_target(x,y,x+1,y,1));self.assertEqual(f.nodes[role],hp-1)

    def test_attackers_hold_position_during_warning_and_burst(self):
        f=Fight();f.move_enemies(2)
        for role,kind in (('eye','aimed'),('raven','raven')):
            f.warning=kind;before=f.node_center(role);f.move_enemies(.2)
            self.assertEqual(before,f.node_center(role))
            f.attack(kind);f.warning=None;f.move_enemies(.2)
            self.assertEqual(before,f.node_center(role))
            shots=[b for b in f.shots if b.kind==('raven' if role=='raven' else 'skull')]
            self.assertTrue(all((b.x,b.y)==before for b in shots))
            f.burst_queue=[];f.move_enemies(.2)
            self.assertNotEqual(before,f.node_center(role))

    def test_patrols_stay_in_upper_arena_and_death_freezes_boss(self):
        f=Fight()
        for n in range(400):
            f.move_enemies(.04)
            for role in f.nodes:
                x,y=f.node_center(role)
                self.assertTrue(50<x<1230);self.assertTrue(60<y<300)
        before=f.boss_offset;f.nodes={'eye':0,'raven':0}
        x,y=f.body;f.hit_target(x,y,x+1,y,999)
        self.assertEqual(f.boss_offset,before)
        f.step(.04);self.assertEqual(f.boss_offset,before)

    def test_telegraph_before_attack(self):
        f=Fight();f.attack_timer=.01;f.step(.02)
        self.assertEqual(f.warning,'aimed');self.assertFalse(f.shots)
        for _ in range(30):f.step(.04)
        self.assertTrue(any(b.enemy for b in f.shots))

    def test_invulnerability_and_death(self):
        f=Fight();f.hurt();self.assertEqual(f.hp,5)
        for _ in range(5):f.invuln=0;f.hurt()
        self.assertEqual(f.state,'dead');x=f.x;f.step(.04,move=1);self.assertEqual(f.x,x)

    def test_win_stops_attacks(self):
        f=Fight();f.nodes={'eye':0,'raven':0};f.exposed=11
        x,y=f.body;f.hit_target(x,y,x+1,y,200)
        self.assertEqual(f.state,'dying');f.step(.04,shoot=True);self.assertFalse(f.shots)
        for _ in range(110):f.step(.04,shoot=True)
        self.assertEqual(f.state,'won');self.assertFalse(f.shots)

    def test_boss_death_is_staged_and_cancels_attacks(self):
        f=Fight();f.nodes={'eye':0,'raven':0};f.exposed=11
        f.attack('aimed');f.wave_queue=[(1,'high')]
        x,y=f.body;f.hit_target(x,y,x+1,y,200)
        self.assertEqual(f.state,'dying');self.assertFalse(f.burst_queue)
        self.assertFalse(f.wave_queue);self.assertFalse(f.shots)
        for _ in range(25):f.step(.04)
        self.assertTrue(f.death_blasts);age=f.death_age
        self.assertFalse(f.hit_target(x,y,x+1,y,200));self.assertEqual(f.death_age,age)
        hp=f.hp;f.invuln=0;f.hurt();self.assertEqual(f.hp,hp)
        for _ in range(85):f.step(.04)
        self.assertEqual(f.state,'won');self.assertFalse(f.death_blasts)
        reset=Fight();self.assertEqual(reset.death_age,0);self.assertEqual(reset.state,'play')

    def test_swept_collision(self):
        self.assertTrue(segment_hit(0,0,100,0,50,1,2))
        self.assertFalse(segment_hit(0,0,100,0,50,10,2))

    def test_low_scythe_hits_legs_but_can_be_jumped(self):
        for jumping in (False,True):
            f=Fight();f.invuln=0
            if jumping:f.y-=90
            f.shots=[Bullet(f.x+5,f.floor-12,-100,0,True,5,kind='scythe')]
            f.step(.04)
            self.assertEqual(f.hp,5 if jumping else 4)

    def test_render_all_states(self):
        import cairo
        from omacontra.stages.reaper.battle_art import BattleRenderer
        renderer=BattleRenderer();f=Fight()
        for state in ('play','dead','dying','won'):
            f.state=state
            c=cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32,1100,700))
            renderer.background(c,f,'arena')
            for role in ('eye','raven'):renderer.weak_point(c,f,role)
            renderer.objects(c,f,(300,100));renderer.hud(c,f)

if __name__=='__main__':unittest.main()

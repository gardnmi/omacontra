import unittest
import math
from chase import Chase
from combat import Bullet

class ChaseTests(unittest.TestCase):
    def test_control_playthrough_completes_both_phases(self):
        from chase_playtest import run
        f,trace=run()
        self.assertEqual(f.state,'won');self.assertGreater(f.hp,0)
        self.assertTrue(any(row[1]=='transform' for row in trace))
        self.assertTrue(any(row[2]==2 and row[1]=='play' for row in trace))
        self.assertEqual(f.encounter_phase,2)

    def test_final_hit_starts_wreck_and_clears_firing(self):
        f=Chase();f.hp=1;f.invuln=0;f.muzzle=.1
        f.shots=[Bullet(300,400,500,0)];f.hurt()
        self.assertEqual(f.state,'dead');self.assertFalse(f.shots)
        self.assertEqual(f.muzzle,0)
        for _ in range(25):f.step(.04,shoot=True)
        self.assertGreater(f.wreck_age,.9);self.assertFalse(f.shots)

    def test_ramp_descent_and_landing_are_protected(self):
        f=Chase();f.encounter_phase=2;f.ramp_flight=True
        f.jump_height=220;f.vy=-400;f.invuln=0;f.next_ramp=999
        f.step(.02);f.hurt();self.assertEqual(f.hp,6)
        for _ in range(50):f.step(.02)
        self.assertFalse(f.ramp_flight)
        self.assertGreater(f.invuln,0)
        f.hurt();self.assertEqual(f.hp,6)
        for _ in range(25):f.step(.02)
        f.invuln=0;f.hurt();self.assertEqual(f.hp,5)

    def test_normal_jump_does_not_grant_descent_protection(self):
        f=Chase();f.jump_height=90;f.vy=-100;f.invuln=0
        f.step(.02);f.hurt();self.assertEqual(f.hp,5)

    def test_jump_lands_and_requires_release(self):
        f=Chase()
        for _ in range(90):f.step(.02,jump=True)
        self.assertEqual(f.jump_height,0)
        f.step(.02);f.step(.02,jump=True);self.assertGreater(f.jump_height,0)
    def test_boost_is_single_press_with_cooldown(self):
        f=Chase()
        for _ in range(180):f.step(.02,slide=True)
        self.assertEqual(f.boost,0)
        f.step(.02);f.step(.02,slide=True);self.assertGreater(f.boost,0)
    def test_boost_escapes_ram_that_hits_idle_car(self):
        for boost in (False,True):
            f=Chase();f.clock=30;f.boss_x=850;f.invuln=0;f.attack_timer=99;f.attack('ram')
            for i in range(110):f.step(.02,slide_pressed=boost and i==12)
            self.assertEqual(f.hp,6 if boost else 5)
    def test_jump_clears_tire_roller(self):
        for jump in (False,True):
            f=Chase();f.invuln=0;f.next_drone=99;f.next_barrier=99
            f.shots=[Bullet(700,562,-430,0,True,4,kind='tire_roller')]
            for i in range(65):f.step(.02,jump=jump and i==17)
            self.assertEqual(f.hp,6 if jump else 5)
    def test_bullet_axis_and_origin_follow_airborne_boost(self):
        f=Chase();f.step(.02,jump=True,slide_pressed=True,shoot=True,aim=(900,300))
        b=f.shots[0];x,y=f.muzzle_position
        self.assertAlmostEqual(b.x-b.vx*.02,x);self.assertAlmostEqual(b.y-b.vy*.02,y)
        self.assertAlmostEqual(b.vx,math.cos(f.gun_angle)*920)
    def test_truck_opens_with_telegraphed_attack(self):
        f=Chase()
        self.assertTrue(f.boss_active);self.assertLess(f.boss_x,1000)
        for _ in range(35):f.step(.02)
        self.assertEqual(f.warning,'ram');self.assertEqual(f.ram_time,0)
        self.assertEqual(f.hp,6)
        for _ in range(80):f.step(.02)
        self.assertGreater(f.ram_time,0)
    def test_weapons_can_break_out_of_order_and_disable_their_attacks(self):
        f=Chase();f.attack_timer=99;f.invuln=99
        for index,health in ((1,80),(0,60)):
            for _ in range(health):
                x,y=f.component_target(index);f.shots=[Bullet(x,y,1,0)];f.step(.001)
            self.assertEqual(f.parts[index],0)
        f.shots=[]
        for kind in ('roller','spread','mortar'):f.attack(kind)
        self.assertFalse(f.shots);self.assertFalse(f.rocket_queue)

    def test_core_needs_ramp_and_trailer_precedes_finisher(self):
        f=Chase();f.attack_timer=99;f.invuln=99
        x,y=f.component_target(2);f.shots=[Bullet(x,y,1,0)];f.step(.001)
        self.assertEqual(f.parts[2],160)
        f.core_open=4
        for _ in range(33):
            x,y=f.component_target(2);f.shots=[Bullet(x,y,1,0)];f.step(.001)
        self.assertEqual(f.parts[2],28);self.assertTrue(f.trailer_done)
        self.assertEqual(f.state,'transform')
        for _ in range(175):f.step(.02)
        self.assertEqual(f.encounter_phase,2);self.assertEqual(f.state,'play')
        self.assertEqual(f.boss_hp,120)
        for _ in range(54):
            f.robot_age=4.4;f.jump_height=500;f.y=90;f.core_open=3;x,y=f.target
            f.shots=[Bullet(x,y,1,0)];f.step(.001)
        f.step(.02)
        self.assertEqual(f.state,'finisher')
        for _ in range(46):f.step(.02)
        f.step(.02,jump=True)
        for _ in range(35):f.step(.02)
        f.step(.02,shoot=True,aim=f.target)
        for _ in range(200):f.step(.02)
        self.assertEqual(f.state,'won')

    def test_ramp_launch_opens_core_and_armor_closes_again(self):
        f=Chase();f.attack_timer=99;f.ramp_x=f.x-2
        f.step(.02)
        self.assertGreater(f.vy,600);self.assertTrue(f.core_vulnerable)
        for _ in range(210):f.step(.02)
        self.assertFalse(f.core_vulnerable)

    def test_robot_ramp_reveals_heart_and_camera_tracks_car(self):
        f=Chase();f.detach_trailer()
        for _ in range(86):f.step(.04)
        f.ramp_x=f.x-1;f.step(.02)
        self.assertGreater(f.vy,1200)
        peak=0
        for _ in range(100):
            f.step(.02);peak=max(peak,f.jump_height)
            if f.jump_height>500:
                self.assertTrue(f.core_vulnerable)
                self.assertTrue(70<f.target[1]+f.camera_y<500)
                self.assertTrue(200<f.y+f.camera_y<550)
                screen=(900,f.target[1]+f.camera_y)
                self.assertAlmostEqual(f.screen_to_world(screen)[1],f.target[1])
        self.assertGreater(peak,600)

    def test_robot_shredder_has_a_normal_jump_escape(self):
        from chase_robot import robot_step
        for jump in (False,True):
            f=Chase();f.encounter_phase=2;f.robot_age=5.49;f.next_ramp=999;f.invuln=0
            robot_step(f,.02)
            self.assertEqual(len(f.shots),1)
            for i in range(90):f.step(.02,jump=jump and i==20)
            self.assertEqual(f.hp,6 if jump else 5)

    def test_ramp_catches_wheels_during_steering_boost_and_small_hops(self):
        for dt in (.016,.04):
            for move in (-1,0,1):
                for boost in (False,True):
                    f=Chase();f.encounter_phase=2;f.next_ramp=999
                    f.ramp_x=f.x-100;f.jump_height=65;f.vy=50
                    for _ in range(12):
                        f.step(dt,move=move,slide=boost)
                        if f.ramp_launched:break
                    self.assertTrue(f.ramp_launched,(dt,move,boost))
                    self.assertGreater(f.vy,1200)
                    f.step(dt,move=move)
                    self.assertLess(f.vy,1250)  # Contact cannot relaunch every frame.

    def test_ramp_does_not_snap_a_high_airborne_car(self):
        f=Chase();f.encounter_phase=2;f.next_ramp=999
        f.ramp_x=f.x-20;f.jump_height=300;f.vy=100
        f.step(.04)
        self.assertFalse(f.ramp_launched);self.assertLess(f.vy,100)

    def test_downward_fans_have_alternating_car_width_gaps(self):
        from chase_robot import robot_step
        for beat,safe_x,blocked_x in ((1.,570,340),(3.3,350,570)):
            for x,expected_hp in ((safe_x,6),(blocked_x,5)):
                f=Chase();f.boss_x=850;f.encounter_phase=2
                f.robot_age=beat-.01;f.next_ramp=999;f.invuln=0;f.x=x
                robot_step(f,.02)
                self.assertEqual(len(f.shots),3)
                self.assertTrue(all(b.vy>0 for b in f.shots))
                self.assertEqual(len({b.vx for b in f.shots}),3)
                for _ in range(50):f.step(.04)
                self.assertEqual(f.hp,expected_hp,(beat,x))

    def test_driver_can_weave_between_successive_fans(self):
        f=Chase();f.boss_x=850;f.encounter_phase=2;f.next_ramp=999
        f.invuln=0;f.x=570
        for _ in range(130):
            move=-1 if f.robot_age>3 and f.x>350 else 0
            f.step(.04,move=move)
        self.assertEqual(f.hp,6)

    def test_trailer_falls_back_away_from_player(self):
        f=Chase();f.invuln=0;f.detach_trailer();previous=f.trailer_x
        for _ in range(40):
            f.step(.02)
            self.assertGreaterEqual(f.trailer_x,previous);previous=f.trailer_x
        self.assertEqual(f.hp,6)
        self.assertGreater(f.trailer_x,f.trailer_origin)

    def test_robot_heart_shutters_control_damage(self):
        f=Chase();f.detach_trailer()
        for _ in range(90):f.step(.04)
        for height,window,damage in ((0,3,0),(500,3,2),(500,0,0)):
            f.jump_height=height;f.y=590-height;f.core_open=window;before=f.boss_hp;x,y=f.target
            f.shots=[Bullet(x,y,1,0)];f.step(.001)
            self.assertEqual(f.boss_hp,before-damage)
        self.assertEqual(f.encounter_phase,2)

    def test_robot_attacks_and_heart_repeat(self):
        from chase_robot import heart_open
        f=Chase();f.detach_trailer()
        for _ in range(86):f.step(.04)
        f.invuln=99;kinds=set();open_cycles=0;was_open=False
        for _ in range(500):
            f.step(.04)
            kinds.update(b.kind for b in f.shots if b.enemy)
            opened=heart_open(f)>.8
            if opened and not was_open:open_cycles+=1
            was_open=opened
        self.assertEqual(kinds,{'tire_roller','robot_shell','drone_laser'})
        self.assertGreaterEqual(open_cycles,3)

    def test_robot_drone_reinforcements_continue_and_stay_capped(self):
        f=Chase();f.detach_trailer()
        for _ in range(86):f.step(.04)
        f.invuln=999;seen=set()
        for _ in range(500):
            f.step(.04)
            seen.update(id(d) for d in f.drones)
            self.assertLessEqual(len(f.drones),2)
        self.assertGreaterEqual(len(seen),2)
        f.drones.clear();f.reinforce_at=f.clock
        f.step(.04);self.assertEqual(len(f.drones),1)

    def test_offscreen_robot_drone_waits_for_visible_charge(self):
        f=Chase();f.encounter_phase=2;f.reinforce_at=999
        f.spawn_drone();d=f.drones[0];d['x']=900;d['y']=250;d['fire']=.01
        f.jump_height=680;f.y=-90
        f.step(.02)
        self.assertGreaterEqual(d['fire'],.8)
        self.assertIsNone(d['lock'])
        self.assertFalse(any(b.kind=='drone_laser' for b in f.shots))

    def test_finisher_timeout_and_missed_shot_recover(self):
        for miss in (False,True):
            f=Chase();f.parts=[0,0,20];f.boss_hp=20;f.begin_finisher()
            for _ in range(46):f.step(.02)
            if miss:
                f.step(.02,jump=True)
                for _ in range(35):f.step(.02)
                f.step(.02,shoot=True,aim=(0,0))
            for _ in range(150):f.step(.02)
            self.assertEqual(f.state,'play');self.assertEqual(f.boss_hp,20)
            self.assertGreater(f.finisher_cooldown,0)

    def test_finisher_requires_fresh_trigger(self):
        f=Chase();f.begin_finisher()
        for _ in range(46):f.step(.02,shoot=True)
        f.was_shoot=True
        f.step(.02,jump=True,shoot=True)
        for _ in range(40):f.step(.02,shoot=True)
        self.assertEqual(f.finisher_phase,'aim');self.assertFalse(f.shots)
        f.step(.02);f.step(.02,shoot=True,aim=f.target)
        self.assertEqual(f.finisher_phase,'flight')

    def test_mortar_has_time_to_drive_out(self):
        for move in (0,-1):
            f=Chase();f.x=420;f.attack_timer=99;f.invuln=0
            f.mortar_targets=[420];f.attack('mortar')
            for _ in range(90):f.step(.02,move=move)
            self.assertEqual(f.hp,5 if move==0 else 6)

    def test_truck_and_drone_have_distinct_ordnance(self):
        f=Chase();f.attack_timer=99
        f.attack('roller');self.assertEqual(f.shots[-1].kind,'tire_roller')
        f.attack('spread');self.assertEqual({b.kind for b in f.shots},{'tire_roller','truck_rocket'})
        f.shots=[];f.spawn_drone();d=f.drones[0];d['fire']=.65
        f.step(.02);self.assertIsNotNone(d['lock']);locked=d['lock']
        f.x-=50;d['fire']=.01;f.step(.02)
        laser=next(b for b in f.shots if b.kind=='drone_laser')
        origin=(laser.x-laser.vx*.02,laser.y-laser.vy*.02)
        self.assertAlmostEqual(math.atan2(laser.vy,laser.vx),math.atan2(locked[1]-origin[1],locked[0]-origin[0]))
        self.assertIsNone(d['lock'])

    def test_horizontal_control_holds_position_and_stays_on_screen(self):
        f=Chase();f.attack_timer=99
        start=f.x
        for _ in range(20):f.step(.02,move=1)
        self.assertGreater(f.x,start)
        parked=f.x
        for _ in range(10):f.step(.02)
        self.assertEqual(f.x,parked)
        for _ in range(150):f.step(.02,move=-1)
        self.assertEqual(f.x,160)
        for _ in range(150):f.step(.02,move=1)
        self.assertEqual(f.x,660)

    def test_steering_avoids_laser_that_hits_parked_car(self):
        for move in (0,-1,1):
            f=Chase();f.invuln=0;f.attack_timer=99
            f.shots=[Bullet(f.player_center[0],300,0,400,True,4,kind='drone_laser')]
            for _ in range(50):f.step(.02,move=move)
            self.assertEqual(f.hp,5 if move==0 else 6)

    def test_airborne_steering_and_boost_follow_selected_direction(self):
        for direction in (-1,1):
            f=Chase();f.attack_timer=99;start=f.x
            f.step(.02,jump=True,move=direction,slide_pressed=True,shoot=True,aim=(1100,400))
            self.assertGreater(f.jump_height,0)
            self.assertGreater((f.x-start)*direction,0)
            b=f.shots[0];x,y=f.muzzle_position
            self.assertAlmostEqual(b.x-b.vx*.02,x);self.assertAlmostEqual(b.y-b.vy*.02,y)

    def test_scrolling_rail_does_not_move_rectangles_of_scenery(self):
        import cairo
        from chase_art import ChaseRenderer
        r=ChaseRenderer();f=Chase();f.state='won';f.invuln=0;f.notice_time=0;f.clock=8
        frames=[]
        for distance in (0,93):
            f.distance=distance;s=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720)
            r.draw(cairo.Context(s),f,hud=False);s.flush();frames.append(bytes(s.get_data()))
        stride=1280*4
        self.assertEqual(frames[0][80*stride:400*stride],frames[1][80*stride:400*stride])
        self.assertNotEqual(frames[0][420*stride:480*stride],frames[1][420*stride:480*stride])

    def test_foreground_scrolls_as_rigid_layer_and_distant_coast_stays_fixed(self):
        import cairo
        from chase_art import ChaseRenderer
        renderer=ChaseRenderer();frames=[]
        for distance in (0,80):
            surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720)
            renderer.scenery(cairo.Context(surface),distance)
            surface.flush();frames.append(bytes(surface.get_data()))
        stride=1280*4
        self.assertEqual(frames[0][:490*stride],frames[1][:490*stride])
        self.assertNotEqual(frames[0][510*stride:580*stride],frames[1][510*stride:580*stride])
        # 80 world pixels become 132 foreground pixels, including foliage tips.
        for y in (610,630,660,690,710):
            start=y*stride
            self.assertEqual(frames[0][start:start+1000*4],
                             frames[1][start+132*4:start+1132*4])

    def test_foreground_buffer_is_reused_and_scroll_coordinates_are_bounded(self):
        import cairo
        from chase_art import ChaseRenderer
        r=ChaseRenderer();buffer=r.foreground
        # A recording target exercises the deferred path used by GTK.
        for distance in (0,1_000_000,1_000_000_000):
            target=cairo.RecordingSurface(cairo.CONTENT_COLOR_ALPHA,(0,0,1280,720))
            r.scenery(cairo.Context(target),distance)
            replay=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720)
            c=cairo.Context(replay);c.set_source_surface(target);c.paint()
            self.assertIs(r.foreground,buffer)
            self.assertEqual((buffer.get_width(),buffer.get_height()),(1280,230))
            self.assertLess(abs(r.foreground_pattern.get_matrix().x0),2*r.road.get_width())

    def test_destroyed_cab_does_not_draw_detached_trailer_again(self):
        import cairo,sprites
        from unittest.mock import patch
        from chase_art import ChaseRenderer
        f=Chase();f.trailer_done=True;f.begin_destruction();f.death_age=.3
        r=ChaseRenderer();surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720)
        with patch('chase_art.sprites.draw',wraps=sprites.draw) as draw:
            r.truck_death(cairo.Context(surface),f)
        for call in draw.call_args_list:
            if call.args[1]=='quattro-enemies.png':
                sx,sy,sw,sh=call.args[2]
                self.assertLessEqual(sx+sw,810)

    def test_destruction_renders_every_frame_including_new_zero_age_blasts(self):
        import cairo
        from chase_art import ChaseRenderer
        f=Chase();f.begin_destruction();r=ChaseRenderer()
        s=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720)
        zero_age_seen=False
        for _ in range(270):
            f.step(.02)
            zero_age_seen|=any(age==0 for _,_,age,_ in f.death_blasts)
            r.draw(cairo.Context(s),f)
            self.assertEqual(f.jump_height,0)
        self.assertTrue(zero_age_seen);self.assertEqual(f.state,'won')

    def test_empty_sprite_does_not_poison_context(self):
        import cairo,sprites
        s=cairo.ImageSurface(cairo.FORMAT_ARGB32,10,10);c=cairo.Context(s)
        for width,height in ((0,10),(10,0),(-1,5),(float('nan'),5)):
            sprites.draw(c,'unused.png',(0,0,10,10),0,0,width,height)
        c.set_source_rgb(1,1,1);c.paint()
        self.assertEqual(bytes(s.get_data())[:4],b'\xff'*4)

    def test_renderer_handles_all_encounter_states(self):
        import cairo
        from chase_art import ChaseRenderer
        r=ChaseRenderer();f=Chase();f.clock=30;f.boss_x=850;f.spawn_drone()
        s=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720)
        for state in ('play','finisher','dying','dead','won'):
            f.state=state;f.death_age=1;r.draw(cairo.Context(s),f)

if __name__=='__main__':unittest.main()

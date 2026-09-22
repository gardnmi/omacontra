import math
import unittest
import cairo
from foundry import Foundry,Hazard,rescue_beat,rescue_car,rescue_tobi,CAR_ENTRY,IMPACT,EJECTION,EXPLOSION,RESCUE_END
from foundry_art import FoundryRenderer,FoundryIntro


class FoundryTests(unittest.TestCase):
    def test_shots_from_under_legs_reach_mouth(self):
        for offset in (-100,0,100):
            f=Foundry();f.shoulder_heat=1
            tx,ty=f.mount_target;sx,sy=f.boss_x+offset,615
            for i in range(60):
                a=i/60;b=(i+1)/60
                if f.hit_target(sx+(tx-sx)*a,sy+(ty-sy)*a,
                                sx+(tx-sx)*b,sy+(ty-sy)*b,1):break
            self.assertEqual(f.mount_hp,f.mount_max-1)
            self.assertEqual(f.armor_flash,0)

    def test_top_platform_double_jump_has_no_invisible_ceiling(self):
        f=Foundry();f.mount_hp=0;f.forge_timer=999
        f.support=f.platforms[3];f.x=530;f.y=f.floor
        highest=f.y
        for i in range(70):
            f.step(.02,jump=i in (0,18))
            highest=min(highest,f.y)
            sx,sy=700,300+f.camera_y
            self.assertEqual(f.screen_to_world((sx,sy)),(700,300))
            self.assertGreaterEqual(f.y+f.camera_y,190)
        self.assertLess(highest,50)
        self.assertEqual(f.y,f.floor)

    def test_rotating_beam_stays_rooted_in_the_mouth(self):
        f=Foundry()
        for angle in (0,math.pi/2,math.pi,math.tau):
            f.shoulder_aim=angle
            self.assertEqual(f.shoulder_muzzle,f.shoulder_mount)
            self.assertEqual(f.mount_target,f.shoulder_mount)
            self.assertEqual(f.shoulder_path()[0],f.shoulder_mount)
        f.begin_disarm()
        self.assertEqual(f.drop_origin,f.shoulder_mount)

    def test_center_arena_rescue_keeps_boss_centered_and_landings_safe(self):
        f=Foundry();f.lava_age=7;f.begin_rescue()
        self.assertEqual(f.rescue_start_boss_x,640)
        for _ in range(135):f.step(.04)
        self.assertAlmostEqual(f.boss_x,640)
        self.assertEqual(f.camera_y,0)
        # Car nose reaches the stationary Warden; both survivors end on the
        # retained lower-left platform, above permanent lava.
        x,_,_=rescue_car(IMPACT)
        from foundry import RESCUE_CAR_SCALE
        self.assertAlmostEqual(x+200*RESCUE_CAR_SCALE,624)
        self.assertGreater(x+200*RESCUE_CAR_SCALE,f.boss_x-160)
        left,right,top=f.platforms[0]
        for landing_x in (390,rescue_tobi(RESCUE_END)[0]):
            self.assertLess(left,landing_x);self.assertLess(landing_x,right)
        self.assertLess(top,f.lava_surface)

    def test_harbor_story_targets_the_space_server(self):
        from journey_cinema import HARBOR_LINES
        text=' '.join(line for line,_ in HARBOR_LINES)
        self.assertIn('SPACE SERVER',text);self.assertIn('SPACESHIP',text)
        self.assertIn('LAUNCH SITE',text);self.assertNotIn('EXIT SIGNAL',text)

    def test_mount_armor_disarm_and_physical_pickup(self):
        f=Foundry();x,y=f.mount_target
        f.hit_target(x-2,y,x+2,y,999)
        self.assertEqual(f.mount_hp,f.mount_max)
        f.shoulder_heat=1;f.hit_target(x-2,y,x+2,y,999)
        self.assertEqual(f.state,'disarm');self.assertEqual(f.mount_hp,0)
        for _ in range(35):f.step(.04)
        self.assertEqual(f.state,'play');self.assertFalse(f.laser)
        self.assertEqual(len(f.pickups),1)
        f.x=f.pickup_spot[0];f.support=f.platforms[0];f.y=f.floor;f.update_pickup()
        self.assertTrue(f.laser);self.assertFalse(f.pickups)

    def test_no_timed_weapon_gift(self):
        f=Foundry();f.combat_age=100;f.forge_timer=0
        f.step(.02)
        self.assertFalse(f.laser);self.assertFalse(f.pickups)
        self.assertEqual(f.state,'play')

    def test_next_charge_does_not_wait_for_bullets(self):
        f=Foundry();f.forge_timer=0;f.emit('fan',0);f.step(.02)
        self.assertEqual(f.forge_warning,'wisps');self.assertTrue(f.bolts)

    def test_fire_and_fan_start_at_live_muzzle(self):
        f=Foundry();f.clock=2;f.boss_x=945
        for kind in ('fire','flood'):
            self.assertEqual(f.fire_path(Hazard(kind,300))[0],f.cannon)
        f.emit('fan',1)
        self.assertTrue(all((b.x,b.y)==f.dragon_point(*__import__('wyrm_scene').EYES[(f.forge_round-1)%2]) for b in f.bolts))
        self.assertEqual(len({round(b.vy) for b in f.bolts}),5)

    def test_shoulder_dash_uses_actual_beam_collision(self):
        for dash in (False,True):
            f=Foundry();f.invuln=0;f.sweep_age=5.;f.shoulder_aim=math.pi
            px,py=f.shoulder_path()[20];f.x=px;f.y=py+35
            f.step(.01,slide_pressed=dash,move=1)
            self.assertEqual(f.hp,6 if dash else 5)
            self.assertEqual(f.enemy_beam[0],f.shoulder_muzzle)

    def test_dash_crosses_cannon_flame_but_flame_still_hurts(self):
        for dash in (False,True):
            f=Foundry();f.mount_hp=0;f.forge_timer=999;f.invuln=0
            f.x=450;f.y=480
            f.hazards=[Hazard('fire',f.x,age=.3,y=f.y-35)]
            f.step(.01,slide_pressed=dash,move=1)
            self.assertEqual(f.hp,6 if dash else 5)

    def test_fan_has_passable_gaps_and_no_overtaking_pulse(self):
        f=Foundry();f.locked_target=(400,500)
        f.emit('fan',0);first=f.bolts[:];f.emit('fan',1)
        self.assertEqual(len(first),5)
        self.assertEqual(len(f.bolts),10)
        for a,b in zip(first,f.bolts[5:]):
            self.assertEqual((a.vx,a.vy),(b.vx,b.vy))
        # At 300px from the cannon each lane leaves room for the 28px
        # player hitbox, both projectile radii, and a steering margin.
        for a,b in zip(first,first[1:]):
            gap=math.hypot(a.vx-b.vx,a.vy-b.vy)*300/245
            self.assertGreater(gap,28+a.radius+b.radius+35)

    def test_wisps_use_one_slow_volley_and_a_recovery_gap(self):
        f=Foundry();f.forge_warning='wisps';f.forge_timer=0
        f.step(.02)
        self.assertEqual(len(f.emit_queue),1)
        self.assertGreaterEqual(f.forge_timer,.65)
        f.step(.02)
        self.assertEqual(len(f.bolts),5)
        self.assertTrue(all(math.hypot(b.vx,b.vy)<=245.01 for b in f.bolts))

    def test_cannon_charge_gives_reaction_time_without_tracking(self):
        from foundry import FORGE_WINDUP
        f=Foundry();f.forge_timer=0;f.step(.01)
        target=f.locked_target
        self.assertEqual(f.forge_warning,'wisps')
        self.assertGreaterEqual(f.forge_timer,.75)
        for _ in range(15):f.step(.04,move=1)
        self.assertEqual(f.locked_target,target)
        self.assertEqual(f.forge_warning,'wisps');self.assertFalse(f.hazards)

    def test_full_rotation_accelerates_smoothly_with_damage(self):
        from foundry import SHOULDER_CHARGE,SHOULDER_PERIOD
        f=Foundry();f.invuln=999;f.forge_timer=999
        f.sweep_age=SHOULDER_CHARGE;initial=f.shoulder_aim
        for _ in range(1000):f.update_shoulder(SHOULDER_PERIOD/1000)
        self.assertAlmostEqual(f.shoulder_aim-initial,math.tau)
        angle=f.shoulder_aim;slow=f.shoulder_speed
        f.mount_hp=f.mount_max*.1
        self.assertEqual(f.shoulder_aim,angle)
        self.assertGreater(f.shoulder_speed,slow)
        f.update_shoulder(.02)
        self.assertAlmostEqual(f.shoulder_aim-angle,f.shoulder_speed*.02)
        points=f.shoulder_path();f.x=1200;f.y=235
        self.assertEqual(points,f.shoulder_path())

    def test_each_completed_rotation_speeds_up_even_without_damage(self):
        from foundry import SHOULDER_CHARGE
        f=Foundry();f.invuln=999;f.sweep_age=SHOULDER_CHARGE
        completions=[]
        for i in range(1700):
            previous=f.shoulder_aim
            f.update_shoulder(.04)
            self.assertGreater(f.shoulder_aim,previous)
            self.assertLessEqual(f.shoulder_aim-previous,math.tau/13*.04+1e-9)
            turns=int((f.shoulder_aim-math.pi/2+1e-9)/math.tau)
            if turns>len(completions):completions.append((i+1)*.04)
            if len(completions)==4:break
        durations=[end-start for start,end in zip([0]+completions,completions)]
        for actual,expected in zip(durations,(18,16,14,13)):
            self.assertAlmostEqual(actual,expected,delta=.05)
        self.assertEqual(len(completions),4)

    def test_phase_attack_sets_and_center_position(self):
        for laser,expected in ((False,{'wisps'}),(True,{'wisps','breath','updraft'})):
            f=Foundry();f.invuln=999;f.laser=laser
            if laser:f.mount_hp=0;f.lava_age=0
            seen=set()
            for _ in range(1500):
                f.step(.02)
                if f.forge_warning:seen.add(f.forge_warning)
                self.assertEqual(f.boss_x,640)
            self.assertEqual(seen,expected)

    def test_mount_can_be_shot_from_both_sides(self):
        for direction in (-1,1):
            f=Foundry();f.shoulder_heat=1
            x,y=f.mount_target
            # Walk a bullet across the body toward the rotor.
            for i in range(30):
                ax=x+direction*(180-i*8)
                if f.hit_target(ax,y,ax-direction*8,y,1):break
            self.assertLess(f.mount_hp,f.mount_max)

    def test_platform_circuit_can_outpace_fastest_rotor(self):
        from foundry import SHOULDER_FAST_PERIOD
        f=Foundry();f.mount_hp=0;f.forge_timer=999
        # Isolate traversal geometry; no teleports, boosted speed, or jumps
        # beyond the player's normal double jump. Include every landing.
        route=[(347,535),(230,435),(315,335),(530,170),(747,170),
               (965,335),(1110,435),(900,535),(1100,630),(750,630),
               (450,630),(210,630)]
        index=0
        for tick in range(int(SHOULDER_FAST_PERIOD/.02)):
            x,y=route[index]
            move=1 if f.x<x-6 else -1 if f.x>x+6 else 0
            jump=y<f.y-10 and (f.y>=f.floor-.1 or f.jumps_used==1 and f.vy>-80)
            f.step(.02,move=move,jump=jump and not f.was_jump)
            if abs(f.x-x)<10 and abs(f.y-y)<.1 and f.vy==0:
                index+=1
                if index==len(route):break
        self.assertEqual(index,len(route))

    def test_beam_stays_on_through_other_attacks(self):
        from foundry import SHOULDER_CHARGE
        f=Foundry();f.invuln=999
        for _ in range(600):
            f.step(.02)
            if f.sweep_age>=SHOULDER_CHARGE:
                self.assertEqual(len(f.enemy_beam),81)
        f.begin_disarm();f.step(.02)
        self.assertFalse(f.enemy_beam)

    def test_lava_starts_at_collection_and_never_recedes(self):
        from foundry import Pickup,LAVA_TOP
        f=Foundry();f.mount_hp=0;f.forge_timer=999
        f.pickups=[Pickup(*f.pickup_spot,'laser')]
        f.step(.04);self.assertIsNone(f.lava_surface)
        f.x=f.pickup_spot[0];f.support=f.platforms[0];f.y=f.floor;f.update_pickup()
        self.assertEqual(f.lava_surface,780)
        previous=f.lava_surface
        for _ in range(400):
            f.step(.04)
            self.assertLessEqual(f.lava_surface,previous);previous=f.lava_surface
        self.assertEqual(f.lava_surface,LAVA_TOP)
        f.begin_rescue();f.step(.04)
        self.assertEqual(f.lava_surface,LAVA_TOP)
        self.assertIsNone(Foundry().lava_surface)

    def test_lava_hurts_ground_but_leaves_all_platforms_safe(self):
        for platform in (None,0,1,2):
            f=Foundry();f.mount_hp=0;f.forge_timer=999;f.lava_age=7;f.invuln=0
            if platform is not None:
                f.support=f.platforms[platform];f.x=(f.support[0]+f.support[1])/2;f.y=f.floor
            f.step(.02)
            self.assertEqual(f.hp,5 if platform is None else 6)

    def test_full_encounter_through_normal_controls(self):
        from foundry_playtest import choose
        f=Foundry(7);moves=set();seen=set()
        for i in range(4000):
            if i%3==0 or f.state!='play':controls=choose(f) if f.state=='play' else {}
            f.step(.04,**dict(controls,slide_pressed=controls.get('slide_pressed',False) and i%3==0))
            if f.dash_time>0:moves.add('dash')
            if f.jumps_used==2:moves.add('double')
            if f.sliding:moves.add('slide')
            if f.forge_warning:seen.add(f.forge_warning)
            if f.enemy_beam:seen.add('shoulder')
            if f.state in ('won','dead'):break
        self.assertEqual(f.state,'won');self.assertGreater(f.hp,0)
        self.assertEqual(f.collected,1)
        self.assertTrue({'shoulder','breath','wisps','updraft'}<=seen)
        self.assertTrue({'dash','double'}<=moves)

    def test_armor_then_continuous_laser_and_rescue(self):
        f=Foundry(1);x,y=f.boss_x,510
        self.assertFalse(f.hit_target(x-5,y,x+5,y,999))
        self.assertEqual(f.boss_hp,f.boss_max)
        self.assertEqual(f.armor_flash,0)
        f.laser=True;f.step(.02,shoot=True,aim=f.core)
        self.assertTrue(f.beam_hit);self.assertLess(f.boss_hp,f.boss_max)
        f.boss_hp=.01;f.step(.02,shoot=True,aim=f.core)
        self.assertEqual(f.state,'rescue');self.assertFalse(f.beam)
        hp=f.hp;f.hurt();self.assertEqual(f.hp,hp)

    def test_stationary_player_cannot_wait_out_opening(self):
        f=Foundry()
        for _ in range(2000):
            f.step(.02,shoot=True,aim=f.core)
            if f.state=='dead':break
        self.assertEqual(f.state,'dead');self.assertFalse(f.laser)

    def test_rescue_order(self):
        self.assertEqual(rescue_beat(IMPACT-.001),'flight')
        self.assertEqual(rescue_beat(IMPACT),'impact')
        self.assertEqual(rescue_beat(EJECTION),'eject')
        self.assertEqual(rescue_beat(EXPLOSION),'explode')
        self.assertLess(IMPACT,EJECTION);self.assertLess(EJECTION,EXPLOSION)

    def test_car_flight_and_tobi_landing_are_continuous(self):
        previous=rescue_car(CAR_ENTRY)
        for i in range(1,111):
            p=rescue_car(CAR_ENTRY+i*.01)
            self.assertGreaterEqual(p[0],previous[0]);self.assertLess(math.dist(p[:2],previous[:2]),15)
            previous=p
        a=rescue_tobi(EJECTION+1.55-.00001);b=rescue_tobi(EJECTION+1.55)
        self.assertLess(math.dist(a[:2],b[:2]),.02)
        self.assertEqual(b[3],'land')
        self.assertLess(rescue_tobi(EXPLOSION)[0],800)

    def test_air_dash_passes_through_bolts(self):
        from foundry import Bolt
        f=Foundry();f.invuln=0;f.y=f.floor-90
        f.bolts=[Bolt(f.x+10,f.y-35,0,0)]
        f.step(.01,slide_pressed=True,move=1)
        self.assertGreater(f.dash_time,0);self.assertEqual(f.hp,6);self.assertFalse(f.bolts)

    def test_no_tutorial_overlays(self):
        from unittest.mock import patch
        f=Foundry();r=FoundryRenderer();surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720)
        with patch('foundry_art.label') as label:
            for kind in ('curtain','beam','embers','rush'):
                f.forge_warning=kind;r.draw(cairo.Context(surface),f)
        texts=' '.join(str(call.args[3]) for call in label.call_args_list)
        for forbidden in ('JUMP','GET LOW','MOVE','SLIDE','CORE OPEN','SHOOT'):
            self.assertNotIn(forbidden,texts)

    def test_platform_landing_walking_off_and_jump_through(self):
        f=Foundry();f.x=350;f.y=510;f.vy=200
        for _ in range(10):f.step(.02)
        self.assertEqual(f.y,535);self.assertEqual(f.floor,535)
        self.assertEqual(f.jumps_used,0)
        f.step(.02,jump=True);self.assertLess(f.y,535)
        f.x=470;f.step(.02);self.assertEqual(f.floor,630)
        f=Foundry();f.x=350
        for i in range(65):f.step(.02,jump=i in (0,15))
        self.assertEqual(f.y,535)

    def test_beam_miss_does_not_damage(self):
        f=Foundry();f.laser=True
        f.step(.02,shoot=True,aim=(100,100))
        self.assertFalse(f.beam_hit);self.assertEqual(f.boss_hp,f.boss_max)

    def test_render_rescue_boundaries_and_intro(self):
        f=Foundry(1);r=FoundryRenderer();surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720)
        for kind in ('fire','flood','shoulder'):
            f.forge_warning=kind;r.draw(cairo.Context(surface),f)
            f.hazards=[Hazard(kind,420,.3)];r.draw(cairo.Context(surface),f)
        f.begin_disarm()
        for t in (0,.5,2.8,4,6.5):
            f.disarm_age=min(1.35,t);r.draw(cairo.Context(surface),f)
        f.state='play';f.begin_rescue()
        for t in (0,.01,1.25,3.2,CAR_ENTRY,IMPACT-.01,IMPACT,EJECTION,EXPLOSION,7.5,9.1,RESCUE_END):
            f.rescue_age=t;r.draw(cairo.Context(surface),f)
        cinema=FoundryIntro();f=Foundry()
        for t in (0,2.6,3.2,4.5,4.9,5.1,7.8,cinema.DURATION):cinema.age=t;cinema.draw(cairo.Context(surface),r,f)
        self.assertEqual(f.x,210)
        self.assertEqual(f.clock,0)
        self.assertTrue(cinema.finished)

    def test_transition_from_tide_and_reset(self):
        from types import SimpleNamespace
        from boss_app import BossApp
        from input_state import KeyboardState
        app=BossApp.__new__(BossApp);app.keyboard=KeyboardState();app.keys=app.keyboard.keys
        app.level=3;app.f=SimpleNamespace(state='won',hp=2);app.journey_cinema=SimpleNamespace(kind='outro',age=6)
        app.intro=None;app.chase_cinema=None;app.paused=False;app.shooting=True;app.slide_requested=False
        app.key(None,SimpleNamespace(hardware_keycode=36,keyval=65293))
        self.assertEqual(app.level,4);self.assertIsInstance(app.f,Foundry);self.assertEqual(app.f.hp,3)
        self.assertFalse(app.shooting);self.assertIsNone(app.journey_cinema)
        app.f.begin_rescue();app.reset_encounter()
        self.assertEqual(app.f.state,'play');self.assertEqual(app.f.rescue_age,0)
        self.assertEqual(app.foundry_intro.age,0)


if __name__=='__main__':unittest.main()

import unittest
from unittest.mock import Mock
import cairo
from omacontra.stages.harbor.tidebreaker import Tidebreaker, TideHazard
from omacontra.stages.harbor.tide_art import TideRenderer
from omacontra.stages.harbor.journey_cinema import JourneyCinema, INTRO_DURATION


def pilot(f):
 move=0;duck=False;jump=False;slide=False;aim=f.core;shoot=f.vulnerable;interact=False
 if not f.stage:
  # Favor the left third to leave room to see and clear incoming wave/cart pairs.
  move=1 if f.x<375 else -1 if f.x>425 else 0
  if f.tide_warning=='claw' or any(h.kind=='claw' for h in f.hazards):
   dest=f.target_x+155 if f.target_x<480 else f.target_x-155
   move=1 if f.x<dest-10 else -1 if f.x>dest+10 else 0
  for h in f.hazards:
   d=(h.x-f.x)*-h.direction
   if h.kind=='surge' and 0<d<150:
    if f.y>=f.floor-.1 or f.jumps_used==1 and f.vy>0:jump=True
   if h.kind=='breaker' and 0<d<270:
    if f.y>=f.floor-.1 or f.jumps_used==1 and f.vy>-100:jump=True
   if h.kind=='ceiling' and -150<d<230:duck=True
  cargo=min((c for c in f.cargos if c.released),key=lambda c:abs(c.x-f.x),default=f.cargo)
  if cargo.released:
   closing=(cargo.x-f.x)*cargo.vx<0
   if abs(cargo.x-f.x)<(120+abs(cargo.vx)*.05 if closing else 65) and f.y>=f.floor-.1:
    jump=True;duck=False;move=-1 if cargo.vx>0 else 1
   elif f.y<f.floor-8 and abs(cargo.x-f.x)<100:
    move=-1 if cargo.vx>0 else 1
    if f.jumps_used==1 and f.vy>0:jump=True
 else:
  # Spread damage across the duo to limit the survivor's enraged duration.
  aim=max(f.guardians,key=lambda a:a.hp).core(f.floor)
  # Run perpendicular to a locked firing lane, stay in the middle of the arena.
  threats=[a for a in f.guardians if a.hp>0 and (a.warning or a.attack or (a.exposed and any(b.enemy for b in f.shots)))]
  dest=640
  if threats:
   a=threats[-1];dest=430 if a.target[0]>620 else 850
  move=1 if f.x<dest-10 else -1 if f.x>dest+10 else 0
  for a in threats:
   if a.attack=='charge' and abs(a.x-f.x)<180:
    if f.y>=f.floor-.1:slide=True
   if (a.warning=='slam' or a.attack=='slam'):
    dest=430 if a.end>620 else 850;move=1 if f.x<dest-10 else -1 if f.x>dest+10 else 0
  for a in threats:
   if a.attack=='relay':
    from omacontra.stages.harbor.tide_guardian_attacks import relay_position
    x,_=relay_position(f,a,a.age)
    if 0<x-f.x<110 and f.y>=f.floor-.1:jump=True
    if a.enraged and a.age>1.8:duck=True;jump=False
   if a.warning=='stars' or a.attack=='stars':
    dest=(a.star_lanes[1]+a.star_lanes[2])/2;move=1 if f.x<dest-5 else -1 if f.x>dest+5 else 0
  coordinated=next((a for a in threats if a.linked and a.kind==1),None)
  if coordinated:
   from omacontra.stages.harbor.tide_guardian_attacks import relay_position
   dest=575;move=1 if f.x<dest-5 else -1 if f.x>dest+5 else 0
   if coordinated.attack=='relay':
    x,_=relay_position(f,coordinated,coordinated.age)
    if 0<x-f.x<110 and f.y>=f.floor-.1:jump=True
    if coordinated.age>1.8:duck=True;jump=False
  for b in f.shots:
   if b.kind=='orbit_bolt' and abs(b.x-f.x)<150 and b.y>f.floor-170 and f.y>=f.floor-.1:jump=True
   if b.kind=='pressure_ring' and abs(b.x-f.x)<160 and (b.x-f.x)*b.vx<0 and f.y>=f.floor-.1:jump=True
 return dict(move=move,slide=slide,jump=jump and not f.was_jump,duck=duck,shoot=shoot,aim=aim,interact=interact)

class TideTests(unittest.TestCase):
    def test_guardian_damage_does_not_trigger_gun_flash(self):
        f=Tidebreaker();f.advance_guardian();a=f.guardians[0];a.exposed=1
        x,y=a.core(f.floor)
        f.hit_guardians(x-10,y,x+10,y,1)
        self.assertGreater(a.flash,0);self.assertEqual(a.muzzle_flash,0)
        a.attack='volley';a.queue=[(0,0)];a.age=0
        f.guardian_step(.02)
        self.assertGreater(a.muzzle_flash,0)


    def test_wave_deck_has_no_interior_movement_wall(self):
        f=Tidebreaker(7);f.invuln=999
        for _ in range(250):f.step(.02,move=1)
        self.assertGreater(f.x,1200)
        f.start_warning('claw');self.assertGreater(f.target_x,1200)
        f.attack_direction=-1;f.spawn_wave('surge')
        self.assertGreater(f.hazards[-1].x,1280)
        for _ in range(300):f.step(.02,move=-1)
        self.assertLess(f.x,40)

    def test_core_takes_damage_during_attacks_and_recovery(self):
        f=Tidebreaker(1);x,y=f.core
        self.assertTrue(f.hit_target(x-90,y,x+90,y,1));self.assertEqual(f.boss_hp,f.boss_max-1)
        f.open_time=1;f.hit_target(x-90,y,x+90,y,1);self.assertEqual(f.boss_hp,f.boss_max-2)

    def test_guardians_take_damage_through_windups_attacks_and_recovery(self):
        f=Tidebreaker();f.advance_guardian()
        for a in f.guardians:
            for attack,warning,exposed in ((None,None,0),(None,'stars',0),('charge',None,0),('stars',None,0),(None,None,2)):
                a.attack=attack;a.warning=warning;a.exposed=exposed
                before=a.hp;x,y=a.core(f.floor)
                self.assertTrue(f.hit_target(x-70,y,x+70,y,3))
                self.assertEqual(a.hp,before-3)
        self.assertEqual(f.boss_hp,sum(a.hp for a in f.guardians))

    def test_damage_is_not_discarded_at_wave_phase_boundaries(self):
        f=Tidebreaker();x,y=f.core
        f.hit_target(x-70,y,x+70,y,205)
        self.assertEqual((f.wave_phase,f.boss_hp),(2,395))
        f.hit_target(x-70,y,x+70,y,200)
        self.assertEqual((f.wave_phase,f.boss_hp),(3,195))

    def test_low_surge_can_be_jumped_and_high_sweep_ducked(self):
        for kind,duck,height in [('surge',False,100),('ceiling',True,0)]:
            f=Tidebreaker(1);f.invuln=0;f.y=f.floor-height;f.hazards=[TideHazard(kind,f.x+3)]
            f.step(.01,duck=duck);self.assertEqual(f.hp,6)
        f=Tidebreaker(1);f.invuln=0;f.hazards=[TideHazard('surge',f.x+3)]
        f.step(.01);self.assertEqual(f.hp,5)

    def test_moving_out_of_claw_mark_avoids_damage(self):
        f=Tidebreaker(1);f.invuln=0;f.start_warning('claw');mark=f.target_x
        for _ in range(100):f.step(.02,move=1)
        self.assertEqual(f.target_x,mark);self.assertEqual(f.hp,6)

    def test_full_encounter_winnable_through_normal_controls(self):
        from omacontra.campaign_progress import prepare_encounter
        f=prepare_encounter(Tidebreaker(7),3);phases=set();attacks=set();stages=set()
        for _ in range(10000):
            phases.add(f.phase);stages.add(f.stage);attacks.update(h.kind for h in f.hazards)
            f.step(.02,**pilot(f))
            if f.state in ('won','dead'):break
        self.assertEqual(f.state,'won');self.assertGreater(f.hp,0)
        self.assertEqual(stages,{0,1});self.assertEqual(phases,{1,2,3})
        self.assertEqual(attacks,{'surge','claw','ceiling','breaker'})

    def test_phase_thresholds_scale_with_health_and_recovery_still_runs(self):
        f=Tidebreaker(1);f.open_time=5;x,y=f.core
        f.hit_target(x-70,y,x+70,y,f.boss_max/3)
        self.assertEqual((f.wave_phase,f.boss_hp),(2,f.boss_max*2/3))
        for _ in range(2500):
            controls=pilot(f);controls['shoot']=False
            f.step(.02,**controls)
            if f.open_time>0:break
        self.assertGreater(f.open_time,0)
        x,y=f.core;f.hit_target(x-70,y,x+70,y,f.boss_max/3)
        self.assertEqual((f.wave_phase,f.boss_hp),(3,f.boss_max/3))

    def test_all_wave_phases_rock_and_do_not_show_attack_instructions(self):
        for phase in (1,2,3):
            f=Tidebreaker();f.wave_phase=phase;f.tide_timer=999;f.combo_wait=999
            slopes=[]
            for _ in range(250):f.step(.02);slopes.append(f.deck_slope)
            self.assertGreater(max(slopes)-min(slopes),.02)
            f.start_warning('ceiling');self.assertEqual(f.notice_time,0)

    def test_undertow_alternates_wave_directions(self):
        f=Tidebreaker();f.wave_phase=2
        for round,direction in ((0,-1),(1,1)):
            f.tide_round=round;f.start_warning('surge');f.spawn_wave('surge')
            self.assertEqual(f.hazards[-1].direction,direction)

    def test_failed_crest_retries_without_reset(self):
        f=Tidebreaker(1);f.wave_phase=3;f.boss_hp=40
        f.combo_index=3;f.combo_failed=True;f.combo_wait=0
        f.step_crest(.02)
        self.assertEqual(f.open_time,3);self.assertEqual(f.combo_index,0)
        self.assertEqual(f.boss_hp,40)
        f.open_time=0;f.combo_index=3;f.combo_wait=0;f.step_crest(.02)
        self.assertEqual(f.open_time,6)

    def test_guardian_reveal_preserves_campaign_ribbon_capacity(self):
        from omacontra.campaign_progress import prepare_encounter
        f=prepare_encounter(Tidebreaker(),3);f.advance_guardian()
        self.assertEqual(f.hp,7)

    def test_both_guardians_arrive_and_both_must_die(self):
        f=Tidebreaker(1);f.hp=3;f.begin_reveal()
        for _ in range(260):f.step(.02,shoot=True)
        self.assertEqual(f.stage,1);self.assertEqual(f.state,'play')
        self.assertEqual(f.hp,4);self.assertEqual(len(f.guardians),2)
        self.assertGreater(f.guardians[0].x,640);self.assertLess(f.guardians[1].x,640)
        for i,a in enumerate(f.guardians):
            a.exposed=2;x,y=a.core(f.floor)
            f.hit_target(x-70,y,x+70,y,999)
            self.assertEqual(f.state,'play' if i==0 else 'dying')
        for _ in range(180):f.step(.02)
        self.assertEqual(f.state,'won');self.assertFalse(f.shots)

    def test_guardian_rendering_covers_both_actors_and_death(self):
        r=TideRenderer();s=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720)
        f=Tidebreaker(1);f.advance_guardian()
        for a in f.guardians:
            for attack in (('pistol','charge') if a.kind==1 else ('orbit','slam')):
                a.warning=attack;r.draw(cairo.Context(s),f)
                a.warning=None;a.attack=attack
                for age in (0,.3,.7,1.4):a.age=age;r.draw(cairo.Context(s),f)
            a.hp=0
            for age in (0,.1,1,2,3.4):a.death_age=age;r.draw(cairo.Context(s),f)

    def test_rolling_deck_keeps_grounded_feet(self):
        f=Tidebreaker(1);f.wave_phase=2;f.tide_timer=999
        for _ in range(300):
            f.step(.02,move=1)
            self.assertAlmostEqual(f.y,f.floor)
            self.assertLessEqual(abs(f.deck_slope),.075)

    def test_ocean_moves_on_both_sides(self):
        r=TideRenderer();f=Tidebreaker(1)
        s=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720)
        r.ocean(cairo.Context(s),f);before=bytes(s.get_data())
        f.clock=1.3;r.ocean(cairo.Context(s),f);after=bytes(s.get_data())
        stride=s.get_stride()
        for x in (100,1000):
            a=b''.join(before[y*stride+x*4:y*stride+(x+100)*4] for y in range(100,500))
            b=b''.join(after[y*stride+x*4:y*stride+(x+100)*4] for y in range(100,500))
            self.assertNotEqual(a,b)

    def test_guardian_practice_retries_without_water_or_cinema(self):
        from omacontra.boss_app import BossApp
        from omacontra.input_state import KeyboardState
        app=BossApp.__new__(BossApp)
        app.music=Mock()
        app.guardian_practice=True;app.tide_renderer=None;app.keyboard=KeyboardState()
        app.start_tide()
        self.assertEqual(app.f.stage,1);self.assertEqual(len(app.f.guardians),2)
        self.assertIsNone(app.journey_cinema)
        app.f.hp=1;app.f.guardians[0].hp=0
        app.reset_encounter()
        self.assertEqual(app.f.stage,1);self.assertEqual(app.f.hp,7)
        self.assertTrue(all(a.hp==a.maximum==190 for a in app.f.guardians))
        self.assertIsNone(app.journey_cinema)

    def test_host_continues_from_quattro_and_resets_tide(self):
        from unittest.mock import Mock
        from types import SimpleNamespace
        from omacontra.boss_app import BossApp
        from omacontra.input_state import KeyboardState
        from omacontra.stages.highway.chase_cinema import ChaseCinema
        app=BossApp.__new__(BossApp)
        app.music=Mock()
        app.keyboard=KeyboardState();app.keys=app.keyboard.keys
        app.level=2;app.f=SimpleNamespace(state='won',hp=2);app.chase_cinema=ChaseCinema('outro')
        app.chase_cinema.age=6;app.journey_cinema=None;app.tide_renderer=None
        app.intro=None;app.paused=False;app.shooting=True;app.slide_requested=False
        app.key(None,SimpleNamespace(hardware_keycode=36,keyval=65293))
        self.assertEqual(app.level,3);self.assertIsInstance(app.f,Tidebreaker);self.assertEqual(app.f.hp,3)
        self.assertEqual(app.journey_cinema.kind,'intro');self.assertFalse(app.shooting)
        app.f.hp=1;app.f.hazards=[TideHazard('surge',500)]
        app.reset_encounter()
        self.assertEqual(app.f.hp,7);self.assertEqual(app.f.max_hp,7);self.assertFalse(app.f.hazards)
        self.assertEqual(app.journey_cinema.age,0)

    def test_cinematic_skip_and_pause_do_not_advance_fight(self):
        from unittest.mock import Mock,patch
        from omacontra.boss_app import BossApp
        from omacontra.input_state import KeyboardState
        app=BossApp.__new__(BossApp)
        app.music=Mock()
        app.closed=False;app.last=0;app.placed=True;app.visible=True;app.paused=True
        app.intro=None;app.level=3;app.f=Tidebreaker();app.journey_cinema=JourneyCinema()
        app.chase_cinema=None;app.keyboard=KeyboardState();app.keys=app.keyboard.keys
        app.area=Mock();app.slide_requested=False;app.shooting=False;app.aim=None
        app.tide_outro_seen=False
        with patch('omacontra.boss_app.time.monotonic',return_value=.02):app.tick()
        self.assertEqual(app.journey_cinema.age,0);self.assertEqual(app.f.clock,0)
        app.paused=False;app.journey_cinema.skip()
        with patch('omacontra.boss_app.time.monotonic',return_value=.04):app.tick()
        self.assertIsNone(app.journey_cinema);self.assertEqual(app.f.clock,0)

    def test_render_tells_attacks_death_and_cinematics(self):
        r=TideRenderer();f=Tidebreaker(1)
        s=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720)
        for kind in ('surge','ceiling','claw'):
            f.start_warning(kind);r.draw(cairo.Context(s),f)
            for age in (0,.18,.4,.7,1.):
                f.hazards=[TideHazard(kind,420,age)];r.draw(cairo.Context(s),f)
        f.hazards=[]
        for state in ('dying','won','dead'):
            f.state=state
            for age in (0,.001,1.4,3.4):f.death_age=age;r.draw(cairo.Context(s),f)
        for kind in ('intro','outro'):
            cinema=JourneyCinema(kind)
            for age in (0,5,19.5,24.5,INTRO_DURATION):
                cinema.age=age;cinema.draw(cairo.Context(s),r,f)
        self.assertEqual(f.clock,0)

if __name__=='__main__':unittest.main()

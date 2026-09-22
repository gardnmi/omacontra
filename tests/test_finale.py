import math
import unittest
import cairo
from omacontra.stages.space.finale import Finale, Shot, DEPARTURE_DURATION, boarding_pose, ENCOUNTER_DURATION
from omacontra.stages.space.finale_art import FinaleRenderer

def pilot(f):
    targets=[f.node(i) for i,h in enumerate(f.nodes) if h>0] if f.phase==1 else [f.boss]
    target=min(targets,key=lambda p:abs(p[0]-f.x))
    best=None
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            norm=max(1,math.hypot(dx,dy));nx=max(45,min(1235,f.x+dx/norm*260*.25));ny=max(310,min(655,f.y+dy/norm*260*.25))
            danger=0.
            for b in f.shots:
                if not b.enemy or f.invuln>.35:continue
                for t in (.08,.18,.3):
                    dist=math.hypot(b.x+b.vx*t-(f.x+(nx-f.x)*t/.25),b.y+b.vy*t-(f.y+(ny-f.y)*t/.25))
                    danger+=max(0,42-dist)**2*3
            score=danger+abs(nx+(f.laser_muzzle[0]-f.x)-target[0])*.13+abs(ny-565)*.06
            if best is None or score<best[0]:best=(score,dx,dy,danger)
    _,dx,dy,danger=best
    return dict(move=dx,vertical=dy,shoot=True,slide_pressed=danger>600 and f.dash_cooldown<=0)

class FinaleTests(unittest.TestCase):
    def test_screensaver_transition_persists_into_last_phase(self):
        f=Finale();f.skip();f.invuln=999
        f.step(.04);self.assertEqual(f.screensaver_age,0)
        f.nodes=[0,0]
        for _ in range(80):f.step(.04)
        self.assertGreater(f.screensaver_age,3)
        age=f.screensaver_age;f.boss_hp=f.boss_max*.3
        f.step(.04)
        self.assertGreater(f.screensaver_age,age)
        surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720)
        FinaleRenderer().draw(cairo.Context(surface),f)

    def test_boarding_walk_lift_and_cockpit_entry_are_continuous(self):
        # DHH reaches the cab before the gates close and remains on its deck
        # throughout the ride; he only crosses to the ship after it stops.
        self.assertEqual(boarding_pose(0)[:2],(545,495))
        self.assertAlmostEqual(boarding_pose(5.2)[0],710)
        for t in (5.8,7,9,10.8):
            x,floor,camera,door,alpha,moving=boarding_pose(t)
            self.assertEqual(x,710);self.assertFalse(moving)
            self.assertAlmostEqual(door,0)
            self.assertTrue(445<=floor+camera<=495)
        self.assertAlmostEqual(boarding_pose(11.4)[3],1)
        self.assertEqual(boarding_pose(14)[4],0)
        self.assertAlmostEqual(boarding_pose(14)[0],970)
        for t in (3,5.2,5.8,10.8,11.4,13.4,13.8,14):
            before=boarding_pose(t-.0001);after=boarding_pose(t+.0001)
            self.assertLess(math.dist(before[:3],after[:3]),.1)

    def test_stolen_laser_replaces_player_bullets_and_stops_on_release(self):
        f=Finale();f.skip();f.volley=999
        f.x=f.node(0)[0]-10
        f.step(.02,shoot=True)
        self.assertTrue(f.beam);self.assertTrue(f.beam_hit)
        self.assertEqual(f.beam[0],f.laser_muzzle)
        self.assertLess(f.nodes[0],f.node_max)
        self.assertEqual(f.nodes[1],f.node_max)
        self.assertFalse(any(not b.enemy for b in f.shots))
        hp=f.nodes[:];f.step(.02,shoot=False)
        self.assertFalse(f.beam);self.assertEqual(f.nodes,hp)

    def test_laser_damage_uses_elapsed_time_and_does_not_clear_enemy_shots(self):
        for dt in (.02,.04):
            f=Finale();f.skip();f.nodes=[0,0];f.last_phase=2;f.volley=999
            f.x=f.boss[0]-10
            enemy=Shot(80,350,0,100);f.shots=[enemy]
            f.step(dt,shoot=True)
            self.assertAlmostEqual(f.boss_hp,f.boss_max-96*dt)
            self.assertIn(enemy,f.shots)
            f.boss_hp=.01;f.step(dt,shoot=True)
            self.assertEqual(f.state,'ending');self.assertFalse(f.beam)

    def test_full_playthrough(self):
        from omacontra.campaign_progress import prepare_encounter
        for dt in (.02,.04):
            f=prepare_encounter(Finale(),5);f.skip();phases=set()
            for _ in range(int(300/dt)):
                phases.add(f.phase);f.step(dt,**pilot(f))
                if f.state in ('won','dead'):break
            self.assertEqual(f.state,'won');self.assertEqual(phases,{1,2,3})
    def test_deck_tobi_and_tower_share_foreground_camera(self):
        from unittest.mock import patch
        f=Finale();renderer=FinaleRenderer()
        surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720)
        for t in (5.8,7,8,9,10.8):
            f.age=t;positions={}
            def capture(c,sheet,frame,x,y,w,h,**kwargs):
                if sheet=='wyrm-stone-platform.png' and y==495:positions['deck']=c.user_to_device(x,y)[1]
                elif sheet=='foundry-rescue.png':positions['feet']=c.user_to_device(x,y+h)[1]
                elif sheet=='shuttle-launch-gantry.png':positions['base']=c.user_to_device(x,y+h)[1]
            with patch('omacontra.stages.space.finale_art.sprites.draw',side_effect=capture):
                renderer.departure(cairo.Context(surface),f)
            expected=495+boarding_pose(t)[2]
            for part in ('deck','feet','base'):
                self.assertAlmostEqual(positions[part],expected)

    def test_departure_and_reset(self):
        f=Finale()
        for _ in range(int(DEPARTURE_DURATION/.04)+1):f.step(.04,shoot=True)
        self.assertEqual(f.state,'encounter');self.assertFalse(f.shots)
        for _ in range(int(ENCOUNTER_DURATION/.04)+1):f.step(.04,shoot=True)
        self.assertEqual(f.state,'play');self.assertFalse(f.shots)
        self.assertEqual(Finale().state,'departure')
    def test_encounter_safe_handoff_and_skip(self):
        f=Finale();f.state='encounter';hp=f.hp
        for _ in range(350):f.step(.04,move=1,shoot=True)
        self.assertEqual(f.state,'encounter');self.assertEqual(f.hp,hp)
        self.assertEqual(f.shots,[]);self.assertEqual(f.beam,[])
        f.skip();self.assertEqual(f.state,'play')
        self.assertEqual((f.x,f.y),(640.,590.))
        self.assertEqual(f.clock,ENCOUNTER_DURATION)
        for _ in range(50):f.step(.04)
        self.assertFalse(f.shots)
        for _ in range(10):f.step(.04)
        self.assertTrue(any(s.enemy for s in f.shots))

    def test_foundry_continue_and_finale_restart(self):
        from types import SimpleNamespace
        from omacontra.boss_app import BossApp
        from omacontra.input_state import KeyboardState
        app=BossApp.__new__(BossApp);app.keyboard=KeyboardState();app.keys=app.keyboard.keys
        app.level=4;app.f=SimpleNamespace(state='won',hp=2);app.intro=None;app.paused=False
        app.shooting=True;app.slide_requested=False
        app.key(None,SimpleNamespace(hardware_keycode=36,keyval=65293))
        self.assertEqual(app.level,5);self.assertEqual(app.f.state,'departure');self.assertEqual(app.f.hp,3)
        self.assertFalse(app.shooting);self.assertFalse(app.keys)
        app.f.skip();app.reset_encounter()
        self.assertEqual(app.f.state,'departure');self.assertEqual(app.f.hp,9);self.assertEqual(app.f.max_hp,9)

    def test_dash_and_bounds(self):
        f=Finale();f.skip();f.invuln=0
        f.shots=[Shot(f.x,f.y,0,0)];f.step(.02,move=1,slide_pressed=True)
        self.assertEqual(f.hp,7);self.assertGreater(f.dash_cooldown,0)
        for _ in range(200):f.step(.02,move=1,vertical=1)
        self.assertLessEqual(f.x,1235);self.assertLessEqual(f.y,655)
    def test_cinematics_and_phases_render(self):
        f=Finale();r=FinaleRenderer();s=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720)
        for state,times in [('departure',(0,4,9,16.9)),('encounter',(0,2,3.8,4.6,6.8,8.5,11.5,14.5)),('ending',(0,.8,2,6.9,7,9.9,10,13.9,14,17.9,18,20.9,21,24,27)),('won',(27,))]:
            f.state=state
            for t in times:f.age=t;r.draw(cairo.Context(s),f)
        f.state='play'
        for nodes,hp in (([65,65],800),([0,0],600),([0,0],100)):
            f.nodes=nodes;f.boss_hp=hp;f.burst();r.draw(cairo.Context(s),f)
    def test_phase_patterns_are_distinct_and_from_jellyfish(self):
        f=Finale();f.skip();phase_kinds=[]
        for nodes in ([450,450],[0,0]):
            f.nodes=nodes;kinds=set()
            for i in range(3):
                f.shots=[];f.round=i;f.burst();x,y=f.emitter
                for b in f.shots:
                    self.assertLessEqual(math.hypot(b.x-x,b.y-y),47)
                    kinds.add(b.kind)
            phase_kinds.append(kinds)
        self.assertEqual(phase_kinds,[{'pearl','spore'},{'shard','needle'}])

    def test_enclosure_cannot_melt_in_one_short_burst(self):
        f=Finale();f.skip();f.volley=999
        for _ in range(25):
            x,y=f.node(0);f.shots=[Shot(x,y+5,0,-850,False)];f.step(.02)
        self.assertGreater(f.nodes[0],400);self.assertEqual(f.phase,1)

    def test_ending_has_no_dhh_dialogue(self):
        from unittest.mock import patch
        f=Finale();f.state='ending';r=FinaleRenderer()
        surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720)
        with patch('omacontra.stages.space.finale_art.label') as label:
            for t in (0,4,8,12,16,20,24):
                f.age=t;r.draw(cairo.Context(surface),f)
        self.assertFalse(any('DHH:' in str(call.args[3]) or 'FIX ANYTHING' in str(call.args[3]) for call in label.call_args_list))

    def test_enclosure_destruction_does_not_repeat_at_low_health(self):
        from unittest.mock import patch
        f=Finale();f.skip();f.nodes=[0,0];f.phase_age=.5
        surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720)
        for hp,expected in ((f.boss_max,True),(f.boss_max*.39,False)):
            f.boss_hp=hp
            with patch('omacontra.stages.space.finale_art.sprites.draw') as draw:
                FinaleRenderer().draw(cairo.Context(surface),f)
            guardian=[call for call in draw.call_args_list
                      if call.args[1]=='finale-guardian.png' and call.args[2][1]==0]
            self.assertEqual(bool(guardian),expected)

    def test_final_phase_has_three_times_the_old_health_budget(self):
        f=Finale();f.nodes=[0,0]
        self.assertEqual(f.boss_max-f.final_phase_max,750)
        self.assertEqual(f.final_phase_max,1500)
        f.boss_hp=f.final_phase_max+.1;self.assertEqual(f.phase,2)
        f.boss_hp=f.final_phase_max;self.assertEqual(f.phase,3)
        # Five seconds of uninterrupted laser damage no longer ends it.
        f.boss_hp-=96*5
        self.assertGreater(f.boss_hp,1000);self.assertEqual(f.phase,3)

    def test_low_health_escalation_keeps_attacking(self):
        f=Finale();f.skip();f.nodes=[0,0];f.last_phase=2
        f.boss_hp=f.final_phase_max+1;f.volley=1.8
        threat=Shot(80,350,0,100)
        x,y=f.boss;f.shots=[threat,Shot(x,y+10,0,-850,False)]
        f.step(.02)
        self.assertEqual(f.phase,3);self.assertNotIn(threat,f.shots)
        self.assertLessEqual(f.volley,2.)
        previous=f.round
        for _ in range(1000):
            f.invuln=1;f.step(.02)
        self.assertEqual(f.state,'play')
        self.assertGreater(f.round,previous+15)
        self.assertTrue(any(b.enemy for b in f.shots))

    def test_ending_keeps_rescue_a_surprise_and_uses_space_burst(self):
        from unittest.mock import patch
        f=Finale();f.state='ending';f.nodes=[0,0];f.boss_hp=0
        r=FinaleRenderer();surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720)
        with patch.object(r,'catch_car') as car:
            for t in (7,9,11,12,12.44):
                f.age=t;r.draw(cairo.Context(surface),f)
            car.assert_not_called()
            f.age=12.8;r.draw(cairo.Context(surface),f)
            self.assertTrue(car.called)
        with patch('omacontra.stages.space.finale_art.sprites.draw') as draw:
            for t in (.55,.9,1.4,2):
                f.age=t;r.draw(cairo.Context(surface),f)
            self.assertFalse(any(call.args[1]=='quattro-explosion.png' for call in draw.call_args_list))

    def test_phase_clear_and_damage(self):
        f=Finale();f.skip();f.nodes=[0,0];f.shots=[Shot(50,500,0,100)]
        f.step(.02);self.assertFalse(any(b.enemy for b in f.shots))
        f.boss_hp=1;x,y=f.boss;f.shots=[Shot(x,y+10,0,-850,False)]
        f.step(.02);self.assertEqual(f.state,'ending');self.assertFalse(f.shots)

if __name__=='__main__':unittest.main()

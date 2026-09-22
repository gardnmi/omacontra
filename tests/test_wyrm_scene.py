import math
import unittest
from unittest.mock import patch
import cairo
from omacontra.stages.dragon.foundry import Foundry, Hazard
from omacontra.stages.dragon.foundry_art import FoundryRenderer, FoundryIntro
from omacontra.stages.dragon.wyrm_scene import MOUTH, EYES, point, pose, head_angle, lightning_paths

class WyrmSceneTests(unittest.TestCase):
    def test_final_charge_lights_three_sources_without_firing(self):
        from omacontra.stages.dragon import wyrm_scene
        f=Foundry();f.begin_rescue();f.rescue_age=4.1
        r=FoundryRenderer();c=cairo.Context(cairo.ImageSurface(cairo.FORMAT_RGB24,1280,720))
        with patch('omacontra.stages.dragon.wyrm_scene.storm_lance') as lance,patch('omacontra.stages.dragon.wyrm_scene.halo',wraps=wyrm_scene.halo) as halo:
            r.draw(c,f)
            lance.assert_not_called()
            centers=[call.args[1:3] for call in halo.call_args_list]
            for anchor in (*EYES,MOUTH):self.assertIn(f.dragon_point(*anchor),centers)

    def test_storm_enters_from_below_screen_without_initial_overlay(self):
        f=Foundry();f.lava_age=0;r=FoundryRenderer()
        s=cairo.ImageSurface(cairo.FORMAT_RGB24,1280,720);c=cairo.Context(s)
        c.set_source_rgb(.2,.3,.4);c.paint();before=bytes(s.get_data())
        r.terrace.storm(c,f)
        self.assertEqual(bytes(s.get_data()),before)
        levels=[]
        for age in (0,1,2,3,4,5,6,7,10):
            f.lava_age=age;levels.append(f.lava_surface)
        self.assertGreater(levels[0],720);self.assertEqual(levels[-1],560)
        self.assertTrue(all(a>=b for a,b in zip(levels,levels[1:])))

    def test_eye_volley_uses_the_eye_that_charged(self):
        for index in (0,1):
            f=Foundry();f.clock=3;f.forge_round=index
            charged=f.dragon_point(*EYES[index])
            f.forge_warning='wisps';f.forge_timer=0
            f.step(0);f.step(0)
            self.assertEqual(len(f.bolts),5)
            self.assertTrue(all((b.x,b.y)==charged for b in f.bolts))

    def test_ledge_eruption_is_warned_locked_and_covers_only_marked_platform(self):
        f=Foundry();f.laser=True;f.mount_hp=0
        f.support=f.platforms[0];f.x=345;f.y=f.floor
        f.update_ledge_pressure(1.6)
        x,y,age,width=f.ledge_warning
        self.assertEqual((x-width,x+width,y),f.platforms[0])
        f.support=f.platforms[1];f.x=220;f.y=f.floor
        f.update_ledge_pressure(1.)
        self.assertFalse(f.hazards)
        f.update_ledge_pressure(.11)
        h=f.hazards[0]
        self.assertEqual((h.x,h.y,h.width),(x,y,width))
        f.invuln=0;f.forge_timer=999
        for _ in range(20):f.step(.02)
        self.assertEqual(f.hp,6)

    def test_stationary_laser_tanking_cannot_win_phase_two(self):
        for platform in range(len(Foundry().platforms)):
            f=Foundry();f.mount_hp=0;f.laser=True;f.lava_age=7
            f.support=f.platforms[platform];f.x=sum(f.support[:2])/2;f.y=f.floor
            for _ in range(1600):
                f.step(.02,shoot=True,aim=f.core)
                if f.state!='play':break
            self.assertEqual(f.state,'dead')
            self.assertGreater(f.boss_hp,0)

    def test_cobra_pose_moves_and_all_mouth_anchors_follow_it(self):
        f=Foundry();points=[]
        for t in (0,1,2,3,4,5,6):
            f.clock=t;points.append(point(f,*MOUTH))
            self.assertEqual(f.cannon,point(f,*MOUTH))
            self.assertEqual(f.mount_target,point(f,*MOUTH))
            self.assertEqual(f.shoulder_path()[0],point(f,*MOUTH))
            self.assertLessEqual(abs(head_angle(f)),.045)
        self.assertGreater(max(x for x,y in points)-min(x for x,y in points),30)
        # Smooth sway cannot teleport the damaging beam between frames.
        f.clock=2;a=f.mount_target;f.clock+=.02
        self.assertLess(math.dist(a,f.mount_target),2)

    def test_updraft_marks_locked_location_before_damaging(self):
        f=Foundry();f.mount_hp=0;f.forge_timer=999;f.invuln=0
        f.support=f.platforms[0];f.x=345;f.y=f.floor
        f.hazards=[Hazard('updraft',345,age=0,y=f.floor)]
        for _ in range(10):f.step(.02)
        self.assertEqual(f.hp,6)
        for _ in range(5):f.step(.02)
        self.assertEqual(f.hp,5)
        f=Foundry();f.mount_hp=0;f.forge_timer=999;f.invuln=0;f.x=500
        f.hazards=[Hazard('updraft',345,age=.3,y=535)]
        f.step(.02);self.assertEqual(f.hp,6)

    def test_intro_approaches_in_depth_with_glow_before_body(self):
        f=Foundry();r=FoundryRenderer();cinema=FoundryIntro()
        c=cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720))
        with patch.object(r.terrace,'dragon') as draw:
            cinema.age=3.4;cinema.draw(c,r,f);early=draw.call_args.kwargs
            cinema.age=6.2;cinema.draw(c,r,f);late=draw.call_args.kwargs
        self.assertLess(early['scale'],.4);self.assertGreater(late['scale'],.99)
        self.assertLess(early['alpha'],.1);self.assertGreater(early['glow_strength'],.8)
        self.assertEqual(f.clock,0);self.assertEqual(f.x,210)

    def test_lightning_is_deterministic_branched_and_only_scenery(self):
        paths=lightning_paths(3)
        self.assertEqual(paths,lightning_paths(3));self.assertGreater(len(paths),3)
        self.assertGreater(len(paths[0]),40)
        f=Foundry();r=FoundryRenderer();c=cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720))
        before=(f.hp,f.x,f.y,len(f.bolts))
        r.background(c,3.5)
        self.assertEqual(before,(f.hp,f.x,f.y,len(f.bolts)))

    def test_updraft_first_and_last_frames_keep_cairo_valid(self):
        f=Foundry();r=FoundryRenderer()
        c=cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720))
        for age in (0,.001,.25,.6,1.05):
            f.hazards=[Hazard('updraft',345,age=age,y=535)]
            r.draw(c,f)
        c.set_source_rgb(1,1,1);c.paint()

    def test_rescue_and_boarding_keep_new_scenery_and_original_car(self):
        from omacontra.stages.space.finale import Finale
        from omacontra.stages.space.finale_art import FinaleRenderer
        from omacontra.rendering import sprites
        c=cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720))
        f=Foundry();f.lava_age=7;f.begin_rescue();f.rescue_age=4.9
        renderer=FoundryRenderer();renderer.background(c,0)
        with patch('omacontra.rendering.sprites.draw',wraps=sprites.draw) as draw:
            renderer.draw(c,f)
            sheets=[call.args[1] for call in draw.call_args_list]
            self.assertIn('foundry-rescue.png',sheets)
            self.assertIn('wyrm-stone-platform.png',sheets)
            self.assertNotIn('foundry-arena.png',sheets)
        finale=Finale();finale.age=8
        with patch('omacontra.rendering.sprites.draw',wraps=sprites.draw) as draw:
            FinaleRenderer().departure(c,finale)
            sheets=[call.args[1] for call in draw.call_args_list]
            for name in ('wyrm-mist-arena.png','wyrm-stone-platform.png','shuttle-launch-gantry.png','foundry-rescue.png'):
                self.assertIn(name,sheets)
            for old in ('foundry-arena.png','foundry-launch-backdrop.png'):
                self.assertNotIn(old,sheets)

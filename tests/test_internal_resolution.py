import unittest
from types import SimpleNamespace
from unittest.mock import Mock
import cairo
from omacontra.boss_app import BossApp

class InternalResolutionTests(unittest.TestCase):
    def app(self,width=3840,height=2160):
        a=BossApp.__new__(BossApp)
        a.area=SimpleNamespace(get_allocated_width=lambda:width,get_allocated_height=lambda:height)
        a.level=1;a.intro=None;a.continue_screen=None;a.paused=False
        a.f=SimpleNamespace(state='play',x=200,facing=1,player_center=(200,500))
        a.aim=None;a.keys=set();a.shooting=False
        a.chase_cinema=a.journey_cinema=a.foundry_intro=None
        self.calls=0
        def native(c,*args):
            self.calls+=1
            self.assertEqual((c.get_target().get_width(),c.get_target().get_height()),(1280,720))
            self.assertEqual(c.user_to_device(1280,720),(1280,720))
            self.assertEqual(c.clip_extents(),(0,0,1280,720))
        a.renderer=SimpleNamespace(**{n:Mock(side_effect=native) for n in ('background','weak_point','objects','hud')})
        for n in ('chase_renderer','tide_renderer','foundry_renderer','finale_renderer','continue_renderer','intro_renderer'):
            setattr(a,n,SimpleNamespace(draw=Mock(side_effect=native)))
        a.frontend=SimpleNamespace(page=None,draw=Mock(side_effect=native))
        return a

    def test_every_screen_uses_one_720p_surface_at_4k(self):
        a=self.app();target=cairo.Context(cairo.ImageSurface(cairo.FORMAT_RGB24,3840,2160))
        frame=None
        for level in range(1,6):
            a.level=level;a.draw(a.area,target)
            if frame is None:frame=a.frame.surface
            self.assertIs(a.frame.surface,frame)
        for level,attribute in ((2,'chase_cinema'),(3,'journey_cinema'),(4,'foundry_intro')):
            a.level=level;setattr(a,attribute,a.finale_renderer)
            a.draw(a.area,target);setattr(a,attribute,None)
        a.intro=object();a.draw(a.area,target)
        self.assertEqual(a.intro_renderer.draw.call_args.args[2:],(1280,720))
        a.intro=None;a.continue_screen=object();a.draw(a.area,target)
        a.continue_screen=None
        for menu in ('mode','pause','results','music','credits'):
            a.frontend.page=menu;a.draw(a.area,target)
        self.assertIs(a.frame.surface,frame)
        self.assertGreater(self.calls,20)

    def test_letterboxing_pointer_mapping_and_resize_reuse(self):
        for width,height in ((1920,1080),(1920,1200),(2560,1080),(1024,768),(960,540)):
            a=self.app(width,height)
            def fill(c,*args):c.set_source_rgb(1,0,0);c.paint()
            a.level=5;a.finale_renderer.draw.side_effect=fill;a.frontend.draw.side_effect=None
            surface=cairo.ImageSurface(cairo.FORMAT_RGB24,width,height)
            a.draw(a.area,cairo.Context(surface));surface.flush()
            data=surface.get_data();stride=surface.get_stride()
            def pixel(x,y):return bytes(data[y*stride+x*4:y*stride+x*4+3])
            self.assertEqual(pixel(width//2,height//2),b'\x00\x00\xff')
            if width/height!=16/9:self.assertEqual(pixel(0,0),b'\x00\x00\x00')
            ox,oy,scale=a.viewport()
            a.motion(a.area,SimpleNamespace(x=ox+333*scale,y=oy+222*scale))
            self.assertAlmostEqual(a.aim[0],333);self.assertAlmostEqual(a.aim[1],222)
            original=a.frame.surface
            a.area=SimpleNamespace(get_allocated_width=lambda:1280,get_allocated_height=lambda:720)
            a.draw(a.area,cairo.Context(cairo.ImageSurface(cairo.FORMAT_RGB24,1280,720)))
            self.assertIs(a.frame.surface,original)

    def test_hidpi_display_scale_does_not_enlarge_internal_surface(self):
        a=self.app(1920,1080)
        surface=cairo.ImageSurface(cairo.FORMAT_RGB24,3840,2160)
        surface.set_device_scale(2,2)
        a.draw(a.area,cairo.Context(surface))
        self.assertEqual(a.frame.surface.get_device_scale(),(1.,1.))
        self.assertEqual((a.frame.width,a.frame.height),(1280,720))

    def test_scene_camera_transform_cannot_leak_into_hud(self):
        a=self.app();a.level=5
        a.finale_renderer.draw.side_effect=lambda c,*args:c.translate(0,150)
        surface=cairo.ImageSurface(cairo.FORMAT_RGB24,3840,2160)
        a.draw(a.area,cairo.Context(surface))
        self.assertEqual(self.calls,1)

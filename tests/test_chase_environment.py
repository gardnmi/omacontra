import unittest
import cairo
from omacontra.stages.highway.chase import Chase
from omacontra.stages.highway.chase_environment import CoastEnvironment
from omacontra.rendering import sprites

class CoastEnvironmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.road=cairo.ImageSurface.create_from_png(str(sprites.ASSETS/'quattro-coast.png'))
        cls.env=CoastEnvironment(cls.road)

    def render(self,t,ambient=True,offset=0):
        s=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,1000);c=cairo.Context(s)
        c.translate(0,offset);sprites.paint_background(c,self.road,0,0,1280,720)
        f=Chase();f.clock=t;f.distance=t*700
        if ambient:self.env.draw(c,f)
        s.flush();return s

    def sun(self,s,offset=0):
        data=bytes(s.get_data());stride=s.get_stride()
        return b''.join(data[y*stride+975*4:y*stride+1180*4] for y in range(205+offset,344+offset))

    def test_sun_only_changes_under_transparent_cloud_pixels(self):
        for offset in (0,240):
            base=self.render(0,False,offset)
            original=self.sun(base,offset)
            for t in (0,6,20,45,100):
                overlay=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,1000)
                c=cairo.Context(overlay);c.translate(0,offset)
                self.env.sun_clouds(c,t);overlay.flush()
                mask=self.sun(overlay,offset)
                result=self.sun(self.render(t,offset=offset),offset)
                # Uncovered pixels, including the disc outline, remain exact.
                for i in range(0,len(original),4):
                    if mask[i+3]==0:self.assertEqual(original[i:i+4],result[i:i+4])
                self.assertNotEqual(original,result)

    def test_motion_is_visible_and_pause_is_stable(self):
        first=bytes(self.render(2).get_data())
        self.assertEqual(first,bytes(self.render(2).get_data()))
        later=bytes(self.render(4).get_data())
        self.assertGreater(sum(a!=b for a,b in zip(first,later)),1000)

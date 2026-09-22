import unittest
import cairo
from frame_buffer import FrameBuffer


class FrameBufferTests(unittest.TestCase):
    def test_fullscreen_keeps_scene_at_native_resolution_and_reuses_surface(self):
        frame = FrameBuffer(8, 6)
        surface = frame.surface
        output = cairo.ImageSurface(cairo.FORMAT_RGB24, 16, 12)
        target = cairo.Context(output)
        target.scale(2, 2)

        def render(scene):
            self.assertEqual(scene.user_to_device(8, 6), (8, 6))
            self.assertEqual(scene.clip_extents(), (0, 0, 8, 6))
            scene.set_source_rgb(1, 0, 0)
            scene.rectangle(2, 1, 1, 1)
            scene.fill()
            scene.translate(99, 99)
            scene.rectangle(0, 0, 1, 1)
            scene.clip()

        for _ in range(2):
            frame.draw(target, render)
            self.assertIs(frame.surface, surface)
            self.assertEqual(target.user_to_device(8, 6), (16, 12))
        expected = cairo.ImageSurface(cairo.FORMAT_RGB24, 16, 12)
        ctx = cairo.Context(expected)
        ctx.set_source_rgb(0, 0, 0);ctx.paint()
        ctx.set_source_rgb(1, 0, 0);ctx.rectangle(4, 2, 2, 2);ctx.fill()
        self.assertEqual(bytes(output.get_data()), bytes(expected.get_data()))

"""Compose expensive scenes at game resolution before presenting pixel art."""
import cairo


class FrameBuffer:
    def __init__(self, width, height):
        self.surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
        self.width, self.height = width, height

    def draw(self, target, render):
        # A fresh context prevents camera transforms and clips leaking frames.
        scene = cairo.Context(self.surface)
        scene.set_source_rgb(0, 0, 0)
        scene.paint()
        render(scene)
        target.save()
        target.rectangle(0, 0, self.width, self.height)
        target.clip()
        target.set_source_surface(self.surface)
        target.get_source().set_filter(cairo.FILTER_NEAREST)
        target.paint()
        target.restore()

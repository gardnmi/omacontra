"""Cairo drawing protocol for the browser canvas backend.

The game imports its original renderers. Only this platform module is replaced.
Commands are flushed once per frame inside the worker, rather than crossing the
Python/JavaScript boundary for every path/transform. Images retain source pixels.
"""

import math
import json
from collections import namedtuple

FORMAT_ARGB32 = 0
FORMAT_RGB24 = 1
FILTER_NEAREST = 0
FILTER_BILINEAR = 1
FILTER_BEST = 1
ANTIALIAS_NONE = 0
FONT_SLANT_NORMAL = 0
FONT_WEIGHT_BOLD = 1
LINE_CAP_SQUARE = 2
LINE_JOIN_MITER = 0
EXTEND_REPEAT = 1
EXTEND_REFLECT = 2
OPERATOR_OVER = "source-over"
OPERATOR_ADD = "lighter"
OPERATOR_DEST_IN = "destination-in"
OPERATOR_IN = "source-in"
OPERATOR_HSL_COLOR = "color"
FILL_RULE_EVEN_ODD = "evenodd"
IMAGES = {}
commands = []
definitions = []
releases = []
counter = 0
TextExtents = namedtuple(
    "TextExtents", "x_bearing y_bearing width height x_advance y_advance"
)


def uid():
    global counter
    counter += 1
    return counter


def flush():
    result = json.dumps(
        {"definitions": definitions, "commands": commands, "releases": releases},
        separators=(",", ":"),
        allow_nan=False,
    )
    definitions.clear()
    commands.clear()
    releases.clear()
    return result


class Matrix:
    def __init__(self, xx=1, yx=0, xy=0, yy=1, x0=0, y0=0):
        self.v = [xx, yx, xy, yy, x0, y0]

    def __iter__(self):
        return iter(self.v)

    def multiply(self, b):
        a, c, e, g, i, k = self.v
        b, d, f, h, j, l = b.v
        return Matrix(
            a * b + e * d,
            c * b + g * d,
            a * f + e * h,
            c * f + g * h,
            a * j + e * l + i,
            c * j + g * l + k,
        )

    def point(self, x, y):
        a, b, c, d, e, f = self.v
        return a * x + c * y + e, b * x + d * y + f

    def inverted(self):
        a, b, c, d, e, f = self.v
        det = a * d - b * c
        if abs(det) < 1e-12:
            return Matrix()
        return Matrix(
            d / det,
            -b / det,
            -c / det,
            a / det,
            (c * f - d * e) / det,
            (b * e - a * f) / det,
        )


class ImageSurface:
    def __init__(self, format, width, height, asset=None):
        self.id = uid()
        self.width = int(width)
        self.height = int(height)
        self.format = format
        definitions.append([self.id, self.width, self.height, asset, format])

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_stride(self):
        return self.width * 4

    def flush(self):
        pass

    def __del__(self):
        try:
            releases.append(self.id)
        except Exception:
            pass

    @classmethod
    def create_from_png(cls, path):
        name = str(path).split("/assets/")[-1]
        return cls.from_asset("raw/" + name)

    @classmethod
    def from_asset(cls, key):
        value = IMAGES[key]
        return cls(FORMAT_ARGB32, value["width"], value["height"], value["file"])

    @classmethod
    def create_for_data(cls, data, format, width, height, stride=None):
        s = cls(format, width, height)
        # Screensaver pixels stay inside the worker; no base64 frame transport.
        from js import cairo_pixels

        cairo_pixels(s.id, data, width, height, format)
        return s


class SurfacePattern:
    def __init__(self, surface):
        self.surface = surface
        self.matrix = Matrix()
        self.extend = 0
        self.filter = FILTER_BILINEAR

    def set_matrix(self, matrix):
        self.matrix = matrix

    def set_extend(self, extend):
        self.extend = extend

    def set_filter(self, filter):
        self.filter = filter

    def value(self):
        return ["surface", self.surface.id, list(self.matrix), self.extend, self.filter]


class LinearGradient:
    def __init__(self, *args):
        self.args = args
        self.stops = []

    def add_color_stop_rgba(self, *args):
        self.stops.append(args)

    def add_color_stop_rgb(self, offset, r, g, b):
        self.add_color_stop_rgba(offset, r, g, b, 1)

    def value(self):
        return ["linear", self.args, self.stops[:]]


class RadialGradient(LinearGradient):
    def value(self):
        return ["radial", self.args, self.stops[:]]


class SolidPattern:
    def __init__(self, *rgba):
        self.rgba = rgba

    def value(self):
        return ["color", self.rgba]

    def set_filter(self, *_):
        pass


class Context:
    def __init__(self, surface):
        self.id = uid()
        self.surface = surface
        self.matrix = Matrix()
        self.clip_box = [0, 0, surface.width, surface.height]
        self.groups = []
        self.stack = []
        self.source = SolidPattern(0, 0, 0, 1)
        self.font = "monospace"
        self.size = 10
        self.bold = False
        self.point = (0, 0)
        self.path_bounds = None
        self.single_rect = None
        commands.append(["context", self.id, surface.id])

    def emit(self, op, *args):
        commands.append([self.id, op, *args])

    def save(self):
        self.stack.append(
            (
                self.matrix,
                self.clip_box[:],
                self.source,
                self.font,
                self.size,
                self.bold,
            )
        )
        self.emit("save")

    def restore(self):
        self.matrix, self.clip_box, self.source, self.font, self.size, self.bold = (
            self.stack.pop()
        )
        self.emit("restore")

    def translate(self, x, y):
        self.matrix = self.matrix.multiply(Matrix(x0=x, y0=y))
        self.emit("translate", x, y)

    def scale(self, x, y):
        self.matrix = self.matrix.multiply(Matrix(xx=x, yy=y))
        self.emit("scale", x, y)

    def rotate(self, a):
        self.transform(Matrix(math.cos(a), math.sin(a), -math.sin(a), math.cos(a)))

    def transform(self, m):
        self.matrix = self.matrix.multiply(m)
        self.emit("transform", *m)

    def set_source_rgba(self, r, g, b, a):
        self.set_source(SolidPattern(r, g, b, a))

    def set_source_rgb(self, r, g, b):
        self.set_source_rgba(r, g, b, 1)

    def set_source(self, source):
        self.source = source
        self.emit("source", source.value())

    def set_source_surface(self, surface, x=0, y=0):
        source = SurfacePattern(surface)
        source.set_matrix(Matrix(x0=-x, y0=-y))
        self.set_source(source)

    def get_source(self):
        return self.source

    def _source(self):
        self.emit("source", self.source.value())

    def _bounds(self, x, y):
        x, y = self.matrix.point(x, y)
        if self.path_bounds is None:
            self.path_bounds = [x, y, x, y]
        else:
            b = self.path_bounds
            b[0] = min(b[0], x)
            b[1] = min(b[1], y)
            b[2] = max(b[2], x)
            b[3] = max(b[3], y)

    def move_to(self, x, y):
        self.single_rect = None
        self.point = (x, y)
        self._bounds(x, y)
        self.emit("move", x, y)

    def line_to(self, x, y):
        self.single_rect = None
        self.point = (x, y)
        self._bounds(x, y)
        self.emit("line", x, y)

    def curve_to(self, *args):
        self.single_rect = None
        for i in range(0, 6, 2):
            self._bounds(args[i], args[i + 1])
        self.point = args[4:]
        self.emit("curve", *args)

    def rectangle(self, x, y, w, h):
        self.single_rect = (x, y, w, h) if self.path_bounds is None else None
        for px, py in ((x, y), (x + w, y), (x, y + h), (x + w, y + h)):
            self._bounds(px, py)
        self.emit("rect", x, y, w, h)

    def arc(self, x, y, r, a, b):
        self.single_rect = None
        self._bounds(x - r, y - r)
        self._bounds(x + r, y + r)
        self.emit("arc", x, y, r, a, b)

    def close_path(self):
        self.emit("close")

    def new_path(self):
        self.path_bounds = None
        self.emit("begin")

    def new_sub_path(self):
        self.emit("subpath")

    def clip(self):
        if self.path_bounds:
            a = self.clip_box
            b = self.path_bounds
            self.clip_box = [
                max(a[0], b[0]),
                max(a[1], b[1]),
                min(a[2], b[2]),
                min(a[3], b[3]),
            ]
        self.emit("clip")
        self.path_bounds = None

    def clip_extents(self):
        x, y, r, b = self.clip_box
        m = self.matrix.inverted()
        points = [m.point(x, y), m.point(r, y), m.point(x, b), m.point(r, b)]
        return (
            min(p[0] for p in points),
            min(p[1] for p in points),
            max(p[0] for p in points),
            max(p[1] for p in points),
        )

    def fill(self):
        p = self.source
        if (
            self.single_rect
            and isinstance(p, SurfacePattern)
            and p.extend
            and p.matrix.v[:4] == [1, 0, 0, 1]
        ):
            self.emit("patternRect", p.value(), *self.single_rect)
        else:
            self._source()
            self.emit("fill")
        self.path_bounds = None
        self.single_rect = None

    def stroke(self):
        self._source()
        self.emit("stroke")
        self.path_bounds = None

    def stroke_preserve(self):
        self._source()
        self.emit("strokeKeep")

    def paint(self):
        self.paint_with_alpha(1)

    def paint_with_alpha(self, alpha):
        self._source()
        self.emit("paint", alpha)

    def mask_surface(self, surface, x=0, y=0):
        mask = SurfacePattern(surface)
        mask.set_matrix(Matrix(x0=-x, y0=-y))
        self.mask(mask)

    def mask(self, pattern):
        if isinstance(pattern, LinearGradient) and all(
            stop[4] <= 0 for stop in pattern.stops
        ):
            return
        self._source()
        self.emit("mask", pattern.value())

    def set_operator(self, op):
        self.emit("operator", op)

    def set_fill_rule(self, rule):
        self.emit("fillRule", rule)

    def set_antialias(self, value):
        self.emit("antialias", value)

    def set_line_width(self, value):
        self.emit("lineWidth", value)

    def set_line_cap(self, value):
        self.emit("lineCap", "square" if value == 2 else "butt")

    def set_line_join(self, value):
        self.emit("lineJoin", "miter")

    def select_font_face(self, font, slant=0, weight=0):
        self.font = font
        self.bold = weight == FONT_WEIGHT_BOLD
        self.emit("font", font, self.size, self.bold)

    def set_font_size(self, size):
        self.size = size
        self.emit("font", self.font, size, self.bold)

    def text_extents(self, text):
        from js import cairo_measure

        width = float(cairo_measure(str(text), self.size, self.bold))
        return TextExtents(0, -self.size * 0.8, width, self.size, width, 0)

    def show_text(self, text):
        self._source()
        self.emit("text", str(text), *self.point)

    def push_group(self):
        self.groups.append(
            (self.matrix, self.clip_box[:], self.font, self.size, self.bold)
        )
        self.emit("pushGroup")

    def pop_group_to_source(self):
        self.matrix, self.clip_box, self.font, self.size, self.bold = self.groups.pop()
        self.source = GroupPattern(uid())
        self.emit("popGroup", self.source.id)


class GroupPattern:
    def __init__(self, id):
        self.id = id

    def value(self):
        return ["group", self.id]

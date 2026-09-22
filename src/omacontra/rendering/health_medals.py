"""Small, cached service medals with the interlocking Omarchy insignia."""
from functools import lru_cache
import cairo


def polygon(c,points,rgb):
    c.set_source_rgb(*rgb)
    c.move_to(*points[0])
    for point in points[1:]:c.line_to(*point)
    c.close_path();c.fill()


def insignia(c,x,y,size,rgb):
    """Keep the reference's square outline and two interlocking stepped paths."""
    c.save();c.translate(x,y);c.scale(size/30,size/30)
    c.set_source_rgb(*rgb);c.set_line_width(2.2)
    c.set_line_join(cairo.LINE_JOIN_MITER);c.set_line_cap(cairo.LINE_CAP_SQUARE)
    c.rectangle(1.1,1.1,27.8,27.8);c.stroke()
    for points in (((15.5,1.1),(15.5,5.5),(4.6,5.5),(4.6,15),(1.1,15)),
                   ((4.6,15),(4.6,25),(13.8,25)),
                   ((14.5,28.9),(14.5,23.8),(24.7,23.8),(24.7,5.5),(21.5,5.5))):
        c.move_to(*points[0])
        for point in points[1:]:c.line_to(*point)
        c.stroke()
    c.restore()


@lru_cache(maxsize=2)
def medal(active=True):
    # Compact interpretation of the reference: folded striped ribbon, green
    # suspension bar and an openwork mint Omarchy emblem. Tiny text
    # is omitted so the silhouette and emblem remain readable during play.
    s=cairo.ImageSurface(cairo.FORMAT_ARGB32,40,64)
    c=cairo.Context(s);c.scale(2,2);c.set_antialias(cairo.ANTIALIAS_NONE)
    def shade(rgb):
        if active:return rgb
        value=sum(rgb)/3
        return (.12+value*.13,.14+value*.14,.14+value*.12)
    def poly(points,rgb):polygon(c,points,shade(rgb))
    ink=(.035,.06,.065);bronze=(.49,.32,.12);gold=(.78,.60,.27)
    mint=(.68,.84,.56);light=(.87,.95,.71);forest=(.055,.24,.15)
    poly(((3,0),(17,0),(17,9),(14,12),(6,12),(3,9)),ink)
    poly(((4,0),(16,0),(16,8),(13,11),(7,11),(4,8)),(.13,.39,.25))
    poly(((8,0),(12,0),(12,10),(8,10)),mint)
    for x in (4,15):poly(((x,0),(x+1,0),(x+1,8),(x,8)),mint)
    # Stepped folds and a small pin bar under the cloth.
    poly(((4,7),(8,8),(12,8),(16,7),(16,9),(12,10),(8,10),(4,9)),(.055,.20,.13))
    poly(((7,8),(12,9),(14,8),(14,9),(12,10),(7,9)),(.36,.57,.35))
    poly(((3,10),(17,10),(18,11),(17,13),(3,13),(2,11)),forest)
    poly(((3,10),(17,10),(17,11),(3,11)),light)
    poly(((5,12),(15,12),(14,15),(6,15)),mint)
    # The green openwork emblem is the pendant: no rim or solid backing.
    insignia(c,2,14.5,16,shade(ink))
    insignia(c,2,14,16,shade(mint))
    return s


def draw_health(c,hp,x=18,y=50,capacity=6,scale=1,unlimited=False,damage_age=99):
    if unlimited:
        draw_health(c,1,x,y,capacity=1,scale=scale)
        c.save();c.set_source_rgb(.68,.84,.56)
        c.set_line_width(2.3*scale)
        cx=x+41*scale;cy=y+16*scale
        c.move_to(cx,cy)
        c.curve_to(cx-25*scale,cy-22*scale,cx-25*scale,cy+22*scale,cx,cy)
        c.curve_to(cx+25*scale,cy-22*scale,cx+25*scale,cy+22*scale,cx,cy)
        c.stroke();c.restore();return
    for i in range(max(0,min(hp,capacity))):
        c.save();c.translate(x+i*25*scale,y);c.scale(.5*scale,.5*scale)
        c.set_source_surface(medal(True));c.get_source().set_filter(cairo.FILTER_NEAREST)
        c.paint();c.restore()
    # The just-lost ribbon flashes briefly, then disappears completely.
    if 0<=damage_age<.22 and hp<capacity and int(damage_age*35)%2==0:
        c.save();c.translate(x+hp*25*scale,y-damage_age*18);c.scale(.5*scale,.5*scale)
        c.set_source_surface(medal(True));c.paint_with_alpha(1-damage_age/.22);c.restore()

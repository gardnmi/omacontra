"""Crisp arcade gunfire: cached pixel silhouettes with a white-hot core."""
from functools import lru_cache
import math
import cairo

EMBER=(.83,.22,.09)
ORANGE=(1.,.55,.15)
GOLD=(1.,.86,.42)
WHITE=(1.,1.,.88)


def poly(c,points,rgb):
    c.set_source_rgb(*rgb);c.move_to(*points[0])
    for point in points[1:]:c.line_to(*point)
    c.close_path();c.fill()

@lru_cache(maxsize=4)
def flash_stamp(frame):
    s=cairo.ImageSurface(cairo.FORMAT_ARGB32,40,32);c=cairo.Context(s)
    c.set_antialias(cairo.ANTIALIAS_NONE)
    # The leftmost ignition point sits on the barrel; ragged lobes change per shot.
    tip=(36,31,38)[frame];up=(2,5,0)[frame];down=(29,31,26)[frame]
    poly(c,[(0,15),(9,11),(7,up),(17,9),(24,6),(23,13),(tip,15),
            (25,19),(29,down),(17,23),(12,31),(10,22),(1,18)],EMBER)
    poly(c,[(0,16),(11,13),(9,up+3),(18,12),(23,9),(22,15),(tip-2,16),
            (22,18),(25,down-2),(16,20),(12,27),(11,19)],ORANGE)
    poly(c,[(1,16),(13,14),(12,8),(18,14),(24,13),(22,16),(30,16),
            (20,18),(21,23),(16,19),(13,23),(13,18)],GOLD)
    poly(c,[(0,16),(13,15),(14,11),(17,15),(25,16),(18,17),
            (17,21),(14,18),(4,17)],WHITE)
    return s

@lru_cache(maxsize=1)
def bullet_stamp():
    s=cairo.ImageSurface(cairo.FORMAT_ARGB32,34,10);c=cairo.Context(s)
    c.set_antialias(cairo.ANTIALIAS_NONE)
    poly(c,[(1,4),(14,4),(18,2),(28,2),(28,3),(32,3),(34,5),
            (30,7),(24,8),(17,8),(15,6),(1,6)],EMBER)
    poly(c,[(7,4),(18,4),(19,3),(29,3),(32,4),(34,5),(28,7),
            (19,7),(18,6),(7,6)],ORANGE)
    poly(c,[(12,4),(22,4),(23,2),(29,3),(30,4),(34,5),
            (29,6),(28,7),(21,7),(20,6),(12,6)],GOLD)
    poly(c,[(10,4),(21,4),(24,3),(29,3),(30,4),(34,5),(29,6),(23,7),(19,6),(10,6)],WHITE)
    c.set_source_rgb(*GOLD);c.rectangle(4,4,2,1);c.fill()
    return s


def muzzle(c,x,y,angle,remaining,serial=0,size=34,alpha=1):
    if remaining<=0:return
    c.save();c.translate(x,y);c.rotate(angle)
    # Brief peak followed by contraction keeps the flash staccato.
    scale=size/40*(1 if remaining>.032 else .73)
    c.scale(scale,scale)
    c.set_source_surface(flash_stamp(serial%3),0,-16)
    c.get_source().set_filter(cairo.FILTER_NEAREST);c.paint_with_alpha(alpha)
    c.restore()


def bullet(c,x,y,vx,vy):
    c.save();c.translate(x,y);c.rotate(math.atan2(vy,vx))
    c.set_source_surface(bullet_stamp(),-34,-5)
    c.get_source().set_filter(cairo.FILTER_NEAREST);c.paint();c.restore()

"""A bounded, reusable molten-surface texture with slowly drifting crust."""
import math
from functools import lru_cache
import cairo

@lru_cache(maxsize=1)
def texture():
    surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,640,160)
    c=cairo.Context(surface)
    # Periodic hot channels between cooled islands; fixed pixel clusters match
    # the arena art. Reuse one tile instead of allocating surfaces every frame.
    for y in range(0,160,2):
        for x in range(0,640,2):
            a=x/640*math.tau;b=y/160*math.tau
            field=math.sin(a*5+math.sin(b*3)*1.3)+.6*math.sin(a*11-b*4)+.35*math.cos(a*17+b*7)
            noise=((x*73+y*193)%97)/97
            fissure=max(0,1-abs(field)*3.4)
            if fissure>.18:
                rgb=(.7+.3*fissure,.11+.55*fissure*fissure,.018+.10*fissure**4)
            else:
                grain=.02+noise*.045
                edge=max(0,1-abs(field))*.14
                rgb=(.11+grain+edge,.032+grain*.5+edge*.22,.025+grain*.35)
            c.set_source_rgb(*rgb);c.rectangle(x,y,2,2);c.fill()
    return surface

def draw(c,f):
    level=f.lava_surface
    if level is None:return
    c.save();c.rectangle(0,level,1280,720-level);c.clip()
    pattern=cairo.SurfacePattern(texture());pattern.set_extend(cairo.EXTEND_REPEAT)
    pattern.set_filter(cairo.FILTER_NEAREST)
    pattern.set_matrix(cairo.Matrix(xx=1.,yy=2.2,x0=-(f.clock*18)%640,y0=-level*2.2))
    c.set_source(pattern);c.paint()
    depth=cairo.LinearGradient(0,level,0,720)
    depth.add_color_stop_rgba(0,1,.18,.01,.18);depth.add_color_stop_rgba(1,.08,.025,.015,.4)
    c.set_source(depth);c.paint()
    # Hot reflected light at the meniscus, above the slower crust movement.
    glow=cairo.LinearGradient(0,level,0,level+24)
    glow.add_color_stop_rgba(0,1,.58,.08,.65);glow.add_color_stop_rgba(1,1,.18,0,0)
    c.set_source(glow);c.rectangle(0,level,1280,24);c.fill()
    c.set_source_rgba(1,.84,.30,.9);c.set_line_width(3)
    for i in range(81):
        x=i*16;y=level+3+2*math.sin(x*.024-f.clock*1.3)
        if i==0:c.move_to(x,y)
        else:c.line_to(x,y)
    c.stroke();c.restore()

"""Shared illustrated effects, anchored to the simulation's existing geometry."""
from functools import lru_cache
import math
import cairo
from omacontra.rendering import sprites

PROPS='industrial-props-v1.png'
EFFECTS='combat-effects-v1.png'
PROJECTILES='hostile-projectiles-v1.png'
STREAMS='furnace-streams-v1.png'


@lru_cache(maxsize=1)
def flame_frames():
    """Preblend a loop once; no per-flame groups or full-atlas allocations."""
    frames=[];poses=(0,1,2,1)
    for tick in range(16):
        phase=tick/4;index=int(phase);mix=phase-index
        surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,192,384)
        c=cairo.Context(surface);c.set_operator(cairo.OPERATOR_ADD)
        for pose,weight in ((poses[index],1-mix),(poses[(index+1)%4],mix)):
            sprites.draw(c,EFFECTS,(pose*512+115,12,305,493),0,0,192,384,alpha=weight)
        frames.append(surface)
    return tuple(frames)


def flame(c,x,y,width,height,t,angle=0,alpha=1):
    """Base at (x,y), pointing up by default. Dimensions bound the hot plume."""
    if min(width,height,alpha)<=0:return
    frames=flame_frames();surface=frames[int(t*24)%len(frames)]
    c.save();c.translate(x,y);c.rotate(angle)
    c.translate(-width/2,-height);c.scale(width/192,height/384)
    c.set_source_surface(surface);c.get_source().set_filter(cairo.FILTER_NEAREST)
    c.paint_with_alpha(alpha);c.restore()


@lru_cache(maxsize=2)
def stream_frames():
    frames=[];poses=(0,1,2,1)
    for tick in range(16):
        phase=tick/4;index=int(phase);mix=phase-index
        surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,384,192)
        c=cairo.Context(surface);c.set_operator(cairo.OPERATOR_ADD)
        for pose,weight in ((poses[index],1-mix),(poses[(index+1)%4],mix)):
            frame=(pose*512+12,176,490,240)
            sprites.draw(c,STREAMS,frame,0,0,384,192,alpha=weight)
        frames.append(surface)
    return tuple(frames)


def fire_stream(c,sx,sy,ex,ey,width,t,alpha=1):
    length=math.hypot(ex-sx,ey-sy)
    if length<=0 or width<=0 or alpha<=0:return
    surface=stream_frames()[int(t*24)%16]
    c.save();c.translate(sx,sy);c.rotate(math.atan2(ey-sy,ex-sx)-math.pi)
    c.translate(-length,-width/2);c.scale(length/384,width/192)
    c.set_source_surface(surface);c.get_source().set_filter(cairo.FILTER_NEAREST)
    c.paint_with_alpha(alpha);c.restore()




def smoke(c,x,y,size,t=0,alpha=.4,steam=False):
    if size<=0 or alpha<=0:return
    frame=(1034 if steam else 520,523,495,491)
    c.save();c.translate(x,y);c.rotate(math.sin(t*.8)*.15)
    sprites.draw(c,EFFECTS,frame,-size/2,-size/2,size,size,alpha=alpha)
    c.restore()


def muzzle(c,x,y,angle,t,size=28,alpha=1):
    c.save();c.translate(x,y);c.rotate(angle)
    # Actual ignition point, not the atlas edge, sits on the gun muzzle.
    length=size*(1+.13*math.sin(t*83))
    sprites.draw(c,EFFECTS,(45,641,445,258),0,-length*.29,length,length*.58,alpha=alpha)
    c.restore()


def rifle(c,x,y,angle,alpha=1):
    c.save();c.translate(x,y);c.rotate(angle)
    if math.cos(angle)<0:c.scale(1,-1)
    sprites.draw(c,PROPS,(24,690,508,205),-14,-8,49,19.8,alpha=alpha)
    c.restore()


def platform(c,left,right,top,floor):
    width=right-left
    # Keep deck thickness constant; only the grounded support span changes.
    sprites.draw(c,PROPS,(25,96,507,91),left,top,width,24)
    sprites.draw(c,PROPS,(25,187,507,343),left,top+24,width,floor-top-24)




def ramp(c,x,width=160,height=40):
    # Launch lip left, low approach right. Collision surface: (x,550)..(x+160,590).
    sprites.draw(c,PROPS,(1035,640,485,286),x,590-height,width,height)


def barricade(c,x):
    sprites.draw(c,PROPS,(549,624,455,275),x,542,55,48)


# Crop, source-space hot-core pivot, display width and height. Position follows
# the collision center; tails/glow are decoration, never new damage areas.
PROJECTILE_FRAMES={
    'pearl':((85,112,340,340),(255,282),23,23),
    'spore':((530,165,428,245),(798,286),32,18),
    'shard':((990,178,516,219),(1330,287),34,14),
    'needle':((58,636,468,178),(367,727),36,14),
    'ember':((550,574,423,310),(815,732),31,23),
    'pressure_ring':((1050,518,459,437),(1287,737),47,45),
}


@lru_cache(maxsize=6)
def projectile_stamp(kind):
    # Area-filter the detailed source once at 2x gameplay size. Direct nearest
    # sampling from a 500px sprite into 20px created crawling bright speckles.
    frame,_,w,h=PROJECTILE_FRAMES[kind]
    surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,w*2,h*2)
    c=cairo.Context(surface);c.scale(w*2/frame[2],h*2/frame[3])
    c.set_source_surface(sprites.atlas(PROJECTILES),-frame[0],-frame[1])
    c.get_source().set_filter(cairo.FILTER_BEST);c.paint()
    return surface


def projectile(c,kind,x,y,vx,vy,t=0,scale=1):
    frame,pivot,w,h=PROJECTILE_FRAMES[kind]
    w*=scale;h*=scale
    angle=math.atan2(vy,vx)
    if kind=='pressure_ring':angle=t*.6
    c.save();c.translate(x,y);c.rotate(angle)
    left=-(pivot[0]-frame[0])*w/frame[2]
    top=-(pivot[1]-frame[1])*h/frame[3]
    surface=projectile_stamp(kind)
    c.translate(left,top);c.scale(w/surface.get_width(),h/surface.get_height())
    c.set_source_surface(surface);c.get_source().set_filter(cairo.FILTER_BILINEAR);c.paint()
    c.restore()

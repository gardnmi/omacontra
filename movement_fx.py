"""Bounded ground dust, shared by DHH's on-foot encounters."""
from dataclasses import dataclass
from functools import lru_cache
import math
import cairo

@dataclass
class Puff:
    x:float
    y:float
    vx:float
    vy:float
    size:float
    age:float=0.
    life:float=.38
    floor:float=0.

def advance(f,dt):
    f.landing_age=max(0,getattr(f,'landing_age',0)-dt)
    f.brake_age=max(0,getattr(f,'brake_age',0)-dt)
    f.footprints=[p for p in getattr(f,'footprints',[]) if f.clock-p[2]<1.8]
    dust=getattr(f,'motion_dust',[])
    for p in dust:p.x+=p.vx*dt;p.y+=p.vy*dt;p.vx*=max(0,1-dt*3);p.age+=dt
    f.motion_dust=[p for p in dust if p.age<p.life]

def step(f,dt,was_running,old_x,was_grounded):
    dust=getattr(f,'motion_dust',[])
    grounded=f.y>=f.floor-.2 and getattr(f,'hit_age',None) is None
    dx=f.x-old_x
    direction=1 if dx>0 else -1 if dx<0 else getattr(f,'run_direction',f.facing)
    running=grounded and f.moving and not f.duck and not f.sliding
    previous_direction=getattr(f,'run_direction',direction)
    launch=running and (not was_running or direction!=previous_direction)
    landing=grounded and not was_grounded
    if landing:f.landing_age=.18
    if running and was_running and direction!=previous_direction:f.brake_age=.10
    f.foot_distance=getattr(f,'foot_distance',0)+abs(dx) if running else 0
    if hasattr(f,'deck_y') and f.foot_distance>=42:
        f.foot_distance=0
        f.footprints=(getattr(f,'footprints',[])+[(f.x,direction,f.clock)])[-16:]
    count=6 if launch else 4 if landing else 0
    f.motion_emit=max(0,getattr(f,'motion_emit',0)-dt)
    if grounded and f.sliding and abs(dx)>.01 and f.motion_emit<=0:
        count=3;f.motion_emit=.035
    for i in range(count):
        side=direction if not landing else (-1 if i%2 else 1)
        x=f.x-side*(11+i%3*4)
        floor=f.deck_y(x) if hasattr(f,'deck_y') else f.y
        dust.append(Puff(x,floor-2,-side*(35+i*13),-12-i%3*8,
                         10+i%3*3,life=.32+i%3*.055,floor=floor))
    f.motion_dust=dust[-42:];f.run_direction=direction;f.was_running=running

@lru_cache(maxsize=2)
def stamp(wet):
    s=cairo.ImageSurface(cairo.FORMAT_ARGB32,32,20);c=cairo.Context(s)
    palette=((.55,.65,.7),(.72,.79,.82)) if wet else ((.48,.44,.36),(.72,.67,.54))
    for layer,(rgb,a) in enumerate(((palette[0],.30),(palette[1],.48))):
        c.set_source_rgba(*rgb,a)
        for x,y,r in ((7,13,5),(12,9,6),(18,11,7),(24,13,4)):
            c.arc(x,y-layer*2,r-layer,0,math.tau);c.fill()
    return s

def draw(c,f):
    wet=hasattr(f,'deck_y')
    height=max(0,f.floor-f.y)
    if f.state!='dead':
        c.save();c.translate(f.x,f.deck_y(f.x) if wet else f.floor)
        c.scale(max(5,19-height*.03),3.2);c.set_source_rgba(.025,.04,.045,max(.04,.26-height*.001));c.arc(0,0,1,0,math.tau);c.fill();c.restore()
    for x,direction,born in getattr(f,'footprints',()):
        age=f.clock-born;y=f.deck_y(x)
        c.save();c.translate(x,y-1);c.rotate(math.atan(f.deck_slope))
        c.set_source_rgba(.025,.065,.085,.28*(1-age/1.8));c.rectangle(-5,-2,10,3);c.fill()
        if age<.5:
            c.scale(1,.22);c.set_source_rgba(.65,.79,.82,.2*(1-age/.5));c.set_line_width(1)
            c.arc(0,0,3+age*24,0,math.tau);c.stroke()
        c.restore()
    for p in getattr(f,'motion_dust',()):
        u=p.age/p.life;size=p.size*(.65+u*.8)
        y=p.y+(f.deck_y(p.x)-p.floor if wet else 0)
        c.save();c.translate(p.x-size/2,y-size*.55);c.scale(size/32,size/32)
        c.set_source_surface(stamp(wet));c.paint_with_alpha((1-u)**1.5);c.restore()
    if getattr(f,'sound_bank','')=='foundry' and getattr(f,'landing_age',0)>0:
        u=1-f.landing_age/.18
        for side in (-1,1):
            c.save();c.translate(f.x+side*(15+u*22)-22,f.y-9);c.scale(1.4,.45)
            c.set_source_surface(stamp(True));c.paint_with_alpha((1-u)*.55);c.restore()

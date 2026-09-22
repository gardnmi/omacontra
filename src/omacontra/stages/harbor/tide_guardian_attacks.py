"""Energy handoff, powered deck blast and staggered stars with fixed lanes."""
import math
import cairo
from functools import lru_cache
from omacontra.rendering import sprites
from omacontra.stages.reaper.combat import segment_box
from omacontra.stages.reaper.battle_art import glow, color
from omacontra.rendering import combat_fx as fx


def start(f,a,kind,linked=False):
    if kind=='stars':f.sound('stars')
    a.linked=linked
    a.warning=kind;a.timer=1.4;a.age=0.;a.target=f.player_center
    a.star_lanes=(350.,500.,650.,800.,950.) if linked or a.enraged else (410.,640.,870.)
    if a.enraged and a.round%2:a.star_lanes=tuple(x-60 for x in a.star_lanes)


def step(f,a,dt):
    old=a.age;a.age+=dt
    if a.attack=='relay':
        x0,y0=relay_position(f,a,old);x,y=relay_position(f,a,a.age)
        l,t,r,b=f.player_hitbox
        if not a.hit and segment_box(x0,y0,x,y,(l-20,t-16,r+20,b+16)):
            hp=f.hp;f.hurt();a.hit=f.hp<hp
        if (a.linked or a.enraged) and old<1.8<=a.age:f.sound('relay')
        if (a.linked or a.enraged) and a.age>=1.8:
            x0=900-max(0,old-1.8)*420;x=900-(a.age-1.8)*420
            if not a.high_hit and segment_box(x0,f.floor-80,x,f.floor-80,(l-22,t-10,r+22,b+10)):
                hp=f.hp;f.hurt();a.high_hit=f.hp<hp
    else:
        for i,x in enumerate(a.star_lanes):
            delay=.65+i*.48
            before=old-delay;now=a.age-delay
            if before<0<=now:f.sound('star_fall',.15)
            if 180+max(0,before)*440<f.floor-12<=180+max(0,now)*440:f.sound('star_impact',.15)
            if now<0 or i in a.star_hits:continue
            y0=180+max(0,before)*440;y=180+now*440
            l,t,r,b=f.player_hitbox
            if segment_box(x,y0,x,y,(l-12,t-16,r+12,b+16)):
                hp=f.hp;f.hurt()
                if f.hp<hp:a.star_hits.add(i)
            if y>f.floor+25:a.star_hits.add(i)
    if a.age>=(4.4 if a.linked or a.enraged else 3.):
        a.attack=None;a.exposed=1.7 if a.enraged else 3.6 if a.linked else 2.4;a.timer=0 if a.enraged else .6


def draw(c,f,a):
    kind=a.warning or a.attack
    if kind not in ('relay','stars'):return
    if kind=='relay':
        if a.warning:
            sx,sy=a.muzzle(f.floor)
            u=max(0,min(1,1-a.timer/1.4))
            if a.linked:
                partner=next(g for g in f.guardians if g.kind==2)
                ox,oy=partner.muzzle(f.floor)
                travel=min(1,u/.7)
                x=ox+(sx-ox)*travel;y=oy+(sy-oy)*travel-140*math.sin(travel*math.pi)
                angle=math.atan2(sy-oy-140*math.pi*math.cos(travel*math.pi),sx-ox)
                bolt(c,x,y,angle,70)
            glow(c,sx,sy,20+u*35,'cream',u*.5)
        elif a.age<2.6:
            x,y=relay_position(f,a,a.age)
            px,py=relay_position(f,a,max(0,a.age-.02))
            bolt(c,x,y,math.atan2(y-py,x-px),135)
            glow(c,x,y,36,'cream',.24)
        if (a.linked or a.enraged) and a.attack:
            if 1.2<a.age<1.8:
                glow(c,900,f.floor-80,40,'cream',(a.age-1.2)*.8)
            elif 1.8<=a.age<3.5:
                bolt(c,900-(a.age-1.8)*420,f.floor-80,math.pi,150)

    else:
        for i,x in enumerate(a.star_lanes):
            age=-1 if a.warning else a.age-.65-i*.48
            y=180+max(0,age)*440
            if y>=f.floor-12:
                impact=(y-(f.floor-12))/440
                meteor_impact(c,x,f.floor,impact,f.clock+i)
                continue
            if age<=0:
                # Stars unfurl out of the astronaut's hand, then hold their lanes.
                u=min(1,max(0,1-a.timer/1.4)) if a.warning else 1
                sx,sy=a.muzzle(f.floor);x=sx+(x-sx)*u;y=sy+(180-sy)*u
                glow(c,x,y,22,'cream',.35)
            meteor(c,x,y,f.clock+i,falling=age>0)


def relay_position(f,a,age):
    sx,sy=a.muzzle(f.floor)
    if age<.4:
        u=age/.4
        return sx-100*u,sy+(f.floor-24-sy)*u
    return sx-100-(age-.4)*335,f.floor-24


def bolt(c,x,y,angle,size):
    c.save();c.translate(x,y);c.rotate(angle-math.pi)
    sprites.draw(c,'guardian-relay-plasma.png',(20,120,1940,575),-size*.3,-size*.15,size,size*.30)
    c.restore()


@lru_cache(maxsize=1)
def meteor_stamp():
    surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,80,190)
    sprites.draw(cairo.Context(surface),'guardian-meteor.png',(170,0,670,1500),0,0,80,190)
    return surface


def meteor(c,x,y,t,falling=True):
    stamp=meteor_stamp()
    c.save();c.translate(x,y)
    if not falling:
        # Condensed, pulsing stone gathers before its flame tail ignites.
        pulse=1+.04*math.sin(t*4)
        c.scale(pulse,pulse)
        mask=cairo.RadialGradient(0,2,25,0,2,42)
        mask.add_color_stop_rgba(0,0,0,0,1);mask.add_color_stop_rgba(1,0,0,0,0)
        c.set_source_surface(stamp,-40,-158);c.mask(mask)
    else:
        # Keep the heavy core centered on the hitbox; only its wake flutters.
        for row in range(0,190,10):
            offset=math.sin(t*17+row*.085)*4*max(0,1-row/145)
            c.save();c.rectangle(-46,row-158,92,10);c.clip()
            c.set_source_surface(stamp,-40+offset,-158);c.paint();c.restore()
        for i in range(7):
            u=(t*1.8+i/7)%1
            glow(c,math.sin(i*13)*26,-30-u*100,3+(1-u)*3,'cream',(1-u)*.35)
    c.restore()


def meteor_impact(c,x,y,age,t):
    if not 0<=age<.5:return
    fade=1-age/.5
    # A bright deck contact, radial stone fragments and a short steam plume.
    glow(c,x,y-8,65*(.5+age),'cream',fade*.65)
    fx.smoke(c,x,y-25-age*75,60+age*110,t,alpha=fade*.65,steam=True)
    for i in range(9):
        angle=math.pi+(i+.5)*math.pi/9
        dist=age*(110+i%3*45)
        px=x+math.cos(angle)*dist;py=y+math.sin(angle)*dist+100*age*age
        c.save();c.translate(px,py);c.rotate(age*(i-4)*5)
        sprites.draw(c,'guardian-meteor.png',(350,1050,260,300),-5,-6,10,12,alpha=fade)
        c.restore()

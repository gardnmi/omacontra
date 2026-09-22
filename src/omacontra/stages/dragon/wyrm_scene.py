"""Cached mist terrace, cloud lightning, and reference-aligned dragon portrait."""
import math
import random
from functools import lru_cache
import cairo
from omacontra.rendering import sprites
from omacontra.rendering import combat_fx as fx

HEAD='wyrm-head.png'
MOUTH=(627.,915.)
EYES=((497.,605.),(778.,605.))

def pose(f):
    recoil,crouch=f.upper_offset
    return f.boss_x-280+recoil+22*math.sin(f.clock*.72),-30+crouch+7*math.sin(f.clock*1.13),560.,560.-crouch

def raw_point(f,x,y):
    left,top,w,h=pose(f)
    return left+x*w/1254,top+y*h/1254

def head_angle(f):return .045*math.sin(f.clock*.83)

def point(f,x,y):
    px,py=raw_point(f,627,1170);xx,yy=raw_point(f,x,y)
    a=head_angle(f);dx=xx-px;dy=yy-py
    return px+dx*math.cos(a)-dy*math.sin(a),py+dx*math.sin(a)+dy*math.cos(a)

@lru_cache(maxsize=1)
def fog_stamp():
    s=cairo.ImageSurface(cairo.FORMAT_ARGB32,256,128);c=cairo.Context(s)
    for x,y,size in ((65,73,125),(121,69,135),(186,77,115)):
        fx.smoke(c,x,y,size,0,.8,steam=True)
    c.set_operator(cairo.OPERATOR_IN);c.set_source_rgba(.87,.86,.80,1);c.paint()
    return s

@lru_cache(maxsize=1)
def halo_stamp():
    s=cairo.ImageSurface(cairo.FORMAT_ARGB32,96,96);c=cairo.Context(s)
    g=cairo.RadialGradient(48,48,1,48,48,48)
    for pos,a in ((0,.9),(.16,.75),(.45,.2),(1,0)):g.add_color_stop_rgba(pos,.94,.97,1,a)
    c.set_source(g);c.paint();return s

def halo(c,x,y,r,alpha=1):
    c.save();c.translate(x-r,y-r);c.scale(r/48,r/48)
    c.set_source_surface(halo_stamp());c.paint_with_alpha(alpha);c.restore()

@lru_cache(maxsize=1)
def throat_core_stamp():
    """Front-facing version of the same ornate jaw weapon DHH can collect."""
    s=cairo.ImageSurface(cairo.FORMAT_ARGB32,80,90);c=cairo.Context(s)
    # The authored white emitter (346,480) sits exactly at (40,40).
    sprites.draw(c,'foundry-throat-weapon.png',(40,145,615,730),
                 9.4,6.5,61.5,73)
    return s

def throat_core(c,f):
    if f.mount_hp<=0:return
    x,y=f.mount_target
    pulse=.5+.5*math.sin(f.clock*4)
    halo(c,x,y,43+pulse*5,.55)
    c.save();c.set_source_surface(throat_core_stamp(),x-40,y-40);c.paint();c.restore()
    # A restrained pulse marks the target; the opaque pearl hides the beam cap.
    halo(c,x,y,12+pulse*3,.65)
    if f.mount_flash:halo(c,x,y,39,min(1,f.mount_flash/.12))

@lru_cache(maxsize=20)
def scaled_fog(w,h):
    s=cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h);c=cairo.Context(s)
    c.scale(w/256,h/128);c.set_source_surface(fog_stamp());c.paint();return s

def fog(c,x,y,w,h,alpha):
    c.save();c.set_source_surface(scaled_fog(round(w),round(h)),round(x),round(y))
    c.paint_with_alpha(alpha);c.restore()

def platform(c,left,right,top,depth=38):
    # Crop to the actual stone top, then align it to the collision plane.
    sprites.draw(c,'wyrm-stone-platform.png',(38,399,1460,360),left,top,right-left,depth)

def ground(c,top=630):
    for i in range(4):platform(c,i*320,(i+1)*320,top,92)

@lru_cache(maxsize=8)
def lightning_paths(seed):
    rng=random.Random(seed+741)
    def fracture(a,b,width,depth):
        if depth==0:return [a,b]
        midpoint=((a[0]+b[0])/2+rng.uniform(-width,width),(a[1]+b[1])/2+rng.uniform(-width*.2,width*.2))
        return fracture(a,midpoint,width*.48,depth-1)[:-1]+fracture(midpoint,b,width*.48,depth-1)
    x=rng.choice((130,270,940,1120))
    main=fracture((x,40),(x+rng.uniform(-140,140),380),65,6)
    paths=[main]
    for index in (13,23,34,47):
        a=main[index];direction=-1 if index%2 else 1
        b=(a[0]+direction*rng.uniform(45,105),a[1]+rng.uniform(50,110))
        paths.append(fracture(a,b,22,4))
    return paths

def lightning(c,t):
    age=t%8.7
    if not (3.35<age<3.68 or 3.78<age<3.91):return
    alpha=.8*max(0,math.sin((age-3.35)*math.pi/.33)) if age<3.68 else .45
    paths=lightning_paths(int(t/8.7)%8)
    for path in paths:
        for width,a in ((14,alpha*.07),(5,alpha*.3),(1.5,alpha)):
            c.set_source_rgba(.80,.89,1,a);c.set_line_width(width);c.move_to(*path[0])
            for p in path[1:]:c.line_to(*p)
            c.stroke()
    x,y=paths[0][4];halo(c,x,y,145,alpha*.24)

class MistTerrace:
    def __init__(self):
        self.background=cairo.ImageSurface(cairo.FORMAT_RGB24,1280,800)
        sprites.draw(cairo.Context(self.background),'wyrm-mist-arena.png',(0,0,1536,1024),0,0,1280,800)
        # The portrait is sampled once, preserving the original transparent edge.
        self.head=cairo.ImageSurface(cairo.FORMAT_ARGB32,640,640)
        hc=cairo.Context(self.head)
        sprites.draw(hc,HEAD,(0,0,1254,1254),0,0,640,640)
        # The neck disappears INTO mist, eliminating a rectangular cut edge.
        fade=cairo.LinearGradient(0,470,0,640)
        fade.add_color_stop_rgba(0,1,1,1,1);fade.add_color_stop_rgba(1,1,1,1,0)
        hc.set_operator(cairo.OPERATOR_DEST_IN);hc.set_source(fade);hc.paint()
        fog_stamp();halo_stamp()

    def sky(self,c,t,ship=True):
        c.set_source_surface(self.background);c.paint();lightning(c,t)
        if ship:
            sprites.draw(c,'finale-atlas.png',(70,510,375,510),1050,250,135,184,alpha=.84)
            platform(c,1030,1210,433,30)
        # Thin mist climbs the distant cliff faces in slow gusts; these
        # cached stamps stay behind the platforms and dragon silhouette.
        for i in range(4):
            age=(t*.065+i*.25)%1
            x=(65 if i%2==0 else 1150)+math.sin(t*.23+i)*15
            fog(c,x-70,470-age*310,140,100,math.sin(age*math.pi)*.19)
        for i in range(5):
            x=(i*360+t*(12+i%2*8))%1800-300
            fog(c,x,340+(i%3)*42,490,145,.23)

    def dragon(self,c,f,dx=0,dy=0,alpha=1,scale=1,glow_strength=1):
        x,y,w,h=pose(f)
        # A wake of existing mist follows the swaying head, behind its silhouette.
        for side in (-1,1):
            fog(c,x+w*.5+side*(w*.28+math.sin(f.clock*.83)*12)-120,
                y+h*.68,240,80,.18*alpha)
        # Approach is depth scaling around the mouth, never a fall from above.
        mx,my=point(f,*MOUTH)
        c.save();c.translate(mx+dx,my+dy);c.scale(scale,scale);c.translate(-mx,-my)
        px,py=raw_point(f,627,1170)
        c.save();c.translate(px,py);c.rotate(head_angle(f));c.translate(-px,-py)
        c.translate(x,y);c.scale(w/640,h/640)
        c.set_source_surface(self.head);c.paint_with_alpha(alpha);c.restore()
        charge=0 if not f.forge_warning else max(0,1-f.forge_timer/1.15)
        pulse=.9+.1*math.sin(f.clock*2)
        for eye in EYES:
            ex,ey=point(f,*eye)
            if alpha<.35:
                c.set_source_rgba(.025,.03,.035,(1-alpha/.35)*glow_strength*.7)
                c.arc(ex,ey,11,0,math.tau);c.fill()
            halo(c,ex,ey,27+charge*12,glow_strength*pulse)
            halo(c,ex,ey,9,glow_strength)
        halo(c,mx,my-14,48+charge*28,glow_strength*(.72+charge*.3))
        halo(c,mx,my-20,16+charge*8,glow_strength*.95)
        if f.mount_flash:halo(c,mx,my,45,.9)
        c.restore()

    def foreground(self,c,t,density=1):
        # Low fog hides the dragon neck, while traversal edges stay readable.
        for i in range(5):
            x=(i*350-t*(18+i%2*9))%1750-300
            fog(c,x,485+(i%2)*35,470,135,.45*density)

    def veil(self,c,t,opacity):
        # Clouds cross the distant face during the intro, then split sideways.
        for side in (-1,1):
            for i in range(3):
                x=640+side*(60+(1-opacity)*360)-240+math.sin(t*.4+i)*35
                fog(c,x,170+i*105,480,245,opacity*.8)

    def storm(self,c,f):
        level=f.lava_surface
        if level is None or level>750:return
        c.save();c.rectangle(0,level,1280,800-level);c.clip()
        g=cairo.LinearGradient(0,level,0,720)
        g.add_color_stop_rgba(0,.14,.18,.21,.85);g.add_color_stop_rgba(1,.025,.04,.055,1)
        c.set_source(g);c.paint()
        for i in range(7):
            x=(i*245+f.clock*35)%1715-250
            fog(c,x,level-28+(i%2)*24,340,125,.32)
        c.restore()
        # A crisp storm front marks the exact damaging surface.
        c.set_source_rgba(.66,.8,.89,.8);c.set_line_width(2)
        for i in range(81):
            x=i*16;y=level+2+math.sin(i*.85+f.clock*3)*2
            if i==0:c.move_to(x,y)
            else:c.line_to(x,y)
        c.stroke()




@lru_cache(maxsize=3)
def ordnance_stamp(kind):
    frame,size={'orb':((25,390,440,340),(56,43)),
                'heavy':((1040,315,496,470),(66,63)),
                'spire':((480,5,555,995),(90,165))}[kind]
    s=cairo.ImageSurface(cairo.FORMAT_ARGB32,*size)
    sprites.draw(cairo.Context(s),'wyrm-storm-ordnance.png',frame,0,0,*size)
    return s

def storm_projectile(c,x,y,angle,age,heavy=False):
    stamp=ordnance_stamp('heavy' if heavy else 'orb')
    c.save();c.translate(x,y);c.rotate(angle)
    # Align the actual armored ball (not the trailing shards) with its hitbox.
    c.set_source_surface(stamp,-44 if heavy else -38,-31 if heavy else -21)
    c.get_source().set_filter(cairo.FILTER_NEAREST);c.paint();c.restore()
    halo(c,x,y,9 if heavy else 6,.35+.15*math.sin(age*16))

def stone_eruption(c,x,y,width,age):
    grow=min(1,age/.25);fade=min(1,max(0,(1.05-age)/.2))
    if grow<=0 or fade<=0:return
    stamp=ordnance_stamp('spire')
    offsets=(-.67,0,.67) if width>30 else (0,)
    for offset in offsets:
        c.save()
        # Reveal from beneath the collision plane, rather than stretch a beam.
        c.rectangle(x-width-10,y-166,width*2+20,166);c.clip()
        c.set_source_surface(stamp,x+offset*width-45,y-165*grow)
        c.paint_with_alpha(fade);c.restore()

def storm_lance(c,sx,sy,ex,ey,t,alpha=1):
    """Narrow forked lightning with a dark silhouette against the pale mist."""
    dx,dy=ex-sx,ey-sy;length=max(1,math.hypot(dx,dy))
    paths=[]
    for branch in range(3):
        path=[]
        for i in range(49):
            u=i/48
            bend=math.sin(u*math.pi)*(math.sin(i*2.3+t*31+branch)*4+branch*5)
            path.append((sx+dx*u-dy/length*bend,sy+dy*u+dx/length*bend))
        paths.append(path)
    for index,path in enumerate(paths):
        for width,rgba in ((13,(.04,.09,.13,.45)),(5,(.25,.56,.7,.6)),(1.7,(.9,.98,1,.95))):
            c.set_line_width(width if index==0 else width*.4)
            c.set_source_rgba(*rgba[:3],rgba[3]*alpha*(1 if index==0 else .5))
            c.move_to(*path[0])
            for p in path[1:]:c.line_to(*p)
            c.stroke()
    halo(c,sx,sy,26,alpha*.8)

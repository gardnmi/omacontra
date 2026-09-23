"""Articulated trailer conversion and shuttered mechanical heart."""
import math
import cairo
from omacontra.rendering import sprites
from omacontra.rendering import combat_fx as fx
from omacontra.stages.reaper.battle_art import glow, line, color
from omacontra.stages.highway.chase_robot import robot_pose, heart_target, heart_open, smooth, ROBOT_SCALE, body_motion, cannon_charge, RAMP_WIDTH, RAMP_HEIGHT

SHEET='highway-heart-robot-v1.png'
SCALE=.48

def warm_shells():
    # Reuse the illustrated molten armor dart and flame loop, already cached.
    fx.projectile_stamp('needle');fx.stream_frames()

def shell(c,b,t):
    angle=math.atan2(b.vy,b.vx);dx,dy=math.cos(angle),math.sin(angle)
    # Long turbulent exhaust trails a substantial pointed armor core.
    # Exhaust is visual; the damaging core is centered on the projectile.
    tail=125+12*math.sin(t*19+b.vx*.01)
    fx.fire_stream(c,b.x-dx*tail,b.y-dy*tail,b.x-dx*12,b.y-dy*12,34,t)
    fx.projectile(c,'needle',b.x,b.y,b.vx,b.vy,t,scale=3.1)


def robot(c,f,alpha=1,deploy=1):
    x,y,bob=robot_pose(f);left=x-123;top=y-466
    c.save();c.translate(x,y);scale=ROBOT_SCALE;c.scale(scale,scale*(.78+.22*deploy));c.translate(-x,-y)
    lean,stretch=body_motion(f)
    c.translate(x,y);c.transform(cairo.Matrix(1,0,lean,stretch,0,0));c.translate(-x,-y)
    if deploy<.25:
        # Use the illustrated folded chassis while the trailer armor releases.
        sprites.draw(c,SHEET,(985,220,545,765),left-8,top+99,261.6,367.2,alpha=alpha)
        c.restore();return
    # Draw one connected silhouette, with both feet anchored to the road.
    sprites.draw(c,SHEET,(0,0,496,1024),left,top,238.08,491.52,alpha=alpha)
    # The chassis wheels are fixed armor in robot form. Keep their painted
    # perspective intact under the body transform; spinning flat cutouts here
    # bends the oblique rims and drags tire/armor pixels across their sockets.
    # Short pressure releases from the shoulder vents accompany the brace.
    vent=(f.robot_age+1.2)%3.75
    if 0<vent<.8:
        for side in (-1,1):
            fx.smoke(c,x+side*77,top+93-vent*36,15+vent*35,f.clock+side,
                     alpha=alpha*(1-vent/.8)*.4,steam=True)
    opening=heart_open(f)
    # Two textured armor shutters slide away from the illustrated heart.
    for side in (-1,1):
        c.save();c.translate(left+side*opening*34,top)
        points=((133,213),(207,237),(207,355),(165,349),(123,293)) if side<0 else ((207,237),(280,211),(312,278),(258,355),(207,355))
        for i,(px,py) in enumerate(points):
            if i==0:c.move_to(px*SCALE,py*SCALE)
            else:c.line_to(px*SCALE,py*SCALE)
        c.close_path();c.clip()
        sprites.draw(c,SHEET,(480,0,512,1024),0,0,238.08,491.52,alpha=alpha)
        c.restore()
    hx,hy=x-22,y-330
    if opening>.15:
        glow(c,hx,hy,30+4*math.sin(f.clock*5),'gold',opening*.4*alpha)
        if f.impact:glow(c,hx,hy,31,'cream',alpha)
    if any(0<=f.robot_age%7.5-beat<.18 for beat in (1.,3.3)):fx.muzzle(c,x-91,y-205,2.25,f.clock,68,alpha)
    if 5.5<=f.robot_age%7.5<5.68:fx.muzzle(c,x-95,y-12,math.pi,f.clock,24,alpha)
    charge=smooth((f.robot_age%7.5-4.7)/.8) if f.robot_age%7.5<5.5 else 0
    glow(c,x-95,y-12,20,'gold',charge*.6*alpha)
    glow(c,x-91,y-205,38,'gold',cannon_charge(f)*.8*alpha)
    if cannon_charge(f)>.15:
        glow(c,x-91,y-205,12,'cream',cannon_charge(f)*alpha)
    c.restore()


def blast(c,x,y,age,size):
    if not 0<=age<.6:return
    frame=min(5,int(age/.1))
    sprites.draw(c,'quattro-explosion.png',((frame%3)*512,(frame//3)*512,512,512),
                 x-size/2,y-size/2,size,size,alpha=min(1,(.6-age)*7))


def transform(c,f):
    t=f.transform_age
    cab=f.boss_x-510*smooth(t/1.5)
    # The nose dives as the engine ruptures. The surviving trailer drops back.
    if t<.95:
        c.save();c.translate(cab+135,565);c.rotate(-.11*smooth(t/.85))
        sprites.draw(c,'quattro-enemies.png',(10,45,800,650),-135,-200,272,221,
                     alpha=1-smooth((t-.65)/.3));c.restore()
    for delay,dx,dy,size in ((.04,190,450,150),(.17,75,505,205),(.32,145,455,250),(.49,220,520,180)):
        origin=f.boss_x-510*smooth(delay/1.5)
        blast(c,origin+dx,dy,t-delay,size)
    # Large, textured engine fragments arc away; wheels tumble separately.
    for i in range(10):
        age=t-(.16+i*.023)
        if not 0<age<1.45:continue
        origin=f.boss_x-510*smooth((.16+i*.023)/1.5)
        dx=(i%5-2)*105-110
        px=origin+130+dx*age;py=min(595,485-(180+i%3*55)*age+340*age*age)
        c.save();c.translate(px,py);c.rotate(age*(i%4-1.5)*4)
        frame=(30+(i%4)*145,90+(i%3)*125,105,95)
        sprites.draw(c,'quattro-enemies.png',frame,-18,-15,36,30,alpha=min(1,(1.45-age)*3));c.restore()
    for i in range(2):
        age=t-.3-i*.08
        if 0<age<1.5:
            c.save();c.translate(f.boss_x+40-i*80-age*(230+i*85),min(580,545-220*age+290*age*age));c.rotate(age*(8+i*3))
            sprites.draw(c,'quattro-enemies.png',(190,435,185,205),-26,-27,52,54,alpha=min(1,(1.5-age)*3));c.restore()
    if .32<t<1.7:
        for i in range(3):
            age=t-.32
            fx.smoke(c,f.boss_x-120-i*95-age*110,495-age*75,65+age*65,t+i,
                     alpha=min(.5,(1.7-t)*.45))

    x=f.trailer_x if f.trailer_x is not None else f.trailer_origin+95
    u=smooth((t-.65)/1.95)
    cx=x+120+(975-(x+120))*smooth((t-.45)/1.9)
    if t>.65:
        from copy import copy
        pose=copy(f);pose.boss_x=cx-125;pose.robot_age=0
        # The chassis extends from a compressed stance instead of uniformly
        # growing a miniature robot. Steam masks the initial armor release.
        robot(c,pose,alpha=smooth((t-.65)/.24),deploy=u)
    if t<2.15:
        unfold=smooth((t-.45)/1.3)
        for side in (-1,1):
            c.save();c.translate(x+120+side*unfold*125,545-unfold*95)
            c.rotate(side*unfold*1.8)
            frame=(810 if side<0 else 1165,45,355,650)
            sprites.draw(c,'quattro-enemies.png',frame,-120 if side<0 else 0,-180,120,221,
                         alpha=1-smooth((t-1.7)/.45));c.restore()
    if 1.15<t<1.6:
        # Brief actuator exhaust covers the folded-to-extended pose change.
        for dx in (-100,0,100):
            fx.smoke(c,cx+dx,400,210,t+dx,alpha=.55*math.sin((t-1.15)/.45*math.pi),steam=True)
    for side in (-1,1):
        if .55<t<1.65:
            age=t-.55
            fx.smoke(c,cx+side*(55+age*95),490-age*100,65+age*125,t+side,
                     alpha=.6*(1-age/1.1),steam=True)
        # A short grounded pressure plume sells the final locking impact.
        if 2.5<t<3.15:
            age=t-2.5
            fx.smoke(c,975+side*(100+age*160),577,40+age*100,t,
                     alpha=.5*(1-age/.65))
    for i in range(26):
        age=t-.45-i*.012
        if 0<age<.85:
            vx=math.sin(i*8)*210;vy=-100-(i%5)*38
            px=cx+vx*age;py=505+vy*age+240*age*age
            line(c,[(px,py),(px-vx*.045,py-vy*.045)],'gold',2,(1-age/.85))


def destruction(c,f):
    t=f.death_age;x,y,bob=robot_pose(f)
    if t<.3:robot(c,f,max(0,1-t/.3))
    for i in range(18):
        age=max(0,t-i*.018)
        px=x+math.sin(i*2.4)*age*230;py=heart_target(f)[1]-(120+i%4*60)*age+180*age*age
        c.save();c.translate(px,min(590,py));c.rotate(age*(i%5-2)*3)
        sprites.draw(c,SHEET,(60+i%4*90,150+i%6*100,90,100),-18,-20,36,40,alpha=max(0,1-t/1.7));c.restore()
    for delay,dx,dy,size in ((0,-20,-330,300),(.1,-70,-220,230),(.2,70,-150,260)):
        age=t-delay
        if 0<=age<1.2:
            frame=min(5,int(age/.14))
            sprites.draw(c,'quattro-explosion.png',((frame%3)*512,(frame//3)*512,512,512),x+dx-size/2,y+dy*ROBOT_SCALE-size/2,size,size,alpha=min(1,(1.2-age)*3))

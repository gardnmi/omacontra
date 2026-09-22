"""World changes and sprite-based guardian animation for Tidebreaker."""
import math
from omacontra.stages.harbor import tide_guardian_attacks as special
from omacontra.rendering import sprites
from omacontra.rendering import combat_fx as fx
from omacontra.stages.reaper.battle_art import label, glow, color
from omacontra.stages.harbor.tide_guardians import REVEAL_DURATION, SWITCH_AT

FRAMES=(
    (((42,20,410,481),225),((526,55,495,440),269),((1030,125,500,367),250)),
    (((30,513,410,496),217),((518,510,455,456),245),((1024,573,490,429),256)),
)

def world(c,stage,alpha=1):
    if stage==0:
        sprites.draw(c,'tidebreaker-arena.png',(0,0,1536,810),0,0,1280,630,alpha=alpha)
    else:
        sprites.draw(c,'tidebreaker-worlds.png',(0,0 if stage==1 else 632,1247,629),0,0,1280,630,alpha=alpha)

def guardian(c,f,alpha=1,entrance=0):
    if not f.stage:return
    art='tidebreaker-guardians-enraged.png' if f.actor.enraged and f.actor.rage_age>.9 else 'tidebreaker-guardians.png'
    frame,anchor=FRAMES[f.stage-1][f.guardian_pose]
    scale=.60 if f.stage==1 else .62
    x=f.guardian_x-(frame[2]-anchor if f.stage==2 else anchor)*scale+entrance;y=f.guardian_bottom-frame[3]*scale
    w,h=frame[2]*scale,frame[3]*scale
    breaking=f.state=='dying' or (f.state=='reveal' and not f.stage_switched)
    if breaking:
        age=f.death_age if f.state=='dying' else f.transition_age
        for i in range(12):
            piece=(frame[0],frame[1]+i*frame[3]/12,frame[2],frame[3]/12)
            dx=math.sin(i*8)*age*55;dy=age*age*90-i*age*5
            sprites.draw(c,art,piece,x+dx,y+i*h/12+dy,w,h/12,flip=f.stage==2,alpha=max(0,1-age/2))
        for i in range(35):
            xx=f.guardian_x+math.sin(i*13)*(age*90+20)
            yy=f.guardian_bottom-170+math.cos(i*9)*age*100+age*age*50
            glow(c,xx,yy,8+age*18,'gold' if f.stage==2 else 'red',max(0,1-age/1.8)*.6)
        return
    if f.guardian_attack=='charge':
        for i in range(3,0,-1):
            sprites.draw(c,art,frame,x+i*26,y,w,h,flip=f.stage==2,alpha=.08*(4-i))
    if f.stage==2 and f.guardian_pose!=2:
        # Nozzle coordinates in each source frame, transformed with the sprite.
        tx,ty=((397,670),(870,739))[f.guardian_pose]
        nx=x+w-(tx-frame[0])*scale;ny=y+(ty-frame[1])*scale
        fx.flame(c,nx,ny,16,48 if not f.actor.enraged else 70,f.clock,angle=math.pi,alpha=.9)
    sprites.draw(c,art,frame,x,y,w,h,flip=f.stage==2,alpha=alpha)
    special.draw(c,f.fight,f.actor)
    if f.guardian_flash:
        glow(c,f.guardian_x,f.guardian_bottom-160,38,'cream',.55)
    if f.guardian_muzzle_flash:
        sx,sy=f.gun_tip;glow(c,sx,sy,40,'gold',.65)
        fx.muzzle(c,sx,sy,math.pi if f.stage==1 else 0,f.clock,size=30)


def guardian_tells(c,f):
    # Actor pose and weapon charge communicate the attack without HUD marks.
    if not f.guardian_warning or f.guardian_warning in ('relay','stars'):return
    x,y=f.gun_tip
    glow(c,x,y,28,'gold',.2+.15*math.sin(f.clock*7)**2)


def reveal_overlay(c,f):
    t=f.transition_age
    # Same black letterbox language as the Quattro, while preserving scene geometry.
    amount=min(1,t/.35,(REVEAL_DURATION-t)/.45);amount=max(0,amount)
    c.set_source_rgba(0,0,0,amount)
    c.rectangle(0,0,1280,150);c.rectangle(0,510,1280,210);c.fill()
    if .45<t<4.55:
        title='THE SEA WAS ONLY A WALL' if f.transition_from==0 else 'THE DOCKYARD IS CHANGING'
        label(c,100,122,title,16,'gold')
        next_name='DEAD ORBIT  /  BLACK COAT'
        if t>SWITCH_AT:
            label(c,100,564,next_name,29)
            text='TOBI / RADIO: TWO OF THEM. WATCH BOTH SIDES.'
            label(c,100,606,text[:int((t-SWITCH_AT)*35)],15)


def rage_cinema(c,f):
    actor=next((a for a in f.guardian_views if a.actor.hp>0 and a.actor.enraged and a.actor.rage_age<2.8),None)
    if actor is None:return False
    t=actor.actor.rage_age
    c.set_source_rgb(.012,.016,.025);c.paint()
    world(c,1 if actor.stage==1 else 2,alpha=.3)
    # Move the same live sprite into a face close-up, then return to its place.
    ramp=min(1,t/.5,max(0,(2.8-t)/.55));ramp=ramp*ramp*(3-2*ramp)
    zoom=1+2.1*ramp
    face_x=actor.guardian_x;face_y=actor.guardian_bottom-(253 if actor.stage==2 else 258)
    c.save();c.translate(640*ramp+face_x*(1-ramp),230*ramp+face_y*(1-ramp))
    c.scale(zoom,zoom);c.translate(-face_x,-face_y)
    guardian(c,actor)
    if .8<t<1.55:
        glow(c,face_x,face_y,45,'red',math.sin((t-.8)/.75*math.pi)*.6)
        fx.smoke(c,face_x,face_y+90,100,t,alpha=.3,steam=True)
    c.restore()
    c.set_source_rgba(0,0,0,.95);c.rectangle(0,0,1280,65);c.rectangle(0,655,1280,65);c.fill()
    if .9<t<1.06:
        c.set_source_rgba(1,.55,.25,(1.06-t)*2);c.paint()
    return True

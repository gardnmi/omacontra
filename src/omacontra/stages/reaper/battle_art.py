"""Code-drawn characters and effects over a locally installed wallpaper."""
from omacontra.rendering.health_medals import draw_health
import math
from pathlib import Path
import cairo
from omacontra.stages.reaper.combat import wave_band, SCYTHE_CUES
from omacontra.rendering import sprites
from omacontra.rendering import combat_fx as fx
from omacontra.rendering import player_gun_fx as gun_fx
from omacontra.rendering import movement_fx
from omacontra.rendering import finish_fx
from omacontra.stages.reaper.reaper_environment import ReaperEnvironment

COLORS={'cream':(.85,.82,.65),'red':(.95,.19,.12),'green':(.61,.77,.36),'gold':(1,.67,.19),'ink':(.07,.07,.075),'smoke':(.22,.12,.09)}
def color(c,name,alpha=1):c.set_source_rgba(*COLORS.get(name,COLORS['cream']),alpha)
def rect(c,x,y,w,h,name):color(c,name);c.rectangle(x,y,w,h);c.fill()
def label(c,x,y,s,size=12,name='cream'):
    color(c,name);c.select_font_face('monospace',cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_BOLD);c.set_font_size(size);c.move_to(x,y);c.show_text(s)
def line(c,points,name='red',width=2,alpha=1):
    color(c,name,alpha);c.set_line_width(width);c.move_to(*points[0])
    for p in points[1:]:c.line_to(*p)
    c.stroke()
def glow(c,x,y,r,name='red',strength=.6):
    g=cairo.RadialGradient(x,y,0,x,y,r);g.add_color_stop_rgba(0,*COLORS[name],strength);g.add_color_stop_rgba(1,*COLORS[name],0);c.set_source(g);c.arc(x,y,r,0,math.tau);c.fill()
from omacontra.rendering.hero_pose import hero_frames, pose_rect, muzzle_position, weapon_pose, carry_frame, run_motion

class BattleRenderer:
    def __init__(self,wallpaper=None):
        default=sprites.ASSETS/'arrival-wallpaper.png'
        self.path=Path(wallpaper) if wallpaper else default
        self.wallpaper=cairo.ImageSurface.create_from_png(str(self.path)) if self.path.exists() else None
        self.stage=cairo.ImageSurface.create_from_png(str(sprites.ASSETS/'reaper-arena.png'))
        self.environment=ReaperEnvironment(self.stage)

    def background(self,c,f,role):
        x,y,w,h=f.rects[role];rect(c,x,y,w,h,'ink')
        if role=='arena':
            c.save();c.rectangle(x,y,w,h);c.clip()
            sprites.paint_background(c,self.stage,x,y+37,w,(h-64)/.82)
            self.environment.draw(c,f,x,y+37,w,(h-64)/.82)
            c.restore()
            self.reaper(c,f)
            if f.state=='play':
                bx,by=f.body
                glow(c,bx,by,90,'red',.15+.1*math.sin(f.clock*3))
                glow(c,bx,by,13,'red',.7+.25*math.sin(f.clock*5))
                if f.shielded:
                    # Faint energized cables replace the geometric shield ring.
                    for i in range(3):
                        points=[(bx+math.sin(j*.7+f.clock*3+i)*9,by+j*5) for j in range(12)]
                        line(c,points,'red',1,.2)
                else:
                    sprites.draw(c,'reaper-sprites.png',sprites.IMPACT,bx-18,by-18,36,36,alpha=.65+.2*math.sin(f.clock*8))
                    label(c,bx-45,by-45,'CORE EXPOSED',11,'red')
                if f.boss_flash:glow(c,bx,by,90,'cream',.9)
            rect(c,x,y,w,37,'ink');label(c,x+14,y+17,'01 / THE REAPER',12)
            label(c,x+w-175,y+17,'PHASE '+str(f.phase)+' / '+('DEFEATED' if f.state=='won' else 'CORE RUPTURE' if f.state=='dying' else 'SHIELDED' if f.shielded else 'EXPOSED'),10,'red')
            rect(c,x+14,y+25,w-28,3,'cream');rect(c,x+14,y+25,(w-28)*f.boss_hp/f.boss_max,3,'red')
            line(c,[(x,f.floor),(x+w,f.floor)],'cream',2,.7)
            for i in range(0,int(w),22):line(c,[(x+i,f.floor+4),(x+i+8,f.floor+12)],'cream',1,.17)
            label(c,x+12,y+h-7,'A/D MOVE   SPACE DOUBLE JUMP   SHIFT SLIDE / AIR DASH   S DUCK   MOUSE FIRE / J FIRE   P PAUSE   R RESTART   ESC MENU',9)
            if f.warning:
                cue=('SCYTHE / '+' > '.join(SCYTHE_CUES[p] for p in f.scythe_pattern)) if f.warning=='scythe' else {'aimed':'EYE LOCK / KEEP MOVING','raven':'RAVENS INBOUND'}[f.warning]
                if f.warning=='scythe' and f.scythe_pattern==('dash',) and f.dash_casts==0:cue='JUMP + AIR DASH OVER THE SWEEP'
                label(c,x+20,y+67,cue,15,'red')
                if f.warning=='scythe':
                    top,bottom=wave_band(f.scythe_pattern[0],f.floor)
                    color(c,'red',.035+.025*math.sin(f.clock*12));c.rectangle(x,top,w,bottom-top);c.fill()
                    label(c,x+280,top-10,SCYTHE_CUES[f.scythe_pattern[0]],13,'cream')
            if f.wave_queue:
                due,kind=f.wave_queue[0]
                label(c,x+20,y+67,'NEXT: '+SCYTHE_CUES[kind],16,'red')
            if f.scythe_flash>0:
                alpha=f.scythe_flash/.22
                sx=x+w*.63+f.boss_offset[0]
                sprites.draw(c,'reaper-sprites.png',sprites.IMPACT,sx-65,f.floor-155,130,130,alpha=alpha)

    def reaper(self,c,f):
        if f.state=='won':return
        x,y,w,h=f.rects['arena'];scale=h/750
        frame=sprites.BOSS[f.death_pose if f.state=='dying' else f.boss_pose]
        bw,bh=frame[2]*scale,frame[3]*scale;dx,dy=f.boss_offset
        left=x+w*.57+dx;top=f.floor-bh+dy
        if f.state!='dying':
            sprites.draw(c,'reaper-sprites.png',frame,left,top,bw,bh)
            return
        age=f.death_age
        # The silhouette shudders, then breaks into strips as the cloak unravels.
        if age<3:
            fade=max(0,1-max(0,age-.65)/2.35)
            for row in range(18):
                delay=row*.035;split=max(0,age-.7-delay)
                sy=frame[1]+frame[3]*row/18
                part=(frame[0],sy,frame[2],frame[3]/18)
                dx=math.sin(age*38+row*.2)*(3+split*9)
                dy=split*split*20
                sprites.draw(c,'reaper-sprites.png',part,left+dx,top+bh*row/18+dy,bw,bh/18,alpha=fade)
        # Fragments use the actual armor artwork, not generic particle squares.
        elapsed=max(0,age-.8)
        if elapsed>0:
            for row in range(7):
                for col in range(5):
                    i=row*5+col
                    sx=frame[0]+col*frame[2]/5;sy=frame[1]+row*frame[3]/7
                    part=(sx,sy,frame[2]/5,frame[3]/7)
                    vx=math.sin(i*2.39)*170;vy=-100-(i*37%150)
                    px=left+(col+.5)*bw/5+vx*elapsed
                    py=top+(row+.5)*bh/7+vy*elapsed+170*elapsed*elapsed
                    py=min(f.floor-10,py)
                    alpha=max(0,min(1,(4-age)*.7))
                    c.save();c.translate(px,py);c.rotate(math.sin(i)*elapsed*3)
                    sprites.draw(c,'reaper-sprites.png',part,-bw/10,-bh/14,bw/5,bh/7,alpha=alpha)
                    c.restore()
        for px,py,blast_age,size in f.death_blasts:
            alpha=max(0,1-blast_age/.55);size*=.65+blast_age*2.7
            glow(c,px,py,size,'red',alpha*.45)
            sprites.draw(c,'reaper-sprites.png',sprites.IMPACT,px-size/2,py-size/2,size,size,alpha=alpha)

    def energy_wave(self,c,x,y,w,h,t):
        # Flowing tendrils breathe in narrow strips; alpha preserves violet light.
        for i in range(16):
            offset=math.sin(t*10-i*.65)*h*.035
            sprites.draw(c,'reaper-energy-wave.png',(40+i*2090/16,165,2090/16,420),
                         x+i*w/16,y+h*.04+offset,w/16+.2,h*.92)

    def scythe_wave(self,c,f,b):
        kind=b.kind[7:];top,bottom=wave_band(kind,f.floor);height=bottom-top
        if kind=='dash':
            self.energy_wave(c,b.x-150,top,300,height,f.clock)
        else:
            c.save();c.translate(b.x+35,top);c.rotate(math.pi/2)
            self.energy_wave(c,0,0,height,70,f.clock)
            c.restore()

    def weak_point(self,c,f,role):
        x,y,w,h=f.rects[role];cx,cy=f.node_center(role)
        if f.nodes[role]<=0:return
        charging=(role=='eye' and f.warning=='aimed') or (role=='raven' and f.warning=='raven')
        glow(c,cx,cy,75 if charging else 55,'red',.5 if charging else .25)
        frame=sprites.RAVENS[int(f.clock*7)%3] if role=='raven' else sprites.EYE
        c.save();c.translate(cx,cy)
        if not charging and not any(kind==('raven' if role=='raven' else 'aimed') for _,kind in f.burst_queue):
            c.rotate((.16 if role=='raven' else .07)*math.sin(f.patrol_time[role]*1.2))
        sprites.draw(c,'reaper-sprites.png',frame,-40,-40,80,78)
        c.restore()
        label(c,cx-32,cy-49,role.upper(),10,'red')
        rect(c,cx-35,cy+47,70*f.nodes[role]/f.node_max,3,'red')
        if f.node_fire_flash.get(role,0):
            sprites.draw(c,'reaper-sprites.png',sprites.IMPACT,cx-35,cy-35,70,70,alpha=f.node_fire_flash[role]/.2)
        if f.node_flash.get(role,0):sprites.draw(c,'reaper-sprites.png',sprites.IMPACT,cx-20,cy-20,40,40)

    def hero(self,c,f,aim):
        movement_fx.draw(c,f)
        finish_fx.recovery(c,f,f.x,f.y-3)
        if getattr(f,'hit_age',None) is not None:
            t=f.hit_age;ox,oy=f.hit_origin;direction=f.hit_facing
            c.save();c.translate(ox-direction*110*t,oy-40-210*t+430*t*t)
            c.rotate(-direction*(.35+t*3.5))
            sprites.draw(c,'dhh-body.png',sprites.HERO[4],-28,-34,55,63,flip=direction<0,alpha=max(0,min(1,(.55-t)/.12)))
            c.restore();return
        if f.state=='dead':return
        alpha=.45 if f.invuln>0 and int(f.clock*14)%2 else 1
        aim=f.aim_target
        lower,upper=hero_frames(f,aim)
        carry=carry_frame(f,aim)
        if f.jump_flash>0:
            age=1-f.jump_flash/.24
            for side in (-1,1):
                fx.smoke(c,f.x+side*(8+age*20),f.y+8,14+age*22,
                         f.clock+side,alpha=(1-age)*.25,steam=True)
        def pose(index):
            left,top,w,h=pose_rect(f,index)
            sprites.draw(c,'dhh-modular-body.png',sprites.HERO[index],left,top,w,h,f.facing<0,alpha)
        if f.moving and not f.duck and not f.sliding and f.y>=f.floor-1:
            # Six contact / compression / passing poses. Feet stay on the floor;
            # the upper body and weapon share the same restrained shoulder bob.
            frame,sink,lean=run_motion(f)
            frame=(1,2,0,4,5,3)[frame]
            centers=(280,288,275,265,278,260)
            sx=(frame%3)*512;sy=0 if frame<3 else 512
            top=85 if frame<3 else 65
            sole=465 if frame<3 else 445
            scale=48/(sole-top)
            width=488*scale
            anchor=(centers[frame]-24)*scale
            left=f.x-anchor if f.facing>0 else f.x-(width-anchor)
            seam=f.y-45+sink
            c.save();c.rectangle(f.x-90,seam,180,47);c.clip()
            sprites.draw(c,'dhh-run-legs.png',(sx+24,sy+top,488,sole-top),left,f.y-48+sink,width,48-sink,f.facing<0,alpha)
            c.restore()
            c.save();c.rectangle(f.x-90,f.y-110,180,seam-(f.y-110));c.clip()
            if carry is None:pose(upper)
            else:
                # Whole authored torso frames flex the elbows and shoulders;
                # do not rotate the extended firing rig to fake a carry pose.
                anchor=(230,208,151,220,223,196)[carry]
                belt=435 if carry<3 else 919
                top=70 if carry<3 else 520
                sw=490 if carry==3 else 512
                scale=.10;width=sw*scale
                left=f.x-anchor*scale if f.facing>0 else f.x-(sw-anchor)*scale
                # Rock from the belt with the loaded leg. The entire authored
                # torso moves together, preserving elbow and shoulder anatomy.
                c.translate(f.x,seam)
                c.transform(cairo.Matrix(1,0,-lean*f.facing,1,0,0))
                c.translate(-f.x,-seam)
                sprites.draw(c,'dhh-run-carry-v3.png',((carry%3)*512,top,sw,belt-top),
                             left,seam-(belt-top)*scale,width,(belt-top)*scale,
                             f.facing<0,alpha)
            c.restore()
        elif lower==upper:pose(upper)
        else:
            # Composite at the belt: aiming cannot replace moving legs with a standing pose.
            c.save();c.rectangle(f.x-90,f.y-35,180,40);c.clip();pose(lower);c.restore()
            c.save();c.rectangle(f.x-90,f.y-105,180,70);c.clip();pose(upper);c.restore()
        if carry is not None:return
        wx,wy,angle=weapon_pose(f,aim)
        c.save();c.translate(wx,wy);c.rotate(angle)
        if f.facing<0:c.scale(1,-1)
        # A single complete arm-and-rifle rig attaches to the bare torso.
        # Uniform scaling preserves anatomy at every aim angle.
        scale=.035
        sprites.draw(c,'dhh-weapon-v2.png',(0,240,1536,530),
                     -180*scale,-170*scale,1536*scale,530*scale,alpha=alpha)
        c.restore()
        if getattr(f,'laser',False):
            px,py=muzzle_position(f,aim)
            if getattr(f,'laser_art',None):
                c.save();c.translate(px,py);c.rotate(angle)
                if f.facing<0:c.scale(1,-1)
                sprites.draw(c,f.laser_art,(725,270,800,510),-48.65,-14.7,56,35.7,alpha=alpha)
                c.restore()
            else:fx.rifle(c,px-math.cos(angle)*35,py-math.sin(angle)*35,angle,alpha)
        if f.muzzle:
            px,py=muzzle_position(f,aim)
            gun_fx.muzzle(c,px,py,angle,f.muzzle,getattr(f,'machine_shots',0),alpha=alpha)

    def objects(self,c,f,aim=None):
        if getattr(f,'sound_bank','reaper')=='reaper':finish_fx.masonry(c,f)
        if f.boss_flash:finish_fx.impact(c,*f.body,.08-f.boss_flash)
        for p in f.particles:
            if p.color=='smoke':
                size=p.size*(1+(.45-p.life)*1.5)
                fx.smoke(c,p.x,p.y,size*2.4,f.clock,alpha=min(.38,p.life*1.2))
        for b in f.shots:
            if b.kind=='raven':
                frame=sprites.RAVENS[int(f.clock*11)%3]
                speed=max(1,math.hypot(b.vx,b.vy));dx,dy=b.vx/speed,b.vy/speed
                for i in (3,2,1):
                    sprites.draw(c,'reaper-sprites.png',frame,b.x-dx*i*13-26,b.y-dy*i*13-24,52,48,flip=b.vx>0,alpha=.07*(4-i))
                glow(c,b.x,b.y,35,'red',.22)
                sprites.draw(c,'reaper-sprites.png',frame,b.x-26,b.y-24,52,48,flip=b.vx>0)
            elif b.kind.startswith('scythe_'):
                self.scythe_wave(c,f,b)
            elif b.kind=='scythe':
                self.energy_wave(c,b.x-25,b.y-15,50,30,f.clock)
            elif b.enemy:
                speed=max(1,math.hypot(b.vx,b.vy));dx,dy=b.vx/speed,b.vy/speed
                glow(c,b.x,b.y,37,'red',.42)
                line(c,[(b.x-dx*48,b.y-dy*48),(b.x,b.y)],'red',9,.22)
                line(c,[(b.x-dx*30,b.y-dy*30),(b.x,b.y)],'gold',3,.65)
                sprites.draw(c,'reaper-sprites.png',sprites.SKULL,b.x-23,b.y-21,46,42,flip=b.vx>0)
            else:
                gun_fx.bullet(c,b.x,b.y,b.vx,b.vy)
        for p in f.particles:
            if p.color=='smoke':continue
            color(c,p.color,min(1,p.life*4));c.rectangle(p.x,p.y,p.size,p.size);c.fill()
        self.hero(c,f,aim)

    def hud(self,c,f,paused=False):
        x,y,w,h=f.rects['arena']
        draw_health(c,f.hp,x+15,y+69,unlimited=getattr(f,'unlimited_lives',False),damage_age=f.clock-getattr(f,'damage_clock',-99),capacity=f.max_hp,scale=.8)
        label(c,x+15,y+111,'MACHINE GUN',10,'green')
        label(c,x+15,y+143,'AIR DASH '+('USED' if f.dash_used else 'READY'),9,'cream' if f.dash_used else 'green')
        if f.slide_cooldown>0:label(c,x+15,y+126,'SLIDE RECHARGING',9,'cream')
        if f.notice_time>0:label(c,x+20,y+161,f.notice,13,'green' if f.state=='won' else 'cream')
        if f.state=='play':
            controls=('A / D   MOVE', 'J   FIRE', 'SPACE   JUMP / DOUBLE JUMP',
                      'SHIFT   SLIDE', 'SPACE + SHIFT   JUMP, THEN AIR DASH', 'S   DUCK')
            if getattr(f,'controller_active',False):controls=('LEFT STICK / D-PAD   MOVE', 'RT / X   FIRE', 'A   JUMP / DOUBLE JUMP', 'B / LB   SLIDE / AIR DASH', 'RIGHT STICK   AIM', 'DOWN   DUCK / MENU   PAUSE')
            for i,control in enumerate(controls):
                # Thin dark outline keeps text legible over detailed wallpaper.
                yy=y+191+i*19
                for dx,dy in ((-1,0),(1,0),(0,-1),(0,1)):
                    label(c,x+15+dx,yy+dy,control,11,'ink')
                label(c,x+15,yy,control,11,'cream')
        if paused:label(c,x+w/2-45,y+h/2,'PAUSED',24)
        if f.state=='won':label(c,x+w/2-110,y+h/2,'MERGE IT',18,'green');label(c,x+w/2-55,y+h/2+28,('A / QUATTRO RUN   MENU / OPTIONS' if getattr(f,'controller_active',False) else 'ENTER / QUATTRO RUN   R / RESTART'),11)

"""Black Moon sprites, orbital arena, and silent cinematic finale."""
from omacontra.rendering.health_medals import draw_health
import math
from omacontra.rendering import finish_fx
import cairo
from omacontra.rendering import sprites
from omacontra.stages.space import orbit_effects
from omacontra.stages.space.screensaver_art import Screensaver
from omacontra.rendering.space_pose import SPACE_SCALE, SPACE_ANCHOR
from omacontra.rendering import combat_fx as fx
from omacontra.stages.dragon.wyrm_scene import ground as mist_ground, fog as mist_fog, lightning as mist_lightning
from omacontra.rendering.laser_art import draw_arc_beam
from omacontra.stages.space import containment_shield
from omacontra.stages.space.finale import REAR_VIEW_AT, ENDING_DURATION, DEPARTURE_LAUNCH_AT, boarding_pose, ENCOUNTER_DURATION
from omacontra.stages.reaper.battle_art import color, glow, line, label

FRAMES=((50,0,410,510),(525,0,495,550),(1125,0,300,510),(70,510,375,510),(450,680,640,230),(1090,550,440,460))
def sprite(c,index,x,y,w,h,alpha=1):
    sheet='finale-people-canonical.png' if index in (2,4,5) else 'finale-atlas.png'
    sprites.draw(c,sheet,FRAMES[index],x,y,w,h,alpha=alpha)
def clamp(t):return max(0,min(1,t))

class FinaleRenderer:
    def __init__(self):
        self.screensaver_player=Screensaver()
        orbit_effects.atmosphere();orbit_effects.cloud_flash()

    def sky(self,c,t,animated=False):
        # Distant orbital drift, with no terrestrial foreground or floor.
        drift=math.sin(t*.025)*8
        sprites.draw(c,'finale-earth.png',(0,0,1672,941),-12+drift,-8,1304,736)
        c.set_source_rgba(.005,.012,.025,.32);c.paint()
        for i in range(36):
            x=(i*173.71+t*.6)%1280;y=(i*91.37+t*.25)%720
            c.set_source_rgba(.7,.8,1,.16);c.rectangle(x,y,1,1);c.fill()
        if animated:orbit_effects.draw(c,t,drift)

    def screensaver(self,c,t,alpha):
        self.screensaver_player.draw(c,t,alpha)

    def spacewalk(self,c,t,x,y,attached=True,thrust=0):
        # A parked shuttle, gently drifting in orbit; the tether pays out from
        # its cargo-bay winch. It is scenery, never a projectile or obstacle.
        sx=1160+math.sin(t*.25)*5;sy=606+math.sin(t*.35)*4
        c.save();c.translate(sx,sy);c.rotate(-.32)
        sprite(c,3,-68,-120,136,225);c.restore()
        ax=sx-22;ay=sy-8
        if attached:
            dx=x-ax;dy=y-ay
            tension=min(1,math.hypot(dx,dy)/1050+thrust*.45)
            slack=(90-72*tension)
            c.move_to(ax,ay)
            c.curve_to(ax+dx*.3,ay+dy*.3+slack,
                       ax+dx*.7,ay+dy*.7+slack+math.sin(t*(.9+thrust*2))*9*(1-tension),x,y)
            c.set_source_rgba(.01,.025,.045,.8);c.set_line_width(4);c.stroke_preserve()
            c.set_source_rgba(.65,.72,.76,.65);c.set_line_width(1.5);c.stroke()
        glow(c,ax,ay,7,'gold',.35)

    def portal(self,c,x,y,t,r=90):
        if r<=0:return
        # Illustrated plasma has thickness, self-shadowing and lensed light.
        # Local strip displacement makes filaments flow without spinning the
        # whole event horizon like a flat sign.
        size=r*3.25
        for sy in range(0,1254,18):
            u=sy/1254
            flow=math.sin(t*1.4+u*8)*r*.012*abs(u-.47)*2
            h=min(18,1254-sy)
            sprites.draw(c,'finale-vortex.png',(0,sy,1254,h),
                         x-size*.5+flow,y-size*.47+u*size,size,size*h/1254+.4)
        # Bright matter orbits toward the lens at differing depths.
        c.save();c.translate(x,y);c.rotate(.16)
        for i in range(38):
            u=(t*.22+i/38)%1;a=i*2.399+u*3
            radius=r*(1.6-u*.65)
            c.set_source_rgba(1,.65+.3*(i%2),.4,u*.55);c.set_line_width(1+i%2)
            c.move_to(math.cos(a)*radius,math.sin(a)*radius*.3+r*.2)
            c.line_to(math.cos(a+.04)*(radius-3),math.sin(a+.04)*(radius-3)*.3+r*.2);c.stroke()
        c.restore()

    def nova(self,c,x,y,age):
        # One filled, spherical rupture blooms and then folds into the rift.
        # Blend atlas stages so the gas evolves rather than popping poses.
        if not 0<=age<1.65:return
        progress=clamp(age/1.4)*5;frame=min(5,int(progress));blend=progress-frame
        size=390+110*clamp(age/.45)
        opacity=clamp((1.65-age)/.35)
        c.save();c.push_group();c.set_operator(cairo.OPERATOR_ADD)
        for index,weight in ((frame,1-blend),(min(5,frame+1),blend)):
            if weight:
                sprites.draw(c,'finale-plasma-burst.png',((index%3)*512,(index//3)*512,512,512),
                             x-size/2,y-size/2,size,size,alpha=weight)
        c.pop_group_to_source();c.set_operator(cairo.OPERATOR_OVER);c.paint_with_alpha(opacity);c.restore()

    def boss(self,c,f,scale=1,hud=True):
        x,y=(f.death_origin or f.boss) if f.state in ('ending','won') else f.boss
        t=f.clock
        # Ease between hand poses rather than snapping entire character frames.
        if f.phase==1:
            beat=(t*.7)%3;index=int(beat);mix=beat-index
            for frame,alpha in ((index,1-mix),((index+1)%3,mix)):
                c.save();c.translate(x+28,y+35);c.rotate(math.sin(t*.8)*.035)
                sprites.draw(c,'finale-guardian.png',(frame*512,0,512,550),-180,-155,360,360,alpha=alpha)
                c.restore()
        jx=x-55 if f.phase==1 else x
        jy=y+38 if f.phase==1 else y
        pulse=math.sin(t*math.tau/5.5)
        w=(235 if f.phase==1 else 310)*scale*(1+pulse*.025)
        h=w*(1.0-pulse*.018)
        frame=0 # One stable silhouette; pose switching made the bell jump.
        # Tendrils undulate separately down the sprite, anchored at the bell.
        for sy in range(0,464,16):
            u=sy/464;offset=(math.sin(t*.8-u*3)*6+math.sin(t*1.3-u*6)*2)*u*u*scale
            sprites.draw(c,'finale-guardian.png',(frame*512,560+sy,512,min(16,464-sy)),jx-w*(.625,.56,.71)[frame]+offset,jy-40*scale+u*h,w,h*min(16,464-sy)/464+.3)
        if f.phase==1:
            for i,hp in enumerate(f.nodes):
                nx,ny=f.node(i)
                if hp:
                    glow(c,nx,ny,25,'gold',.35+.15*math.sin(t*5+i))
                    if hud:line(c,[(nx-25,ny+29),(nx-25+50*hp/f.node_max,ny+29)],'gold',3)
        if f.emission:
            ex,ey=f.emitter;glow(c,ex,ey,42,'gold',f.emission*1.5)
        if f.boss_flash:glow(c,x,y,65,'cream',.45)
    def draw(self,c,f,paused=False):
        if f.state=='departure':self.departure(c,f)
        elif f.state=='encounter':self.encounter(c,f)
        elif f.state in ('ending','won'):self.ending(c,f)
        else:
            fade=clamp(f.screensaver_age/3) if f.phase>=2 else 0
            if fade<1:self.sky(c,f.clock,animated=f.phase==1)
            if f.phase>=2:
                self.screensaver(c,f.screensaver_age,fade*fade*(3-2*fade))
            self.spacewalk(c,f.clock,f.x,f.y,thrust=min(1,f.dash_time/.18))
            finish_fx.recovery(c,f,f.x,f.y+18)
            if f.phase>=2:
                glow(c,*f.boss,300,'red',.10 if f.phase==2 else .19)
                if f.phase==2 and f.phase_age<2:
                    bx,by=f.boss
                    for side in (-1,1):
                        c.save();c.rectangle(bx+(0 if side>0 else -210)+side*f.phase_age*100,0,210,450);c.clip()
                        sprites.draw(c,'finale-guardian.png',(0,0,512,550),bx-152+side*f.phase_age*100,by-120,360,360,alpha=max(0,1-f.phase_age/2));c.restore()
            self.boss(c,f)
            if f.phase==3 and f.phase_age<2:
                # The brief transition is an active charge, not another death.
                bx,by=f.emitter
                glow(c,bx,by,45+f.phase_age*25,'gold',.2+f.phase_age*.15)
                for i in range(12):
                    a=i*math.tau/12-f.phase_age*2
                    radius=115-35*f.phase_age
                    line(c,[(bx+math.cos(a)*radius,by+math.sin(a)*radius),
                            (bx+math.cos(a)*(radius-12),by+math.sin(a)*(radius-12))],'gold',2,.7)
            for x,y,life in f.trail:self.player(c,x,y,life*2)
            hit=max(0,1-(f.clock-getattr(f,'hit_clock',-99))/.4)
            if f.invuln<=0 or int(f.clock*15)%2:
                c.save();c.translate(f.x,f.y);c.rotate(math.sin((1-hit)*12)*.2*hit)
                self.player(c,0,0);c.restore()
            if hit>0:glow(c,f.x,f.y,45,'cream',hit*.6)
            glow(c,f.x,f.y+29,13,'gold',.65)
            for b in f.shots:
                if b.enemy:
                    fx.projectile(c,b.kind,b.x,b.y,b.vx,b.vy,f.clock)
                else:line(c,[(b.x,b.y+15),(b.x,b.y)],'gold',3)
            draw_arc_beam(c,f.beam,f.clock,f.beam_hit)
            containment_shield.draw(c,f)
            color(c,'cream');c.arc(f.x,f.y,3,0,math.tau);c.fill()
            color(c,'ink',.9);c.rectangle(0,0,1280,58);c.fill()
            label(c,25,25,'05 / BLACK MOON',16);draw_health(c,f.hp,25,30,unlimited=getattr(f,'unlimited_lives',False),damage_age=f.clock-getattr(f,'damage_clock',-99),capacity=f.max_hp,scale=.75)
            label(c,420,24,('THE ENCLOSURE','THE INTELLIGENCE','CONTAINMENT FAILURE')[f.phase-1],14)
            line(c,[(420,40),(1160,40)],'smoke',7)
            health=sum(f.nodes)/(2*f.node_max) if f.phase==1 else f.boss_hp/f.boss_max
            line(c,[(420,40),(420+740*health,40)],'gold',7)
            label(c,270,695,'ARC RIFLE',12,'gold');label(c,25,695,'THRUSTER',12);line(c,[(125,690),(125+110*(1-f.dash_cooldown/1.2),690)],'gold',4)
            if f.state=='dead':
                color(c,'ink',.8);c.rectangle(320,285,640,145);c.fill()
                label(c,475,340,'SIGNAL LOST',32,'gold')
                label(c,415,388,'CONTINUE SCREEN INCOMING',21)
        if paused:
            color(c,'ink',.7);c.paint();label(c,550,350,'PAUSED',26)
    def player(self,c,x,y,alpha=1):
        # One integrated pose: the glove actually grips the stolen weapon.
        # Shared source coordinates keep the live beam on its aperture.
        scale=SPACE_SCALE;ax,ay=SPACE_ANCHOR
        sprites.draw(c,'dhh-space-laser.png',(0,0,1024,1536),
                     x-ax*scale,y-ay*scale,1024*scale,1536*scale,alpha=alpha)

    def boarding_hero(self,c,t):
        x,floor,_,_,alpha,moving=boarding_pose(t)
        frame=(1,2,3,4)[int(x/15)%4] if moving else 0
        cellx=(frame%3)*512;celly=(frame//3)*512
        sprites.draw(c,'dhh-space-walk.png',(cellx,celly,512,500),
                     x-45.3,floor-88.5,90.6,88.5,alpha=alpha)

    def shuttle_hatch(self,c,t,front=False):
        # Ceramic pressure hatch shares the shuttle's white hull and teal glass.
        x,y,w,h=933,-257,54,112
        closed=clamp((t-13.9)/.7)
        if not front:
            sprites.draw(c,'shuttle-boarding-hatch.png',(96,148,486,982),x,y,w,h)
        elif closed>0:
            # The two pressure-door leaves meet at the center after entry.
            c.save()
            c.rectangle(x,y,w*closed/2,h)
            c.rectangle(x+w-w*closed/2,y,w*closed/2,h)
            c.clip()
            sprites.draw(c,'shuttle-boarding-hatch.png',(672,148,486,982),x,y,w,h)
            c.restore()

    def launch_elevator(self,c,t,front=False):
        _,floor,_,door,_,_=boarding_pose(t)
        if not front:
            # Purpose-built tower: repeated braced bays, rail guides and
            # a complete hoist head. Preserve its illustrated proportions.
            sprites.draw(c,'shuttle-launch-gantry.png',(218,10,585,1500),
                         532,-415,355,910)
            for x in (685,735):
                line(c,[(x,-333),(x,floor-105)],'ink',4)
                line(c,[(x,-333),(x,floor-105)],'cream',1,.6)
            # Ground boarding uses the existing foundry deck. A second
            # support platform here projected through its front wall.
            fx.platform(c,775,952,-145,-115)
            # Recessed hatch in the side of the cockpit hull.
            self.shuttle_hatch(c,t)
            color(c,'ink',.35);c.rectangle(648,floor-104,124,104);c.fill()
            return
        # Cab fascia, side posts and two sliding mesh gates in front of DHH.
        for y,h in ((floor-110,12),(floor,18)):
            sprites.draw(c,fx.PROPS,(25,96,507,91),640,y,140,h)
        for x in (643,773):
            c.save();c.translate(x,floor);c.rotate(-math.pi/2)
            sprites.draw(c,fx.PROPS,(25,96,507,91),0,-4,102,8);c.restore()
        for side in (-1,1):
            c.save();c.rectangle(649,floor-98,122,96);c.clip()
            gx=710+side*(30+door*62)
            color(c,'ink',.3);c.rectangle(gx-30,floor-98,60,96);c.fill()
            for j in range(7):
                x=gx-30+j*10
                line(c,[(x,floor-98),(x,floor-2)],'cream',1,.45)
            for y in range(0,96,12):
                line(c,[(gx-30,floor-98+y),(gx+30,floor-98+y)],'cream',1,.3)
            c.restore()
        glow(c,650,floor-105,7,'green' if door>.8 else 'gold',.8)

    def rocket_exhaust(self,c,x,y,t):
        # Keep the wallpaper's twin red ribbons, but light them from the engines
        # and break up their edges into a fading, turbulent wake.
        for side in (-1,1):
            nozzle=x+side*10
            gradient=cairo.LinearGradient(0,y,0,720)
            gradient.add_color_stop_rgba(0,1,.45,.08,.6)
            gradient.add_color_stop_rgba(.25,1,.12,.035,.42)
            gradient.add_color_stop_rgba(1,.75,.025,.015,.06)
            c.set_source(gradient)
            for edge in (-1,1):
                indices=range(25) if edge==-1 else range(24,-1,-1)
                for i in indices:
                    u=i/24;yy=y+(720-y)*u
                    center=nozzle+side*u*24
                    width=3+u*39
                    ripple=math.sin(u*22-t*14+side)*u*3
                    xx=center+edge*width+ripple
                    if edge==-1 and i==0:c.move_to(xx,yy)
                    else:c.line_to(xx,yy)
            c.close_path();c.fill()
        # Three compact engine plumes with white cores and moving shock cells.
        for i,offset in enumerate((-10,0,10)):
            px=x+offset;length=(80 if offset else 65)*(1+.08*math.sin(t*29+i*2))
            for width,scale,rgb,alpha in ((10,1.2,(1,.12,.02),.35),(6,1,(1,.5,.08),.85),(3,.68,(1,.96,.72),1)):
                grad=cairo.LinearGradient(0,y,0,y+length*scale)
                grad.add_color_stop_rgba(0,*rgb,alpha);grad.add_color_stop_rgba(1,*rgb,0)
                c.set_source(grad);c.move_to(px-width,y)
                c.curve_to(px-width*1.7,y+length*.3,px-width*.4,y+length*.8,px,y+length*scale)
                c.curve_to(px+width*.4,y+length*.8,px+width*1.7,y+length*.3,px+width,y)
                c.close_path();c.fill()
            for j in range(4):
                u=(j/4+t*2.5)%1;yy=y+u*length
                w=3*(1-u);h=7*(1-u)
                c.set_source_rgba(1,.95,.65,(1-u)*.7)
                c.move_to(px,yy-h);c.line_to(px+w,yy);c.line_to(px,yy+h);c.line_to(px-w,yy);c.close_path();c.fill()
            glow(c,px,y,13,'gold',.55)

    def encounter(self,c,f):
        # Illustrated strip matches the harbor/story cutscenes. No gameplay
        # scene, HUD, sprite enlargement or camera-to-arena zoom is used here.
        t=f.age
        c.set_source_rgb(0,0,0);c.paint()
        panel=0 if t<4 else 1 if t<8.5 else 2
        start=(0,4,8.5)[panel];duration=(4,4.5,6)[panel]
        progress=clamp((t-start)/duration)
        atlas=sprites.atlas('finale-last-dive-cinema.png')
        sw=atlas.get_width();sh=atlas.get_height()/3
        x,y,w,h=100,180,1080,250
        c.save();c.rectangle(x,y,w,h);c.clip()
        # Gentle camera travel within each drawn composition, not across the
        # live arena. The last frame holds until the cut to player control.
        zoom=1.035+.025*progress
        offset=(progress-.5)*14
        sprites.draw(c,'finale-last-dive-cinema.png',(0,panel*sh,sw,sh),
                     x-w*(zoom-1)/2+offset,y-h*(zoom-1)/2,w*zoom,h*zoom)
        # Brief dip at each cut preserves clear separation between shots.
        fade=clamp((t-start)/.22) if panel else clamp(t/.4)
        fade*=clamp((ENCOUNTER_DURATION-t)/.3)
        c.set_source_rgba(0,0,0,1-fade);c.paint();c.restore()
        label(c,100,143,'BLACK MOON / THE LAST DIVE',14,'gold')
        if t<4:text='';spoken=0
        elif t<6.6:text='TOBI / RADIO: TELL ME YOU HAVE A WAY BACK.';spoken=t-4
        elif t<9.6:text='DHH: WORKING ON IT.';spoken=t-6.6
        else:text="DHH: LET’S FINISH THIS.";spoken=t-9.6
        label(c,100,505,text[:int(spoken*40)],18)
        label(c,100,549,'ENTER / SKIP TO THE FIGHT',11)

    def departure(self,c,f):
        t=f.age;self.sky(c,f.clock)
        if t<DEPARTURE_LAUNCH_AT:
            _,_,camera,_,_,_=boarding_pose(t)
            sprites.draw(c,'wyrm-mist-arena.png',(0,0,1536,1024),0,-135+camera*.2,1280,800)
            mist_lightning(c,t)
            for i in range(3):mist_fog(c,(i*450+t*16)%1700-250,360+camera*.2,500,150,.23)
            c.save();c.translate(0,camera)
            sprite(c,3,660,-405,660,900)
            # Deck, tower and both characters occupy the same foreground
            # coordinate system. Only the distant mist terrace uses parallax.
            mist_ground(c,495)
            self.launch_elevator(c,t)
            self.boarding_hero(c,t)
            self.launch_elevator(c,t,front=True)
            self.shuttle_hatch(c,t,front=True)
            sprites.draw(c,'foundry-rescue.png',(1200,540,245,470),450,410,45,85)
            c.restore()
            text='TOBI: THE WINE RACK WAS A TERMINAL. THE CORE IS IN ORBIT.' if t<3 else 'DHH: ONE SEAT.' if t<5.8 else 'TOBI: GO. I WILL FIND ANOTHER WAY.'
        else:
            u=clamp((t-DEPARTURE_LAUNCH_AT)/8);y=420-u*340
            haze=max(0,1-u*2.5)
            if haze>0:
                sprites.draw(c,'wyrm-mist-arena.png',(0,0,1536,1024),0,u*260,1280,800,alpha=haze)
                mist_fog(c,120,430+u*180,1000,220,haze*.55)
            self.rocket_exhaust(c,640,y+93,t)
            sprite(c,3,603,y,74,100)
            text='DHH: YOUR LAST RIDE EXPLODED.' if t<DEPARTURE_LAUNCH_AT+3 else 'TOBI: I WILL FIND SOMETHING FASTER.'
        self.bars(c,'THE LAST CONNECTION',text)
        label(c,90,700,'ENTER / SKIP',11)
    def bars(self,c,title,text):
        c.set_source_rgb(0,0,0);c.rectangle(0,0,1280,105);c.rectangle(0,590,1280,130);c.fill()
        label(c,90,68,title,18,'gold');label(c,90,650,text,16)

    def coast(self,c,t):
        # Continuous tracking motion: distant coast drifts slowly, road rapidly.
        offset=min(100,max(0,t-11)*5)
        sprites.draw(c,'finale-homecoming.png',(offset,0,1436,1024),0,0,1280,720)
        for i in range(14):
            x=(i*130-t*390)%1500-130
            line(c,[(x,583),(x+65,583)],'cream',2,.35)

    def ending(self,c,f):
        t=f.age
        if t<7:
            self.sky(c,f.clock);x,y=f.death_origin or f.boss
            pullback=clamp(t/.6);pullback=pullback*pullback*(3-2*pullback)
            c.save();c.translate(640,330+55*pullback);c.scale(1-.22*pullback,1-.22*pullback);c.translate(-640,-330)
            if t<.9:
                c.push_group();self.boss(c,f,1+math.sin(t*27)*.025)
                c.pop_group_to_source();c.paint_with_alpha(clamp((.9-t)/.35))
                glow(c,x,y,50+t*100,'cream',t*.6)
            self.nova(c,x,y,t-.55)
            for i in range(80):
                age=max(0,t-.8);a=i*2.4+age*1.8
                radius=(35+i%9*12)*min(1,age*3)*max(0,1-(age-1)/4)
                color(c,'gold' if i%2 else 'cream',clamp(1-(age-3)/2))
                c.rectangle(x+math.cos(a)*radius,y+math.sin(a)*radius,2+i%3,2+i%3);c.fill()
            if t>1.2:self.portal(c,x,y,t,35+clamp((t-1.2)/1.7)*150)
            u=clamp((t-2.3)/3.9);ease=u*u
            px=f.x+(x-f.x)*ease+math.sin(u*math.tau)*35*math.sin(u*math.pi)
            py=f.y+(y-f.y)*ease
            self.spacewalk(c,f.clock,px,py,attached=t<3.1)
            if 3.1<t<3.45:glow(c,px,py,24,'gold',(3.45-t)*2)
            size=max(.02,1-ease)
            c.save();c.translate(px,py);c.rotate(math.atan2(y-py,x-px)+1.05)
            sprites.draw(c,'dhh-portal-reach.png',(0,0,1254,1254),-38*size,-38*size,76*size,76*size);c.restore()
            if .75<t<.95:
                color(c,'cream',.35*(1-(t-.75)/.2));c.paint()
            c.restore();self.bars(c,'','')
        elif t<11:
            # Wide sky shot establishes the height before showing the rescue car.
            sprites.draw(c,'finale-homecoming.png',(0,0,1536,650),0,0,1280,720)
            u=(t-7)/4
            self.portal(c,640,120,t,45*(1-clamp(u*2))) if u<.5 else None
            py=120+340*u*u
            c.save();c.translate(640+math.sin(u*4)*35,py);c.rotate(-.15+u*.3)
            sprite(c,5,-65,-65,130,136);c.restore()
            for i in range(12):
                x=200+i*80;yy=(i*91-t*230)%720
                line(c,[(x,yy),(x,yy+40)],'cream',1,.3)
            self.bars(c,'','')
        else:
            self.homecoming(c,f)

    def catch_car(self,c,x,y,width,t,landed=False,compression=0,alpha=1):
        # Both poses share exactly the same wheelbase and camera perspective.
        k=width/1420
        c.save();c.translate(x,y);c.scale(k,k)
        c.save();c.rectangle(0,28 if landed else 0,1420,472 if landed else 500);c.clip()
        sprites.draw(c,'finale-catch-car-canonical.png',(50,488 if landed else 0,1420,500),0,compression,1420,500,alpha=alpha)
        c.restore()
        # Rotate the actual inner rim pixels, clipped inside stationary tires.
        for cx,cy in ((235,364),(1056,364)):
            c.save();c.translate(cx,cy+compression)
            c.arc(0,0,88,0,math.tau);c.clip();c.rotate(t*31)
            sprites.draw(c,'finale-catch-car-canonical.png',(50+cx-88,cy-88,176,176),-88,-88,176,176,alpha=alpha)
            c.restore()
        c.restore()

    def homecoming(self,c,f):
        t=min(f.age,ENDING_DURATION);elapsed=t-13
        if t>=REAR_VIEW_AT:
            self.drive_away(c,f,t-REAR_VIEW_AT);return
        # Close tracking at interception, then reveal the entire coastal road.
        u=clamp(elapsed/5);ease=u*u*(3-2*u)
        zoom=1.3-.3*ease
        approach=clamp((t-11)/2)
        arrival=clamp((t-12.45)/.55)
        carx=370-1220*(1-arrival)**2+26*min(0,elapsed)
        if elapsed>=0:carx=370+26*elapsed+1100*max(0,elapsed-.2)**2
        width=660.;k=width/1280
        compression=14*math.exp(-max(0,elapsed)*4)*math.sin(max(0,elapsed)*12) if elapsed>=0 else 0
        c.save();c.translate(680,580);c.scale(zoom,zoom);c.translate(-680,-580)
        self.coast(c,t)
        # Foreground asphalt moves much faster than the distant coastline.
        shift=((t-11)*900)%1280
        c.save();c.rectangle(0,565,1280,155);c.clip()
        for left in (-shift,1280-shift):
            sprites.draw(c,'finale-homecoming.png',(0,850,1536,174),left,565,1280,155)
        c.restore()
        # Road rush stays continuous through impact and the final pullback.
        for i in range(20):
            xx=(i*93-t*560)%1500-100
            line(c,[(xx,614+i%3*18),(xx+45,614+i%3*18)],'cream',2,.15)
        seatx=370+510*k
        py=315-630*(1-approach*approach)
        blend=clamp(elapsed/.16)
        if blend<1:
            c.save();c.rectangle(0,0,1280,445);c.clip()
            # Scale matches the heads in the dedicated landed frame.
            sprite(c,5,seatx-90,py,190,198,1-blend)
            c.restore()
        # Draw exactly one opaque car. Overlapping whole atlas poses doubled
        # the driver's scalp because the original frames were not aligned.
        if t>=12.45:self.catch_car(c,carx,360,width,t,landed=elapsed>=0,compression=compression)
        if 0<=elapsed<.9:
            for i in range(28):
                u=elapsed/.9;px=carx+110-i*3-u*(70+i*4)
                py=558-u*(18+i%5*9)+u*u*50
                color(c,'cream',(1-u)*.25)
                c.arc(px,py,1+u*(2+i%3),0,math.tau);c.fill()
        c.restore()
        self.bars(c,'','')
        if f.state=='won':label(c,345,365,'OMACONTRA / THE END',34);label(c,435,410,'RESULTS INCOMING',14)

    def drive_away(self,c,f,t):
        # Reverse-angle match cut: same passengers, camera following the car.
        sprites.draw(c,'finale-coastal-highway.png',(0,0,1672,941),0,0,1280,720)
        horizon=285.;vanish=650.
        # Perspective lane markings expand toward the camera to show speed.
        for lane in (-1,0,1):
            for i in range(14):
                z=(i/14+t*.48)%1
                z2=min(1,z+.024)
                y1=horizon+(720-horizon)*z*z;y2=horizon+(720-horizon)*z2*z2
                x1=vanish+lane*650*z*z;x2=vanish+lane*650*z2*z2
                width=1+z*z*8
                color(c,'gold' if lane==-1 else 'cream',.8)
                c.move_to(x1-width/2,y1);c.line_to(x1+width/2,y1)
                c.line_to(x2+width/2,y2);c.line_to(x2-width/2,y2);c.close_path();c.fill()
        # Actual project wordmark, integrated above the destination skyline.
        wordmark=sprites.atlas('omarchy-wordmark.png')
        c.save();c.translate(465,119);c.scale(350/wordmark.get_width(),62/wordmark.get_height())
        c.set_source_rgba(.04,.13,.20,.75);c.mask_surface(wordmark,2,3)
        c.set_source_rgb(.94,.94,.81);c.mask_surface(wordmark,0,0);c.restore()
        u=clamp(t/7.6);ease=u*u*(3-2*u)
        w=520-310*ease;h=w*800/1160
        x=650-w/2+math.sin(t*.85)*8*(1-u)
        bottom=575-165*ease;y=bottom-h+math.sin(t*15)*1.2*(1-u)
        c.save();c.translate(x+w*.5,bottom-6*w/520);c.scale(w*.45,12*w/520)
        c.set_source_rgba(.015,.02,.03,.5);c.arc(0,0,1,0,math.tau);c.fill();c.restore()
        sprites.draw(c,'finale-car-rear.png',(45,285,1160,800),x,y,w,h)
        # Small exhaust glints and road streaks stay behind the bumper.
        for side in (-1,1):
            glow(c,650+side*w*.26,bottom-h*.12,5*(1-u),'gold',.15)
        self.bars(c,'','')
        if f.state=='won':
            label(c,425,650,'OMACONTRA / THE END',25)
            label(c,450,689,'RESULTS INCOMING',13)

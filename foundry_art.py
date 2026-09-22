"""Moonlit foundry and the Quattro rescue, rendered from dedicated sprite art."""
import copy
from laser_art import draw_arc_beam
from health_medals import draw_health
import math
import sprites
import combat_fx as fx
import player_gun_fx as gun_fx
import wyrm_scene as wyrm
from battle_art import BattleRenderer, color, glow, label, line
from foundry import RESCUE_CAR_SCALE, RESCUE_CAR_X, SHOULDER_CHARGE, FORGE_WINDUP, CAR_ENTRY, IMPACT, EJECTION, EXPLOSION, rescue_car, rescue_tobi


def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)


class FoundryRenderer:
    def __init__(self):
        self.hero_renderer=BattleRenderer()
        self.terrace=wyrm.MistTerrace()
        wyrm.wisp_stamp()

    def background(self,c,t):
        self.terrace.sky(c,t)

    def warden(self,c,f,pose=None,dx=0,dy=0,alpha=1):
        self.terrace.dragon(c,f,dx,dy,alpha)

    def weapon(self,c,x,y,angle,scale=1):
        c.save();c.translate(x,y);c.rotate(angle)
        if math.cos(angle)<0:c.scale(1,-1)
        sprites.draw(c,'foundry-throat-weapon.png',(725,270,800,510),
                     -40*scale,-21*scale,80*scale,51*scale)
        c.restore()

    def mouth_emitter(self,c,x,y,alpha=1):
        wyrm.halo(c,x,y,23,alpha)

    def shoulder(self,c,f,dx=0,dy=0):
        x,y=f.mount_target;self.mouth_emitter(c,x+dx,y+dy)

    def hero(self,c,f,x=None,duck=False,y=None):
        actor=copy.copy(f)
        if x is not None:
            actor.x=x;actor.y=630. if y is None else y;actor.moving=False
            if y is not None:actor.support=(x-100,x+100,535. if f.lava_age is not None else 630.)
            actor.slide_time=actor.dash_time=0.;actor.duck=duck;actor.muzzle=0.
            actor.facing=1;actor.aim_target=None;actor.invuln=0.
        self.hero_renderer.hero(c,actor,None if x is not None else f.aim_target)

    def explosion(self,c,x,y,age,size):
        if not 0<=age<.78:return
        frame=min(5,int(age/.13))
        sprites.draw(c,'quattro-explosion.png',((frame%3)*512,(frame//3)*512,512,512),x-size/2,y-size/2,size,size)

    def tells(self,c,f):
        if f.forge_warning in ('wisps','fan','breath','fire'):
            x,y=f.dragon_point(*wyrm.EYES[f.forge_round%2])
            charge=max(0,1-f.forge_timer/FORGE_WINDUP[f.forge_warning])
            wyrm.halo(c,x,y,16+charge*23,.4+charge*.6)
            for i in range(5):
                a=i*math.tau/5+f.clock*2;radius=29*(1-charge)+6
                wyrm.halo(c,x+math.cos(a)*radius,y+math.sin(a)*radius,3,charge)
        warning=getattr(f,'ledge_warning',None)
        if warning:
            x,y,age,width=warning
            wyrm.fog(c,x-width,y-24,width*2,48,.3+age*.3)
            for offset in (-.75,0,.75):
                wyrm.halo(c,x+width*offset,y-4,18+age*18,.3+age*.35)
        if f.forge_warning=='updraft':
            charge=max(0,1-f.forge_timer/1.15)
            wyrm.fog(c,f.mark-55,f.attack_floor-26,110,42,.35+charge*.5)
            wyrm.halo(c,f.mark,f.attack_floor-8,15+charge*12,charge*.4)
        for h in f.hazards:
            if h.kind in ('breath','fire'):
                (sx,sy),(ex,ey)=f.fire_path(h)
                alpha=min(1,h.age/.16)*min(1,max(0,(.8-h.age)/.15))
                wyrm.storm_lance(c,sx,sy,ex,ey,f.clock,alpha)
            elif h.kind=='updraft':
                wyrm.stone_eruption(c,h.x,h.y,h.width,h.age)
        self.arc_beam(c,f.enemy_beam,f.clock)
        for b in f.bolts:
            wyrm.storm_projectile(c,b.x,b.y,math.atan2(b.vy,b.vx),b.age,b.kind=='heavy')

    def disarm(self,c,f):
        self.background(c,f.clock)
        c.save();c.translate(0,f.camera_y)
        self.warden(c,f);self.terrace.foreground(c,f.clock);self.platforms(c,f);self.hero(c,f)
        x,y,angle=f.dropped_weapon
        unfold=min(1,f.disarm_age/.3)
        c.save();c.translate(x,y);c.rotate(angle)
        self.mouth_emitter(c,0,0,1-unfold)
        c.restore()
        c.save();c.push_group();self.weapon(c,x,y,angle,.4+.25*unfold)
        c.pop_group_to_source();c.paint_with_alpha(unfold);c.restore()
        fx.smoke(c,*f.drop_origin,65,f.clock,alpha=max(0,.45-f.disarm_age*.4),steam=True)
        glow(c,x,y,30,'gold',max(0,1-f.disarm_age))
        c.restore()
        bars=55*min(1,f.disarm_age/.15,max(0,(1.35-f.disarm_age)/.2))
        color(c,'ink');c.rectangle(0,0,1280,bars);c.rectangle(0,720-bars,1280,bars);c.fill()

    def platforms(self,c,f):
        for left,right,top in f.platforms:
            wyrm.platform(c,left,right,top,42)
        wyrm.ground(c)

    def laser(self,c,f):
        self.arc_beam(c,f.beam,f.clock,f.beam_hit)

    arc_beam=staticmethod(draw_arc_beam)

    def draw(self,c,f,paused=False,hud=True):
        if f.state=='disarm':
            self.disarm(c,f)
            if paused:self.pause(c)
            return
        if f.state in ('rescue','won'):
            self.rescue(c,f)
            if paused:self.pause(c)
            return
        self.background(c,f.clock)
        c.save();c.translate(0,f.camera_y)
        self.warden(c,f);self.terrace.foreground(c,f.clock);self.platforms(c,f)
        self.terrace.storm(c,f)
        for p in f.pickups:
            self.weapon(c,p.x,p.y,-.4,.65)
            glow(c,p.x,p.y,28,'gold',.2)
        cx,cy=f.core
        wyrm.halo(c,cx,cy,38,.25+.15*math.sin(f.clock*5)**2)
        if f.boss_flash:glow(c,cx,cy,45,'cream',.65)
        self.tells(c,f);wyrm.throat_core(c,f);self.hero(c,f);self.laser(c,f)
        for b in f.shots:
            gun_fx.bullet(c,b.x,b.y,b.vx,b.vy)
        for p in f.particles:
            if p.color=='smoke':fx.smoke(c,p.x,p.y,p.size*3,f.clock,alpha=min(.35,p.life))
            else:
                color(c,p.color,min(1,p.life*3));c.rectangle(p.x,p.y,p.size,p.size);c.fill()
        c.restore()
        if hud:
            color(c,'ink',.93);c.rectangle(0,0,1280,70);c.fill()
            label(c,25,26,'04 / THE MIST GATE',16);draw_health(c,f.hp,25,34,unlimited=getattr(f,'unlimited_lives',False),damage_age=f.clock-getattr(f,'damage_clock',-99),capacity=f.max_hp,scale=.75)
            label(c,410,25,'OBSIDIAN WYRM',14)
            color(c,'smoke');c.rectangle(410,38,720,9);c.fill()
            color(c,'gold');c.rectangle(410,38,720*f.boss_hp/f.boss_max,9);c.fill()
            if f.mount_hp>0:
                label(c,410,63,'THROAT CORE',10,'gold')
                color(c,'smoke');c.rectangle(545,55,190,5);c.fill()
                color(c,'gold');c.rectangle(545,55,190*f.mount_hp/f.mount_max,5);c.fill()
            color(c,'ink',.88);c.rectangle(0,680,1280,40);c.fill()
            label(c,25,705,'ARC RIFLE' if f.laser else 'MACHINE GUN / ARMORED',12,'gold')
        if f.state=='dead':
            color(c,'ink',.8);c.paint();label(c,410,340,'DHH DOWN',34);label(c,410,384,'CONTINUE SCREEN INCOMING',16)
        elif paused:self.pause(c)

    def pause(self,c):
        color(c,'ink',.75);c.paint();label(c,510,350,'PAUSED',32)

    def rescue(self,c,f):
        t=f.rescue_age
        c.set_source_rgb(0,0,0);c.paint()
        # Widescreen strip closes around the same arena, without changing scale
        # or cutting away from the impact. Car and Tobi have independent paths.
        bars=100*smooth(t/.8)
        c.save();c.rectangle(0,bars,1280,720-bars*2);c.clip()
        shake=max(0,1-(t-IMPACT)/.38)*9 if t>=IMPACT else 0
        c.translate(math.sin(t*103)*shake,math.cos(t*127)*shake*.5)
        # Include the grounded survivors in the strip without clipping heads.
        c.save();c.translate(0,-35*smooth(t/.8))
        self.background(c,f.clock)
        if f.lava_age is not None:self.platforms(c,f)
        sx,sy=f.cannon
        dhh_x=f.rescue_start_x+(390-f.rescue_start_x)*smooth(t/1.15)
        if t<EXPLOSION:
            self.warden(c,f,2 if t>=1.25 else 0,dx=math.sin(t*38)*max(0,1-t)*9)
            charge=smooth((t-1.25)/2.7)
            wyrm.halo(c,sx,sy,90+charge*160,charge*.7)
            wyrm.halo(c,sx,sy,35+charge*65,charge)
            for i in range(30):
                r=(1-(t*.5+i/30)%1)*210
                angle=i*2.4+t
                x=sx+math.cos(angle)*r;y=sy+math.sin(angle)*r
                color(c,'gold',charge);c.rectangle(x,y,3,3);c.fill()
            for eye in wyrm.EYES:
                ex,ey=f.dragon_point(*eye)
                wyrm.halo(c,ex,ey,24+charge*55,charge*.95)
                wyrm.halo(c,ex,ey,9+charge*14,charge)
        if CAR_ENTRY<=t<EXPLOSION:
            x,y,angle=rescue_car(t)
            if t>=IMPACT:
                crash=t-IMPACT;x+=10*math.sin(crash*25);y+=110*crash*crash;angle+=.65*crash
            c.save();c.translate(x,y);c.rotate(angle);c.scale(RESCUE_CAR_SCALE,RESCUE_CAR_SCALE)
            sprites.draw(c,'foundry-rescue-empty.png' if t>=EJECTION else 'foundry-rescue.png',(195,12,1200,524),-200,-87,400,175)
            c.restore()
            if t>=EJECTION:
                # Glass and sparks trail the now-empty cockpit as Tobi exits.
                glow(c,x-40*RESCUE_CAR_SCALE,y-50*RESCUE_CAR_SCALE,28,'smoke',.95)
                self.explosion(c,x-40*RESCUE_CAR_SCALE,y-45*RESCUE_CAR_SCALE,t-EJECTION,55)
            if t<IMPACT:
                for i in range(12):
                    line(c,[(x-160-i*6,y+20+i%3*5),(x-180-i*8,y+20+i%3*5)],'gold',2,.4)
        if t>=IMPACT:
            self.explosion(c,600,380,t-IMPACT,160)
        if t>=EXPLOSION:
            age=t-EXPLOSION
            # Debris uses actual car and furnace fragments, never respawns the
            # intact vehicle. Short staggered bursts carry the main destruction.
            for i in range(24):
                car=i%2==0;sheet='foundry-rescue-empty.png' if car else 'wyrm-head.png'
                frame=((i*127)%1300,150+(i%3)*70,110,85) if car else (140+(i%4)*170,240+(i%5)*190,100,110)
                vx=math.sin(i*2.4)*290;vy=-170-i%5*42
                x=(RESCUE_CAR_X if car else f.boss_x)+vx*age;y=min(620,385+vy*age+240*age*age)
                c.save();c.translate(x,y);c.rotate(age*math.sin(i)*5)
                sprites.draw(c,sheet,frame,-16,-13,32,26,alpha=max(.25,1-age*.16));c.restore()
            for i in range(14):
                start=(i%5)*.11
                self.explosion(c,560+math.sin(i*8)*140,370+math.cos(i*7)*145,age-start,180+i%3*60)
            for i in range(18):
                glow(c,420+i*13,619-abs(math.sin(t*5+i))*18,28,'red',max(.08,.3-age*.03))
        self.terrace.storm(c,f)
        landing=535. if f.lava_age is not None else 630.
        hop=min(1,t/1.15)
        dhh_y=f.rescue_start_y+(landing-f.rescue_start_y)*smooth(hop)
        if f.lava_age is not None:dhh_y-=70*math.sin(math.pi*hop)
        self.hero(c,f,dhh_x,duck=2.6<t<8.3,y=dhh_y)
        if t>=EJECTION:
            x,y,angle,pose=rescue_tobi(t)
            if f.lava_age is not None:y-=95*smooth((t-EJECTION)/1.55)
            index={'air':0,'land':1,'stand':2}[pose]
            c.save();c.translate(x,y);c.rotate(angle)
            frame=((75,540,540,410),(688,662,330,343),(1200,540,245,470))[index]
            width,height=((95,72),(64,67),(43,83))[index]
            sprites.draw(c,'foundry-rescue.png',frame,-width/2,-height,width,height)
            c.restore()
        c.restore();c.restore()
        if IMPACT<=t<IMPACT+.07:
            c.set_source_rgba(1,.91,.7,.6*(1-(t-IMPACT)/.07));c.paint()
        if t<1.25:title='THE WYRM FALLS SILENT';text=''
        elif t<2.7:title='THE STORM GATHERS';text='DHH: THAT DOES NOT LOOK FIXED.'
        elif t<CAR_ENTRY:title='THE STORM GATHERS';text='DHH: DO IT....DO IT NOW!!!!!'
        elif t<IMPACT:title='INCOMING';text='TOBI: GET DOWN!'
        elif t<9.1:title='QUATTRO / LAST DELIVERY';text=''
        elif t<11.3:title='THE MIST GATE IS CLEAR';text='DHH: YOU JUST THREW A QUATTRO AT A DRAGON.'
        else:title='THE MIST GATE IS CLEAR';text="TOBI: YOU’RE WELCOME."
        label(c,70,65,title,17,'gold');label(c,70,660,text,17)
        if f.state=='won':label(c,70,695,'ENTER / THE LAUNCH SITE / R REPLAY / ESC MENU',12)


class FoundryIntro:
    DURATION=8.6
    def __init__(self):self.age=0.;self.kind='intro'
    @property
    def finished(self):return self.age>=self.DURATION
    def step(self,dt):self.age+=max(0,min(.04,dt))
    def skip(self):self.age=self.DURATION
    def draw(self,c,renderer,f):
        t=self.age;scene=copy.copy(f);scene.clock=t
        scene.x=90+120*smooth(t/2.6);scene.y=630
        scene.moving=t<2.6;scene.run_phase=t*8
        scene.invuln=0.;scene.muzzle=0.;scene.aim_target=None;scene.facing=1
        scene.forge_warning=None;scene.sweep_age=0.
        renderer.background(c,t)
        if t>=2.4:
            approach=smooth((t-4.8)/1.35)
            scale=.32+.68*approach
            alpha=.12*smooth((t-3.0)/1.4)+.88*smooth((t-4.8)/1.2)
            renderer.terrace.dragon(c,scene,alpha=alpha,scale=scale,
                                    glow_strength=min(1,(t-2.4)/1.2))
            renderer.terrace.veil(c,t,.9*(1-approach))
        renderer.terrace.foreground(c,t,1.5)
        renderer.platforms(c,scene);renderer.hero(c,scene)
        opening=smooth((t-6.6)/2)
        c.set_source_rgb(.025,.03,.035)
        c.rectangle(0,0,1280,70*(1-opening));c.rectangle(0,650+70*opening,1280,70*(1-opening));c.fill()
        if opening<.9:
            label(c,55,45,'04 / THE MIST GATE',19)
            text='DHH: THERE’S THE SHIP.' if t<2.8 else 'DHH: SOMETHING IS IN THE FOG.' if t<5.4 else ''
            label(c,55,684,text,16)
            label(c,1080,684,'ENTER / SKIP',11)

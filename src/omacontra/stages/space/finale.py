"""Black Moon: deterministic top-down finale and departure/homecoming timeline."""
import math
import random
from dataclasses import dataclass
from omacontra.stages.dragon.foundry import rope_path
from omacontra.stages.reaper.combat import segment_box
from omacontra.rendering.space_pose import laser_muzzle

DEPARTURE_LAUNCH_AT=15.
BOARDING_LANDING_Y=-65. # Hull hatch below the cockpit glass.
DEPARTURE_DURATION=23.
ENCOUNTER_DURATION=14.5
REAR_VIEW_AT=14.4
ENDING_DURATION=REAR_VIEW_AT+7.6

def boarding_pose(t):
    """Launch-tower movement in world space: deck, lift, upper walkway."""
    def ease(u):
        u=max(0.,min(1.,u));return u*u*(3-2*u)
    walk=ease((t-3)/2.2)
    rise=ease((t-5.8)/5.)
    cross=ease((t-11.4)/2.4)
    x=545+165*walk+260*cross
    floor=495-(495-BOARDING_LANDING_Y)*rise
    camera=(445-BOARDING_LANDING_Y)*rise
    door=1-ease((t-5.2)/.6)+ease((t-10.8)/.6)
    alpha=1-ease((t-13.4)/.6)
    moving=3<t<5.2 or 11.4<t<13.8
    return x,floor,camera,door,alpha,moving

@dataclass
class Shot:
    x:float
    y:float
    vx:float
    vy:float
    enemy:bool=True
    age:float=0.
    kind:str="pearl"
    turn:float=0.

class Finale:
    sound_bank='finale'
    def __init__(self,seed=5):
        self.rng=random.Random(seed);self.state='departure';self.age=0.;self.clock=0.
        self.x=640.;self.y=590.;self.hp=7;self.max_hp=self.hp;self.invuln=0.;self.shots=[]
        self.final_phase_max=1500.
        self.boss_hp=self.boss_max=750.+self.final_phase_max
        self.node_max=675.;self.nodes=[self.node_max,self.node_max]
        self.fire=0.;self.volley=1.5;self.round=0;self.boss_flash=0.
        self.dash_time=0.;self.dash_cooldown=0.;self.dash_vector=(0.,-1.);self.was_slide=False
        self.emission=0.;self.death_origin=None
        self.trail=[];self.phase_age=0.;self.last_phase=1
        self.beam=[];self.beam_hit=False;self.laser_contact=None;self.screensaver_age=0.
        self.sfx_events=[];self.sfx_last={};self.laser_held=False

    def sound(self,name,cooldown=0):
        if self.clock-self.sfx_last.get(name,-999)<cooldown:return
        self.sfx_last[name]=self.clock
        self.sfx_events.append(name);self.sfx_events=self.sfx_events[-32:]
    @property
    def phase(self):return 1 if any(self.nodes) else 2 if self.boss_hp>self.final_phase_max else 3
    @property
    def boss(self):return 640+math.sin(self.clock*.55)*210,175+math.sin(self.clock*.9)*20
    @property
    def emitter(self):
        x,y=self.boss
        return (x-55,y+38) if self.phase==1 else (x,y)
    def node(self,i):
        x,y=self.boss;return x+(-110 if i==0 else -25),y+(65 if i==0 else 108)
    @property
    def shield_hitbox(self):
        # Whole containment area: helmet, hands and enclosed jellyfish.
        x,y=self.boss
        return x-210,y-105,x+150,y+215

    def begin_encounter(self):
        self.state='encounter';self.age=0.;self.shots=[];self.beam=[]

    def skip(self):
        if self.state in ('departure','encounter'):
            self.state='play';self.age=0.;self.clock=ENCOUNTER_DURATION
            self.x,self.y=640.,590.;self.volley=2.25;self.invuln=2.25
            self.shots=[];self.beam=[];self.beam_hit=False;self.laser_contact=None
    def hurt(self):
        if self.state=='play' and self.invuln<=0 and self.dash_time<=0:
            self.damage_taken=getattr(self,'damage_taken',0)+1;self.damage_clock=self.clock;self.hp-=0 if getattr(self,'unlimited_lives',False) else 1;self.invuln=3.;self.hit_clock=self.clock
            self.sound('death' if self.hp<=0 else 'hurt')
            if self.hp<=0:self.state='dead'
    def burst(self):
        x,y=self.emitter;phase=self.phase
        self.emission=.35
        self.sound(('ring','fan')[self.round%2] if phase==1 else ('spiral','needles','curtain')[self.round%3])
        if phase==1:
            if self.round%2==0:
                # Enclosure: deliberate double rings, separated by speed.
                for speed in (150,190):
                    for i in range(24):
                        a=i*math.tau/24+self.round*.17
                        self.shots.append(Shot(x,y,math.cos(a)*speed,math.sin(a)*speed,kind='pearl'))
            else:
                angle=math.atan2(self.y-y,self.x-x)
                for i in range(-4,5):
                    a=angle+i*.12
                    self.shots.append(Shot(x,y,math.cos(a)*230,math.sin(a)*230,kind='spore'))
        elif self.round%3==0:
            # Released AI: opposing curved pinwheels, each with six spokes.
            for handed in (-1,1):
                for spoke in range(6):
                    for bead in range(3 if phase==2 else 4):
                        a=spoke*math.tau/6+self.round*.23+handed*bead*.065
                        speed=170+bead*26
                        self.shots.append(Shot(x,y,math.cos(a)*speed,math.sin(a)*speed,kind='shard',turn=handed*.40))
        elif self.round%3==1:
            # Twin tendrils send faster needles toward the committed position.
            for side in (-1,1):
                sx=x+side*30;angle=math.atan2(self.y-y,self.x-sx)
                for i in range(-3,4):
                    a=angle+i*.11
                    self.shots.append(Shot(sx,y+30,math.cos(a)*285,math.sin(a)*285,kind='needle'))
        else:
            for i in range(-14,15):
                if abs(i-((self.round%5)-2))<=1:continue
                a=math.pi/2+i*.08
                for speed in ((180,235) if phase==3 else (215,)):
                    self.shots.append(Shot(x,y+20,math.cos(a)*speed,math.sin(a)*speed,kind='shard',turn=.15))
        self.round+=1
    @property
    def laser_muzzle(self):return laser_muzzle(self.x,self.y)

    def update_laser(self,dt,shoot):
        self.beam=[];self.beam_hit=False;self.laser_contact=None
        if shoot and not self.laser_held:self.sound('laser_start',.35)
        self.laser_held=shoot
        if not shoot:return
        points=rope_path(*self.laser_muzzle,-math.pi/2,self.clock,1000.)
        if self.phase==1:
            left,top,right,bottom=self.shield_hitbox
            # Both shield reserves cover the entire enclosure. Breaking one
            # must not leave an untargetable half of the visible shield.
            reserve=next(i for i,hp in enumerate(self.nodes) if hp>0)
            targets=[(reserve,(left+right)/2,(top+bottom)/2,(right-left)/2,(bottom-top)/2)]
        else:targets=[(-1,*self.boss,85,55)]
        self.beam=[points[0]]
        for a,b in zip(points,points[1:]):
            self.beam.append(b)
            for i,x,y,rx,ry in targets:
                if segment_box(*a,*b,(x-rx,y-ry,x+rx,y+ry)):
                    if i>=0:
                        self.nodes[i]=max(0,self.nodes[i]-48*dt)
                        if self.nodes[i]==0:self.sound('node_break')
                    else:self.boss_hp=max(0,self.boss_hp-96*dt)
                    self.laser_contact='shield' if i>=0 else 'flesh'
                    if i<0:self.sound('laser_hit',.10)
                    self.beam_hit=True;self.boss_flash=.08
                    return

    def step(self,dt,move=0,vertical=0,shoot=False,slide=False,slide_pressed=False,**unused):
        dt=max(0,min(.04,dt));self.clock+=dt
        self.beam=[];self.beam_hit=False;self.laser_contact=None
        if self.state in ('departure','encounter','ending'):
            self.age+=dt
            if self.state=='departure' and self.age>=DEPARTURE_DURATION:
                self.begin_encounter()
            elif self.state=='encounter' and self.age>=ENCOUNTER_DURATION:self.skip()
            elif self.state=='ending' and self.age>=ENDING_DURATION:self.state='won'
            return
        if self.state!='play':return
        self.emission=max(0,self.emission-dt)
        if self.phase>=2:self.screensaver_age+=dt
        self.phase_age+=dt;self.invuln=max(0,self.invuln-dt);self.boss_flash=max(0,self.boss_flash-dt)
        if 0<self.dash_cooldown<=dt:self.sound('thruster_ready')
        self.dash_cooldown=max(0,self.dash_cooldown-dt);self.dash_time=max(0,self.dash_time-dt)
        norm=max(1,math.hypot(move,vertical));vx=move/norm;vy=vertical/norm
        if (slide_pressed or slide and not self.was_slide) and self.dash_cooldown<=0:
            self.dash_vector=(vx,vy) if move or vertical else (0,-1)
            self.dash_time=.20;self.dash_cooldown=1.2
            self.sound('thruster')
        self.was_slide=slide
        if self.dash_time>0:vx,vy=self.dash_vector
        speed=680 if self.dash_time>0 else 260
        self.x=max(45,min(1235,self.x+vx*speed*dt));self.y=max(310,min(655,self.y+vy*speed*dt))
        self.trail=[(x,y,life-dt) for x,y,life in self.trail if life>dt]
        if self.dash_time>0:self.trail.append((self.x,self.y,.20))
        self.update_laser(dt,shoot)
        self.volley-=dt
        if self.volley<=0:
            self.burst();self.volley=1.10 if self.phase==1 else .78 if self.phase==2 else .60
            if self.round%6==0:self.volley+=.75 if self.phase==1 else .45 # short readable reset
        for b in self.shots:
            if b.turn and b.age<1.4:
                angle=b.turn*dt;co=math.cos(angle);si=math.sin(angle)
                b.vx,b.vy=b.vx*co-b.vy*si,b.vx*si+b.vy*co
            oldy=b.y;b.x+=b.vx*dt;b.y+=b.vy*dt;b.age+=dt
            if b.enemy:
                # Swept segment avoids tunnelling during fast dashes.
                dx=b.vx*dt;dy=b.vy*dt;den=dx*dx+dy*dy
                u=max(0,min(1,((self.x-(b.x-dx))*dx+(self.y-(b.y-dy))*dy)/den)) if den else 0
                if math.hypot(b.x-dx+u*dx-self.x,b.y-dy+u*dy-self.y)<11:
                    self.hurt();b.age=99
            elif self.phase==1:
                for i,hp in enumerate(self.nodes):
                    nx,ny=self.node(i)
                    if hp>0 and abs(b.x-nx)<42 and b.y-30<ny<oldy+30:
                        self.nodes[i]=max(0,hp-1.5);b.age=99;self.boss_flash=.08;break
            else:
                bx,by=self.boss
                if abs(b.x-bx)<80 and b.y-50<by<oldy+50:
                    self.boss_hp=max(0,self.boss_hp-3);b.age=99;self.boss_flash=.07
        self.shots=[b for b in self.shots if -50<b.x<1330 and -50<b.y<780 and b.age<12][-500:]
        if self.phase!=self.last_phase:
            self.sound('release' if self.phase==2 else 'enrage')
            self.last_phase=self.phase;self.phase_age=0.
            self.shots=[b for b in self.shots if not b.enemy]
            self.volley=2.
        if self.boss_hp<=0 and self.state=='play':
            self.sound('defeat')
            self.death_origin=self.boss;self.state='ending';self.age=0.;self.shots.clear();self.beam=[];self.beam_hit=False;self.laser_contact=None

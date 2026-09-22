"""Independent left/right guardians with a shared safety gate for movement attacks."""
from dataclasses import dataclass,field
import math
import tide_guardian_attacks as special
from combat import Bullet,segment_box,segment_hit

STAGE_NAMES=('THE LIVING TIDE','BLACK COAT + DEAD ORBIT')
REVEAL_DURATION=5.0
SWITCH_AT=2.0

@dataclass
class Guardian:
    kind:int
    hp:float=190.
    maximum:float=190.
    clock:float=0.
    attack:str|None=None
    warning:str|None=None
    age:float=0.
    timer:float=1.
    round:int=0
    exposed:float=0.
    flash:float=0.
    muzzle_flash:float=0.
    death_age:float=0.
    target:tuple=(640.,578.)
    end:float=640.
    hit:bool=False
    queue:list=field(default_factory=list)
    enraged:bool=False
    rage_age:float=0.
    rage_fire:float=.3
    linked:bool=False
    high_hit:bool=False
    star_lanes:tuple=(410.,640.,870.)
    star_hits:set=field(default_factory=set)

    @property
    def home(self):return 1060. if self.kind==1 else 170.
    @property
    def x(self):
        if self.attack in ('charge','slam'):
            duration=.85 if self.attack=='charge' else .7
            u=min(1,self.age/duration)
            if self.age>1.1:u=max(0,1-(self.age-1.1)/.8)
            u=u*u*(3-2*u)
            return self.home+(self.end-self.home)*u
        return self.home+math.sin(self.clock*.9)*(8 if self.kind==1 else 35)
    def bottom(self,floor):
        if self.kind==1:return floor
        if self.attack=='slam':return floor-max(0,1-self.age/.7)*150
        return floor-50-25*math.sin(self.clock*1.3)**2
    def core(self,floor):return self.x,self.bottom(floor)-160
    def muzzle(self,floor):
        return self.x+(-161 if self.kind==1 else 150),self.bottom(floor)-(225 if self.kind==1 else 239)

class GuardianView:
    """Render one actor using the same frame geometry, without mutating the fight."""
    def __init__(self,fight,actor):self.fight=fight;self.actor=actor
    def __getattr__(self,name):return getattr(self.fight,name)
    @property
    def stage(self):return self.actor.kind
    @property
    def state(self):return 'dying' if self.actor.hp<=0 else self.fight.state
    @property
    def death_age(self):return self.actor.death_age
    @property
    def guardian_x(self):return self.actor.x
    @property
    def guardian_bottom(self):return self.actor.bottom(self.floor)
    @property
    def guardian_attack(self):return self.actor.attack
    @property
    def guardian_warning(self):return self.actor.warning
    @property
    def guardian_age(self):return self.actor.age
    @property
    def guardian_pose(self):return 2 if self.actor.attack in ('charge','slam') else 1 if self.actor.attack or self.actor.warning else 0
    @property
    def guardian_flash(self):return self.actor.flash
    @property
    def guardian_muzzle_flash(self):return self.actor.muzzle_flash
    @property
    def gun_tip(self):return self.actor.muzzle(self.floor)
    @property
    def locked_aim(self):return self.actor.target
    @property
    def landing_x(self):return self.actor.end

class GuardianCombat:
    def init_guardians(self):
        self.stage=0;self.transition_age=0.;self.transition_from=0;self.stage_switched=False
        self.guardians=[];self.team_timer=6.;self.wave_reveal=0.
    @property
    def stage_name(self):return STAGE_NAMES[self.stage]
    @property
    def guardian_views(self):return [GuardianView(self,a) for a in self.guardians]
    @property
    def target_guardian(self):return next((a for a in self.guardians if a.hp>0),None)

    def begin_reveal(self):
        # Same playable deck: the defeated water dissipates in front of the duo.
        self.sound('wave_death')
        position=(self.x,self.y,self.vy,self.deck_roll,self.deck_slope)
        arena=self.rects['arena']
        self.advance_guardian()
        self.x,self.y,self.vy,self.deck_roll,self.deck_slope=position
        self.rects['arena']=arena
        self.wave_reveal=2.4
        self.guardians[0].timer=2.8;self.guardians[1].timer=3.5
        self.hazards=[];self.tide_warning=None;self.tide_followups=[]
        self.shots=[b for b in self.shots if not b.enemy]
        self.notice='';self.notice_time=0.
    def advance_guardian(self):
        self.stage=1;self.guardians=[Guardian(1,timer=1.),Guardian(2,timer=2.5)]
        self.boss_max=sum(a.maximum for a in self.guardians);self.boss_hp=self.boss_max;self.hp=min(self.max_hp,self.hp+1)
        self.open_time=0.;self.invuln=1.5;self.deck_roll=0.;self.deck_slope=0.
        self.rects['arena']=(260.,0.,760.,657.);self.x=640.;self.y=min(self.y,self.floor)
        self.stage_switched=True
    def step_reveal(self,dt):
        self.transition_age+=dt;self.clock+=dt;self.vy+=1250*dt;self.y=min(self.floor,self.y+self.vy*dt)
        if self.y>=self.floor:self.vy=0.
        self.particles=[]
        if self.transition_age>=SWITCH_AT and not self.stage_switched:self.advance_guardian()
        if self.transition_age>=REVEAL_DURATION:
            self.state='play';self.was_jump=False;self.was_slide=False;self.fire=0.
            self.notice='CROSSFIRE / DEAD ORBIT LEFT. BLACK COAT RIGHT.';self.notice_time=4.

    def projectile_hits_player(self,b,ox,oy):
        if b.kind in ('heavy_slug','orbit_bolt','pressure_ring'):
            rx,ry=(12,7) if b.kind=='heavy_slug' else (11,11) if b.kind=='orbit_bolt' else (19,20)
            l,t,r,bot=self.player_hitbox
            return segment_box(ox,oy,b.x,b.y,(l-rx,t-ry,r+rx,bot+ry))
        return super().projectile_hits_player(b,ox,oy)

    def hit_guardians(self,ax,ay,bx,by,damage):
        candidates=[]
        for a in self.guardians:
            cx,cy=a.core(self.floor)
            if a.hp>0 and segment_hit(ax,ay,bx,by,cx,cy,62):candidates.append((math.hypot(cx-ax,cy-ay),a))
        if not candidates:return False
        a=min(candidates,key=lambda p:p[0])[1]
        self.burst(bx,by,'cream',3)
        if a.hp>damage:self.sound('guardian_hit',.14)
        a.hp=max(0,a.hp-damage);a.flash=.09
        if a.hp<=0:
            self.sound('coat_death' if a.kind==1 else 'orbit_death')
            a.attack=a.warning=None;a.queue=[];a.death_age=0.
            for survivor in self.guardians:
                if survivor is not a and survivor.hp>0 and not survivor.enraged:
                    self.sound('rage_coat' if survivor.kind==1 else 'rage_orbit')
                    survivor.enraged=True;survivor.rage_age=0.
                    survivor.attack=survivor.warning=None;survivor.queue=[]
                    survivor.linked=False;survivor.exposed=0.;survivor.timer=.15;survivor.round=1
            self.shots=[b for b in self.shots if not b.enemy]

            self.notice=('BLACK COAT DOWN' if a.kind==1 else 'DEAD ORBIT DOWN')+' / FINISH THE OTHER';self.notice_time=3.
        self.boss_hp=sum(g.hp for g in self.guardians)
        if self.boss_hp<=0:
            self.state='dying';self.death_age=0.;self.shots=[];self.muzzle=0.;self.aim_target=None
            self.notice='BOTH SIGNALS LOST / UPLINK CLEAR';self.notice_time=4.
        return True

    def guardian_step(self,dt):
        self.team_timer-=dt
        living=[a for a in self.guardians if a.hp>0]
        if len(living)==2 and self.team_timer<=0 and not any(a.attack or a.warning for a in living) and not any(b.enemy for b in self.shots):
            for a in living:
                a.exposed=0;special.start(self,a,'relay' if a.kind==1 else 'stars',linked=True)
            self.team_timer=14.
        for a in self.guardians:
            a.clock+=dt;a.flash=max(0,a.flash-dt);a.muzzle_flash=max(0,a.muzzle_flash-dt);a.exposed=max(0,a.exposed-dt)
            if a.hp<=0:a.death_age+=dt;continue
            if a.enraged:
                a.rage_age+=dt
                if a.rage_age<2.8:continue
                a.exposed=max(a.exposed,.1)
                # A separate weapon cadence persists through special attacks,
                # recovery openings and the next attack's windup.
                a.rage_fire-=dt
                if a.rage_fire<=0:
                    self.sound('orbit' if a.kind==2 else 'pistol',.10)
                    a.rage_fire=.52 if a.kind==2 else .42
                    sx,sy=a.muzzle(self.floor)
                    angle=math.atan2(self.player_center[1]-sy,self.x-sx)
                    self.shots.append(Bullet(sx,sy,math.cos(angle)*360,math.sin(angle)*360,True,2.8,kind='orbit_bolt' if a.kind==2 else 'heavy_slug'))
                    a.muzzle_flash=.12
            if a.attack in ('relay','stars'):
                special.step(self,a,dt);continue
            if a.attack:
                old=a.age;a.age+=dt
                while a.queue and a.queue[0][0]<=a.age:
                    self.sound('pistol' if a.kind==1 else 'orbit',.10)
                    _,offset=a.queue.pop(0);sx,sy=a.muzzle(self.floor)
                    angle=math.atan2(a.target[1]-sy,a.target[0]-sx)+offset
                    speed=(435 if a.kind==1 else 330)*(1.15 if a.enraged else 1)
                    self.shots.append(Bullet(sx,sy,math.cos(angle)*speed,math.sin(angle)*speed,True,2.8,kind='heavy_slug' if a.kind==1 else 'orbit_bolt'))
                    a.muzzle_flash=.12
                if a.attack=='charge' and not self.sliding and abs(self.x-a.x)<95 and self.y>self.floor-125 and not a.hit:
                    hp=self.hp;self.hurt();a.hit=self.hp<hp
                if a.attack=='slam' and old<.7<=a.age:
                    self.sound('slam')
                    if abs(self.x-a.end)<85 and self.y>self.floor-150:self.hurt()
                    for direction in (-1,1):self.shots.append(Bullet(a.end,self.floor-22,direction*375,0,True,3.,kind='pressure_ring'))
                    self.burst(a.end,self.floor,'gold',25)
                if a.age>=(1.9 if a.attack in ('charge','slam') else .9):
                    a.attack=None;a.exposed=1.7 if a.enraged else 2.4;a.timer=0 if a.enraged else .45
                continue
            if a.exposed>0 and not a.enraged:continue
            a.timer-=dt
            if a.timer>0:continue
            if a.warning:
                a.attack=a.warning;a.warning=None;a.age=0.;a.hit=False;a.high_hit=False;a.star_hits.clear();a.round+=1
                if a.attack in ('charge','slam','relay'):self.sound({'charge':'dash','slam':'jet','relay':'relay'}[a.attack])
                if a.attack=='pistol':a.queue=[(i*.12,(i%3-1)*.12) for i in range(6)] if a.enraged else [(i*.18,0.) for i in range(4)]
                elif a.attack=='orbit':a.queue=[(i*.12,(i-2)*.23) for i in range(5)] if a.enraged else [(i*.15,(i-1)*.32) for i in range(3)]
                continue
            kind=('pistol','relay','charge')[a.round%3] if a.kind==1 else ('orbit','stars','slam')[a.round%3]
            # No charge/slam alongside bullets or another movement tell. Ranged
            # crossfire can overlap; both enemies commit to the previewed target.
            other=[g for g in self.guardians if g is not a and g.hp>0]
            maneuver=any(g.attack in ('charge','slam','relay','stars') or g.warning in ('charge','slam','relay','stars') for g in other)
            if maneuver:continue
            if not a.enraged and kind in ('charge','slam','relay','stars') and (any(b.enemy for b in self.shots) or any(g.attack or g.warning for g in other)):continue
            if kind in ('relay','stars'):
                special.start(self,a,kind);continue
            a.warning=kind;a.timer=.85 if a.enraged else 1.05;a.target=self.player_center
            a.end=max(360,min(910,self.x)) if kind=='slam' else max(320,min(750,self.x-80))
            self.notice_time=0.

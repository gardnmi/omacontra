"""Mobile Foundry barrage encounter and deterministic Quattro rescue."""
import math
from wyrm_scene import point as dragon_point,MOUTH,EYES
from dataclasses import dataclass
from combat import Fight, Bullet, segment_hit, segment_box

CAR_ENTRY=4.25
IMPACT=5.35
EJECTION=IMPACT+.10
EXPLOSION=IMPACT+.65
RESCUE_END=13.5
RESCUE_CAR_SCALE=2/3
RESCUE_CAR_X=624-200*RESCUE_CAR_SCALE
OPENING=('wisps',)
SHOULDER_CHARGE=2.
SHOULDER_PERIOD=18.
SHOULDER_FAST_PERIOD=13.
LAVA_RISE_TIME=7.
LAVA_TOP=560.
LAVA_START=780.
DISARM_DURATION=1.35
FORGE_WINDUP={'breath':1.15,'updraft':1.15,'wisps':1.0,'fire':1.15,'fan':1.0,'flood':.85,'rush':.85}

def rope_path(sx,sy,angle,clock,length=1300.):
    """Shared elastic centerline for both owners; collisions use these points."""
    dx,dy=math.cos(angle),math.sin(angle)
    points=[]
    for i in range(81):
        u=i/80;d=u*length
        bend=math.sin(u*math.pi)*(math.sin(u*12-clock*10)*27+math.sin(u*23+clock*7)*9)
        points.append((sx+dx*d-dy*bend,sy+dy*d+dx*bend))
    return points

@dataclass
class Hazard:
    kind: str
    x: float
    age: float=0.
    hit: bool=False
    y: float=550.
    angle: float=2.6
    origin: tuple | None=None
    width: float=24.

@dataclass
class Bolt:
    x: float
    y: float
    vx: float
    vy: float
    kind: str='curtain'
    age: float=0.
    life: float=5.
    radius: float=7.

@dataclass
class Pickup:
    x: float
    y: float
    kind: str
    age: float=0.

class Foundry(Fight):
    sound_bank="foundry"

    def sound(self,name,cooldown=0.):
        if self.clock-self.sfx_last.get(name,-999)<cooldown:return
        self.sfx_last[name]=self.clock
        self.sfx_events.append(name);self.sfx_events=self.sfx_events[-32:]

    def __init__(self,seed=None):
        self.support=None
        super().__init__(seed)
        self.rects['arena']=(30.,0.,1220.,657.)
        self.x=210.;self.y=self.floor;self.hp=6;self.max_hp=self.hp
        self.boss_hp=self.boss_max=440.;self.attack_timer=math.inf
        self.boss_x=640.;self.boss_start=640.;self.rush_age=-1.
        self.forge_timer=1.6;self.forge_warning=None;self.forge_round=0
        self.forge_pose=0;self.forge_action=0.;self.mark=400.;self.attack_floor=630.
        self.hazards=[];self.bolts=[];self.emit_queue=[];self.pickups=[]
        self.vents=[18.,18.];self.vent_flash=[0.,0.]
        self.power_time=0.;self.power_kind=None;self.collected=0
        self.rescue_age=0.;self.rescue_start_x=self.x;self.rescue_start_boss_x=1020.
        self.notice='';self.notice_time=0.
        # A climbable circuit: left stairs, overhead crossing, right stairs.
        self.platforms=((250.,445.,535.),(140.,320.,435.),(225.,405.,335.),
                        (440.,625.,170.),(655.,840.,170.),(875.,1055.,335.),
                        (960.,1140.,435.),(835.,1030.,535.))
        self.pickup_spot=(345.,516.)
        self.combat_age=0.;self.disarm_age=0.;self.drop_origin=(0.,0.)
        self.mount_max=135.;self.mount_hp=self.mount_max;self.mount_flash=0.
        self.shoulder_heat=0.;self.shoulder_aim=math.pi/2;self.enemy_beam=[]
        self.locked_target=(self.x,self.y-35)
        self.sweep_age=0.;self.lava_age=None;self.rescue_start_y=self.y
        self.laser_art='foundry-throat-weapon.png'
        self.laser=False;self.laser_spawned=False;self.beam=[];self.beam_hit=False
        self.armor_flash=0.;self.walk_distance=0.
        self.ledge_warning=None;self.ledge_timer=1.6

    def update_ledge_pressure(self,dt):
        if not self.laser:return
        if self.ledge_warning:
            x,y,age,width=self.ledge_warning;age+=dt
            if age>=1.1:
                self.hazards.append(Hazard('updraft',x,y=y,width=width))
                self.sound('eye_lance',.2)
                self.ledge_warning=None;self.ledge_timer=1.25
            else:self.ledge_warning=(x,y,age,width)
        else:
            self.ledge_timer-=dt
            if self.ledge_timer<=0 and self.y>=self.floor-2:
                left,right,top=self.support or (self.x-55,self.x+55,self.floor)
                self.ledge_warning=((left+right)/2,top,0.,(right-left)/2)
                self.sound('eye_charge',.2)

    @property
    def camera_y(self):
        # Follow high jumps instead of colliding with an invisible ceiling.
        # Keep headroom above the sprite, with the HUD fixed in screen space.
        return max(0.,190-self.y) if self.state in ('play','dead','disarm') else 0.

    def screen_to_world(self,point):
        if point is None:return None
        return point[0],point[1]-self.camera_y

    @property
    def shielded(self):return True
    @property
    def phase(self):return 1 if self.boss_hp>self.boss_max*.65 else 2 if self.boss_hp>self.boss_max*.3 else 3
    @property
    def core(self):return self.dragon_point(*MOUTH)

    def dragon_point(self,x,y):
        return dragon_point(self,x,y)
    @property
    def upper_offset(self):
        crouch=7*math.sin(self.clock*1.6)**2
        if self.forge_warning=='rush':crouch+=14*(1-min(1,self.forge_timer/.7))
        return (math.sin(self.clock*47)*2 if self.beam_hit else 0),crouch
    @property
    def cannon(self):
        # Both breath weapons originate inside the illustrated dragon's jaws.
        return self.shoulder_mount
    @property
    def shoulder_mount(self):
        return self.dragon_point(*MOUTH)
    @property
    def shoulder_speed(self):
        damage=1-max(0,self.mount_hp)/self.mount_max
        turns=max(0,math.floor((self.shoulder_aim-math.pi/2+1e-9)/math.tau))
        period=max(SHOULDER_FAST_PERIOD,SHOULDER_PERIOD-2*turns-5*damage)
        return math.tau/period
    @property
    def shoulder_muzzle(self):
        x,y=self.shoulder_mount
        return x,y
    @property
    def mount_target(self):
        x,y=self.shoulder_mount
        return x,y
    @property
    def mount_exposed(self):return self.mount_hp>0 and self.shoulder_heat>0
    @property
    def dropped_weapon(self):
        u=min(1,self.disarm_age/1.05)
        x,y=self.drop_origin
        return x+(self.pickup_spot[0]-x)*u,y+(self.pickup_spot[1]-y)*u-95*math.sin(u*math.pi),-.4+u*math.tau

    def fire_path(self,h):
        sx,sy=h.origin if h.origin is not None else self.cannon
        if h.kind=='flood':return [(sx,sy),(h.x,630.)]
        angle=math.atan2(h.y-sy,h.x-sx)
        return [(sx,sy),(sx+1400*math.cos(angle),sy+1400*math.sin(angle))]

    @property
    def lava_surface(self):
        if self.lava_age is None:return None
        u=min(1,self.lava_age/LAVA_RISE_TIME)
        # Enter from below the viewport; pickup must not spawn a full ground layer.
        return LAVA_START-(LAVA_START-LAVA_TOP)*u

    def shoulder_path(self):
        # Angle is integrated rather than derived from damage, so landing a
        # shot accelerates the rotor without teleporting the beam forward.
        return rope_path(*self.shoulder_muzzle,self.shoulder_aim,self.clock)

    def update_shoulder(self,dt):
        self.enemy_beam=[]
        if self.mount_hp<=0:return
        previous=self.sweep_age
        self.sweep_age+=dt
        # Continuous laser is intentionally quiet; no repeating synthetic pulses.
        active_dt=max(0,self.sweep_age-max(previous,SHOULDER_CHARGE))
        self.shoulder_aim+=self.shoulder_speed*active_dt
        points=self.shoulder_path()
        if self.sweep_age<SHOULDER_CHARGE:return
        self.enemy_beam=points;self.shoulder_heat=1.
        if self.dash_time<=0 and self.path_hits(points,8):self.hurt()

    def update_lava(self,dt):
        if self.lava_age is None:return
        self.lava_age+=dt
        if self.player_hitbox[3]>self.lava_surface:self.hurt()

    def path_hits(self,points,radius):
        l,t,r,b=self.player_hitbox
        return any(segment_box(*a,*z,(l-radius,t-radius,r+radius,b+radius))
                   for a,z in zip(points,points[1:]))

    def vent_position(self,i):return self.boss_x-18+i*90,215.+i*25
    def move_enemies(self,dt):pass

    @property
    def floor(self):
        return self.support[2] if self.support is not None else super().floor

    def hit_target(self,ax,ay,bx,by,damage):
        if self.state!='play':return False
        if self.mount_hp>0 and segment_hit(ax,ay,bx,by,*self.mount_target,36):
            self.sound("core_hit",.15)
            self.mount_flash=.12;self.burst(bx,by,'gold',4)
            if self.mount_exposed:
                self.mount_hp=max(0,self.mount_hp-damage)
                if self.mount_hp==0:self.begin_disarm()
            return True
        # The Warden stands behind the traversal plane. While its mouth is
        # active, body and legs must not eat bullets aimed through it.
        if self.mount_hp>0:return False
        if not segment_box(ax,ay,bx,by,(self.boss_x-80,310,self.boss_x+125,630)):return False
        self.armor_flash=.09;self.burst(bx,by,'cream',3)
        return True

    def begin_disarm(self):
        self.sound("disarm")
        self.drop_origin=self.mount_target;self.disarm_age=0.;self.state='disarm'
        self.mount_hp=0.;self.enemy_beam=[];self.shoulder_heat=0.
        self.hazards.clear();self.bolts.clear();self.emit_queue.clear();self.shots.clear()
        self.forge_warning=None;self.forge_timer=2.;self.rush_age=-1.
        self.slide_time=self.dash_time=0.;self.moving=self.duck=False;self.muzzle=0.
        self.burst(*self.drop_origin,'gold',28)

    def update_pickup(self):
        if not self.pickups:return
        p=self.pickups[0];l,t,r,b=self.player_hitbox
        if l-18<p.x<r+18 and t-16<p.y<b+16:
            self.pickups.clear();self.laser=True;self.laser_spawned=True
            self.sound("pickup");self.sound("lava")
            self.lava_age=0.
            self.power_kind='laser';self.collected=1;self.fire=1.
            self.burst(p.x,p.y,'gold',20)

    def update_laser(self,dt,shoot):
        self.beam=[];self.beam_hit=False
        if not self.laser or not shoot:return
        sx,sy=self.muzzle_position
        target=self.aim_target or (sx+self.facing*1300,sy)
        angle=math.atan2(target[1]-sy,target[0]-sx)
        for x,y in rope_path(sx,sy,angle,self.clock):
            self.beam.append((x,y))
            if self.boss_x-125<x<self.boss_x+125 and 210<y<630:
                self.beam_hit=True;self.boss_flash=.09
                self.boss_hp=max(0,self.boss_hp-dt*19)
                self.burst(x,y,'gold',2)
                if self.boss_hp==0:self.begin_rescue()
                break

    def begin_rescue(self):
        if self.state!='play':return
        self.sound('defeat')
        self.beam=[];self.enemy_beam=[];self.support=None
        self.state='rescue';self.rescue_age=0.;self.rescue_start_x=self.x;self.rescue_start_y=self.y
        self.rescue_start_boss_x=self.boss_x
        self.shots.clear();self.hazards.clear();self.bolts.clear();self.emit_queue.clear();self.pickups.clear()
        self.forge_warning=None;self.muzzle=0.;self.slide_time=self.dash_time=0.
        self.ledge_warning=None
        self.moving=self.duck=False;self.notice='';self.notice_time=0.

    def emit(self,kind,index):
        heavy=kind=='breath'
        self.sound('eye_lance' if heavy else 'eye_shot')
        sx,sy=self.dragon_point(*EYES[(self.forge_round-1)%2])
        tx,ty=self.locked_target
        aim=math.atan2(ty-sy,tx-sx)
        count=3 if heavy else 5
        spacing=.50 if heavy else (.40 if self.forge_round%2 else .46)
        for i in range(count):
            a=aim+(i-(count-1)/2)*spacing
            speed=260 if heavy else 245
            self.bolts.append(Bolt(sx,sy,math.cos(a)*speed,math.sin(a)*speed,
                                  'heavy' if heavy else 'wisp',life=5.5,radius=12 if heavy else 9))

    def step(self,dt,**controls):
        dt=min(.04,max(0.,dt))
        if self.state in ('rescue','won'):
            if self.state=='rescue':
                old_age=self.rescue_age
                self.rescue_age=min(RESCUE_END,self.rescue_age+dt);self.clock+=dt
                if old_age<EXPLOSION<=self.rescue_age:self.sound("rescue_blast")
                if self.lava_age is not None:self.lava_age+=dt
                u=min(1,self.rescue_age/1.2);u=u*u*(3-2*u)
                self.boss_x=self.rescue_start_boss_x
                if self.rescue_age>=RESCUE_END:self.state='won'
            return
        if self.state=='disarm':
            self.disarm_age+=dt;self.clock+=dt
            self.vy+=1250*dt;self.y=min(self.floor,self.y+self.vy*dt)
            if self.y>=self.floor:self.vy=0
            if self.disarm_age>=DISARM_DURATION:
                self.state='play';self.pickups=[Pickup(*self.pickup_spot,'laser')]
                self.invuln=max(self.invuln,.5);self.was_jump=self.was_slide=False
            return
        self.mount_flash=max(0,self.mount_flash-dt)
        self.shoulder_heat=max(0,self.shoulder_heat-dt)
        self.enemy_beam=[]
        self.armor_flash=max(0,self.armor_flash-dt)
        old_clock=self.clock
        old_y=self.y
        if self.support and not self.support[0]-8<=self.x<=self.support[1]+8:self.support=None
        if self.laser:self.fire=1. # Keep inherited aiming/animation, suppress discrete bullets.
        super().step(dt,**controls)
        if self.state!='play':return
        if math.floor((old_clock-4.15)/8.7)!=math.floor((self.clock-4.15)/8.7) and self.clock>4.15:self.sound('thunder',8.)
        if self.vy>=0:
            for platform in sorted(self.platforms,key=lambda p:p[2]):
                left,right,top=platform
                if left-8<=self.x<=right+8 and old_y<=top and self.y>=top:
                    if old_y<top-1:self.landing_age=.18
                    self.support=platform;self.y=top;self.vy=0
                    self.jumps_used=0;self.dash_used=False;break
        self.combat_age+=dt
        self.update_pickup()
        self.update_lava(dt)
        if self.state!='play':return
        self.update_ledge_pressure(dt)
        self.update_laser(dt,controls.get('shoot',False) and getattr(self,'hit_age',None) is None)
        if self.state!='play':return
        # The Warden stays planted at the center throughout both phases.
        self.update_shoulder(dt)
        if self.state!='play':return
        for b in self.bolts:
            ox,oy=b.x,b.y;b.age+=dt;b.life-=dt
            b.x+=b.vx*dt;b.y+=b.vy*dt
            if b.kind=="wisp":
                bend=(math.sin(b.age*3)-math.sin((b.age-dt)*3))*12
                speed=max(1,math.hypot(b.vx,b.vy))
                b.x-=b.vy/speed*bend;b.y+=b.vx/speed*bend
            l,t,r,bot=self.player_hitbox
            if segment_box(ox,oy,b.x,b.y,(l-b.radius,t-b.radius,r+b.radius,bot+b.radius)):
                if self.dash_time<=0:
                    self.sound('storm_hit',.2);self.hurt()
                b.life=0
        self.bolts=[b for b in self.bolts if b.life>0 and -40<b.x<1320 and -40<b.y<720][-100:]
        for h in self.hazards:
            h.age+=dt
            if h.kind in ('breath','fire'):
                if .16<h.age<.65 and self.dash_time<=0 and self.path_hits(self.fire_path(h),14):self.hurt()
            elif h.kind=='updraft':
                l,t,r,b=self.player_hitbox
                if .25<h.age<.85 and l<h.x+h.width and r>h.x-h.width and b>h.y-160 and t<h.y and self.dash_time<=0:self.hurt()
            elif h.kind=='flood':
                if .16<h.age<.9 and self.dash_time<=0 and self.path_hits(self.fire_path(h),12):self.hurt()
                if .7<h.age<2.5:
                    l,t,r,b=self.player_hitbox
                    if l<h.x+180 and r>h.x-180 and b>585:self.hurt()
        self.hazards=[h for h in self.hazards if h.age<{'breath':.8,'fire':.8,'updraft':1.05,'flood':2.9}[h.kind]]
        for due,kind,index in list(self.emit_queue):
            if self.clock>=due:self.emit(kind,index);self.emit_queue.remove((due,kind,index))
        if any(h.width<=30 for h in self.hazards) or self.emit_queue or self.rush_age>=0:return
        self.forge_timer-=dt
        if self.forge_timer>0:return
        if self.forge_warning:
            kind=self.forge_warning;self.forge_warning=None
            if kind in ('breath','fire'):
                self.emit_queue=[(self.clock,'breath',0)]
            elif kind=='updraft':
                self.sound('gust');self.hazards.append(Hazard('updraft',self.mark,y=self.attack_floor))
            elif kind=='flood':self.hazards.append(Hazard('flood',self.mark))
            elif kind in ('wisps','fan'):self.emit_queue=[(self.clock,kind,0)]
            else:self.rush_age=0.;self.boss_start=self.boss_x
            self.forge_round+=1;self.forge_timer=.65 if self.mount_hp>0 else .75
        else:
            # Expired volleys never gate the next windup. Every pause is short
            # and visible as a weapon charge, not waiting for offscreen bullets.
            pattern=OPENING if not self.laser else ('wisps','breath','updraft')
            kind=pattern[self.forge_round%len(pattern)]
            self.forge_warning=kind
            self.sound('eye_charge' if kind!='updraft' else 'gust')
            self.forge_timer=FORGE_WINDUP[kind]
            self.locked_target=self.player_center
            self.mark=self.x;self.attack_floor=self.floor
            self.mark=max(55,min(1225,self.x))


def rescue_beat(age):
    if age < 1.25: return 'stagger'
    if age < CAR_ENTRY: return 'super'
    if age < IMPACT: return 'flight'
    if age < EJECTION: return 'impact'
    if age < EXPLOSION: return 'eject'
    if age < 9.1: return 'explode'
    return 'aftermath'


def rescue_car(age):
    """Position, angle: one continuous flight into the furnace's chest."""
    u=max(0.,min(1.,(age-CAR_ENTRY)/(IMPACT-CAR_ENTRY)))
    return -220+(RESCUE_CAR_X+220)*u, 460-175*math.sin(u*math.pi)-90*u, -.18+.35*u


def rescue_tobi(age):
    """Ballistic ejection leftward, then a grounded recovery; survives blast."""
    t=max(0.,age-EJECTION)
    if t < 1.55-1e-9:
        start=RESCUE_CAR_X-52*RESCUE_CAR_SCALE
        return start+(286.75-start)*t/1.55, 330-350*t+(842.5/2.4025)*t*t, -math.tau*(t/1.55)**2*(3-2*t/1.55), 'air'
    if t < 2.2:
        u=(t-1.55)/.65
        return 286.75-10*u, 630., 0., 'land'
    return 276.75,630.,0.,'stand'

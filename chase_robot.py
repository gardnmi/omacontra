"""The detached trailer's second life: a mechanical heart on the highway."""
import math
from combat import Bullet

TRANSFORM_DURATION=3.4
ROBOT_HEALTH=120.
CYCLE=7.5
ROBOT_SCALE=2.35
RAMP_VELOCITY=1250.
RAMP_WIDTH=280
RAMP_HEIGHT=100

def smooth(t):
    t=max(0,min(1,t));return t*t*(3-2*t)

def heart_open(f):
    if f.state=='finisher':return 1.
    if f.encounter_phase!=2 or f.state!='play':return 0.
    return smooth(f.core_open/.2) if f.jump_height>220 else 0.

def robot_pose(f):
    # Feet remain on the road; only suspension and the chest settle vertically.
    return f.boss_x+125,590.,math.sin(f.robot_age*1.8)*2

def cannon_charge(f):
    phase=f.robot_age%CYCLE
    return max((smooth((phase-(beat-.7))/.7) if beat-.7<=phase<beat else 0) for beat in (1.,3.3))

def body_motion(f):
    # Continuous planted-foot lean and compression: no separated limb slices.
    charge=cannon_charge(f)
    recoil=max((max(0,1-(f.robot_age%CYCLE-beat)/.45) if 0<=f.robot_age%CYCLE-beat<.45 else 0) for beat in (1.,3.3))
    return math.sin(f.robot_age*1.25)*.045+charge*.032-recoil*.040, 1+math.sin(f.robot_age*1.8)*.016-charge*.026

def body_point(f,dx,dy):
    x,y,_=robot_pose(f);lean,stretch=body_motion(f)
    return x+(dx+lean*dy)*ROBOT_SCALE,y+dy*stretch*ROBOT_SCALE

def heart_target(f):
    return body_point(f,-22,-330)

def cannon_target(f):
    return body_point(f,-91,-205)


def detach(f):
    f.sound('truck_break')
    f.state='transform';f.transform_age=0.;f.trailer_done=True
    f.trailer_origin=f.boss_x+272;f.trailer_x=f.trailer_origin
    f.trailer_warning=0.;f.warning=None;f.ram_time=0.;f.notice_time=0
    f.shots=[];f.rocket_queue=[];f.drones=[];f.ramp_x=None
    f.mortar_targets=[];f.road_blasts=[];f.obstacles=[]

def transform_step(f,dt):
    old=f.transform_age
    f.transform_age+=dt;f.trailer_age=f.transform_age
    # Match panel release and planted locking impact in chase_robot_art.
    if old<.65<=f.transform_age:f.sound('unfold')
    if old<2.5<=f.transform_age:f.sound('lock')
    f.distance+=dt*700
    f.trailer_x=f.trailer_origin+95*smooth(f.transform_age/.85)
    f.x+=(300-f.x)*min(1,dt*5)
    f.vy-=1250*dt;f.jump_height=max(0,f.jump_height+f.vy*dt);f.y=590-f.jump_height
    if f.transform_age>=TRANSFORM_DURATION:
        f.state='play';f.encounter_phase=2;f.robot_age=0.;f.trailer_x=None
        f.boss_x=850.;f.boss_hp=f.boss_max=ROBOT_HEALTH;f.parts=[0.,0.,0.]
        f.invuln=max(f.invuln,1.);f.attack_timer=1.;f.next_ramp=f.clock+1.5
        f.core_open=0.;f.finisher_cooldown=0.;f.notice_time=0;f.reinforce_at=f.clock+.8

def robot_step(f,dt):
    old=f.robot_age;f.robot_age+=dt
    if f.boss_hp<=12 and f.finisher_cooldown<=0:f.begin_finisher();return
    # One ground shredder per cycle, emitted from the ankle mechanism. It is
    # jumpable, spaced after the downward volleys.
    beat=5.5
    if math.floor((old-beat)/CYCLE)!=math.floor((f.robot_age-beat)/CYCLE) and f.jump_height<50:
        f.sound('mine')
        x,y,_=robot_pose(f)
        f.shots.append(Bullet(x-95*ROBOT_SCALE,562,-450,0,True,5,kind='tire_roller'))
        f.robot_muzzle=.18
    # Three descending rays form broad steering corridors. Alternate the
    # gaps instead of tracking the driver and closing an escape mid-flight.
    for beat,lanes in ((1.,(-120,340,800)),(3.3,(100,560,1020))):
        if math.floor((old-beat)/CYCLE)!=math.floor((f.robot_age-beat)/CYCLE):
            f.sound('cannon')
            x,y=cannon_target(f)
            for tx in lanes:
                duration=1.75
                f.shots.append(Bullet(x,y,(tx-x)/duration,(550-y)/duration,True,3.2,kind='robot_shell'))
            f.robot_muzzle=.22
    f.robot_muzzle=max(0,f.robot_muzzle-dt)

"""Quattro highway encounter. Pure simulation; no desktop dependencies."""
import math
import random
from omacontra.stages.highway import chase_robot
from omacontra.stages.reaper.combat import Bullet, Particle, segment_box, W

class Chase:
    sound_bank='chase'
    def __init__(self,seed=8):
        self.sfx_events=[];self.sfx_last={};self.heart_was_open=False
        self.rng=random.Random(seed);self.clock=0.;self.state='play';self.hp=6;self.max_hp=self.hp;self.invuln=2.
        self.x=310.;self.y=590.;self.vy=0.;self.jump_height=0.;self.was_jump=False;self.was_boost=False
        self.boost=0.;self.boost_cooldown=0.;self.fire=0.;self.muzzle=0.;self.aim_target=None
        self.shots=[];self.particles=[];self.drones=[];self.obstacles=[];self.distance=0.
        self.boss_x=820.;self.boss_max=300.;self.boss_hp=self.boss_max;self.parts=[60.,80.,160.];self.attack_timer=.6
        self.warning=None;self.warning_time=0.;self.attack_number=0;self.ram_time=0.
        self.next_drone=4.;self.next_barrier=11.;self.barrier_warning=0.
        self.notice='TOBI: HE IS RIGHT BEHIND US.';self.notice_time=4.
        self.death_age=0.;self.impact=0.;self.destroyed=0
        self.mortar_targets=[];self.road_blasts=[];self.rocket_queue=[];self.reinforce_at=8.
        self.death_blasts=[];self.death_origin=820.
        self.ramp_x=None;self.ramp_launched=False;self.ramp_flight=False;self.wreck_age=0.;self.ramp_warning=0.;self.next_ramp=7.;self.core_open=0.
        self.trailer_age=0.;self.trailer_origin=0.;self.trailer_x=None;self.trailer_warning=0.;self.trailer_done=False;self.trailer_hit=False
        self.encounter_phase=1;self.transform_age=0.;self.robot_age=0.;self.robot_muzzle=0.
        self.finisher_phase='prompt';self.finisher_age=0.;self.finisher_timer=2.5;self.was_shoot=False;self.finisher_cooldown=0.
    @property
    def camera_y(self):
        if self.encounter_phase!=2:return 0.
        rise=max(0,self.jump_height-80)
        return rise*rise/200 if rise<100 else rise-50
    def screen_to_world(self,point):
        return (point[0],point[1]-self.camera_y) if point is not None else None

    @property
    def boss_active(self):return True
    @property
    def road_speed(self):return 1150 if self.boost>0 else 700
    @property
    def part(self):return next((i for i,hp in enumerate(self.parts) if hp>0),2)
    @property
    def target(self):
        if self.encounter_phase==2:return chase_robot.heart_target(self)
        return ((self.boss_x+180,565),(self.boss_x+145,390),(self.boss_x+239,472))[2 if self.state=='finisher' else self.part]
    def component_target(self,index):
        return ((self.boss_x+180,565),(self.boss_x+145,390),(self.boss_x+239,472))[index]
    @property
    def core_vulnerable(self):return chase_robot.heart_open(self)>.8 if self.encounter_phase==2 else self.core_open>0
    def attack_enabled(self,kind):
        return not ((kind=='roller' and self.parts[0]<=0) or
                    (kind in ('spread','mortar') and self.parts[1]<=0))
    def detach_trailer(self):
        chase_robot.detach(self)
    @property
    def player_center(self):return self.x+15,self.y-48
    @property
    def car_box(self):return self.x-102,self.y-81,self.x+117,self.y-8
    @property
    def gun_pivot(self):return self.x+51,self.y-96
    @property
    def barrel_length(self):return 74.52
    @property
    def gun_angle(self):
        x,y=self.gun_pivot
        return math.atan2(self.aim_target[1]-y,self.aim_target[0]-x) if self.aim_target else -.12
    @property
    def muzzle_position(self):
        x,y=self.gun_pivot;a=self.gun_angle
        return x+math.cos(a)*self.barrel_length,y+math.sin(a)*self.barrel_length
    def burst(self,x,y,n=12,color='gold'):
        for _ in range(n):
            a=self.rng.random()*math.tau;v=self.rng.uniform(40,200)
            self.particles.append(Particle(x,y,math.cos(a)*v,math.sin(a)*v,self.rng.uniform(.2,.65),color,self.rng.uniform(2,5)))
    def sound(self,name,cooldown=0.,position=None):
        # Off-screen impacts/spawns should not masquerade as nearby dangers.
        if position is not None:
            x,y=position
            if not (-60<x<1340 and -80<y+self.camera_y<800):return
        if self.clock-self.sfx_last.get(name,-999)<cooldown:return
        self.sfx_last[name]=self.clock
        self.sfx_events.append(name);self.sfx_events=self.sfx_events[-32:]

    def hurt(self):
        if self.invuln>0 or self.state!='play':return
        self.damage_taken=getattr(self,'damage_taken',0)+1;self.damage_clock=self.clock;self.hp-=0 if getattr(self,'unlimited_lives',False) else 1;self.invuln=3.;self.hit_clock=self.clock;self.burst(*self.player_center,22,'red')
        self.sound('car_wreck' if self.hp<=0 else 'car_hit')
        if self.hp<=0:
            self.state='dead';self.wreck_age=0.;self.wreck_origin=(self.x,self.y)
            self.shots=[];self.muzzle=0.;self.boost=0.;self.notice_time=0.
            self.burst(self.x,self.y-40,65,'gold')
    def spawn_drone(self):
        self.drones.append({'x':1330.,'y':(min(250.,self.y-160) if self.encounter_phase==2 else 250.)+self.rng.uniform(-45,90),'hp':4,'fire':2.,'age':0.,'lock':None})
    def attack(self,kind):
        if not self.attack_enabled(kind):return
        if kind=='ram':self.sound('ram');self.ram_time=2.4
        elif kind=='roller':self.sound('mine');self.shots.append(Bullet(self.boss_x,559,-400,0,True,4,kind='tire_roller'))
        elif kind=='drones':
            for _ in range(1+(self.part>0)):
                if len(self.drones)<3:self.spawn_drone()
        elif kind=='mortar':
            self.sound('mortar')
            if not self.mortar_targets:self.mortar_targets=[self.x]
            sx,sy=self.boss_x+145,380
            for tx in self.mortar_targets:
                flight=1.5
                self.shots.append(Bullet(sx,sy,(tx-sx)/flight,(570-sy-.5*520*flight*flight)/flight,True,4,kind='truck_mortar'))
        else:
            self.sound('rockets')
            sx,sy=self.boss_x+225,392;px,py=self.player_center
            a=math.atan2(py-sy,px-sx)
            for offset in (-.60,0,.60):self.shots.append(Bullet(sx,sy,math.cos(a+offset)*285,math.sin(a+offset)*285,True,5,kind='truck_rocket'))
            if self.part>0:self.rocket_queue.append((self.clock+.4,sx,sy,a))
    @property
    def roof_progress(self):
        if self.state!='finisher' or self.finisher_phase in ('settle','prompt'):return 0.
        return min(1,self.finisher_age/.65) if self.finisher_phase=='climb' else 1.
    @property
    def bazooka_pivot(self):return self.x+52,self.y-178
    def begin_finisher(self):
        if self.encounter_phase==2 and not self.heart_was_open:self.sound('heart')
        self.invuln=0.;self.muzzle=0.;self.boost=0.;self.notice_time=0.;self.ram_time=0.;self.state='finisher';self.finisher_phase='settle';self.finisher_age=0.;self.finisher_timer=2.5
        self.shots=[];self.rocket_queue=[];self.drones=[];self.mortar_targets=[];self.road_blasts=[];self.warning=None
    def begin_destruction(self):
        self.sound('robot_break')
        self.boss_hp=0.;self.parts=[0.,0.,0.];self.state='dying';self.death_origin=self.boss_x
        self.shots=[];self.rocket_queue=[];self.drones=[];self.mortar_targets=[];self.road_blasts=[];self.warning=None
        self.death_age=0.;self.vy=0.;self.boost=0.;self.notice='TOBI: HOLD MY WINE.';self.notice_time=999
    def fail_finisher(self):
        self.state='play';self.shots=[];self.finisher_cooldown=3.;self.attack_timer=1.8
        self.notice='MISSED THE OPENING / EXPOSE THE CORE AGAIN';self.notice_time=2.
    def step_finisher(self,dt,jump,shoot,aim):
        self.distance+=dt*700;self.finisher_age+=dt;self.aim_target=aim
        if self.encounter_phase==2:
            self.jump_height+=(500-self.jump_height)*min(1,dt*4);self.vy=0
        else:
            self.jump_height=max(0,self.jump_height+self.vy*dt);self.vy-=1250*dt
        if self.jump_height==0:self.vy=0
        self.y=590-self.jump_height
        if self.finisher_phase=='settle':
            self.x+=(300-self.x)*min(1,dt*6)
            self.boss_x+=(850-self.boss_x)*min(1,dt*6)
            if self.finisher_age>=.9:
                self.finisher_phase='prompt';self.finisher_age=0.;self.finisher_timer=2.5
        elif self.finisher_phase=='prompt':
            self.finisher_timer-=dt
            if jump and not self.was_jump:self.finisher_phase='climb';self.finisher_age=0.
            elif self.finisher_timer<=0:self.fail_finisher()
        elif self.finisher_phase=='climb':
            if self.finisher_age>=.65:self.finisher_phase='aim';self.finisher_timer=6.
        elif self.finisher_phase=='aim':
            self.finisher_timer-=dt
            if shoot and not self.was_shoot:
                self.sound('finisher')
                x,y=self.bazooka_pivot;tx,ty=aim or self.target;a=math.atan2(ty-y,tx-x)
                self.shots=[Bullet(x+math.cos(a)*45,y+math.sin(a)*45,math.cos(a)*800,math.sin(a)*800,kind='finisher_rocket')]
                self.finisher_phase='flight';self.finisher_age=0.;self.burst(x,y,20)
            elif self.finisher_timer<=0:self.fail_finisher()
        else:
            for b in self.shots:
                ox,oy=b.x,b.y;b.x+=b.vx*dt;b.y+=b.vy*dt
                tx,ty=self.target
                if segment_box(ox,oy,b.x,b.y,(tx-50,ty-45,tx+50,ty+45)):
                    self.begin_destruction();break
            if self.state=='finisher' and self.finisher_age>2:self.fail_finisher()
        self.was_jump=jump;self.was_shoot=shoot

    def step(self,dt,move=0,jump=False,duck=False,shoot=False,aim=None,aim_up=False,slide=False,slide_pressed=False):
        dt=max(0,min(.04,dt));self.clock+=dt
        for p in self.particles:p.x+=p.vx*dt;p.y+=p.vy*dt;p.vy+=260*dt;p.life-=dt
        self.particles=[p for p in self.particles if p.life>0][-450:]
        self.road_blasts=[(x,age+dt) for x,age in self.road_blasts if age+dt<.6]
        if self.state=='dead':
            self.wreck_age+=dt;return
        if self.state=='transform':chase_robot.transform_step(self,dt);return
        if self.state=='finisher':self.step_finisher(dt,jump,shoot,aim);return
        if self.state=='dying':
            self.death_age+=dt;self.boss_x=self.death_origin+max(0,self.death_age-2)*35;self.distance+=dt*1150
            self.death_blasts=[(x,y,age+dt,size) for x,y,age,size in self.death_blasts if age+dt<.85]
            self.x+=(195-self.x)*min(1,dt*5)
            self.vy-=1250*dt;self.jump_height=max(0,self.jump_height+self.vy*dt);self.y=590-self.jump_height
            if self.death_age<.6 and int(self.death_age*8)!=int((self.death_age-dt)*8):
                x=self.boss_x+self.rng.uniform(20,320);y=self.rng.uniform(360,560)
                self.death_blasts.append((x,y,0.,self.rng.uniform(65,125)))
                self.burst(x,y,22,'gold')
            if self.death_age>2.0:self.state='won';self.boost=0.;self.notice='TOBI: TOLD YOU WE COULD FIX IT.'
            return
        if self.state!='play':return
        self.was_shoot=shoot;self.finisher_cooldown=max(0,self.finisher_cooldown-dt)
        self.invuln=max(0,self.invuln-dt);self.notice_time=max(0,self.notice_time-dt)
        if 0<self.boost_cooldown<=dt:self.sound('boost_ready')
        self.boost=max(0,self.boost-dt);self.boost_cooldown=max(0,self.boost_cooldown-dt)
        self.impact=max(0,self.impact-dt);self.muzzle=max(0,self.muzzle-dt);self.fire-=dt
        if jump and not self.was_jump and self.jump_height<=0:self.sound('takeoff');self.vy=610;self.burst(self.x,590,10,'smoke')
        self.was_jump=jump
        if (slide_pressed or slide and not self.was_boost) and self.boost_cooldown<=0:
            self.sound('boost')
            self.boost=1.2;self.boost_cooldown=3.2
        self.was_boost=slide
        if self.jump_height>0 or self.vy>0:
            self.vy-=1250*dt;self.jump_height=max(0,self.jump_height+self.vy*dt)
            if self.ramp_flight and self.vy<=0:
                self.invuln=max(self.invuln,.2)
                if self.jump_height==0:
                    self.invuln=max(self.invuln,.8);self.ramp_flight=False
            if self.jump_height==0:self.sound('landing');self.landed_at=self.clock;self.vy=0;self.burst(self.x,590,14,'smoke')
        # Steering is direct and works on the ground or in the air. Releasing
        # the controls holds position instead of returning to an invisible rail.
        direction=max(-1,min(1,move))
        speed=direction*(440 if self.boost>0 else 330) if direction else (-220 if self.boost>0 else 0)
        old_car_x=self.x
        self.tire_marks=[p for p in getattr(self,'tire_marks',[]) if self.clock-p[2]<.65]
        if self.jump_height==0 and (self.boost>0 or direction and direction!=getattr(self,'last_direction',direction)) and self.clock-getattr(self,'mark_at',-99)>.08:
            self.tire_marks.append((self.x,self.distance,self.clock));self.mark_at=self.clock
        self.last_direction=direction
        self.x=max(160,min(660,self.x+speed*dt))
        self.y=590-self.jump_height+(math.sin(self.distance*.12)*1.5 if self.jump_height==0 else 0)
        self.distance+=dt*self.road_speed
        self.aim_target=aim if shoot and aim else None
        if shoot and self.fire<=0:
            self.machine_shots=getattr(self,'machine_shots',0)+1
            self.fire=.08;self.muzzle=.055;mx,my=self.muzzle_position;a=self.gun_angle
            self.shots.append(Bullet(mx,my,math.cos(a)*920,math.sin(a)*920,life=2.))
        if self.boss_x>850:self.boss_x=max(850,self.boss_x-dt*180)
        elif self.ram_time<=0:self.boss_x+=(850-self.boss_x)*min(1,dt*3)
        self.core_open=max(0,self.core_open-dt)
        trailer_active=self.encounter_phase==2
        if trailer_active:
            chase_robot.robot_step(self,dt)
            if self.state!='play':return
        if self.state=='play':
            if self.ramp_x is None and self.clock>=self.next_ramp:
                self.ramp_warning=2.;self.ramp_x=-900.;self.ramp_launched=False;self.next_ramp=self.clock+(7.5 if trailer_active else 10)
            if self.ramp_x is not None:
                self.ramp_warning=max(0,self.ramp_warning-dt)
                old=self.ramp_x;self.ramp_x+=self.road_speed*dt
                # Sweep the front wheel across the raised lip, retaining contact
                # while the rear wheel is still over it. A small manual hop
                # must not cancel a ramp launch.
                height=chase_robot.RAMP_HEIGHT if trailer_active else 40
                contact=(old-old_car_x<=82 and self.ramp_x-self.x>=-82)
                if not self.ramp_launched and contact and self.jump_height<=height:
                    self.sound('takeoff',.18)
                    self.ramp_launched=True
                    self.ramp_flight=trailer_active
                    self.vy=chase_robot.RAMP_VELOCITY if trailer_active else 720;self.jump_height=max(height,self.jump_height);self.y=590-self.jump_height;self.core_open=4.
                    self.notice='' if trailer_active else 'CORE EXPOSED / AIM FOR THE ENGINE';self.notice_time=0 if trailer_active else 4.
                    self.burst(self.x,590,25,'gold')
                if self.ramp_x>1450:self.ramp_x=None
        self.attack_timer-=dt
        if self.warning and not trailer_active:
            self.warning_time-=dt
            if self.warning_time<=0:self.attack(self.warning);self.warning=None;self.attack_timer=1.8
        elif self.attack_timer<=0 and self.ram_time<=0 and not trailer_active and self.core_open<=0 and not any(b.enemy for b in self.shots):
            choices=[k for k in ('ram','mortar','drones','spread','roller','spread') if self.attack_enabled(k)]
            self.warning=choices[self.attack_number%len(choices)];self.attack_number+=1
            self.warning_time=1.6
            self.mortar_targets=[max(165,min(660,self.x)),max(165,min(660,self.x+240))] if self.warning=='mortar' else []
        if self.ram_time>0:
            self.ram_time=max(0,self.ram_time-dt)
            target=385 if self.ram_time>1.1 else 850
            self.boss_x+=(target-self.boss_x)*min(1,dt*5)
            if self.boss_x<self.car_box[2]+12 and self.jump_height<120:self.hurt()
        if trailer_active and self.clock>=self.reinforce_at and len(self.drones)<2:
            self.spawn_drone();self.reinforce_at=self.clock+7.5
        if not trailer_active and self.core_open<=0 and self.clock>=self.reinforce_at and len(self.drones)<2 and not self.warning and self.ram_time<=0:
            self.spawn_drone();self.reinforce_at=self.clock+10
        for due,sx,sy,a in list(self.rocket_queue):
            if self.clock>=due:
                self.sound('rockets')
                for offset in (-.60,0,.60):self.shots.append(Bullet(sx,sy,math.cos(a+offset)*285,math.sin(a+offset)*285,True,5,kind='truck_rocket'))
                self.rocket_queue.remove((due,sx,sy,a))
        for i,ox in enumerate(self.obstacles):
            nx=ox+dt*self.road_speed;self.obstacles[i]=nx
            if ox<self.car_box[2] and nx+55>self.car_box[0] and self.jump_height<67:self.hurt()
        self.obstacles=[x for x in self.obstacles if x<1400]
        for d in self.drones:
            d['age']+=dt;d['x']-=dt*95;d['fire']-=dt
            if trailer_active and not (50<d['y']+self.camera_y<650 and d['x']<1200):
                d['fire']=max(d['fire'],.8);d['lock']=None
            if d['fire']<=.7 and d['lock'] is None:d['lock']=self.player_center
            if d['fire']<=0:
                self.sound('drone_fire',.12,position=(d['x'],d['y']))
                px,py=d['lock'];a=math.atan2(py-d['y'],px-d['x'])
                d['fire']=3.5;d['lock']=None
                self.shots.append(Bullet(d['x'],d['y'],math.cos(a)*420,math.sin(a)*420,True,4,kind='drone_laser'))
        for b in list(self.shots):
            if self.state!='play':break
            ox,oy=b.x,b.y
            if b.kind=='truck_mortar':b.vy+=520*dt
            b.x+=b.vx*dt;b.y+=b.vy*dt;b.life-=dt
            if b.kind=='truck_mortar' and b.y>=570:
                self.sound('road_blast',.16,position=(b.x,570))
                b.life=0;self.road_blasts.append((b.x,0.));self.burst(b.x,570,35,'gold')
                if abs(self.x-b.x)<170 and self.jump_height<80:self.hurt()
            elif b.enemy:
                l,t,r,bt=self.car_box;size=22 if b.kind=='tire_roller' else 18 if b.kind=='robot_shell' else 6 if b.kind=='drone_laser' else 10
                if segment_box(ox,oy,b.x,b.y,(l-size,t-size,r+size,bt+size)):self.hurt();b.life=0
            else:
                for d in self.drones:
                    if d['hp']>0 and segment_box(ox,oy,b.x,b.y,(d['x']-45,d['y']-25,d['x']+45,d['y']+25)):
                        d['hp']-=1;b.life=0;self.burst(b.x,b.y,6)
                        self.sound('drone_break' if d['hp']<=0 else 'impact',.14,position=(d['x'],d['y']))
                        if d['hp']<=0:self.burst(d['x'],d['y'],30,'red');self.destroyed+=1
                        break
                if b.life>0 and self.encounter_phase==2:
                    tx,ty=self.target
                    if segment_box(ox,oy,b.x,b.y,(tx-65,ty-80,tx+65,ty+80)):
                        b.life=0
                        if chase_robot.heart_open(self)>.8:
                            self.sound('impact',.14)
                            self.boss_hp=max(12,self.boss_hp-2);self.impact=.1;self.burst(tx,ty,8)
                        else:self.sound('armor',.2);self.burst(tx,ty,3,'cream')
                    continue
                if b.life>0 and self.boss_active:
                    for index in (0,1,2):
                        if self.parts[index]<=0:continue
                        tx,ty=self.component_target(index)
                        if not segment_box(ox,oy,b.x,b.y,(tx-38,ty-32,tx+38,ty+32)):continue
                        b.life=0
                        if trailer_active or (index==2 and not self.core_vulnerable):
                            self.sound('armor',.2);self.burst(tx,ty,3,'cream');break
                        damage=4 if index==2 and self.core_open>0 else 1
                        self.parts[index]=max(0,self.parts[index]-damage)
                        if index==2:self.parts[2]=max(20,self.parts[2])
                        self.boss_hp=sum(self.parts);self.impact=.10;self.burst(tx,ty,8)
                        if self.parts[index]>0:self.sound('impact',.14)
                        if index<2 and self.parts[index]==0:
                            self.sound('component_break')
                            if index==1:self.rocket_queue=[]
                            if self.warning and not self.attack_enabled(self.warning):self.warning=None
                            self.notice=('MINE LAUNCHER DESTROYED','TURRET DESTROYED')[index];self.notice_time=2.
                        if index==2 and self.parts[2]<=30 and not self.trailer_done:
                            self.detach_trailer();break
                        if index==2 and self.parts[2]<=20 and self.trailer_done and self.finisher_cooldown<=0:
                            self.begin_finisher();break
                        break
        if self.encounter_phase==2 and self.state=='play':
            heart_now=chase_robot.heart_open(self)>.8
            if heart_now!=self.heart_was_open:self.sound('heart',.25)
            self.heart_was_open=heart_now
        self.shots=[b for b in self.shots if b.life>0 and -80<b.x<W+100 and (-900 if self.encounter_phase==2 else -80)<b.y<780]
        self.drones=[d for d in self.drones if d['hp']>0 and d['x']>-100]

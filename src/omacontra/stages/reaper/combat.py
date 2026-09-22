"""Pure boss encounter simulation; positions are fullscreen arena coordinates."""
from dataclasses import dataclass
from omacontra import hit_recovery
from omacontra.rendering import movement_fx
import math
import random
from omacontra.rendering.hero_pose import muzzle_position, weapon_pose

W,H=1280,720
SCYTHE_PATTERNS=(('dash',),('double',),('high',),('low','high','low'),('dash','dash'))
SCYTHE_CUES={'double':'DOUBLE JUMP','high':'SLIDE','low':'JUMP','dash':'AIR DASH'}

def wave_band(kind,floor):
    if kind=='dash':return floor-68,floor
    return (floor-250,floor-49) if kind=='high' else (floor-140,floor) if kind=='double' else (floor-68,floor)

def wave_hits(kind,floor,old_x,new_x,player_x,player_y,sliding=False,duck=False):
    top,bottom=wave_band(kind,floor)
    height=46 if sliding else 62 if duck else 80
    half_width=150 if kind=='dash' else 30
    return min(old_x,new_x)-half_width<player_x+14 and max(old_x,new_x)+half_width>player_x-14 and player_y>top and player_y-height<bottom



def segment_hit(ax,ay,bx,by,x,y,r):
    dx,dy=bx-ax,by-ay
    u=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/max(.001,dx*dx+dy*dy)))
    return (ax+u*dx-x)**2+(ay+u*dy-y)**2 <= r*r


def segment_box(ax,ay,bx,by,box):
    """Swept projectile versus a body rectangle; fast shots cannot tunnel."""
    left,top,right,bottom=box;lo,hi=0.,1.
    for start,delta,mn,mx in ((ax,bx-ax,left,right),(ay,by-ay,top,bottom)):
        if abs(delta)<1e-9:
            if not mn<=start<=mx:return False
        else:
            a,b=(mn-start)/delta,(mx-start)/delta
            lo=max(lo,min(a,b));hi=min(hi,max(a,b))
            if lo>hi:return False
    return True

PROJECTILE_SIZE={'skull':(16,16),'raven':(19,14),'bullet':(3,3)}


@dataclass
class Bullet:
    x: float
    y: float
    vx: float
    vy: float
    enemy: bool=False
    life: float=2.
    damage: float=1.
    kind: str='bullet'
    trail_timer: float=0.


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    color: str
    size: float=3.


class Fight:
    def __init__(self,seed=None):
        self.sfx_events=[];self.sfx_last={}
        self.rng=random.Random(seed)
        self.rects={'arena':(0.,0.,float(W),float(H)),'eye':(460.,160.,130.,130.),'raven':(1040.,65.,130.,130.)}
        self.hp=5;self.max_hp=self.hp;self.boss_hp=180.;self.boss_max=180.;self.state='play'
        self.x=180.;self.y=self.floor;self.vy=0.;self.facing=1;self.duck=False;self.moving=False
        self.clock=0.;self.fire=0.;self.invuln=2.;self.weapon='machine';self.run_phase=0.
        self.shots=[];self.particles=[]
        self.node_max=12;self.nodes={'eye':12,'raven':12};self.exposed=0.;self.attack_timer=2.0
        self.warning=None;self.warning_time=0.;self.attack_number=0;self.swing_time=0.
        self.notice='THE WALLPAPER IS AWAKE';self.notice_time=3.
        self.node_flash={};self.boss_flash=0.;self.muzzle=0.;self.was_jump=False
        self.jumps_used=0;self.jump_flash=0.;self.slide_time=0.;self.slide_cooldown=0.
        self.aim_target=None;self.muzzle_position=(self.x,self.y-52);self.shoot_held=False
        self.dash_time=0.;self.dash_used=False;self.dash_direction=1
        self.volley_target=None
        self.patrol_time={'eye':0.,'raven':0.};self.boss_motion_time=0.
        self.death_offset=(0.,0.)
        self.slide_direction=1;self.was_slide=False;self.slide_dust=0.;self.slide_buffer=0.
        self.dash_casts=0;self.scythe_round=0;self.scythe_pattern=();self.wave_queue=[];self.wave_clock=0.;self.scythe_flash=0.;self.burst_queue=[];self.node_fire_flash={}
        self.death_age=0.;self.death_pose=0;self.death_blast_timer=0.;self.death_blasts=[]

    @property
    def floor(self):return self.rects['arena'][1]+self.rects['arena'][3]-27
    @property
    def phase(self):return 1 if self.boss_hp>120 else 2 if self.boss_hp>60 else 3
    @property
    def shielded(self):return any(hp>0 for hp in self.nodes.values())
    @property
    def body(self):
        x,y,w,h=self.rects['arena'];scale=h/750
        hx,hy,bh=((180,215,570),(227,245,590),(385,105,439))[self.boss_pose]
        dx,dy=self.boss_offset
        return x+w*.57+hx*scale+dx,self.floor-bh*scale+hy*scale+dy
    @property
    def boss_offset(self):
        if self.state in ('dying','won'):return self.death_offset
        t=self.boss_motion_time
        windup=max(0,1-self.warning_time/1.5) if self.warning=='scythe' else 0
        lunge=max(windup,self.swing_time/.65)
        return math.sin(t*.65)*38-lunge*28,-abs(math.sin(t*.85))*10

    def move_enemies(self,dt):
        # Plant each attacker before its tell and keep the entire burst coherent.
        for role,kind in (('eye','aimed'),('raven','raven')):
            firing=any(queued==kind for _,queued in self.burst_queue)
            if self.nodes[role]>0 and self.warning!=kind and not firing:
                self.patrol_time[role]+=dt
        if self.warning!='scythe' and self.swing_time<=0:self.boss_motion_time+=dt

    @property
    def boss_pose(self):return 1 if self.warning=='scythe' else 2 if self.swing_time>0 else 0
    @property
    def sliding(self):return self.slide_time>0
    @property
    def player_center(self):return self.x,self.y-(32 if self.sliding else 43 if self.duck else 35 if self.y<self.floor-1 else 52)

    @property
    def player_hitbox(self):
        height=40 if self.sliding else 59 if self.duck else 60 if self.y<self.floor-1 else 77
        half_width=24 if self.sliding else 14
        return self.x-half_width,self.y-height,self.x+half_width,self.y-3

    def projectile_hits_player(self,b,ox,oy):
        rx,ry=PROJECTILE_SIZE.get(b.kind,(3,3))
        left,top,right,bottom=self.player_hitbox
        return segment_box(ox,oy,b.x,b.y,(left-rx,top-ry,right+rx,bottom+ry))

    def node_center(self,role):
        x,y,w,h=self.rects[role];t=self.patrol_time[role]
        if role=='eye':dx,dy=115*math.sin(t*.65),52*math.sin(t*1.1)
        else:dx,dy=-190*math.sin(t*.4)**2,35*math.sin(t*1.25)
        return x+w/2+dx,y+h/2+dy

    def burst(self,x,y,color,n=18):
        for _ in range(n):
            a=self.rng.random()*math.tau;v=self.rng.uniform(20,140)
            self.particles.append(Particle(x,y,math.cos(a)*v,math.sin(a)*v,self.rng.uniform(.2,.8),color))
        self.particles=self.particles[-300:]

    def sound(self,name,cooldown=0.):
        # Other encounters inherit movement/damage but have their own sound scope.
        if type(self) is not Fight:return
        if self.clock-self.sfx_last.get(name,-999)<cooldown:return
        self.sfx_last[name]=self.clock
        self.sfx_events.append(name);self.sfx_events=self.sfx_events[-32:]

    def hurt(self):
        if self.invuln>0 or self.state!='play':return
        self.damage_taken=getattr(self,'damage_taken',0)+1;self.damage_clock=self.clock;self.hp-=0 if getattr(self,'unlimited_lives',False) else 1;self.burst(*self.player_center,'red',22);hit_recovery.begin(self)
        self.sound('player_death' if self.hp<=0 else 'hurt')
        if self.hp<=0:self.state='dead';self.notice='DHH DOWN / R TO RETRY';self.notice_time=999

    def hit_target(self,ax,ay,bx,by,damage):
        if self.state!='play':return False
        self.last_hit=None
        hits=[]
        for role,hp in self.nodes.items():
            if hp>0:
                x,y,w,h=self.rects[role];cx,cy=self.node_center(role)
                if segment_hit(ax,ay,bx,by,cx,cy,min(w,h)*.36):
                    hits.append((math.hypot(cx-ax,cy-ay),role,cx,cy))
        cx,cy=self.body
        if segment_hit(ax,ay,bx,by,cx,cy,75):hits.append((math.hypot(cx-ax,cy-ay),'boss',cx,cy))
        if not hits:return False
        _,role,x,y=min(hits)
        self.last_hit=(x,y)
        if role=='boss':
            self.sound('armor' if self.shielded else 'impact')
            self.burst(x,y,'cream' if self.shielded else 'gold',9)
            if not self.shielded:
                self.boss_hp=max(0,self.boss_hp-damage);self.boss_flash=.08
                if self.boss_hp<=0:
                    self.sound('rupture')
                    self.death_pose=self.boss_pose;self.death_offset=self.boss_offset;self.state='dying';self.death_age=0.
                    self.shots=[];self.wave_queue=[];self.burst_queue=[];self.warning=None
                    self.muzzle=0.;self.node_fire_flash={};self.boss_flash=0.
                    self.notice='CORE RUPTURE';self.notice_time=999
                    self.burst(x,y,'gold',65)
        else:
            if self.nodes[role]>damage:self.sound('raven_hit' if role=='raven' else 'eye_hit')
            self.nodes[role]=max(0,self.nodes[role]-damage);self.node_flash[role]=.1;self.burst(x,y,'gold',9)
            if self.nodes[role]<=0:
                self.sound('raven_break' if role=='raven' else 'eye_break')
                self.burst(x,y,'red',35)
                if not self.shielded:
                    self.sound('expose')
                    self.exposed=11.;self.notice='CORE EXPOSED / HIT THE REAPER';self.notice_time=3.
        return True

    def step_death(self,dt):
        self.death_age+=dt
        self.death_blasts=[(x,y,age+dt,size) for x,y,age,size in self.death_blasts if age+dt<.55]
        self.death_blast_timer-=dt
        if .45<self.death_age<2.7 and self.death_blast_timer<=0:
            self.sound('death_blast',.22)
            self.death_blast_timer=.16
            ax,ay,w,h=self.rects['arena']
            x=ax+w*.57+self.death_offset[0]+self.rng.uniform(80,330)*h/750
            y=self.floor+self.death_offset[1]-self.rng.uniform(80,440)*h/750
            self.death_blasts.append((x,y,0.,self.rng.uniform(55,115)))
            self.burst(x,y,self.rng.choice(('red','gold','cream')),14)
        # DHH lands naturally if the finishing shot was fired during a jump.
        self.slide_time=0.;self.dash_time=0.;self.moving=False;self.duck=False
        self.vy+=1250*dt;self.y=min(self.floor,self.y+self.vy*dt)
        if self.y==self.floor:self.vy=0
        if self.death_age>=4.2:
            self.sound('defeat')
            self.state='won';self.death_blasts=[]
            self.notice='WALLPAPER RESTORED';self.notice_time=999

    def prepare_scythe(self):
        self.scythe_pattern=SCYTHE_PATTERNS[self.scythe_round%len(SCYTHE_PATTERNS)]
        self.scythe_round+=1

    def launch_wave(self,kind):
        self.sound('sweep')
        self.swing_time=.65;self.scythe_flash=.22
        x=self.rects['arena'][0]+self.rects['arena'][2]*.63+self.boss_offset[0]
        top,bottom=wave_band(kind,self.floor)
        speed=200 if kind=='dash' and self.dash_casts==0 else 280 if kind=='dash' else 380+self.phase*15
        if kind=='dash':self.dash_casts+=1
        self.shots.append(Bullet(x,(top+bottom)/2,-speed,0,True,7,kind='scythe_'+kind))
        self.burst(x,(top+bottom)/2,'red',35)
        self.notice=' / '.join(SCYTHE_CUES[p] for p in self.scythe_pattern);self.notice_time=2.5
        if kind=='dash' and self.dash_casts==1:
            self.notice='JUMP + AIR DASH OVER THE SWEEP';self.notice_time=4.

    def attack(self,kind):
        px,py=self.player_center
        if kind=='scythe':
            if not self.scythe_pattern:self.prepare_scythe()
            self.wave_clock=0.
            self.wave_queue=[(i*(2. if part=='dash' else 1.15),part) for i,part in enumerate(self.scythe_pattern)]
            self.launch_wave(self.wave_queue.pop(0)[1])
        else:
            self.volley_target=self.player_center
            self.fire_volley(kind)
            count=2
            self.burst_queue.extend((self.clock+i*.24,kind) for i in range(1,count))

    def fire_volley(self,kind):
        role='raven' if kind=='raven' else 'eye'
        if self.nodes[role]<=0:return
        self.sound('raven' if role=='raven' else 'skull')
        sx,sy=self.node_center(role)
        px,py=self.volley_target or self.player_center
        count=min(5,3+self.phase) if role=='raven' else min(5,1+2*self.phase)
        speed=225+self.phase*15 if role=='raven' else 285+self.phase*15
        # At 350px, adjacent lanes are ~90px apart: room for the player's body.
        spread=.27
        self.node_fire_flash[role]=.20
        self.burst(sx,sy,'red',12)
        for i in range(count):
            angle=math.atan2(py-sy,px-sx)+(i-(count-1)/2)*spread
            self.shots.append(Bullet(sx,sy,math.cos(angle)*speed,math.sin(angle)*speed,True,7,kind='raven' if role=='raven' else 'skull'))

    def step(self,dt,move=0,jump=False,duck=False,shoot=False,aim=None,aim_up=False,slide=False,slide_pressed=False):
        dt=min(.04,max(0,dt));self.clock+=dt;self.swing_time=max(0,self.swing_time-dt);self.scythe_flash=max(0,self.scythe_flash-dt)
        movement_fx.advance(self,dt)
        was_running=getattr(self,'was_running',False)
        was_grounded=self.y>=self.floor-.2
        for p in self.particles:p.x+=p.vx*dt;p.y+=p.vy*dt;p.vy+=120*dt;p.life-=dt
        self.particles=[p for p in self.particles if p.life>0]
        was_recovering=getattr(self,'hit_age',None) is not None
        recovering=hit_recovery.tick(self,dt)
        if was_recovering and getattr(self,'hit_age',None) is None and self.hp>0:self.sound('respawn')
        if recovering:
            move=0;jump=duck=shoot=slide=slide_pressed=False;aim=None;aim_up=False
        self.shoot_held=bool(shoot)
        if self.state=='dying':self.step_death(dt);return
        if self.state!='play':return
        self.move_enemies(dt)
        self.notice_time=max(0,self.notice_time-dt);self.invuln=max(0,self.invuln-dt)
        self.fire-=dt;self.muzzle=max(0,self.muzzle-dt);self.boss_flash=max(0,self.boss_flash-dt)
        self.node_fire_flash={k:max(0,v-dt) for k,v in self.node_fire_flash.items()}
        self.node_flash={k:max(0,v-dt) for k,v in self.node_flash.items()}
        self.jump_flash=max(0,self.jump_flash-dt)
        self.slide_time=max(0,self.slide_time-dt)
        self.slide_cooldown=max(0,self.slide_cooldown-dt)
        self.dash_time=max(0,self.dash_time-dt)
        grounded=self.y>=self.floor-.1
        if grounded:self.jumps_used=0;self.dash_used=False;self.dash_time=0.
        elif self.jumps_used==0:self.jumps_used=1
        self.slide_buffer=max(0,self.slide_buffer-dt)
        if slide_pressed or (slide and not self.was_slide):
            if not grounded and not self.dash_used:
                self.sound('dash')
                self.dash_used=True;self.dash_time=.18;self.slide_buffer=0.
                self.dash_direction=(1 if move>0 else -1) if move else self.facing
                self.burst(self.x,self.y-35,'cream',10)
            elif grounded:self.slide_buffer=.18
        if self.slide_buffer>0 and grounded and self.slide_cooldown<=0:
            self.sound('slide')
            self.slide_time=.42;self.slide_cooldown=.65;self.slide_buffer=0.
            self.slide_direction=(1 if move>0 else -1) if move else self.facing
        self.was_slide=slide
        if jump and not self.was_jump and self.jumps_used<2:
            self.sound('double_jump' if self.jumps_used==1 else 'jump')
            self.jumps_used+=1;self.vy=-510 if self.jumps_used==1 else -475
            self.slide_time=0.;self.dash_time=0.;self.slide_buffer=0.;grounded=False
            if self.jumps_used==2:
                self.jump_flash=.24;self.burst(self.x,self.y,'cream',12)
        self.was_jump=jump
        self.duck=(duck or self.sliding) and grounded
        if move:self.facing=1 if move>0 else -1
        was_airborne=self.y<self.floor-.1
        if self.dash_time<=0:self.vy+=1250*dt;self.y+=self.vy*dt
        if was_airborne and self.y>=self.floor:self.sound('land',.15)
        if self.y>=self.floor:self.y=self.floor;self.vy=0;self.jumps_used=0;self.dash_used=False
        x,y,w,h=self.rects['arena'];old_x=self.x
        speed=self.slide_direction*(280+240*self.slide_time/.42) if self.sliding else move*(110 if self.duck else 240)
        if self.dash_time>0:
            speed=self.dash_direction*620
            self.particles.append(Particle(self.x-self.dash_direction*12,self.y-32,-self.dash_direction*80,0,.16,'cream',5))
        self.x=max(x+22,min(x+w-22,self.x+speed*dt))
        self.moving=abs(self.x-old_x)>.001 and not self.duck
        if not recovering and self.y>=self.floor-.1:self.respawn_anchor=(self.x,self.y)
        if self.moving and not self.sliding and self.y>=self.floor-.2:
            if not was_running:self.run_phase=0.
            # Six poses over 144 px: a .60 s stride at normal running speed.
            # Give the tucked-rifle arm swing time to read alongside the legs.
            self.run_phase+=abs(self.x-old_x)/24
        movement_fx.step(self,dt,was_running,old_x,was_grounded)
        self.aim_target=aim if shoot and aim else (self.x+self.facing*100,self.player_center[1]-102) if aim_up else None
        # Face the target continuously; all poses share the same barrel geometry.
        if self.aim_target:self.facing=1 if self.aim_target[0]>=self.x else -1
        px,py=muzzle_position(self,self.aim_target)
        self.muzzle_position=(px,py)
        angle=weapon_pose(self,self.aim_target)[2]
        if not self.shielded:
            self.exposed-=dt
            if self.exposed<=0:self.sound('reform');self.node_max=12+self.phase*2;self.nodes={'eye':12+self.phase*2,'raven':12+self.phase*2};self.notice='WEAK POINTS REFORMED';self.notice_time=2.
        if shoot and self.fire<=0:
            self.machine_shots=getattr(self,'machine_shots',0)+1
            self.fire=.10
            self.muzzle=.06
            self.shots.append(Bullet(px,py,math.cos(angle)*800,math.sin(angle)*800))
        if self.state!='play':return
        for due,kind in list(self.burst_queue):
            if due<=self.clock:
                self.fire_volley(kind);self.burst_queue.remove((due,kind))
        self.wave_clock+=dt
        while self.wave_queue and self.wave_queue[0][0]<=self.wave_clock:
            self.launch_wave(self.wave_queue.pop(0)[1])
        waves_active=bool(self.wave_queue) or any(b.kind.startswith('scythe_') for b in self.shots)
        if not waves_active and not self.burst_queue:self.attack_timer-=dt
        if self.warning:
            self.warning_time-=dt
            if self.warning_time<=0:self.attack(self.warning);self.warning=None;self.attack_timer=1.65-self.phase*.15
        elif self.attack_timer<=0 and not waves_active and not self.burst_queue:
            sequence=('aimed','raven','aimed','scythe','raven')
            next_attack=sequence[self.attack_number%5]
            # Broken turrets stay silent; the exposed boss still uses its scythe.
            while next_attack!='scythe' and self.nodes['raven' if next_attack=='raven' else 'eye']<=0:
                self.attack_number+=1;next_attack=sequence[self.attack_number%5]
            # Never demand a jump/slide sequence through an existing projectile fan.
            active=sum(b.enemy and b.life>0 for b in self.shots)
            if active>(0 if next_attack=='scythe' else 4):
                self.attack_timer=.08
            else:
                self.warning=next_attack;self.attack_number+=1
                if next_attack=='scythe':self.sound('charge')
            self.warning_time=1.5 if self.warning=='scythe' else .95
            if self.warning=='scythe':
                self.prepare_scythe()
                if self.scythe_pattern==('dash',) and self.dash_casts==0:self.warning_time=2.1
        for b in list(self.shots):
            ox,oy=b.x,b.y;b.x+=b.vx*dt;b.y+=b.vy*dt;b.life-=dt
            if b.enemy:
                if b.kind.startswith('scythe_'):
                    b.trail_timer-=dt
                    if b.trail_timer<=0:
                        b.trail_timer=.025
                        top,bottom=wave_band(b.kind[7:],self.floor)
                        for _ in range(3):
                            yy=self.rng.uniform(top+5,bottom-5)
                            self.particles.append(Particle(b.x+self.rng.uniform(5,24),yy,self.rng.uniform(35,110),self.rng.uniform(-65,5),self.rng.uniform(.18,.45),'smoke',self.rng.uniform(8,19)))
                            self.particles.append(Particle(b.x+self.rng.uniform(0,15),yy,self.rng.uniform(65,190),self.rng.uniform(-100,25),self.rng.uniform(.15,.40),self.rng.choice(('red','gold','cream')),self.rng.uniform(2,5)))
                    hit=wave_hits(b.kind[7:],self.floor,ox,b.x,self.x,self.y,self.sliding,self.duck)
                    if hit:self.hurt()
                else:
                    if b.kind=='scythe':
                        hit=segment_hit(ox,oy,b.x,b.y,self.x,self.y-12,17)
                    else:hit=self.projectile_hits_player(b,ox,oy)
                    if hit:self.hurt();b.life=0
            elif self.hit_target(ox,oy,b.x,b.y,b.damage):b.life=0
        self.particles=self.particles[-600:]
        self.shots=[b for b in self.shots if b.life>0 and (-180 if b.kind=='scythe_dash' else -30)<b.x<W+180 and -30<b.y<H+30][-350:]

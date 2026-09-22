"""Tidebreaker encounter. Reuses DHH's tested locomotion and gun simulation.

Reaper AI is disabled: tide hazards and attack recovery are independent.
Coordinates are fixed arena space; deck bob is applied equally to art and floor.
"""
from dataclasses import dataclass
import math
from omacontra.stages.reaper.combat import Fight, segment_hit
from omacontra.stages.harbor.tide_guardians import GuardianCombat
from omacontra.stages.harbor.tide_cargo import Cargo, step_pair

@dataclass
class TideHazard:
    kind: str
    x: float
    age: float = 0.
    hit: bool = False
    direction: int = -1

class Tidebreaker(GuardianCombat,Fight):
    sound_bank='tide'
    def __init__(self, seed=None):
        super().__init__(seed)
        self.rects['arena']=(0.,0.,1280.,657.)
        self.x=220.;self.y=self.floor
        self.hp=6;self.max_hp=self.hp;self.boss_max=600.;self.boss_hp=self.boss_max
        self.attack_timer=math.inf
        self.hazards=[];self.tide_warning=None;self.tide_timer=3.
        self.tide_round=0;self.open_time=0.;self.target_x=400.;self.tide_followups=[]
        self.notice='';self.notice_time=0.
        self.core_flash=0.;self.deck_roll=0.
        self.wave_phase=1;self.attack_direction=-1;self.exposure_pending=False
        self.tilt_clock=0.;self.deck_slope=0.;self.combo_index=0
        self.combo_wait=.8;self.combo_active=False;self.combo_failed=False;self.combo_damage=False
        self.cargo=Cargo()
        self.cargos=[self.cargo,Cargo(x=1110.,release_phase=2)]
        self.roll_rate=.68
        self.ocean_rage=0.
        self.init_guardians()

    def sound(self,name,cooldown=0.):
        if self.clock-self.sfx_last.get(name,-999)<cooldown:return
        self.sfx_last[name]=self.clock
        self.sfx_events.append(name);self.sfx_events=self.sfx_events[-32:]

    @property
    def floor(self):return self.deck_y(getattr(self,'x',640.))
    def deck_y(self,x):return 630.+getattr(self,'deck_roll',0.)+getattr(self,'deck_slope',0.)*(x-640.)
    @property
    def phase(self):return getattr(self,'wave_phase',1)
    @property
    def shielded(self):return True # Suppress the inherited Reaper node cycle.
    @property
    def core(self):
        if self.stage:
            a=self.target_guardian
            return a.core(self.floor) if a else (640.,400.)
        return 974.,345.+math.sin(self.clock*1.4)*4
    @property
    def vulnerable(self):return self.state=='play' and (any(a.hp>0 for a in self.guardians) if self.stage else self.boss_hp>0)
    def move_enemies(self,dt):pass

    def hit_target(self,ax,ay,bx,by,damage):
        if self.state!='play':return False
        if self.stage:return self.hit_guardians(ax,ay,bx,by,damage)
        cx,cy=self.core
        if not segment_hit(ax,ay,bx,by,cx,cy,57):return False
        self.sound('water_hit',.18)
        self.burst(bx,by,'cream',3)
        self.boss_hp=max(0,self.boss_hp-damage);self.core_flash=.09
        if self.boss_hp<=0:self.begin_reveal()
        else:
            if self.wave_phase==1 and self.boss_hp<=self.boss_max*2/3:
                self.wave_phase=2;self.open_time=0.;self.hazards=[];self.tide_followups=[]
                self.tide_warning=None;self.tide_timer=1.3;self.exposure_pending=False
            if self.wave_phase==2 and self.boss_hp<=self.boss_max/3:
                self.wave_phase=3;self.open_time=0.;self.hazards=[];self.tide_followups=[]
                self.tide_warning=None;self.combo_wait=1.5;self.combo_index=0;self.combo_active=True

        return True

    def spawn_wave(self,kind):
        if kind!='claw':self.sound('surge' if kind=='surge' else 'breaker')
        origin=-40. if self.attack_direction>0 else 1320.
        self.hazards.append(TideHazard(kind,self.target_x if kind=='claw' else origin,
                                       direction=self.attack_direction))

    def step_death(self,dt):
        for a in self.guardians:a.death_age+=dt
        self.death_age+=dt;self.vy+=1250*dt;self.y=min(self.floor,self.y+self.vy*dt)
        self.slide_time=0.;self.moving=False;self.duck=False
        if self.y>=self.floor:self.vy=0
        if self.death_age>=3.4:self.state='won';self.notice='PASSAGE OPEN / THE FOUNDRY';self.notice_time=999

    def start_warning(self,kind):
        self.tide_warning=kind;self.tide_timer=1.05 if kind=='claw' else .8
        self.target_x=max(55,min(1225,self.x))
        self.attack_direction=1 if self.phase==2 and self.tide_round%2 else -1
        self.notice_time=0.

    def step(self,dt,**controls):
        dt=min(.04,max(0,dt))
        old_clock=self.clock;old_tilt=self.tilt_clock
        self.wave_reveal=max(0,self.wave_reveal-dt)
        if self.state=='reveal':self.step_reveal(dt);return
        if self.stage and self.state=='play' and any(a.hp>0 and a.enraged and a.rage_age<2.8 for a in self.guardians):
            self.clock+=dt;self.guardian_step(dt);return
        controls.pop('interact',False)
        old_floor=self.floor;was_grounded=self.y>=old_floor-.1
        if self.stage==0:
            self.ocean_rage+=((0.,.42,1.)[self.wave_phase-1]-self.ocean_rage)*min(1,dt*.65)
            self.roll_rate+=((.68,.83,1.02)[self.wave_phase-1]-self.roll_rate)*min(1,dt)
            self.tilt_clock+=dt*self.roll_rate
            amplitude=(.045,.075,.10)[self.wave_phase-1]
            target=amplitude*math.sin(self.tilt_clock)
            self.deck_slope+=(target-self.deck_slope)*min(1,dt*2)
            self.deck_roll=math.sin(self.tilt_clock*1.1)*5
        else:
            self.deck_slope*=max(0,1-dt*2);self.deck_roll*=max(0,1-dt*2)

        if self.y>=old_floor-.1:self.y=self.floor
        super().step(dt,**controls)
        if was_grounded and not controls.get('jump') and abs(self.y-self.floor)<28:self.y=self.floor
        if self.state!='play':return
        self.core_flash=max(0,self.core_flash-dt)
        self.open_time=max(0,self.open_time-dt)
        if self.stage:
            self.guardian_step(dt);return
        if int((old_clock-.45)/9)!=int((self.clock-.45)/9) and self.clock>.45:self.sound('thunder',8.)
        if int(old_tilt/math.pi)!=int(self.tilt_clock/math.pi):self.sound('deck_creak',3.)
        step_pair(self,dt)
        for hazard in self.hazards:
            old_x=hazard.x;old_age=hazard.age;hazard.age+=dt
            if hazard.kind=='claw' and old_age<.18<=hazard.age:self.sound('water_crash')
            if hazard.kind in ('surge','ceiling','breaker'):
                hazard.x+=hazard.direction*(400 if self.phase==1 else 440)*dt
                ground=self.deck_y(hazard.x)
                top,bottom=(ground-62,ground) if hazard.kind=='surge' else (ground-140,ground) if hazard.kind=='breaker' else (ground-235,ground-64)
                left,up,right,down=self.player_hitbox
                hit=min(old_x,hazard.x)-26<right and max(old_x,hazard.x)+26>left and down>top and up<bottom
            else:
                left,up,right,down=self.player_hitbox
                height=max(20,320*(1-min(1,max(0,hazard.age-.18)/.4))**2)
                hit=.18<hazard.age<.58 and left<hazard.x+55 and right>hazard.x-55 and down>self.deck_y(hazard.x)-height
            if hit and not hazard.hit:
                before=self.hp;self.hurt();hazard.hit=self.hp<before
                if hazard.hit and self.wave_phase==3:self.combo_failed=True
        self.hazards=[h for h in self.hazards if -180<h.x<1480 and h.age<(1.1 if h.kind=='claw' else 4.)]
        if self.wave_phase==3:
            self.step_crest(dt);return
        for due,kind in list(self.tide_followups):
            if self.clock>=due:
                self.spawn_wave(kind);self.tide_followups.remove((due,kind))
        if self.hazards or self.tide_followups or self.open_time>0:return
        if self.exposure_pending:
            self.exposure_pending=False;self.open_time=3.4 if self.phase==1 else 4.2
            self.tide_timer=.65;return
        self.tide_timer-=dt
        if self.tide_timer>0:return
        if self.tide_warning:
            kind=self.tide_warning;self.tide_warning=None
            self.spawn_wave(kind)
            self.tide_timer=.22
            if kind=='surge':
                self.tide_followups.append((self.clock+1.05,'surge'))

            self.tide_round+=1
            if self.tide_round%3==0:self.exposure_pending=True
        else:
            sequence=('surge','claw','ceiling') if self.phase==1 else ('claw','surge','ceiling','surge','ceiling','claw')
            self.start_warning(sequence[self.tide_round%len(sequence)])

    def step_crest(self,dt):
        if self.open_time>0:return
        if self.hazards:return
        self.combo_wait-=dt
        if self.combo_wait>0:return
        if self.combo_index==3:
            self.open_time=3. if self.combo_failed else 6.
            self.combo_index=0;self.combo_failed=False;self.tide_warning=None;self.combo_wait=1.2
            return
        pattern=('surge','ceiling','breaker')
        kind=pattern[self.combo_index]
        if self.tide_warning is None:
            self.tide_warning=kind;self.combo_wait=1.
            self.attack_direction=-1;self.notice_time=0.
        else:
            self.spawn_wave(kind);self.tide_warning=None
            self.combo_index+=1;self.combo_wait=.35

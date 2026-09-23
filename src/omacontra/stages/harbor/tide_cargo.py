"""Loose AAA overstock trolley: uninterrupted deck-driven momentum."""
from dataclasses import dataclass
from omacontra.stages.reaper.combat import segment_box

@dataclass
class Cargo:
    x: float=650.
    vx: float=0.
    released: bool=False
    impact: float=0.
    hits: int=0
    age: float=0.
    released_at: float=0.
    release_phase: int=1

    @property
    def bounds(self):return 48.,1232.

    def step(self,f,dt):
        self.age+=dt;self.impact=max(0,self.impact-dt)
        if not self.released:
            if self.age<4.5 or f.wave_phase<self.release_phase:return
            f.sound('cargo_bump')
            self.released=True;self.released_at=self.age;self.impact=.35
            f.burst(self.x,f.deck_y(self.x)-24,'gold',12)
        old=self.x
        self.vx+=f.deck_slope*3000*dt
        self.vx*=max(0,1-.12*dt)
        limit=(220,290,350)[f.wave_phase-1]
        self.vx=max(-limit,min(limit,self.vx));self.x+=self.vx*dt
        if abs(self.vx)>70 and int(old/90)!=int(self.x/90):f.sound('cargo',.30)
        lo,hi=self.bounds
        if self.x<lo or self.x>hi:
            self.x=max(lo,min(hi,self.x))
            if abs(self.vx)>35:
                f.sound('cargo_bump',.3)
                self.impact=.3;self.hits+=1
                f.burst(self.x,f.deck_y(self.x)-8,'gold',8)
            self.vx*=-.3
        ground=f.deck_y(self.x)
        left,top,right,bottom=f.player_hitbox
        # Swept contact; jumping above the lid clears the full trolley.
        if segment_box(old,f.deck_y(old)-27,self.x,ground-27,
                       (left-39,top-27,right+39,bottom+27)):
            before=f.hp;f.hurt()
            if f.hp<before and f.wave_phase==3:f.combo_failed=True


def step_cargos(f,dt):
    for cargo in f.cargos:cargo.step(f,dt)
    carts=sorted((cargo for cargo in f.cargos if cargo.released),key=lambda cargo:cargo.x)
    # Only released trolleys collide. Resolve every neighbor, including a chain
    # pressed against either deck edge, without introducing interior stops.
    for a,b in zip(carts,carts[1:]):
        if b.x-a.x>=100:continue
        middle=(a.x+b.x)/2
        a.x=middle-50;b.x=middle+50
        if a.vx>b.vx:
            a.vx,b.vx=b.vx*.8,a.vx*.8
            a.impact=b.impact=.25
            f.sound('cargo_bump',.3)
    if not carts:return
    carts[0].x=max(carts[0].bounds[0],carts[0].x)
    for a,b in zip(carts,carts[1:]):b.x=max(b.x,a.x+100)
    carts[-1].x=min(carts[-1].bounds[1],carts[-1].x)
    for a,b in reversed(list(zip(carts,carts[1:]))):a.x=min(a.x,b.x-100)

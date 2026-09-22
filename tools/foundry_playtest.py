"""Control-only Foundry playtest; plans dodges without granting health or skipping phases."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from copy import deepcopy
from itertools import product
from omacontra.stages.dragon.foundry import Foundry

def choose(f):
 best=None;score=-1e99
 for move,jump,dash in product((-1,0,1),(False,True),(False,True)):
  g=deepcopy(f)
  controls=dict(move=move,jump=jump,slide_pressed=dash,duck=not jump,shoot=True,aim=f.mount_target if f.mount_hp>0 else f.core)
  for i in range(24):
   g.step(.04,**dict(controls,slide_pressed=dash and i==0))
   if g.state!='play':break
  target=f.pickup_spot[0] if f.mount_hp==0 else 400
  value=(g.hp-f.hp)*10000+(f.mount_hp-g.mount_hp)*3+(f.boss_hp-g.boss_hp)*2-abs(g.x-target)*.035
  if g.state=='dead':value-=100000
  if f.pickups:value-=abs(g.y-(f.pickup_spot[1]+19))*.13;value+=500 if g.laser else 0
  if g.state=='disarm':value+=1000
  if jump:value-=.1
  if dash:value-=.15
  if value>score:best=controls;score=value
 return best

if __name__=='__main__':
 f=Foundry(7);hp=f.hp;state=''
 for i in range(4000):
  if i%3==0 or f.state!='play':control=choose(f) if f.state=='play' else {}
  f.step(.04,**dict(control,slide_pressed=control.get('slide_pressed',False) and i%3==0))
  if f.hp!=hp or f.state!=state:print(round(f.clock,2),f.state,f.hp,f.mount_hp,round(f.boss_hp),round(f.x),round(f.y),flush=True);hp=f.hp;state=f.state
  if f.state in ('won','dead'):break

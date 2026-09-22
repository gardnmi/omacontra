"""Deterministic control-only playthrough; never grants health or skips phases."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from copy import deepcopy
from itertools import product
from omacontra.stages.highway.chase import Chase


def choose(f):
    if f.state=='finisher':
        return dict(jump=f.finisher_phase=='prompt',shoot=f.finisher_phase=='aim',aim=f.target)
    if f.state!='play':return {}
    best={};score=-1e99
    target=f.target
    if f.encounter_phase==1 and f.core_open>0:target=f.component_target(2)
    for move,jump,boost in product((-1,0,1),(False,True),(False,True)):
        g=deepcopy(f)
        controls=dict(move=move,jump=jump,slide_pressed=boost,shoot=True,aim=target)
        for i in range(30):
            g.step(.04,**dict(controls,slide_pressed=boost and i==0))
            if g.state!='play':break
        value=(g.hp-f.hp)*10000+(f.boss_hp-g.boss_hp)*4-abs(g.x-310)*.01
        if g.state=='dead':value-=100000
        if g.state in ('transform','finisher'):value+=1000
        if jump:value-=.1
        if boost:value-=.2
        if value>score:best=controls;score=value
    return best


def run(dt=.04):
    f=Chase(8);trace=[]
    for i in range(int(240/dt)):
        if i%3==0 or f.state!='play':controls=choose(f)
        f.step(dt,**dict(controls,slide_pressed=controls.get('slide_pressed',False) and i%3==0))
        if i%25==0:trace.append((round(f.clock,2),f.state,f.encounter_phase,f.hp,round(f.boss_hp,1)))
        if f.state in ('won','dead'):break
    return f,trace

if __name__=='__main__':
    f,trace=run()
    for row in trace:print(*row)
    print('RESULT',f.state,'health',f.hp)

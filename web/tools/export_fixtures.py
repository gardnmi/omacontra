#!/usr/bin/env python3
"""Record deterministic gameplay traces from the desktop reference implementation."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from omacontra.stages.reaper.combat import Fight
cases=[]
for name in ('movement','volleys','targeting'):
    f=Fight(seed=31);f.invuln=999
    actions=[];snapshots=[]
    for i in range(2700 if name=='volleys' else 360):
        if name=='movement':
            action={'move':1 if i<90 else -1 if i<180 else 1 if i<280 else 0,'jump':i in (10,26,145,162,220),'slide':i in (38,182,235),'shoot':70<=i<140 or i>=300,'aim_up':i>=300,'duck':285<=i<300}
        elif name=='targeting':
            target=f.node_center('eye' if f.nodes['eye']>0 else 'raven') if f.shielded else f.body
            action={'shoot':True,'aim':target}
        else:action={}
        f.step(1/60,**action);actions.append(action)
        if i%10==0 or i==len(actions)-1 and i in (359,2699):
            snapshots.append({'frame':i,'values':{'x':f.x,'y':f.y,'vy':f.vy,'runPhase':f.run_phase,'jumpsUsed':f.jumps_used,'dashUsed':f.dash_used,'hp':f.hp,'bossHp':f.boss_hp,'phase':f.phase,'shielded':f.shielded,'nodes':f.nodes.copy(),'attackNumber':f.attack_number,'warning':f.warning,'state':f.state,'shotsFired':getattr(f,'machine_shots',0)},'shots':[[b.x,b.y,b.vx,b.vy,b.kind] for b in f.shots]})
    cases.append({'name':name,'actions':actions,'snapshots':snapshots})
(ROOT/'web/tests/desktop-traces.json').write_text(json.dumps(cases,separators=(',',':'))+'\n')
print('Saved reference traces for movement, targeting, and 45 seconds of attacks.')

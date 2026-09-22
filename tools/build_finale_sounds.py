"""Quiet, varied sci-fi cues; no per-bullet noise or repeated metal impacts."""
from sound_palette import PALETTE,build_bank,layer,ROOT

PALETTE['finale']={
 'ring':(.65,-36,[layer('field',speed=.8,length=.65)]),
 'fan':(.32,-37,[layer('laser',speed=.85,length=.3)]),
 'spiral':(.55,-37,[layer('field',speed=1.25,length=.5)]),
 'needles':(.28,-37,[layer('large_laser',speed=1.3,length=.28)]),
 'curtain':(.55,-36,[layer('large_laser',speed=.7,length=.5)]),
 'thruster':(.35,-34,[layer('thruster',speed=1.1,length=.35)]),
 'laser_start':(.22,-40,[layer('field',speed=1.5,length=.22)]),
 'laser_hit':(.12,-44,[layer('laser',speed=.8,length=.12)]),
 'node_break':(1.25,-31,[layer('field',speed=.65,length=.8),layer('low',at=.08,gain=.5,speed=1.3)]),
 'release':(2.,-30,[layer('field',speed=.55,length=1.5),layer('low',at=.15,gain=.4,speed=.8)]),
 'enrage':(1.25,-32,[layer('large_laser',speed=.55,length=.8),layer('field',at=.2,gain=.4,speed=.8)]),
 'hurt':(.4,-32,[layer('field',speed=1.6,length=.25),layer('low',gain=.35,speed=1.8,length=.4)]),
 'death':(1.7,-31,[layer('low',speed=.8),layer('field',gain=.3,speed=.6)]),
 'defeat':(3.2,-29,[layer('low',speed=.6),layer('field',at=.2,gain=.6,speed=.55),layer('low',at=1.1,gain=.3,speed=.75)])
}

if __name__=='__main__':
    (ROOT/'finale').mkdir(exist_ok=True)
    build_bank('finale')

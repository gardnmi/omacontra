from sound_palette import PALETTE,build_bank
"""Deterministic, subdued vehicle/mechanical effects for Quattro Run.
Original synthesis plus the project's revised non-metallic explosion textures.
"""
from pathlib import Path
import array, math, random, wave
ROOT=Path(__file__).resolve().parents[1]/'assets/audio'
OUT=ROOT/'chase';OUT.mkdir(exist_ok=True)
RATE=44100
SOUNDS=[
 ('boost',1.15,-34,'engine'),('ram',1.1,-35,'engine'),
 ('takeoff',.22,-37,'suspension'),('landing',.28,-34,'suspension'),
 ('mine',.23,-37,'mechanism'),('mortar',.36,-32,'cannon'),
 ('rockets',.45,-34,'rocket'),('drone_fire',.15,-39,'laser'),
 ('impact',.10,-40,'impact'),('armor',.09,-42,'impact'),
 ('car_hit',.32,-32,'suspension'),('component_break',1.05,-31,'break'),
 ('drone_break',.6,-35,'break'),('road_blast',.8,-33,'break'),
 ('car_wreck',2.8,-28,'rupture'),('truck_break',1.55,-29,'rupture'),
 ('unfold',1.95,-33,'servo'),('lock',.65,-31,'suspension'),
 ('heart',.28,-37,'servo'),('cannon',.85,-30,'cannon'),
 ('finisher',.7,-31,'rocket'),('robot_break',4.,-28,'rupture')]

def read(name):
    with wave.open(str(ROOT/'reaper'/f'{name}.wav')) as f:
        pcm=array.array('h',f.readframes(f.getnframes()))
    peak=max(map(abs,pcm));return [v/peak for v in pcm]

textures={key:read(key) for key in ('break','rupture')}
for seed,(name,duration,db,kind) in enumerate(SOUNDS):
    if name in PALETTE['chase']:continue
    rng=random.Random(440+seed);low=deep=mid=phase=0.;values=[]
    for i in range(round(duration*RATE)):
        t=i/RATE;u=t/duration;n=rng.uniform(-1,1)
        low+=.037*(n-low);deep+=.009*(n-deep);mid+=.16*(n-mid)
        decay=math.exp(-u*6);attack=min(1,t/.004)
        if kind in textures:
            source=textures[kind];speed=.90 if name in ('car_wreck','robot_break') else 1.08
            pos=i*speed;j=int(pos)
            value=source[j]*(1-pos+j)+source[j+1]*(pos-j) if j+1<len(source) else 0.
            value+=deep*.6*math.exp(-u*4)
        elif kind=='engine':
            # Low exhaust pulses and intake rush, a single acceleration event.
            hz=48+55*math.sin(math.pi*u*.8)
            phase+=math.tau*hz/RATE
            value=(math.sin(phase)*.11+math.sin(phase*2)*.035+low*1.6)*math.sin(math.pi*u)**.8
        elif kind=='servo':
            phase+=math.tau*(95+32*math.sin(u*math.pi))/RATE
            envelope=math.sin(math.pi*u)**.7
            value=(low*1.5+math.sin(phase)*.04+mid*.09)*envelope
            # Heavy actuator stops without a long ringing metallic tone.
            for beat in ((.18,.55,.82) if name=='unfold' else (.12,.8)):
                age=u-beat
                if age>=0:value+=deep*4*math.exp(-age*45)
        elif kind=='rocket':
            value=low*3.2*math.exp(-u*3)+mid*.38*math.exp(-u*8)+deep*2*decay
        elif kind=='cannon':
            value=(mid-low)*.75*math.exp(-t*38)+low*5*math.exp(-t*9)+deep*8*math.exp(-t*5)
        elif kind=='laser':
            # Brief, dark electrical snap tied to the visible drone muzzle.
            phase+=math.tau*(170+530*math.exp(-t*45))/RATE
            value=(math.sin(phase)*.06+mid*.65+low)*decay
        elif kind=='suspension':
            value=(deep*8+low*2.2)*decay+mid*.18*math.exp(-u*20)
        elif kind=='mechanism':value=(low*2+mid*.30)*decay
        else:value=(low*3+mid*.3)*decay
        values.append(value*attack*min(1,(duration-t)/min(.30,duration*.35)))
    gain=10**(db/20)/max(map(abs,values))
    with wave.open(str(OUT/f'{name}.wav'),'wb') as f:
        f.setparams((1,2,RATE,0,'NONE','not compressed'))
        f.writeframes(array.array('h',(round(v*gain*32767) for v in values)).tobytes())
print(f'Built {len(SOUNDS)} stage-two effects')

build_bank('chase')

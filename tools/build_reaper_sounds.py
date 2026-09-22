from sound_palette import PALETTE,build_bank
"""Build soft textured arcade effects; no runtime synthesis or external tools.
Uses our existing explosion and CC0-derived rifle impact for physical body.
"""
from pathlib import Path
import array, math, random, wave
ROOT=Path(__file__).resolve().parents[1]/'assets/audio'
OUT=ROOT/'reaper';OUT.mkdir(exist_ok=True)
RATE=44100

def read(name):
    with wave.open(str(ROOT/name)) as f:
        assert (f.getframerate(),f.getnchannels(),f.getsampwidth())==(RATE,1,2)
        return [v/32768 for v in array.array('h',f.readframes(f.getnframes()))]

blast=read('omacontra-start-impact.wav');shot=read('machine-gun-1.wav')
def destruction(name,duration,seed):
    """Broad pressure blasts and rolling debris, without metallic resonances."""
    rng=random.Random(seed);low=deep=air=0.;out=[]
    layers={
        'break':((0.,1.),(.075,.24)),
        'rupture':((0.,1.),(.18,.48),(.46,.42),(.92,.32),(1.65,.22)),
        'death_blast':((0.,1.),),
        'defeat':((0.,1.),(.15,.38),(.42,.22)),
    }[name]
    for i in range(round(duration*RATE)):
        t=i/RATE;n=rng.uniform(-1,1)
        # Wide, non-pitched layers: dark air, pressure body, deep turbulence.
        air+=.13*(n-air);low+=.026*(n-low);deep+=.008*(n-deep)
        value=0.
        for onset,gain in layers:
            age=t-onset
            if age<0:continue
            attack=min(1,age/.006)
            body_decay=4.8 if name in ('break','death_blast') else 2.5
            value+=gain*attack*(
                (air-low)*.7*math.exp(-age*28)
                +low*5.5*math.exp(-age*body_decay)
                +deep*9*math.exp(-age*(3 if name=='break' else 1.5)))
        # Smooth long release, rather than chopping a ringing short sample.
        out.append(value*min(1,max(0,(duration-t)/min(.75,duration*.5))))
    return out

# name, duration, peak dBFS, texture, priority (documented in mixer)
SOUNDS=[
 ('charge',.65,-36,'charge'),('sweep',.52,-30,'sweep'),
 ('skull',.24,-33,'skull'),('raven',.36,-34,'raven'),
 ('armor',.10,-42,'metal'),('impact',.11,-40,'impact'),
 ('break',1.05,-31,'destruction'),('expose',.48,-35,'release'),
 ('reform',.45,-36,'charge'),('hurt',.28,-31,'impact'),
 ('player_death',.8,-29,'blast'),('respawn',.3,-39,'release'),
 ('jump',.11,-43,'jump'),('land',.12,-43,'impact'),
 ('slide',.27,-42,'scrape'),('dash',.22,-38,'sweep'),
 ('rupture',4.0,-28,'destruction'),('death_blast',.55,-37,'destruction'),
 ('defeat',2.8,-29,'destruction')]
for seed,(name,duration,db,kind) in enumerate(SOUNDS):
    if name in PALETTE['reaper']:continue
    rng=random.Random(910+seed);low=deep=mid=0.;values=[];phase=0.
    for i in range(round(duration*RATE)):
        t=i/RATE;u=t/duration;n=rng.uniform(-1,1)
        low+=.045*(n-low);deep+=.011*(n-deep);mid+=.19*(n-mid)
        # Colored noise avoids harsh white-noise hiss. Resonances stay brief.
        attack=min(1,t/.004);decay=math.exp(-u*6)
        recorded=shot[min(len(shot)-1,int(i*.8))]*32 if i*.8<len(shot) else 0
        if kind in ('blast','collapse'):
            speed=.75 if kind=='collapse' else 1.15
            j=min(len(blast)-1,int(i*speed))
            value=blast[j]*.8+deep*2.4*math.exp(-u*3)
            if kind=='collapse':value+=low*.5*max(0,math.sin(t*43))*math.exp(-u*4)
        elif kind in ('sweep','release','charge'):
            envelope=(math.sin(math.pi*u)**1.3) if kind=='charge' else math.exp(-u*4)*min(1,t/.035)
            value=(low*3+mid*.25)*envelope
            phase+=math.tau*(100+160*(1-u))/RATE
            value+=math.sin(phase)*.055*envelope
        elif kind=='raven':
            # Three close wing beats, a low raspy edge, no piercing bird shriek.
            flap=sum(math.exp(-((t-c)/.025)**2) for c in (.025,.11,.19))
            value=(low*2+mid*.3)*flap+low*.4*decay
        elif kind=='skull':
            value=recorded*.4+low*2.4*decay
            value+=math.sin(math.tau*(105*t+25*(1-math.exp(-t*18))/18))*.1*decay
        elif kind=='metal':
            value=recorded*.14+sum(math.sin(math.tau*hz*t)*.09 for hz in (370,613,917))*decay+low*decay
        elif kind=='impact':value=recorded*.8+deep*4*decay+low*decay
        elif kind=='jump':value=low*2*decay+mid*.16*decay
        else:value=(low+mid*.25)*math.sin(math.pi*u)*math.exp(-u*2)
        values.append(value*attack*min(1,(duration-t)/.055))
    if kind=='destruction':values=destruction(name,duration,seed+1500)
    gain=10**(db/20)/max(map(abs,values))
    pcm=array.array('h',(round(v*gain*32767) for v in values))
    with wave.open(str(OUT/f'{name}.wav'),'wb') as f:
        f.setparams((1,2,RATE,0,'NONE','not compressed'));f.writeframes(pcm.tobytes())
print(f'Built {len(SOUNDS)} quiet Reaper effects in {OUT}')

build_bank('reaper')

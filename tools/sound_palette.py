"""Distinct sampled weapon/destruction palette; source masters and CC0 credits in audio/sources.
Builders call this after their movement/ambience pass. No shared synthesized thud.
"""
from pathlib import Path
from functools import lru_cache
import array,math,subprocess,wave
ROOT=Path(__file__).resolve().parents[1]/'assets/audio';RATE=44100

def layer(name,at=0,gain=1,speed=1,trim=0,length=None):
    return name,at,gain,speed,trim,length

# Every event has its own envelope and source combination. The alternate takes
# choose different source performances, not a randomized playback pitch.
PALETTE={
 'chase':{
  'mortar':(.50,-32,[layer('shot',length=.48)]),
  'cannon':(1.05,-30,[layer('shot',speed=.70,length=.8),layer('low',.025,.28,speed=1.2)]),
  'rockets':(.62,-34,[layer('thruster',speed=1.2,length=.6)]),
  'finisher':(.9,-31,[layer('thruster',gain=.85,length=.85),layer('shot',gain=.18,length=.10)]),
  'drone_fire':(.32,-39,[layer('laser',speed=1.1)]),
  'impact':(.095,-40,[layer('shot',speed=1.5,trim=.012,length=.095)]),
  'armor':(.085,-42,[layer('shot',speed=1.8,trim=.02,length=.08)]),
  'car_hit':(.40,-32,[layer('crunch',speed=1.4,length=.4)]),
  'component_break':(1.45,-31,[layer('crunch',gain=1),layer('laser',.055,.22,speed=.8)]),
  'drone_break':(.8,-35,[layer('laser',gain=.42,speed=.75),layer('crunch',.035,.7,speed=1.4,length=.70)]),
  'road_blast':(1.1,-33,[layer('low',gain=.65,speed=1.5),layer('crunch',gain=.6,speed=1.2,length=.7)]),
  'car_wreck':(3.0,-28,[layer('crunch'),layer('low',.02,.8,speed=.8),layer('crunch',.45,.32,speed=.9)]),
  'truck_break':(2.0,-29,[layer('crunch',speed=.85),layer('low',.06,.8),layer('crunch',.35,.45,speed=1.3)]),
  'robot_break':(4.0,-28,[layer('low',gain=.9,speed=.8),layer('crunch'),layer('crunch',.34,.65,speed=.8),layer('low',1.45,.32,speed=.9),layer('crunch',1.9,.20,speed=.85)])},
 'reaper':{
  'armor':(.085,-42,[layer('shot',speed=1.8,trim=.02,length=.08)]),
  'impact':(.095,-40,[layer('shot',speed=1.5,trim=.012,length=.095)]),
  'skull':(.40,-33,[layer('large_laser',speed=1.15,length=.4)]),
  'sweep':(.60,-30,[layer('thruster',speed=1.3,length=.6),layer('field',gain=.18,speed=1.2,length=.6)]),
  'break':(1.2,-31,[layer('crunch'),layer('laser',.06,.2)]),
  'eye_break':(1.35,-31,[layer('crunch'),layer('large_laser',.07,.23,speed=.65)]),
  'raven_break':(1.1,-33,[layer('field',speed=.8),layer('thruster',.04,.3,speed=1.4,length=.8)]),
  'player_death':(.85,-29,[layer('crunch',speed=1.25),layer('low',gain=.35,speed=1.6)]),
  'death_blast':(.65,-37,[layer('crunch',speed=1.25,length=.65)]),
  'rupture':(4.,-28,[layer('low',speed=.75),layer('crunch',gain=.85,speed=.8),layer('crunch',.55,.55),layer('low',1.5,.35),layer('crunch',2.05,.18,speed=.85)]),
  'defeat':(2.8,-29,[layer('low',speed=.8),layer('crunch',.12,.45,speed=.8)])}}
VARIED={bank:tuple(names) for bank,names in PALETTE.items()}

@lru_cache(maxsize=None)
def decode(filename):
    data=array.array('f',subprocess.check_output(['ffmpeg','-v','error','-i',str(filename),'-ac','1','-ar',str(RATE),'-f','f32le','-']))
    return data

@lru_cache(maxsize=None)
def source(kind,take):
    if kind=='shot':
        a=decode(ROOT/'sources/model12-recorded.wav')
        onset=(.895,7.046)[take%2];a=a[round(onset*RATE):round((onset+.85)*RATE)]
    else:
        prefixes={'crunch':'explosionCrunch','low':'lowFrequency_explosion','laser':'laserSmall','large_laser':'laserLarge','thruster':'thrusterFire','field':'forceField'}
        numbers={'crunch':(0,2,4,1,3),'low':(0,1,0),'laser':(1,2,4),'large_laser':(0,3,2),'thruster':(1,3,4),'field':(2,0,4)}
        a=decode(ROOT/'sources/kenney-scifi'/f'{prefixes[kind]}_{numbers[kind][take%len(numbers[kind])]:03}.ogg')
        # Remove only leading silence; keep the authored attack/body/tail.
        threshold=max(map(abs,a))*.015
        first=next((i for i,v in enumerate(a) if abs(v)>threshold),0)
        a=a[max(0,first-88):]
    peak=max(map(abs,a)) or 1
    return array.array('f',(v/peak for v in a))

def build_bank(bank):
    out=ROOT/bank;(out/'variants').mkdir(exist_ok=True)
    for name,(duration,db,layers) in PALETTE[bank].items():
        for take in range(3):
            values=[0.]*round(duration*RATE)
            for layer_index,(kind,at,gain,speed,trim,length) in enumerate(layers):
                a=source(kind,take+sum(map(ord,name))+layer_index);offset=round(at*RATE)
                count=min(len(values)-offset,round((len(a)/RATE-trim)/speed*RATE))
                if length is not None:count=min(count,round(length*RATE))
                for i in range(max(0,count-1)):
                    pos=trim*RATE+i*speed;j=int(pos)
                    if j+1>=len(a):break
                    fade=min(1,i/88,(count-i)/max(1,min(2205,count*.25)))
                    values[offset+i]+=(a[j]*(1-pos+j)+a[j+1]*(pos-j))*gain*fade
            # Light treble softening preserves the crack and textured decay.
            # Heavy low-pass filtering was responsible for the old dull thuds.
            low=dc=0.
            for i,v in enumerate(values):
                dc+=.002*(v-dc);low+=.48*(v-dc-low)
                values[i]=low*min(1,i/88,(len(values)-1-i)/2205)
            scale=10**(db/20)/max(map(abs,values))
            path=out/f'{name}.wav' if take==0 else out/'variants'/f'{name}-{take}.wav'
            with wave.open(str(path),'wb') as f:
                f.setparams((1,2,RATE,0,'NONE','not compressed'))
                f.writeframes(array.array('h',(round(v*scale*32767) for v in values)).tobytes())
    print(f'Rebuilt {bank} weapon/destruction palette with three takes per event')

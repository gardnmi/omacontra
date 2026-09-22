"""Short material-specific impacts; original synthesis plus credited water recordings."""
import array
import math
import random
import wave
from sound_palette import ROOT,RATE,decode
# Bank/event names preserve existing combat routing and destruction sounds.
EVENTS={
 'reaper':{'armor':'heavy','impact':'bone','eye_hit':'mechanical','raven_hit':'soft'},
 'chase':{'armor':'heavy','impact':'panel','heart_hit':'energy','drone_hit':'mechanical'},
 'tide':{'guardian_hit':'shell','suit_hit':'heavy','water_hit':'water'},
 'wyrm':{'core_hit':'crystal','scale_hit':'shell','laser_hit':'energy'},
 'finale':{'laser_hit':'gel','node_hit':'crystal'},
}
# Duration, resonant partials, decay seconds, noise texture weight.
MATERIALS={
 'heavy':(.13,(780,1395,2160),.023,.50),
 'panel':(.16,(465,1085,1810),.045,.65),
 'mechanical':(.13,(1530,2490,3910),.018,.55),
 'bone':(.105,(590,950),.013,1.2),
 'soft':(.105,(170,280),.017,.65),
 'shell':(.12,(850,1420),.014,1.1),
 'energy':(.18,(520,1030,1540),.055,.15),
 'crystal':(.18,(2140,3410,4670),.041,.25),
 'gel':(.16,(260,480),.035,.45),
}
def make(material,take):
 if material=='water':
  src=decode(ROOT/'sources/water/ezwa-water_splash'/f'water_splash-{take+1:02}.flac')
  peak=max(map(abs,src));start=next(i for i,v in enumerate(src) if abs(v)>peak*.04)
  return list(src[start:start+round(.15*RATE)])
 duration,freqs,decay,texture=MATERIALS[material]
 rng=random.Random(material+str(take));low=0.;values=[]
 detune=(.95,1.02,1.07)[take]
 for i in range(round(duration*RATE)):
  t=i/RATE;noise=rng.uniform(-1,1)
  low+=(.08 if material in ('soft','gel') else .35)*(noise-low)
  grain=low if material in ('soft','gel','panel') else noise-low
  # Separate tiny secondary chips/taps, not a long metallic ring.
  chips=sum(math.exp(-(t-at)/.009) for at in (.022+take*.003,.055-take*.004) if t>=at)
  body=0.
  for j,f in enumerate(freqs):
   glide=1+(.18*math.exp(-t*30) if material in ('gel','energy') else 0)
   body+=math.sin(math.tau*f*detune*t*glide)/(j+1)*math.exp(-t/decay)
  values.append(body*.35+grain*texture*(math.exp(-t/.013)+chips*.16))
 return values

def main():
 for bank,events in EVENTS.items():
  out=ROOT/bank;(out/'variants').mkdir(exist_ok=True)
  for name,material in events.items():
   for take in range(3):
    values=make(material,take);count=len(values)
    values=[v*min(1,i/90,(count-1-i)/400) for i,v in enumerate(values)]
    db=-36 if material in ('heavy','panel','bone','shell','water') else -37
    gain=32767*10**(db/20)/(max(map(abs,values)) or 1)
    path=out/f'{name}.wav' if take==0 else out/'variants'/f'{name}-{take}.wav'
    with wave.open(str(path),'wb') as f:
     f.setparams((1,2,RATE,0,'NONE','not compressed'))
     f.writeframes(array.array('h',(round(v*gain) for v in values)).tobytes())
if __name__=='__main__':main()

"""Short material-specific impacts; original synthesis plus credited water recordings."""
import array
import math
import random
import wave
import subprocess
from sound_palette import ROOT,RATE,decode,source
# Bank/event names preserve existing combat routing and destruction sounds.
EVENTS={
 'reaper':{'armor':'heavy','impact':'reaper_body','eye_hit':'reaper_eye','raven_hit':'soft'},
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
def recorded_metal(material,take):
 kind,speed,duration={'heavy':('heavy',1.12,.075),'panel':('medium',1.25,.068),'mechanical':('light',1.40,.060)}[material]
 source=ROOT/'sources/kenney-impact'/f'impactMetal_{kind}_{(0,2,4)[take]:03}.ogg'
 # Suppress the hollow container resonance; retain the recorded sharp transient.
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(source),'-af',
     'highpass=f=140,equalizer=f=650:t=q:w=0.8:g=-9,lowpass=f=4800',
     '-ac','1','-ar',str(RATE),'-f','f32le','-'])
 src=array.array('f',raw);peak=max(map(abs,src))
 start=max(0,next(i for i,v in enumerate(src) if abs(v)>peak*.045)-22)
 values=[]
 for i in range(round(duration*RATE)):
  pos=start+i*speed;j=int(pos)
  v=src[j]*(1-pos+j)+src[j+1]*(pos-j) if j+1<len(src) else 0
  # Fast dry decay ends before the next round lands; no bell-like sustain.
  values.append(v*math.exp(-i/RATE/ .019))
 return values

def reaper_damage(material,take):
 """Compact damage crunch with sustained bass; reference audio is not sampled."""
 eye=material=='reaper_eye';duration=.095 if eye else .10
 crack=source('crunch',take+(2 if eye else 0))
 bass=source('low',take)
 values=[];lp=low=0.;phase=0.
 for i in range(round(duration*RATE)):
  t=i/RATE
  j=min(len(crack)-1,round(i*(1.45 if eye else .82)))
  k=min(len(bass)-1,round(i*.8))
  # A falling low pulse gives the hit mass; a recorded crunch provides texture.
  phase+=math.tau*((195 if eye else 145)*math.exp(-t*13)+55)/RATE
  weight=math.sin(phase)*.35
  v=crack[j]*(.70 if eye else .43)+bass[k]*.65+weight
  low+=.045*(v-low)
  v=v*.6+low*.9
  lp+=(.31 if eye else .23)*(v-lp)
  v=math.tanh(lp*4)
  attack=min(1,t/.0015)
  # Hold the body for 30 ms before a short, smooth falloff. No ringing tone.
  tail=max(0,1-max(0,t-.03)/(duration-.03))**1.25
  values.append(v*attack*tail)
 return values

def make(material,take):
 if material in ('reaper_body','reaper_eye'):return reaper_damage(material,take)
 if material in ('heavy','panel','mechanical'):return recorded_metal(material,take)
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
    db=-34 if material=='reaper_body' else -35 if material=='reaper_eye' else -39 if material in ('heavy','panel','mechanical') else -36 if material in ('heavy','panel','bone','shell','water') else -37
    gain=32767*10**(db/20)/(max(map(abs,values)) or 1)
    path=out/f'{name}.wav' if take==0 else out/'variants'/f'{name}-{take}.wav'
    with wave.open(str(path),'wb') as f:
     f.setparams((1,2,RATE,0,'NONE','not compressed'))
     f.writeframes(array.array('h',(round(v*gain) for v in values)).tobytes())
if __name__=='__main__':main()

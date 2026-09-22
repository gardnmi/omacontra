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
 'chase':{'armor':'vehicle_armor','impact':'vehicle_panel','heart_hit':'robot_heart','drone_hit':'drone'},
 'tide':{'guardian_hit':'guardian_shell','suit_hit':'guardian_suit','water_hit':'wave'},
 'wyrm':{'core_hit':'dragon_core','scale_hit':'dragon_scale','laser_hit':'dragon_laser'},
 'finale':{'laser_hit':'jellyfish','node_hit':'space_node'},
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

# Duration, texture, playback speed, pulse pitch, texture/body mix, low-pass,
# take offset. Each target gets its own weight and texture, with no ringing tail.
WEIGHTED={
 'vehicle_armor':(.080,'crunch',1.12,170,.65,.65,.29,1),
 'vehicle_panel':(.080,'crunch',.72,125,.52,.72,.24,3),
 'robot_heart':(.095,'field',1.65,205,.50,.62,.33,2),
 'drone':(.080,'crunch',1.75,225,.72,.55,.36,4),
 'guardian_shell':(.100,'crunch',.94,150,.62,.65,.25,2),
 'guardian_suit':(.100,'crunch',.65,110,.47,.80,.20,4),
 'wave':(.115,'water',1.5,115,.85,.50,.30,0),
 'dragon_core':(.100,'crunch',1.95,250,.72,.54,.38,3),
 'dragon_scale':(.100,'crunch',.76,130,.67,.72,.26,1),
 'dragon_laser':(.110,'field',1.12,175,.65,.64,.29,4),
 'space_node':(.100,'field',2.1,265,.65,.56,.36,1),
}

def weighted_impact(material,take):
 duration,kind,speed,pitch,texture_gain,bass_gain,cutoff,offset=WEIGHTED[material]
 speed*=(.97,1.,1.04)[take];pitch*=(.96,1.,1.05)[take]
 if kind=='water':
  raw=decode(ROOT/'sources/water/ezwa-water_splash'/f'water_splash-{take+1:02}.flac')
  peak=max(map(abs,raw));start=next(i for i,v in enumerate(raw) if abs(v)>peak*.04)
  texture=[v/peak for v in raw[start:]]
 else:texture=source(kind,take+offset)
 bass=source('low',take+offset)
 values=[];low=lp=phase=0.
 for i in range(round(duration*RATE)):
  t=i/RATE
  phase+=math.tau*(pitch*math.exp(-t*13)+50)/RATE
  v=texture[min(len(texture)-1,round(i*speed))]*texture_gain
  v+=bass[min(len(bass)-1,round(i*.8))]*bass_gain+math.sin(phase)*.35
  low+=.045*(v-low)
  lp+=cutoff*(v*.6+low*.9-lp)
  tail=max(0,1-max(0,t-.028)/(duration-.028))**1.25
  values.append(math.tanh(lp*4)*min(1,t/.0015)*tail)
 return values

def electrical_contact(take):
 """Dry broadband arc/static, with irregular sputters instead of a wet thud."""
 rng=random.Random(7319+take)
 duration=.11;values=[];low=high=0.;flutter=1.
 for i in range(round(duration*RATE)):
  t=i/RATE
  noise=rng.uniform(-1,1)
  # Band-limit the fizz: no piercing top end or booming low-frequency pulse.
  low+=.42*(noise-low);high+=.035*(low-high)
  if i%round(.003*RATE)==0:flutter=rng.uniform(.70,1.)
  static=math.tanh((low-high)*7)*flutter
  # A few short arcing snaps sit in a continuous bed of electrical grain.
  crackle=sum(math.exp(-(t-at)/.0025) for at in (.008,.032+take*.002,.061) if t>=at)
  tail=max(0,1-max(0,t-.035)/(duration-.035))**1.1
  values.append(static*(.8+.2*min(1,crackle))*min(1,t/.001)*tail)
 return values

def make(material,take):
 if material=='jellyfish':return electrical_contact(take)
 if material in WEIGHTED:return weighted_impact(material,take)
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
    db=-35 if material in WEIGHTED or material=='jellyfish' else -34 if material=='reaper_body' else -35 if material=='reaper_eye' else -39 if material in ('heavy','panel','mechanical') else -36 if material in ('heavy','panel','bone','shell','water') else -37
    gain=32767*10**(db/20)/(max(map(abs,values)) or 1)
    path=out/f'{name}.wav' if take==0 else out/'variants'/f'{name}-{take}.wav'
    with wave.open(str(path),'wb') as f:
     f.setparams((1,2,RATE,0,'NONE','not compressed'))
     f.writeframes(array.array('h',(round(v*gain) for v in values)).tobytes())


def build_space_contact_loops():
 """Two-second seamless textures; no per-hit envelope or rhythmic retrigger."""
 out=ROOT/'finale/loops';out.mkdir(exist_ok=True)
 for kind in ('shield','flesh'):
  rng=random.Random(908 if kind=='shield' else 1908)
  count=RATE*2;values=[];low=high=wet=0.
  for i in range(count):
   t=i/RATE;noise=rng.uniform(-1,1)
   low+=.34*(noise-low);high+=.025*(low-high);wet+=.007*(noise-wet)
   # Continuous static over a restrained electrical carrier. Exposed tissue
   # adds a thick, noise-driven squelch, without discrete pops or beat pulses.
   if kind=='shield':v=math.tanh((low-high)*5)*.72+math.sin(math.tau*173*t)*.16
   else:v=math.tanh((low-high)*4)*.40+math.tanh(wet*22)*.65
   values.append(v)
  # Crossfade the wrap and rotate it inside the file: sample zero isn't a
  # special attack, and crossing the loop boundary never inserts silence.
  fade=RATE//10
  for i in range(fade):
   u=i/fade;values[i]=values[count-fade+i]*(1-u)+values[i]*u
  values=values[:count-fade]
  peak=max(map(abs,values));gain=32767*10**(-35/20)/peak
  with wave.open(str(out/f'{kind}.wav'),'wb') as f:
   f.setparams((1,2,RATE,0,'NONE','not compressed'))
   f.writeframes(array.array('h',(round(v*gain) for v in values)).tobytes())

if __name__=='__main__':
 main()
 build_space_contact_loops()

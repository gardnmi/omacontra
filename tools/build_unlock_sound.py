"""Original bright rising metallic chime for the secret-code unlock."""
from pathlib import Path
import math,random,struct,wave
rate=44100;duration=2.;rng=random.Random(71);values=[];phase=0.;low=0.
for i in range(round(rate*duration)):
 t=i/rate
 phase+=math.tau*(700+1600*min(1,t/.18))/rate
 n=rng.uniform(-1,1);low+=.15*(n-low)
 sweep=math.sin(phase)*.15*math.exp(-t*15)+(n-low)*.12*math.exp(-t*20)
 ring=0.
 for delay,freq in ((.02,1046.5),(.075,1318.5),(.13,1568),(.19,2093)):
  u=t-delay
  if u>=0:
   env=min(1,u/.004)*math.exp(-u*3.1)
   ring+=env*(math.sin(math.tau*freq*u)+.25*math.sin(math.tau*freq*2.013*u))*.18
 values.append((sweep+ring)*min(1,(duration-t)/.25))
peak=max(map(abs,values));path=Path(__file__).resolve().parents[1]/'assets/audio/unlimited-lives-unlock.wav'
with wave.open(str(path),'wb') as f:
 f.setparams((1,2,rate,0,'NONE','not compressed'))
 f.writeframes(b''.join(struct.pack('<h',round(v/peak*.72*32767)) for v in values))
print(path)

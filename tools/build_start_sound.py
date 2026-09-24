"""Build an original cinematic arcade explosion, without external samples."""
from pathlib import Path
import math, random, struct, wave

rate=44100;duration=2.35;rng=random.Random(17)
low=mid=deep=0.;phase=0.;dry=[]
for i in range(round(rate*duration)):
    t=i/rate;n=rng.uniform(-1,1)
    # Fast pressure crack, broad turbulent blast, descending sub-bass and debris.
    low += .055*(n-low);mid += .32*(n-mid);deep += .008*(n-deep)
    phase += math.tau*(34+88*math.exp(-t*18))/rate
    attack=min(1,t/.003)
    crack=(mid-low)*2.8*math.exp(-t*23)
    blast=low*4.5*math.exp(-t*3.7)*(1+.22*math.sin(t*83))
    thump=math.sin(phase)*.70*math.exp(-t*5.2)
    rumble=deep*5.5*math.exp(-t*1.7)*(1-math.exp(-t*25))
    debris=mid*.42*math.exp(-t*3)*(max(0,math.sin(t*109))*max(0,math.sin(t*43)))
    dry.append(math.tanh((crack+blast+thump+rumble+debris)*attack))
samples=[]
for i,value in enumerate(dry):
    # Diffuse short reflections give the blast size; longer taps carry the tail.
    for delay,gain in ((.047,.20),(.091,.17),(.157,.14),(.263,.12),(.419,.10),(.631,.07)):
        j=i-round(delay*rate)
        if j>=0:value+=dry[j]*gain
    t=i/rate
    samples.append(value*min(1,max(0,(duration-t)/.55)))
peak=max(map(abs,samples))
# Keep the blast/tail intact, but soften this isolated menu cue by 12 dB.
# Bake the trim into the shared asset so desktop and browser playback agree.
start_gain=10**(-12/20)
path=Path(__file__).resolve().parents[1]/'assets/audio/omacontra-start-impact.wav'
with wave.open(str(path),'wb') as out:
    out.setparams((1,2,rate,0,'NONE','not compressed'))
    out.writeframes(b''.join(struct.pack('<h',round(v/peak*.89*start_gain*32767)) for v in samples))
print(path)

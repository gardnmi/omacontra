"""Quiet short rifle reports from CC0 recorded AK-47 fire, not synthesis.
Source/credits: assets/audio/sources/README.md. Requires ffmpeg to decode master.
"""
from pathlib import Path
import array,math,struct,subprocess,wave
root=Path(__file__).resolve().parents[1]/'assets/audio';rate=44100
master=root/'sources/ak47-recorded-burst.wav'
a=array.array('f',subprocess.check_output([
 'ffmpeg','-v','error','-i',str(master),'-ac','1','-ar',str(rate),'-f','f32le','-']))
# Different real rounds from the recording retain natural acoustic variation.
for variant,center in enumerate((.2754,.461,.6465,.9159,1.1015,5.7509),1):
 lo=int((center-.008)*rate);hi=int((center+.008)*rate)
 peak=max(range(lo,hi),key=lambda i:abs(a[i]));start=peak-round(.004*rate)
 values=[];dc=low=0.
 for i in range(round(rate*.074)):
  t=i/rate;v=a[start+i]
  # Remove subsonic rumble and soften the upper crack without replacing it.
  dc+=.012*(v-dc);low+=.40*((v-dc)-low)
  envelope=min(1,t/.0008)*min(1,max(0,(.074-t)/.022))
  values.append(low*envelope)
 maximum=max(map(abs,values))
 gain=10**(-29/20)*(1-(variant%3)*.025)/maximum
 with wave.open(str(root/f'machine-gun-{variant}.wav'),'wb') as out:
  out.setparams((1,2,rate,0,'NONE','not compressed'))
  out.writeframes(b''.join(struct.pack('<h',round(v*gain*32767)) for v in values))
print('Built six recorded rifle shots: 74 ms, peak at or below -29 dBFS.')

# Deeper automatic-fire recording: resample down about two semitones and
# lift the low body without synthesizing an extra tone. Keep the mix quiet.
pitch_ratio=.88
start=round(.267*rate);source_count=round(.826*rate)
count=round(source_count/pitch_ratio);dc=low=bass=sub=0.;values=[]
bass_alpha=1-math.exp(-2*math.pi*240/rate)
sub_alpha=1-math.exp(-2*math.pi*70/rate)
for i in range(count):
 position=start+min(source_count-1,i*pitch_ratio)
 index=int(position);fraction=position-index
 v=a[index]*(1-fraction)+a[index+1]*fraction
 # Retain low-end punch, discard subsonic rumble, soften the upper crack.
 dc+=.003*(v-dc);low+=.24*((v-dc)-low)
 bass+=bass_alpha*(low-bass)
 sub+=sub_alpha*(low-sub)
 # Emphasize the recording's 70–240 Hz impact and reduce the upper report.
 # Less compression preserves each transient instead of a constant rumble.
 value=math.tanh((.6*low+4.5*(bass-sub))*2)
 values.append(value)
# End just before the next recorded round: no trailing silence/burst pause.
# Join the quiet inter-shot tails without fading the whole firing loop.
seam=round(.002*rate)
join=(values[0]+values[-1])*.5
for i in range(seam):
 blend=i/seam
 values[i]=join*(1-blend)+values[i]*blend
 values[-1-i]=join*(1-blend)+values[-1-i]*blend
gain=10**(-34/20)/max(map(abs,values))
with wave.open(str(root/'machine-gun-burst.wav'),'wb') as out:
 out.setparams((1,2,rate,0,'NONE','not compressed'))
 out.writeframes(b''.join(struct.pack('<h',round(v*gain*32767)) for v in values))
print('Built bassier automatic-fire burst: pitch 88%, peak -34 dBFS.')

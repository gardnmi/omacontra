"""Original soft arcade UI tones: no sampled impacts or metal-hit layers."""
from pathlib import Path
import array
import math
import wave
ROOT=Path(__file__).resolve().parents[1]/'assets/audio/menu'
# Each note: delay, pitch, duration. Rounded attacks keep fast navigation gentle.
CUES={
 'move':[(0,330,.085)],
 'adjust':[(0,440,.075)],
 'confirm':[(0,330,.14),(.065,495,.18)],
 'back':[(0,330,.11),(.055,220,.14)],
 'open':[(0,165,.22),(.045,330,.20)],
 'complete':[(0,262,.26),(.10,330,.28),(.20,392,.30),(.32,524,.40)],
}
def main():
 ROOT.mkdir(parents=True,exist_ok=True)
 for name,notes in CUES.items():
  duration=max(at+length for at,_,length in notes)+.015
  pcm=[0.]*round(duration*44100)
  for at,pitch,length in notes:
   for i in range(round(length*44100)):
    t=i/44100;u=t/length
    envelope=min(1,t/.008)*(1-u)**2
    phase=math.tau*pitch*t
    value=(math.sin(phase)+.16*math.sin(phase*2)+.035*math.sin(phase*3))*envelope
    pcm[round(at*44100)+i]+=value
  peak=10**((-35 if name in ('complete','confirm') else -39)/20)*32767
  scale=peak/max(map(abs,pcm))
  with wave.open(str(ROOT/f'{name}.wav'),'wb') as out:
   out.setparams((1,2,44100,0,'NONE','not compressed'))
   out.writeframes(array.array('h',(round(v*scale) for v in pcm)).tobytes())
if __name__=='__main__':main()

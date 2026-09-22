"""Quiet air and distant thunder. No recycled laser, thruster or metallic samples."""
from pathlib import Path
import array,math,subprocess,wave,shutil
ROOT=Path(__file__).resolve().parents[1]/'assets/audio'
OUT=ROOT/'wyrm';OUT.mkdir(exist_ok=True)
RATE=44100

def source(name):
 return array.array('f',subprocess.check_output(['ffmpeg','-v','error','-i',str(ROOT/'sources/storm'/name),'-ac','1','-ar',str(RATE),'-f','f32le','-']))
wind=source('wind.wav');thunder=source('thunder.ogg')
# Peak levels are before the common +5 dB mixer gain. Air is short and soft;
# thunder retains a longer low tail. The laser itself makes no repeating noise.
for name,duration,db,clip,start,speed in (
 ('gust',.7,-42,wind,.8,1.),('breath',1.0,-40,wind,1.0,.8),
 ('core_hit',.10,-48,wind,1.8,1.2),('disarm',1.25,-38,thunder,.05,1.1),
 ('pickup',.4,-45,wind,1.1,1.2),('lava',2.0,-45,wind,.7,.7),
 ('defeat',2.9,-37,thunder,.05,.9),('rescue_blast',3.0,-36,thunder,.05,.8),
 ('thunder',3.8,-42,thunder,0,1.),
 ('eye_charge',.85,-35,wind,1.15,.65),
 ('eye_shot',.38,-30,thunder,.12,1.8),
 ('eye_lance',.72,-31,thunder,.08,1.15),
 ('storm_hit',.20,-34,thunder,.20,1.5)):
 values=[];low=dc=0
 for i in range(round(duration*RATE)):
  t=i/RATE;pos=(start+t*speed)*RATE;j=int(pos)
  v=clip[j]*(1-pos+j)+clip[j+1]*(pos-j) if j+1<len(clip) else 0
  dc+=.001*(v-dc);low+=(.095 if clip is wind else .055)*(v-dc-low)
  attack=.008 if name in ('eye_shot','eye_lance','storm_hit') else .035 if name=='core_hit' else .10
  envelope=min(1,t/attack,(duration-t)/min(.55,duration*.45))
  if name=='eye_charge':envelope*=.15+.85*(t/duration)**2
  values.append(low*max(0,envelope))
 gain=10**(db/20)/(max(map(abs,values)) or 1)
 with wave.open(str(OUT/f'{name}.wav'),'wb') as f:
  f.setparams((1,2,RATE,0,'NONE','not compressed'));f.writeframes(array.array('h',(round(v*gain*32767) for v in values)).tobytes())
# Preserve the player's previously accepted movement cues.
for name in ('jump','land','slide','dash','hurt','player_death','respawn'):
 shutil.copy2(ROOT/'reaper'/f'{name}.wav',OUT/f'{name}.wav')
print('Built 20 mist encounter effects; recorded wind/thunder, no metallic hits')

"""Tidebreaker: water recordings, projectile-specific samples and quiet deck foley."""
from sound_palette import PALETTE,build_bank,layer,ROOT,RATE,decode
import array,math,random,wave,shutil
out=ROOT/'tide';out.mkdir(exist_ok=True);(out/'variants').mkdir(exist_ok=True)
# Sampled guardian weapons use the established palette tools, not one common thud.
PALETTE['tide']={
 'pistol':(.30,-35,[layer('shot',speed=1.2,length=.29)]),
 'orbit':(.38,-35,[layer('large_laser',speed=1.0,length=.38)]),
 'relay':(.85,-32,[layer('field',gain=.4),layer('large_laser',gain=.8,speed=.8)]),
 'stars':(.70,-35,[layer('field',speed=1.1),layer('laser',gain=.3)]),
 'star_fall':(.40,-39,[layer('thruster',length=.4,speed=1.5)]),
 'star_impact':(.55,-35,[layer('laser',gain=.6,speed=.75),layer('crunch',gain=.25,speed=1.5,length=.5)]),
 'jet':(.75,-36,[layer('thruster',length=.75)]),
 'slam':(.9,-31,[layer('low',speed=1.6),layer('crunch',gain=.25,length=.4)]),
 'guardian_hit':(.095,-40,[layer('shot',speed=1.6,trim=.012,length=.095)]),
 'coat_death':(1.6,-30,[layer('crunch',speed=.85),layer('field',gain=.25)]),
 'orbit_death':(2.5,-29,[layer('low'),layer('large_laser',.05,.55,speed=.7),layer('crunch',.22,.4)]),
 'rage_coat':(2.7,-33,[layer('field',speed=.6),layer('large_laser',1.1,.6,speed=.6)]),
 'rage_orbit':(2.7,-33,[layer('thruster',length=2.6),layer('field',1.1,.6,speed=.8)]),
 'thunder':(2.2,-43,[layer('low',speed=.65)])}
build_bank('tide')
water=ROOT/'sources/water'
for name,duration,db in [('surge',1.25,-33),('breaker',1.7,-31),('water_crash',1.9,-30),('water_hit',.16,-43),('wave_death',3.5,-29),('land',.19,-41)]:
 for take in range(3):
  short=decode(water/'ezwa-water_splash'/f'water_splash-{take+1:02}.flac')
  short_peak=max(map(abs,short)) or 1
  long=decode(water/'ocean-splash.ogg')
  src=short if name in ('water_hit','land') else long
  peak=max(map(abs,src));threshold=peak*.015
  start=max(0,next((i for i,v in enumerate(src) if abs(v)>threshold),0)-88)
  speed=(.85,1.,1.15)[take]*(.65 if name=='wave_death' else 1)
  values=[];low=dc=0.
  for i in range(round(duration*RATE)):
   pos=start+i*speed;j=int(pos)
   v=(src[j]*(1-pos+j)+src[j+1]*(pos-j))/peak if j+1<len(src) else 0
   # Small splashes distinguish individual water impacts from the main surge.
   if name not in ('water_hit','land') and i<len(short):v+=short[i]/short_peak*.15
   dc+=.002*(v-dc);low+=.5*(v-dc-low)
   values.append(low*min(1,i/88,(duration-i/RATE)/min(.6,duration*.3)))
  gain=10**(db/20)/(max(map(abs,values)) or 1)
  path=out/f'{name}.wav' if take==0 else out/'variants'/f'{name}-{take}.wav'
  with wave.open(str(path),'wb') as f:
   f.setparams((1,2,RATE,0,'NONE','not compressed'));f.writeframes(array.array('h',(round(v*gain*32767) for v in values)).tobytes())
# Brief dry wooden caster rattle; soft enough to remain incidental.
for name,duration,db in [('cargo',.23,-42),('cargo_bump',.3,-36),('deck_creak',.7,-44)]:
 rng=random.Random(71);values=[];low=0
 for i in range(round(duration*RATE)):
  t=i/RATE;low+=.13*(rng.uniform(-1,1)-low)
  envelope=sum(math.exp(-max(0,t-d)*70) if t>=d else 0 for d in (0,.035,.10,.17))
  value=low*envelope if name!='deck_creak' else low*.25*math.sin(math.pi*t/duration)**2*(.5+.5*math.sin(t*93))
  values.append(value*min(1,t/.002,(duration-t)/.04))
 gain=10**(db/20)/max(map(abs,values))
 with wave.open(str(out/f'{name}.wav'),'wb') as f:
  f.setparams((1,2,RATE,0,'NONE','not compressed'));f.writeframes(array.array('h',(round(v*gain*32767) for v in values)).tobytes())
for name in ('jump','slide','dash','hurt','player_death','respawn'):
 shutil.copy2(ROOT/'reaper'/f'{name}.wav',out/f'{name}.wav')
print('Built Tidebreaker water, guardian and deck effects')

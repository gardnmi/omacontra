"""Silent art/motion preview of intro and attacks using the actual game renderer."""
from pathlib import Path
import sys,subprocess,cairo
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from foundry import Foundry
from foundry_art import FoundryRenderer,FoundryIntro
ROOT=Path(__file__).resolve().parents[1];fps=24
r=FoundryRenderer();f=Foundry();intro=FoundryIntro()
s=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720);c=cairo.Context(s)
out=ROOT/'review/wyrm-mist-preview.mp4'
p=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pixel_format','bgra','-video_size','1280x720','-framerate',str(fps),'-i','-','-c:v','libx264','-preset','fast','-crf','22','-pix_fmt','yuv420p',str(out)],stdin=subprocess.PIPE)
for tick in range(int((intro.DURATION+12)*fps)):
 t=tick/fps
 if t<intro.DURATION:
  intro.age=t;intro.draw(c,r,f)
 else:
  age=t-intro.DURATION
  f.invuln=999
  if age>=5 and not f.laser:
   f.mount_hp=0;f.laser=True;f.lava_age=0
   f.support=f.platforms[0];f.x=345;f.y=f.floor
   f.forge_timer=0;f.forge_warning=None
  f.step(1/fps,shoot=False)
  r.draw(c,f)
 s.flush();p.stdin.write(s.get_data())
p.stdin.close();assert p.wait()==0
print(out)

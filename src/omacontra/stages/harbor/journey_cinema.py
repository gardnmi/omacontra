"""Shared black-screen cinematic strips for the harbor and ocean chapters."""
import copy
from omacontra.rendering import sprites
from omacontra.stages.reaper.battle_art import label
from omacontra.stages.highway.chase_cinema import smooth

HARBOR_LINES=(
    ('TOBI: THE CELLAR AI IS RUNNING ON A SPACE SERVER.',3.8),
    ('DHH: THEN WE NEED A SPACESHIP.',3.2),
    ('TOBI: THE LAUNCH SITE IS ACROSS THE WATER.',4.3),
    ('DHH: I TAKE THE FERRY. YOU FIND A WAY IN FROM SHORE.',4.6),
    ('TOBI: I WILL MEET YOU AT THE LAUNCH SITE.',3.6),
)
HARBOR_DURATION=sum(duration for _,duration in HARBOR_LINES)
INTRO_DURATION=HARBOR_DURATION+6.5

class JourneyCinema:
    def __init__(self,kind='intro'):
        self.kind=kind;self.age=0.
    @property
    def finished(self):return self.kind=='intro' and self.age>=INTRO_DURATION
    def step(self,dt):self.age+=max(0,min(.04,dt))
    def skip(self):
        if self.kind=='intro':self.age=INTRO_DURATION
    def draw(self,c,renderer,f):
        c.set_source_rgb(0,0,0);c.paint()
        if self.kind=='intro' and self.age<HARBOR_DURATION:
            elapsed=self.age
            for text,duration in HARBOR_LINES:
                if elapsed<duration:break
                elapsed-=duration
            x,y,w,h=100,180,1080,240
            c.save();c.rectangle(x,y,w,h);c.clip()
            sprites.draw(c,'journey-cinema.png',(0,685,1536,339),x,y,w,h)
            # Amber beacons and rain are independent from the illustrated panel.
            for i in range(35):
                xx=x+(i*71-self.age*35)%w;yy=y+(i*51+self.age*180)%h
                c.set_source_rgba(.7,.84,1,.2);c.move_to(xx,yy);c.line_to(xx-3,yy+7);c.stroke()
            c.restore()
            label(c,100,143,'THE HARBOR / THE ROAD TO ORBIT',14,'gold')
            label(c,100,505,text[:int(elapsed*38)],18)
            label(c,100,549,('A / SKIP TO THE CROSSING' if getattr(self,"controller_active",False) else 'ENTER / SKIP TO THE CROSSING'),11)
            return
        t=max(0,self.age-HARBOR_DURATION) if self.kind=='intro' else self.age
        opening=smooth((t-5)/1.5) if self.kind=='intro' else 0.
        x=100*(1-opening);y=150*(1-opening);w=1080+200*opening;h=320+400*opening
        c.save();c.rectangle(x,y,w,h);c.clip()
        scene=copy.copy(f);scene.clock=f.clock+t
        c.translate(x,y+h/2);c.scale(w/1280,w/1280);c.translate(0,-(460-100*opening))
        renderer.draw(c,scene,hud=False)
        c.restore()
        if opening<.9:
            label(c,100,142,'03 / TIDEBREAKER' if self.kind=='intro' else 'THE UPLINK FALLS SILENT',14,'gold')
            text='DHH / RADIO: TOBI... THE OCEAN IS MOVING WRONG.' if self.kind=='intro' else 'TOBI / RADIO: THE SHIP IS BEYOND THE MIST. I FOUND A WAY OVER.'
            label(c,100,505,text[:int(t*32)],18)
            label(c,100,549,('A / SKIP' if getattr(self,"controller_active",False) else 'ENTER / SKIP') if self.kind=='intro' else ('A / THE MIST GATE     VIEW / MENU' if getattr(self,"controller_active",False) else 'ENTER / THE MIST GATE     R / REPLAY     ESC / EXIT'),11)

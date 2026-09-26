"""Letterboxed close-ups bookend the Quattro encounter without advancing combat."""
import copy
import math
from omacontra.stages.reaper.battle_art import label, glow, color
from omacontra.rendering import sprites

PANEL=(160.,180.,960.,208.)
INTRO_DURATION=11.8
RALLY_PANEL=(120.,150.,1040.,347.)

def smooth(value):
    t=max(0.,min(1.,value));return t*t*(3-2*t)

class ChaseCinema:
    def __init__(self,kind='intro'):
        if kind not in ('intro','outro'):raise ValueError(kind)
        self.kind=kind;self.age=0.
    @property
    def finished(self):return self.kind=='intro' and self.age>=INTRO_DURATION
    def step(self,dt):self.age+=max(0,min(.04,dt))
    def skip(self):
        if self.kind=='intro':self.age=INTRO_DURATION
    def framing(self,f):
        """Return panel bounds, zoom, and world-space focal point."""
        if self.kind=='intro':
            opening=smooth((self.age-10.4)/1.4)
            # Hard cut from Tobi and DHH to the truck, then establish the full road.
            if self.age<8.0:zoom=2.65-min(self.age,2.8)*.10;cx,cy=f.x+12, f.y-86
            else:zoom=1.;cx,cy=640,465
            cx+=(640-cx)*opening;cy+=(360-cy)*opening;zoom+=(1-zoom)*opening
        else:
            opening=0.;zoom=1.;cx,cy=f.x+200+(640-f.x-200)*smooth(self.age/1.2),f.y-85
        x,y,w,h=PANEL
        return (x*(1-opening),y*(1-opening),w+(1280-w)*opening,h+(720-h)*opening),zoom,(cx,cy)
    def rally_pose(self):
        # Low, stationary camera: approach behind the crest, jump toward
        # the lens, then pass out of frame. Hermite tangents keep speed continuous.
        keys=((600,310,170),(585,285,230),(545,240,300),(485,230,390),
              (355,300,560),(135,415,780),(-240,525,1030),(-720,630,1250))
        t=max(0.,min(3.5,self.age-.45))*2
        i=min(len(keys)-2,int(t));u=t-i
        values=[]
        for axis in range(3):
            a=keys[i][axis];b=keys[i+1][axis]
            before=keys[max(0,i-1)][axis];after=keys[min(len(keys)-1,i+2)][axis]
            m0=(b-before)/2 if i else b-a
            m1=(after-a)/2 if i+2<len(keys) else b-a
            values.append((2*u**3-3*u*u+1)*a+(u**3-2*u*u+u)*m0+(-2*u**3+3*u*u)*b+(u**3-u*u)*m1)
        return (*values,.045*math.sin(min(1,t/7)*math.pi))

    def draw_rally(self,c,renderer,f):
        # Dedicated low three-quarter artwork, rather than a zoom of the road.
        x,y,w,h=RALLY_PANEL
        fade=smooth(self.age/.8)
        if fade<1:
            c.push_group();renderer.draw(c,f,hud=False)
            c.pop_group_to_source();c.paint_with_alpha(1-fade)
        c.save();c.rectangle(x,y,w,h);c.clip();c.translate(x,y);c.push_group()
        sprites.draw(c,'quattro-rally-cinema.png',(0,0,1536,510),0,0,w,h)
        cx,bottom,width,tilt=self.rally_pose();height=width*480/1000
        # The plume stays at the takeoff crest while the car advances toward
        # the lens. This depth cue prevents the jump reading as a floating cutout.
        strength=smooth((self.age-.5)/.5)*(1-smooth((self.age-3.7)/1.2))
        for i in range(55):
            age=(i/55+self.age*.42)%1
            px=625+math.sin(i*13)*age*150-age*35
            py=292-age*115+age*age*55
            glow(c,px,py,8+age*34,'red',strength*(1-age)*.23)
            color(c,'gold' if i%7==0 else 'smoke',strength*(1-age)*.8)
            c.rectangle(px,py,2+age*3,2+age*3);c.fill()
        c.save();c.translate(cx,bottom-height/2);c.rotate(tilt)
        sprites.draw(c,'quattro-rally-cinema.png',(260,520,1000,480),-width/2,-height/2,width,height)
        c.restore()
        # Foreground dirt masks the approach; clear the ridge before revealing
        # the undercarriage, preserving the low-angle wallpaper composition.
        reveal=smooth((self.age-.8)/.22)
        if reveal<1:
            c.save();c.move_to(0,275)
            for px,py in ((100,270),(270,263),(430,258),(590,266),(750,289),(900,319),(1040,328),(1040,347),(0,347)):
                c.line_to(px,py)
            c.close_path();c.clip()
            sprites.draw(c,'quattro-rally-cinema.png',(0,0,1536,510),0,0,w,h,alpha=1-reveal)
            c.restore()
        c.pop_group_to_source();c.paint_with_alpha(fade);c.restore()
        label(c,150,115,'ROADBLOCK DESTROYED',14,'gold')
        if self.age>4.1:
            text='TOBI: GOOD THING WE TOOK THE QUATTRO.'
            label(c,150,550,text[:int((self.age-4.1)*28)],19,'cream')
        if self.age>5.5:label(c,150,586,('A / CONTINUE TO THE HARBOR     VIEW / MENU' if getattr(self,"controller_active",False) else 'ENTER / CONTINUE TO THE HARBOR     R / REPLAY     ESC / EXIT'),11,'cream')

    def draw(self,c,renderer,f):
        c.set_source_rgb(0,0,0);c.paint()
        if self.kind=='outro':self.draw_rally(c,renderer,f);return
        scene=copy.copy(f)
        scene.clock=f.clock+self.age;scene.distance=f.distance+self.age*(700 if self.kind=='intro' else 450)
        scene.invuln=0.;scene.notice_time=0.;scene.warning=None;scene.muzzle=0.
        scene.shots=[];scene.particles=[];scene.obstacles=[];scene.drones=[]
        fade=smooth(self.age/.35)
        if 8.0<=self.age<10.4:
            t=(self.age-8.0)/2.4
            scene.boss_x=1100-250*smooth(t)
            scene.x=f.x+40*smooth(t)
            scene.boost=.5;scene.muzzle=.1
        (x,y,w,h),zoom,(cx,cy)=self.framing(scene)
        c.save();c.rectangle(x,y,w,h);c.clip();c.push_group()
        c.translate(x+w/2,y+h/2);c.scale(zoom,zoom);c.translate(-cx,-cy)
        renderer.draw(c,scene,hud=False)
        c.pop_group_to_source();c.paint_with_alpha(fade);c.restore()
        if self.kind=='intro' and self.age<10.4:
            text=('TOBI: DHH! FOUND THIS SWEET QUATTRO.' if self.age<3.8 else
                  'HOP IN. I THINK I KNOW HOW TO GET US OUT.' if self.age<8.0 else
                  'DHH: WE HAVE COMPANY.')
            elapsed=self.age if self.age<3.8 else self.age-3.8 if self.age<8.0 else self.age-8.0
            label(c,192,442,text[:int(elapsed*28)],17,'cream')
            label(c,192,138,'02 / QUATTRO RUN',12,'gold')
            label(c,192,480,('A / SKIP' if getattr(self,"controller_active",False) else 'ENTER / SKIP'),10,'cream')

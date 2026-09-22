"""Living industrial backdrop; all motion follows simulation time and stays behind combat.
Small cached smoke/light stamps avoid full-screen surfaces or per-frame filters.
Coordinates refer to the original 1774 x 887 arena painting.
"""
import math
import cairo
from omacontra.rendering import combat_fx as fx

class ReaperEnvironment:
    def __init__(self,stage):
        self.stage=stage
        self.smoke=cairo.ImageSurface(cairo.FORMAT_ARGB32,128,128)
        fx.smoke(cairo.Context(self.smoke),64,64,124,0,alpha=1,steam=True)
        self.lights=[]
        for rgb in ((1,.13,.035),(1,.40,.12)):
            surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,96,96)
            c=cairo.Context(surface);g=cairo.RadialGradient(48,48,0,48,48,48)
            g.add_color_stop_rgba(0,*rgb,.85);g.add_color_stop_rgba(.24,*rgb,.28)
            g.add_color_stop_rgba(1,*rgb,0);c.set_source(g);c.paint()
            self.lights.append(surface)

    @staticmethod
    def stamp(c,image,x,y,w,h,alpha):
        if alpha<=0:return
        c.save();c.translate(x-w/2,y-h/2);c.scale(w/image.get_width(),h/image.get_height())
        c.set_source_surface(image);c.get_source().set_filter(cairo.FILTER_BILINEAR)
        c.paint_with_alpha(alpha);c.restore()

    def cloth(self,c,t,x,y,w,h,phase):
        # Warp the existing painted fabric inside its silhouette, with the top
        # pinned to its rail; no second flag silhouette or new art style.
        c.save();c.rectangle(x,y,w,h);c.clip()
        for row in range(16):
            fraction=row/16;top=y+row*h/16
            sway=math.sin(t*1.55-fraction*4+phase)*3*fraction
            c.save();c.rectangle(x,top,w,h/16+.2);c.clip()
            c.translate(sway,0);c.set_source_surface(self.stage)
            c.get_source().set_filter(cairo.FILTER_BILINEAR);c.paint();c.restore()
        c.restore()

    def draw(self,c,f,x,y,w,h):
        c.save();c.rectangle(x,y,w,h);c.clip();c.translate(x,y);c.scale(w/1774,h/887)
        t=f.clock
        power=(max(.08,1-f.death_age/4.2) if f.state=='dying' else .08 if f.state=='won' else 1.)
        # Slow, asynchronous fabric motion makes the chamber feel drafty.
        self.cloth(c,t,64,88,80,270,0)
        self.cloth(c,t,1160,275,66,193,2)
        self.cloth(c,t,1574,274,62,167,4)
        surge=(.22 if f.warning=='scythe' else 0)+f.scythe_flash*.8
        for i,(lx,ly) in enumerate(((261,192),(481,191),(981,350),(1077,527),(1314,689),(1473,689))):
            flicker=.66+.17*math.sin(t*2.2+i*2)+.08*math.sin(t*17+i*5)
            if int(t*8+i*3)%37==0:flicker*=.35
            strength=min(1,(flicker+surge)*power)
            self.stamp(c,self.lights[0],lx,ly,115,145,.44*strength)
            # Pulse the light through the existing cage rather than covering it.
            c.set_source_rgba(1,.18,.06,.55*strength)
            for dy in (-9,0,9):c.rectangle(lx-2,ly+dy,3,5)
            c.fill()
        # Faint furnace light deep in the wall's skull, well above player fire.
        for lx in (1365,1417):
            self.stamp(c,self.lights[1],lx,154,57,40,(.22+.08*math.sin(t*1.7))*power)
        # Steam issues from actual pipe couplings. Four small puffs per vent;
        # deterministic ages keep pause/retry exact without particle allocation.
        for i,(vx,vy,direction) in enumerate(((685,493,-1),(1000,228,-1),(1279,356,1))):
            pressure=.35+.65*max(0,math.sin(t*.8+i*2))
            for j in range(4):
                age=(t*.32+j*.25+i*.21)%1
                alpha=math.sin(age*math.pi)*.20*pressure*(.45+.55*power)
                size=27+age*79
                px=vx+direction*(age*64)+math.sin(t*.8+j)*age*13
                py=vy-age*102
                self.stamp(c,self.smoke,px,py,size*1.3,size,alpha)
        # Condensation gathers on the cold pipe flanges, then falls into the
        # recess below. Pinpoints remain behind the combat plane.
        for i,(px,py) in enumerate(((685,499),(1000,234),(1279,362))):
            age=(t+i*.91)%2.7
            bead=min(1,age/1.9)
            c.set_source_rgba(.53,.65,.66,.32)
            c.rectangle(px,py,1.5,1+bead*2);c.fill()
            if age>1.9:
                fall=(age-1.9)/.8
                c.set_source_rgba(.60,.69,.68,.32*(1-fall))
                c.rectangle(px+fall*3,py+fall*fall*68,1,3+fall*3);c.fill()
        # Sparse ash drifts in the rear plane; no glow or hostile-shot colors.
        for i in range(26):
            px=(i*137.71+t*(6+i%4))%1774
            py=70+(i*89.31+t*(8+i%5))%605
            alpha=(.08+.07*math.sin(t*.7+i)**2)*(.5+.5*power)
            c.set_source_rgba(.70,.60,.47,alpha);c.rectangle(px,py,1.4,2);c.fill()
        # Brief sparks fall from two damaged upper cable joints, away from the floor.
        for i,(sx,sy) in enumerate(((555,285),(1533,244))):
            age=(t+i*3.2)%7.4
            if age>.65 or power<.2:continue
            for j in range(5):
                a=max(0,age-j*.035)
                px=sx+math.sin(j*7+i)*a*42;py=sy+18*a+95*a*a
                c.set_source_rgba(.86,.44,.16,(1-age/.65)*.6*power)
                c.set_line_width(1.2);c.move_to(px,py);c.line_to(px-1,py-3-a*6);c.stroke()
        c.restore()

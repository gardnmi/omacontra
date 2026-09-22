"""Harbor motion and wet-deck details; all animation follows simulation time."""
import math
import cairo
from omacontra.rendering import sprites
from omacontra.rendering import combat_fx as fx

class TideEnvironment:
    def __init__(self):
        self.worlds=[]
        for y in (0,632):
            surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,630)
            sprites.draw(cairo.Context(surface),'tidebreaker-worlds.png',(0,y,1247,629),0,0,1280,630)
            self.worlds.append(surface)
        # Downsample once instead of sampling a large effects atlas for every puff.
        self.mist=cairo.ImageSurface(cairo.FORMAT_ARGB32,96,96)
        fx.smoke(cairo.Context(self.mist),48,48,96,0,1,steam=True)

    def puff(self,c,x,y,size,alpha):
        c.save();c.translate(x-size/2,y-size/2);c.scale(size/96,size/96)
        c.set_source_surface(self.mist);c.paint_with_alpha(alpha);c.restore()

    def background(self,c,f):
        t=f.clock
        if f.stage:
            night=not all(a.hp>0 for a in f.guardians)
            # Confine displacement to open water; retain the pier and skyline.
            c.save();c.move_to(0,488);c.line_to(600,495);c.line_to(810,562)
            c.line_to(1280,580);c.line_to(1280,630);c.line_to(0,630);c.close_path();c.clip()
            for row in range(36):
                y=486+row*4
                dx=math.sin(t*1.7-row*.52)*(3+row*.13)
                c.save();c.rectangle(0,y,1280,4);c.clip()
                c.set_source_surface(self.worlds[int(night)],dx,0);c.paint();c.restore()
            c.restore()
            if not night:
                for x,y in ((920,254),(693,318),(364,415)):
                    for i in range(5):
                        age=(t*.23+i/5)%1
                        self.puff(c,x+age*68,y-age*86,16+age*64,.24*(1-age))
            # Tiny reflections follow real distant harbor fixtures.
            for i,(x,y) in enumerate(((34,465),(128,467),(258,476),(480,486),(744,510))):
                a=.12+.15*(.5+.5*math.sin(t*2+i*2))
                c.set_source_rgba(.45 if night else 1,.72 if night else .55,.85 if night else .25,a)
                for j in range(5):
                    width=3+j*1.4
                    c.rectangle(x+math.sin(t*2-j)*3-width/2,y+j*3,width,1.5)
                c.fill()
        # Low wind-torn sea mist at the edges, away from attacks and the core.
        for side in (0,1):
            for i in range(4):
                age=(t*.38+i*.25)%1
                x=(15+age*110) if side==0 else (1265-age*110)
                self.puff(c,x,f.deck_y(x)-12-age*25,38+age*60,(1-age)*(.22 if not f.stage else .10))

    def deck(self,c,f):
        t=f.clock
        c.save();c.translate(640,630+f.deck_roll);c.rotate(math.atan(f.deck_slope))
        # Ripples and glints sit in the deck's local coordinates, so they never
        # float or expose a wallpaper seam when the platform tilts.
        for i in range(32 if not f.stage else 14):
            age=(t*(1.8 if not f.stage else 1.2)+i*.381)%1
            x=(i*173)%1340-670;y=5+(i*19)%28
            c.save();c.translate(x,y);c.scale(1,.25)
            c.set_source_rgba(.69,.85,.91,(1-age)*.38);c.set_line_width(1)
            c.arc(0,0,2+age*10,0,math.tau);c.stroke();c.restore()
            if age<.23:
                c.set_source_rgba(.77,.9,.95,(1-age/.23)*.45)
                c.rectangle(x-3,y-4-age*20,1,3);c.rectangle(x+3,y-2-age*13,1,2);c.fill()
        # Water drains over the deck's lip. Gravity is converted into deck
        # coordinates, so the drops still fall vertically as the deck rolls.
        slope=math.atan(f.deck_slope)
        for i,x in enumerate((-540,-335,-105,145,365,550)):
            for j in range(2):
                age=(t*.72+i*.317+j*.5)%1
                drop=age*age*65
                dx=math.sin(slope)*drop;dy=math.cos(slope)*drop
                c.set_source_rgba(.60,.77,.81,(1-age)*(.32 if not f.stage else .20))
                c.set_line_width(1)
                c.move_to(x+dx,38+dy)
                c.line_to(x+dx+math.sin(slope)*5,38+dy+math.cos(slope)*5)
                c.stroke()
        c.restore()

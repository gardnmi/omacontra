"""Lightweight coastal atmosphere in world coordinates, behind all combat."""
import math
import cairo
from omacontra.rendering import sprites
from omacontra.rendering import combat_fx as fx

class CoastEnvironment:
    def __init__(self,road):
        self.scene=cairo.ImageSurface(cairo.FORMAT_RGB24,1280,720)
        sprites.paint_background(cairo.Context(self.scene),road,0,0,1280,720)
        # Isolate existing sunset-colored cloud pixels once. Moving these
        # transparent silhouettes cannot drag sky/sun pixels across a clip edge.
        self.cloud_banks=[]
        self.scene.flush();pixels=memoryview(self.scene.get_data());stride=self.scene.get_stride()
        for ox,oy in ((400,15),(770,65)):
            cloud=cairo.ImageSurface(cairo.FORMAT_ARGB32,360,100)
            data=memoryview(cloud.get_data());pitch=cloud.get_stride()
            for yy in range(100):
                for xx in range(360):
                    pos=(oy+yy)*stride+(ox+xx)*4
                    b,g,r=pixels[pos],pixels[pos+1],pixels[pos+2]
                    if r<220 or g>110 or not 50<b<195:continue
                    alpha=round(255*min(1,xx/28,(359-xx)/28,yy/12,(99-yy)/12))
                    out=yy*pitch+xx*4
                    data[out:out+4]=bytes((b*alpha//255,g*alpha//255,r*alpha//255,alpha))
            cloud.mark_dirty();self.cloud_banks.append(cloud)
        self.mist=cairo.ImageSurface(cairo.FORMAT_ARGB32,128,128)
        fx.smoke(cairo.Context(self.mist),64,64,124,0,alpha=1,steam=True)
        self.wisp=cairo.ImageSurface(cairo.FORMAT_ARGB32,128,128)
        cc=cairo.Context(self.wisp);cc.set_source_rgba(.54,.10,.36,1)
        cc.mask_surface(self.mist)

    def haze(self,c,x,y,w,h,alpha):
        c.save();c.translate(x,y);c.scale(w/128,h/128)
        c.set_source_surface(self.mist,-64,-64);c.paint_with_alpha(alpha);c.restore()

    def sun_clouds(self,c,t):
        """Cloud-only transparent artwork crosses the intact painted sun."""
        c.save()
        c.rectangle(885,220,395,120);c.clip();c.push_group()
        # Narrow banks cross at different speeds: they occlude the disc without
        # ever copying, clipping, or translating any of its yellow pixels.
        for row,(yy,speed,scale_y,alpha) in enumerate(((238,18,.38,.90),(282,25,.32,.84))):
            for i in range(3):
                xx=(i*600+t*speed+680+row*170)%1800-450
                c.save();c.translate(xx,yy);c.scale(1.6,scale_y)
                c.set_source_surface(self.cloud_banks[row]);c.get_source().set_filter(cairo.FILTER_NEAREST)
                c.paint_with_alpha(alpha);c.restore()
        c.pop_group_to_source()
        # Fade in over the open sky, keeping distant clouds behind the cliffs.
        mask=cairo.LinearGradient(885,0,985,0)
        mask.add_color_stop_rgba(0,0,0,0,0);mask.add_color_stop_rgba(1,0,0,0,1)
        c.mask(mask);c.restore()

    def draw(self,c,f):
        t=f.clock;_,top,_,bottom=c.clip_extents()
        c.save()
        # Substantial cloud banks move as independent artwork, not faint mist.
        # Repeat along each altitude so motion is visible throughout both phases.
        for row,yy in enumerate((-590,-415,-230,40,105)):
            if not top-80<yy<bottom+40:continue
            image=self.cloud_banks[row%2]
            for i in range(3):
                xx=(i*615+t*(19+row%2*7)+row*173)%1845-480
                c.save();c.translate(xx,yy);c.scale(1.42,.68)
                c.set_source_surface(image);c.get_source().set_filter(cairo.FILTER_NEAREST)
                c.paint_with_alpha(.70);c.restore()
        if top<314 and bottom>238:self.sun_clouds(c,t)
        if top<470 and bottom>340:
            # Reflected sunset ripples stay inside the sea, never across the cliffs.
            c.save();c.move_to(670,395)
            for p in ((860,354),(1280,348),(1280,365),(1130,446),(1020,468),(810,424)):c.line_to(*p)
            c.close_path();c.clip()
            # Move the painted wave/reflection texture in narrow rows. The
            # shift is coherent but varies with depth, making the sea roll.
            for row in range(28):
                yy=348+row*4.4
                shift=math.sin(t*1.55-row*.52)*(4+row*.35)
                c.save();c.rectangle(640,yy,640,4.4);c.clip()
                c.set_source_surface(self.scene,shift,0)
                c.get_source().set_filter(cairo.FILTER_NEAREST);c.paint();c.restore()
            for i in range(35):
                yy=355+i*3.1;xx=1060+math.sin(i*4.73+t*.9)*(16+i*.8)
                width=9+(i%5)*8+math.sin(t*1.3+i)*6
                c.set_source_rgba(1,.65,.30,.16+.13*math.sin(t*1.5+i)**2)
                c.rectangle(xx-width/2,yy,width,1.1);c.fill()
            # Smaller rose-colored swells in the open water left of the truck.
            for i in range(16):
                xx=720+(i*41+t*12)%325;yy=381+(i*13)%54
                c.set_source_rgba(1,.32,.48,.10+.09*math.sin(t*2+i)**2)
                c.rectangle(xx,yy,12+(i%4)*8,1.2);c.fill()
            # A far-off fishing boat rides the open sea, with a narrow wake
            # fading behind it. Its tiny silhouette never resembles a hazard.
            bx=890+(t*3.2)%190;by=375+math.sin(t*.9)*.7
            c.set_source_rgba(.22,.06,.24,.75)
            c.move_to(bx-7,by);c.line_to(bx+7,by);c.line_to(bx+4,by+3)
            c.line_to(bx-5,by+3);c.close_path();c.fill()
            c.rectangle(bx-2,by-3,3,3);c.fill()
            for j in range(5):
                c.set_source_rgba(1,.55,.40,.24*(1-j/5))
                c.rectangle(bx-10-j*6,by+2+math.sin(t*1.5-j)*.6,4,1);c.fill()
            for i in range(3):
                self.haze(c,810+i*160+math.sin(t*.17+i)*40,394+i*16,240,29,.085)
            c.restore()
            # Tiny existing shoreline lights twinkle asynchronously.
            for i,(x,y) in enumerate(((544,381),(564,379),(602,386),(640,356),(679,348),(708,349),(748,346),(789,345))):
                alpha=.18+.35*max(0,math.sin(t*.8+i*1.7))**3
                c.set_source_rgba(1,.60,.25,alpha);c.rectangle(x,y,1.6,1.8);c.fill()
        # Road-edge gusts follow road speed, with no particles crossing the gunner.
        if top<492 and bottom>450:
            for i in range(5):
                x=(i*297+f.distance*.6)%1500-110
                self.haze(c,x,481+(i%2)*4,135,20,.14)
        # Distant birds are tiny dark silhouettes high above the projectile lanes.
        if top<200 and bottom>20:
            c.set_source_rgba(.14,.04,.20,.85);c.set_line_width(1.0)
            for i in range(4):
                x=(t*27+i*29+400)%1450-70;y=125+i*7+math.sin(t*.8+i)*4
                flap=math.sin(t*5+i)*4
                c.move_to(x-6,y+flap);c.line_to(x,y);c.line_to(x+6,y+flap);c.stroke()
        c.restore()

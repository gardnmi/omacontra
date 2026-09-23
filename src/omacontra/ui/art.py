"""Arcade cinematics sharing the reaper level's artwork and metal/red palette."""
from omacontra.resources import ASSETS
import math
import cairo
from omacontra.rendering import sprites

W,H=960,540
CREAM=(.86,.84,.73)
GOLD=(.48,.43,.30)
RED=(.90,.24,.23)
INK=(.025,.03,.035)
COVER=ASSETS/'omacontra-cover-v2.png'


def box(c,x,y,w,h,color,alpha=1):
    c.set_source_rgba(*color,alpha);c.rectangle(x,y,w,h);c.fill()


def text(c,line,y,size=26,color=CREAM):
    c.select_font_face('monospace',cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(size)
    ext=c.text_extents(line);x=(W-ext.width)/2-ext.x_bearing
    c.set_source_rgba(0,0,0,.85);c.move_to(x+2,y+2);c.show_text(line)
    c.set_source_rgb(*color);c.move_to(x,y);c.show_text(line)


def picture(c,image,x=0,y=0,w=W,h=H):
    c.save();c.rectangle(x,y,w,h);c.clip();c.translate(x,y)
    # Cover the frame without distorting the illustrated pixel proportions.
    scale=max(w/image.get_width(),h/image.get_height())
    c.translate((w-image.get_width()*scale)/2,(h-image.get_height()*scale)/2)
    c.scale(scale,scale);c.set_source_surface(image);c.get_source().set_filter(cairo.FILTER_NEAREST);c.paint();c.restore()


def lamp(c,x,y,r=22,alpha=.5):
    g=cairo.RadialGradient(x,y,0,x,y,r)
    g.add_color_stop_rgba(0,*RED,alpha);g.add_color_stop_rgba(1,*RED,0)
    c.set_source(g);c.arc(x,y,r,0,math.tau);c.fill()
    box(c,x-1,y-2,2,4,RED)


def metal_frame(c,x,y,w,h):
    box(c,x,y,w,h,GOLD)
    box(c,x+2,y+2,w-4,h-4,INK)
    box(c,x+5,y+5,w-10,h-10,CREAM,.12)
    box(c,x+7,y+7,w-14,h-14,INK)
    for px in (x+4,x+w-7):
        for py in (y+4,y+h-7):
            box(c,px,py,3,3,CREAM,.65);box(c,px+1,py+1,1,1,INK)


class Renderer:
    def __init__(self):
        from omacontra.stages.reaper.battle_art import BattleRenderer
        from omacontra.stages.reaper.combat import Fight
        self.arrival_hero=Fight()
        self.arrival_renderer=BattleRenderer()
        self.cover=cairo.ImageSurface.create_from_png(str(COVER))
        self.stage=cairo.ImageSurface.create_from_png(str(ASSETS/'reaper-arena.png'))
        self.cellar=cairo.ImageSurface.create_from_png(str(ASSETS/'intro-cellar.png'))

    def atmosphere(self,c,t,dim=.45):
        picture(c,self.stage)
        box(c,0,0,W,H,INK,dim)
        # Sparse rising ash echoes the worn, mechanical boss arena.
        for i in range(19):
            x=(i*173+math.sin(t*.4+i)*8)%W;y=(i*61-t*(5+i%4))%H
            box(c,x,y,1+i%2,2,GOLD,.18+.22*(.5+.5*math.sin(t+i)))
        for x,y in ((W*.18,H*.52),(W*.83,H*.20),(W*.93,H*.65)):
            lamp(c,x,y,18,.12+.07*math.sin(t*2+x))

    def wine_cellar(self,c,t):
        c.save();zoom=1+min(t,6)*.006
        c.translate(W/2,H/2);c.scale(zoom,zoom);c.translate(-W/2,-H/2)
        picture(c,self.cellar)
        awakened=max(0,min(1,(t-1.5)/2.2))
        for i,(u,v) in enumerate(((.461,.369),(.541,.369),(.461,.478),(.541,.478),(.403,.37),(.584,.37),(.468,.587))):
            if (int(t*7)+i)%4:
                lamp(c,W*u,H*v,9+awakened*12,.18+awakened*.38)
        # Rotating fan spokes stay inside the cooler's illustrated fan housings.
        for u,v in ((.484,.395),(.517,.395),(.484,.495),(.517,.495)):
            c.save();c.translate(W*u,H*v);c.rotate(t*(3+awakened*5))
            for i in range(4):
                c.rotate(math.pi/2);box(c,2,-1,8,2,GOLD,.35)
            c.restore()
        c.restore()
        box(c,0,0,W,87,INK,.88);box(c,0,H-74,W,74,INK,.88)
        text(c,'TRANSMISSION SOURCE / PRIVATE CELLAR',30,11,GOLD)
        text(c,'IN TOBI LUTKE\'S WINE CELLAR.',65,25)
        if t>2.4:text(c,'CONTAINMENT STATUS: UNCORKED',H-42,16,RED)

    def story_card(self,c,intro):
        kind,t=intro.beat.kind,intro.age
        self.atmosphere(c,t,.53 if kind!='threat' else .68)
        text(c,'OMACONTRA / INCIDENT ARCHIVE',52,12,GOLD)
        # Riveted dark plate leaves the lettering readable against detailed scenery.
        metal_frame(c,99,164,W-198,205)
        box(c,111,176,3,181,RED,.7)
        titles={'story':'01 / THE FORECAST','containment':'02 / LOCKDOWN','labs':'03 / WATCHLIST','threat':'04 / WRONG TARGET','resolve':'05 / THE ANSWER'}
        text(c,titles[kind],198,11,RED)
        if kind=='resolve':
            for i,line in enumerate(intro.typed_lines):text(c,line,258+i*53,25 if i==0 else 29)
        else:
            for i,line in enumerate(intro.typed_lines):text(c,line,263+i*44,25,RED if kind=='threat' else CREAM)
        if kind=='containment':
            travel=min(1,t/1.7)*40
            for x in (35+travel,W-53-travel):
                metal_frame(c,x,116,18,302)
                for y in range(133,402,21):box(c,x+5,y,8,3,GOLD)
        if kind=='labs':
            for x in (218,555):
                box(c,x,392,186,3,GOLD,.45);box(c,x+(t*44)%176,392,10,3,RED)
        if kind=='threat':
            for x in (78,W-78):lamp(c,x,264,58,.22+.12*math.sin(t*3))
        if kind=='resolve' and t>2:box(c,220,391,520,2,GOLD,.7)

    def title(self,c,t,start_age=None):
        self.atmosphere(c,t,.40)
        h=H-57;w=self.cover.get_width()*h/self.cover.get_height()
        x=(W-w)/2;y=15
        metal_frame(c,x-9,y-9,w+18,h+18)
        picture(c,self.cover,x,y,w,h)
        if start_age is not None:
            # Blink only the baked-in PRESS START area, leaving both heroes visible.
            if int(start_age/.085)%2:
                box(c,x+w*.225,y+h*.912,w*.55,h*.031,INK,.98)
            if start_age>2.15:box(c,x,y,w,h,INK,min(1,(start_age-2.15)/.25))
        for side in (-1,1):
            lamp(c,W/2+side*(w/2+25),H*.55,38,.25+.08*math.sin(t*2))
        text(c,'ENTER / START     R / REPLAY INTRO',H-13,11,CREAM)
        if t<.22:box(c,0,0,W,H,CREAM,.85*(1-t/.22))

    def unlock_banner(self,c,intro):
        from omacontra.rendering.health_medals import insignia
        t=intro.unlock_age if intro.unlock_age is not None else 99
        mint=(.68,.90,.53);pale=(.88,1.,.77)
        if t<3.4:
            y=370+55*(1-min(1,t/.22))**2;x=285;w=390;h=76
            box(c,x-5,y-5,w+10,h+10,mint,.08)
            box(c,x,y,w,h,(.018,.065,.045),.97)
            box(c,x,y,w,2,mint);box(c,x,y+h-2,w,2,mint)
            for xx in (x,x+w-2):box(c,xx,y,2,h,mint,.7)
            insignia(c,x+17,y+18,39,mint)
            c.select_font_face('monospace',cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_BOLD)
            c.set_source_rgb(*pale);c.set_font_size(20);c.move_to(x+76,y+32);c.show_text('UNLIMITED LIVES')
            c.set_source_rgb(*mint);c.set_font_size(14);c.move_to(x+76,y+56);c.show_text('A C T I V A T E D')
            # A short bright scan travels across the unlocked badge.
            sweep=(t/.65)%1
            if t<1.3:box(c,x+w*sweep,y+3,3,h-6,pale,.45)
            for j in range(12):
                a=j*math.tau/12;radius=25+t*85
                box(c,W/2+math.cos(a)*radius,y+h/2+math.sin(a)*radius*.4,2,2,mint,max(0,.75-t))
        else:
            insignia(c,756,225,36,mint)
            c.select_font_face('monospace',cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_BOLD)
            c.set_source_rgb(*mint);c.set_font_size(12)
            for yy,line in ((279,'UNLIMITED'),(296,'LIVES ACTIVE')):
                c.move_to(731,yy);c.show_text(line)

    def cinematic_strip(self,c,intro):
        kind,t=intro.beat.kind,intro.age
        x,y,w,h=64,140,832,188
        c.save();c.rectangle(x,y,w,h);c.clip()
        if kind in ('story','cellar','demonstration'):
            sprites.draw(c,'journey-cinema.png',(0,0,1536,346),x,y,w,h)
            for u,v in ((.455,.17),(.455,.43),(.455,.66)):
                lamp(c,x+w*u,y+h*v,7,.15+.13*math.sin(t*7))
        elif kind in ('portal','separated'):
            shake=math.sin(t*29)*2 if kind=='portal' else 0
            sprites.draw(c,'journey-cinema.png',(0,352,1536,325),x+shake,y,w,h)
            c.set_source_rgba(.25,.85,1,.07+.06*math.sin(t*11));c.paint()
            for i in range(36):
                age=(i/36+t*.35)%1;xx=x+w/2+(i%2*2-1)*age*w*.55
                yy=y+h/2+math.sin(i*17)*age*h
                box(c,xx,yy,3+age*10,2,(.55,.94,1),age*.8)
            if kind=='separated':box(c,x,y,w,h,(0,0,0),min(1,t/3.2))
        else:
            picture(c,self.stage,x,y,w,h)
            sprites.draw(c,'reaper-sprites.png',sprites.BOSS[0],600,145,155,180)
        c.restore()
        headings={'story':'OMACONTRA / THE INCIDENT','cellar':'A PRIVATE DEMONSTRATION',
                  'demonstration':'ONE COMMAND','portal':'TRANSFER IN PROGRESS',
                  'separated':'SIGNAL LOST','wake':'01 / THE REAPER','resolve':'YOU CAN FIX ANYTHING'}
        c.select_font_face('monospace',cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_BOLD)
        c.set_source_rgb(*GOLD);c.set_font_size(12);c.move_to(x,110);c.show_text(headings[kind])
        for i,line in enumerate(intro.typed_lines):
            c.set_source_rgb(*CREAM);c.set_font_size(18);c.move_to(x,385+i*33);c.show_text(line)

    def wallpaper_arrival(self,c,intro):
        # Same 1280x720 coordinates, floor and hero scale as the playable fight.
        from omacontra.stages.reaper.battle_art import label
        t=intro.age;f=self.arrival_hero;r=self.arrival_renderer
        f.unlimited_lives=intro.unlimited_lives
        f.x=-45+225*min(1,t/2.1);f.y=f.floor
        f.clock=t;f.run_phase=t*9;f.moving=t<2.1;f.invuln=0
        f.aim_target=None;f.notice_time=0
        c.save();c.scale(W/1280,H/720)
        wallpaper=r.wallpaper or r.stage
        sprites.paint_background(c,wallpaper,0,0,1280,720)
        reveal=max(0,min(1,(t-5.2)/1.5))
        if reveal:
            c.push_group()
            r.background(c,f,'arena')
            for role in ('eye','raven'):r.weak_point(c,f,role)
            r.hud(c,f)
            c.pop_group_to_source();c.paint_with_alpha(reveal)
        r.hero(c,f,None)
        if 2.3<t<6.7:
            phrase=intro.typed_lines[0]
            for dx,dy in ((-1,-1),(1,1),(-1,1),(1,-1)):
                label(c,f.x+35+dx,f.floor-125+dy,phrase,18,'ink')
            label(c,f.x+35,f.floor-125,phrase,18,'cream')
        c.restore()

    def draw(self,c,intro,width,height):
        box(c,0,0,width,height,(0,0,0))
        scale=min(width/W,height/H)
        c.save();c.translate((width-W*scale)/2,(height-H*scale)/2);c.scale(scale,scale)
        c.rectangle(0,0,W,H);c.clip()
        kind,t=intro.beat.kind,intro.age
        if kind=='cover':
            self.title(c,t,intro.start_age)
            if intro.unlimited_lives:self.unlock_banner(c,intro)
        elif intro.journey and kind=='wake':self.wallpaper_arrival(c,intro)
        elif not intro.journey:
            if kind=='cellar':self.wine_cellar(c,t)
            else:self.story_card(c,intro)
        else:self.cinematic_strip(c,intro)
        if kind!='cover' and not (intro.journey and kind=='wake'):
            text(c,'SPACE / NEXT    P / PAUSE    R / REPLAY    ESC / EXIT',H-16,10,GOLD)
            if t<.22:box(c,0,0,W,H,(0,0,0),1-t/.22)
        if kind!='cover' and not intro.journey and intro.unlock_age is not None and intro.unlock_age<3.4:
            self.unlock_banner(c,intro)
        if intro.paused:text(c,'PAUSED',H-34,12,CREAM)
        c.restore()

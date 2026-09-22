"""Cached pixel-art shipping crate and harmless loose game cases."""
from functools import lru_cache
from pathlib import Path
import math
import cairo
from battle_art import line

@lru_cache(maxsize=1)
def crate_stamp():
    # Cache at twice gameplay size: no large sprite resampling during combat.
    source=cairo.ImageSurface.create_from_png(str(Path(__file__).parent/'assets/tide-overstock-cart.png'))
    s=cairo.ImageSurface(cairo.FORMAT_ARGB32,184,128);c=cairo.Context(s)
    c.scale(184/1500,124/800)
    c.set_source_surface(source,-22,-152)
    c.get_source().set_filter(cairo.FILTER_BILINEAR);c.paint()
    return s

def draw(c,f):
    if f.stage and f.wave_reveal<=0:return
    for cargo in f.cargos:
        c.save()
        if f.stage:c.push_group()
        draw_cart(c,f,cargo)
        if f.stage:
            c.pop_group_to_source();c.paint_with_alpha(min(1,f.wave_reveal/2.4))
        c.restore()

def draw_cart(c,f,cargo):
    x=cargo.x;y=f.deck_y(x)
    if f.state=='reveal':
        # The collapse finally bursts the shipping case: still-sealed games
        # scatter into the sea. These pieces never become collision hazards.
        age=f.transition_age
        for i in range(18):
            px=x+(i%7-3)*age*48;py=y-40-(90+i%4*30)*age+190*age*age
            c.save();c.translate(px,py);c.rotate(age*(i%5-2)*3)
            c.set_source_rgba(.13,.25,.34,max(0,1-age/2.5));c.rectangle(-5,-8,10,16);c.fill()
            c.set_source_rgba(.8,.75,.57,max(0,1-age/2.5));c.rectangle(-4,-6,8,5);c.fill();c.restore()
        return
    c.save();c.translate(x,y);c.rotate(math.atan(f.deck_slope))
    c.save();c.scale(42,3);c.set_source_rgba(.02,.04,.05,.28);c.arc(0,0,1,0,math.tau);c.fill();c.restore()
    c.translate(0,-math.sin(cargo.impact*35)*cargo.impact*5)
    # Existing illustrated cases rattle independently of the heavy wooden cart.
    s=crate_stamp();strength=min(1,abs(getattr(cargo,'vx',0))/240)
    for i in range(4):
        c.save();c.rectangle(-46+i*23,-65,23,16);c.clip()
        c.translate(0,math.sin(f.clock*19+i*2)*strength*1.1)
        c.scale(.5,.5);c.set_source_surface(s,-92,-124);c.paint();c.restore()
    c.rectangle(-47,-49,94,53);c.clip()
    c.scale(.5,.5);c.set_source_surface(crate_stamp(),-92,-124)
    c.get_source().set_filter(cairo.FILTER_NEAREST);c.paint();c.restore()
    if not cargo.released:
        for side in (-1,1):
            line(c,[(x+side*35,y-49),(x+side*57,y)],'cream',2,.65)
    elif cargo.age-cargo.released_at<.45:
        age=cargo.age-cargo.released_at
        for side in (-1,1):line(c,[(x+side*(35+age*40),y-40+age*65),(x+side*57,y)],'cream',2,1-age/.45)
    if cargo.hits and cargo.impact>0:
        age=.3-cargo.impact
        for i in range(3):
            c.save();c.translate(x+(i-1)*age*160,y-42-age*(95+i*30));c.rotate(age*(i-1)*8)
            c.set_source_rgb(.16,.27,.36);c.rectangle(-4,-6,8,12);c.fill()
            c.set_source_rgb(.8,.75,.6);c.rectangle(-3,-4,6,5);c.fill();c.restore()

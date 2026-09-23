"""Cached pixel-art shipping crate and harmless loose game cases."""
from omacontra.resources import ASSETS
from functools import lru_cache
import math
import cairo
from omacontra.stages.reaper.battle_art import line

CARTS=('tide-dock-wood.png','tide-dock-steel.png')

@lru_cache(maxsize=2)
def crate_stamp(variant=0):
    # Pre-sized transparent sprites: no large atlas resize in the combat loop.
    return cairo.ImageSurface.create_from_png(str(ASSETS/CARTS[variant]))


def wheel_spray(c,f,cargo,strength):
    if strength<.25:return
    direction=-1 if cargo.vx>0 else 1
    for wheel in (-39,30):
        for i in range(3):
            age=(f.clock*5+i*.31)%1
            px=wheel+direction*(2+age*10*strength)
            py=-math.sin(age*math.pi)*(2+strength*2)
            c.set_source_rgba(.58,.73,.79,(1-age)*strength*.45)
            c.rectangle(round(px),round(py),1.5,1);c.fill()


def draw(c,f):
    if f.stage and f.wave_reveal<=0:return
    for variant,cargo in enumerate(f.cargos):
        c.save()
        if f.stage:c.push_group()
        draw_cart(c,f,cargo,variant)
        if f.stage:
            c.pop_group_to_source();c.paint_with_alpha(min(1,f.wave_reveal/2.4))
        c.restore()

def draw_cart(c,f,cargo,variant=0):
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
    strength=min(1,abs(cargo.vx)/300) if cargo.released else 0.
    # Dense contact shadow and a soft wet reflection keep the wheels on deck.
    c.save();c.scale(44,2.5);c.set_source_rgba(.015,.025,.03,.5)
    c.arc(0,0,1,0,math.tau);c.fill();c.restore()
    wheel_spray(c,f,cargo,strength)
    # Less than a degree of sprung-body lean; collision and movement are unchanged.
    lean=-cargo.vx/350*.012 if cargo.released else 0.
    lean+=math.sin(cargo.impact*28)*cargo.impact*.022
    c.rotate(lean)
    stamp=crate_stamp(variant)
    c.save();c.scale(.25,.25);c.set_source_surface(stamp,-184,-216)
    c.get_source().set_filter(cairo.FILTER_NEAREST);c.paint();c.restore()
    # The cases visible through the broken lid rattle within their small recess.
    if strength:
        c.save();c.rectangle(-33,-46,9,6);c.clip()
        c.translate(0,math.sin(f.clock*19+variant*2)*strength*.3)
        c.scale(.25,.25);c.set_source_surface(stamp,-184,-216)
        c.get_source().set_filter(cairo.FILTER_NEAREST);c.paint();c.restore()
        # Tiny rotating hub highlights; tire silhouettes retain their perspective.
        for wx,wy in ((-39.5,-8),(30,-5.5)) if variant==0 else ((-40,-7.5),(29.5,-6)):
            angle=cargo.x/2.2
            c.set_source_rgba(.7,.75,.7,.65*strength)
            c.rectangle(wx+math.cos(angle)*.8-.5,wy+math.sin(angle)*.8-.5,1,1);c.fill()
    c.restore()
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

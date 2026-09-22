"""Small, bounded finishing effects. Rendering never advances simulation."""
import math


def recovery(c,f,x,y):
    remaining=getattr(f,'invuln',0)
    if not 0<remaining<.65 or f.state!='play':return
    c.save();c.translate(x,y);c.scale(1,.45)
    c.set_source_rgba(.72,.91,.82,.42);c.set_line_width(1.5)
    c.arc(0,0,22,-math.pi/2,-math.pi/2+math.tau*remaining/.65);c.stroke();c.restore()


def impact(c,x,y,age,armored=False):
    if not 0<=age<.12:return
    u=age/.12
    for i in range(5 if armored else 7):
        angle=i*2.399
        radius=3+u*(11 if armored else 19)
        c.set_source_rgba(*((.64,.70,.74) if armored else (1.,.83,.42)),(1-u)*.65)
        c.set_line_width(1 if armored else 1.8)
        c.move_to(x+math.cos(angle)*radius,y+math.sin(angle)*radius)
        c.line_to(x+math.cos(angle)*(radius+4),y+math.sin(angle)*(radius+4));c.stroke()


def masonry(c,f):
    last=max(getattr(f,'sfx_last',{}).get(k,-99) for k in ('sweep','rupture'))
    age=f.clock-last
    if not 0<age<1.15:return
    for i in range(18):
        x=110+i*61+math.sin(i*9)*age*9;y=85+(i%4)*52+age*age*100
        c.set_source_rgba(.46,.43,.37,.32*(1-age/1.15));c.rectangle(x,y,2+i%2,2);c.fill()


def tire_marks(c,f):
    for x,d,born in getattr(f,'tire_marks',()):
        age=f.clock-born
        if age>=.65:continue
        x+=f.distance-d
        c.set_source_rgba(.025,.025,.03,.35*(1-age/.65));c.set_line_width(3)
        for wheel in (-73,88):c.move_to(x+wheel,587);c.line_to(x+wheel+30,587);c.stroke()

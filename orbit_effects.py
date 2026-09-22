"""Phase-one orbital scenery. Deterministic, bounded, and independent of combat."""
import math
from functools import lru_cache
import cairo
import sprites

@lru_cache(maxsize=1)
def cloud_flash():
    s=cairo.ImageSurface(cairo.FORMAT_ARGB32,96,64);c=cairo.Context(s)
    c.scale(1,2/3)
    g=cairo.RadialGradient(48,48,0,48,48,48)
    g.add_color_stop_rgba(0,.75,.86,1,.45)
    g.add_color_stop_rgba(.3,.5,.7,1,.20)
    g.add_color_stop_rgba(1,.35,.6,1,0)
    c.set_source(g);c.paint();return s

@lru_cache(maxsize=1)
def atmosphere():
    source=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720)
    sprites.draw(cairo.Context(source),'finale-earth.png',(0,0,1672,941),-12,-8,1304,736)
    data=source.get_data().cast('B');stride=source.get_stride()
    result=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720)
    pixels=result.get_data().cast('B')
    def blue(x,y):
        i=y*stride+x*4;b,g,r=data[i:i+3]
        return b>135 and g>75 and b>r*1.4
    for x in range(0,1050):
        for y in range(90,610):
            if blue(x,y) and sum(blue(x,y+j) for j in range(1,10))>=8:
                for j in range(10):
                    i=(y+j)*stride+x*4
                    alpha=round(50*(1-j/10))
                    pixels[i:i+4]=bytes((alpha,round(alpha*.8),round(alpha*.25),alpha))
                break
    result.mark_dirty();return result

def draw(c,t,drift=0):
    c.save()
    # Stars stay in the dark sky, above/right of the Earth. Slow shimmer,
    # deliberately much smaller and dimmer than any enemy projectile.
    for i in range(30):
        x=(i*173.71+41)%1240+20;y=65+(i*23.71)%55
        if i%3==0:x=1060+(i*39.7)%200;y=150+(i*51.1)%380
        a=.15+.48*(.5+.5*math.sin(t*.8+i*2.1))**4
        c.set_source_rgba(.65,.81,1,a);c.rectangle(round(x),round(y),2,2);c.fill()
        if i%7==0:
            c.set_source_rgba(.7,.84,1,a*.4)
            c.rectangle(round(x)-2,round(y),6,1);c.rectangle(round(x),round(y)-2,1,6);c.fill()
    # Reuse the actual blue edge pixels: no guessed arc floating above Earth.
    c.save();c.translate(drift,0)
    c.set_source_surface(atmosphere())
    c.paint_with_alpha(.4+.25*math.sin(t*.7))
    c.restore()
    # Muted lightning within the clouds, never a full-screen flash.
    for i,(x,y) in enumerate(((305,295),(572,373),(170,490))):
        age=(t+i*4.3)%14
        if age<.55:
            alpha=math.sin(age/.55*math.pi)**2*(.7 if age<.25 else .35)
            c.set_source_surface(cloud_flash(),x+drift-48,y-32);c.paint_with_alpha(alpha)
    # One distant satellite, slow enough to read as orbital scenery.
    x=(t*7+180)%1500-110;y=90+math.sin(t*.06)*12
    c.save();c.translate(x,y);c.rotate(-.2+math.sin(t*.13)*.22)
    c.set_source_rgba(.27,.40,.51,.65)
    for side in (-1,1):
        c.rectangle(side*6-4,-3,8,6);c.fill()
        c.set_source_rgba(.40,.56,.67,.5)
        c.rectangle(side*6-3,-2,6,1);c.fill()
    c.set_source_rgba(.78,.8,.74,.7);c.rectangle(-2,-2,4,4);c.fill()
    # A brief reflection travels over the solar panels as attitude changes.
    # Only the phase-one sky calls this renderer.
    glint=max(0,math.sin(t*.31))**18
    for side in (-1,1):
        c.set_source_rgba(.82,.90,1,glint*.6)
        c.rectangle(side*6-3,-2,6,1);c.fill()
    c.restore();c.restore()

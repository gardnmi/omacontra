"""Painted energy membrane, progressively fractured by containment damage."""
import math
import cairo
from omacontra.rendering import sprites

ATLAS='finale-shield-membrane.png'
CELL=627

def integrity(f):
    return max(0.,min(1.,sum(f.nodes)/(len(f.nodes)*f.node_max)))

def damage_layers(health):
    """Blend authored damage stages without random holes or wireframe geometry."""
    health=max(0.,min(1.,health))
    if health>=.55:
        worn=(1-health)/.45
        return ((0,1-worn),(1,worn))
    if health>=.15:
        broken=(.55-health)/.40
        return ((1,1-broken),(2,broken))
    return ((2,health/.15),)

def stamp(c,index,x,y,w,h,alpha):
    if alpha<=0:return
    sprites.draw(c,ATLAS,((index%2)*CELL,(index//2)*CELL,CELL,CELL),x-w/2,y-h/2,w,h,alpha=alpha)

def draw(c,f):
    if f.phase!=1:return
    x,y=f.boss;health=integrity(f);t=f.clock
    c.save();c.set_operator(cairo.OPERATOR_ADD)
    # Black in the atlas contributes no light. Fine painted edge refractions
    # replace the old geometric outline; the dark interior stays see-through.
    for index,alpha in damage_layers(health):
        stamp(c,index,x,y+40,472,468,alpha*.64)
    if f.beam_hit and f.laser_contact=='shield' and f.beam:
        hx,hy=f.beam[-1]
        size=118+3*math.sin(t*13)
        stamp(c,3,hx,hy,size,size,.78+.07*math.sin(t*19))
    c.restore()

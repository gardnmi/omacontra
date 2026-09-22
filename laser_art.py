"""Shared electrical strands for the stolen Foundry weapon."""
import math
from battle_art import line,glow

def draw_arc_beam(c,points,t,hit=False):
    if not points:return
    for width,alpha in ((26,.06),(17,.14),(10,.7)):
        line(c,points,'gold',width,alpha)
    line(c,points,'cream',4,1)
    for strand in range(3):
        arc=[]
        for i,(x,y) in enumerate(points):
            prev=points[max(0,i-1)];nxt=points[min(len(points)-1,i+1)]
            dx=nxt[0]-prev[0];dy=nxt[1]-prev[1];mag=max(1,math.hypot(dx,dy))
            offset=math.sin(i*.8-t*19+strand*2.1)*(8+strand*5)*math.sin(i/max(1,len(points)-1)*math.pi)
            arc.append((x-dy/mag*offset,y+dx/mag*offset))
        c.set_source_rgba(.36,.42,1,.28);c.set_line_width(7)
        c.move_to(*arc[0])
        for point in arc[1:]:c.line_to(*point)
        c.stroke()
        c.set_source_rgba(.72,.82,1,.95);c.set_line_width(1.8)
        c.move_to(*arc[0])
        for point in arc[1:]:c.line_to(*point)
        c.stroke()
    sx,sy=points[0];ex,ey=points[-1]
    glow(c,sx,sy,22,'cream',.75)
    if hit:
        glow(c,ex,ey,47,'gold',.8);glow(c,ex,ey,17,'cream',1)

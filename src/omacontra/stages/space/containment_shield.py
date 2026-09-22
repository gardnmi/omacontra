"""Lightweight containment shell: persistent damage gaps and local laser ripples."""
import math

def integrity(f):
    return max(0.,min(1.,sum(f.nodes)/(len(f.nodes)*f.node_max)))

def panel_survives(index,health):
    # Fixed damage ordering: missing panels never randomly reappear each frame.
    return ((index*37+13)%101)/101 < health

def draw(c,f):
    if f.phase!=1:return
    x,y=f.boss;cy=y+40;health=integrity(f);t=f.clock
    c.save()
    # The enclosing silhouette stays faint enough to read incoming projectiles.
    for i in range(64):
        if not panel_survives(i,health):continue
        a=i*math.tau/64;b=a+math.tau/64*.91
        points=[(x+222*math.cos(a+(b-a)*j/4),cy+218*math.sin(a+(b-a)*j/4)) for j in range(5)]
        for width,alpha in ((7,.045),(2,.35)):
            c.set_source_rgba(.24,.78,1,alpha);c.set_line_width(width)
            c.move_to(*points[0])
            for p in points[1:]:c.line_to(*p)
            c.stroke()
    index=0
    for row in range(-5,6):
        for col in range(-5,6):
            px=col*37+(row%2)*18.5;py=row*32
            if (px/198)**2+(py/193)**2>1:continue
            index+=1
            if not panel_survives(index+71,health):continue
            pts=[(x+px+21*math.cos(i*math.pi/3),cy+py+21*math.sin(i*math.pi/3)) for i in range(6)]
            c.move_to(*pts[0])
            for p in pts[1:]:c.line_to(*p)
            c.close_path();c.set_source_rgba(.15,.65,1,.025);c.fill_preserve()
            c.set_source_rgba(.3,.8,1,.11);c.set_line_width(.8);c.stroke()
            # Stable broken seams spread across surviving panels as health falls.
            if health<.8 and panel_survives(index+19,1-health):
                c.move_to(x+px-14,cy+py-11);c.line_to(x+px-3,cy+py-3)
                c.line_to(x+px-7,cy+py+4);c.line_to(x+px+13,cy+py+12)
                c.set_source_rgba(.6,.91,1,.48);c.set_line_width(1.3);c.stroke()
    if f.beam_hit and f.laser_contact=='shield' and f.beam:
        hx,hy=f.beam[-1]
        for i in range(3):
            u=(t*2.2+i/3)%1;r=9+u*48
            c.set_source_rgba(.45,.88,1,(1-u)*.65);c.set_line_width(2.5*(1-u)+.5)
            c.save();c.translate(hx,hy);c.scale(1,.65);c.arc(0,0,r,0,math.tau);c.stroke();c.restore()
        for i in range(6):
            a=i*math.tau/6+t*1.8;length=20+8*math.sin(t*31+i*7)
            c.move_to(hx,hy);c.line_to(hx+math.cos(a+.18)*length*.55,hy+math.sin(a+.18)*length*.55)
            c.line_to(hx+math.cos(a)*length,hy+math.sin(a)*length)
            c.set_source_rgba(.75,.96,1,.8);c.set_line_width(1.4);c.stroke()
    c.restore()

"""Ten-second arcade continue decision and portrait comeback animation."""
import math
import cairo
import sprites


class ContinueScreen:
    sound_bank='continue'
    def __init__(self,hardcore=False):
        self.hardcore=hardcore
        self.clock=0.;self.age=0.;self.state='expired' if hardcore else 'countdown'
        self.sfx_events=['death_blow' if hardcore else 'tick']

    @property
    def remaining(self):return max(0,math.ceil(10-self.age))

    @property
    def finished(self):return self.state=='accepted' and self.age>=1.35

    def accept(self):
        if self.state!='countdown':return False
        self.state='accepted';self.age=0.;self.sfx_events.append('accept');return True

    def step(self,dt):
        dt=max(0,dt);self.clock+=dt;previous=self.remaining;self.age+=dt
        if self.state=='countdown':
            if self.age>=10:
                self.state='expired';self.age=0.;self.sfx_events.append('death_blow')
            elif self.remaining!=previous:self.sfx_events.append('tick')
        self.sfx_events=self.sfx_events[-8:]


def centered(c,text,y,size,rgb):
    c.select_font_face('monospace',cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(size);ext=c.text_extents(text)
    c.set_source_rgb(*rgb);c.move_to(640-ext.width/2-ext.x_bearing,y);c.show_text(text)


class ContinueRenderer:
    def __init__(self):
        # Cache each complete row at its final size, never resample the atlas
        # during the countdown or comeback animation.
        source=cairo.ImageSurface.create_from_png(str(sprites.ASSETS/'continue-portraits.png'))
        self.rows=[]
        for row in range(2):
            s=cairo.ImageSurface(cairo.FORMAT_ARGB32,1120,374);c=cairo.Context(s)
            c.scale(1120/1536,374/512);c.set_source_surface(source,0,-row*512)
            c.get_source().set_filter(cairo.FILTER_NEAREST);c.paint();self.rows.append(s)

    def draw(self,c,screen):
        c.set_source_rgb(.018,.014,.028);c.paint()
        g=cairo.LinearGradient(0,130,0,550)
        g.add_color_stop_rgb(0,.025,.018,.05);g.add_color_stop_rgb(1,.13,.026,.035)
        c.set_source(g);c.rectangle(50,155,1180,390);c.fill()
        accepting=screen.state=='accepted';expired=screen.state=='expired'
        rise=min(1,screen.age/.55) if accepting else 0
        rise=rise*rise*(3-2*rise)
        for row,alpha in ((0,1-rise),(1,rise)):
            if alpha<=0:continue
            c.set_source_surface(self.rows[row],80,175-8*rise);c.paint_with_alpha(alpha)
        if expired:
            c.set_source_rgba(.025,.015,.03,.62);c.rectangle(50,155,1180,390);c.fill()
            flash=max(0,1-screen.age/.16)
            c.set_source_rgba(.85,.09,.04,flash*.3);c.paint()
        c.set_source_rgb(.68,.65,.46);c.set_line_width(2)
        c.move_to(60,155);c.line_to(1220,155);c.move_to(60,549);c.line_to(1220,549);c.stroke()
        centered(c,'BACK IN THE FIGHT' if accepting else 'GAME OVER' if expired else 'CONTINUE?',112,54,(.92,.9,.72))
        for text,x in (('DHH',330),('TOBI',900)):
            c.set_font_size(23);c.set_source_rgb(.68,.85,.59);c.move_to(x,580);c.show_text(text)
        if accepting:
            # Authored lifted-eye locations in the bottom portrait row.
            gleam=max(0,1-abs(screen.age-.65)/.25)
            for x,y in ((344,316),(408,315),(832,337),(883,321)):
                y+=7-8*rise
                g=cairo.RadialGradient(x,y,0,x,y,14)
                g.add_color_stop_rgba(0,.8,.95,1,gleam*.8)
                g.add_color_stop_rgba(1,.4,.7,1,0)
                c.set_source(g);c.arc(x,y,14,0,math.tau);c.fill()
                c.set_source_rgba(.85,.98,1,gleam);c.set_line_width(2)
                c.move_to(x-25*gleam,y);c.line_to(x+25*gleam,y)
                c.move_to(x,y-10*gleam);c.line_to(x,y+10*gleam);c.stroke()
            centered(c,'LET’S GO.',660,28,(.68,.9,.56))
        elif expired:
            if screen.hardcore:centered(c,'HARDCORE RUN ENDED / NO CONTINUES',616,22,(.95,.53,.35))
            centered(c,'ENTER / TITLE SCREEN     ESC / MENU',662,20,(.76,.75,.65))
        else:
            centered(c,str(screen.remaining),660,74,(1,.64,.22))
            centered(c,'ENTER / SPACE / R  —  CONTINUE',704,17,(.76,.75,.65))

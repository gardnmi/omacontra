"""Seekable gallery using the game's actual cinematic renderers, without combat."""
import math
from finale import ENDING_DURATION,DEPARTURE_DURATION,ENCOUNTER_DURATION

SCENES = {
    'orbit-enrage': ('Dead Orbit / enrage', 2.8),
    'coat-enrage': ('Black Coat / enrage', 2.8),
    'opening': ('Original opening', 28.2),
    'portal-story': ('Wine rack / separation', 25.8),
    'quattro-intro': ('Quattro / reunion', 11.8),
    'quattro-transform': ('Quattro / trailer transformation', 3.4),
    'quattro-outro': ('Quattro / victory jump', 8.),
    'harbor': ('Harbor / split up', 26.),
    'tide-outro': ('Tidebreaker / aftermath', 9.),
    'foundry-intro': ('Foundry / arrival', 9.8),
    'foundry-disarm': ('Foundry / shoulder weapon falls', 1.35),
    'foundry-rescue': ('Foundry / Tobi rescue', 13.5),
    'departure': ('Black Moon / departure', DEPARTURE_DURATION),
    'encounter': ('Black Moon / last dive', ENCOUNTER_DURATION),
    'ending': ('Finale / portal, fall and catch', ENDING_DURATION),
}

class Review:
    def __init__(self, name='ending'):
        self.select(name)

    def select(self, name):
        self.name=name;self.title,self.duration=SCENES[name]
        self.time=0.;self.playing=True;self.speed=1.
        self.scene=None;self.f=None
        if name in ('opening','portal-story'):
            from story import Intro
            from art import Renderer
            self.scene=Intro(journey=name=='portal-story');self.renderer=Renderer()
            self.duration=sum(b.duration for b in self.scene.beats if math.isfinite(b.duration))+(5 if name=='opening' else 0)
        elif name in ('orbit-enrage','coat-enrage'):
            from tidebreaker import Tidebreaker
            from tide_art import TideRenderer
            self.f=Tidebreaker();self.f.advance_guardian();self.renderer=TideRenderer()
            for a in self.f.guardians:
                a.enraged=a.kind==(2 if name=='orbit-enrage' else 1)
                if not a.enraged:a.hp=0;a.death_age=3
        elif name.startswith('quattro'):
            from chase import Chase
            from chase_art import ChaseRenderer
            from chase_cinema import ChaseCinema
            self.f=Chase();self.renderer=ChaseRenderer()
            if name=='quattro-transform':self.f.detach_trailer()
            else:self.scene=ChaseCinema('outro' if name.endswith('outro') else 'intro')
        elif name in ('harbor','tide-outro'):
            from tidebreaker import Tidebreaker
            from tide_art import TideRenderer
            from journey_cinema import JourneyCinema,INTRO_DURATION
            self.f=Tidebreaker();self.renderer=TideRenderer()
            self.scene=JourneyCinema('intro' if name=='harbor' else 'outro')
            if name=='harbor':self.duration=INTRO_DURATION
        elif name.startswith('foundry'):
            from foundry import Foundry
            from foundry_art import FoundryRenderer,FoundryIntro
            self.f=Foundry();self.renderer=FoundryRenderer()
            if name.endswith('intro'):self.scene=FoundryIntro()
            elif name=='foundry-disarm':self.f.begin_disarm()
            else:
                self.f.state='rescue';self.f.rescue_start_x=315.;self.f.boss_hp=0;self.f.mount_hp=0;self.f.lava_age=7.;self.f.rescue_start_y=435.
        else:
            from finale import Finale
            from finale_art import FinaleRenderer
            self.f=Finale();self.renderer=FinaleRenderer();self.f.state=name
            if name=='ending':
                self.f.nodes=[0,0];self.f.boss_hp=0;self.f.death_origin=(640,175)
        self.seek(0)

    def seek(self, t):
        self.time=max(0.,min(self.duration,t))
        if self.name in ('opening','portal-story'):
            self.scene.reset();self.scene.step(self.time)
        elif self.scene:self.scene.age=self.time
        if self.f:
            self.f.clock=0. if self.scene else self.time
            if self.name in ('orbit-enrage','coat-enrage'):
                for a in self.f.guardians:
                    if a.enraged:a.rage_age=min(2.799,self.time)
            if self.name=='quattro-transform':
                from chase_robot import smooth
                self.f.transform_age=self.time;self.f.trailer_age=self.time
                self.f.trailer_x=self.f.trailer_origin+95*smooth(self.time/.85)
                self.f.distance=self.time*700
            if self.name in ('departure','encounter','ending'):self.f.age=self.time
            if self.name=='foundry-disarm':self.f.disarm_age=self.time
            if self.name=='foundry-rescue':self.f.rescue_age=self.time

    def step(self,dt):
        if self.playing:
            self.seek(self.time+max(0,dt)*self.speed)
            if self.time>=self.duration:self.playing=False

    def draw(self,c):
        if self.name in ('opening','portal-story'):self.renderer.draw(c,self.scene,1280,720)
        elif self.scene:self.scene.draw(c,self.renderer,self.f)
        else:self.renderer.draw(c,self.f)


def launch(name='ending',at=0):
    import time
    import gi
    gi.require_version('Gtk','3.0');gi.require_version('Gdk','3.0')
    from gi.repository import Gtk,Gdk,GLib
    review=Review(name);review.seek(at)
    window=Gtk.Window(title='OMACONTRA / Cutscene review')
    window.set_default_size(1100,720)
    box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6);window.add(box)
    area=Gtk.DrawingArea();area.set_hexpand(True);area.set_vexpand(True)
    box.pack_start(area,True,True,0)
    controls=Gtk.Box(spacing=8);box.pack_start(controls,False,False,6)
    menu=Gtk.ComboBoxText()
    for key,(title,_) in SCENES.items():menu.append(key,title)
    menu.set_active_id(name);controls.pack_start(menu,False,False,4)
    play=Gtk.Button(label='Pause');controls.pack_start(play,False,False,0)
    restart=Gtk.Button(label='Replay');controls.pack_start(restart,False,False,0)
    speed=Gtk.ComboBoxText()
    for value in (.25,.5,1.,2.):speed.append(str(value),f'{value:g}x')
    speed.set_active_id('1.0');controls.pack_start(speed,False,False,0)
    stamp=Gtk.Label();controls.pack_start(stamp,False,False,0)
    slider=Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL,0,review.duration,1/60)
    slider.set_draw_value(False);box.pack_start(slider,False,False,4)
    hint=Gtk.Label(label='Space: pause/play   ← →: seek 1s   Shift + ← →: one frame   R: replay   Esc: close')
    box.pack_start(hint,False,False,4)
    updating=False
    def refresh():
        nonlocal updating
        updating=True;slider.set_value(review.time);updating=False
        stamp.set_text(f'{review.time:05.2f} / {review.duration:.2f}s')
        play.set_label('Pause' if review.playing else 'Play');area.queue_draw()
    def toggle(*_):
        if review.time>=review.duration:review.seek(0)
        review.playing=not review.playing;refresh()
    def replay(*_):review.seek(0);review.playing=True;refresh()
    def select(widget):
        nonlocal updating
        review.select(widget.get_active_id());review.speed=float(speed.get_active_id())
        updating=True;slider.set_range(0,review.duration);updating=False;refresh()
    def scrub(widget):
        if not updating:review.playing=False;review.seek(widget.get_value());refresh()
    def draw(widget,c):
        w=widget.get_allocated_width();h=widget.get_allocated_height()
        c.set_source_rgb(0,0,0);c.paint();scale=min(w/1280,h/720)
        if scale<=0:return
        c.save();c.translate((w-1280*scale)/2,(h-720*scale)/2);c.scale(scale,scale)
        review.draw(c);c.restore()
    def key(_,event):
        name=Gdk.keyval_name(event.keyval).lower()
        if name=='escape':window.destroy()
        elif name=='space':toggle()
        elif name=='r':replay()
        elif name in ('left','right'):
            delta=1/60 if event.state&Gdk.ModifierType.SHIFT_MASK else 1.
            review.playing=False;review.seek(review.time+delta*(1 if name=='right' else -1));refresh()
        else:return False
        return True
    last=time.monotonic()
    def tick():
        nonlocal last
        now=time.monotonic();review.step(min(.1,now-last));last=now;refresh();return True
    area.connect('draw',draw);play.connect('clicked',toggle);restart.connect('clicked',replay)
    menu.connect('changed',select);slider.connect('value-changed',scrub)
    speed.connect('changed',lambda widget:setattr(review,'speed',float(widget.get_active_id())))
    window.connect('key-press-event',key)
    source=GLib.timeout_add(16,tick)
    def close(*_):GLib.source_remove(source);Gtk.main_quit()
    window.connect('destroy',close);window.show_all();refresh();Gtk.main()

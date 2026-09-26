"""Shared controller actions. Hardware readers supply standard Xbox button names."""
import math

BUTTONS = ('a','b','x','y','lb','rb','lt','rt','view','menu','ls','rs','up','down','left','right')
KEY_CODES = {name: -1000-i for i,name in enumerate(BUTTONS)}

class Controller:
    def __init__(self, app):
        self.app=app
        self.held={}
        self.raw=set()
        self.blocked=set()
        self.axes=(0.,0.,0.,0.)
        self.connected=False
        self.repeat={}
        self.clock=0.
        self.aim=None
        self.direction=None

    def context(self):
        a=self.app
        if a.frontend.page:return ('menu',a.frontend.page)
        if a.intro:return ('story', 'intro')
        if getattr(a,'continue_screen',None):return ('story','continue')
        if any(getattr(a,n,None) for n in ('chase_cinema','journey_cinema','foundry_intro')):return ('story','cinema')
        if a.f.state not in ('play','finisher'):return ('story',a.f.state)
        return ('play',a.level)

    def release(self,button):
        key=self.held.pop(button,None)
        if key is not None:self.app.input_release(KEY_CODES[button],key)
        self.repeat.pop(button,None)

    def suspend(self):
        self.blocked.update(self.raw)
        for b in list(self.held):self.release(b)
        self.aim=None
        self.direction=None

    def sample(self, sample):
        a=self.app
        connected=bool(sample and sample.get('connected'))
        if not connected:
            was=self.connected
            self.suspend();self.raw.clear();self.blocked.clear();self.axes=(0.,)*4
            self.connected=False
            if was and getattr(a,'input_device','keyboard')=='controller' and a.visible and not a.frontend.page:
                a.frontend.open()
            return
        self.connected=True
        axes=sample.get('axes',())
        self.axes=tuple(max(-1.,min(1.,float(v))) if isinstance(v,(int,float)) and math.isfinite(v) else 0. for v in list(axes[:4])+[0.]*(4-len(axes[:4])))
        raw={b for b in sample.get('buttons',()) if b in BUTTONS}
        dz=max(.05,min(.4,a.frontend.profile.settings.get('deadzone',20)/100))
        x,y=self.axes[:2]
        for b,on in (('left',x < -dz),('right',x > dz),('up',y < -dz),('down',y > dz)):
            if on:raw.add(b)
        self.blocked.intersection_update(raw)
        for b in list(self.held):
            if b not in raw:self.release(b)
        fresh=raw-self.raw
        self.raw=raw
        if not a.visible:
            self.suspend();return
        if fresh or math.hypot(*self.axes[2:])>dz:
            a.input_device='controller'
        context=self.context()
        # Keep each physical button's original binding until released. A held
        # menu-confirm must never become a jump after the menu closes.
        for b in BUTTONS:
            if b not in fresh or b in self.blocked:continue
            mode=context[0]
            key={'a':'space','b':'Shift_L','x':'j','y':'e','lb':'Shift_L','rt':'j','menu':'Escape','view':'Escape',
                 'up':'Up','down':'Down','left':'Left','right':'Right'}.get(b)
            if mode=='menu':key={'a':'Return','b':'Escape','menu':'Escape','view':'Escape','up':'Up','down':'Down','left':'Left','right':'Right'}.get(b)
            elif mode=='story' and b=='a':key='Return'
            if key:
                self.held[b]=key
                self.app.input_press(KEY_CODES[b],key)
                self.repeat[b]=self.clock+.4
                if self.context()!=context:
                    self.suspend();break

    def tick(self,dt):
        self.clock+=dt
        a=self.app
        if not a.visible:return
        if self.context()[0]=='menu':
            for b in ('up','down','left','right'):
                if b in self.held and self.clock>=self.repeat.get(b,float('inf')):
                    a.frontend.key(self.held[b].lower());self.repeat[b]=self.clock+.13
        self.aim=None
        self.direction=None
        if getattr(a,'input_device','keyboard')!='controller' or self.context()[0]!='play':return
        x,y=self.axes[2:];length=math.hypot(x,y)
        dz=max(.05,min(.4,a.frontend.profile.settings.get('deadzone',20)/100))
        if length<=dz and a.keys & {'j','z'}:
            # Contra-style movement-stick firing, with independent right-stick
            # aim taking priority. Use the same dead-zoned directions as movement.
            directions=self.raw-self.blocked
            x=int('right' in directions)-int('left' in directions)
            y=int('down' in directions)-int('up' in directions)
            length=math.hypot(x,y)
        if length>dz:
            self.direction=(x/length,y/length)
            px,py=(a.f.x,a.f.y) if a.level==5 else a.f.player_center
            self.aim=(px+320*x/length,py+320*y/length)

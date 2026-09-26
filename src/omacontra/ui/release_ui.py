"""Player-facing menus, persisted preferences, campaign records and rewards."""
import json
import os
from pathlib import Path
import math
import time
import cairo
from omacontra.rendering.health_medals import medal
from omacontra.audio.weapon_audio import SFX_BOOST
from omacontra.audio.jukebox import Jukebox

NAMES=('THE REAPER','QUATTRO RUN','TIDEBREAKER','THE MIST GATE','BLACK MOON')
DEFAULTS={'music':100,'effects':100,'deadzone':20}

def setting_limits(name):return (5,40) if name=='deadzone' else (0,150)

class Profile:
    def __init__(self,path=None):
        self.path=Path(path) if path else Path(os.environ.get('XDG_CONFIG_HOME',Path.home()/'.config'))/'omacontra/profile.json'
        self.settings=dict(DEFAULTS);self.best={};self.error=''
        try:
            data=json.loads(self.path.read_text())
            if not isinstance(data,dict):return
            settings=data.get('settings')
            if not isinstance(settings,dict):settings={}
            for k in DEFAULTS:
                v=settings.get(k,DEFAULTS[k])
                if isinstance(v,(int,float)) and math.isfinite(v):self.settings[k]=max(setting_limits(k)[0],min(setting_limits(k)[1],int(v)))
            best=data.get('best',{})
            if isinstance(best,dict):self.best={k:v for k,v in best.items() if isinstance(v,(int,float)) and math.isfinite(v) and v>0}
        except (OSError,ValueError,TypeError):pass
    def save(self):
        try:
            self.path.parent.mkdir(parents=True,exist_ok=True)
            tmp=self.path.with_suffix('.tmp');tmp.write_text(json.dumps({'settings':self.settings,'best':self.best},indent=2));tmp.replace(self.path)
            self.error=''
        except OSError:self.error='Could not save preferences on this device.'

class RunRecord:
    def __init__(self,start=1,practice=False,hardcore=False):
        self.hardcore=hardcore
        self.start=start;self.practice=practice;self.elapsed=0.;self.losses=0;self.continues=0;self.restarts=0
        self.hits={};self.cleared=set();self.unlimited=False
    def observe(self,level,dt,hits,losses,active,unlimited):
        if active:self.elapsed+=dt
        # Unlimited lives preserve HP, but accepted damage still counts as a loss.
        self.losses+=max(0,hits if unlimited else losses)
        self.hits[level]=self.hits.get(level,0)+max(0,hits)
        self.unlimited|=unlimited
    @property
    def category(self):
        return 'practice' if self.practice or self.start!=1 or len(self.cleared)!=5 else 'unlimited' if self.unlimited else 'hardcore' if self.hardcore else 'arcade'
    @property
    def clean(self):return sum(not self.hits.get(n,0) for n in self.cleared)

def label(c,x,y,text,size=22,color=(.86,.84,.68)):
    c.set_source_rgb(*color);c.select_font_face('monospace',cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_BOLD);c.set_font_size(size);c.move_to(x,y);c.show_text(str(text))

def time_text(seconds):
    return f'{int(seconds)//60:02d}:{int(seconds)%60:02d}.{int(seconds*10)%10}'

class Frontend:
    def __init__(self,app,profile=None):
        self.app=app;self.profile=profile or Profile();self.page=None;self.selection=0;self.parent='pause';self.pending=None
        self.record=RunRecord(app.level,getattr(app,'guardian_practice',False));self.award=None;self.award_age=0.;self.result_saved=False
        self.jukebox=Jukebox()
        self.credits_page=0;self.apply_audio()
        self.opened_at=time.monotonic();self.last_menu_sound=0.;self.menu_positions={}
        self.blocked=set();self.finish_age=99.;self.last_state=app.f.state
    def apply_audio(self):
        s=self.profile.settings
        for music in (self.app.music,self.app.game_music):music.set_volume(85*s['music']/100)
        self.app.unlock_sound.set_volume(85*SFX_BOOST*s['effects']/100)
        self.app.weapon_audio.set_volumes(s['effects']/100)
    def cue(self,name):
        now=time.monotonic()
        if name in ('move','adjust') and now-self.last_menu_sound<.045:return
        self.last_menu_sound=now
        self.app.weapon_audio.menu_effects.trigger(name)

    def open(self,page='pause'):
        if getattr(self.app,'controller',None):self.app.controller.suspend()
        previous=self.page
        if previous=='music' and page!='music':self.jukebox.stop()
        if previous:self.menu_positions[previous]=self.selection
        self.page=page;self.selection=0 if page=='confirm' else self.menu_positions.get(page,0)
        self.selection=min(self.selection,len(self.rows())-1)
        self.opened_at=time.monotonic();self.app.paused=True
        if self.app.intro:self.app.intro.paused=True
        self.app.keyboard.clear();self.app.shooting=False;self.app.slide_requested=False
        self.app.weapon_audio.silence()
        if page=='results' and previous is None:self.cue('complete')
        elif previous is None:self.cue('open')
    def resume(self):
        if getattr(self.app,'controller',None):self.app.controller.suspend()
        self.jukebox.stop()
        self.blocked=set(self.app.keys)
        self.page=None;self.app.paused=False
        if self.app.intro:self.app.intro.paused=False
        self.app.keyboard.clear();self.app.shooting=False;self.app.slide_requested=False
    def new_run(self,level=1,practice=False,hardcore=False):
        from omacontra.audio.intro_music import shuffled_tracks
        self.app.run_playlist=shuffled_tracks();self.app.game_music.stop()
        self.record=RunRecord(level,practice,hardcore);self.result_saved=False;self.award=None
    def rows(self):
        if self.page=='mode':return ['Standard','Hardcore','Music player','Back']
        if self.page=='music':return [t['title'] for t in self.jukebox.tracks]+['Stop','Back']
        if self.page=='pause':return ['Resume','Controls','Options']+([] if self.record.hardcore else ['Restart encounter'])+['Return to title','Music player','Credits','Quit']
        if self.page=='options':return [f'{k.upper():8}  {v:3}%' for k,v in self.profile.settings.items()]+['Back']
        if self.page=='results':return ['Play again','Boss select','Return to title','Music player','Credits','Quit']
        if self.page=='bosses':return list(NAMES)+['Back']
        if self.page=='confirm':return ['Cancel','Confirm']
        return ['Back']
    def request(self,action):
        if action=='restart' and self.record.hardcore:return
        self.pending=action;self.parent=self.page or 'pause';self.open('confirm')
    def activate(self,action):
        a=self.app
        if action=='restart':
            if self.record.hardcore:return
            self.record.restarts+=1;self.resume();self.award=None
            if a.intro:
                a.intro.reset()
                if not a.intro.journey:a.music.restart()
            else:
                if a.f.state=='won':self.record.practice=True
                guardians=a.level==3 and bool(getattr(a.f,'stage',0))
                a.reset_encounter()
                if guardians and not a.f.stage:
                    a.f.advance_guardian();a.journey_cinema=None
        elif action=='title':
            self.resume();a.return_to_title()
        elif action=='quit':a.close()
        elif action=='again':
            self.resume();self.new_run(hardcore=self.record.hardcore);a.guardian_practice=False;a.level=1;a.intro=None;a.reset_encounter()
    def pointer(self,x,y,click=False):
        if not self.page:return
        from omacontra.ui.menu_art import row_boxes
        for i,(rx,ry,w,h) in enumerate(row_boxes(self)):
            if not (rx<=x<=rx+w and ry<=y<=ry+h):continue
            if self.selection!=i:self.selection=i;self.cue('move')
            if click:
                if self.page=='options' and i<len(DEFAULTS):
                    if y<ry+35 or x<rx+38 or x>rx+428:return
                    name=tuple(DEFAULTS)[i]
                    lo,hi=setting_limits(name)
                    value=max(lo,min(hi,round((lo+(x-rx-38)/390*(hi-lo))/5)*5))
                    if value!=self.profile.settings[name]:
                        self.profile.settings[name]=value;self.apply_audio();self.profile.save();self.cue('adjust')
                else:self.key('return')
            break

    def key(self,key):
        if not self.page:return False
        old_page=self.page;old_selection=self.selection;old_credits=self.credits_page
        before=dict(self.profile.settings);choice=self.rows()[self.selection]
        handled=self._key(key)
        if before!=self.profile.settings:self.cue('adjust')
        elif self.page!=old_page or key in ('return','space'):
            if key in ('escape','p') or choice in ('Back','Cancel','Resume'):self.cue('back')
            elif key in ('return','space'):self.cue('move' if old_page=='credits' and key=='space' else 'confirm')
        elif self.selection!=old_selection or self.credits_page!=old_credits:self.cue('move')
        return handled

    def _key(self,key):
        if not self.page:return False
        rows=self.rows()
        if key in ('up','w'):self.selection=(self.selection-1)%len(rows)
        elif key in ('down','s'):self.selection=(self.selection+1)%len(rows)
        elif key in ('left','right') and self.page=='music':
            self.jukebox.skip(1 if key=='right' else -1);self.selection=self.jukebox.index
        elif key in ('left','right','a','d') and self.page=='options' and self.selection<len(DEFAULTS):
            name=tuple(DEFAULTS)[self.selection];v=self.profile.settings[name]
            lo,hi=setting_limits(name)
            self.profile.settings[name]=max(lo,min(hi,v+(5 if key in ('right','d') else -5)))
            self.apply_audio();self.profile.save()
        elif key in ('escape','p'):
            if self.page in ('pause','mode'):self.resume()
            elif self.page=='results':pass
            elif self.page=='confirm':self.open(self.parent)
            else:self.open(self.parent)
        elif key in ('return','space'):
            choice=rows[self.selection]
            if choice=='Music player' and self.page in ('mode','pause','results'):
                self.parent=self.page;self.open('music')
            elif self.page=='music':
                if self.selection<len(self.jukebox.tracks):self.jukebox.play(self.selection)
                elif choice=='Stop':self.jukebox.stop()
                else:self.open(self.parent)
            elif self.page=='mode':
                if choice=='Back':self.resume()
                else:
                    a=self.app;hardcore=choice=='Hardcore'
                    self.new_run(hardcore=hardcore)
                    if hardcore:
                        a.unlimited_lives=False;a.f.unlimited_lives=False
                        a.intro.unlimited_lives=False;a.intro.unlock_age=None
                    self.resume()
                    if a.intro.request_start():a.music.play_start()
            elif self.page=='confirm':
                if self.selection:self.activate(self.pending)
                else:self.open(self.parent)
            elif self.page=='pause':
                if choice=='Resume':self.resume()
                elif choice=='Restart encounter':self.request('restart')
                elif choice=='Return to title':self.request('title')
                elif choice=='Quit':self.request('quit')
                else:self.parent='pause';self.open(choice.lower())
            elif self.page=='results':
                if choice=='Play again':self.activate('again')
                elif choice=='Boss select':self.parent='results';self.open('bosses')
                elif choice=='Return to title':self.activate('title')
                elif choice=='Quit':self.request('quit')
                else:self.parent='results';self.open('credits')
            elif self.page=='bosses' and self.selection<5:
                level=self.selection+1;self.new_run(level,True);self.resume();a=self.app
                a.intro=None;a.guardian_practice=False;a.level=level;a.reset_encounter()
            elif self.page=='credits' and key=='space':self.credits_page=(self.credits_page+1)%3
            elif choice=='Back':self.open(self.parent)
        elif self.page=='credits' and key in ('left','right'):self.credits_page=(self.credits_page+(1 if key=='right' else -1))%3
        return True
    def observe(self,dt,old_f,old_hp,old_hits,active):
        a=self.app;f=a.f
        if self.award and self.award!=a.level:self.award=None
        self.finish_age+=dt
        if self.last_state not in ('dying','ending','won','rescue') and f.state in ('dying','ending','rescue'):
            self.finish_age=0.
        self.last_state=f.state
        # Brief breathing room under the existing final destruction sounds.
        duck=.65+.35*min(1,self.finish_age/.65)
        a.game_music.set_volume(85*self.profile.settings['music']/100*duck)
        if old_f is f:
            self.record.observe(a.level,dt,getattr(f,'damage_taken',0)-old_hits,old_hp-f.hp,active,getattr(f,'unlimited_lives',False))
        if self.award is not None:self.award_age+=dt
        if f.state=='won' and a.level not in self.record.cleared:
            self.record.cleared.add(a.level);self.award=a.level;self.award_age=0.
            a.weapon_audio.ui_effects.trigger('accept')
        if a.level==5 and f.state=='won' and not self.result_saved and self.award_age>=3.:
            category=self.record.category
            if category!='practice':
                best=self.profile.best.get(category,float('inf'))
                self.profile.best[category]=min(best,self.record.elapsed);self.profile.save()
            self.result_saved=True;self.open('results')
    def draw(self,c):
        if self.record.hardcore and not self.app.intro and not self.page and not getattr(self.app,'continue_screen',None):
            c.set_source_rgba(.035,.025,.025,.85);c.rectangle(1030,668,230,27);c.fill()
            label(c,1040,686,'HARDCORE / NO CONTINUES',13,(.95,.53,.35))
        if self.award and self.award_age<3 and not self.page:
            t=self.award_age
            c.set_source_rgba(.025,.045,.04,.88);c.rectangle(375,80,530,100);c.fill()
            label(c,420,116,'STAGE CLEAR',24)
            label(c,420,146,'CAMPAIGN COMPLETE' if self.award==5 else 'EXTRA RIBBON AWARDED',16,(.65,.84,.48))
            if self.award<5:
                c.save();c.translate(850,105);c.scale(1.3,1.3)
                c.set_source_surface(medal(True));c.paint();c.restore()
        if not self.page:return
        from omacontra.ui.menu_art import draw
        draw(c,self)

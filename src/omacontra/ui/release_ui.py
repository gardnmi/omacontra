"""Player-facing menus, persisted preferences, campaign records and rewards."""
import json
import os
from pathlib import Path
import math
import cairo
from omacontra.rendering.health_medals import medal

NAMES=('THE REAPER','QUATTRO RUN','TIDEBREAKER','THE MIST GATE','BLACK MOON')
DEFAULTS={'music':100,'effects':100,'gunfire':100}

class Profile:
    def __init__(self,path=None):
        self.path=Path(path) if path else Path(os.environ.get('XDG_CONFIG_HOME',Path.home()/'.config'))/'omacontra/profile.json'
        self.settings=dict(DEFAULTS);self.best={};self.error=''
        try:
            data=json.loads(self.path.read_text())
            if not isinstance(data,dict):return
            for k in DEFAULTS:
                v=data.get('settings',{}).get(k,100)
                if isinstance(v,(int,float)) and math.isfinite(v):self.settings[k]=max(0,min(150,int(v)))
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
        self.losses+=max(0,losses);self.hits[level]=self.hits.get(level,0)+max(0,hits)
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
        self.credits_page=0;self.apply_audio()
        self.blocked=set();self.finish_age=99.;self.last_state=app.f.state
    def apply_audio(self):
        s=self.profile.settings
        for music in (self.app.music,self.app.game_music):music.set_volume(85*s['music']/100)
        self.app.unlock_sound.set_volume(85*s['effects']/100)
        self.app.weapon_audio.set_volumes(s['effects']/100,s['gunfire']/100)
    def open(self,page='pause'):
        self.page=page;self.selection=0;self.app.paused=True
        if self.app.intro:self.app.intro.paused=True
        self.app.keyboard.clear();self.app.shooting=False;self.app.slide_requested=False
        self.app.weapon_audio.silence()
    def resume(self):
        self.blocked=set(self.app.keys)
        self.page=None;self.app.paused=False
        if self.app.intro:self.app.intro.paused=False
        self.app.keyboard.clear();self.app.shooting=False;self.app.slide_requested=False
    def new_run(self,level=1,practice=False,hardcore=False):
        self.record=RunRecord(level,practice,hardcore);self.result_saved=False;self.award=None
    def rows(self):
        if self.page=='mode':return ['Standard','Hardcore','Back']
        if self.page=='pause':return ['Resume','Controls','Options']+([] if self.record.hardcore else ['Restart encounter'])+['Return to title','Credits','Quit']
        if self.page=='options':return [f'{k.upper():8}  {v:3}%' for k,v in self.profile.settings.items()]+['Back']
        if self.page=='results':return ['Play again','Boss select','Return to title','Credits','Quit']
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
            self.resume();a.return_to_title();self.new_run()
        elif action=='quit':a.close()
        elif action=='again':
            self.resume();self.new_run(hardcore=self.record.hardcore);a.guardian_practice=False;a.level=1;a.intro=None;a.reset_encounter()
    def key(self,key):
        if not self.page:return False
        rows=self.rows()
        if key in ('up','w'):self.selection=(self.selection-1)%len(rows)
        elif key in ('down','s'):self.selection=(self.selection+1)%len(rows)
        elif key in ('left','right','a','d') and self.page=='options' and self.selection<3:
            name=tuple(DEFAULTS)[self.selection];v=self.profile.settings[name]
            self.profile.settings[name]=max(0,min(150,v+(5 if key in ('right','d') else -5)))
            self.apply_audio();self.profile.save()
        elif key in ('escape','p'):
            if self.page in ('pause','mode'):self.resume()
            elif self.page=='results':pass
            elif self.page=='confirm':self.open(self.parent)
            else:self.open(self.parent)
        elif key in ('return','space'):
            choice=rows[self.selection]
            if self.page=='mode':
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
        c.set_source_rgba(.018,.024,.035,.96);c.paint()
        c.set_source_rgb(.39,.55,.34);c.set_line_width(2);c.rectangle(200,55,880,610);c.stroke()
        title={'mode':'CHOOSE YOUR RUN','pause':'PAUSED','options':'AUDIO OPTIONS','controls':'CONTROLS','results':'MISSION COMPLETE','bosses':'BOSS SELECT / PRACTICE','credits':'CREDITS','confirm':'ARE YOU SURE?'}[self.page]
        label(c,260,108,title,30)
        y=180
        if self.page=='results':
            r=self.record;label(c,260,158,f'{r.category.upper()} RUN   CLEAR TIME {time_text(r.elapsed)}',18)
            label(c,260,192,f'LIVES LOST {r.losses}    CONTINUES {r.continues}    RESTARTS {r.restarts}',16)
            label(c,260,223,f'NO-HIT STAGES {r.clean}/5',17)
            best=self.profile.best.get(r.category)
            if best:label(c,650,223,'PERSONAL BEST '+time_text(best),17)
            for i,name in enumerate(NAMES):
                if i+1 not in r.cleared:continue
                c.save();c.translate(725,280+i*52);c.scale(.85,.85);c.set_source_surface(medal(True));c.paint();c.restore()
                label(c,758,299+i*52,name,14)
                label(c,758,317+i*52,'NO HIT' if not r.hits.get(i+1,0) else 'CLEARED',11,(.65,.83,.47))
            y=295
        elif self.page=='mode':
            label(c,260,355,'STANDARD: 10-second continue countdown.',18)
            label(c,260,400,'HARDCORE: lose every life and the run ends.',18,(.95,.63,.43))
            label(c,260,440,'No continues, encounter restarts or unlimited lives.',16)
            label(c,260,480,'Both modes carry lives forward and award extra ribbons.',16)
        elif self.page=='controls':
            lines=['A/D or Arrows: move     Space/K: jump / double jump','J/Z: fire     Mouse + left click: aim and fire','S/Down: crouch     Shift: slide / air dash','Quattro: Space jumps; Shift boosts','Space: W/A/S/D move; Shift uses thrusters','Esc/P: pause menu     R: confirm restart','Menus: arrows select, Enter confirms','Options: Left/Right adjusts volume']
            for i,line in enumerate(lines):label(c,260,180+i*40,line,16)
            y=550
        elif self.page=='credits':
            pages=[['OMACONTRA','Created by gardnmi','DHH and Tobi: fictional action-adventure portrayals','Pixel artwork: AI-assisted original game assets','Visual direction: Omarchy wallpaper worlds','Movement inspiration: Contra; gun effects: Blazing Chrome'],['SOUNDTRACK','Off Duty Mercenary / user-provided track','Omarchy Oligarchy (Synthwave Mix) / YZL81','Contra / user-provided track','The Descent / user-provided track','Omacontra Opening Theme / user-provided track','Music source: Omarchy Radio and supplied recordings'],['SOUND AND TOOLS','Kenney / Sci-Fi Sounds (CC0)','Free Firearm Sound Library (CC0)','Ben Jaszczak, Brian Nelson, Kevin Heras, Matthew Nanney','Ocean Splash / Thimras (CC0)','Short Water Splashes / ezwa, qubodup (CC0)','Screensaver: Omarchy / terminal text effects','Full source notes: assets/audio/sources/README.md']]
            for i,line in enumerate(pages[self.credits_page]):label(c,260,170+i*40,line,15 if len(line)>55 else 18)
            label(c,260,515,f'LEFT / RIGHT: PAGE {self.credits_page+1}/3',15);y=560
        elif self.page=='confirm':label(c,260,168,'This will '+{'quit':'close the game.','title':'leave the current encounter.','restart':'restart the current encounter.'}.get(self.pending,'leave this run.'),18);y=260
        for i,row in enumerate(self.rows()):
            label(c,270,y+i*43,('> ' if i==self.selection else '  ')+row,22,(.72,.9,.5) if i==self.selection else (.78,.79,.73))
            if self.page=='options' and i<3:
                value=self.profile.settings[tuple(DEFAULTS)[i]]
                c.set_source_rgb(.14,.19,.15);c.rectangle(675,y+i*43-15,270,10);c.fill()
                c.set_source_rgb(.65,.83,.47);c.rectangle(675,y+i*43-15,270*value/150,10);c.fill()
                c.set_source_rgb(.8,.81,.68);c.rectangle(854,y+i*43-19,2,18);c.fill()
        label(c,260,638,'ARROWS / SELECT     ENTER / CONFIRM'+('' if self.page=='results' else '     ESC / BACK'),13)
        if self.page=='options' and not self.profile.error:label(c,260,570,'LEFT / RIGHT ADJUSTS BY 5%  /  SAVED AUTOMATICALLY',13)
        if self.profile.error:label(c,260,609,self.profile.error,13,(1,.55,.35))

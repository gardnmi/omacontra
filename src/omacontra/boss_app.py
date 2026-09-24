"""Single fullscreen host for the cinematic and boss encounter."""
import json
import os
import signal
import time
import gi
gi.require_version('Gtk','3.0');gi.require_version('Gdk','3.0');gi.require_version('GLibUnix','2.0')
from gi.repository import Gtk,Gdk,GLib,GLibUnix
from omacontra.desktop import Hyprland
from omacontra.stages.reaper.combat import Fight, W, H
from omacontra.stages.reaper.battle_art import BattleRenderer
from omacontra.input_state import KeyboardState
from omacontra.campaign_progress import prepare_encounter
from omacontra.ui.story import Intro
from omacontra.ui.art import Renderer
from omacontra.audio.weapon_audio import WeaponAudio, SFX_BOOST
from omacontra.audio.intro_music import IntroMusic, GAME_TRACKS, FINALE_TRACK, UNLOCK_SOUND, shuffled_tracks
from omacontra.rendering.frame_buffer import FrameBuffer
from omacontra.ui.release_ui import Frontend

class BossApp:
    def __init__(self,wallpaper=None,smoke=False,intro=False,level=1,guardians=False):
        self.weapon_audio=WeaponAudio()
        self.unlimited_lives=False
        self.guardian_practice=guardians
        if guardians:level=3;intro=False
        self.run_playlist=shuffled_tracks()
        self.music=IntroMusic();self.game_music=IntroMusic(playlist=self.run_playlist)
        self.unlock_sound=IntroMusic(track=UNLOCK_SOUND,extra_args=('--loop-file=no',))
        self.closed=False;self.window=None;self.rules=[];self.previous=None;self.sources=[]
        self.h=Hyprland();self.f=self.prepare_encounter(Fight(),1);self.renderer=BattleRenderer(wallpaper)
        self.tide_renderer=None;self.journey_cinema=None;self.tide_outro_seen=False
        self.foundry_renderer=None;self.foundry_intro=None
        self.continue_screen=None;self.continue_renderer=None;self.death_wait=0.
        self.level=1;self.chase_renderer=None;self.chase_cinema=None;self.chase_outro_seen=False
        if level==5:self.start_finale()
        elif level==2:self.start_chase()
        elif level==3:self.start_tide()
        elif level==4:self.start_foundry()
        self.intro=Intro() if intro else None;self.intro_renderer=Renderer() if intro else None
        if self.intro_renderer:self.intro_renderer.arrival_renderer=self.renderer
        self.keyboard=KeyboardState();self.keys=self.keyboard.keys;self.slide_requested=False;self.shooting=False;self.aim=None;self.paused=False
        self.placed=False;self.visible=True;self.fullscreen=False;self.last=self.started=time.monotonic()
        self.frontend=Frontend(self)
        try:self.setup(smoke)
        except Exception:self.close();raise

    def prepare_encounter(self,f,level):
        f=prepare_encounter(f,level)
        f.unlimited_lives=getattr(self,'unlimited_lives',False)
        return f

    def advance_campaign(self):
        remaining=self.f.hp
        next_level=self.level+1
        starters={2:self.start_chase,3:self.start_tide,4:self.start_foundry,5:self.start_finale}
        if next_level not in starters:return
        starters[next_level]()
        prepare_encounter(self.f,next_level,remaining=remaining)

    def start_chase(self):
        from omacontra.stages.highway.chase import Chase
        from omacontra.stages.highway.chase_art import ChaseRenderer
        from omacontra.stages.highway.chase_cinema import ChaseCinema
        self.level=2;self.f=self.prepare_encounter(Chase(),2);self.chase_cinema=ChaseCinema();self.chase_outro_seen=False
        if self.chase_renderer is None:self.chase_renderer=ChaseRenderer()

    def start_tide(self):
        from omacontra.stages.harbor.tidebreaker import Tidebreaker
        from omacontra.stages.harbor.tide_art import TideRenderer
        from omacontra.stages.harbor.journey_cinema import JourneyCinema
        self.level=3;self.f=self.prepare_encounter(Tidebreaker(),3);self.chase_cinema=None
        self.journey_cinema=JourneyCinema();self.tide_outro_seen=False
        if self.tide_renderer is None:self.tide_renderer=TideRenderer()
        if getattr(self,'guardian_practice',False):
            self.journey_cinema=None;self.f.advance_guardian()
            self.f.y=self.f.floor;self.f.respawn_anchor=(self.f.x,self.f.y)


    def reset_encounter(self):
        self.continue_screen=None;self.death_wait=0.
        if self.level==5:self.start_finale()
        elif self.level==2:self.start_chase()
        elif self.level==3:self.start_tide()
        elif self.level==4:self.start_foundry()
        else:self.f=self.prepare_encounter(Fight(),1)
        self.slide_requested=False;self.paused=False;self.shooting=False;self.keyboard.consume()

    def start_finale(self):
        from omacontra.stages.space.finale import Finale
        from omacontra.stages.space.finale_art import FinaleRenderer
        self.level=5;self.f=self.prepare_encounter(Finale(),5);self.finale_renderer=FinaleRenderer()
        self.chase_cinema=None;self.journey_cinema=None;self.foundry_intro=None

    def continue_encounter(self):
        if getattr(self,'frontend',None):
            if self.frontend.record.hardcore:return
            self.frontend.record.continues+=1
        guardians=self.level==3 and bool(getattr(self.f,'stage',0))
        self.reset_encounter()
        self.chase_cinema=None;self.journey_cinema=None;self.foundry_intro=None
        if guardians and not self.f.stage:self.f.advance_guardian()
        if self.level==5:self.f.skip()

    def return_to_title(self):
        self.continue_screen=None;self.death_wait=0.;self.level=1
        self.unlimited_lives=False;self.guardian_practice=False
        self.f=self.prepare_encounter(Fight(),1)
        self.chase_cinema=None;self.journey_cinema=None;self.foundry_intro=None
        self.intro=Intro();self.intro.index=len(self.intro.beats)-1
        if self.intro_renderer is None:self.intro_renderer=Renderer()
        self.intro_renderer.arrival_renderer=self.renderer
        self.music.restart()
        if getattr(self,'frontend',None):self.frontend.new_run()
        self.paused=False;self.keyboard.consume();self.shooting=False;self.slide_requested=False

    def start_foundry(self):
        from omacontra.stages.dragon.foundry import Foundry
        from omacontra.stages.dragon.foundry_art import FoundryRenderer, FoundryIntro
        self.level=4;self.f=self.prepare_encounter(Foundry(),4);self.chase_cinema=None;self.journey_cinema=None
        self.foundry_intro=FoundryIntro()
        if getattr(self,'foundry_renderer',None) is None:self.foundry_renderer=FoundryRenderer()

    def setup(self,smoke):
        self.previous=self.h.request('activeworkspace',True)['name']
        used={w['id'] for w in self.h.request('workspaces',True)}
        self.workspace=next(i for i in range(2,1000) if i not in used)
        self.title=f'Omacontra-{os.getpid()}-game'
        rule=f'omacontra_boss_{os.getpid()}';self.rules.append(rule)
        self.h.request(f'eval {rule}=hl.window_rule({{name="{rule}",match={{initial_title="^{self.title}$"}},workspace="{self.workspace}",float=false,no_anim=true,no_blur=true,no_shadow=true,border_size=0,rounding=0,opacity="1 override 1 override"}})')
        self.h.run(f'hl.dsp.focus({{workspace="{self.workspace}"}})')
        win=self.window=Gtk.Window(title=self.title);win.set_decorated(False);win.set_default_size(W,H)
        win.connect('delete-event',lambda *_:self.close() or True)
        win.connect('key-press-event',self.key);win.connect('key-release-event',self.release)
        win.connect('focus-out-event',self.unfocus)
        self.area=Gtk.DrawingArea();self.area.add_events(Gdk.EventMask.POINTER_MOTION_MASK|Gdk.EventMask.BUTTON_PRESS_MASK|Gdk.EventMask.BUTTON_RELEASE_MASK)
        self.area.connect('draw',self.draw);self.area.connect('button-press-event',self.button);self.area.connect('button-release-event',self.button);self.area.connect('motion-notify-event',self.motion)
        win.add(self.area);win.show_all()
        self.sources.extend([GLib.timeout_add(80,self.sync),GLib.timeout_add(16,self.tick)])
        for sig in (signal.SIGTERM,signal.SIGINT):self.sources.append(GLibUnix.signal_add(GLib.PRIORITY_DEFAULT,sig,self.close))
        if smoke:self.sources.append(GLib.timeout_add(6000,self.smoke_end))

    def smoke_end(self):
        print('SMOKE '+('PASS: one fullscreen window' if self.placed and self.fullscreen else 'FAIL: fullscreen not confirmed'),flush=True)
        self.close();return False

    def sync(self):
        if self.closed:return False
        try:
            client=next((c for c in self.h.request('clients',True) if c.get('initialTitle')==self.title),None)
            if not client:
                if self.placed or time.monotonic()-self.started>6:self.close();return False
                return True
            if not self.placed:
                selector=json.dumps('address:'+client['address'])
                self.h.focus(client['address'])
                self.h.run(f'hl.dsp.window.fullscreen({{window={selector},mode="fullscreen",action="set"}})')
                self.placed=True;print(f'OMACONTRA READY workspace={self.workspace}',flush=True)
            self.fullscreen=bool(client.get('fullscreen',0))
            self.visible=self.h.request('activeworkspace',True)['id']==self.workspace
            if not self.visible:
                self.slide_requested=False;self.keyboard.clear();self.shooting=False
                if getattr(self,'frontend',None) and not self.frontend.page:self.frontend.open()
        except Exception as error:print(f'OMACONTRA: {error}',flush=True);self.close();return False
        return True

    def tick(self):
        if self.closed:return False
        now=time.monotonic();dt=min(.04,now-self.last);self.last=now
        front=getattr(self,'frontend',None)
        menu=bool(front and front.page)
        old_f=self.f;old_hp=self.f.hp;old_hits=getattr(self.f,'damage_taken',0)
        active=not self.paused and not self.intro and not menu and self.f.state=='play' and not any(getattr(self,n,None) for n in ('chase_cinema','journey_cinema','foundry_intro'))
        if front:self.music.set_volume(85*(SFX_BOOST if self.music.start_effect else 1)*front.profile.settings['effects' if self.music.start_effect else 'music']/100)
        choosing_run=bool(menu and front.page=='mode')
        browsing_music=bool(menu and front.page=='music')
        if browsing_music:front.jukebox.update(self.placed and self.visible,85*front.profile.settings['music']/100)
        self.music.update(bool(self.intro and not self.intro.journey),
                          browsing_music or not self.placed or not self.visible or bool(self.intro and self.intro.paused and not choosing_run))
        if getattr(self,'game_music',None):
            # Results menus freeze gameplay, but the finale soundtrack continues.
            results_music=bool(menu and self.level==5 and self.f.state=='won' and front.result_saved)
            self.game_music.select_playlist((FINALE_TRACK,) if self.level==5 and self.intro is None else getattr(self,'run_playlist',GAME_TRACKS))
            self.game_music.update(self.intro is None or self.intro.journey,
                                   browsing_music or not self.placed or not self.visible or
                                   (self.intro.paused if self.intro else self.paused and not results_music))
        if getattr(self,'unlock_sound',None):
            ringing=bool(self.intro and self.intro.unlock_age is not None and self.intro.unlock_age<2.05 and self.intro.start_age is None)
            self.unlock_sound.update(ringing,not self.placed or not self.visible or bool(self.intro and self.intro.paused))
        if self.placed and self.visible and not menu:
            if getattr(self,'continue_screen',None):
                self.continue_screen.step(dt)
                if self.continue_screen.finished:self.continue_encounter()
            elif self.intro:
                self.intro.step(dt)
                if self.intro.start_finished:
                    self.music.stop();self.intro=Intro(journey=True)
                    self.intro.unlimited_lives=getattr(self,'unlimited_lives',False)
                    self.keyboard.consume();self.shooting=False
                elif self.intro.finished:
                    self.intro=None;self.f=self.prepare_encounter(Fight(),1);self.keyboard.consume();self.shooting=False
            elif not self.paused and getattr(self,'foundry_intro',None):
                self.foundry_intro.step(dt);self.slide_requested=False
                if self.foundry_intro.finished:
                    self.foundry_intro=None;self.keyboard.consume();self.shooting=False
            elif not self.paused and getattr(self,'journey_cinema',None):
                self.journey_cinema.step(dt);self.slide_requested=False
                if self.journey_cinema.finished:
                    self.journey_cinema=None;self.keyboard.consume();self.shooting=False
            elif not self.paused and self.chase_cinema:
                self.chase_cinema.step(dt)
                self.slide_requested=False
                if self.chase_cinema.finished:
                    self.chase_cinema=None;self.keyboard.consume();self.shooting=False
            elif not self.paused:
                k=self.keys
                self.f.step(dt,move=int(bool(k&{'d','right'}))-int(bool(k&{'a','left'})),jump=bool(k&{'space','k'}),duck=bool(k&{'s','down'}),shoot=self.shooting or bool(k&{'j','z'}),aim=(self.f.screen_to_world(self.aim) if self.level in (2,4) else self.aim) if self.shooting or (self.level==2 and self.f.state=='finisher') else None,aim_up=bool(k&{'w','up'}),slide=bool(k&{'shift_l','shift_r'}),slide_pressed=self.slide_requested,**({'interact':bool(k&{'e'})} if self.level==3 else {'vertical':int(bool(k&{'s','down'}))-int(bool(k&{'w','up'}))} if self.level==5 else {}))
                self.slide_requested=False
                if self.level==2 and self.f.state=='won' and not self.chase_outro_seen:
                    from omacontra.stages.highway.chase_cinema import ChaseCinema
                    self.chase_cinema=ChaseCinema('outro');self.chase_cinema.age=.8;self.chase_outro_seen=True
                    self.shooting=False;self.keyboard.consume()
                if self.level==3 and self.f.state=='won' and not self.tide_outro_seen:
                    from omacontra.stages.harbor.journey_cinema import JourneyCinema
                    self.journey_cinema=JourneyCinema('outro');self.tide_outro_seen=True
                    self.shooting=False;self.keyboard.consume()
            if not self.intro and self.f.state=='dead' and not getattr(self,'continue_screen',None):
                self.death_wait=getattr(self,'death_wait',0.)+dt
                if self.death_wait>=1.2:
                    from omacontra.ui.continue_screen import ContinueScreen, ContinueRenderer
                    if self.continue_renderer is None:self.continue_renderer=ContinueRenderer()
                    self.continue_screen=ContinueScreen(hardcore=bool(front and front.record.hardcore));self.paused=False
                    self.continue_blocked_keys=set(self.keys)
                    self.keyboard.consume();self.shooting=False;self.slide_requested=False
            self.area.queue_draw()
        if front and self.placed and self.visible and not menu:front.observe(dt,old_f,old_hp,old_hits,active)
        if menu and self.placed and self.visible:self.area.queue_draw()
        if getattr(self,'weapon_audio',None):
            if menu:
                self.weapon_audio.update_menu(self.placed and self.visible);return True
            if getattr(self,'continue_screen',None):
                self.weapon_audio.update(self.continue_screen,False,self.placed and self.visible)
                return True
            audible=(self.placed and self.visible and not self.paused and not self.intro
                     and self.level!=5 and self.f.state=='play'
                     and not any(getattr(self,name,None) for name in ('chase_cinema','journey_cinema','foundry_intro'))
                     and getattr(self.f,'hit_age',None) is None
                     and (self.shooting or bool(self.keys&{'j','z'})))
            # Let the robot explosion decay naturally into its immediate outro.
            chase_outro=(self.level==2 and self.f.state=='won'
                         and getattr(getattr(self,'chase_cinema',None),'kind',None)=='outro')
            effects_audible=(self.placed and self.visible and not self.paused and not self.intro
                             and self.level in (1,2,3,4,5)
                             and (not getattr(self,'chase_cinema',None) or chase_outro)
                             and not any(getattr(self,name,None) for name in ('journey_cinema','foundry_intro')))
            self.weapon_audio.update(self.f,audible,effects_audible)
        return True

    def viewport(self):
        width,height=self.area.get_allocated_width(),self.area.get_allocated_height()
        scale=min(width/W,height/H)
        return (width-W*scale)/2,(height-H*scale)/2,scale

    def draw(self,area,c):
        # Compose gameplay, cinematics and UI at one fixed resolution. Only
        # this final presentation scales to the display (including HiDPI).
        c.set_source_rgb(0,0,0);c.paint()
        ox,oy,scale=self.viewport()
        if scale<=0:return
        if not getattr(self,'frame',None):self.frame=FrameBuffer(W,H)
        def render(scene):
            front=getattr(self,'frontend',None)
            if not (front and front.page):
                scene.save();self.draw_scene(area,scene);scene.restore()
            if front:front.draw(scene)
        c.save();c.translate(ox,oy);c.scale(scale,scale)
        self.frame.draw(c,render)
        c.restore()

    def draw_scene(self,area,c):
        # Native 1280x720 coordinates; display transforms belong in draw().
        if getattr(self,'continue_screen',None):
            self.continue_renderer.draw(c,self.continue_screen)
            return
        if self.intro:self.intro_renderer.draw(c,self.intro,W,H);return
        if self.level==5:
            self.finale_renderer.draw(c,self.f,self.paused);return
        if self.level==4:
            if self.foundry_intro:self.foundry_intro.draw(c,self.foundry_renderer,self.f)
            else:self.foundry_renderer.draw(c,self.f,self.paused)
            return
        if self.level==3:
            if self.journey_cinema:self.journey_cinema.draw(c,self.tide_renderer,self.f)
            else:self.tide_renderer.draw(c,self.f,self.paused)
            return
        if self.level==2:
            if self.chase_cinema:self.chase_cinema.draw(c,self.chase_renderer,self.f)
            elif self.f.state=='dying' and self.f.death_age>=1.2:
                from omacontra.stages.highway.chase_cinema import ChaseCinema
                transition=ChaseCinema('outro');transition.age=self.f.death_age-1.2
                transition.draw(c,self.chase_renderer,self.f)
            else:self.chase_renderer.draw(c,self.f,self.paused)
            return
        self.renderer.background(c,self.f,'arena')
        for role in ('eye','raven'):self.renderer.weak_point(c,self.f,role)
        aim=self.aim if self.shooting else (self.f.x+self.f.facing*100,self.f.player_center[1]-102) if self.keys&{'w','up'} else None
        self.renderer.objects(c,self.f,aim);self.renderer.hud(c,self.f,self.paused)

    def motion(self,area,event):
        ox,oy,scale=self.viewport();self.aim=((event.x-ox)/scale,(event.y-oy)/scale)
        if getattr(self,'frontend',None) and self.frontend.page:self.frontend.pointer(*self.aim)
        return True

    def button(self,area,event):
        if getattr(self,'frontend',None) and self.frontend.page:
            ox,oy,scale=self.viewport()
            if event.button==1 and event.type==Gdk.EventType.BUTTON_PRESS:self.frontend.pointer((event.x-ox)/scale,(event.y-oy)/scale,True)
            return True
        self.motion(area,event)
        if event.button==1:self.shooting=event.type!=Gdk.EventType.BUTTON_RELEASE
        return True

    def key(self,win,event):
        key,fresh=self.keyboard.press(event.hardware_keycode,Gdk.keyval_name(event.keyval) or '')
        if not fresh:return True
        front=getattr(self,'frontend',None)
        if front:
            if key in front.blocked:return True
            if front.page:return front.key(key)
            if key in ('escape','p'):
                front.open();return True
            if key=='r' and not getattr(self,'continue_screen',None) and not (self.intro and self.intro.beat.kind=='cover'):
                front.request('restart');return True
        if key in ('shift_l','shift_r') and not self.intro and not self.paused:self.slide_requested=True
        if key=='escape':self.close()
        elif getattr(self,'continue_screen',None):
            if key in getattr(self,'continue_blocked_keys',set()):return True
            if key in ('return','space','r'):
                if self.continue_screen.state=='countdown':self.continue_screen.accept()
                elif self.continue_screen.state=='expired' and self.continue_screen.age>=.7:self.return_to_title()
            return True
        elif not self.intro and self.f.state=='dead':return True
        elif key=='f6' and self.level==3 and not (front and front.record.hardcore):
            self.guardian_practice=True;self.reset_encounter()
        elif self.intro:
            if self.intro.enter_code(key):
                self.unlimited_lives=True;self.f.unlimited_lives=True
                self.unlock_sound.update(True)
            if key=='r':
                self.intro.reset()
                if not self.intro.journey:self.music.restart()
            elif key=='p':self.intro.paused=not self.intro.paused
            elif key in ('space','return'):
                if self.intro.beat.kind=='cover':
                    if front and self.intro.start_age is None:
                        front.open('mode');return True
                    if self.intro.request_start():self.music.play_start()
                    self.shooting=False;self.keyboard.consume()
                else:self.intro.advance()
        elif self.level==5 and self.f.state in ('departure','encounter') and key=='return':
            if self.f.state=='departure':self.f.begin_encounter()
            else:self.f.skip()
            self.keyboard.consume();self.shooting=False
        elif self.level==4 and self.f.state=='won' and key=='return':
            self.advance_campaign();self.keyboard.consume();self.shooting=False;self.slide_requested=False
        elif getattr(self,'foundry_intro',None) and key=='return':self.foundry_intro.skip()
        elif getattr(self,'journey_cinema',None) and self.journey_cinema.kind=='intro' and key=='return':self.journey_cinema.skip()
        elif self.chase_cinema and self.chase_cinema.kind=='intro' and key=='return':self.chase_cinema.skip()
        elif key=='p':self.paused=not self.paused
        elif key=='r':self.reset_encounter()
        elif key=='return' and self.level==1 and self.f.state=='won':
            self.advance_campaign();self.keyboard.consume();self.shooting=False;self.slide_requested=False
        elif key=='return' and self.level==2 and self.f.state=='won' and self.chase_cinema and self.chase_cinema.age>=5.5:
            self.advance_campaign();self.keyboard.consume();self.shooting=False;self.slide_requested=False
        elif key=='return' and self.level==3 and self.f.state=='won' and self.journey_cinema and self.journey_cinema.kind=='outro':
            self.advance_campaign();self.keyboard.consume();self.shooting=False;self.slide_requested=False
        return True

    def release(self,win,event):
        self.keyboard.release(event.hardware_keycode)
        if getattr(self,'frontend',None):self.frontend.blocked.discard((Gdk.keyval_name(event.keyval) or '').lower())
        if getattr(self,'continue_blocked_keys',None):
            self.continue_blocked_keys.discard((Gdk.keyval_name(event.keyval) or '').lower())
        return True
    def unfocus(self,*_):
        if getattr(self,'frontend',None) and self.placed and not self.frontend.page:self.frontend.open()
        # Releases may go to another app; do not retain consumed physical keys.
        self.slide_requested=False;self.keyboard.clear();self.shooting=False
        if getattr(self,'weapon_audio',None):self.weapon_audio.silence()
        return False

    def close(self,*_):
        if self.closed:return False
        self.closed=True
        if getattr(self,'weapon_audio',None):self.weapon_audio.close()
        if getattr(self,'music',None):self.music.stop()
        if getattr(self,'game_music',None):self.game_music.stop()
        if getattr(self,'frontend',None):self.frontend.jukebox.stop()
        if getattr(self,'unlock_sound',None):self.unlock_sound.stop()
        for source in self.sources:
            if GLib.MainContext.default().find_source_by_id(source):GLib.source_remove(source)
        if self.window:self.window.destroy()
        for rule in self.rules:
            try:self.h.request(f'eval if {rule} then {rule}:set_enabled(false);{rule}=nil end')
            except Exception as error:print(error,flush=True)
        if self.previous is not None:
            try:
                if self.h.request('activeworkspace',True)['id']==self.workspace:self.h.run(f'hl.dsp.focus({{workspace={json.dumps(self.previous)}}})')
            except Exception as error:print(error,flush=True)
        if Gtk.main_level():Gtk.main_quit()
        return False

def launch(wallpaper=None,smoke=False,intro=False,level=1,guardians=False):
    app=BossApp(wallpaper,smoke,intro,level,guardians)
    try:Gtk.main()
    finally:app.close()

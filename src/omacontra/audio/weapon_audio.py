"""Stage and UI sound effects through one bounded SDL stream; player gun is silent."""
from omacontra.resources import ASSETS
import ctypes as C
from ctypes.util import find_library
from omacontra.audio.reaper_audio import ReaperEffects
from omacontra.audio.chase_audio import ChaseEffects
from omacontra.audio.tide_audio import TideEffects
from omacontra.audio.foundry_audio import FoundryEffects
from omacontra.audio.finale_audio import FinaleEffects

AUDIO=ASSETS/'audio'
SFX_BOOST=1.10

class AudioSpec(C.Structure):
    _fields_=[('freq',C.c_int),('format',C.c_uint16),('channels',C.c_uint8),
              ('silence',C.c_uint8),('samples',C.c_uint16),('padding',C.c_uint16),
              ('size',C.c_uint32),('callback',C.c_void_p),('userdata',C.c_void_p)]

class WeaponAudio:
    def __init__(self):
        self.effects=ReaperEffects()
        self.banks={'reaper':self.effects,'chase':ChaseEffects(),'tide':TideEffects(),'foundry':FoundryEffects(),'finale':FinaleEffects()}
        self.banks['continue']=ReaperEffects(audio=AUDIO/'continue',priority={'tick':1,'accept':3,'death_blow':4})
        self.ui_effects=ReaperEffects(audio=AUDIO/'continue',priority={'accept':3})
        self.menu_effects=ReaperEffects(audio=AUDIO/'menu',priority={'confirm':3,'complete':4})
        self.lib=None;self.device=0;self.initialized=False;self.failed=False
        self.owner=None

    def set_volumes(self,effects):
        for bank in self.banks.values():bank.gain=SFX_BOOST*max(0,min(1.5,effects))
        self.ui_effects.gain=SFX_BOOST*max(0,min(1.5,effects))
        self.menu_effects.gain=SFX_BOOST*max(0,min(1.5,effects))
        if self.device:self.lib.SDL_ClearQueuedAudio(self.device)

    def open(self):
        if self.device:return True
        if self.failed:return False
        try:
            name=find_library('SDL2') or find_library('SDL2-2.0')
            if not name:raise OSError('SDL2 audio library is unavailable')
            lib=self.lib=C.CDLL(name)
            for name,args,result in (
                ('SDL_InitSubSystem',[C.c_uint32],C.c_int),
                ('SDL_QuitSubSystem',[C.c_uint32],None),
                ('SDL_GetError',[],C.c_char_p),
                ('SDL_OpenAudioDevice',[C.c_char_p,C.c_int,C.POINTER(AudioSpec),C.POINTER(AudioSpec),C.c_int],C.c_uint32),
                ('SDL_PauseAudioDevice',[C.c_uint32,C.c_int],None),
                ('SDL_QueueAudio',[C.c_uint32,C.c_void_p,C.c_uint32],C.c_int),
                ('SDL_GetQueuedAudioSize',[C.c_uint32],C.c_uint32),
                ('SDL_ClearQueuedAudio',[C.c_uint32],None),
                ('SDL_CloseAudioDevice',[C.c_uint32],None)):
                fn=getattr(lib,name);fn.argtypes=args;fn.restype=result
            if lib.SDL_InitSubSystem(0x10):raise OSError(lib.SDL_GetError())
            self.initialized=True
            spec=AudioSpec(freq=44100,format=0x8010,channels=1,samples=512)
            self.device=lib.SDL_OpenAudioDevice(None,0,C.byref(spec),None,0)
            if not self.device:raise OSError(lib.SDL_GetError())
            lib.SDL_PauseAudioDevice(self.device,0)
            return True
        except (OSError,ValueError) as error:
            self.failed=True;self.close()
            print(f'Sound effects unavailable: {error}',flush=True)
            return False

    def update(self,f,enabled,effects_enabled=False):
        if f is not self.owner:
            self.owner=f
            self.effects.clear();self.ui_effects.clear()
            if self.device:self.lib.SDL_ClearQueuedAudio(self.device)
            self.effects=self.banks[getattr(f,'sound_bank','reaper')]
        events=getattr(f,'sfx_events',[])
        pending=list(events);events.clear()
        if isinstance(self.effects,FinaleEffects):
            self.effects.set_contact('shield' if effects_enabled and f.state=='play' and f.beam_hit and getattr(f,'laser_contact',None)=='shield' else None)
        if not effects_enabled:self.effects.clear()
        else:
            for name in pending:self.effects.trigger(name)
        if not effects_enabled and not self.ui_effects.voices and not self.menu_effects.voices:self.silence();return
        self.pump()

    def update_menu(self,visible=True):
        self.effects.clear();self.ui_effects.clear()
        if not visible:self.silence();return
        self.pump()

    def pump(self):
        if not self.effects.active and not self.ui_effects.voices and not self.menu_effects.voices:return
        if not self.open():return
        # One device mixes bounded effects, only 40 ms ahead.
        queued=self.lib.SDL_GetQueuedAudioSize(self.device)
        if queued>8820:
            self.lib.SDL_ClearQueuedAudio(self.device);queued=0
        while queued<3528:
            length=1764;data=bytes(length)
            data=self.effects.mix(data)
            data=self.ui_effects.mix(data)
            data=self.menu_effects.mix(data)
            if self.lib.SDL_QueueAudio(self.device,data,len(data)):
                self.failed=True;self.close();return
            queued+=len(data)

    def silence(self):
        self.effects.clear()
        self.ui_effects.clear()
        self.menu_effects.clear()
        if self.device:self.lib.SDL_ClearQueuedAudio(self.device)

    def close(self):
        self.effects.clear();self.ui_effects.clear();self.menu_effects.clear()
        if self.device:
            self.lib.SDL_ClearQueuedAudio(self.device);self.lib.SDL_CloseAudioDevice(self.device)
            self.device=0
        if self.initialized:self.lib.SDL_QuitSubSystem(0x10);self.initialized=False

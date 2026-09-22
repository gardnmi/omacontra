"""Quiet recorded automatic fire, streamed through one SDL audio device."""
from omacontra.resources import ASSETS
import ctypes as C
from ctypes.util import find_library
import wave
import time
import array
from omacontra.audio.reaper_audio import ReaperEffects
from omacontra.audio.chase_audio import ChaseEffects
from omacontra.audio.tide_audio import TideEffects
from omacontra.audio.foundry_audio import FoundryEffects
from omacontra.audio.finale_audio import FinaleEffects

AUDIO=ASSETS/'audio'

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
        self.lib=None;self.device=0;self.initialized=False;self.failed=False
        self.burst=b'';self.cursor=0;self.owner=None;self.serial=0;self.last_shot=None
        self.gun_gain=1.

    def set_volumes(self,effects,gunfire):
        self.gun_gain=max(0,min(1.5,gunfire))
        for bank in self.banks.values():bank.gain=max(0,min(1.5,effects))
        self.ui_effects.gain=max(0,min(1.5,effects))
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
            with wave.open(str(AUDIO/'machine-gun-burst.wav')) as f:
                if (f.getframerate(),f.getnchannels(),f.getsampwidth())!=(44100,1,2):
                    raise ValueError('Unexpected machine-gun sample format')
                self.burst=f.readframes(f.getnframes())
            spec=AudioSpec(freq=44100,format=0x8010,channels=1,samples=512)
            self.device=lib.SDL_OpenAudioDevice(None,0,C.byref(spec),None,0)
            if not self.device:raise OSError(lib.SDL_GetError())
            lib.SDL_PauseAudioDevice(self.device,0)
            return True
        except (OSError,ValueError,wave.Error) as error:
            self.failed=True;self.close()
            print(f'Machine-gun audio unavailable: {error}',flush=True)
            return False

    def update(self,f,enabled,effects_enabled=False):
        now=time.monotonic();serial=getattr(f,'machine_shots',0)
        if f is not self.owner:
            self.owner=f;self.serial=0;self.silence()
            self.effects=self.banks[getattr(f,'sound_bank','reaper')]
        events=getattr(f,'sfx_events',[])
        pending=list(events);events.clear()
        if not effects_enabled:self.effects.clear()
        else:
            for name in pending:self.effects.trigger(name)
        fired=serial>self.serial;self.serial=serial
        if not enabled or getattr(f,'laser',False):
            if self.last_shot is not None and self.device:self.lib.SDL_ClearQueuedAudio(self.device)
            self.last_shot=None;self.cursor=0
        elif fired:self.last_shot=now
        if self.last_shot is not None and now-self.last_shot>.15:
            self.last_shot=None;self.cursor=0
            if self.device:self.lib.SDL_ClearQueuedAudio(self.device)
        gun_active=self.last_shot is not None
        if not enabled and not effects_enabled and not self.ui_effects.voices:self.silence();return
        if not gun_active and not self.effects.voices and not self.ui_effects.voices:return
        if not self.open():return
        # One device mixes the gun and bounded effects, only 40 ms ahead.
        queued=self.lib.SDL_GetQueuedAudioSize(self.device)
        if queued>8820:
            self.lib.SDL_ClearQueuedAudio(self.device);queued=0
        while queued<3528:
            length=1764;data=bytes(length)
            if gun_active:
                end=self.cursor+length
                data=self.burst[self.cursor:end]
                if end>len(self.burst):data+=self.burst[:end-len(self.burst)]
                self.cursor=end%len(self.burst)
                if self.gun_gain!=1:data=array.array('h',(max(-32768,min(32767,round(v*self.gun_gain))) for v in array.array('h',data))).tobytes()
            data=self.effects.mix(data)
            data=self.ui_effects.mix(data)
            if self.lib.SDL_QueueAudio(self.device,data,len(data)):
                self.failed=True;self.close();return
            queued+=len(data)

    def silence(self):
        self.effects.clear()
        self.ui_effects.clear()
        self.last_shot=None;self.cursor=0
        if self.device:self.lib.SDL_ClearQueuedAudio(self.device)

    def close(self):
        self.effects.clear()
        if self.device:
            self.lib.SDL_ClearQueuedAudio(self.device);self.lib.SDL_CloseAudioDevice(self.device)
            self.device=0
        if self.initialized:self.lib.SDL_QuitSubSystem(0x10);self.initialized=False
        self.burst=b''

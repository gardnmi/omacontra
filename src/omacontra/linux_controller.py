"""Poll mapped controllers through the SDL2 library already used for audio.

SDL handles Xbox/HID variations (including GameSir), device permissions and
hotplug. GTK remains the window/input host; no extra window or thread is made.
Only the controller subsystem is acquired/released, never the audio subsystem.
"""
import ctypes as C
from ctypes.util import find_library

# SDL's button order differs from the browser's standard gamepad order.
BUTTONS={0:'a',1:'b',2:'x',3:'y',4:'view',6:'menu',7:'ls',8:'rs',9:'lb',10:'rb',11:'up',12:'down',13:'left',14:'right'}
INIT_GAMECONTROLLER=0x2000

class LinuxController:
    def __init__(self):
        self.handle=None;self.lib=None;self.next_scan=0.
        self.initialized=False;self.name='';self.error=''
        try:
            name=find_library('SDL2') or find_library('SDL2-2.0')
            if not name:raise OSError('SDL2 is unavailable')
            self.lib=C.CDLL(name)
            for name,args,result in (
                ('SDL_InitSubSystem',[C.c_uint32],C.c_int),
                ('SDL_QuitSubSystem',[C.c_uint32],None),
                ('SDL_GetError',[],C.c_char_p),
                ('SDL_NumJoysticks',[],C.c_int),
                ('SDL_IsGameController',[C.c_int],C.c_int),
                ('SDL_GameControllerOpen',[C.c_int],C.c_void_p),
                ('SDL_GameControllerClose',[C.c_void_p],None),
                ('SDL_GameControllerName',[C.c_void_p],C.c_char_p),
                ('SDL_GameControllerGetAttached',[C.c_void_p],C.c_int),
                ('SDL_GameControllerGetAxis',[C.c_void_p,C.c_int],C.c_int16),
                ('SDL_GameControllerGetButton',[C.c_void_p,C.c_int],C.c_uint8),
                ('SDL_GameControllerUpdate',[],None),
                ('SDL_GameControllerEventState',[C.c_int],C.c_int),
                ('SDL_JoystickEventState',[C.c_int],C.c_int),
                ('SDL_PumpEvents',[],None),
            ):
                fn=getattr(self.lib,name);fn.argtypes=args;fn.restype=result
            if self.lib.SDL_InitSubSystem(INIT_GAMECONTROLLER):
                raise OSError((self.lib.SDL_GetError() or b'Controller initialization failed').decode(errors='replace'))
            self.initialized=True
            # State is polled; do not fill SDL's unconsumed event queue.
            self.lib.SDL_GameControllerEventState(0)
            self.lib.SDL_JoystickEventState(0)
        except (OSError,AttributeError) as e:
            self.error=str(e);self.close()

    def close(self):
        if self.handle:self.lib.SDL_GameControllerClose(self.handle)
        self.handle=None
        if self.initialized:self.lib.SDL_QuitSubSystem(INIT_GAMECONTROLLER)
        self.initialized=False

    def poll(self,now):
        if not self.initialized:return None
        lib=self.lib
        lib.SDL_PumpEvents();lib.SDL_GameControllerUpdate()
        if self.handle and not lib.SDL_GameControllerGetAttached(self.handle):
            lib.SDL_GameControllerClose(self.handle);self.handle=None
            return None
        if self.handle is None:
            if now<self.next_scan:return None
            self.next_scan=now+1
            for index in range(lib.SDL_NumJoysticks()):
                if not lib.SDL_IsGameController(index):continue
                self.handle=lib.SDL_GameControllerOpen(index)
                if self.handle:
                    self.name=(lib.SDL_GameControllerName(self.handle) or b'Controller').decode(errors='replace')
                    lib.SDL_GameControllerUpdate();break
            if not self.handle:return None
        axes=[max(-1.,lib.SDL_GameControllerGetAxis(self.handle,i)/32767) for i in range(4)]
        buttons=[name for index,name in BUTTONS.items() if lib.SDL_GameControllerGetButton(self.handle,index)]
        for index,name in ((4,'lt'),(5,'rt')):
            if lib.SDL_GameControllerGetAxis(self.handle,index)>16383:buttons.append(name)
        return {'connected':True,'buttons':buttons,'axes':axes}

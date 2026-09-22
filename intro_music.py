"""Opening audio and continuous gameplay playlist using private mpv IPC."""
import json
from pathlib import Path
import socket
import subprocess

UNLOCK_SOUND=Path(__file__).parent/'assets/audio/unlimited-lives-unlock.wav'
START_SOUND=Path(__file__).parent/'assets/audio/omacontra-start-impact.wav'
TRACK=Path(__file__).parent/'assets/audio/omacontra-opening-theme.mp3'

JOURNEY_TRACK=Path(__file__).parent/'assets/audio/wine-cellar-off-duty-mercenary.mp3'
CHASE_TRACK=Path(__file__).parent/'assets/audio/quattro-run-omarchy-oligarchy.mp3'
GAME_TRACKS=(JOURNEY_TRACK,CHASE_TRACK,
             TRACK.parent/'contra.mp3',TRACK.parent/'the-descent.mp3',TRACK)

class IntroMusic:
    def __init__(self,extra_args=(),track=TRACK,playlist=None):
        self.process=None;self.socket=None;self.paused=None;self.failed=False
        self.track=track
        self.playlist=tuple(playlist) if playlist else None
        self.extra_args=extra_args
        self.start_effect=False
        self.volume=85

    def set_volume(self,value):
        value=max(0,min(150,value))
        if value!=self.volume:self.volume=value;self.command('set_property','volume',self.volume)

    def command(self,*args):
        if self.socket:
            try:self.socket.sendall((json.dumps({'command':list(args)})+'\n').encode())
            except OSError:self.stop()

    def update(self,active,paused=False):
        if not active:
            self.stop();return
        if self.failed or (self.start_effect and self.process is None):return
        if self.process is None:
            if paused:return  # Do not play before the game is visible.
            parent,child=socket.socketpair()
            try:
                self.process=subprocess.Popen([
                    'mpv','--no-config','--no-video','--audio-display=no','--no-terminal',
                    '--input-default-bindings=no',f'--volume={self.volume}',
                    *(['--loop-file=no','--loop-playlist=inf'] if self.playlist else ['--loop-file=inf']),
                    f'--input-ipc-client=fd://{child.fileno()}',*self.extra_args,'--',*[str(p) for p in (self.playlist or (self.track,))]],
                    pass_fds=(child.fileno(),),stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                self.socket=parent;self.paused=False
            except OSError as error:
                parent.close();self.failed=True
                print(f'Opening music unavailable: {error}',flush=True)
            finally:child.close()
        if self.process and self.process.poll() is not None:
            self.stop();self.failed=not self.start_effect;return
        if self.process and paused!=self.paused:
            self.command('set_property','pause',paused);self.paused=paused

    def play_start(self):
        if self.start_effect:return
        self.start_effect=True
        self.command('set_property','loop-file','no')
        self.command('loadfile',str(START_SOUND),'replace')
        self.command('set_property','pause',False)
        self.paused=False

    def restart(self):
        if self.start_effect:
            self.start_effect=False
            self.command('set_property','loop-file','inf')
            self.command('loadfile',str(self.track),'replace')
        self.command('seek',0,'absolute')

    def stop(self):
        if self.socket:self.socket.close();self.socket=None
        process=self.process;self.process=None;self.paused=None
        if process:
            if process.poll() is None:process.terminate()
            try:process.wait(timeout=.4)
            except subprocess.TimeoutExpired:process.kill();process.wait()

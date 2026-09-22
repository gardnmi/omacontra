"""Play the actual ttfx terminal frames through Cairo, without a subprocess.

Animations are exported by tools/build_screensaver.py at Omarchy's 120 FPS
and sampled at 30 FPS. Terminal parsing and rasterization happen at build
time; runtime only inflates cached pixels. Combat owns the playback clock.
"""
from functools import lru_cache
import struct
import zlib
import json
import random
import re
import cairo
import sprites

EFFECTS=('beams','rings','blackhole','fireworks','swarm','matrix','expand','colorshift')
SGR=re.compile(r'\x1b\[([0-9;]*)m')

@lru_cache(maxsize=1)
def clips():
    result={}
    for name in EFFECTS:
        with (sprites.ASSETS/'screensaver'/f'{name}.ttframes').open('rb') as stream:
            if stream.read(4)!=b'TTF1':raise ValueError('Invalid screensaver asset')
            size=struct.unpack('<I',stream.read(4))[0]
            clip=json.loads(stream.read(size));frames=[]
            for _ in range(clip['count']):
                size=struct.unpack('<I',stream.read(4))[0]
                data=stream.read(size)
                if len(data)!=size:raise ValueError('Truncated screensaver asset')
                frames.append(data)
            clip['frames']=frames;result[name]=clip
    return result

def frame_cells(frame):
    """Decode the engine's RGB SGR output; never interpret it in a terminal."""
    x=y=0;rgb=(255,255,255);cursor=0
    for match in SGR.finditer(frame):
        for ch in frame[cursor:match.start()]:
            if ch=='\n':y+=1;x=0
            else:
                if ch!=' ':yield x,y,ch,rgb
                x+=1
        codes=match.group(1)
        if codes in ('','0'):rgb=(255,255,255)
        elif codes.startswith('38;2;'):rgb=tuple(map(int,codes.split(';')[2:5]))
        cursor=match.end()
    for ch in frame[cursor:]:
        if ch=='\n':y+=1;x=0
        else:
            if ch!=' ':yield x,y,ch,rgb
            x+=1

class Screensaver:
    def __init__(self):
        self.clips=clips();self.key=None;self.surface=None
        self.cycle_duration=sum(len(c['frames'])/c['fps']+.6 for c in self.clips.values())

    def frame_at(self,t):
        t=max(0,t);cycle=int(t/self.cycle_duration);t%=self.cycle_duration
        order=list(EFFECTS)
        # Start with beams for an immediate visible transition; subsequent
        # cycles reshuffle the same authentic effects like the screensaver.
        if cycle:random.Random(73+cycle).shuffle(order)
        for name in order:
            clip=self.clips[name];duration=len(clip['frames'])/clip['fps']+.6
            if t<duration:
                index=min(len(clip['frames'])-1,int(t*clip['fps']))
                return name,index
            t-=duration
        return order[-1],len(self.clips[order[-1]]['frames'])-1

    @lru_cache(maxsize=4)
    def prepared_frame(self,name,index):
        clip=self.clips[name]
        # Baked pixels are native Cairo RGB24 (little-endian BGRX).
        data=bytearray(zlib.decompress(clip['frames'][index]))
        width,height=clip['pixel_width'],clip['pixel_height']
        if len(data)!=width*height*4:raise ValueError('Invalid screensaver pixel buffer')
        import sys
        if sys.byteorder!='little':
            for i in range(0,len(data),4):data[i:i+4]=data[i:i+4][::-1]
        return cairo.ImageSurface.create_for_data(data,cairo.FORMAT_RGB24,width,height,width*4)

    def draw(self,c,t,alpha):
        key=self.frame_at(t)
        if key!=self.key:
            self.key=key;self.surface=self.prepared_frame(*key)
        c.set_source_rgba(0,0,0,alpha);c.rectangle(0,0,1280,58);c.fill()
        c.save();c.translate(0,58);c.scale(1280/self.surface.get_width(),662/self.surface.get_height())
        c.set_source_surface(self.surface);c.get_source().set_filter(cairo.FILTER_NEAREST)
        c.paint_with_alpha(alpha);c.restore()

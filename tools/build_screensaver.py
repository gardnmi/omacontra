"""Export authentic ttfx effects for lightweight, simulation-timed playback.
Requires ttfx 0.3.2+. No terminal or system screensaver settings are changed.
"""
import gzip
import io
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
EFFECTS=('beams','rings','blackhole','fireworks','swarm','expand','colorshift')

def unpack(data):
    stream=io.BytesIO(data)
    while line:=stream.readline():
        size=int(line)
        frame=stream.read(size)
        if len(frame)!=size or stream.read(1)!=b'\n':
            raise ValueError('Truncated ttfx frame')
        yield frame.decode('utf-8')

def build():
    target=ROOT/'assets/screensaver';target.mkdir(exist_ok=True)
    version=subprocess.check_output(['ttfx','--version'],text=True).strip()
    for effect in EFFECTS:
        command=['ttfx','--parity-dump','--seed','42','--frame-rate','120',
                 '--canvas-width','96','--canvas-height','30',
                 '--ignore-terminal-dimensions','--anchor-text','c',
                 '-i',str(ROOT/'assets/omarchy-screensaver.txt'),effect]
        result=subprocess.run(command,capture_output=True,check=True,timeout=60)
        original=list(unpack(result.stdout))
        # Omarchy runs at 120 FPS; preserve its speed at 30 background FPS.
        frames=original[::4]
        if frames[-1]!=original[-1]:frames.append(original[-1])
        payload={'engine':version,'effect':effect,'fps':30,'width':96,'height':30,'frames':frames}
        (target/f'{effect}.json.gz').write_bytes(gzip.compress(json.dumps(payload,ensure_ascii=False).encode(),mtime=0))
        print(effect,len(original),'source frames,',len(frames),'playback frames',flush=True)

def rasterize():
    # Bake terminal interpretation and glyph rendering out of the game loop.
    import sys,struct,zlib
    sys.path.insert(0,str(ROOT/"src"))
    import cairo
    from omacontra.stages.space.screensaver_art import frame_cells
    for effect in EFFECTS:
        target=ROOT/'assets/screensaver'
        clip=json.loads(gzip.decompress((target/f'{effect}.json.gz').read_bytes()))
        surface=cairo.ImageSurface(cairo.FORMAT_RGB24,576,300)
        c=cairo.Context(surface);c.select_font_face('monospace');c.set_font_size(9)
        metadata={k:v for k,v in clip.items() if k!='frames'}
        metadata.update(pixel_width=576,pixel_height=300,count=len(clip['frames']))
        header=json.dumps(metadata).encode()
        with (target/f'{effect}.ttframes').open('wb') as out:
            out.write(b'TTF1');out.write(struct.pack('<I',len(header)));out.write(header)
            for frame in clip['frames']:
                c.set_source_rgb(0,0,0);c.paint()
                groups={}
                for x,y,ch,rgb in frame_cells(frame):groups.setdefault(rgb,[]).append((x*6,y*10,ch))
                for rgb,cells in groups.items():
                    c.set_source_rgb(*(v/255*.4 for v in rgb))
                    for x,y,ch in cells:
                        if ch=='█':c.rectangle(x,y,6,10)
                        elif ch=='▀':c.rectangle(x,y,6,5)
                        elif ch=='▄':c.rectangle(x,y+5,6,5)
                        else:c.move_to(x,y+8);c.show_text(ch)
                    c.fill()
                surface.flush();data=zlib.compress(bytes(surface.get_data()),6)
                out.write(struct.pack('<I',len(data)));out.write(data)
        print(effect,'raster frames baked',flush=True)

if __name__=='__main__':
    import sys
    if '--raster-only' not in sys.argv:build()
    rasterize()

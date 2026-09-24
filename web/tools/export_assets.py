#!/usr/bin/env python3
"""Prepare only Reaper assets; reuse desktop chroma-keying and authored poses.
Generated files are build output, never modifications of the source artwork.
"""
from pathlib import Path
import sys, json, shutil, math
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
import cairo
from omacontra.rendering import sprites
from omacontra.rendering.hero_pose import FRAMES, pose_rect
from types import SimpleNamespace
OUT=ROOT/'web/public/game'
OUT.mkdir(parents=True,exist_ok=True)
frames={};items=[]
def add(name,surface):items.append((name,surface))
def crop(name,sheet,frame):
    x,y,w,h=frame
    s=cairo.ImageSurface(cairo.FORMAT_ARGB32,int(w),int(h));c=cairo.Context(s)
    c.set_source_surface(sprites.atlas(sheet),-x,-y);c.paint();add(name,s)
for i,frame in enumerate(sprites.BOSS):crop(f'boss{i}','reaper-sprites.png',frame)
for name,frame in [('eye',sprites.EYE),('skull',sprites.SKULL),('impact',sprites.IMPACT)]:crop(name,'reaper-sprites.png',frame)
for i,frame in enumerate(sprites.RAVENS):crop(f'raven{i}','reaper-sprites.png',frame)
crop('wave','reaper-energy-wave.png',(40,165,2090,420))
# Downsample the large energy strip to a useful atlas size.
name,large=items.pop();s=cairo.ImageSurface(cairo.FORMAT_ARGB32,1045,210);c=cairo.Context(s);c.scale(.5,.5);c.set_source_surface(large);c.paint();add(name,s)
crop('weapon','dhh-weapon-v2.png',(0,240,1536,530))
name,large=items.pop();s=cairo.ImageSurface(cairo.FORMAT_ARGB32,216,75);c=cairo.Context(s);c.scale(216/1536,75/530);c.set_source_surface(large);c.paint();add(name,s)

def hero(name,mode='stand',frame=0):
    # 2x screen size gives authored detail without loading giant original sheets.
    s=cairo.ImageSurface(cairo.FORMAT_ARGB32,256,224);c=cairo.Context(s);c.scale(2,2)
    f=SimpleNamespace(x=64.,y=96.,floor=96.,facing=1,moving=False,sliding=mode=='slide',landing_age=0)
    index=4 if mode=='jump' else 5 if mode in ('duck','slide') else 0
    def body():
        left,top,w,h=pose_rect(f,index)
        sprites.draw(c,'dhh-modular-body.png',FRAMES[index],left,top,w,h)
    if mode.startswith('run'):
        sink=(0.,-.5,2.,0.,-.5,2.)[frame];leg=(1,2,0,4,5,3)[frame]
        centers=(280,288,275,265,278,260);top=85 if leg<3 else 65;sole=465 if leg<3 else 445
        scale=48/(sole-top);width=488*scale;anchor=(centers[leg]-24)*scale;seam=f.y-45+sink
        c.save();c.rectangle(f.x-90,seam,180,47);c.clip()
        sprites.draw(c,'dhh-run-legs.png',((leg%3)*512+24,(0 if leg<3 else 512)+top,488,sole-top),f.x-anchor,f.y-48+sink,width,48-sink);c.restore()
        c.save();c.rectangle(f.x-90,f.y-110,180,seam-(f.y-110));c.clip()
        if mode in ('runfire','runback'):
            c.translate(-1.5 if mode=='runback' else 1.5,sink);body()
        else:
            carry=(3,3,2,0,0,2)[frame];anchor=(230,208,151,220,223,196)[carry]
            belt=435 if carry<3 else 919;top=70 if carry<3 else 520;sw=490 if carry==3 else 512
            c.translate(f.x,seam);c.transform(cairo.Matrix(1,0,-.025,1,0,0));c.translate(-f.x,-seam)
            sprites.draw(c,'dhh-run-carry-v3.png',((carry%3)*512,top,sw,belt-top),f.x-anchor*.1,seam-(belt-top)*.1,sw*.1,(belt-top)*.1)
        c.restore()
    else:body()
    add(name,s)
for mode in ('stand','jump','duck','slide'):hero(mode,mode)
for i in range(6):
    hero(f'runfire{i}','runfire',i);hero(f'runback{i}','runback',i);hero(f'runcarry{i}','runcarry',i)
# Soft effect stamps uploaded once, transformed/tinted by the GPU each frame.
s=cairo.ImageSurface(cairo.FORMAT_ARGB32,128,128);c=cairo.Context(s)
g=cairo.RadialGradient(64,64,0,64,64,64);g.add_color_stop_rgba(0,1,1,1,1);g.add_color_stop_rgba(.25,1,1,1,.6);g.add_color_stop_rgba(1,1,1,1,0);c.set_source(g);c.paint();add('glow',s)
from omacontra.rendering.movement_fx import stamp
add('dust',stamp(False))
# Deterministic shelf-packed pages, with gutters to prevent neighboring bleed.
pages=[];page=None;x=y=row=0
for name,s in sorted(items,key=lambda item:(-item[1].get_height(),item[0])):
    w,h=s.get_width(),s.get_height()
    if page is None or y+h+2>2048:
        page=cairo.ImageSurface(cairo.FORMAT_ARGB32,2048,2048);pages.append(page);x=y=row=2
    if x+w+2>2048:x=2;y+=row+2;row=0
    if y+h+2>2048:
        page=cairo.ImageSurface(cairo.FORMAT_ARGB32,2048,2048);pages.append(page);x=y=row=2
    c=cairo.Context(page);c.set_source_surface(s,x,y);c.paint()
    frames[name]={'page':len(pages)-1,'rect':[x,y,w,h]};x+=w+2;row=max(row,h)
for i,page in enumerate(pages):page.write_to_png(str(OUT/f'atlas-{i}.png'))
bg=cairo.ImageSurface(cairo.FORMAT_RGB24,1280,720);c=cairo.Context(bg)
source=cairo.ImageSurface.create_from_png(str(ROOT/'assets/reaper-arena.png'))
sprites.paint_background(c,source,0,37,1280,(720-64)/.82);bg.write_to_png(str(OUT/'arena.png'))
(OUT/'audio').mkdir(exist_ok=True)
audio={}
for p in sorted((ROOT/'assets/audio/reaper').rglob('*.wav')):
    rel=p.relative_to(ROOT/'assets/audio/reaper');dest=OUT/'audio'/rel;dest.parent.mkdir(exist_ok=True);shutil.copy2(p,dest);audio[str(rel.with_suffix(''))]='audio/'+str(rel)
# Stream a gameplay song; the opening theme is deliberately excluded.
shutil.copy2(ROOT/'assets/audio/contra.opus',OUT/'music.opus')
(OUT/'credits').mkdir(exist_ok=True)
shutil.copy2(ROOT/'LICENSE',OUT/'credits/LICENSE.txt')
shutil.copytree(ROOT/'THIRD_PARTY',OUT/'credits/THIRD_PARTY',dirs_exist_ok=True)
(OUT/'manifest.json').write_text(json.dumps({'pages':[f'atlas-{i}.png' for i in range(len(pages))],'frames':frames,'audio':audio,'music':'music.opus'},indent=2)+'\n')
print(f'Exported {len(frames)} frames on {len(pages)} atlas pages; {sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())/1024**2:.1f} MiB total including streamed music.')

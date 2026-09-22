"""Render repeatable visual checks using the actual five encounter renderers.

Run: python asset_review.py --output /tmp/omacontra-art
The optional --video creates a short animated Foundry effects review.
"""
import argparse
import math
from pathlib import Path
import subprocess

import cairo


def scenes():
    from combat import Fight, Bullet
    from battle_art import BattleRenderer
    from chase import Chase
    from chase_art import ChaseRenderer
    from tidebreaker import Tidebreaker, TideHazard
    from tide_art import TideRenderer
    from foundry import Foundry, Hazard, Bolt
    from foundry_art import FoundryRenderer
    from finale import Finale
    from finale_art import FinaleRenderer

    f=Fight(7);f.clock=8;f.muzzle=.1
    r=BattleRenderer()
    def reaper(c,f):
        r.background(c,f,'arena');r.weak_point(c,f,'eye')
        r.weak_point(c,f,'raven');r.objects(c,f);r.hud(c,f)
    yield '01-reaper',reaper,f
    f=Chase();f.ramp_x=120;f.obstacles=[570];f.boost=.5
    yield '02-highway',ChaseRenderer().draw,f
    f=Tidebreaker(7);f.clock=8;f.wave_phase=2;f.boss_hp=75
    f.hazards=[TideHazard('surge',850,.2)]
    tide=TideRenderer()
    yield '03-ocean',tide.draw,f
    f=Tidebreaker(7);f.advance_guardian();f.clock=8
    for i,kind in enumerate(('heavy_slug','orbit_bolt','pressure_ring')):
        for j in range(4):
            f.shots.append(Bullet(390+j*125,450+i*64,-210,0,True,kind=kind))
    yield '03-guardians',tide.draw,f
    foundry=FoundryRenderer()
    for kind in ('fire','flood','shoulder'):
        f=Foundry(7);f.clock=8;f.muzzle=.1
        f.hazards=[Hazard(kind,630,1.5 if kind=='flood' else .3)]
        if kind=='shoulder':f.hazards=[];f.sweep_age=4.;f.enemy_beam=f.shoulder_path()
        f.bolts=[Bolt(520+i*55,310+i%3*24,-120,40) for i in range(5)]
        yield '04-'+kind,foundry.draw,f
    f=Foundry(7);f.begin_disarm();f.disarm_age=.6;f.clock=8
    yield '04-disarm',foundry.draw,f
    f=Foundry(7);f.laser=True;f.invuln=0
    f.step(.02,shoot=True,aim=f.core)
    yield '04-arc-rifle',foundry.draw,f
    finale=FinaleRenderer()
    for phase in (1,2,3):
        f=Finale();f.skip();f.clock=12
        if phase>1:f.nodes=[0,0]
        if phase==3:f.boss_hp=300
        f.last_phase=phase;f.phase_age=5;f.invuln=999
        for _ in range(130):f.step(.02)
        f.invuln=0
        yield '05-orbit-'+str(phase),finale.draw,f


def render(output,video=False):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    previews=[]
    for name,draw,f in scenes():
        surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720)
        draw(cairo.Context(surface),f)
        surface.write_to_png(str(output/(name+'.png')))
        previews.append((name,surface))
    sheet=cairo.ImageSurface(cairo.FORMAT_RGB24,1280,390*math.ceil(len(previews)/2))
    c=cairo.Context(sheet);c.set_source_rgb(.035,.04,.05);c.paint()
    for i,(name,surface) in enumerate(previews):
        x=i%2*640;y=i//2*390
        c.save();c.translate(x,y);c.scale(.5,.5);c.set_source_surface(surface);c.paint();c.restore()
        c.set_source_rgb(.9,.85,.7);c.set_font_size(14);c.move_to(x+12,y+380);c.show_text(name)
    sheet.write_to_png(str(output/'contact-sheet.png'))
    if video:
        from foundry import Foundry,Hazard
        from foundry_art import FoundryRenderer
        f=Foundry(7);r=FoundryRenderer()
        surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720)
        with subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pixel_format','bgra',
                               '-video_size','1280x720','-framerate','30','-i','-',
                               '-an','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p',
                               str(output/'effects-motion.mp4')],stdin=subprocess.PIPE) as process:
            for i in range(240):
                f.clock=i/30;f.muzzle=.1 if i%5<2 else 0
                f.sweep_age=1.2+i/30;f.enemy_beam=f.shoulder_path()
                r.draw(cairo.Context(surface),f);surface.flush();process.stdin.write(surface.get_data())
            process.stdin.close();process.wait()
            if process.returncode:raise RuntimeError('Video encoding failed')
    print(f'Rendered {len(previews)} gameplay states to {output}')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',default=str(Path(__file__).parent/'review'/'asset-quality'))
    parser.add_argument('--video',action='store_true')
    args=parser.parse_args();render(args.output,args.video)

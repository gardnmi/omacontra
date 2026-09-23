#!/usr/bin/env python3
"""OMACONTRA — fullscreen wallpaper boss rush."""
import argparse
from pathlib import Path
import subprocess

from omacontra.ui.story import Intro, COVER_AT
from omacontra.version import __version__


def render_preview(path):
    import cairo
    from omacontra.ui.art import Renderer, W, H
    path=Path(path)
    # ffmpeg -n exits 0 when it refuses to overwrite, so check first.
    if path.exists():raise RuntimeError(f'Refusing to overwrite {path}')
    path.parent.mkdir(parents=True,exist_ok=True)
    renderer=Renderer()
    intro=Intro()
    frames=round((COVER_AT+4)*30)
    process=subprocess.Popen([
        'ffmpeg','-nostdin','-n','-v','error','-f','rawvideo','-pixel_format','bgra',
        '-video_size',f'{W}x{H}','-framerate','30','-i','pipe:0','-an',
        '-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',
        '-movflags','+faststart',str(path)],stdin=subprocess.PIPE)
    stopped=False
    try:
        for frame in range(frames):
            surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H)
            renderer.draw(cairo.Context(surface),intro,W,H)
            surface.flush()
            try:process.stdin.write(surface.get_data())
            except BrokenPipeError:
                stopped=True;break
            intro.step(1/30)
    finally:
        try:process.stdin.close()
        except BrokenPipeError:pass
        code=process.wait()
    if code or stopped:
        raise RuntimeError(f'ffmpeg exited with {code}' if code else 'ffmpeg stopped reading frames')
    print(f'Rendered {frames/30:.1f}s: {path}')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version',action='version',version=f'Omacontra {__version__}')
    parser.add_argument('--render-preview',metavar='FILE.mp4',help='Render without a desktop; requires ffmpeg, refuses overwrite')
    parser.add_argument("--level",type=int,choices=(1,2,3,4,5),default=1,help="Start at Reaper (1), Quattro (2), Tidebreaker (3), Foundry (4), or Black Moon (5)")
    parser.add_argument("--guardians",action="store_true",help="Start directly at the Tidebreaker guardian duo; R retries the duo")
    parser.add_argument("--boss",action="store_true",help="Skip the opening cinematic")
    parser.add_argument("--wallpaper",help="Local reaper wallpaper PNG")
    parser.add_argument("--smoke-test",action="store_true",help="Open the fullscreen game and close after six seconds")
    parser.add_argument('--cutscene',nargs='?',const='ending',metavar='SCENE',help='Open the cutscene review gallery (default: ending)')
    parser.add_argument('--at',type=float,default=0,help='Start cutscene review at this many seconds')
    args=parser.parse_args()
    if args.cutscene:
        from omacontra.ui.cutscene_review import SCENES
        if args.cutscene not in SCENES:
            parser.error('Unknown cutscene. Choose: '+', '.join(SCENES))
        from omacontra.ui.cutscene_review import launch
        launch(args.cutscene,args.at)
    elif args.render_preview:render_preview(args.render_preview)
    else:
        from omacontra.boss_app import launch as launch_boss
        launch_boss(args.wallpaper,args.smoke_test,intro=not (args.boss or args.smoke_test or args.level>1),level=args.level,guardians=args.guardians)

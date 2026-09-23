#!/usr/bin/env python3
"""Normalize generated transparent cargo sprites to small runtime textures.

Usage: python tools/build_dock_cargo.py wood-generated.png steel-generated.png
Only alpha cropping and resampling occur here; artwork is generated separately.
"""
import argparse
from pathlib import Path
import cairo

ROOT=Path(__file__).resolve().parents[1]


def normalize(source, target):
    image=cairo.ImageSurface.create_from_png(str(source))
    if image.get_format()!=cairo.FORMAT_ARGB32:
        raise ValueError('Cargo sprite must have real transparency')
    image.flush();data=memoryview(image.get_data()).cast('B')
    width,height=image.get_width(),image.get_height();stride=image.get_stride()
    left,top,right,bottom=width,height,0,0
    for y in range(height):
        for x in range(width):
            if data[y*stride+x*4+3]>8:
                left=min(left,x);top=min(top,y);right=max(right,x+1);bottom=max(bottom,y+1)
    if right<=left or bottom<=top:raise ValueError('Empty sprite')
    surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,368,216)
    c=cairo.Context(surface);c.scale(368/(right-left),216/(bottom-top))
    c.set_source_surface(image,-left,-top);c.get_source().set_filter(cairo.FILTER_BEST);c.paint()
    surface.write_to_png(str(target))
    print(target, 'source bounds', (left,top,right,bottom))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('wood',type=Path);parser.add_argument('steel',type=Path)
    args=parser.parse_args()
    normalize(args.wood,ROOT/'assets/tide-dock-wood.png')
    normalize(args.steel,ROOT/'assets/tide-dock-steel.png')

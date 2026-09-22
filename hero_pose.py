"""Shared sprite geometry: rendering and firing use the same barrel position."""
import math

FRAMES=((45,48,305,409),(392,51,350,406),(810,56,315,401),(1170,55,365,402),
        (60,544,275,317),(400,654,355,310),(800,520,300,450),(1140,565,396,403))
ANCHORS=(25,37.8,30,40,23,31.6,24.2,22)
SCALE=.20
# Shoulder sockets in the cropped body frames (before scaling/mirroring).
# The tucked jump frame has a shorter silhouette, not a lower shoulder.
SHOULDERS={0:(90,110),4:(85,100),5:(110,100)}


def run_motion(f):
    """Two held carry beats, quick extended stride, then the opposite half.

    The close-up Contra reference holds each arm extreme across two leg poses;
    the lower, extended stride bridges them. Keep the head quiet, not swaying.
    """
    phase=f.run_phase if getattr(f,'run_direction',f.facing)==f.facing else -f.run_phase
    phase%=6
    boundaries=(1.2,2.4,3.,4.2,5.4,6.)
    frame=next(i for i,end in enumerate(boundaries) if phase<end)
    sink=(0.,-.5,2.,0.,-.5,2.)[frame]
    lean=.025
    if getattr(f,'brake_age',0)>0:lean=-.035
    sink+=2*math.sin(math.pi*getattr(f,'landing_age',0)/.18)
    return frame,sink,lean


def hero_frames(f,aim):
    airborne=f.y<f.floor-1
    if f.duck or f.sliding:return 5,5
    if airborne:return 4,4
    upper=0
    lower=(1,2,3,2)[int(f.run_phase)%4] if f.moving else upper
    return lower,upper


def pose_rect(f,index):
    _,_,sw,sh=FRAMES[index]
    w,h=sw*SCALE,sh*SCALE*(.75 if f.sliding else 1)
    if f.y>=f.floor-1 and not f.moving:
        h*=1-.04*math.sin(math.pi*getattr(f,'landing_age',0)/.18)
    anchor=ANCHORS[index]
    left=f.x-anchor if f.facing>0 else f.x-(w-anchor)
    top=f.y-h
    if index==0 and f.moving and not f.duck and not f.sliding and f.y>=f.floor-1:
        left+=getattr(f,'run_direction',f.facing)*1.5
        top+=run_motion(f)[1]
    return left,top,w,h


def carry_frame(f,aim=None):
    """Dedicated tucked-rifle run poses; firing switches immediately to the rig."""
    if (not f.moving or f.duck or f.sliding or f.y<f.floor-1
            or aim is not None or getattr(f,'shoot_held',False)
            or getattr(f,'muzzle',0) or getattr(f,'laser',False)):
        return None
    return 1 if getattr(f,'brake_age',0)>0 else (3,3,2,0,0,2)[run_motion(f)[0]]


def weapon_pose(f,aim=None):
    """Shoulder pivot and barrel angle shared by drawing and projectile physics."""
    _,upper=hero_frames(f,aim)
    left,top,w,h=pose_rect(f,upper)
    sx,sy=SHOULDERS[upper]
    sw,sh=FRAMES[upper][2:]
    offset=sx*w/sw
    pivot=(left+(offset if f.facing>0 else w-offset),top+sy*h/sh)
    angle=math.atan2(aim[1]-pivot[1],aim[0]-pivot[0]) if aim else (0 if f.facing>0 else math.pi)
    return pivot[0],pivot[1],angle


BARREL_LENGTH=1310*.035


def muzzle_position(f,aim=None):
    x,y,angle=weapon_pose(f,aim)
    return x+math.cos(angle)*BARREL_LENGTH,y+math.sin(angle)*BARREL_LENGTH

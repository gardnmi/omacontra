"""Shared placement and physical muzzle for the integrated EVA laser sprite."""
SPACE_SCALE=.06
SPACE_ANCHOR=(518,760)
SPACE_MUZZLE=(736,147)

def laser_muzzle(x,y,rotation=0):
    import math
    dx=(SPACE_MUZZLE[0]-SPACE_ANCHOR[0])*SPACE_SCALE
    dy=(SPACE_MUZZLE[1]-SPACE_ANCHOR[1])*SPACE_SCALE
    co,si=math.cos(rotation),math.sin(rotation)
    return x+dx*co-dy*si,y+dx*si+dy*co

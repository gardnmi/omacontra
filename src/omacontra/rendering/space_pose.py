"""Shared placement and physical muzzle for the integrated EVA laser sprite."""
SPACE_SCALE=.06
SPACE_ANCHOR=(518,760)
SPACE_MUZZLE=(736,147)

def laser_muzzle(x,y):
    return (x+(SPACE_MUZZLE[0]-SPACE_ANCHOR[0])*SPACE_SCALE,
            y+(SPACE_MUZZLE[1]-SPACE_ANCHOR[1])*SPACE_SCALE)

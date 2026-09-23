"""Runtime chroma-key atlas decoding and nearest-neighbor sprite drawing."""
from omacontra.resources import ASSETS
from functools import lru_cache
import cairo
import math
from omacontra.rendering.character_assets import CHARACTER_ASSETS, ALPHA_MATTES


@lru_cache(maxsize=16)
def atlas(name):
    source=cairo.ImageSurface.create_from_png(str(ASSETS/CHARACTER_ASSETS.get(name,name)))
    if name in {'dhh-run-carry-v3.png','dhh-run-legs.png','wyrm-storm-ordnance.png','dhh-weapon-v2.png'}:return source
    if name in {'wyrm-head.png','wyrm-mist-arena.png','wyrm-stone-platform.png','reaper-energy-wave.png','shuttle-launch-gantry.png','finale-last-dive-cinema.png','dhh-space-laser.png','shuttle-boarding-hatch.png','foundry-throat-weapon.png','tidebreaker-guardians-enraged.png','guardian-meteor.png','dhh-modular-body.png','guardian-relay-plasma.png','highway-heart-robot-v1.png','industrial-props-v1.png','combat-effects-v1.png','hostile-projectiles-v1.png','furnace-streams-v1.png'}:
        return source  # True alpha; violet projectiles must never be chroma-keyed.
    if name in ALPHA_MATTES:
        # Identity edits retain the original sprite silhouette. Reuse its alpha
        # matte so generated ambient halos cannot leak into live scenery.
        matte=cairo.ImageSurface.create_from_png(str(ASSETS/ALPHA_MATTES[name]))
        clipped=cairo.ImageSurface(cairo.FORMAT_ARGB32,source.get_width(),source.get_height())
        context=cairo.Context(clipped);context.set_source_surface(source)
        context.mask_surface(matte,0,0);source=clipped
    if name in {'finale-people-canonical.png','foundry-rescue-empty.png','finale-plasma-burst.png','omarchy-wordmark.png','finale-vortex.png','finale-coastal-highway.png','finale-car-rear.png','finale-earth.png','dhh-portal-reach.png','dhh-space-walk.png','finale-guardian.png','finale-homecoming.png','finale-atlas.png','foundry-rescue.png','tidebreaker-guardians.png','tidebreaker-worlds.png','tidebreaker-arena.png','tidebreaker-natural-waves.png','journey-cinema.png'}:return source
    if name in {'quattro-car.png','quattro-enemies.png','quattro-munitions.png','quattro-guardrail.png','quattro-bazooka.png','quattro-rally-cinema.png','quattro-explosion.png'}:return source
    # Decode the sheet into ARGB. Magenta is the atlas's reserved transparency key.
    surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,source.get_width(),source.get_height())
    c=cairo.Context(surface);c.set_source_surface(source);c.paint();surface.flush()
    data=surface.get_data().cast('B')
    for i in range(0,len(data),4):
        b,g,r=data[i:i+3]
        if r>40 and b>40 and min(r,b)>g*1.5+20:data[i:i+4]=b'\0\0\0\0'
    surface.mark_dirty()
    return surface

# Explicit frame bounds keep transparent padding out of animation alignment.
from omacontra.rendering.hero_pose import FRAMES as HERO
BOSS=((10,20,492,570),(503,0,468,590),(973,155,550,439))
EYE=(16,615,404,390)
RAVENS=((452,679,177,216),(633,700,185,201),(818,743,164,182))
BLADE=(1024,714,143,201)
IMPACT=(1193,728,151,181)
SKULL=(1355,758,157,142)

def draw(c,sheet,frame,x,y,w,h,flip=False,alpha=1):
    sx,sy,sw,sh=frame
    # Zero-size animation endpoints must not poison the caller's Cairo context.
    if not all(math.isfinite(v) for v in (x,y,w,h,sx,sy,sw,sh,alpha)):return
    if min(w,h,sw,sh)<=0 or alpha<=0:return
    c.save();c.translate(x,y)
    if flip:c.translate(w,0);c.scale(-1,1)
    c.rectangle(0,0,w,h);c.clip();c.scale(w/sw,h/sh)
    c.set_source_surface(atlas(sheet),-sx,-sy);c.get_source().set_filter(cairo.FILTER_NEAREST)
    c.paint_with_alpha(alpha);c.restore()

def paint_background(c,image,x,y,w,h):
    c.save();c.rectangle(x,y,w,h);c.clip();c.translate(x,y)
    c.scale(w/image.get_width(),h/image.get_height());c.set_source_surface(image);c.get_source().set_filter(cairo.FILTER_NEAREST);c.paint();c.restore()

"""Short Contra-style life loss and a protected return to the arena."""
DURATION=.55
PROTECTION=3.

def begin(f):
    f.hit_age=0.;f.hit_origin=(f.x,f.y);f.hit_facing=f.facing
    f.invuln=DURATION+PROTECTION
    f.muzzle=0.;f.slide_time=0.;f.dash_time=0.;f.vy=0.
    f.moving=False

def tick(f,dt):
    if getattr(f,'hit_age',None) is None:return False
    f.hit_age+=dt
    if f.hit_age<DURATION:return True
    f.hit_age=None
    if f.hp<=0:return True
    f.x,f.y=getattr(f,'respawn_anchor',f.hit_origin)
    if hasattr(f,'platforms') and getattr(f,'lava_age',None) is not None:
        # The permanent lava makes a road-level respawn unsafe.
        platform=min(f.platforms,key=lambda p:abs((p[0]+p[1])/2-f.x))
        f.support=platform;f.x=(platform[0]+platform[1])/2;f.y=platform[2]
    else:
        if hasattr(f,'support'):f.support=None
        f.y=f.floor
    f.vy=0.;f.jumps_used=0;f.dash_used=False;f.slide_cooldown=0.;f.slide_buffer=0.
    f.was_jump=False;f.was_slide=False;f.duck=False
    f.invuln=PROTECTION
    return True

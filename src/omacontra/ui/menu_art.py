"""Cached game artwork and lightweight animated arcade menu chrome."""
from functools import lru_cache
import math
import time
import cairo
from omacontra.resources import ASSETS
from omacontra.rendering.health_medals import medal

CREAM=(.89,.88,.76);GREEN=(.68,.85,.52);MUTED=(.48,.57,.51);AMBER=(.92,.57,.29)
NAMES=('THE REAPER','QUATTRO RUN','TIDEBREAKER','THE MIST GATE','BLACK MOON')
ART=('reaper-arena.png','quattro-coast.png','tidebreaker-arena.png','wyrm-mist-arena.png','finale-earth.png')
DESCRIPTIONS=('A haunted wallpaper. A very real fight.','Tobi drives. DHH handles the firepower.','Ride out the storm. Face the guardians.','Circle the dragon. Claim its weapon.','Stay tethered. Finish what you started.')
TITLES={'mode':'CHOOSE YOUR RUN','pause':'TAKE A BREATHER','options':'TUNE THE MIX','controls':'KNOW YOUR MOVES','results':'MISSION COMPLETE','bosses':'CHOOSE YOUR BATTLE','credits':'BEHIND THE GAME','confirm':'ONE MORE THING'}

def text(c,x,y,value,size=20,color=CREAM,width=None):
    c.select_font_face('monospace',cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(size)
    if width:
        actual=c.text_extents(str(value)).width
        if actual>width:c.set_font_size(size*width/actual)
    c.set_source_rgb(*color);c.move_to(x,y);c.show_text(str(value))

def box(c,x,y,w,h,color):
    c.set_source_rgba(*color);c.rectangle(x,y,w,h);c.fill()

@lru_cache(maxsize=8)
def artwork(name,w,h):
    src=cairo.ImageSurface.create_from_png(str(ASSETS/name))
    out=cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h);c=cairo.Context(out)
    scale=max(w/src.get_width(),h/src.get_height())
    c.translate((w-src.get_width()*scale)/2,(h-src.get_height()*scale)/2)
    c.scale(scale,scale);c.set_source_surface(src);c.get_source().set_filter(cairo.FILTER_NEAREST);c.paint()
    return out

def image(c,name,x,y,w,h):
    c.set_source_surface(artwork(name,int(w),int(h)),x,y);c.paint()

def frame(c,x,y,w,h):
    box(c,x,y,w,h,(.04,.065,.062,1))
    c.set_source_rgb(.25,.34,.29);c.set_line_width(1);c.rectangle(x+.5,y+.5,w-1,h-1);c.stroke()
    for xx,yy in ((x,y),(x+w-16,y),(x,y+h-3),(x+w-16,y+h-3)):
        box(c,xx,yy,16,3,(*GREEN,.75))

def row_boxes(f):
    if f.page=='results':x,y,w,h,gap=80,342,450,44,9
    elif f.page in ('controls','credits'):x,y,w,h,gap=80,581,250,42,9
    elif f.page=='confirm':x,y,w,h,gap=80,300,450,52,12
    elif f.page=='options':x,y,w,h,gap=80,228,510,70,20
    else:x,y,w,h,gap=80,211,480,45,9
    return [(x,y+i*(h+gap),w,h) for i in range(len(f.rows()))]

def draw_rows(c,f,t):
    for i,(row,bounds) in enumerate(zip(f.rows(),row_boxes(f))):
        x,y,w,h=bounds;selected=i==f.selection
        if selected:
            box(c,x,y,w,h,(.15,.23,.16,1))
            box(c,x,y,4,h,(*GREEN,1))
            box(c,x+5,y,w-5,1,(*GREEN,.25))
            offset=2*math.sin(t*4)
            c.set_source_rgb(*GREEN);c.move_to(x+18+offset,y+h/2-5);c.line_to(x+25+offset,y+h/2);c.line_to(x+18+offset,y+h/2+5);c.fill()
        else:box(c,x,y,w,h,(.06,.085,.077,.8))
        if f.page=='options' and i<2:
            name=('music','effects')[i];value=f.profile.settings[name]
            text(c,x+38,y+24,name.upper(),17,GREEN if selected else CREAM)
            text(c,x+w-75,y+24,f'{value}%',17)
            for n in range(30):
                box(c,x+38+n*13,y+43,9,9,(*(GREEN if n<value/5 else (.18,.23,.20)),1))
            box(c,x+38+20*13-3,y+40,2,15,(*AMBER,1))
        else:text(c,x+38,y+h/2+7,row.upper(),20,GREEN if selected else CREAM,width=w-58)

def stage_panel(c,level,x=644,y=211,w=556,h=270):
    frame(c,x-2,y-2,w+4,h+4);image(c,ART[level-1],x,y,w,h)
    gradient=cairo.LinearGradient(0,y+h-100,0,y+h)
    gradient.add_color_stop_rgba(0,0,0,0,0);gradient.add_color_stop_rgba(1,.015,.025,.022,.97)
    c.set_source(gradient);c.rectangle(x,y,w,h);c.fill()
    text(c,x+22,y+h-48,f'STAGE {level:02d}',13,GREEN)
    text(c,x+22,y+h-20,NAMES[level-1],26,width=w-44)

def draw(c,f):
    t=time.monotonic()-f.opened_at
    # Fully opaque backing avoids the old PAUSED/ending labels showing through.
    box(c,0,0,1280,720,(.017,.027,.026,1))
    image(c,ART[max(0,min(4,f.app.level-1))],0,0,1280,720)
    box(c,0,0,1280,720,(.015,.025,.023,.93))
    frame(c,48,38,1184,638)
    box(c,50,40,1180,634,(.025,.042,.036,.97))
    # Small moving indicator, not a screen-wide shader or particle system.
    box(c,80,70,22,5,(*GREEN,.65+.25*math.sin(t*2)))
    text(c,116,80,'OMACONTRA',16,GREEN)
    text(c,950,80,'MISSION DEBRIEF' if f.page=='results' else 'FIELD TERMINAL',13,MUTED)
    text(c,80,139,TITLES[f.page],34,width=1090)
    box(c,80,161,1120,1,(.24,.33,.27,1))
    if f.page=='results':results(c,f)
    elif f.page in ('pause','bosses'):
        level=f.selection+1 if f.page=='bosses' and f.selection<5 else f.app.level
        stage_panel(c,level)
        text(c,644,519,DESCRIPTIONS[level-1],17,width=550)
        mode='HARDCORE / NO CONTINUES' if f.record.hardcore else 'STANDARD / CONTINUES ENABLED'
        text(c,644,556,'PRACTICE / SEPARATE RECORDS' if f.page=='bosses' else mode,14,GREEN)
        text(c,644,583,'Your run is paused.' if f.page=='pause' else 'Jump straight into an encounter.',15,MUTED)
    elif f.page=='mode':
        image(c,'omacontra-cover-v2.png',896,195,285,380)
        hardcore=f.selection==1
        color=AMBER if hardcore else GREEN
        text(c,80,430,'ONE RUN. NO SECOND CHANCES.' if hardcore else 'GET BACK IN THE FIGHT.',22,color,width=755)
        lines=(['No continues. No encounter restarts.','Unlimited lives are disabled.','Your best time gets its own record.'] if hardcore else ['A 10-second countdown gives you another shot.','Lives carry forward between stages.','Clear a stage to earn an extra ribbon.'])
        for i,line in enumerate(lines):text(c,80,474+i*34,line,17,MUTED,width=755)
    elif f.page=='options':
        text(c,654,248,'LET THE SOUNDTRACK LEAD.',23,GREEN,width=520)
        for i,line in enumerate(('MUSIC','The full soundtrack and final-level theme.','','EFFECTS','Combat, movement and menu feedback.')):
            text(c,654,298+i*36,line,16,CREAM if i in (0,3) else MUTED,width=530)
        text(c,654,540,'Amber mark = original mix level.',14,AMBER)
        text(c,80,568,'LEFT / RIGHT: 5%    CLICK METER: SET VOLUME',13,MUTED)
    elif f.page=='controls':controls(c)
    elif f.page=='credits':credits(c,f)
    elif f.page=='confirm':
        descriptions={'quit':('LEAVE THE GAME?','Your current run will end.'),'restart':('RESTART THIS ENCOUNTER?','This restart is recorded in your run.'),'title':('RETURN TO THE TITLE?','Your current run will end.')}
        heading,body=descriptions.get(f.pending,('LEAVE THIS RUN?','Your current run will end.'))
        text(c,80,218,heading,24,AMBER);text(c,80,255,body,18,MUTED)
        stage_panel(c,f.app.level,644,300,556,240)
    draw_rows(c,f,t)
    box(c,80,642,1120,1,(.20,.29,.23,1))
    text(c,80,662,'ARROWS / SELECT     ENTER / CONFIRM     MOUSE / POINT + CLICK',12,MUTED)
    text(c,1040,662,'ESC / BACK' if f.page!='results' else 'RUN COMPLETE',12,GREEN)
    if f.profile.error:text(c,80,632,f.profile.error,13,AMBER)

def results(c,f):
    from omacontra.ui.release_ui import time_text
    r=f.record
    text(c,80,194,f'{r.category.upper()} RUN',14,GREEN)
    values=[('CLEAR TIME',time_text(r.elapsed)),('LIVES LOST',str(r.losses)),('CONTINUES',str(r.continues)),('NO-HIT STAGES',f'{r.clean}/5')]
    for i,(heading,value) in enumerate(values):
        x=80+i*284;frame(c,x,211,264,94)
        text(c,x+16,235,heading,12,MUTED);text(c,x+16,280,value,32,GREEN if i==0 else CREAM)
    best=f.profile.best.get(r.category)
    text(c,644,332,'PERSONAL BEST  '+time_text(best) if best else 'PRACTICE RUN / NO RECORD',15,GREEN)
    for i,name in enumerate(NAMES):
        y=351+i*51;box(c,644,y,556,45,(.055,.08,.067,1))
        cleared=i+1 in r.cleared
        if cleared:
            c.save();c.translate(657,y+2);c.scale(.43,.43);c.set_source_surface(medal(True));c.paint();c.restore()
        text(c,690,y+20,f'{i+1:02d}  {name}',15,CREAM if cleared else MUTED)
        text(c,690,y+36,'NO HIT' if cleared and not r.hits.get(i+1,0) else 'CLEARED' if cleared else 'NOT CLEARED',10,GREEN if cleared else MUTED)
    text(c,644,628,f'ENCOUNTER RESTARTS  {r.restarts}',12,MUTED)

def controls(c):
    entries=[('A / D','Move','SPACE / K','Jump / double jump'),('J / Z','Fire','MOUSE','Aim + left click to fire'),('S / DOWN','Crouch','SHIFT','Slide / air dash'),('QUATTRO','Space jumps','SHIFT','Boost the car'),('SPACE STAGE','W / A / S / D move','SHIFT','Thruster burst'),('ESC / P','Pause','R','Request encounter restart')]
    for i,row in enumerate(entries):
        for j in range(2):
            x=80+j*570;y=203+i*58
            box(c,x,y,154,37,(.12,.18,.135,1));text(c,x+12,y+24,row[j*2],14,GREEN,width=132)
            text(c,x+169,y+24,row[j*2+1],15,width=368)

def credits(c,f):
    pages=[('THE PEOPLE & THE PIXELS',['Created by gardnmi','DHH and Tobi: fictional action-adventure portrayals','Pixel artwork: AI-assisted original game assets','Visual direction: Omarchy wallpaper worlds','Movement inspiration: Contra','Gun-effect inspiration: Blazing Chrome']),('THE SOUNDTRACK',['Off Duty Mercenary / user-provided track','Omarchy Oligarchy (Synthwave Mix) / YZL81','Contra / user-provided track','The Descent / user-provided track','Omacontra Opening Theme / user-provided track','Sources: Omarchy Radio and supplied recordings']),('SOUND & TOOLS',['Kenney / Sci-Fi Sounds (CC0)','Free Firearm Sound Library (CC0)','Ben Jaszczak, Brian Nelson, Kevin Heras, Matthew Nanney','Ocean Splash / Thimras (CC0)','Short Water Splashes / ezwa, qubodup (CC0)','Original menu tones / Omacontra','Screensaver: Omarchy / terminal text effects','Source notes: assets/audio/sources/README.md'])]
    heading,lines=pages[f.credits_page]
    text(c,80,207,heading,19,GREEN)
    for i,line in enumerate(lines):text(c,80,247+i*37,line,17,width=1090)
    text(c,80,563,f'LEFT / RIGHT OR SPACE: PAGE {f.credits_page+1} OF 3',13,MUTED)
    for i in range(3):box(c,1080+i*36,551,24,5,(*(GREEN if i==f.credits_page else MUTED),1))

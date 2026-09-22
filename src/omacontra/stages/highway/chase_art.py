"""Pixel-art highway rendering, layered over the shared fullscreen host."""
import math
from omacontra.rendering import finish_fx
import cairo
from omacontra.rendering import sprites
from omacontra.rendering import combat_fx as fx
from omacontra.rendering import player_gun_fx as gun_fx
from omacontra.rendering.health_medals import draw_health
from omacontra.stages.highway import chase_robot_art as robot_art
from omacontra.stages.highway.chase_environment import CoastEnvironment
from omacontra.stages.reaper.battle_art import label, rect, line, glow, color

CAR=(45,240,1450,650)
TRUCK=(10,45,1510,650)
DRONE=(430,705,685,280)
ROLLER=(80,20,1060,780)
ROCKET=(35,810,1180,420)

def spinning_wheel(c,sheet,cx,cy,rx,ry,x,y,screen_rx,screen_ry,angle,alpha=1):
    """Spin only the spoke band; keep the tire, rim and axle cap stationary."""
    c.save();c.translate(x,y);c.scale(screen_rx,screen_ry)
    c.new_path();c.arc(0,0,1,0,math.tau);c.new_sub_path();c.arc(0,0,.32,0,math.tau)
    c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD);c.clip()
    c.rotate(angle)
    sprites.draw(c,sheet,(cx-rx,cy-ry,rx*2,ry*2),-1,-1,2,2,alpha=alpha)
    # A short angular exposure softens the spoke motion at highway speed.
    c.rotate(.14)
    sprites.draw(c,sheet,(cx-rx,cy-ry,rx*2,ry*2),-1,-1,2,2,alpha=.22*alpha)
    c.restore()
    # Asymmetric spokes and traveling tread marks remain visible at game scale.
    c.save();c.translate(x,y);c.scale(screen_rx,screen_ry);c.rotate(angle)
    for i in range(5):
        a=i*math.tau/5
        c.set_source_rgba(.96,.72,.42,alpha*(.85 if i==0 else .45));c.set_line_width(.12 if i==0 else .07)
        c.move_to(math.cos(a)*.38,math.sin(a)*.38);c.line_to(math.cos(a)*.94,math.sin(a)*.94);c.stroke()
    for i in range(7):
        a=i*math.tau/7
        c.set_source_rgba(.04,.035,.05,alpha*.8);c.set_line_width(.15)
        c.arc(0,0,1.8,a,a+.16);c.stroke()
    c.restore()

class ChaseRenderer:
    def __init__(self):
        robot_art.warm_shells()
        self.road=cairo.ImageSurface.create_from_png(str(sprites.ASSETS/'quattro-coast.png'))
        self.environment=CoastEnvironment(self.road)
        # Rasterize reflected strips offscreen. Passing hundreds of translated
        # repeating patterns to GTK's recording/backend surface can exhaust it.
        self.sky=cairo.ImageSurface(cairo.FORMAT_RGB24,1280,200)
        sky=cairo.Context(self.sky);sky.scale(1280/(self.road.get_width()*.7),200/(self.road.get_height()*.22))
        sky.set_source_surface(self.road,-self.road.get_width()*.3,0);sky.paint()
        self.sky_pattern=cairo.SurfacePattern(self.sky);self.sky_pattern.set_extend(cairo.EXTEND_REFLECT)
        self.sky_pattern.set_matrix(cairo.Matrix(yy=-1))
        # Flatten the reflected sky once. Repeating filtered patterns become
        # expensive when the ramp camera fills a fullscreen GTK surface with it.
        self.extended_sky=cairo.ImageSurface(cairo.FORMAT_RGB24,1280,700)
        sky=cairo.Context(self.extended_sky);sky.translate(0,700)
        sky.set_source(self.sky_pattern);sky.paint()
        self.foreground=cairo.ImageSurface(cairo.FORMAT_RGB24,1280,230)
        self.foreground_context=cairo.Context(self.foreground)
        self.foreground_pattern=cairo.SurfacePattern(self.road)
        self.foreground_pattern.set_extend(cairo.EXTEND_REFLECT)
        self.foreground_pattern.set_filter(cairo.FILTER_NEAREST)
    def scenery(self,c,distance):
        sprites.paint_background(c,self.road,0,0,1280,720)
        # Reflect the texture at its edges so the shoulder loops without a cut.
        # Perspective increases asphalt speed toward the camera; the shrubs and
        # rocks then travel as one rigid foreground layer, without being sheared.
        _,visible_top,_,visible_bottom=c.clip_extents()
        if visible_bottom<=490:return
        pattern=self.foreground_pattern;buffer=self.foreground_context
        sx=self.road.get_width()/1280;sy=self.road.get_height()/720
        for y in range(max(490,int(visible_top)//2*2),min(720,int(visible_bottom)+2),2):
            depth=min(1.,(y-490)/116)
            speed=1.65*depth*depth*(3-2*depth)
            shift=(distance*speed)%2560
            pattern.set_matrix(cairo.Matrix(xx=sx,yy=sy,x0=-shift*sx,y0=490*sy))
            buffer.set_source(pattern);buffer.rectangle(0,y-490,1280,2);buffer.fill()
        c.save();c.rectangle(0,490,1280,230);c.clip()
        c.set_source_surface(self.foreground,0,490);c.paint();c.restore()

    def draw(self,c,f,paused=False,hud=True):
        # Extend the sky above the source wallpaper while the camera follows
        # the ramp jump. All actors/projectiles use the same world transform.
        color(c,'ink');c.paint()
        c.set_source_rgb(.20,.045,.28);c.rectangle(0,0,1280,720);c.fill()
        c.save();c.translate(0,f.camera_y)
        if f.camera_y>0:
            c.save();c.rectangle(0,-700,1280,700);c.clip()
            c.set_source_surface(self.extended_sky,0,-700);c.get_source().set_filter(cairo.FILTER_NEAREST);c.paint();c.restore()
        self.scenery(c,f.distance)
        self.environment.draw(c,f)
        shift=f.distance%224
        for i in range(-1,7):
            sprites.draw(c,'quattro-guardrail.png',(495,255,592,225),
                         i*224+shift,438,224,60)
        for i in range(8):
            x=(i*220+f.distance)%1760-220
            line(c,[(x,555),(x+90,555)],'cream',4,.28)
        for i in range(160):
            y=501+(i*43)%139
            speed=.85+(y-501)/139*.65
            x=(i*173.17+f.distance*speed)%1360-40
            length=2+(i%5)*2+(10 if f.boost>0 else 0)
            line(c,[(x,y),(x+length,y)],'cream' if i%3 else 'smoke',1,.09)
        if f.ramp_x is not None:
            x=f.ramp_x
            fx.ramp(c,x,robot_art.RAMP_WIDTH,robot_art.RAMP_HEIGHT) if f.encounter_phase==2 else fx.ramp(c,x)
        for x in f.obstacles:
            fx.barricade(c,x)
        if f.boss_active and f.state!='won':self.truck(c,f)
        for d in f.drones:
            c.save();c.translate(d['x'],d['y']);c.rotate(math.sin(d['age']*3)*.07)
            sprites.draw(c,'quattro-enemies.png',DRONE,-55,-23,110,45)
            glow(c,0,0,18,'gold',.3);c.restore()
            if d.get('lock') is not None:
                tx,ty=d['lock']
                c.set_source_rgba(.25,.85,1.,.25);c.set_line_width(1)
                c.move_to(d['x'],d['y']);c.line_to(tx,ty);c.stroke()
                c.set_source_rgba(.4,.95,1.,.9);c.arc(d['x'],d['y'],7,0,math.tau);c.fill()
            line(c,[(d['x']-22,d['y']-32),(d['x']-22+44*d['hp']/4,d['y']-32)],'red',2)
        # Tire dust lies behind the car, never obscuring the gunner.
        if f.jump_height<5:
            for i in range(9):
                age=(f.clock*2+i*.11)%1;x=f.x+100+age*150;y=580-age*18
                fx.smoke(c,x,y,18+age*38,f.clock+i,alpha=(1-age)*.16)
        if f.warning=='mortar' or any(b.kind=='truck_mortar' for b in f.shots):
            for x in f.mortar_targets:
                line(c,[(x-170,586),(x+170,586)],'red',5,.65)
                label(c,x-35,618,'IMPACT',12,'gold')
        for x,age in f.road_blasts:
            frame=min(5,int(age/.1))
            sprites.draw(c,'quattro-explosion.png',((frame%3)*512,(frame//3)*512,512,512),
                         x-120,350,240,240,alpha=max(0,1-age/.6))
        self.car(c,f)
        for b in f.shots:
            if b.kind=='tire_roller':
                sprites.draw(c,'quattro-munitions.png',ROLLER,b.x-42,b.y-31,84,62)
                # Motor housing stays upright while its grinding hub turns.
                c.save();c.translate(b.x+1,b.y+2);c.scale(10.7,15.9)
                c.arc(0,0,1,0,math.tau);c.clip();c.rotate(-b.x/22)
                sprites.draw(c,'quattro-munitions.png',(485,235,270,400),-1,-1,2,2);c.restore()
                for i in range(3):
                    x=b.x+18+i*10;y=589-(i*7+int(f.clock*70))%16
                    line(c,[(x,y),(x+9,y-5)],'gold',2,.7)
            elif b.kind=='robot_shell':
                robot_art.shell(c,b,f.clock)
            elif b.kind in ('truck_rocket','finisher_rocket','truck_mortar'):
                a=math.atan2(b.vy,b.vx)
                c.save();c.translate(b.x,b.y);c.rotate(a-math.pi)
                sprites.draw(c,'quattro-munitions.png',ROCKET,-25,-10,50,20)
                fx.flame(c,23,0,12,26,f.clock,math.pi/2);c.restore()
            elif b.kind=='drone_laser':
                a=math.atan2(b.vy,b.vx);dx,dy=math.cos(a),math.sin(a)
                c.set_source_rgba(.15,.7,1.,.3);c.set_line_width(10)
                c.move_to(b.x-dx*32,b.y-dy*32);c.line_to(b.x,b.y);c.stroke()
                c.set_source_rgb(.55,.95,1.);c.set_line_width(3)
                c.move_to(b.x-dx*28,b.y-dy*28);c.line_to(b.x,b.y);c.stroke()
            else:
                gun_fx.bullet(c,b.x,b.y,b.vx,b.vy)
        for p in f.particles:
            if p.color=='smoke':fx.smoke(c,p.x,p.y,p.size*3,f.clock,alpha=min(.35,p.life))
            else:
                color(c,p.color,min(1,p.life*3));c.rectangle(p.x,p.y,p.size,p.size);c.fill()
        c.restore()
        if hud:self.hud(c,f,paused)
    def car_wreck(self,c,f):
        t=f.wreck_age;x,y=getattr(f,'wreck_origin',(f.x,f.y))
        # No intact car, occupants or firing pose survive the final impact.
        for delay,dx,dy,size in ((0,-45,-40,190),(.1,60,-55,210),(.24,0,-65,230)):
            robot_art.blast(c,x+dx,y+dy,t-delay,size)
        for i in range(9):
            age=max(0,t-.04*i)
            px=x+(i-4)*24*min(age,1.2)
            py=min(588,y-35-(90+i%3*55)*age+280*age*age)
            c.save();c.translate(px,py);c.rotate(min(age,1.2)*(i%3-1)*5)
            # Lower bodywork only: never cut fragments from either occupant.
            sprites.draw(c,'quattro-car.png',(70+i*140,635,120,110),-16,-12,32,24,
                         alpha=max(.3,1-age*.5));c.restore()
        for i in range(3):
            if t>.18:
                age=t-.18
                fx.smoke(c,x+(i-1)*44,y-50-min(age,2)*45,65+min(age,1.5)*55,
                         f.clock+i,alpha=.45)
        if t>.35:
            for dx in (-40,35):fx.flame(c,x+dx,min(590,y),20,45,f.clock+dx)

    def car(self,c,f):
        if f.state=='dead':self.car_wreck(c,f);return
        finish_fx.tire_marks(c,f);finish_fx.recovery(c,f,f.x,f.y-12)
        alpha=.5 if f.state=='play' and f.invuln>0 and int(f.clock*15)%2 else 1
        # The small suspension motion carries the gunner and rifle together.
        hit=max(0,1-(f.clock-getattr(f,'hit_clock',-99))/.35)
        bob=math.sin((1-hit)*22)*5*hit
        landing=f.clock-getattr(f,'landed_at',-99)
        compression=6*math.sin(landing*math.pi/.16) if 0<=landing<.16 else -2*math.sin((landing-.16)*math.pi/.18) if .16<=landing<.34 else 0
        c.save();c.translate(0,bob)
        c.translate(f.x,f.y);c.scale(1,1-compression/125);c.translate(-f.x,-f.y)
        tilt=getattr(f,'victory_tilt',.14*f.jump_height/150 if f.state=='dying' else 0)
        tilt+=math.sin((1-hit)*18)*.045*hit
        c.translate(f.x,f.y-60);c.rotate(tilt);c.translate(-f.x,-f.y+60)
        if f.boost:
            glow(c,f.x+145,f.y-32,40,'gold',.5)
            fx.flame(c,f.x+132,f.y-32,20,72,f.clock,math.pi/2)
        sprites.draw(c,'quattro-car.png',CAR,f.x-140,f.y-125,280,125,alpha=alpha)
        for cx,cy,rx,ry in ((856,738,37,68),(1330,733,28,61)):
            sx=f.x-140+(cx-CAR[0])*280/CAR[2]
            sy=f.y-125+(cy-CAR[1])*125/CAR[3]
            spinning_wheel(c,'quattro-car.png',cx,cy,rx,ry,sx,sy,
                           rx*280/CAR[2],ry*125/CAR[3],-f.distance/28,alpha)
        roof=f.roof_progress
        if roof>0:
            lift=93*roof+math.sin(roof*math.pi)*35
            sprites.draw(c,'dhh-body.png',sprites.HERO[0],f.x+27,f.y-114-lift,61,81.8)
            px,py=f.bazooka_pivot;py+=93-lift
            tx,ty=f.aim_target or f.target;a=math.atan2(ty-py,tx-px)
            c.save();c.translate(px,py);c.rotate(a)
            sprites.draw(c,'quattro-bazooka.png',(100,115,1840,495),-30,-9,75,20.2)
            c.restore()
        else:
            # The weapon layer supplies both complete arms. Keep only the
            # head and shirt from the body atlas, following its shirt contour
            # so the old downward-facing arm stubs cannot show underneath.
            c.save()
            outline=((105,48),(225,48),(225,122),(198,128),
                     (201,202),(192,215),(130,215),(126,193),
                     (136,148),(132,124),(105,124))
            for i,(sx,sy) in enumerate(outline):
                x=f.x+30.2+(sx-45)*.26;y=f.y-122+(sy-48)*.26
                if i==0:c.move_to(x,y)
                else:c.line_to(x,y)
            c.close_path();c.clip()
            c.rectangle(f.x+30.2,f.y-126,79.3,44);c.clip()
            sprites.draw(c,'dhh-body.png',sprites.HERO[0],f.x+30.2,f.y-122,79.3,106.34,alpha=alpha)
            c.restore()
            px,py=f.gun_pivot;a=f.gun_angle
            c.save();c.translate(px,py);c.rotate(a)
            if math.cos(a)<0:c.scale(1,-1)
            scale=f.barrel_length/1355
            sprites.draw(c,'dhh-weapon.png',(150,250,1460,380),-100*scale,-125*scale,1460*scale,380*scale,alpha=alpha)
            c.restore()
            if f.muzzle:
                mx,my=f.muzzle_position
                gun_fx.muzzle(c,mx,my,a,f.muzzle,getattr(f,'machine_shots',0),size=29,alpha=alpha)
        c.restore()
    def truck(self,c,f):
        if f.state=='transform':robot_art.transform(c,f);return
        if f.encounter_phase==2:
            if f.state=='dying':robot_art.destruction(c,f)
            else:robot_art.robot(c,f)
            return
        if f.state=='dying':self.truck_death(c,f);return
        dying=False;age=f.death_age
        alpha=max(0,1-age/3.5) if dying else 1
        shake=math.sin(age*55)*age*4 if dying else math.sin(f.distance*.1)*1.5
        if f.trailer_x is not None or f.trailer_done:
            sprites.draw(c,'quattro-enemies.png',(10,45,800,650),f.boss_x,365+shake,272,221,alpha=alpha)
        else:sprites.draw(c,'quattro-enemies.png',TRUCK,f.boss_x,365+shake,513,221,alpha=alpha)
        for cx,cy in (((546,580),) if f.trailer_x is not None or f.trailer_done else ((546,580),(1120,580),(1377,580))):
            sx=f.boss_x+(cx-TRUCK[0])*513/TRUCK[2]
            sy=365+shake+(cy-TRUCK[1])*221/TRUCK[3]
            spinning_wheel(c,'quattro-enemies.png',cx,cy,40,42,sx,sy,
                           40*513/TRUCK[2],42*221/TRUCK[3],-f.distance/43,alpha)
        if not dying:
            for index,hp in enumerate(f.parts):
                if hp<=0:continue
                tx,ty=f.component_target(index)
                vulnerable=index<2 or f.core_vulnerable
                tone='gold' if vulnerable else 'cream'
                glow(c,tx,ty,38,tone,.35 if vulnerable else .12)
                label(c,tx-36,ty-43,('MINES','TURRET','CORE OPEN' if vulnerable else 'ARMORED')[index],10,tone)
                line(c,[(tx-30,ty+38),(tx+30,ty+38)],'ink',4)
                line(c,[(tx-30,ty+38),(tx-30+60*hp/(60,80,160)[index],ty+38)],tone,3)
                if index==2 and not vulnerable:
                    color(c,'cream',.5);c.set_line_width(2);c.arc(tx,ty,34,0,math.tau);c.stroke()
            # Damaged components belch smoke and shed hot debris.
            for i,hp in enumerate(f.parts[:2]):
                if hp<=0:
                    x=f.boss_x+(180 if i==0 else 145);y=555 if i==0 else 390
                    for j in range(4):
                        t=(f.clock*.7+j*.25)%1
                        fx.smoke(c,x+t*40,y-t*75,24+t*45,f.clock+j,alpha=.5*(1-t))
        else:
            for i in range(12):
                t=max(0,age-i*.05);x=f.boss_x+40+i*32+math.sin(i*9)*t*70;y=430-t*120+t*t*95
                c.save();c.translate(x,min(590,y));c.rotate(t*(i%3-1)*3)
                sprites.draw(c,'quattro-enemies.png',(500+i%4*80,350,70,70),-12,-12,24,24,alpha=alpha);c.restore()
    def truck_death(self,c,f):
        t=f.death_age;alpha=min(1,max(0,(1.5-t)/.7))
        # Cab and trailer physically split; their artwork stays at game scale.
        for start,width,sign in (((0,800,-1),) if f.trailer_done else ((0,720,-1),(720,790,1))):
            c.save();c.translate(f.boss_x+start*.34+width*.17,530)
            c.rotate(sign*min(.45,t*.6));c.translate(-width*.17,-165+min(65,t*90))
            sprites.draw(c,'quattro-enemies.png',(10+start,45,width,650),0,0,width*.34,221,alpha=alpha)
            c.restore()
        for i in range(18):
            age=max(0,t-i*.035);x=f.boss_x+150+math.sin(i*8)*age*140
            y=min(603,445-(120+i%4*45)*age+100*age*age)
            c.save();c.translate(x,y);c.rotate(age*(i%5-2)*2)
            frame=(160+i%5*110,340+i%3*70,100,100)
            if i==0:frame=(475,495,170,170)
            size=48 if i==0 else 22+i%3*8
            if i==0:c.arc(0,0,size*.48,0,math.tau)
            else:
                c.move_to(-size*.45,-size*.3);c.line_to(size*.2,-size*.48)
                c.line_to(size*.46,size*.15);c.line_to(-size*.16,size*.46);c.close_path()
            c.clip()
            sprites.draw(c,'quattro-enemies.png',frame,-size/2,-size/2,size,size,alpha=alpha);c.restore()
        # A primary fuel detonation rolls into smoke; smaller secondary
        # blasts follow it, rather than repeating the same impact starburst.
        for delay,offset,size in (((0,180,330),(.12,65,230)) if f.trailer_done else ((0,220,330),(.12,75,230),(.23,360,260))):
            age=t-delay
            if not 0<=age<1.65:continue
            frame=min(5,int(age/.18))
            fade=min(1,max(0,(1.65-age)/.5))
            sprites.draw(c,'quattro-explosion.png',((frame%3)*512,(frame//3)*512,512,512),
                         f.boss_x+offset-size/2,595-size,size,size,alpha=fade)
        if t<.13:
            color(c,'gold',.35*(1-t/.13));c.rectangle(f.boss_x-30,320,580,285);c.fill()

    def hud(self,c,f,paused):
        rect(c,0,0,1280,41,'ink');label(c,15,18,'02 / QUATTRO RUN',12)
        label(c,15,34,'TOBI / DRIVER    DHH / GUNNER',10,'gold')
        label(c,925,18,'IRON HEART' if f.encounter_phase==2 else 'ROADBLOCK',12,'gold')
        if f.boss_active:
            line(c,[(925,30),(1255,30)],'smoke',4);line(c,[(925,30),(925+330*f.boss_hp/f.boss_max,30)],'red',4)
        draw_health(c,f.hp,unlimited=getattr(f,'unlimited_lives',False),damage_age=f.clock-getattr(f,'damage_clock',-99),capacity=f.max_hp)
        label(c,18,92,'BOOST '+('READY' if f.boost_cooldown<=0 else '%.1fs'%f.boost_cooldown),11,'green' if f.boost_cooldown<=0 else 'cream')
        if f.notice_time>0:label(c,345,75,f.notice,15,'cream')
        if f.warning:
            cue={'ram':'RAM INCOMING / SHIFT BOOST','roller':'TIRE SHREDDER / SPACE JUMP','spread':'ROCKET FAN / FIND THE GAP','drones':'DRONES DEPLOYING','mortar':'MORTARS / MOVE OUT OF MARKED ZONES'}[f.warning]
            rect(c,380,110,510,35,'ink');label(c,402,133,cue,16,'gold')
        elif not f.boss_active and 0<f.barrier_warning<1.5:label(c,350,130,'ROADBLOCK AHEAD / SPACE JUMP',17,'gold')
        if f.clock<.6 and f.state=='play':
            label(c,420,240,'QUATTRO RUN',34,'cream');label(c,430,272,'THE WALLPAPER KEEPS MOVING.',12,'cream')
        if f.state=='transform':
            rect(c,320,106,640,42,'ink');label(c,340,133,'THE CARGO WAS ALIVE',19,'gold')
        elif f.core_open>0 and f.encounter_phase==1:
            rect(c,360,106,560,42,'ink');label(c,380,133,'CORE EXPOSED / %.1fs / 4x DAMAGE'%f.core_open,18,'gold')
        elif f.ramp_x is not None and f.ramp_x<f.x:
            rect(c,320,106,640,42,'ink');label(c,340,133,'RAMP AHEAD / STAY LOW TO LAUNCH',18,'gold')
        elif f.clock<7 and f.encounter_phase==1:
            label(c,300,105,'BREAK MINES OR TURRET / RAMPS EXPOSE THE CORE',13,'cream')
        if f.state=='finisher':
            cue={'settle':'HEART BREACHED / GET READY','prompt':'SPACE / JUMP ON THE ROOF','climb':'DHH: MY TURN.','aim':'AIM AT THE HEART / CLICK TO FIRE','flight':'ROCKET AWAY!'}[f.finisher_phase]
            rect(c,325,120,630,60,'ink');label(c,350,149,cue,21,'gold')
            if f.finisher_phase in ('prompt','aim'):
                total=2.5 if f.finisher_phase=='prompt' else 6
                line(c,[(350,166),(350+580*max(0,f.finisher_timer)/total,166)],'gold',4)
            tx,ty=f.target;ty+=f.camera_y;color(c,'cream');c.set_line_width(2);c.arc(tx,ty,35,0,math.tau);c.stroke()
        if paused:label(c,570,330,'PAUSED',25)
        if f.state=='dead' and f.wreck_age>.8:label(c,420,300,'QUATTRO DOWN',24)
        if f.state=='won':label(c,380,300,'YOU CAN FIX ANYTHING.',28);label(c,465,336,'ROADBLOCK DESTROYED / R TO REPLAY',13)
        rect(c,0,695,1280,25,'ink');label(c,18,713,'A/D OR ARROWS MOVE    MOUSE / J FIRE    SPACE JUMP    SHIFT BOOST    P PAUSE    R RESTART    ESC MENU',11)

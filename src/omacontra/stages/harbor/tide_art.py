"""Layered storm, independently animated water attacks, and existing DHH sprites."""
from omacontra.rendering.health_medals import draw_health
import math
import cairo
from omacontra.rendering import sprites
from omacontra.rendering import combat_fx as fx
from omacontra.rendering import player_gun_fx as gun_fx
from omacontra.stages.harbor import tide_cargo_art
from omacontra.stages.harbor.tide_environment import TideEnvironment
from omacontra.stages.harbor.tide_guardian_art import world, guardian, guardian_tells, reveal_overlay, rage_cinema
from omacontra.stages.harbor.tide_guardians import SWITCH_AT
from omacontra.stages.reaper.battle_art import BattleRenderer, label, glow, color

class TideRenderer:
    def __init__(self):
        tide_cargo_art.crate_stamp(0);tide_cargo_art.crate_stamp(1)
        self.hero_renderer=BattleRenderer()
        self.environment=TideEnvironment()
        self.ocean_source=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,630)
        sprites.draw(cairo.Context(self.ocean_source),'tidebreaker-arena.png',(0,0,1536,810),0,0,1280,630)
        # Recolor the existing boss, retaining all original foam and detail.
        # Cache the palette once; phase blending and turbulence are runtime effects.
        self.blood_source=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,630)
        blood=cairo.Context(self.blood_source)
        blood.set_source_surface(self.ocean_source);blood.paint()
        blood.set_operator(cairo.OPERATOR_HSL_COLOR)
        blood.set_source_rgb(.62,.035,.065);blood.paint()
        self.palette_buffer=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,630)
        self.ocean_buffer=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720)
        self.ocean_pattern=cairo.SurfacePattern(self.palette_buffer)
        self.ocean_pattern.set_extend(cairo.EXTEND_REFLECT)
        self.ocean_pattern.set_filter(cairo.FILTER_BILINEAR)

    def ocean(self,c,f):
        # Bounded software sampling across the entire scene avoids GPU pattern
        # allocation growth and the old hard seam down the middle of the wave.
        rage=f.ocean_rage
        palette=cairo.Context(self.palette_buffer)
        palette.set_source_surface(self.ocean_source);palette.paint()
        palette.set_source_surface(self.blood_source)
        # Blood color grows through the boss and lower water, leaving the port
        # sky cold for contrast. No detached foreground wave appears.
        mask=cairo.LinearGradient(250,80,880,500)
        mask.add_color_stop_rgba(0,0,0,0,0)
        mask.add_color_stop_rgba(.65,0,0,0,rage*.85)
        mask.add_color_stop_rgba(1,0,0,0,rage)
        palette.mask(mask)
        dest=cairo.Context(self.ocean_buffer)
        for y in range(0,720,3):
            strength=1.+5*max(0,(y-360)/270)
            dx=math.sin(y*.026+f.clock*(2.1+rage*1.4))*strength*(1+rage*1.8)
            dx+=rage*math.sin(y*.061-f.clock*4.2)*4
            dy=math.sin(f.clock*(1.4+rage))*(2+rage*4)
            # Stretch the lower water continuously to the bottom of the viewport.
            # Keep the boss core fixed, then ease into the extra coverage;
            # never paste a repeated strip across the exposed deck edge.
            source_y=y-100*(max(0,y-350)/370)**2
            self.ocean_pattern.set_matrix(cairo.Matrix(1,0,0,1,dx,source_y-y+dy))
            dest.set_source(self.ocean_pattern);dest.rectangle(0,y,1280,3);dest.fill()
        if c is not None:
            c.set_source_surface(self.ocean_buffer,0,0);c.paint()

    def swell(self,c,x,ground,w,h,pose=0,barrel=False,alpha=1):
        # All water keeps its feet in the sea; the crest changes shape instead
        # of translating a detached object downward.
        pose=max(0,min(2,pose));index=int(pose);mix=pose-index
        for idx,weight in ((index,1-mix),(min(2,index+1),mix)):
            if weight<=0:continue
            frame=(idx*512+12,560 if barrel else 80,500,385 if barrel else 395)
            sprites.draw(c,'tidebreaker-natural-waves.png',frame,x,ground-h,w,h,alpha=alpha*weight)

    def collapse_warning(self,c,f):
        t=max(0,min(1,1-f.tide_timer/1.05))
        travel=min(1,t/.62);travel=travel*travel*(3-2*travel)
        origin=1050 if f.attack_direction<0 else -100
        x=origin+(f.target_x-origin)*travel
        grow=max(0,(t-.35)/.65)
        self.swell(c,x-75,f.deck_y(x)+8,220,70+250*grow,max(0,min(1,(t-.25)/.5)))

    def draw(self,c,f,paused=False,hud=True):
        if f.stage and f.state=='play' and rage_cinema(c,f):return
        c.set_source_rgb(.018,.045,.075);c.paint()
        revealing=f.state=='reveal'
        if revealing:
            t=f.transition_age
            world(c,f.transition_from+1)
            # The old environment collapses downward as a sheet of water or pixels.
            fade=max(0,1-t/2.)
            c.save();c.rectangle(0,0,1280,630);c.clip()
            c.translate(0,t*t*105)
            world(c,f.transition_from,fade)
            c.restore()
            for i in range(130):
                age=max(0,t-i%9*.045)
                xx=(i*89)%1280;yy=(i*47)%570+age*age*220
                c.set_source_rgba(.82,.89,.86,max(0,1-age/1.8)*.7)
                c.rectangle(xx,yy,3+i%4,12+i%17);c.fill()
        else:
            if f.stage==0:self.ocean(c,f)
            else:world(c,1 if all(a.hp>0 for a in f.guardians) else 2)
        self.environment.background(c,f)
        # Rain is continuous and bounded; lightning affects scenery only.
        for i in range(95 if f.stage==0 else 24):
            x=(i*137-f.clock*145)%1320-20;y=(i*73+f.clock*400)%640
            c.set_source_rgba(.56,.76,.86,.17);c.set_line_width(1);c.move_to(x,y);c.line_to(x-9,y+19);c.stroke()
        if f.stage==0 and f.clock%9<.10:
            c.set_source_rgba(.6,.8,1,.13);c.rectangle(0,0,1280,620);c.fill()
        # The steel deck and feet share the exact same world-space floor.
        c.save();c.translate(640,630+f.deck_roll);c.rotate(math.atan(f.deck_slope))
        sprites.draw(c,'tidebreaker-arena.png',(0,810,1536,214),-700,0,1400,178);c.restore()
        self.environment.deck(c,f)
        if f.stage:
            for view in f.guardian_views:
                entrance=max(0,1-(f.transition_age-SWITCH_AT)/1.5)*350 if revealing else 0
                guardian(c,view,entrance=entrance*(-1 if view.stage==2 else 1))
                if f.state=='play' and view.actor.hp>0:guardian_tells(c,view)
        if f.wave_reveal>0:
            # Guardians already stand in the harbor, behind the dying water.
            # Composite only above the deck: no moving scenery, wipe or title.
            self.ocean(None,f)
            c.save();c.move_to(0,0);c.line_to(1280,0)
            c.line_to(1280,f.deck_y(1280));c.line_to(0,f.deck_y(0));c.close_path();c.clip()
            c.set_source_surface(self.ocean_buffer)
            c.paint_with_alpha(min(1,f.wave_reveal/2.4));c.restore()
        if f.state=='play':
            cx,cy=f.core
            if not f.stage and f.vulnerable:
                glow(c,cx,cy,95,'gold',.45);glow(c,cx,cy,32,'cream',.9)
                for i in range(3):
                    c.set_source_rgba(.7,.95,1,.65-i*.15);c.set_line_width(2)
                    c.arc(cx,cy,42+i*9+math.sin(f.clock*5)*3,f.clock+i,f.clock+i+3.2);c.stroke()
            if f.stage:
                for a in f.guardians:
                    if a.hp>0:
                        ax,ay=a.core(f.floor);glow(c,ax,ay,60,'gold',.4)
            if f.core_flash:glow(c,cx,cy,65,'cream',.8)
            if f.tide_warning=='claw':
                self.collapse_warning(c,f)
            elif f.tide_warning:
                charge=1-min(1,max(0,f.tide_timer)/.8) if f.wave_phase<3 else 1-min(1,max(0,f.combo_wait))
                charge=max(.06,charge)
                height=(235 if f.tide_warning=='ceiling' else 150 if f.tide_warning=='breaker' else 78)*charge
                c.save()
                if f.attack_direction>0:c.translate(1280,0);c.scale(-1,1)
                self.swell(c,1240,f.deck_y(1260 if f.attack_direction<0 else 20)+8,220,height,
                           charge,f.tide_warning=='ceiling')
                c.restore()
        for hazard in f.hazards:
            ground=f.deck_y(hazard.x)
            c.save()
            if hazard.direction>0:
                c.translate(hazard.x*2,0);c.scale(-1,1)
            if hazard.kind in ('surge','breaker'):
                height=78 if hazard.kind=='surge' else 150
                # Trailing foam broadens and settles, never floats above the sea.
                self.swell(c,hazard.x+25,ground+8,210,height*.55,2,alpha=.75)
                self.swell(c,hazard.x-40,ground+8,170,height,0 if hazard.age<.2 else 1)
            elif hazard.kind=='ceiling':
                self.swell(c,hazard.x-40,ground+8,250,250,1,True)
            else:
                age=hazard.age
                if age<.18:
                    self.swell(c,hazard.x-75,ground+8,220,320+25*math.sin(age/.18*math.pi),1)
                else:
                    fall=min(1,(age-.18)/.4)
                    height=max(20,320*(1-fall)**2)
                    self.swell(c,hazard.x-75-fall*35,ground+8,220+fall*100,height,1+min(1,fall*3),alpha=min(1,(1.1-age)*3))
                    for i in range(24):
                        t=max(0,age-.18-i%4*.018)
                        xx=hazard.x+math.sin(i*7)*t*240
                        yy=ground-20-(140+i%5*20)*t+420*t*t
                        if yy<ground:
                            color(c,'cream',max(0,1-t*1.6));c.rectangle(xx,yy,3+i%3,3);c.fill()
            c.restore()
        tide_cargo_art.draw(c,f)
        self.hero_renderer.hero(c,f,f.aim_target)
        for shot in f.shots:
            if shot.enemy:
                kind={'heavy_slug':'needle','orbit_bolt':'pearl','pressure_ring':'pressure_ring'}[shot.kind]
                fx.projectile(c,kind,shot.x,shot.y,shot.vx,shot.vy,f.clock)
                continue
            gun_fx.bullet(c,shot.x,shot.y,shot.vx,shot.vy)
        for p in f.particles:
            if p.color=='smoke':fx.smoke(c,p.x,p.y,p.size*3,f.clock,alpha=min(.3,p.life))
            else:
                color(c,p.color,min(1,p.life*3));c.rectangle(p.x,p.y,p.size,p.size);c.fill()
        if revealing:reveal_overlay(c,f)
        elif hud:self.hud(c,f,paused)

    def hud(self,c,f,paused):
        c.set_source_rgba(.01,.025,.04,.86);c.rectangle(0,0,1280,79);c.fill()
        label(c,28,27,'03 / TIDEBREAKER',16)
        draw_health(c,f.hp,28,34,unlimited=getattr(f,'unlimited_lives',False),damage_age=f.clock-getattr(f,'damage_clock',-99),capacity=f.max_hp,scale=.75)
        label(c,380,25,f.stage_name,13)
        c.set_source_rgb(.1,.22,.28);c.rectangle(380,37,650,9);c.fill()
        c.set_source_rgb(.28,.78,.86);c.rectangle(380,37,650*f.boss_hp/f.boss_max,9);c.fill()
        if f.stage:
            for i,a in enumerate(reversed(f.guardians)):
                x=380+i*335
                color(c,'ink');c.rectangle(x,37,315,9);c.fill()
                color(c,'gold');c.rectangle(x,37,315*a.hp/a.maximum,9);c.fill()
                label(c,x,66,'DEAD ORBIT / LEFT' if a.kind==2 else 'BLACK COAT / RIGHT',10)
        label(c,1060,47,f'WAVE {f.wave_phase}/3' if not f.stage else 'DUO BATTLE',12)
        if f.state=='dead' or paused:
            c.set_source_rgba(0,0,0,.7);c.paint()
            label(c,420,345,'PAUSED' if paused else 'LOST AT SEA',32)
            label(c,420,386,'P / RESUME' if paused else 'CONTINUE SCREEN INCOMING',16,'gold')

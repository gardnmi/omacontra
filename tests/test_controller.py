import unittest
from types import SimpleNamespace as NS
from unittest.mock import Mock, patch
from omacontra.controller import Controller
from omacontra.boss_app import BossApp
from omacontra.input_state import KeyboardState
from omacontra.stages.reaper.combat import Fight
from omacontra.ui.story import Intro
from omacontra.ui.release_ui import Profile
from omacontra.linux_controller import LinuxController

class ControllerTests(unittest.TestCase):
    def setUp(self):
        a=self.a=BossApp.__new__(BossApp)
        a.keyboard=KeyboardState();a.keys=a.keyboard.keys
        a.intro=None;a.f=Fight();a.level=1;a.visible=True;a.input_device='keyboard';a.paused=False
        a.slide_requested=False;a.shooting=False;a.continue_screen=None;a.chase_cinema=None
        a.frontend=NS(page=None,blocked=set(),profile=NS(settings={'deadzone':20}),open=Mock(),key=Mock())
        a.unlock_sound=Mock()
        self.c=a.controller=Controller(a)
    def sample(self,buttons=(),axes=(0,0,0,0)):
        self.c.sample(dict(connected=True,buttons=buttons,axes=axes));self.c.tick(.016)
    def test_move_fire_jump_dash_release(self):
        self.sample(['a','rt','lb'],[1,0,0,0])
        self.assertTrue({'right','space','j','shift_l'}<=self.a.keys)
        self.assertTrue(self.a.slide_requested)
        self.sample();self.assertFalse(self.a.keys)
    def test_keyboard_and_two_fire_buttons_do_not_release_each_other(self):
        self.a.input_press(44,'j');self.sample(['rt','x'])
        self.sample(['x']);self.assertIn('j',self.a.keys)
        self.sample();self.assertIn('j',self.a.keys)
        self.a.input_release(44,'j');self.assertNotIn('j',self.a.keys)
    def test_right_stick_aim_relative_to_player_in_all_stages(self):
        from omacontra.stages.highway.chase import Chase
        from omacontra.stages.harbor.tidebreaker import Tidebreaker
        from omacontra.stages.dragon.foundry import Foundry
        from omacontra.stages.space.finale import Finale
        for level,cls in enumerate((Fight,Chase,Tidebreaker,Foundry,Finale),1):
            self.a.f=cls();self.a.f.state='play';self.a.level=level
            self.sample(['rt'],[0,0,1,-1]);x,y=(self.a.f.x,self.a.f.y) if level==5 else self.a.f.player_center
            self.assertAlmostEqual(self.c.aim[0]-x,320/2**.5)
            self.assertAlmostEqual(self.c.aim[1]-y,-320/2**.5)
    def test_deadzone_and_invalid_axes(self):
        self.sample(axes=[.1,-.1,.1,.1]);self.assertFalse(self.a.keys);self.assertIsNone(self.c.aim)
        self.sample(axes=[float('nan'),float('inf'),None,0]);self.assertFalse(self.a.keys)
        self.a.frontend.profile.settings['deadzone']=40
        self.sample(axes=[.3,0,.3,0]);self.assertFalse(self.a.keys);self.assertIsNone(self.c.aim)
    def test_disconnect_releases_and_pauses_once(self):
        self.sample(['rt'],[1,0,0,0]);self.c.sample(None)
        self.assertFalse(self.a.keys);self.a.frontend.open.assert_called_once()
        self.c.sample(None);self.a.frontend.open.assert_called_once()
    def test_focus_requires_neutral_before_repress(self):
        self.sample(['a','rt']);self.c.suspend();self.a.visible=False
        self.sample(['a','rt']);self.a.visible=True
        self.sample(['a','rt']);self.assertFalse(self.a.keys)
        self.sample();self.sample(['a']);self.assertIn('space',self.a.keys)
    def test_held_menu_confirm_does_not_become_jump(self):
        self.a.frontend.page='pause'
        def confirm(key):self.a.frontend.page=None
        self.a.frontend.key=confirm
        self.sample(['a']);self.sample(['a']);self.assertNotIn('space',self.a.keys)
        self.sample();self.sample(['a']);self.assertIn('space',self.a.keys)
    def test_menu_repeat_and_release(self):
        self.a.frontend.page='pause';self.sample(['down'])
        self.a.frontend.key.assert_called_once_with('down')
        self.c.tick(.5);self.assertEqual(self.a.frontend.key.call_count,2)
        self.sample();self.c.tick(1);self.assertEqual(self.a.frontend.key.call_count,2)
    def test_secret_code_works_on_intro(self):
        self.a.intro=Intro()
        for b in ('up','up','down','down','left','right','left','right'):
            self.sample([b]);self.sample()
        self.assertTrue(self.a.unlimited_lives)
    def test_late_keyboard_release_does_not_clear_controller_move(self):
        self.a.input_press(12,'Right');self.sample(['right']);self.a.input_release(12,'Right')
        self.assertIn('right',self.a.keys)
    def test_consumed_buttons_need_new_press(self):
        self.sample(['a']);self.a.keyboard.consume();self.sample(['a']);self.assertFalse(self.a.keys)
        self.sample();self.sample(['a']);self.assertIn('space',self.a.keys)
    def reader(self):
        r=LinuxController.__new__(LinuxController)
        r.lib=Mock();r.initialized=True;r.handle=123;r.next_scan=0;r.name='';r.error=''
        r.lib.SDL_GameControllerGetAttached.return_value=1
        r.lib.SDL_GameControllerGetAxis.side_effect=lambda h,i:{0:32767,2:-32768,5:32767}.get(i,0)
        r.lib.SDL_GameControllerGetButton.side_effect=lambda h,i:i in (0,2,11)
        return r
    def test_sdl_mapping_preserves_triggers_sticks_and_face_buttons(self):
        r=self.reader();s=r.poll(0)
        self.assertEqual(set(s['buttons']),{'a','x','up','rt'})
        self.assertEqual(s['axes'],[1,0,-1,0])
        r.lib.SDL_GameControllerGetAttached.return_value=0
        self.assertIsNone(r.poll(0));self.assertIsNone(r.handle)
        r.lib.SDL_GameControllerClose.assert_called_once_with(123)
    def test_missing_controller_is_optional_and_rescans_are_throttled(self):
        r=self.reader();r.handle=None;r.lib.SDL_NumJoysticks.return_value=0
        self.assertIsNone(r.poll(0));self.assertIsNone(r.poll(.5))
        r.lib.SDL_NumJoysticks.assert_called_once()
        self.assertIsNone(r.poll(1));self.assertEqual(r.lib.SDL_NumJoysticks.call_count,2)
    def test_hotplug_and_shutdown_leave_audio_subsystem_alone(self):
        r=self.reader();r.handle=None;r.lib.SDL_NumJoysticks.return_value=1
        r.lib.SDL_IsGameController.return_value=1;r.lib.SDL_GameControllerOpen.return_value=321
        r.lib.SDL_GameControllerName.return_value=b'GameSir'
        self.assertTrue(r.poll(1)['connected']);self.assertEqual(r.name,'GameSir')
        r.close();r.close();r.lib.SDL_QuitSubSystem.assert_called_once_with(0x2000)
    def test_unavailable_sdl_does_not_prevent_keyboard_play(self):
        with patch('omacontra.linux_controller.find_library',return_value=None):r=LinuxController()
        self.assertIsNone(r.poll(0));self.assertIn('unavailable',r.error)
    def test_profile_deadzone_migrates_and_clamps(self):
        import tempfile,json
        from pathlib import Path
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'profile.json';p.write_text(json.dumps({'settings':{'music':70}}))
            self.assertEqual(Profile(p).settings['deadzone'],20)
            p.write_text(json.dumps({'settings':{'deadzone':150}}))
            self.assertEqual(Profile(p).settings['deadzone'],40)

    def test_space_aim_rotates_beam_and_muzzle_together(self):
        import math
        from omacontra.stages.space.finale import Finale
        from omacontra.rendering.space_pose import laser_muzzle
        f=Finale();f.skip();f.invuln=999
        f.step(.016,shoot=True,aim=(f.x+300,f.y))
        self.assertAlmostEqual(f.laser_angle,0)
        self.assertEqual(f.laser_muzzle,laser_muzzle(f.x,f.y,math.pi/2))
        self.assertGreater(f.beam[-1][0],f.beam[0][0])
        f.step(.016,shoot=True)
        self.assertAlmostEqual(f.laser_angle,-math.pi/2)
        self.assertEqual(f.laser_muzzle,laser_muzzle(f.x,f.y))

    def test_left_stick_and_dpad_have_all_eight_fire_directions(self):
        import math
        for dx,dy in ((0,-1),(0,1),(-1,0),(1,0),(-1,-1),(1,-1),(-1,1),(1,1)):
            self.sample();self.sample(['rt'],[dx,dy,0,0])
            length=math.hypot(dx,dy)
            self.assertEqual(self.c.direction,(dx/length,dy/length))
        self.sample();self.sample(['x','up']);self.assertEqual(self.c.direction,(0,-1))
        self.sample();self.sample(['x','down']);self.assertEqual(self.c.direction,(0,1))
    def test_right_stick_overrides_movement_aim_and_neutral_movement_does_not_aim(self):
        self.sample(['rt'],[0,-1,1,0]);self.assertEqual(self.c.direction,(1,0))
        self.sample(axes=[0,1,0,0]);self.assertIsNone(self.c.direction)
    def test_vertical_fire_has_no_sideways_drift_or_facing_flip(self):
        from omacontra.rendering.hero_pose import weapon_pose
        for direction in (-1,1):
            for facing in (-1,1):
                f=self.a.f=Fight();f.facing=facing;f.invuln=99
                self.sample();self.sample(['rt'],[0,direction,0,0])
                f.stick_aim=self.c.direction
                f.step(.016,shoot=True,duck=direction>0,aim=self.c.aim)
                bullets=[b for b in f.shots if not b.enemy]
                self.assertTrue(bullets);self.assertAlmostEqual(bullets[0].vx,0,places=6)
                self.assertAlmostEqual(bullets[0].vy,800*direction,places=6)
                self.assertEqual(f.facing,facing)

import unittest
from omacontra.stages.dragon.foundry import Foundry, EXPLOSION
from omacontra.audio.foundry_audio import FoundryEffects, AUDIO
import cairo
from omacontra.rendering import sprites
from omacontra.stages.dragon.wyrm_scene import MOUTH, EYES

class FoundryAudioTests(unittest.TestCase):
    def test_breath_and_laser_follow_dragon_mouth(self):
        f=Foundry();f.clock=2
        self.assertEqual(f.cannon,f.dragon_point(*MOUTH))
        self.assertEqual(f.mount_target,f.cannon)
        f.emit('fan',0)
        self.assertEqual(f.sfx_events,['eye_shot'])
        self.assertTrue(all((b.x,b.y)==f.dragon_point(*EYES[(f.forge_round-1)%2]) for b in f.bolts))
        f.update_shoulder(.02);self.assertNotIn('laser_charge',f.sfx_events)
        self.assertNotIn('laser_pulse',f.sfx_events)

    def test_disarm_and_rescue_blast_are_single_events(self):
        f=Foundry();f.begin_disarm();self.assertIn('disarm',f.sfx_events)
        f.state='play';f.begin_rescue();self.assertIn('defeat',f.sfx_events)
        f.rescue_age=EXPLOSION-.01
        f.step(.02);f.step(.02)
        self.assertEqual(f.sfx_events.count('rescue_blast'),1)

    def test_all_sound_assets_load_and_sprite_has_alpha(self):
        mixer=FoundryEffects();paths=list(AUDIO.glob('*.wav'))
        self.assertEqual(len(paths),24)
        for path in paths:
            for _ in range(3):mixer.trigger(path.stem);mixer.mix(bytes(1764))
        self.assertFalse(mixer.failed)
        s=sprites.atlas('wyrm-head.png')
        self.assertEqual((s.get_width(),s.get_height()),(1254,1254))
        self.assertEqual(s.get_format(),cairo.FORMAT_ARGB32)
        self.assertEqual(bytes(s.get_data())[3],0)

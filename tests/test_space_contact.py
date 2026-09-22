import array
import unittest
from unittest.mock import patch
import cairo
from omacontra.audio.finale_audio import FinaleEffects
from omacontra.audio.weapon_audio import WeaponAudio
from omacontra.stages.space.finale import Finale
from omacontra.stages.space import containment_shield

class SpaceContactTests(unittest.TestCase):
    def test_contact_stream_is_unbroken_and_does_not_restart_each_frame(self):
        for kind in ('shield','flesh'):
            bank=FinaleEffects();chunks=[]
            for _ in range(210):
                bank.set_contact(kind)
                chunks.append(array.array('h',bank.mix(bytes(1764))))
            # Covers two wraps. Every 20ms buffer after fade-in has energy.
            rms=[(sum(v*v for v in chunk)/len(chunk))**.5 for chunk in chunks[1:]]
            self.assertGreater(min(rms),100)
            self.assertLess(max(rms)/min(rms),2.5)
            self.assertGreater(len({c.tobytes() for c in chunks[:40]}),35)
            self.assertFalse(bank.voices)
            bank.set_contact(None);bank.mix(bytes(1764))
            self.assertFalse(bank.active)
            self.assertEqual(bank.mix(bytes(1764)),bytes(1764))

    def test_switch_material_and_pause_clear_sustained_audio(self):
        bank=FinaleEffects();bank.set_contact('shield');bank.mix(bytes(1764))
        bank.set_contact('flesh');bank.mix(bytes(1764))
        self.assertEqual(bank.contact_gain,{'shield':0.,'flesh':1.})
        bank.clear();self.assertFalse(bank.active)
        sound=WeaponAudio();f=Finale();f.skip();f.beam_hit=True;f.laser_contact='shield'
        with patch.object(sound,'open',return_value=False):sound.update(f,False,True)
        self.assertEqual(sound.effects.contact,'shield')
        sound.update_menu(False);self.assertFalse(sound.effects.active)

    def test_real_laser_contact_selects_material_without_periodic_hit_events(self):
        f=Finale();f.skip()
        for exposed,expected in ((False,'shield'),(True,'flesh')):
            if exposed:f.nodes=[0,0]
            f.x=(f.boss if exposed else f.node(0))[0];f.y=550
            f.sfx_events.clear();f.update_laser(.02,True)
            self.assertTrue(f.beam_hit)
            self.assertEqual(f.laser_contact,expected)
            self.assertNotIn('node_hit',f.sfx_events);self.assertNotIn('laser_hit',f.sfx_events)
            f.update_laser(.02,False)
            self.assertIsNone(f.laser_contact)

    def test_shield_damage_is_progressive_and_exposed_phase_has_no_shield(self):
        previous_damage=-1
        for health in (1.,.75,.55,.5,.25,.15,.05,0.):
            layers=containment_shield.damage_layers(health)
            self.assertTrue(all(0<=alpha<=1 for _,alpha in layers))
            weight=sum(alpha for _,alpha in layers)
            self.assertLessEqual(weight,1.00001)
            damage=sum(index*alpha for index,alpha in layers)/(weight or 1) if health else 2
            self.assertGreaterEqual(damage,previous_damage);previous_damage=damage
        self.assertEqual(containment_shield.damage_layers(0),((2,0.),))
        f=Finale();f.skip();images=[]
        for hp in (f.node_max,f.node_max*.5,0):
            f.nodes=[hp,hp]
            s=cairo.ImageSurface(cairo.FORMAT_ARGB32,1280,720)
            containment_shield.draw(cairo.Context(s),f);images.append(bytes(s.get_data()))
        self.assertNotEqual(images[0],images[1])
        self.assertFalse(any(images[2]))

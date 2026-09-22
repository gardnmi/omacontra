import unittest
from omacontra.stages.reaper.combat import Fight
from omacontra.stages.highway.chase import Chase
from omacontra.stages.harbor.tidebreaker import Tidebreaker
from omacontra.stages.dragon.foundry import Foundry
from omacontra.stages.space.finale import Finale


class ArcadeDetailsTests(unittest.TestCase):
    def test_double_jump_has_distinct_cue_on_foot(self):
        for cls in (Fight,Tidebreaker,Foundry):
            with self.subTest(stage=cls.__name__):
                f=cls();f.step(.02,jump=True);f.step(.02,jump=False);f.step(.02,jump=True)
                self.assertEqual(f.sfx_events.count('jump'),1)
                self.assertEqual(f.sfx_events.count('double_jump'),1)
                f.step(.02,jump=True)
                self.assertEqual(f.sfx_events.count('double_jump'),1)

    def test_ready_cues_only_fire_when_recharge_finishes(self):
        for cls,field,cue in ((Chase,'boost_cooldown','boost_ready'),(Finale,'dash_cooldown','thruster_ready')):
            with self.subTest(stage=cls.__name__):
                f=cls();f.state='play'
                f.step(.02);self.assertNotIn(cue,f.sfx_events)
                setattr(f,field,.03);f.step(.02);self.assertNotIn(cue,f.sfx_events)
                f.step(.02);f.step(.02)
                self.assertEqual(f.sfx_events.count(cue),1)

    def test_guardian_reveal_and_final_charge_are_one_shots(self):
        f=Tidebreaker();f.begin_reveal();f.wave_reveal=.03
        f.step(.02);self.assertNotIn('guardian_arrival',f.sfx_events)
        f.step(.02);f.step(.02)
        self.assertEqual(f.sfx_events.count('guardian_arrival'),1)
        f=Foundry();f.begin_rescue();f.rescue_age=1.23
        f.step(.04);f.step(.04)
        self.assertEqual(f.sfx_events.count('ultimate_charge'),1)

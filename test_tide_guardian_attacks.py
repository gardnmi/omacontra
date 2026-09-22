import unittest
from tidebreaker import Tidebreaker
import tide_guardian_attacks as special

class GuardianAttackTests(unittest.TestCase):
    def fight(self):
        f=Tidebreaker(7);f.advance_guardian();f.invuln=0
        return f

    def test_relay_can_be_jumped(self):
        for airborne in (False,True):
            f=self.fight();a=f.guardians[0];a.attack='relay';a.age=1
            f.x=special.relay_position(f,a,1)[0];f.y=f.floor-(100 if airborne else 0)
            special.step(f,a,.04)
            self.assertEqual(f.hp,6 if airborne else 5)

    def test_stars_hold_locked_lanes_and_fall_in_sequence(self):
        f=self.fight();a=f.guardians[1];special.start(f,a,'stars')
        lanes=a.star_lanes;f.x=900
        a.warning=None;a.attack='stars'
        for _ in range(95):special.step(f,a,.02)
        self.assertEqual(a.star_lanes,lanes)
        self.assertIn(0,a.star_hits);self.assertNotIn(2,a.star_hits)

    def test_coordinated_attack_has_jump_then_duck_escape(self):
        f=self.fight();f.x=575;f.y=f.floor;f.team_timer=0
        hp=f.hp;f.step(.02)
        self.assertEqual([a.warning for a in f.guardians],['relay','stars'])
        for _ in range(300):
            relay=f.guardians[0]
            hook,_=special.relay_position(f,relay,relay.age)
            jump=relay.attack=='relay' and 0<hook-f.x<110 and f.y>=f.floor-.1
            f.step(.02,jump=jump,duck=relay.attack=='relay' and relay.age>1.8)
        self.assertEqual(f.hp,hp)
        self.assertTrue(all(a.exposed>0 for a in f.guardians))

    def test_high_followup_requires_duck_or_slide(self):
        for duck in (False,True):
            f=self.fight();a=f.guardians[0];a.attack='relay';a.linked=True;a.age=2.4
            f.x=640;f.y=f.floor;f.duck=duck
            special.step(f,a,.04)
            self.assertEqual(f.hp,6 if duck else 5)

    def test_either_survivor_enrages_once_and_switches_patterns(self):
        for dead_index in (0,1):
            f=self.fight();dead=f.guardians[dead_index];survivor=f.guardians[1-dead_index]
            dead.exposed=1;dead.hp=1;x,y=dead.core(f.floor)
            f.hit_guardians(x-10,y,x+10,y,2)
            self.assertTrue(survivor.enraged);self.assertEqual(survivor.rage_age,0)
            self.assertEqual(survivor.hp,survivor.maximum)
            for _ in range(50):f.guardian_step(.02)
            self.assertIsNone(survivor.attack);self.assertIsNone(survivor.warning)
            for _ in range(100):f.guardian_step(.02)
            self.assertEqual(survivor.warning,'relay' if survivor.kind==1 else 'stars')
            if survivor.kind==2:self.assertEqual(len(survivor.star_lanes),5)

    def test_slide_passes_under_charge_but_standing_is_hit(self):
        for sliding in (False,True):
            f=self.fight();a=f.guardians[0];a.attack='charge';a.end=640;a.age=.8
            f.x=640;f.y=f.floor;f.slide_time=.3 if sliding else 0
            f.guardian_step(.02)
            self.assertEqual(f.hp,6 if sliding else 5)

    def test_enraged_astronaut_fires_during_meteor_attack(self):
        f=self.fight();a=f.guardians[1];f.guardians[0].hp=0
        a.enraged=True;a.rage_age=3;a.attack='stars';a.age=0;a.rage_fire=0
        f.guardian_step(.02)
        self.assertEqual(a.attack,'stars')
        self.assertTrue(any(b.kind=='orbit_bolt' for b in f.shots))
        self.assertGreater(a.exposed,0)

    def test_rage_cinema_freezes_player_and_shots(self):
        f=self.fight();a=f.guardians[1];a.enraged=True;a.rage_age=0
        x,y=f.x,f.y
        for _ in range(50):f.step(.02,move=1,jump=True,shoot=True)
        self.assertEqual((f.x,f.y),(x,y));self.assertFalse(f.shots)

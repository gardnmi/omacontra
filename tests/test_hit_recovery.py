import unittest
from omacontra.stages.reaper.combat import Fight
from omacontra.stages.dragon.foundry import Foundry

class HitRecoveryTests(unittest.TestCase):
    def test_life_loss_fall_respawn_and_protection(self):
        f=Fight();f.invuln=0;f.y=f.floor;f.step(.01)
        hp=f.hp;f.hurt();f.hurt()
        self.assertEqual(f.hp,hp-1);self.assertEqual(f.hit_age,0)
        before=len(f.shots)
        for _ in range(10):f.step(.04,shoot=True,move=1)
        self.assertIsNotNone(f.hit_age);self.assertEqual(len(f.shots),before)
        for _ in range(5):f.step(.04)
        self.assertIsNone(f.hit_age);self.assertGreater(f.invuln,2.8)
        self.assertEqual(f.y,f.floor);f.hurt();self.assertEqual(f.hp,hp-1)
        f.invuln=0;f.hurt();self.assertEqual(f.hp,hp-2)

    def test_last_ribbon_does_not_respawn(self):
        f=Fight();f.hp=1;f.invuln=0;f.hurt()
        for _ in range(20):f.step(.04)
        self.assertEqual(f.state,'dead');self.assertEqual(f.hp,0)
        self.assertIsNone(f.hit_age)

    def test_lava_recovery_places_player_on_platform(self):
        f=Foundry();f.lava_age=9;f.invuln=0;f.hurt()
        from omacontra import hit_recovery
        hit_recovery.tick(f,.6)
        self.assertIn(f.support,f.platforms)
        self.assertEqual(f.y,f.support[2]);self.assertEqual(f.invuln,3)

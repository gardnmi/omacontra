import unittest
from types import SimpleNamespace
from omacontra.campaign_progress import prepare_encounter

class CampaignHealthTests(unittest.TestCase):
    def test_advancing_keeps_losses_and_adds_exactly_one_life(self):
        for level in range(2,6):
            for remaining in (1,2,level+3):
                f=prepare_encounter(SimpleNamespace(),level,remaining=remaining)
                self.assertEqual(f.hp,remaining+1)
                self.assertEqual(f.max_hp,5+level-1)

    def test_one_extra_ribbon_for_each_cleared_chapter(self):
        previous=4
        for level in range(1,6):
            f=prepare_encounter(SimpleNamespace(hp=1),level)
            self.assertEqual(f.max_hp,previous+1)
            self.assertEqual(f.hp,f.max_hp)
            previous=f.max_hp

    def test_retry_restores_health_without_adding_another_ribbon(self):
        f=SimpleNamespace(hp=0)
        for _ in range(4):
            prepare_encounter(f,4)
            self.assertEqual((f.hp,f.max_hp),(8,8))
            f.hp=0

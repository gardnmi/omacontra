import unittest
import cairo
from omacontra.rendering import sprites
from omacontra.rendering.character_assets import ALPHA_MATTES

class CharacterAssetTests(unittest.TestCase):
    def test_replacement_backgrounds_stay_transparent(self):
        for name,original in ALPHA_MATTES.items():
            with self.subTest(asset=name):
                old=cairo.ImageSurface.create_from_png(str(sprites.ASSETS/original))
                new=sprites.atlas(name)
                self.assertEqual((old.get_width(),old.get_height()),(new.get_width(),new.get_height()))
                old_data=old.get_data();new_data=new.get_data()
                for y in range(0,old.get_height(),31):
                    for x in range(0,old.get_width(),31):
                        offset=y*old.get_stride()+x*4+3
                        if old_data[offset]==0:self.assertEqual(new_data[offset],0)

    def test_lamborghini_head_gap_has_no_brown_haze(self):
        sheet=sprites.atlas('finale-catch-car-canonical.png')
        data=sheet.get_data()
        for x,y in ((710,550),(500,540),(800,520)):
            self.assertEqual(data[y*sheet.get_stride()+x*4+3],0)

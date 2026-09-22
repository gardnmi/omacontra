import unittest
from omacontra.input_state import KeyboardState
from omacontra.stages.reaper.combat import Fight

class KeyboardTests(unittest.TestCase):
    def test_shift_press_caps_lock_release_rearms_each_slide(self):
        keys=KeyboardState();f=Fight();f.invuln=99
        for _ in range(4):
            key,fresh=keys.press(50,'Shift_L')
            self.assertTrue(fresh)
            f.step(.02,slide='shift_l' in keys.keys,slide_pressed=fresh)
            self.assertTrue(f.sliding)
            # The live GTK trace releases keycode 50 as Caps_Lock: release by code.
            keys.release(50)
            self.assertNotIn('shift_l',keys.keys)
            for _ in range(40):f.step(.02,slide='shift_l' in keys.keys)
            self.assertFalse(f.sliding)

    def test_auto_repeat_does_not_create_new_press(self):
        keys=KeyboardState();self.assertEqual(keys.press(50,'Shift_L'),('shift_l',True))
        for name in ('Shift_L','Caps_Lock','Shift_L'):
            self.assertEqual(keys.press(50,name),('shift_l',False))
        keys.release(50);self.assertEqual(keys.press(50,'Shift_L'),('shift_l',True))

    def test_shifted_letters_release_and_focus_reset(self):
        keys=KeyboardState();keys.press(38,'A');keys.press(40,'d')
        keys.release(38);self.assertEqual(keys.keys,{'d'})
        keys.clear();self.assertFalse(keys.keys)
        self.assertEqual(keys.press(40,'D'),('d',True))

    def test_two_physical_keys_for_same_action(self):
        keys=KeyboardState();keys.press(50,'Shift_L');keys.press(62,'Shift_L')
        keys.release(50);self.assertEqual(keys.keys,{'shift_l'})
        keys.release(62);self.assertFalse(keys.keys)

if __name__=='__main__':unittest.main()

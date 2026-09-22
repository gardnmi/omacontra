import array
import unittest
import wave
from omacontra.resources import ASSETS
from omacontra.audio.reaper_audio import ReaperEffects

class MenuAudioTests(unittest.TestCase):
    def test_all_cues_have_soft_complete_tails_and_bounded_voices(self):
        root=ASSETS/'audio/menu'
        names={'move','adjust','open','back','confirm','complete'}
        self.assertEqual({p.stem for p in root.glob('*.wav')},names)
        bank=ReaperEffects(root)
        for name in names:
            with wave.open(str(root/f'{name}.wav')) as f:
                self.assertEqual((f.getframerate(),f.getnchannels(),f.getsampwidth()),(44100,1,2))
                pcm=array.array('h',f.readframes(f.getnframes()))
            self.assertEqual(pcm[0],0);self.assertEqual(pcm[-1],0)
            self.assertGreater(max(map(abs,pcm)),200)
            self.assertLess(max(map(abs,pcm)),650)
            for _ in range(20):bank.trigger(name)
            self.assertLessEqual(len(bank.voices),6)
        self.assertFalse(bank.failed)

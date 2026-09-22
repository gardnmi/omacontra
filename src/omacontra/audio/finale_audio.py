"""Soft orbital weapons and containment effects on the shared audio stream."""
from omacontra.resources import ASSETS
import array
import wave
from omacontra.audio.reaper_audio import ReaperEffects, EFFECT_GAIN, LIMIT

AUDIO=ASSETS/'audio/finale'

class FinaleEffects(ReaperEffects):
    def __init__(self):
        super().__init__(audio=AUDIO,priority={
            'defeat':4,'death':4,'release':4,'node_break':3,'hurt':3,
            'enrage':3,'thruster':2,'ring':2,'fan':2,'spiral':2,'needles':2,
            'curtain':2,'laser_start':1,'laser_hit':1})

        self.contact=None;self.contact_samples={}
        self.contact_gain={'shield':0.,'flesh':0.};self.contact_pos={'shield':0,'flesh':0}

    def set_contact(self,kind):
        if kind and kind not in self.contact_samples:
            try:
                with wave.open(str(self.audio/'loops'/f'{kind}.wav')) as f:
                    if (f.getframerate(),f.getnchannels(),f.getsampwidth())!=(44100,1,2):
                        raise ValueError('Unexpected contact-loop format')
                    self.contact_samples[kind]=array.array('h',f.readframes(f.getnframes()))
            except (OSError,ValueError,wave.Error):kind=None
        self.contact=kind

    @property
    def active(self):return super().active or self.contact is not None or any(self.contact_gain.values())

    def mix(self,data):
        output=array.array('h',super().mix(data))
        for kind,sample in self.contact_samples.items():
            gain=self.contact_gain[kind];target=1. if self.contact==kind else 0.
            if gain==target==0:continue
            pos=self.contact_pos[kind]
            for i in range(len(output)):
                gain=min(target,gain+1/661.5) if gain<target else max(target,gain-1/661.5)
                v=output[i]+round(sample[pos]*gain*self.gain*EFFECT_GAIN)
                output[i]=max(-LIMIT,min(LIMIT,v));pos=(pos+1)%len(sample)
            self.contact_gain[kind]=gain;self.contact_pos[kind]=pos
        return output.tobytes()

    def clear(self):
        super().clear();self.contact=None
        self.contact_gain={'shield':0.,'flesh':0.};self.contact_pos={'shield':0,'flesh':0}

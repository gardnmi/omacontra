"""Bounded one-shot mixer for the first encounter, sharing the gun's SDL stream."""
from omacontra.resources import ASSETS
import array
import wave

AUDIO=ASSETS/'audio/reaper'
PRIORITY={'rupture':4,'defeat':4,'player_death':4,'hurt':3,'break':3,
          'raven_break':3,'eye_break':3,'expose':2,'reform':2,'sweep':2,'skull':2,'raven':2,'charge':2}
EFFECT_GAIN=10**(5/20)  # +3 dB above the previous mix.
LIMIT=round(32767*10**(-20/20))

class ReaperEffects:
    def __init__(self,audio=AUDIO,priority=None):
        self.audio=audio;self.priority=PRIORITY if priority is None else priority
        self.samples={};self.voices=[];self.failed=False;self.takes={}
        self.gain=1.

    def trigger(self,name):
        if self.failed:return
        try:
            variant=self.takes.get(name,0)%3
            self.takes[name]=variant+1
            key=f'variants/{name}-{variant}' if variant else name
            if variant and not (self.audio/f'{key}.wav').exists():key=name
            if key not in self.samples:
                with wave.open(str(self.audio/f'{key}.wav')) as f:
                    if (f.getframerate(),f.getnchannels(),f.getsampwidth())!=(44100,1,2):
                        raise ValueError('Unexpected encounter sound format')
                    pcm=array.array('h',f.readframes(f.getnframes()))
                    self.samples[key]=array.array('h',(round(v*EFFECT_GAIN) for v in pcm))
            selected=self.samples[key]
        except (OSError,ValueError,wave.Error) as error:
            self.failed=True;self.clear();print(f'Encounter effects unavailable: {error}',flush=True);return
        # Never stack repeated impact tails; important cues displace quiet ones.
        self.voices=[v for v in self.voices if v[0]!=name]
        priority=self.priority.get(name,1)
        if len(self.voices)>=6:
            quiet=min(self.voices,key=lambda v:self.priority.get(v[0],1))
            if self.priority.get(quiet[0],1)>priority:return
            self.voices.remove(quiet)
        self.voices.append([name,0,selected])

    def mix(self,data):
        if not self.voices:return data
        output=list(array.array('h',data));keep=[]
        for voice in self.voices:
            name,pos,sample=voice
            count=min(len(output),len(sample)-pos)
            for i in range(count):output[i]+=round(sample[pos+i]*self.gain)
            voice[1]+=count
            if voice[1]<len(sample):keep.append(voice)
        self.voices=keep
        # Bound the complete effect + gun mix so a busy frame stays soft.
        return array.array('h',(max(-LIMIT,min(LIMIT,v)) for v in output)).tobytes()

    @property
    def active(self):return bool(self.voices)

    def clear(self):self.voices=[]

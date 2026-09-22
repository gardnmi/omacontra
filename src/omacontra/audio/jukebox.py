"""Menu-only soundtrack player; preserves the campaign player's position."""
import json
from omacontra.audio.intro_music import IntroMusic, GAME_TRACKS, FINALE_TRACK, TRACK
from omacontra.resources import ASSETS

class Jukebox:
    def __init__(self):
        library=json.loads((ASSETS/'audio/library.json').read_text())
        by_file={v['file']:v for v in library.values() if isinstance(v,dict) and 'file' in v}
        self.tracks=tuple(by_file[p.name] for p in (*GAME_TRACKS,TRACK.parent/'the-descent.mp3',TRACK,FINALE_TRACK))
        self.audio=IntroMusic()
        self.index=None;self.paused=False

    def play(self,index):
        if index==self.index:
            self.paused=not self.paused
        else:
            self.audio.stop();self.audio.failed=False
            self.audio.track=ASSETS/'audio'/self.tracks[index]['file']
            self.index=index;self.paused=False

    def skip(self,direction):
        base=self.index if self.index is not None else (-1 if direction>0 else 0)
        index=(base+direction)%len(self.tracks)
        self.play(index)

    def stop(self):
        self.audio.stop();self.index=None;self.paused=False

    def update(self,visible,volume):
        self.audio.set_volume(volume)
        self.audio.update(self.index is not None,not visible or self.paused)

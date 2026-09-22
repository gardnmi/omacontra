"""Dragon breath and throat-energy bank, mixed softly under the soundtrack."""
from omacontra.resources import ASSETS
from omacontra.audio.reaper_audio import ReaperEffects
AUDIO=ASSETS/'audio/wyrm'
class FoundryEffects(ReaperEffects):
    def __init__(self):
        super().__init__(audio=AUDIO,priority={'disarm':4,'defeat':4,'rescue_blast':4,'player_death':4,'hurt':3,'ultimate_charge':3,'pickup':3,'breath':2,'gust':2})

"""Soft orbital weapons and containment effects on the shared audio stream."""
from omacontra.resources import ASSETS
from omacontra.audio.reaper_audio import ReaperEffects

AUDIO=ASSETS/'audio/finale'

class FinaleEffects(ReaperEffects):
    def __init__(self):
        super().__init__(audio=AUDIO,priority={
            'defeat':4,'death':4,'release':4,'node_break':3,'hurt':3,
            'enrage':3,'thruster':2,'ring':2,'fan':2,'spiral':2,'needles':2,
            'curtain':2,'laser_start':1,'laser_hit':1})

"""Vehicle effects use the same bounded mixer and gain as stage one."""
from omacontra.resources import ASSETS
from omacontra.audio.reaper_audio import ReaperEffects

AUDIO=ASSETS/'audio/chase'
PRIORITY={'car_wreck':4,'robot_break':4,'truck_break':4,'car_hit':3,
          'component_break':3,'unfold':3,'lock':3,'cannon':3,'finisher':3,
          'mortar':2,'rockets':2,'road_blast':2,'boost':2,'heart':2}

class ChaseEffects(ReaperEffects):
    def __init__(self):super().__init__(audio=AUDIO,priority=PRIORITY)

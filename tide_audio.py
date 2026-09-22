"""Tidebreaker sound bank: water, deck foley, and distinct guardian weapons."""
from pathlib import Path
from reaper_audio import ReaperEffects
AUDIO=Path(__file__).parent/'assets/audio/tide'
PRIORITY={'wave_death':4,'coat_death':4,'orbit_death':4,'player_death':4,
          'rage_coat':3,'rage_orbit':3,'hurt':3,'water_crash':3,'slam':3,
          'surge':2,'breaker':2,'pistol':2,'orbit':2,'relay':2,'stars':2}
class TideEffects(ReaperEffects):
    def __init__(self):super().__init__(audio=AUDIO,priority=PRIORITY)

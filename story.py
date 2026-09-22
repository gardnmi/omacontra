"""OMACONTRA intro timing, independent of GTK and rendering."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Beat:
    kind: str
    lines: tuple[str, ...]
    duration: float


JOURNEY_BEATS = (
    Beat('story', ('THE WORLD WATCHED THE FRONTIER LABS.', 'THE REAL PROBLEM WAS IN A WINE CELLAR.'), 5.4),
    Beat('cellar', ('TOBI: COME LOOK AT THE SERVER I BUILT.', 'DHH: IN YOUR WINE RACK?'), 5.8),
    Beat('demonstration', ('TOBI: PERFECT TEMPERATURE. PLENTY OF SPACE.', 'WATCH THIS.'), 5.0),
    Beat('portal', ('DHH: TOBI... WHAT DID YOU RUN?', 'TOBI: THAT WAS NOT SUPPOSED TO HAPPEN.'), 5.8),
    Beat('separated', ('CONNECTION LOST.', 'TWO USERS. TWO UNKNOWN LOCATIONS.'), 4.0),
    Beat('wake', ("DHH: AM I IN AN OMARCHY MACHINE?",), 8.5),
    Beat('resolve', ("BUT IT DOESN'T MATTER.", 'BECAUSE YOU CAN FIX ANYTHING.'), 5.4),
    Beat('cover', (), float('inf')),
)
BEATS = (
    Beat('story', ('THE WORLD EXPECTED AI DOOM', 'TO COME FROM THE FRONTIER LABS.'), 5.2),
    Beat('containment', ('NATIONS PREPARED FOR CONTAINMENT.', 'SAFEGUARDS. SHUTDOWN SWITCHES.'), 5.2),
    Beat('labs', ('EVERY EYE WAS ON', 'OPENAI AND ANTHROPIC.'), 4.6),
    Beat('threat', ('BUT THE REAL THREAT', 'WAS ALREADY ONLINE...'), 4.0),
    Beat('cellar', ("IN TOBI LUTKE'S WINE CELLAR.",), 6.0),
    Beat('resolve', ("BUT IT DOESN'T MATTER.", 'BECAUSE YOU CAN FIX ANYTHING.'), 5.4),
    Beat('cover', (), float('inf')),
)
# The newer portal story belongs after Start, before the Reaper encounter.
JOURNEY_BEATS = JOURNEY_BEATS[1:6]
COVER_AT = sum(beat.duration for beat in BEATS[:-1])


SECRET_CODE=('up','up','down','down','left','right','left','right')

class Intro:
    def __init__(self,journey=False):
        self.journey=journey
        self.beats=JOURNEY_BEATS if journey else BEATS
        self.index = 0
        self.age = 0.
        self.paused = False
        self.start_age = None
        self.unlimited_lives=False
        self.code_keys=()
        self.unlock_age=None

    @property
    def beat(self):
        return self.beats[self.index]

    def step(self, dt):
        if self.paused:
            return
        if self.unlock_age is not None:self.unlock_age+=max(0.,dt)
        if self.start_age is not None:
            self.start_age += max(0.,dt)
            return
        self.age += max(0., dt)
        while self.age >= self.beat.duration and self.index < len(self.beats)-1:
            self.age -= self.beat.duration
            self.index += 1

    @property
    def finished(self):
        return self.journey and self.index==len(self.beats)-1 and self.age>=self.beat.duration

    def enter_code(self,key):
        if self.beat.kind!='cover' or self.start_age is not None or self.unlimited_lives:return False
        self.code_keys=(*self.code_keys,key)[-len(SECRET_CODE):]
        if self.code_keys==SECRET_CODE:
            self.unlimited_lives=True;self.unlock_age=0.;self.code_keys=()
            return True
        # Retain the longest matching prefix, including overlapping Up presses.
        while self.code_keys and self.code_keys!=SECRET_CODE[:len(self.code_keys)]:
            self.code_keys=self.code_keys[1:]
        return False

    def request_start(self):
        if self.beat.kind!='cover' or self.start_age is not None:return False
        self.start_age=0.;self.paused=False
        return True

    @property
    def start_finished(self):
        return self.start_age is not None and self.start_age>=2.4

    def advance(self):
        if self.index < len(self.beats)-1:
            self.index += 1
            self.age = 0.
        elif self.journey:self.age=self.beat.duration

    def reset(self):
        self.code_keys=();self.unlock_age=None
        self.index = 0
        self.age = 0.
        self.paused = False
        self.start_age = None

    @property
    def typed_lines(self):
        if self.beat.kind == 'resolve':
            return (self.beat.lines[0] if self.age > .35 else '',
                    self.beat.lines[1] if self.age > 2.0 else '')
        delay = 2.3 if self.beat.kind == 'wake' else .35
        count = max(0, int((self.age-delay)*31))
        output = []
        for line in self.beat.lines:
            output.append(line[:count])
            count = max(0, count-len(line)-5)
        return tuple(output)

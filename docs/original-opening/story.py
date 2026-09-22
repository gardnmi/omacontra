"""OMACONTRA intro timing, independent of GTK and rendering."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Beat:
    kind: str
    lines: tuple[str, ...]
    duration: float


BEATS = (
    Beat('story', ('THE WORLD EXPECTED AI DOOM', 'TO COME FROM THE FRONTIER LABS.'), 5.2),
    Beat('containment', ('NATIONS PREPARED FOR CONTAINMENT.', 'SAFEGUARDS. SHUTDOWN SWITCHES.'), 5.2),
    Beat('labs', ('EVERY EYE WAS ON', 'OPENAI AND ANTHROPIC.'), 4.6),
    Beat('threat', ('BUT THE REAL THREAT', 'WAS ALREADY ONLINE...'), 4.0),
    Beat('cellar', ("IN TOBI LUTKE'S WINE CELLAR.",), 6.0),
    Beat('resolve', ("BUT IT DOESN'T MATTER.", 'BECAUSE YOU CAN FIX ANYTHING.'), 5.4),
    Beat('cover', (), float('inf')),
)
COVER_AT = sum(beat.duration for beat in BEATS[:-1])


class Intro:
    def __init__(self):
        self.index = 0
        self.age = 0.
        self.paused = False

    @property
    def beat(self):
        return BEATS[self.index]

    def step(self, dt):
        if self.paused:
            return
        self.age += max(0., dt)
        while self.age >= self.beat.duration and self.index < len(BEATS)-1:
            self.age -= self.beat.duration
            self.index += 1

    def advance(self):
        if self.index < len(BEATS)-1:
            self.index += 1
            self.age = 0.

    def reset(self):
        self.index = 0
        self.age = 0.
        self.paused = False

    @property
    def typed_lines(self):
        if self.beat.kind == 'resolve':
            return (self.beat.lines[0] if self.age > .35 else '',
                    self.beat.lines[1] if self.age > 2.0 else '')
        count = max(0, int((self.age-.35)*31))
        output = []
        for line in self.beat.lines:
            output.append(line[:count])
            count = max(0, count-len(line)-5)
        return tuple(output)

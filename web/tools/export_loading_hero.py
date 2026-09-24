"""Render the web loader through the game's real DHH renderer (no new artwork)."""
from pathlib import Path
import sys
import cairo

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from omacontra.stages.reaper.combat import Fight
from omacontra.stages.reaper.battle_art import BattleRenderer

# Thirty evenly spaced samples preserve the native held torso/stride timings.
WIDTH, HEIGHT, FRAMES = 128, 112, 30
sheet = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH * (FRAMES + 1), HEIGHT)
c = cairo.Context(sheet)
f = Fight(7)
f.invuln = 0
f.aim_target = None
renderer = BattleRenderer()
for i in range(FRAMES + 1):
    f.moving = i < FRAMES
    f.run_phase = i * 6 / FRAMES
    c.save()
    c.rectangle(i * WIDTH, 0, WIDTH, HEIGHT)
    c.clip()
    c.translate(i * WIDTH + 48 - f.x, 102 - f.y)
    renderer.hero(c, f, None)
    c.restore()
sheet.write_to_png(str(ROOT / 'web/src/campaign/assets/loading-dhh.png'))

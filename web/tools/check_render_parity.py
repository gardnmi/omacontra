#!/usr/bin/env python3
"""Compare the browser's real renderer captures to the native Cairo art sheet.

Run after Playwright and tools/asset_review.py. Canvas and Cairo have slightly
 different edge/font rasterization, so this checks whole-frame RGB mean error.
"""

from pathlib import Path
import json
import cairo

ROOT = Path(__file__).resolve().parents[1]
NAMES = (
    "01-reaper",
    "02-highway",
    "03-ocean",
    "03-guardians",
    "04-fire",
    "04-flood",
    "04-shoulder",
    "04-disarm",
    "04-arc-rifle",
    "05-orbit-1",
    "05-orbit-2",
    "05-orbit-3",
)
results = {}
# Firefox resamples transformed nearest-neighbor images differently from Cairo;
# inspected differences are concentrated at pixel/shape edges, not placement.
limits = {"chromium": 4, "firefox": 6}
for browser in ("chromium", "firefox"):
    for index, name in enumerate(NAMES):
        native = cairo.ImageSurface.create_from_png(
            str(ROOT / "test-results/native" / f"{name}.png")
        )
        web = cairo.ImageSurface.create_from_png(
            str(ROOT / "test-results" / f"{browser}-native-scene-{index}.png")
        )
        assert (web.get_width(), web.get_height()) == (1280, 720)
        a, b = native.get_data().cast("B"), web.get_data().cast("B")
        errors = [
            sum(abs(x - y) for x, y in zip(a[k::4], b[k::4])) / (1280 * 720)
            for k in (2, 1, 0)
        ]
        results[f"{browser}/{name}"] = [round(v, 3) for v in errors]
        assert max(errors) < limits[browser], f"{browser}/{name}: native/browser RGB error {errors}"
(ROOT / "test-results/render-parity.json").write_text(
    json.dumps(results, indent=2) + "\n"
)
print(f"{len(results)} native/browser captures match within the inspected browser rasterization tolerances.")

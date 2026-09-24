#!/usr/bin/env python3
"""Package unchanged native game modules and browser-ready original artwork."""

from pathlib import Path
import sys, json, hashlib, shutil, zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
import cairo
from omacontra.rendering import sprites
from omacontra.rendering.character_assets import CHARACTER_ASSETS

OUT = ROOT / "web/public/campaign"
if "--code-only" not in sys.argv and OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "images").mkdir(exist_ok=True)
files = [
    line.strip()
    for line in (ROOT / "release-assets.txt").read_text().splitlines()
    if line.strip() and not line.startswith("#")
]
images = (
    json.loads((OUT / "manifest.json").read_text())["images"]
    if "--code-only" in sys.argv
    else {}
)


def store(key, s):
    import io

    buffer = io.BytesIO()
    s.write_to_png(buffer)
    data = buffer.getvalue()
    name = "images/" + hashlib.sha256(data).hexdigest()[:20] + ".png"
    target = OUT / name
    if not target.exists():
        target.write_bytes(data)
    images[key] = {"file": name, "width": s.get_width(), "height": s.get_height()}


if "--code-only" not in sys.argv:
    for name in files:
        if not name.endswith(".png"):
            continue
        store(
            "raw/" + name,
            cairo.ImageSurface.create_from_png(str(ROOT / "assets" / name)),
        )
        store("atlas/" + name, sprites.atlas(name))
    for name in CHARACTER_ASSETS:
        store("atlas/" + name, sprites.atlas(name))
    # Pixel-derived effects are prepared by their actual native code, once at build
    # time. There is no expensive image readback or chroma-key pass in the browser.
    from omacontra.stages.highway.chase_environment import CoastEnvironment

    coast = CoastEnvironment(
        cairo.ImageSurface.create_from_png(str(ROOT / "assets/quattro-coast.png"))
    )
    for i, s in enumerate(coast.cloud_banks):
        store(f"prepared/cloud-{i}", s)
    from omacontra.stages.space.orbit_effects import atmosphere

    store("prepared/atmosphere", atmosphere())
audio = {}
for name in files:
    if name.startswith("audio/"):
        dest = OUT / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / "assets" / name, dest)
        if name.endswith((".wav", ".opus")):
            audio[name] = name
# Package data consumed directly by Python, alongside unmodified game modules.
with zipfile.ZipFile(OUT / "game.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for path in sorted((ROOT / "src/omacontra").rglob("*.py")):
        z.write(path, "src/" + str(path.relative_to(ROOT / "src")))
    for path in sorted((ROOT / "web/runtime").glob("*.py")):
        z.write(path, "runtime/" + path.name)
    for name in files:
        if name.endswith((".json", ".ttframes")):
            z.write(ROOT / "assets" / name, "assets/" + name)
    # exists() checks are used for optional assets/variant sounds. Real image and
    # sound bytes are fetched lazily by the browser, not copied into Python RAM.
    for name in files:
        if name.endswith((".png", ".wav", ".opus")):
            z.writestr("assets/" + name, b"")
    z.writestr("images.json", json.dumps(images, separators=(",", ":")))
shutil.copytree(ROOT / "web/licenses", OUT / "credits/browser", dirs_exist_ok=True)
shutil.copytree(ROOT / "THIRD_PARTY", OUT / "credits/THIRD_PARTY", dirs_exist_ok=True)
shutil.copy2(ROOT / "LICENSE", OUT / "credits/LICENSE.txt")
manifest = {
    "images": images,
    "audio": audio,
    "sourceRevision": hashlib.sha256(
        b"".join(p.read_bytes() for p in sorted((ROOT / "src/omacontra").rglob("*.py")))
    ).hexdigest(),
}
(OUT / "manifest.json").write_text(json.dumps(manifest, separators=(",", ":")) + "\n")
# Self-host the pinned Python/WASM runtime: no CDN needed during play.
pkg = ROOT / "web/node_modules/pyodide"
runtime = OUT / "python"
runtime.mkdir(exist_ok=True)
for name in (
    "pyodide.mjs",
    "pyodide.asm.mjs",
    "pyodide.asm.wasm",
    "python_stdlib.zip",
    "pyodide-lock.json",
):
    shutil.copy2(pkg / name, runtime / name)
print(
    f"Campaign: {len(images)} image mappings; {len(audio)} audio files; unchanged Python source packaged."
)

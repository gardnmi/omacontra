#!/usr/bin/env python3
"""Verify the full browser package uses the current desktop source and assets."""

from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "web/public/campaign"
manifest = json.loads((OUT / "manifest.json").read_text())
paths = sorted((ROOT / "src/omacontra").rglob("*.py"))
expected = hashlib.sha256(b"".join(p.read_bytes() for p in paths)).hexdigest()
assert manifest["sourceRevision"] == expected, (
    "Rebuild browser assets after changing desktop code."
)
with zipfile.ZipFile(OUT / "game.zip") as archive:
    for path in paths:
        name = "src/" + str(path.relative_to(ROOT / "src"))
        assert archive.read(name) == path.read_bytes(), name
    for name in ("beams", "rings", "blackhole"):
        path = f"assets/screensaver/{name}.ttframes"
        assert archive.read(path) == (ROOT / path).read_bytes(), path
for name, entry in manifest["images"].items():
    path = OUT / entry["file"]
    assert path.is_file() and entry["width"] > 0 and entry["height"] > 0, name
    assert hashlib.sha256(path.read_bytes()).hexdigest().startswith(path.stem), name
for name, path in manifest["audio"].items():
    assert (OUT / path).read_bytes() == (ROOT / "assets" / name).read_bytes(), name
assert (
    json.loads((OUT / "python/pyodide-lock.json").read_text())["info"]["python"]
    == "3.14.2"
)
for name in (
    "pyodide-LICENSE.txt",
    "python-LICENSE.txt",
    "emscripten-LICENSE.txt",
    "README.md",
):
    assert (OUT / "credits/browser" / name).is_file(), name
print(
    f"Full campaign verified: {len(paths)} unchanged Python modules, {len(manifest['images'])} image mappings, {len(manifest['audio'])} original recordings, three original screensavers."
)

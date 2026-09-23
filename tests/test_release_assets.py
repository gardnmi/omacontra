"""Catch omitted runtime sprites, soundtrack entries, masks and attribution."""
import ast
from pathlib import Path
import tempfile
import unittest

from release_assets import asset_paths
from omacontra.rendering.character_assets import CHARACTER_ASSETS, ALPHA_MATTES
from omacontra.audio.intro_music import GAME_TRACKS, TRACK, FINALE_TRACK, START_SOUND, UNLOCK_SOUND
from omacontra.stages.space.screensaver_art import EFFECTS

ROOT = Path(__file__).resolve().parents[1]


class ReleaseAssetsTests(unittest.TestCase):
    def test_runtime_art_and_its_transparency_masks_are_included(self):
        assets = set(asset_paths(ROOT))
        for path in (ROOT / 'src/omacontra').rglob('*.py'):
            # These contain decoding rules for both current and archived artwork.
            if path.name in ('sprites.py', 'character_assets.py'):
                continue
            for node in ast.walk(ast.parse(path.read_text())):
                if isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value.endswith('.png'):
                    name = node.value
                    with self.subTest(module=path.name, asset=name):
                        self.assertIn(CHARACTER_ASSETS.get(name, name), assets)
                        if name in ALPHA_MATTES:
                            self.assertIn(ALPHA_MATTES[name], assets)

    def test_all_music_and_screensavers_and_credits_are_included(self):
        assets = set(asset_paths(ROOT))
        for track in (*GAME_TRACKS, TRACK, FINALE_TRACK, TRACK.parent/'the-descent.mp3', START_SOUND, UNLOCK_SOUND):
            self.assertIn('audio/' + track.name, assets)
        for effect in EFFECTS:
            self.assertIn(f'screensaver/{effect}.ttframes', assets)
        for path in (ROOT/'assets').rglob('*'):
            if path.is_file() and (path.suffix in ('.md', '.txt') or path.name.startswith('LICENSE')):
                self.assertIn(path.relative_to(ROOT/'assets').as_posix(), assets)
        self.assertIn('audio/finale/loops/shield.wav', assets)

    def test_development_assets_do_not_ship(self):
        assets = set(asset_paths(ROOT))
        self.assertFalse(any(name.startswith(('reference/', 'audio/foundry/')) for name in assets))
        self.assertFalse(any(name.startswith('audio/sources/') and Path(name).suffix in ('.wav','.ogg','.flac') for name in assets))
        for old in ('dhh-run-carry-v2.png', 'foundry-dragon.png', 'audio/reaper-quattro-lets-go-nerds.mp3'):
            self.assertNotIn(old, assets)
            if old.endswith('.png'):
                self.assertFalse((ROOT/'assets'/old).exists())

    def test_manifest_rejects_missing_and_unsafe_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root/'assets').mkdir()
            (root/'outside').write_text('private')
            for name in ('../outside', '/etc/passwd', 'missing.png'):
                (root/'release-assets.txt').write_text(name+'\n')
                with self.subTest(name=name), self.assertRaises(ValueError):
                    asset_paths(root)

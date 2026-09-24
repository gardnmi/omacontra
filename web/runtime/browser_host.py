"""Browser adapters around the unmodified BossApp/campaign implementation."""

import sys, types, json, time, os, gc
from pathlib import Path
from functools import lru_cache
import cairo

AUDIO = []
MUSIC = []
PROFILE = None
os.environ["XDG_CONFIG_HOME"] = "/profile"
cairo.IMAGES = json.loads(Path("/game/images.json").read_text())
# These imports only provide desktop host names; no GTK or compositor is run.
gi = types.ModuleType("gi")
gi.require_version = lambda *a: None
repository = types.ModuleType("gi.repository")
repository.Gdk = types.SimpleNamespace(
    keyval_name=lambda key: key,
    EventType=types.SimpleNamespace(BUTTON_PRESS=1, BUTTON_RELEASE=2),
)
repository.Gtk = types.SimpleNamespace()
repository.GLib = types.SimpleNamespace()
repository.GLibUnix = types.SimpleNamespace()
gi.repository = repository
sys.modules["gi"] = gi
sys.modules["gi.repository"] = repository
platform = types.ModuleType("omacontra.desktop")
platform.Hyprland = lambda: None
sys.modules["omacontra.desktop"] = platform

from omacontra.rendering import sprites


@lru_cache(maxsize=16)
def atlas(name):
    return cairo.ImageSurface.from_asset("atlas/" + name)


sprites.atlas = atlas


# One command per sprite preserves native crop/flip/nearest sampling without
# allocating a Python command for each save/translate/clip/scale operation.
def sprite_draw(c, sheet, frame, x, y, w, h, flip=False, alpha=1):
    import math

    if (
        not all(math.isfinite(v) for v in (*frame, x, y, w, h, alpha))
        or min(w, h, frame[2], frame[3]) <= 0
        or alpha <= 0
    ):
        return
    c.emit("blit", atlas(sheet).id, list(frame), x, y, w, h, flip, alpha)
    c.path_bounds = None


sprites.draw = sprite_draw
from omacontra.stages.highway.chase_environment import CoastEnvironment
from omacontra.rendering import combat_fx as fx


def coast_init(self, road):
    self.scene = cairo.ImageSurface(cairo.FORMAT_RGB24, 1280, 720)
    sprites.paint_background(cairo.Context(self.scene), road, 0, 0, 1280, 720)
    self.cloud_banks = [
        cairo.ImageSurface.from_asset(f"prepared/cloud-{i}") for i in range(2)
    ]
    self.mist = cairo.ImageSurface(cairo.FORMAT_ARGB32, 128, 128)
    fx.smoke(cairo.Context(self.mist), 64, 64, 124, 0, alpha=1, steam=True)
    self.wisp = cairo.ImageSurface(cairo.FORMAT_ARGB32, 128, 128)
    c = cairo.Context(self.wisp)
    c.set_source_rgba(0.54, 0.10, 0.36, 1)
    c.mask_surface(self.mist)


CoastEnvironment.__init__ = coast_init
from omacontra.stages.space import orbit_effects

orbit_effects.atmosphere = lru_cache(maxsize=1)(
    lambda: cairo.ImageSurface.from_asset("prepared/atmosphere")
)

from omacontra.audio import intro_music

OriginalMusic = intro_music.IntroMusic


class BrowserMusic(OriginalMusic):
    next_id = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = BrowserMusic.next_id
        BrowserMusic.next_id += 1
        self.active = False
        self.paused = False
        self.generation = 0
        self.sent = None

    def command(self, *args):
        pass

    def emit(self):
        tracks = [
            str(p).split("/assets/")[-1]
            for p in (
                (intro_music.START_SOUND,)
                if self.start_effect
                else self.playlist or (self.track,)
            )
        ]
        data = {
            "id": self.id,
            "tracks": tracks,
            "active": self.active,
            "paused": self.paused,
            "volume": self.volume / 100,
            "effect": self.start_effect or all(p.endswith(".wav") for p in tracks),
            "loop": not self.start_effect and "--loop-file=no" not in self.extra_args,
            "generation": self.generation,
        }
        signature = json.dumps(data, sort_keys=True)
        if signature != self.sent:
            MUSIC.append(data)
            self.sent = signature

    def update(self, active, paused=False):
        if not active:
            self.stop()
            return
        self.active = True
        self.paused = paused
        self.emit()

    def set_volume(self, value):
        self.volume = max(0, min(150, value))
        self.emit()

    def play_start(self):
        if self.start_effect:
            return
        self.start_effect = True
        self.generation += 1
        self.active = True
        self.paused = False
        self.emit()

    def restart(self):
        self.start_effect = False
        self.generation += 1
        self.emit()

    def stop(self):
        if self.active:
            self.generation += 1
        self.active = False
        self.emit()


intro_music.IntroMusic = BrowserMusic

from omacontra.audio.reaper_audio import PRIORITY as REAPER_PRIORITY, EFFECT_GAIN
from omacontra.audio.chase_audio import PRIORITY as CHASE_PRIORITY
from omacontra.audio.tide_audio import PRIORITY as TIDE_PRIORITY
from omacontra.audio.foundry_audio import FoundryEffects
from omacontra.audio.finale_audio import FinaleEffects


class Bank:
    def __init__(self, name, priority=None, scope=None):
        self.name = name
        self.scope = scope or name
        self.priority = priority or {}
        self.gain = 1.1
        self.takes = {}
        self.voices = []

    def trigger(self, name):
        variant = self.takes.get(name, 0) % 3
        self.takes[name] = variant + 1
        root = f"audio/{self.name}/"
        path = root + (f"variants/{name}-{variant}" if variant else name) + ".wav"
        if not (Path("/game/assets") / path).exists():
            path = root + name + ".wav"
        if not (Path("/game/assets") / path).exists():
            raise FileNotFoundError(path)
        AUDIO.append(
            {
                "kind": "effect",
                "path": path,
                "name": name,
                "scope": self.scope,
                "gain": self.gain * EFFECT_GAIN,
                "priority": self.priority.get(name, 1),
            }
        )

    def clear(self):
        AUDIO.append({"kind": "clear", "scope": self.scope})


class BrowserWeaponAudio:
    def __init__(self):
        self.banks = {
            "reaper": Bank("reaper", REAPER_PRIORITY),
            "chase": Bank("chase", CHASE_PRIORITY),
            "tide": Bank("tide", TIDE_PRIORITY),
            "foundry": Bank("wyrm", FoundryEffects().priority),
            "finale": Bank("finale", FinaleEffects().priority),
            "continue": Bank("continue", {"tick": 1, "accept": 3, "death_blow": 4}),
        }
        self.ui_effects = Bank("continue", {"accept": 3}, "ui")
        self.menu_effects = Bank("menu", {"confirm": 3, "complete": 4}, "menu")
        self.owner = None
        self.effects = self.banks["reaper"]
        self.contact = False
        self.enabled = False

    def set_volumes(self, effects):
        for bank in (*self.banks.values(), self.ui_effects, self.menu_effects):
            bank.gain = 1.1 * max(0, min(1.5, effects))
        AUDIO.append(
            {"kind": "volume", "gain": 1.1 * max(0, min(1.5, effects)) * EFFECT_GAIN}
        )

    def update(self, f, enabled, effects_enabled=False):
        if f is not self.owner:
            self.effects.clear()
            self.owner = f
            self.effects = self.banks[getattr(f, "sound_bank", "reaper")]
        events = getattr(f, "sfx_events", [])
        pending = list(events)
        events.clear()
        contact = bool(
            effects_enabled
            and getattr(f, "sound_bank", "") == "finale"
            and f.state == "play"
            and f.beam_hit
            and getattr(f, "laser_contact", None) == "shield"
        )
        if contact != self.contact:
            self.contact = contact
            AUDIO.append(
                {
                    "kind": "contact",
                    "enabled": contact,
                    "gain": self.effects.gain * EFFECT_GAIN,
                }
            )
        if effects_enabled:
            for name in pending:
                self.effects.trigger(name)
        elif self.enabled:
            self.effects.clear()
        self.enabled = effects_enabled

    def update_menu(self, visible=True):
        if self.enabled:
            self.effects.clear()
            self.enabled = False
        if self.contact:
            self.contact = False
            AUDIO.append({"kind": "contact", "enabled": False, "gain": 0})

    def silence(self):
        for bank in (*self.banks.values(), self.ui_effects, self.menu_effects):
            bank.clear()
        self.contact = False
        self.enabled = False
        AUDIO.append({"kind": "contact", "enabled": False, "gain": 0})

    def close(self):
        self.silence()


weapon = types.ModuleType("omacontra.audio.weapon_audio")
weapon.WeaponAudio = BrowserWeaponAudio
weapon.SFX_BOOST = 1.1
sys.modules[weapon.__name__] = weapon

from omacontra.ui import release_ui

# Use a quieter browser default; Profile still restores saved user settings.
release_ui.DEFAULTS["music"] = 60
OriginalProfile = release_ui.Profile


class BrowserProfile(OriginalProfile):
    def save(self):
        global PROFILE
        super().save()
        if not self.error:
            PROFILE = self.path.read_text()


release_ui.Profile = BrowserProfile
from omacontra.boss_app import BossApp
from omacontra.stages.reaper.combat import W, H


class Area:
    def get_allocated_width(self):
        return W

    def get_allocated_height(self):
        return H

    def queue_draw(self):
        pass


class BrowserApp(BossApp):
    def setup(self, smoke):
        self.placed = True
        self.visible = True
        self.fullscreen = True
        self.area = Area()

    def close(self, *args):
        self.closed = True
        self.weapon_audio.close()
        self.music.stop()
        self.game_music.stop()
        self.unlock_sound.stop()
        self.frontend.jukebox.stop()
        return False


app = None
screen = None
last_level = 1


def boot(profile=None, level=0):
    global app, screen, last_level
    if profile:
        path = Path("/profile/omacontra/profile.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(profile)
    app = BrowserApp(intro=not level, level=level or 1)
    screen = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    last_level = app.level
    return render()


def event(data):
    kind = data["type"]
    if kind in ("down", "up"):
        e = types.SimpleNamespace(hardware_keycode=data["code"], keyval=data["key"])
        if kind == "down":
            app.key(None, e)
        else:
            app.release(None, e)
    elif kind == "motion":
        app.motion(None, types.SimpleNamespace(x=data["x"], y=data["y"]))
    elif kind in ("press", "release"):
        app.button(
            None,
            types.SimpleNamespace(
                x=data["x"],
                y=data["y"],
                button=data.get("button", 1),
                type=1 if kind == "press" else 2,
            ),
        )
    elif kind == "blur":
        app.unfocus()
        app.visible = False
    elif kind == "focus":
        app.visible = True
        app.last = time.monotonic()
    elif kind == "storage-error":
        app.frontend.profile.error = "Could not save preferences on this device."
    elif kind == "restart-session":
        app.closed = False
        app.frontend.page = None
        app.return_to_title()


def tick(dt, events):
    global last_level
    # A tap shorter than one browser frame must still reach the native step.
    # Menu/story key events stay immediate, including repeated secret-code keys.
    pressed = set()
    deferred = {}
    for e in events:
        code = e.get("code", "mouse")
        if e["type"] in ("down", "press"):
            if code in deferred:
                event(deferred.pop(code))
            pressed.add(code)
        playing = not app.intro and not app.frontend.page and app.f.state == "play"
        if playing and e["type"] in ("up", "release") and code in pressed:
            deferred[code] = e
        else:
            event(e)
    if not app.closed:
        app.last = time.monotonic() - min(0.04, max(0, dt))
        app.tick()
    for e in deferred.values():
        event(e)
    if app.level != last_level:
        # The native host keeps old renderer instances for convenience. Browser
        # memory is bounded by the active stage; on revisit they reconstruct.
        for level, name in (
            (2, "chase_renderer"),
            (3, "tide_renderer"),
            (4, "foundry_renderer"),
            (5, "finale_renderer"),
        ):
            if level != app.level:
                setattr(app, name, None)
        sprites.atlas.cache_clear()
        gc.collect()
        last_level = app.level
    return render()


def render():
    global PROFILE
    context = cairo.Context(screen)
    app.draw(app.area, context)
    del context
    result = {
        "draw": cairo.flush(),
        "surface": screen.id,
        "audio": AUDIO[:],
        "music": MUSIC[:],
        "profile": PROFILE,
        "status": status(),
    }
    AUDIO.clear()
    MUSIC.clear()
    PROFILE = None
    return json.dumps(result, separators=(",", ":"), allow_nan=False)


def status():
    f = app.f
    front = app.frontend
    return {
        "level": app.level,
        "state": f.state,
        "intro": app.intro.beat.kind if app.intro else None,
        "journey": bool(app.intro and app.intro.journey),
        "menu": front.page,
        "selection": front.selection,
        "paused": app.paused,
        "closed": app.closed,
        "hp": f.hp,
        "x": f.x,
        "y": f.y,
        "clock": f.clock,
        "bossHp": f.boss_hp,
        "phase": getattr(f, "phase", 1),
        "unlimited": app.unlimited_lives,
        "hardcore": front.record.hardcore,
        "losses": front.record.losses,
        "continues": front.record.continues,
        "cleared": sorted(front.record.cleared),
        "continue": app.continue_screen.state if app.continue_screen else None,
        "screensaver": getattr(f, "screensaver_age", 0),
        "stage": getattr(f, "stage", 0),
        "damage": getattr(f, "damage_taken", 0),
        "shots": len(f.shots),
        "dash": getattr(f, "dash_used", False),
        "settings": front.profile.settings,
        "category": front.record.category,
        "cinema": next(
            (
                name
                for name in ("chase_cinema", "journey_cinema", "foundry_intro")
                if getattr(app, name, None)
            ),
            None,
        ),
    }


def debug(action, values=None):
    """Only the development worker routes this command. No production shortcut."""
    values = values or {}
    if action == "script":
        exec(values["code"], globals())
    elif action == "stage":
        app.intro = None
        app.level = values["level"]
        app.guardian_practice = False
        app.frontend.page = None
        app.frontend.new_run(app.level, True)
        app.reset_encounter()
        if values.get("skip"):
            app.chase_cinema = app.journey_cinema = app.foundry_intro = None
            if app.level == 5:
                app.f.skip()
    elif action == "set":
        for key, value in values.items():
            setattr(app.f, key, value)
    elif action == "intro":
        app.return_to_title()
        app.intro.index = values.get("index", 0)
        app.intro.age = values.get("age", 0)
        app.frontend.page = None
    elif action == "menu":
        app.frontend.open(values["page"])
    elif action == "continue":
        from omacontra.ui.continue_screen import ContinueScreen, ContinueRenderer

        app.continue_screen = ContinueScreen(hardcore=values.get("hardcore", False))
        app.continue_renderer = ContinueRenderer()
    elif action == "guardians":
        app.f.advance_guardian()
        app.journey_cinema = None
    elif action == "advance":
        app.advance_campaign()
    elif action == "fastforward":
        for _ in range(values.get("frames", 1)):
            app.last = time.monotonic() - 1 / 60
            app.tick()
    return render()

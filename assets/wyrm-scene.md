# Mist Gate assets

Generated from the user-provided black dragon reference with imagegen, 2026-09-21.

- `wyrm-head.png`: transparent 1254 square head/neck portrait. Mouth anchor (627,915); eye anchors (497,605), (778,605). Runtime neck fade blends into animated mist.
- `wyrm-mist-arena.png`: 1536×1024 pale cloud/mountain launch terrace. The existing shuttle is composited separately.
- `wyrm-stone-platform.png`: 1536×1024 transparent stone slab; runtime frame (38,399,1460,360) places the actual top at the collision plane.
- `wyrm-storm-wisp.png`: 1536×1024 transparent vapor/lightning ribbon; cached frame (0,250,1536,550).

`wyrm_scene.py` owns the shared sway/tilt transform, glow anchors, cached fog and branched lightning. Cosmetic lightning never enters the hazard collection. The dark rising storm reuses the previous lava collision boundary without changing platform safety.

Stage 4 is composed into a reusable 1280×720 `FrameBuffer` before the host scales
the completed image with nearest-neighbor sampling. This covers the reveal,
combat, disarm and car rescue. Fog and portrait compositing therefore stay at
game resolution on larger displays; simulation, aiming and collision coordinates
are unchanged. Each frame gets a fresh Cairo context to isolate camera transforms
and clipping. In a local 2560×1440 CPU rendering comparison (60 warmed frames),
normal combat dropped from 32.6 to 4.6 ms and a storm/breath scene from 52.0 to
12.6 ms, including the final upscale but excluding desktop presentation.

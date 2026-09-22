# Tidebreaker overstock trolley

Asset: `tide-overstock-cart.png`. Generated using the built-in imagegen tool.
Rendered at 92 × 62 gameplay pixels, cached once at double resolution. Native alpha is retained. The trolley retains the existing collision dimensions.

## Generation prompt

Create one production game sprite on genuinely transparent background: a battered low wooden shipping crate packed with unsold shrinkwrapped AAA video game cases on a small industrial wheeled cargo trolley. High quality detailed pixel art matching a gritty 16-bit arcade action game, richly shaded weathered timber, riveted blue-gray steel corner braces, wet highlights, rusty bolts, little rubber caster wheels. Side-on view with only a slight view of top and right face, wide low silhouette, width to height about 1.5, compact jumpable obstacle. Readable cream shipping placard on front says 'AAA OVERSTOCK', small red clearance sticker. Several colorful sealed game cases visible above crate rim. Entire object isolated, centered, tightly framed with small transparent margin. No scene, no floor, no background, no surrounding shadow or haze. Crisp pixel clusters rather than smooth illustration. Output a single sprite, not a sheet.

## Refinements

Replace recognizable games and console branding with fictional generic sci-fi/fantasy game case illustrations without logos. Keep identical pixel art detail and silhouette.

Final extraction prompt: Background extraction for a game sprite. The previous attempt incorrectly retained the blue/brown/black background. REMOVE that entire colored background around this trolley, including the colored haze. Output an RGBA PNG with alpha=0 everywhere outside the object. Keep only crate, games, metal frame and wheels. No background gradients, no background black, no cast shadow. The transparent area must be fully clear. Preserve the exact object.

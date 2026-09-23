# Harbor cargo trolley redesign

Generated with the built-in image-generation tool, September 2026. References:
the previous `tide-overstock-cart.png` (retained in Git history) and the shipped
`tidebreaker-arena.png`. The second generation also referenced the new wood cart.
No stock artwork or third-party game-case covers were inserted.

Runtime sprites: `tide-dock-wood.png` and `tide-dock-steel.png`.
The full generated originals remain in the local image-generation output directory;
only the normalized 368 × 216 transparent runtime textures ship. The normalization
script `tools/build_dock_cargo.py` crops transparent padding and resamples using
Cairo; it does not alter the painted subjects. Display footprint is 92 × 54 pixels.
The same collision and motion simulation is used for both variants.

## Wood prompt (built-in tool)

Use case: precise-object-edit. Create a replacement GAME SPRITE for the wooden cargo trolley from reference image 1. Reference image 2 is the game's actual storm harbor: match the dark industrial deck's detailed crisp pixel-art rendering, cool blue-gray metal, aged gunmetal rivets, salt stains and pale wet edge highlights. Redesign the trolley as heavy battered dock cargo: dark desaturated weathered wood, thick riveted steel framing, dented reinforced corners, mostly CLOSED lid, one small broken opening at the upper left revealing only THREE muted blue game-case spines. Faded off-white front stencil exactly 'AAA' over 'OVERSTOCK', one small worn red clearance sticker. Small heavy industrial wheels partly tucked under the base, clearly visible straight ground contact. Proportions wide and squat, width to total height about 1.7:1, same easy-to-jump silhouette as reference 1, horizontal bottom wheel baseline. Side-scrolling game view: mostly front with a shallow right side visible, no exaggerated perspective. Cool storm lighting, restrained rusty orange accents, high material detail using deliberate visible pixel clusters rather than smooth illustration. The object must read at just 92 by 58 gameplay pixels. Single complete isolated trolley, entire object including wheels fits with minimal 5% padding on an otherwise truly TRANSPARENT alpha background. No environment, no floor, no cast shadow, no ropes, no loose separate props, no colored background, no glow, no checkerboard baked into image. Make the sprite itself production quality like the attached deck.

## Steel prompt (built-in tool)

Use case: precise-object-edit. Make a complementary SECOND production-quality pixel-art trolley sprite for this game's storm harbor. Image 1 is the wooden first trolley: preserve its approximately 1.7:1 wide squat silhouette, overall size, small tucked-under industrial casters, shallow three-quarter side-scroller view and grounded weight. Replace the WOOD with a dented STEEL dock shipping bin. Image 2 defines the rendering quality, palette, material weathering and lighting: dark gunmetal industrial deck, cool blue-gray wet reflections, strong readable pixel clusters. Thick ribbed metal panels with dents, chipped charcoal paint, salt encrustation, rust around rivets, small diagonal faded hazard stripe patches on corners. Mostly shut heavy steel lid, one small opening near upper left with only TWO dull purple and blue sealed game spines visible. Front has faded off-white painted stencil exactly 'AAA' and 'OVERSTOCK' beneath, plus a small torn red clearance label. Slightly chamfered upper corners make this silhouette distinct from the wood crate, but same height for jumping over. Solid black rubber small wheels with aged steel hubs, clearly readable and tucked under the heavy frame. Cool desaturated palette, extremely restrained rusty orange highlights. Single complete isolated sprite on genuinely TRANSPARENT alpha background. Entire object with wheels visible, minimal padding. No floor, no cast shadow, no scenery, no ropes, no gradients or glow outside silhouette, no baked checkerboard, no extra objects, no photorealism. Must remain legible at just 92 by 58 gameplay pixels. Match the reference game's detailed gritty pixel-art metalwork.

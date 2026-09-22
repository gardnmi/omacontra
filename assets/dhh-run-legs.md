# DHH running legs

Generated with built-in imagegen, 2026-09-22. Reference: `dhh-modular-body.png`.
Output: `dhh-run-legs.png`, RGBA 1536×1024, six frames in reading order.
Runtime crops align the pelvis and soles, with a small upper-body bounce shared
by the arms and muzzle. Backward movement reverses the cycle. No gameplay
speed, jump arc, slide duration, or collision dimensions changed.

Movement reference inspected: [Contra NES Bill & Lance sprite sheet](https://www.spriters-resource.com/nes/contra/asset/90325/).
Contra art is reference only; no Contra sprites are included in the game.

## Generation prompt

Create a production 6-frame SIDE VIEW running LEGS ONLY sprite sheet for the reference character. Genuine transparent background, exactly 1536x1024, strict THREE columns by TWO rows, each cell 512x512. Show ONLY waist/belt down: olive military cargo pants, knee pads, brown-red combat boots, chunky shaded pixel-art texture exactly matching reference. No head, torso, arms, weapon, text, borders or ground. Each pelvis center anchored at cell x256 y70, belt cropped horizontally at y60, planted boot soles at y465. All six poses face RIGHT and are same size, hip width about120pixels, legs totalheight400pixels. Six DISTINCT consecutive natural run-cycle poses in reading order: 1 front leg stretches right heel strike, back leg extends left; 2 down/compression front knee bends weight on front foot trailing leg lifts; 3 passing pose legs cross beneath hips with lifted rear knee; 4 opposite foot reaches forward right and other leg extends back left; 5 opposite down/compression; 6 opposite passing pose. Anatomically correct two legs only per cell. Distinguish near leg brighter and far leg darker so each half cycle reads as opposite legs. Boots never touch cell border. Consistent pixel scale and proportions; realistic muscular action hero rather than cartoon. Transparent negative space separates all six cells.

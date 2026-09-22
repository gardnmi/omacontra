"""Canonical character assets, matched to assets/reference/canonical-characters.png.

Versioned files preserve the previous artwork for review. Route shared source
names here so gameplay and cinematic users cannot silently select old models.
"""
CHARACTER_ASSETS = {
    'dhh-portal-reach.png': 'dhh-portal-reach-canonical.png',
    'dhh-body.png': 'dhh-body-canonical.png',
    'quattro-car.png': 'quattro-car-canonical.png',
    'quattro-rally-cinema.png': 'quattro-rally-cinema-canonical.png',
    'journey-cinema.png': 'journey-cinema-canonical.png',
    'dhh-space-walk.png': 'dhh-space-walk-canonical.png',
    'finale-car-rear.png': 'finale-car-rear-canonical.png',
    'foundry-rescue.png': 'foundry-rescue-canonical.png',
}

ALPHA_MATTES = {
    **{k:k for k in CHARACTER_ASSETS if k != "dhh-body.png"},
    "finale-people-canonical.png": "finale-atlas.png",
}

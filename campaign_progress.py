"""Campaign health rewards, derived from the chapter so retries never stack them."""
BASE_HEALTH=5

def prepare_encounter(fight,level,remaining=None):
    if not 1<=level<=5:raise ValueError('Campaign level must be between 1 and 5')
    fight.max_hp=BASE_HEALTH+level-1
    # Fresh starts/continues refill; advancing carries survivors plus one award.
    fight.hp=fight.max_hp if remaining is None else min(fight.max_hp,max(0,remaining)+1)
    return fight

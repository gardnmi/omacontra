from sound_palette import PALETTE,build_bank,layer,ROOT

PALETTE['continue']={
    'tick':(.10,-42,[layer('laser',speed=1.6,length=.10)]),
    'accept':(1.1,-31,[layer('field',speed=1.8,length=.7),layer('laser',at=.45,gain=.3,speed=1.6,length=.4)]),
    'death_blow':(2.1,-27,[layer('shot',speed=.65,length=.5),layer('low',at=.035,gain=.9,speed=.65)])}
if __name__=='__main__':
    (ROOT/'continue').mkdir(exist_ok=True);build_bank('continue')

"""Add restrained action/readiness cues without rebuilding existing sound banks."""
from sound_palette import PALETTE, ROOT, RATE, build_bank, layer
import array
import math
import wave


def ready(bank, name, notes):
    """Short, soft two-note arcade confirmation, never a repeating alarm."""
    duration=.28
    values=[]
    for i in range(round(duration*RATE)):
        t=i/RATE
        note=int(t>=.105)
        age=t-(.105 if note else 0)
        envelope=min(1,age/.009)*math.exp(-age*28)*min(1,max(0,(duration-t)/.025))
        phase=math.tau*notes[note]*age
        values.append((math.sin(phase)+.10*math.sin(phase*2))*envelope)
    gain=32767*10**(-40/20)/max(map(abs,values))
    with wave.open(str(ROOT/bank/(name+'.wav')),'wb') as out:
        out.setparams((1,2,RATE,0,'NONE','not compressed'))
        out.writeframes(array.array('h',(round(v*gain) for v in values)).tobytes())


def main():
    for bank in ('reaper','tide','wyrm'):
        PALETTE[bank]={'double_jump':(.22,-39,[layer('thruster',speed=1.6,length=.17),layer('field',gain=.15,speed=1.8,length=.22)])}
        build_bank(bank)
    PALETTE['tide']={'guardian_arrival':(.85,-36,[layer('field',speed=.72,length=.8),layer('thruster',gain=.22,speed=.8,length=.55)])}
    build_bank('tide')
    PALETTE['wyrm']={'ultimate_charge':(2.7,-34,[layer('field',speed=.48,length=2.6),layer('large_laser',at=.7,gain=.25,speed=.55,length=1.6)])}
    build_bank('wyrm')
    ready('chase','boost_ready',(330,495))
    ready('finale','thruster_ready',(440,660))


if __name__=='__main__':main()

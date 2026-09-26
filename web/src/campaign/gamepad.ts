/** Browser input only; binding, dead zones and menu handling live in Python. */
const names = ['a','b','x','y','lb','rb','lt','rt','view','menu','ls','rs','up','down','left','right'];
export type PadState = { connected: true; buttons: string[]; axes: number[] };
export function gameSirRaw(p: Gamepad): boolean {
  // Linux HID layout verified against SDL's mapping for 3537:1082 (G7 SE).
  // Never apply a guessed Xbox layout to an arbitrary unmapped controller.
  return p.mapping !== 'standard' &&
    (/3537.*1082/i.test(p.id) || /gamesir[- ]?g7\s*se/i.test(p.id)) &&
    p.axes.length >= 6 && p.buttons.length >= 12;
}
export function readGamepad(pads: ArrayLike<Gamepad | null>, preferred?: number): {index: number; state: PadState} | null {
  const list = Array.from(pads);
  const supported=(p: Gamepad | null): p is Gamepad => !!p?.connected && (p.mapping === 'standard' || gameSirRaw(p));
  const pad = list.find(p => supported(p) && p.index === preferred) ?? list.find(supported);
  if (!pad) return null;
  const pressed=(i:number)=>!!pad.buttons[i]?.pressed || (pad.buttons[i]?.value ?? 0) > .5;
  const axis=(i:number)=>Number.isFinite(pad.axes[i]) ? pad.axes[i] : 0;
  let buttons:string[];
  if (gameSirRaw(pad)) {
    const map:Record<string,number>={a:0,b:1,x:3,y:4,lb:6,rb:7,view:10,menu:11,ls:13,rs:14};
    buttons=Object.entries(map).filter(([,i])=>pressed(i)).map(([name])=>name);
    if(axis(4)>0)buttons.push('rt');
    if(axis(5)>0)buttons.push('lt');
    if(axis(6)<-.5)buttons.push('left');
    if(axis(6)>.5)buttons.push('right');
    if(axis(7)<-.5)buttons.push('up');
    if(axis(7)>.5)buttons.push('down');
  } else buttons=names.filter((_,i)=>pressed(i));
  return {index: pad.index, state: {connected: true, buttons,
    axes: Array.from({length:4}, (_,i) => axis(i))}};
}

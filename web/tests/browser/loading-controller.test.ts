import {test,expect} from '@playwright/test';
for(const button of [0,9]) {
 test(`loading screen queues controller ${button===0?'A':'Menu'} without skipping intro`,async({page})=>{
  await page.addInitScript((button)=>{
   (window as any).__buttons=[button];
   Object.defineProperty(navigator,'getGamepads',{value:()=>[{
    index:0,id:'Test Xbox',mapping:'standard',connected:true,axes:[0,0,0,0],
    buttons:Array.from({length:16},(_,i)=>({pressed:(window as any).__buttons.includes(i),value:(window as any).__buttons.includes(i)?1:0}))
   }]});
  },button);
  await page.goto('/');
  await expect(page.locator('#gate')).toBeHidden({timeout:30000});
  const intro=()=>page.evaluate(()=>(window as any).__campaign?.status?.intro);
  await expect.poll(intro).toBe('story');
  await page.waitForTimeout(500);
  expect(await intro()).toBe('story');
  await page.evaluate(()=>{(window as any).__buttons=[]});
  await page.waitForTimeout(150);
  await page.evaluate(()=>{(window as any).__buttons=[0]});
  await expect.poll(intro).toBe('containment');
 });
}

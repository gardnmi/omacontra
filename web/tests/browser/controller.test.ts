import {test,expect,type Page} from '@playwright/test';
const state=(page:Page)=>page.evaluate(()=>(window as any).__campaign.status);
const debug=(page:Page,action:string,values:any={})=>page.evaluate(([a,v])=>(window as any).__campaign.debug(a,v),[action,values]);
async function pad(page:Page,buttons:number[]=[],axes=[0,0,0,0]) {
 await page.evaluate(({buttons,axes})=>{(window as any).__pad={index:0,id:'Test Xbox',mapping:'standard',connected:true,axes,buttons:Array.from({length:16},(_,i)=>({pressed:buttons.includes(i),value:buttons.includes(i)?1:0}))};},{buttons,axes});
 await page.waitForTimeout(110);
}
async function tap(page:Page,button:number) {await pad(page,[button]);await pad(page);}
test.beforeEach(async({page})=>{
 page.on('pageerror',e=>{throw e});
 await page.addInitScript(()=>{
   (window as any).__pad=null;
   Object.defineProperty(navigator,'getGamepads',{value:()=>[(window as any).__pad]});
 });
 await page.goto('/');await expect(page.locator('#play')).toBeVisible({timeout:30000});await page.locator('#play').click();
});
test('controller code, menus, held confirm, controls and deadzone',async({page})=>{
 for(const b of [12,12,13,13,14,15,14,15]) await tap(page,b);
 await expect.poll(async()=>(await state(page)).unlimited).toBe(true);
 await debug(page,'intro');
 // Use the actual cover index rather than depending on the number of intro beats.
 await debug(page,'script',{code:'app.intro.index=len(app.intro.beats)-1'});
 await tap(page,0);await expect.poll(async()=>(await state(page)).menu).toBe('mode');
 await pad(page,[0]);await page.waitForTimeout(650);
 expect((await state(page)).selection).toBe(0);
 await pad(page);
 await debug(page,'stage',{level:1,skip:true});
 await tap(page,9);await expect.poll(async()=>(await state(page)).menu).toBe('pause');
 await tap(page,13);await tap(page,0);
 await expect.poll(async()=>(await state(page)).menu).toBe('controls');
 await page.screenshot({path:'test-results/controller-controls.png'});
 await tap(page,1);await tap(page,13);await tap(page,0);
 await expect.poll(async()=>(await state(page)).menu).toBe('options');
 await tap(page,13);await tap(page,13);await tap(page,14);
 await expect.poll(async()=>(await state(page)).settings.deadzone).toBe(15);
 await page.screenshot({path:'test-results/controller-options.png'});
});
test('movement, dash, right-stick aiming in all five stages and disconnect',async({page})=>{
 test.setTimeout(90000);
 for(let level=1;level<=5;level++){
  await pad(page);await debug(page,'stage',{level,skip:true});
  await debug(page,'set',{invuln:999});
  const before=(await state(page)).x;
  await pad(page,[7],[1,0,1,-.5]);
  await expect.poll(async()=>(await state(page)).x).toBeGreaterThan(before);
  await expect.poll(async()=>(await state(page)).controllerAim).not.toBeNull();
  expect((await state(page)).inputDevice).toBe('controller');
  await pad(page);await tap(page,0);await tap(page,4);
  if(level===5){await pad(page,[7],[0,0,.7,-1]);await debug(page,'set',{invuln:0});await page.screenshot({path:'test-results/controller-space.png'});}
 }
 await page.evaluate(()=>{(window as any).__pad=null});
 await expect.poll(async()=>(await state(page)).menu).toBe('pause');
 expect((await state(page)).controllerAim).toBeNull();
});
test('focus loss releases held buttons and controller can accept continue',async({page})=>{
 await debug(page,'stage',{level:1,skip:true});await pad(page,[7],[1,0,0,0]);
 await page.evaluate(()=>window.dispatchEvent(new Event('blur')));
 await expect.poll(async()=>(await state(page)).menu).toBe('pause');
 await page.evaluate(()=>window.dispatchEvent(new Event('focus')));
 await pad(page);await tap(page,1);
 await expect.poll(async()=>(await state(page)).menu).toBeNull();
 await debug(page,'continue');await tap(page,0);
 await expect.poll(async()=>(await state(page)).continue).toBe('accepted');
});

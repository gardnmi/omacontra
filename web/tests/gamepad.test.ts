import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readGamepad} from '../src/campaign/gamepad';
const pad=(index=0,buttons:number[]=[],axes=[0,0,0,0]) => ({index,connected:true,mapping:'standard',axes,buttons:Array.from({length:16},(_,i)=>({pressed:buttons.includes(i),value:buttons.includes(i)?1:0}))} as unknown as Gamepad);
test('standard buttons and all four axes survive browser translation',()=>{
 const result=readGamepad([null,pad(1,[0,7,12],[.8,0,0,-1])]);
 assert.deepEqual(result,{index:1,state:{connected:true,buttons:['a','rt','up'],axes:[.8,0,0,-1]}});
});
test('disconnect and unsupported mappings do not invent input',()=>{
 assert.equal(readGamepad([]),null);
 assert.equal(readGamepad([{...pad(),mapping:''} as Gamepad]),null);
 assert.equal(readGamepad([{...pad(),connected:false}]),null);
});
test('retain chosen device and normalize missing axes',()=>{
 assert.equal(readGamepad([pad(0),pad(1)],1)?.index,1);
 assert.deepEqual(readGamepad([pad(0,[],[])])?.state.axes,[0,0,0,0]);
});

test('unmapped GameSir G7 SE uses verified Linux HID buttons, triggers and hats',()=>{
 const raw={...pad(0,[3,4,11],[.2,-.4,.8,-.5,1,-1,-1,1]),id:'3537-1082-GameSir-G7 SE Controller for Xbox',mapping:''} as Gamepad;
 const result=readGamepad([raw])!;
 assert.deepEqual(result.state.axes,[.2,-.4,.8,-.5]);
 assert.deepEqual(new Set(result.state.buttons),new Set(['x','y','menu','rt','left','down']));
});
test('raw GameSir neutral triggers never fire and unrelated pads remain unmapped',()=>{
 const raw={...pad(0,[],[0,0,0,0,-1,-1,0,0]),id:'GameSir-G7 SE Controller for Xbox',mapping:''} as Gamepad;
 assert.deepEqual(readGamepad([raw])?.state.buttons,[]);
 assert.equal(readGamepad([{...raw,id:'Unknown controller'}]),null);
});

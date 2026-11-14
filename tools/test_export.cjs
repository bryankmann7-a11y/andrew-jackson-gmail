#!/usr/bin/env node
/* Standalone export must include every required script and original records. */
"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const root=path.resolve(__dirname,".."),assets=path.join(root,"app/src/main/assets");
const html=fs.readFileSync(path.join(assets,"index.html"),"utf8");
const start=html.indexOf("async function downloadCompiledHTML(){");
const end=html.indexOf("\nfunction exportData(){",start);
assert.ok(start>0&&end>start,"Export function missing");
let artifact=null,toastText="";
const source=html.replace(/^<!doctype html>\s*/i,"");
const element={querySelector:()=>null,outerHTML:source};
const data=[{id:"test",from:"Andrew Jackson",to:"Test",date:"1800-01-01",modern:"</script><img src=x onerror=1> & text",original:"A letter with angle brackets."}];
const ctx={
 window:{},JSON,document:{documentElement:{cloneNode:()=>element}},
 data,people:{"Andrew Jackson":{initials:"AJ"}},notes:{"test":"My note"},starred:new Set(["test"]),read:new Set(["test"]),
 fetch:async url=>{
  const file=url.replace(/^\//,"");
  return {ok:true,status:200,text:async()=>fs.readFileSync(path.join(assets,file),"utf8")};
 },
 toast:txt=>{toastText=txt},
 download:(name,blob,mime)=>{artifact={name,blob,mime}}
};
vm.createContext(ctx);
vm.runInContext(html.slice(start,end)+"\nwindow.saveStandalone=downloadCompiledHTML;",ctx);
(async()=>{
 await ctx.window.saveStandalone();
 assert.ok(artifact,"Export failed: "+toastText);
 assert.ok(artifact.blob.length>html.length);
 assert.ok(artifact.name.endsWith("_1_letters.html"));
 for(const file of ["threading.js","sms_view.js","navigation.js","reader_ui.js"]){
  assert.ok(!artifact.blob.includes('<script src="'+file+'"></script>'),file+" still external");
  assert.ok(artifact.blob.includes(fs.readFileSync(path.join(assets,file),"utf8").slice(0,45)),file+" source not embedded");
 }
 assert.equal(artifact.blob.split("read.add(state.id);save(false);render();loadLargeArchive();loadBundledCorrespondence();").length-1,1,"Standalone export should retain this loader only as an inert string inside the exporter function, not call it");
 assert.ok(artifact.blob.includes("\\u003c/script"),"Embedded JSON wasn't HTML-escaped");
 assert.ok(artifact.blob.includes("My note") && artifact.blob.includes("A letter with angle brackets"));
 console.log("STANDALONE_EXPORT_TESTS_OK: embedded archive, four scripts, notes and safe JSON");
})().catch(err=>{console.error(err);process.exitCode=1});

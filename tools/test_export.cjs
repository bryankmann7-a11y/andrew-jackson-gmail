#!/usr/bin/env node
/* Standalone export must include every required script and original records. */
"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const root=path.resolve(__dirname,".."),assets=path.join(root,"app/src/main/assets");
const html=fs.readFileSync(path.join(assets,"index.html"),"utf8");
const start=html.indexOf("async function downloadCompiledHTML(){");
const end=html.indexOf("\nfunction exportData(){",start);
assert.ok(start>0&&end>start,"Export function missing");

const inlineBegin=html.indexOf("<script>\nconst STARTER_LETTERS="),inlineEnd=html.lastIndexOf("</script>");
assert.ok(inlineBegin>0 && inlineEnd>inlineBegin);
assert.ok(!html.slice(inlineBegin+8,inlineEnd).toLowerCase().includes("</script>"),
  "The HTML parser will prematurely terminate the main script");

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
 assert.equal(artifact.blob.split("save(false);render();loadLargeArchive();loadBundledCorrespondence();").length-1,1,
   "The original loader must remain only as a quoted string inside the exporter");
 assert.ok(/\}save\(false\);render\(\);\s*<\/script><\/body><\/html>/.test(artifact.blob),
   "Standalone archive must launch without trying to fetch missing bundled assets");
 assert.ok(artifact.blob.includes("\\u003c/script"),"Embedded JSON wasn't HTML-escaped");
 assert.ok(artifact.blob.includes("My note") && artifact.blob.includes("A letter with angle brackets"));
 // Importing an exported letter must not silently strip its OCR review status,
 // source page or editorial provenance. User records can keep those fields.
 const normalizeStart=html.indexOf("function normalize(item,i){");
 const normalizeEnd=html.indexOf("\nlet lastImportSavedPromise",normalizeStart);
 assert.ok(normalizeStart>0&&normalizeEnd>normalizeStart);
 const importer=vm.runInNewContext("("+html.slice(normalizeStart,normalizeEnd)+")");
 const imported=importer({id:"sample",date:"1814-06-01",from:"Andrew Jackson",
   to:"John Coffee",original:"Text",readable:"Cleaned display",ocrFlags:["symbol_in_word"],
   needsReview:true,volume:2,page:110,sourceChecked:false,modernType:"not yet written"},0);
 assert.equal(imported.readable,"Cleaned display");
 assert.equal(imported.ocrFlags[0],"symbol_in_word");
 assert.equal(imported.needsReview,true);
 assert.equal(imported.page,110);
 assert.equal(imported.sourceChecked,false);
 // Java encodes each AndroidBridge chunk separately; never split a surrogate pair.
 const chunkStart=html.indexOf("function* safeExportChunks(");
 const chunkEnd=html.indexOf("\nfunction downloadTemplate()",chunkStart);
 assert.ok(chunkStart>0&&chunkEnd>chunkStart);
 const sent=[];
 const bridge={beginSave(){},saveChunk(text){sent.push(text)},finishSave(){}};
 const unicode="A".repeat(15999)+"😀"+"B".repeat(16000)+"𐐷";
 vm.runInNewContext(html.slice(chunkStart,chunkEnd)+"\ndownload('archive.json',payload);",
   {window:{AndroidBridge:bridge},AndroidBridge:bridge,toast(){},payload:unicode});
 assert.equal(sent.join(""),unicode,"Android export must preserve complete Unicode characters");
 assert.ok(sent.length>2);
 for(const chunk of sent){
   assert.ok(chunk.length<=16000);
   const first=chunk.charCodeAt(0),last=chunk.charCodeAt(chunk.length-1);
   assert.ok(first<0xDC00||first>0xDFFF,"Export chunk begins with low surrogate");
   assert.ok(last<0xD800||last>0xDBFF,"Export chunk ends with high surrogate");
 }
 console.log("STANDALONE_EXPORT_TESTS_OK: standalone offline launch, Unicode-safe backup, source metadata");
})().catch(err=>{console.error(err);process.exitCode=1});

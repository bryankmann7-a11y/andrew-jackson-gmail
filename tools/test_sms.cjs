#!/usr/bin/env node
/* No fabricated replies; text-message view navigation and performance guardrails. */
"use strict";
const fs=require("node:fs"),path=require("node:path"),assert=require("node:assert/strict"),vm=require("node:vm");
const root=path.resolve(__dirname,"..");
const letters=JSON.parse(fs.readFileSync(path.join(root,"app/src/main/assets/archive/corpus.json"),"utf8")).letters;
const escapeHTML=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const ctx={
 data:letters.slice(),state:{id:letters[0].id,view:"sms"},
 document:{createElement:()=>({textContent:""}),head:{appendChild:()=>{}},getElementById:()=>null},
 window:{},escapeHTML,
 dateFmt:s=>s, sourceHref:s=>s, avatar:n=>'<div class="avatar">'+escapeHTML(n)+'</div>',safeKey:encodeURIComponent,
 requestAnimationFrame:null
};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(root,"app/src/main/assets/sms_view.js"),"utf8"),ctx);
const ui=ctx.window.SmsConversationUI;
assert.ok(ui&&typeof ui.render==="function"&&typeof ui.move==="function");
const sevier=letters.filter(x=>x.date>="1797-05-08"&&x.date<="1797-05-13"&&
 (x.from==="John Sevier"||x.to==="John Sevier"));
assert.ok(sevier.length>=4,"Historical Sevier exchange missing");
const selected=sevier.find(d=>d.from==="John Sevier")||sevier[0];
const all=ui.collect("John Sevier");
assert.ok(all.length>=sevier.length);
assert.ok(all.every(d=>d.from==="John Sevier"||d.to==="John Sevier"),"Merged unrelated correspondents");
assert.ok(all.every((d,i)=>!i||all[i-1].date<=d.date),"Messages not in date order");
const selectedWindow=ui.windowFor(selected);
assert.ok(selectedWindow.end-selectedWindow.start<=48,"Too many letters in one SMS render");
assert.ok(all.slice(selectedWindow.start,selectedWindow.end).some(d=>d.id===selected.id),"Selected letter not visible");
const html=ui.render(selected);
assert.ok(html.includes("sms-date-divider"),"No date separators");
assert.ok(html.includes("John Sevier"),"Missing correspondent name");
assert.ok(html.includes("not actual text messages"),"Missing historical disclaimer");
assert.ok(html.includes("Source"),"Missing historical source links");
assert.ok(html.includes("Read full letter"),"Long letters should begin collapsed");
assert.ok(html.includes("Open letter"),"Cannot open full mail view");
assert.ok(html.includes("sms-letter-"+selected.id),"Missing selected document");
assert.ok(!html.includes('id="nonexistent-reply"'),"Unreal reply created");
const veryLong=all.find(d=>ui.messageText(d).length>5000);
if(veryLong){
  assert.ok(ui.messageText(veryLong).length>5000,"Full original no longer accessible");
  const individual=ui.render(veryLong);
  assert.ok(individual.includes("Read full letter"),"Full text should be collapsible");
}
// Never erase uncertain same-day correspondence or imported documents.
const source=letters.find(d=>d.status==="ocr" && d.from==="Andrew Jackson" && d.to==="Waightstill Avery");
assert.ok(source);
const sourceOther="Waightstill Avery";
const count0=ui.collect(sourceOther).length;
ctx.data.push({id:"j-sms-known-adaptation",date:source.date,from:source.from,to:source.to,
               status:"adapted",modern:"Historical starter text"});
assert.equal(ui.collect(sourceOther).length,count0,"Unique OCR should replace a known starter copy");
ctx.data.push(Object.assign({},source,{id:"basset-extra-same-day"}));
assert.equal(ui.collect(sourceOther).length,count0+2,
 "Two originals on one day are ambiguous; preserve both and the starter");
ctx.data.push({id:"user-import-unique",date:source.date,from:source.from,to:source.to,
               status:"original",original:"A separate imported record"});
assert.equal(ui.collect(sourceOther).length,count0+3,
 "Never silently discard a user-imported document");
let biggest=0;
const others=new Set(letters.map(x=>x.from==="Andrew Jackson"?x.to:x.from));
for (const other of others) biggest=Math.max(biggest,ui.collect(other).length);
assert.ok(biggest>50,"Paging not tested on a long correspondence");
// Regression: SMS → full Gmail email must select the Mail tab, not call .forEach on a single element.
const tabs=[{dataset:{view:"mail"},classList:{toggle(name,on){this.selected=on}}},
            {dataset:{view:"sms"},classList:{toggle(name,on){this.selected=on}}}];
let selectedId=null,skipNav=null,enterCount=0,expandedId=null;
ctx.document.querySelectorAll=selector=>{
  assert.equal(selector,"#viewMode button");
  return tabs;
};
ctx.window.JacksonNav={enter(){enterCount++}};
ctx.JacksonNav=ctx.window.JacksonNav;
ctx.GmailThreadUI={setExpanded(id){expandedId=id}};
ctx.selectLetter=(id,skip)=>{selectedId=id;skipNav=skip};
ui.openAsLetter(selected.id);
assert.equal(ctx.state.view,"mail");
assert.equal(selectedId,selected.id);
assert.equal(skipNav,true);
assert.equal(expandedId,selected.id);
assert.equal(enterCount,1);
assert.equal(tabs[0].classList.selected,true);
assert.equal(tabs[1].classList.selected,false);
console.log("SMS_TESTS_OK",letters.length,"historical OCR entries;",all.length,"Sevier letters;",biggest,"max correspondent letters; window",selectedWindow.end-selectedWindow.start);

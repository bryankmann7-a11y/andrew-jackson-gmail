#!/usr/bin/env node
/* Regression checks for Gmail-style archival reply grouping.
   The matching algorithm only infers possible threads and never invents documents. */
"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");
const root=path.resolve(__dirname,"..");
const archive=JSON.parse(fs.readFileSync(path.join(root,"app/src/main/assets/archive/corpus.json"),"utf8"));
const records=archive.letters;
const ctx={
 data:records.slice(),starred:new Set(),read:new Set(),
 state:{folder:"all",sort:"old",query:"",id:records[0].id},
 document:{createElement:()=>({textContent:""}),head:{appendChild:()=>{}}},
 window:{}
};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(root,"app/src/main/assets/threading.js"),"utf8"),ctx);
const ui=ctx.window.GmailThreadUI;
assert.ok(ui && typeof ui.threadForMessage==="function","Gmail thread interface was not registered");
const total=ui.counts("all");
assert.ok(total>1000 && total<records.length,"Expected meaningful, conservative grouping");
const maySevier=records.filter(x=>x.date>="1797-05-08"&&x.date<="1797-05-11" &&
  (x.from==="John Sevier"||x.to==="John Sevier"));
assert.ok(maySevier.length>=4,"Missing historic May 1797 two-way Sevier exchange");
const thread=ui.threadForMessage(maySevier[0].id);
for(const d of maySevier)assert.equal(ui.threadForMessage(d.id)?.id,thread.id,"Known Sevier reply not in one conversation");
assert.ok(thread.messages.length>=4);
assert.ok(thread.messages.every(d=>d.from==="Andrew Jackson"||d.to==="Andrew Jackson"));
assert.ok(thread.messages.every(d=>d.from==="John Sevier"||d.to==="John Sevier"));
assert.ok(thread.messages.every((d,i)=>i===0||d.date>=thread.messages[i-1].date));
for (const d of records) {
  const t=ui.threadForMessage(d.id);
  assert.ok(t, "Letter disappeared from its Gmail thread: "+d.id);
  const other=d.from==="Andrew Jackson"?d.to:d.from;
  if(t.messages.length>1)assert.equal(t.other,other,"Unrelated correspondents merged");
}
assert.equal(new Set(records.map(x=>x.id)).size,records.length,"Corpus identifiers are not unique");
// Make sure an earlier starter adaptation does not produce a second inbox row
// when a real scan-derived record for the same date and correspondent exists.
const sample=records.find(d=>d.status==="ocr"&&d.from==="Andrew Jackson"&&d.to==="Waightstill Avery");
assert.ok(sample);
ctx.data.push({id:"j-test-duplicate",date:sample.date,from:sample.from,to:sample.to,status:"adapted",modern:"Earlier unchecked adaptation"});
assert.equal(ui.counts("all"),total,"Legacy adaptation was duplicated beside its OCR source");
assert.equal(sample._legacyId,"j-test-duplicate","Legacy star/note alias was not retained");
ctx.STARTER_LETTERS=[{id:"in-synthetic-starter"}];
ctx.data.push({id:"in-synthetic-starter",date:sample.date,from:sample.from,to:sample.to,status:"adapted",modern:"Second starter copy"});
assert.equal(ui.counts("all"),total,"Non-j starter copy duplicated the OCR letter");
// If two actual originals share the same date and parties, don't merge a
// historic starter into an arbitrary one.
const duplicateOriginal=Object.assign({},sample,{id:"basset-test-same-day"});
ctx.data.push(duplicateOriginal);
ctx.data.push({id:"j-ambiguous",date:sample.date,from:sample.from,to:sample.to,status:"adapted",modern:"Uncertain alternate text"});
const after=ui.threadForMessage("j-ambiguous");
assert.ok(after && after.messages.some(d=>d.id==="j-ambiguous"),"Ambiguous same-day document was silently hidden");

// Multiple query terms can match across metadata and body, and costly OCR
// normalization happens once per record rather than every keystroke.
let rawReads=0;
const costly={from:"Andrew Jackson",to:"Jane",date:"1800-01-01",
  subject:"Orders",readable:"",get original(){rawReads++;return "Supplies reached Nashville."}};
assert.equal(ui.matchesQuery(costly,"jane supplies"),true);
assert.equal(ui.matchesQuery(costly,"Jane NASHVILLE"),true);
assert.equal(ui.matchesQuery(costly,"jane absent"),false);
assert.equal(rawReads,1,"Search should cache full-text normalization per record");
assert.ok(ui.matchesQuery(costly,""));
console.log("THREAD_TESTS_OK",records.length,"OCR candidates in",total,"email conversations;",thread.messages.length,"Sevier messages grouped");

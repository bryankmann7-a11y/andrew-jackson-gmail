#!/usr/bin/env node
/* Reader settings + archive filter regression: conservative claims, no mutation. */
"use strict";
const fs=require("node:fs"),path=require("node:path"),vm=require("node:vm"),assert=require("node:assert/strict");
const base=path.resolve(__dirname,"..");
const file=fs.readFileSync(path.join(base,"app/src/main/assets/reader_ui.js"),"utf8");
const records=new Map();
const classes=new Set();
const elements={
 filterPeriod:{value:"all"},
 filterQuality:{value:"all"},
 filterReset:{style:{display:"none"}}
};
let rerenders=0,property="",sizeValue="";
const doc={
 readyState:"complete",
 createElement:()=>({textContent:""}),
 head:{appendChild(){}},
 body:{classList:{add(x){classes.add(x)},remove(x){classes.delete(x)}}},
 documentElement:{style:{setProperty(k,v){property=k;sizeValue=v}}},
 getElementById:k=>elements[k]||null
};
const context={
 document:doc,window:{},localStorage:{
   getItem:key=>records.get(key)||null,
   setItem:(key,value)=>records.set(key,value)
 },LIST_LIMIT:999,
 render(){rerenders++}
};
vm.createContext(context);
vm.runInContext(file,context);
const ui=context.window.JacksonReaderUI;
assert.ok(ui&&ui.filterBar().includes("OCR reading copy"));
assert.equal(property,"--reading-size");
assert.equal(ui.getPrefs().size,16);
assert.equal(ui.getPrefs().mode,"paper");
const before={date:"1803-10-02",status:"ocr",modern:"",original:"Original only",needsReview:true};
const modern={date:"1797-05-11",status:"ocr",modern:"Human rendering",needsReview:false};
const late={date:"1834-06-12",status:"ocr",modern:"",needsReview:false};
const baseline=JSON.stringify([before,modern,late]);
assert.ok(ui.matches(before)&&ui.matches(modern)&&ui.matches(late));
ui.setFilter("1788-1819","needsReview");
assert.equal(ui.matches(before),true);
assert.equal(ui.matches(modern),false);
assert.equal(ui.matches(late),false);
ui.setFilter("all","modern");
assert.equal(ui.matches(modern),true);
assert.equal(ui.matches(before),false);
ui.setFilter("all","ocr");
assert.equal(ui.matches(before),true);
assert.equal(ui.matches(modern),false);
elements.filterPeriod.value="1829-1837";
elements.filterQuality.value="all";
ui.changed();
assert.equal(context.LIST_LIMIT,120);
assert.equal(rerenders,1);
assert.ok(elements.filterReset.style.display!=="none");
assert.equal(ui.matches(late),true);
ui.clear();
assert.equal(ui.matches(before),true);
assert.equal(ui.matches(late),true);
assert.equal(elements.filterReset.style.display,"none");
ui.adjust(3);
assert.equal(ui.getPrefs().size,19);
ui.adjust(200);
assert.equal(ui.getPrefs().size,23);
ui.adjust(-200);
assert.equal(ui.getPrefs().size,13);
ui.theme();
assert.equal(ui.getPrefs().mode,"sepia");
ui.theme();
assert.equal(ui.getPrefs().mode,"night");
assert.ok(classes.has("reader-theme-night"));
assert.equal(JSON.stringify([before,modern,late]),baseline,"Reader UI must not edit archival records");
assert.ok(records.has("jackson_reader_prefs_v1"));
const java=fs.readFileSync(path.join(base,"app/src/main/java/org/jacksonletters/archive/MainActivity.java"),"utf8");
const html=fs.readFileSync(path.join(base,"app/src/main/assets/index.html"),"utf8");
const threads=fs.readFileSync(path.join(base,"app/src/main/assets/threading.js"),"utf8");
assert.ok(java.includes('path.equals("/reader_ui.js")'));
assert.ok(html.includes('<script src="reader_ui.js"></script>'));
assert.ok(html.includes('id="filtersMount"'));
assert.ok(html.includes("JacksonReaderUI.filterBar()"));
assert.ok(threads.includes("JacksonReaderUI.matches(d)"));
assert.ok(threads.includes("JacksonReaderUI.controls()"));
console.log("READER_UI_TESTS_OK: periods, editions, OCR review, themes, text size, persistence, no source mutation");

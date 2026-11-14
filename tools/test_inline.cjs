#!/usr/bin/env node
/* Preflight the actual Android WebView inline program, not just external JS. */
"use strict";
const fs=require("node:fs"),path=require("node:path"),assert=require("node:assert/strict"),vm=require("node:vm");
const html=fs.readFileSync(path.join(__dirname,"../app/src/main/assets/index.html"),"utf8");
const marker="<script>\nconst STARTER_LETTERS=";
const start=html.indexOf(marker),end=html.lastIndexOf("</script>");
assert.ok(start>=0&&end>start,"Main WebView app script missing");
const source=html.slice(start+"<script>".length,end);
assert.ok(!source.toLowerCase().includes("</script"),"Raw script-closing tag inside inline JS");
new vm.Script(source,{filename:"index.html inline"});
for(const asset of ["threading.js","sms_view.js","navigation.js","reader_ui.js"]){
 assert.ok(html.includes('<script src="'+asset+'"></script>'),asset+" must load before main script");
}
assert.ok(html.includes("loadBundledCorrespondence();"),"Offline corpus loader missing");
assert.ok(html.includes("archiveLoadStatus='loading'"),"Initial loading message missing");
assert.ok(html.includes("archiveLoadStatus='ready'"),"Successful load state missing");
assert.ok(html.includes("archiveLoadStatus='error'"),"Failure state missing");
console.log("WEBVIEW_INLINE_TEST_OK: parsing, module order, archive start/failure states");

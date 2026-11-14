#!/usr/bin/env node
/* Fast deterministic tests of in-app Back semantics (does not replace phone QA). */
"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),vm=require("node:vm"),path=require("node:path");
const root=path.resolve(__dirname,"..");
function el(id){
  return {
    value:"",scrollTop:0,innerHTML:"",closed:false,
    classList:{
      flags:new Set(),contains(v){return this.flags.has(v)},
      add(v){this.flags.add(v)},remove(v){this.flags.delete(v)},
      toggle(v,bool){if(bool)this.add(v);else this.remove(v);}
    },
    querySelector(){return null},querySelectorAll(){return []}
  };
}
const els=new Map(Object.entries({
 "#records":el("records"),"#reader":el("reader"),"#search":el("search"),
 "#sidebar":el("sidebar"),"#modalMount":el("modal"),"#viewMode":el("mode")
}));
els.get("#modalMount").querySelector=(s)=>s===".modal-back"&&els.get("#modalMount").innerHTML?{id:"modal"}:null;
const state={folder:"all",id:"initial",view:"mail",tab:"modern",profile:false,sort:"old",query:"",mobileOpen:false};
let renderCalls=0, closeCalls=0, cancelCalls=0,navCloseCalls=0;
const context={
 state,LIST_LIMIT:240,
 document:{querySelector:s=>els.get(s)||null,activeElement:{tagName:"DIV",blur(){}}},
 window:{},
 render(){renderCalls++;els.get("#records").scrollTop=0;els.get("#reader").scrollTop=0;},
 closeModal(){closeCalls++;els.get("#modalMount").innerHTML="";},
 cancelBulkLoad(){cancelCalls++;els.get("#modalMount").innerHTML="";},
 toggleNav(){navCloseCalls++;els.get("#sidebar").classList.remove("open");},
 bulkLoading:false
};
vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(root,"app/src/main/assets/navigation.js"),"utf8"),context);
const nav=context.window.JacksonNav;
assert.ok(nav && typeof nav.back==="function");
// Opening a letter must return to same inbox filters and scroll.
state.query="sevier";state.sort="new";state.id="inbox-selected";
els.get("#search").value="sevier";els.get("#records").scrollTop=918;
nav.enter();
state.folder="all";state.query="";state.id="opened-letter";state.sort="old";
els.get("#search").value="";
els.get("#reader").classList.add("show");els.get("#reader").scrollTop=400;
assert.equal(nav.back(),true);
assert.equal(els.get("#reader").classList.contains("show"),false);
assert.equal(state.id,"inbox-selected");
assert.equal(state.query,"sevier");
assert.equal(state.sort,"new");
assert.equal(els.get("#search").value,"sevier");
assert.equal(els.get("#records").scrollTop,918);
assert.equal(context.LIST_LIMIT,240);
assert.equal(renderCalls,1);
// Opening a profile on top of an open thread returns to that thread.
els.get("#reader").classList.add("show");
els.get("#reader").scrollTop=570;
state.id="letter-1";state.folder="all";
nav.enter();
state.folder="contacts";state.profile="John Sevier";state.id="profile";
els.get("#reader").scrollTop=22;
assert.equal(nav.back(),true);
assert.equal(state.profile,false);
assert.equal(state.id,"letter-1");
assert.equal(els.get("#reader").classList.contains("show"),true);
assert.equal(els.get("#reader").scrollTop,570);
// Opening a full email from SMS must return to the SMS message with its position.
state.view="sms";state.id="sms-selected";state.folder="all";
els.get("#reader").classList.add("show");els.get("#reader").scrollTop=212;
nav.enter();
state.view="mail";state.id="opened-full-mail";
els.get("#reader").scrollTop=0;
assert.equal(nav.back(),true);
assert.equal(state.view,"sms");
assert.equal(state.id,"sms-selected");
assert.equal(els.get("#reader").scrollTop,212);
// Back while editing notes should dismiss the keyboard first, not close the letter.
let blurred=0;
context.document.activeElement={tagName:"TEXTAREA",blur(){blurred++;}};
assert.equal(nav.back(),true);
assert.equal(blurred,1);
assert.equal(els.get("#reader").classList.contains("show"),true);
context.document.activeElement={tagName:"DIV",blur(){}};
// Drawer has priority over the reader.
els.get("#sidebar").classList.add("open");
assert.equal(nav.back(),true);
assert.equal(navCloseCalls,1);
assert.equal(els.get("#reader").classList.contains("show"),true);
// Modal has higher priority than reader/drawer.
els.get("#modalMount").innerHTML="dialog";
assert.equal(nav.back(),true);
assert.equal(closeCalls,1);
context.bulkLoading=true;
els.get("#modalMount").innerHTML="import in progress";
assert.equal(nav.back(),true);
assert.equal(cancelCalls,1);
context.bulkLoading=false;
// Reader without history closes without exiting app.
assert.equal(nav.back(),true);
assert.equal(els.get("#reader").classList.contains("show"),false);
// Search clears, then non-home folder returns home, then exit is allowed.
assert.equal(nav.back(),true);
assert.equal(state.query,"");
state.folder="contacts";
assert.equal(nav.back(),true);
assert.equal(state.folder,"all");
assert.equal(nav.back(),false);
// Static Android integration checks.
const java=fs.readFileSync(path.join(root,"app/src/main/java/org/jacksonletters/archive/MainActivity.java"),"utf8");
const manifest=fs.readFileSync(path.join(root,"app/src/main/AndroidManifest.xml"),"utf8");
const html=fs.readFileSync(path.join(root,"app/src/main/assets/index.html"),"utf8");
assert.ok(java.includes("handleNavigationBack()")&&java.includes("window.JacksonNav.back()"));
assert.ok(java.includes('path.equals("/navigation.js")'));
assert.ok(manifest.includes('orientation|screenSize|keyboardHidden'));
assert.ok(html.includes('<script src="navigation.js"></script>'));
assert.ok(html.includes("function backMobile(){if(window.JacksonNav)JacksonNav.back()"));
console.log("NAVIGATION_TESTS_OK: reader / inbox / filters / scroll / profile / drawer / modal / Android Back wiring");

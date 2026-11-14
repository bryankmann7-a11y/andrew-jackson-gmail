/* Compact SMS-style rendering of historical letters. These were never actual text messages. */
(function(){
"use strict";
const WINDOW=48, PREVIEW=440;
const css = document.createElement("style");
css.textContent = [
".sms-wrap{height:100%;min-height:0;display:flex;flex-direction:column}",
".sms-head{flex-shrink:0}",
".sms-head .sms-actions{display:flex;gap:5px;margin-left:auto}",
".sms-head .sms-actions .ghost{padding:8px 9px}",
".sms-stream{scroll-behavior:auto}",
".sms-bubble{white-space:pre-wrap;overflow-wrap:anywhere;max-width:100%;font-size:13px;line-height:1.65}",
".sms-date-divider{align-self:center;position:relative;background:#e9edf4;border:1px solid #dfe5ee;color:#53637a;border-radius:30px;padding:5px 13px;margin:10px 0 5px;font-size:11px;font-weight:650}",
".sms-window-actions{display:flex;justify-content:center;margin:8px 0}",
".sms-window-actions button{border:1px solid var(--line);background:#fff;color:var(--blue);border-radius:18px;font-size:12px;padding:8px 15px}",
".sms-line{max-width:88%;display:flex;flex-direction:column;gap:4px;align-items:flex-start}",
".sms-line.sent{align-self:flex-end;align-items:flex-end}",
".sms-line .bubble{word-break:break-word;overflow-wrap:anywhere;white-space:pre-wrap}",
".sms-line.selected .bubble{outline:2px solid #9aaedc;outline-offset:2px}",
".sms-body-bottom{font-size:10px;color:#8490a3;display:flex;flex-wrap:wrap;gap:9px;align-items:center;padding:0 3px}",
".sms-line.sent .sms-body-bottom{justify-content:flex-end}",
".sms-bubble-toggle{border:0;background:transparent;color:#275eb9;padding:4px 0;font-weight:700;font-size:12px}",
".sms-bubble-toggle.sent{color:#275eb9}",
".sms-meta-note{color:#7c8799;font-size:10.5px;line-height:1.45}",
".sms-footer{flex-shrink:0}",
"@media(max-width:730px){.sms-head strong{max-width:36vw;overflow:hidden;white-space:nowrap;text-overflow:ellipsis}.sms-head .sms-actions .ghost{font-size:11px;padding:7px}.sms-stream{padding:12px 12px 25px}.sms-line{max-width:93%}.sms-line .bubble{padding:11px 13px}}"
].join("\n");
document.head.appendChild(css);
let cached=null, cachedCount=-1, cachedOther="", currentKey="", windowStart=0;
let expanded=new Set(), scrollToId=null;

function otherPerson(d){
 if(d.from==="Andrew Jackson")return d.to;
 if(d.to==="Andrew Jackson")return d.from;
 return null;
}
function collect(other){
 if(cached && cachedCount===data.length && cachedOther===other)return cached;
 const all=data.filter(d => (d.from==="Andrew Jackson" && d.to===other) ||
                             (d.to==="Andrew Jackson" && d.from===other));
 const ocrKeys=new Set(all.filter(d=>d.status==="ocr").map(d=>d.date+"|"+d.from+"|"+d.to));
 const docs=all.filter(d=>d.status==="ocr" || !ocrKeys.has(d.date+"|"+d.from+"|"+d.to))
               .sort((a,b)=>String(a.date).localeCompare(String(b.date)) || String(a.id).localeCompare(String(b.id)));
 cached=docs;cachedCount=data.length;cachedOther=other;
 return docs;
}
function boundedStart(index,count){
 return Math.max(0,Math.min(Math.max(0,count-WINDOW),index-12));
}
function windowFor(selected){
 const other=otherPerson(selected),docs=collect(other);
 const index=Math.max(0,docs.findIndex(d=>d.id===selected.id));
 const key=other+"|"+selected.id;
 if(key!==currentKey){
    currentKey=key;
    windowStart=boundedStart(index,docs.length);
    expanded=new Set();
    scrollToId=docs[index]?.id||null;
 }
 windowStart=Math.max(0,Math.min(windowStart,Math.max(0,docs.length-WINDOW)));
 return {other,docs,index,start:windowStart,end:Math.min(docs.length,windowStart+WINDOW)};
}
function messageText(d){return String(d.modern||d.readable||d.original||"Text not available.");}
function dateGroup(d){return String(d.date||"Unknown").slice(0,7);}
function qualityLabel(d){
 if(d.modern)return "Condensed modern English · not scan-verified";
 if(d.status==="ocr" && Array.isArray(d.ocrFlags) && d.ocrFlags.length)return "Uncorrected OCR · source review needed";
 if(d.status==="ocr")return "Uncorrected OCR reading copy · not translated";
 return "Earlier adaptation · source not fully checked";
}
function message(d,selectedId){
 const full=messageText(d),long=full.length>PREVIEW;
 const isExpanded=!long||expanded.has(d.id);
 const shown=isExpanded?full:full.slice(0,PREVIEW).replace(/\s+\S*$/,"")+"…";
 const sent=d.from==="Andrew Jackson";
 const source=sourceHref(d.source);
 const action=long?'<button class="sms-bubble-toggle" aria-expanded="'+isExpanded+'" onclick="SmsConversationUI.toggle(\''+escapeHTML(d.id)+'\')">'+
    (isExpanded?"Show less":"Read full letter")+"</button>":"";
 return '<div class="sms-line '+(sent?"sent ":"")+(d.id===selectedId?"selected":"")+
    '" id="sms-letter-'+escapeHTML(d.id)+'">'+
    '<div class="bubble-meta">'+escapeHTML(d.from)+' · '+escapeHTML(dateFmt(d.date))+'</div>'+
    '<div class="bubble sms-bubble">'+escapeHTML(shown)+'</div>'+
    '<div class="sms-body-bottom"><span>'+escapeHTML(qualityLabel(d))+'</span>'+action+
    '<button class="switchlink" onclick="SmsConversationUI.openAsLetter(\''+escapeHTML(d.id)+'\')">Open letter</button>'+
    (source?'<a target="_blank" rel="noopener" href="'+source+'">Source</a>':"")+
    '</div></div>';
}
function render(selected){
 const w=windowFor(selected);
 if(!w.other)return '<div class="empty">This document does not have a known Jackson correspondent.</div>';
 const current=w.docs.slice(w.start,w.end);
 let lastGroup="", fragments=[];
 if(w.start>0)fragments.push('<div class="sms-window-actions"><button onclick="SmsConversationUI.move(-1)">Show earlier letters ('+w.start+' more)</button></div>');
 for(const d of current){
   const group=dateGroup(d);
   if(group!==lastGroup){
      fragments.push('<div class="sms-date-divider">'+escapeHTML(group==='Unknown'?"Undated":new Date(group+"-15T12:00:00").toLocaleDateString("en-US",{month:"long",year:"numeric"}))+'</div>');
      lastGroup=group;
   }
   fragments.push(message(d,selected.id));
 }
 if(w.end<w.docs.length)fragments.push('<div class="sms-window-actions"><button onclick="SmsConversationUI.move(1)">Show later letters ('+(w.docs.length-w.end)+' more)</button></div>');
 const out='<div class="sms-wrap">'+
 '<div class="sms-head"><button class="ghost mobile-back" onclick="backMobile()">← Inbox</button>'+avatar(w.other)+
 '<div><strong>'+escapeHTML(w.other)+'</strong><small>'+w.docs.length+' historic letters · oldest to newest</small></div>'+
 '<div class="sms-actions"><button class="ghost" onclick="SmsConversationUI.jump()" aria-label="Jump to selected letter">Locate</button>'+
 '<button class="ghost" onclick="openProfile(\''+safeKey(w.other)+'\')">Profile</button></div></div>'+
 '<div class="sms-stream" id="sms-stream" role="list" aria-label="Historical letters presented as messages">'+fragments.join("")+'</div>'+
 '<div class="sms-footer">These are historical letters, not actual text messages. Letters are grouped by correspondent, not assumed to be replies. Missing letters are not invented.</div></div>';
 if(scrollToId && typeof requestAnimationFrame==="function"){
    const id=scrollToId;scrollToId=null;
    requestAnimationFrame(()=>{
      const el=document.getElementById("sms-letter-"+id);
      const scroller=document.getElementById("sms-stream");
      if(el&&scroller){
        const offset=el.getBoundingClientRect().top-scroller.getBoundingClientRect().top;
        scroller.scrollTop+=offset-80;
      }
    });
 }
 return out;
}
function sync(restore){
 const scroller=document.getElementById("sms-stream");
 const oldTop=restore&&scroller?scroller.scrollTop:0;
 if(typeof window.render==="function")window.render();
 if(restore){const next=document.getElementById("sms-stream");if(next)next.scrollTop=oldTop;}
}
function toggle(id){
 expanded.has(id)?expanded.delete(id):expanded.add(id);
 sync(true);
}
function move(direction){
 const selected=data.find(d=>d.id===state.id);
 if(!selected)return;
 const n=collect(otherPerson(selected)).length;
 windowStart=Math.max(0,Math.min(Math.max(0,n-WINDOW),windowStart+direction*WINDOW));
 scrollToId=null;
 sync(false);
 const scroller=document.getElementById("sms-stream");
 if(scroller)scroller.scrollTop=0;
}
function jump(){
 const id=state.id;
 const selected=data.find(d=>d.id===id);if(!selected)return;
 const docs=collect(otherPerson(selected));
 windowStart=boundedStart(Math.max(0,docs.findIndex(d=>d.id===id)),docs.length);
 scrollToId=id;
 sync(false);
}
function openAsLetter(id){
 if(window.JacksonNav)JacksonNav.enter();
 state.view="mail";
 if(typeof GmailThreadUI!=="undefined")GmailThreadUI.setExpanded(id);
 selectLetter(id,true);
 $("#viewMode button").forEach(b=>b.classList.toggle("selected",b.dataset.view==="mail"));
}
window.SmsConversationUI={render,toggle,move,jump,openAsLetter,collect,windowFor,messageText};
})();

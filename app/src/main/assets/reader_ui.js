/* Reader controls and conservative archive filters for Jackson Letters.
   Display-only preferences; originals and saved notes are not modified. */
(function () {
  "use strict";
  const KEY = "jackson_reader_prefs_v1";
  const modes = ["paper", "sepia", "night"];
  const limits = {min:13,max:23};
  const filter = {period:"all",quality:"all"};
  let saved={};
  try { saved=JSON.parse(localStorage.getItem(KEY)||"{}")||{}; } catch (_) {}
  let size=Number(saved.size)||16;
  if(!Number.isFinite(size))size=16;
  size=Math.max(limits.min,Math.min(limits.max,size));
  let mode=modes.includes(saved.mode)?saved.mode:"paper";
  const css=document.createElement("style");
  css.textContent=[
    ".archive-filters{display:flex;gap:6px;align-items:center;flex-wrap:wrap;padding:4px 14px 12px;background:white;border-bottom:1px solid var(--line)}",
    ".archive-filters select{background:#f5f7fb;border:1px solid #dce4ef;color:#3b4a60;border-radius:9px;font-size:12px;padding:9px 8px;max-width:46%;flex:1;min-width:110px}",
    ".archive-filters button{border:0;background:transparent;color:#2859c5;padding:8px;font-size:12px;white-space:nowrap}",
    ".reader-pref-controls{display:inline-flex;flex-wrap:wrap;align-items:center;gap:5px}",
    ".reader-pref-controls button{font-size:12px;padding:9px 10px}",
    ".reader .gmail-document:not(.info),.reader .letter-body{font-size:var(--reading-size,16px)!important;line-height:1.85!important;overflow-wrap:anywhere}",
    ".reader .gmail-document.info{font-size:14px}",
    "body.reader-theme-sepia .reader{background:#f4ecd9;color:#3c3325}",
    "body.reader-theme-sepia .gmail-message,body.reader-theme-sepia .envelope{background:#fff8e7;border-color:#e1d2b6;color:#3c3325}",
    "body.reader-theme-sepia .gmail-message-head{background:#fff8e7;color:#3c3325}",
    "body.reader-theme-sepia .gmail-message-head:hover{background:#f9efd9}",
    "body.reader-theme-sepia .gmail-document,body.reader-theme-sepia .letter-body{color:#392f22}",
    "body.reader-theme-night .reader{background:#171d28;color:#e5eaf2}",
    "body.reader-theme-night .gmail-wrap,body.reader-theme-night .reader-pad{color:#e5eaf2}",
    "body.reader-theme-night .gmail-message,body.reader-theme-night .envelope{background:#222b39;border-color:#3b4759;color:#e5eaf2;box-shadow:none}",
    "body.reader-theme-night .gmail-message-head{background:#222b39;color:#e5eaf2}",
    "body.reader-theme-night .gmail-message-head:hover{background:#2a3646}",
    "body.reader-theme-night .gmail-document,body.reader-theme-night .letter-body{color:#eef1f7}",
    "body.reader-theme-night .gmail-message-person small,body.reader-theme-night .gmail-message-date,body.reader-theme-night .gmail-source,body.reader-theme-night .gmail-conversation-sub{color:#b9c5d7}",
    "body.reader-theme-night .gmail-tab{color:#b9c5d7}",
    "body.reader-theme-night .gmail-tab.active{color:#9fc0ff}",
    "body.reader-theme-night .gmail-thread-note{background:#303448;color:#e1d3b6;border-color:#66604e}",
    "body.reader-theme-night .gmail-tabs{border-color:#455365}",
    "body.reader-theme-night .gmail-message-actions .ghost,body.reader-theme-night .gmail-toolbar .ghost{background:#2c3950;color:#e5efff;border-color:#52647c}",
    "body.reader-theme-night .gmail-wrap a{color:#adc8ff}",
    "@media(max-width:730px){.archive-filters{padding:3px 10px 9px}.archive-filters select{font-size:11px;max-width:46%}.reader-pref-controls button{font-size:11px;padding:8px}}"
  ].join("\n");
  document.head.appendChild(css);

  function persist(){
    try { localStorage.setItem(KEY,JSON.stringify({size,mode})); } catch (_) {}
  }
  function apply(){
    document.documentElement.style.setProperty("--reading-size",size+"px");
    for(const m of modes)document.body.classList.remove("reader-theme-"+m);
    document.body.classList.add("reader-theme-"+mode);
  }
  function isActive(){return filter.period!=="all"||filter.quality!=="all";}
  function matches(d){
    if(filter.period!=="all"){
      const year=Number(String(d.date||"").slice(0,4));
      if(!Number.isFinite(year))return false;
      let [start,end]=filter.period.split("-").map(Number);
      if(year<start||year>end)return false;
    }
    if(filter.quality==="modern")return Boolean(d.modern||d._legacyAdaptation);
    if(filter.quality==="needsReview")return Boolean(d.needsReview||(Array.isArray(d.ocrFlags)&&d.ocrFlags.length));
    if(filter.quality==="ocr")return d.status==="ocr"&&!d.modern&&!d._legacyAdaptation;
    return true;
  }
  function filterBar(){
    return '<div class="archive-filters" role="group" aria-label="Filter historical letters">'+
    '<select id="filterPeriod" aria-label="Historical period" onchange="JacksonReaderUI.changed()">'+
    [['all','All years'],['1788-1819','1788–1819'],['1820-1828','1820–1828'],['1829-1837','1829–1837'],['1838-1845','1838–1845']].map(([v,l])=>'<option value="'+v+'">'+l+'</option>').join('')+
    '</select><select id="filterQuality" aria-label="Letter text quality" onchange="JacksonReaderUI.changed()">'+
    [['all','All letters'],['modern','Plain English'],['ocr','OCR reading copy'],['needsReview','Needs OCR review']].map(([v,l])=>'<option value="'+v+'">'+l+'</option>').join('')+
    '</select><button id="filterReset" onclick="JacksonReaderUI.clear()" aria-label="Clear filters" style="display:none">Clear</button></div>';
  }
  function sync(){
    const period=document.getElementById("filterPeriod");
    const quality=document.getElementById("filterQuality");
    const reset=document.getElementById("filterReset");
    if(period)period.value=filter.period;
    if(quality)quality.value=filter.quality;
    if(reset)reset.style.display=isActive()?"inline-flex":"none";
  }
  function refresh(){
    if(typeof LIST_LIMIT!=="undefined")LIST_LIMIT=120;
    if(typeof render==="function")render();
  }
  function changed(){
    const period=document.getElementById("filterPeriod"),quality=document.getElementById("filterQuality");
    filter.period=period?period.value:"all";
    filter.quality=quality?quality.value:"all";
    sync();refresh();
  }
  function clear(){
    filter.period="all";filter.quality="all";sync();refresh();
  }
  function controls(){
    return '<span class="reader-pref-controls" role="group" aria-label="Reading display options">'+
      '<button class="ghost" onclick="JacksonReaderUI.adjust(-1)" aria-label="Smaller letter text">A−</button>'+
      '<button class="ghost" onclick="JacksonReaderUI.adjust(1)" aria-label="Larger letter text">A+</button>'+
      '<button class="ghost" onclick="JacksonReaderUI.theme()" aria-label="Change reading background">Theme</button></span>';
  }
  function adjust(delta){
    size=Math.max(limits.min,Math.min(limits.max,size+delta));
    persist();apply();
  }
  function theme(){
    mode=modes[(modes.indexOf(mode)+1)%modes.length];
    persist();apply();
  }
  function annotation(d){
    if(d.modern||d._legacyAdaptation)return "Plain-English adaptation — not verbatim";
    if(d.status==="ocr")return d.needsReview?"OCR needs checking":"Uncorrected OCR";
    return d.sourceChecked?"Source-checked":"Unverified adaptation";
  }
  // Apply after document body exists (module is loaded just before inline logic).
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",apply);
  else apply();
  window.JacksonReaderUI={filter,matches,filterBar,sync,changed,clear,controls,adjust,theme,annotation,getPrefs:()=>({size,mode}),setFilter:(period,quality)=>{filter.period=period;filter.quality=quality;}};
})();
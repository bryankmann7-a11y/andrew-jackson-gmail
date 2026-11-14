/* Gmail-like conversation view for historical correspondence.
   Thread links are inferred from archival evidence; no unseen replies are fabricated. */
(function () {
  "use strict";
  const JACKSON = "Andrew Jackson";
  let cache = null, cacheCount = -1, opened = new Set(), tabById = new Map();
  let noteTimer = null;
  const styles = [
    ".gmail-list-item{display:flex;width:100%;gap:12px;text-align:left;padding:15px 16px;border:0;border-bottom:1px solid var(--line);background:#fff;align-items:flex-start;color:var(--ink)}",
    ".gmail-list-item:hover{background:#f5f8fc}.gmail-list-item.selected{background:#eaf1fc}.gmail-list-item.unread .gmail-who,.gmail-list-item.unread .gmail-subject{font-weight:760}",
    ".gmail-list-copy{flex:1;min-width:0}.gmail-topline{display:flex;justify-content:space-between;align-items:center;gap:8px}.gmail-who{font-size:13.5px;font-weight:670;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.gmail-date{font-size:10.5px;color:var(--muted);flex-shrink:0}.gmail-subject{font-size:12.5px;white-space:nowrap;text-overflow:ellipsis;overflow:hidden;margin-top:5px;font-weight:580}.gmail-preview{font-size:11.5px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:4px}",
    ".gmail-meta{display:flex;align-items:center;flex-wrap:wrap;gap:6px;margin-top:8px;color:#69788a;font-size:10.5px}.gmail-count{background:#e8edf7;color:#3d536f;border-radius:12px;padding:2px 7px;font-weight:700}",
    ".gmail-wrap{max-width:860px;margin:0 auto;padding:22px 20px 50px}.gmail-toolbar{display:flex;gap:7px;flex-wrap:wrap;justify-content:space-between;margin-bottom:15px}.gmail-toolbar .ghost{white-space:nowrap}.gmail-conversation-title{font-size:25px;line-height:1.22;font-weight:730;letter-spacing:-.4px;margin:0 0 9px}.gmail-conversation-sub{font-size:12px;color:var(--muted);margin:0 0 18px;line-height:1.6}",
    ".gmail-message{background:white;border:1px solid #e0e5ed;border-radius:13px;margin:0 0 10px;overflow:hidden;box-shadow:0 2px 12px #24385809}.gmail-message.open{box-shadow:0 4px 23px #24385814;border-color:#cdd9e9}",
    ".gmail-message-head{display:flex;text-align:left;align-items:center;width:100%;gap:12px;padding:17px 18px;border:0;background:#fff;color:var(--ink)}.gmail-message-head:hover{background:#f8fafe}.gmail-message-person{flex:1;min-width:0}.gmail-message-person strong{font-size:13.4px;display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.gmail-message-person small{display:block;font-size:11px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:4px}.gmail-message-date{font-size:11px;flex-shrink:0;color:var(--muted)}.gmail-collapse-symbol{color:#74849b;font-size:16px}",
    ".gmail-content{padding:0 19px 20px 70px}.gmail-message-tools{display:flex;align-items:center;flex-wrap:wrap;gap:8px;margin:8px 0 0}.gmail-thread-note{font-size:11px;color:#77674c;background:#fff8e9;border:1px solid #f0e5c8;padding:8px 12px;margin:0 0 14px;border-radius:8px}.gmail-tabs{margin:16px 0 0;display:flex;gap:12px;border-bottom:1px solid var(--line);overflow:auto}.gmail-tab{padding:9px 1px;border:0;border-bottom:2px solid transparent;background:transparent;color:#647086;font-size:12px;white-space:nowrap}.gmail-tab.active{color:var(--blue);border-color:var(--blue);font-weight:700}.gmail-document{font:15px/1.85 Georgia,'Times New Roman',serif;white-space:pre-wrap;margin:18px 0 8px;overflow-wrap:anywhere}.gmail-document.info{font:13px/1.8 system-ui,sans-serif}.gmail-source{margin-top:15px;font-size:11.5px;color:var(--muted);line-height:1.6}.gmail-note{display:block;min-height:150px;width:100%;border-radius:9px;border:1px solid var(--line);padding:12px;resize:vertical;margin:12px 0}",
    ".gmail-message-actions{display:flex;flex-wrap:wrap;gap:7px;margin-top:14px}.gmail-subdued{font-size:11px;color:var(--muted)}.gmail-footer{font-size:12px;color:var(--muted);padding:16px 0;line-height:1.6}",
    "@media(max-width:730px){.gmail-wrap{padding:12px 10px 40px}.gmail-toolbar{gap:5px}.gmail-conversation-title{font-size:21px}.gmail-message-head{padding:13px 11px;gap:9px}.gmail-message-head .avatar{width:36px;height:36px;flex:0 0 36px}.gmail-message-date{font-size:10px}.gmail-content{padding:0 12px 15px 12px}.gmail-document{font-size:15px;line-height:1.75}.gmail-list-item{padding:13px 10px}.gmail-tabs{gap:10px}}"
  ];
  const css = document.createElement("style");
  css.textContent = styles.join("\n");
  document.head.appendChild(css);

  function matches(a, b) {
    return a.from === b.from && a.to === b.to && a.date === b.date;
  }
  function otherPerson(d) {
    if (d.from === JACKSON && d.to !== JACKSON) return d.to;
    if (d.to === JACKSON && d.from !== JACKSON) return d.from;
    return null;
  }
  function direction(d) {
    return d.from === JACKSON ? "sent" : "received";
  }
  function days(a, b) {
    return Math.round((Date.parse(a.date + "T12:00:00Z") - Date.parse(b.date + "T12:00:00Z")) / 86400000);
  }
  function searchText(d) {
    return [d.from,d.to,d.date,d.subject,d.summary,d.modern,d.original,d.context].join(" ").toLowerCase();
  }
  function excerpt(d, max) {
    let raw = d.summary && !d.summary.toLowerCase().includes("automatically extracted") ? d.summary : (d.modern || d.readable || d.original || "");
    return String(raw).replace(/\s+/g, " ").slice(0, max || 140);
  }
  function build() {
    const byKey = new Map();
    const originals = new Map();
    const all = data.slice();
    for (const d of all) {
      if (d.status === "ocr") {
        const k = d.date + "|" + d.from + "|" + d.to;
        if (!originals.has(k)) originals.set(k, d);
      }
    }
    const keep = [];
    for (const d of all) {
      const k = d.date + "|" + d.from + "|" + d.to;
      const canonical = originals.get(k);
      if (d.id && d.id.startsWith("j-") && canonical) {
        if (!byKey.has(k)) byKey.set(k, d);
        continue;
      }
      keep.push(d);
    }
    for (const d of keep) {
      const k = d.date + "|" + d.from + "|" + d.to;
      const legacy = byKey.get(k);
      if (legacy && d.status === "ocr" && !d.modern && legacy.modern) {
        d._legacyAdaptation = legacy.modern;
        d._legacyId = legacy.id;
      }
    }
    keep.sort((a,b) => String(a.date).localeCompare(String(b.date)) || String(a.id).localeCompare(String(b.id)));
    const groups = [], byMessage = new Map(), byThread = new Map();
    const recentByOther = new Map();
    for (const d of keep) {
      const other = otherPerson(d);
      const history = other ? (recentByOther.get(other) || []) : [];
      let group = null, how = "standalone";
      if (d.replyToId && byMessage.has(d.replyToId)) {
        const candidate = byMessage.get(d.replyToId);
        if (candidate.other === other && days(d,candidate.messages[candidate.messages.length-1]) >= 0) {
          group = candidate;
          how = "suggested-reference";
        }
      }
      if (!group && other && history.length) {
        const replyWord = /\b(your (letter|note|communication)|(?:received|recd|receipt of) your letter|in (answer|reply) to|answer to your)\b/i.test(String(d.original || d.modern || "").slice(0,2400));
        const options = history.filter(prev => {
          const lag = days(d,prev.message);
          const span = days(d,prev.thread.messages[0]);
          return prev.direction !== direction(d) && lag >= 0 && lag <= 30 && span <= 75 && (lag <= 7 || (lag <= 30 && replyWord));
        });
        if (options.length) {
          const winner = options[options.length - 1];
          group = winner.thread;
          how = "date-and-participants";
        }
      }
      if (!group) {
        group = {id:d.id,other:other || "Other correspondents",messages:[], links:[],first:d.date,last:d.date};
        groups.push(group);
        byThread.set(group.id,group);
      }
      if (group.messages.length) group.links.push({id:d.id,via:how});
      group.messages.push(d);
      group.last = d.date;
      byMessage.set(d.id,group);
      if (other) {
        history.push({message:d,thread:group,direction:direction(d)});
        while(history.length > 45) history.shift();
        recentByOther.set(other,history);
      }
    }
    groups.sort((a,b) => a.last.localeCompare(b.last) || a.id.localeCompare(b.id));
    return {groups,byMessage,byThread};
  }
  function model() {
    if (!cache || cacheCount !== data.length) {
      cache = build();
      cacheCount = data.length;
      opened.clear();
    }
    return cache;
  }
  function folderMatches(d, folder) {
    if (folder === "out") return d.from === JACKSON;
    if (folder === "in") return d.to === JACKSON;
    if (folder === "starred") return starred.has(d.id) || Boolean(d._legacyId && starred.has(d._legacyId));
    if (folder === "unread") return !read.has(d.id) && !(d._legacyId && read.has(d._legacyId));
    return true;
  }
  function list() {
    const query = state.query.trim().toLowerCase();
    const groups = model().groups.filter(t => t.messages.some(d => folderMatches(d,state.folder) && (!window.JacksonReaderUI || JacksonReaderUI.matches(d)) && (!query || searchText(d).includes(query))));
    groups.sort((a,b) => state.sort === "old" ? a.last.localeCompare(b.last) : b.last.localeCompare(a.last));
    return groups;
  }
  function title(t) {
    return "Correspondence with " + t.other;
  }
  function newest(t) {
    return t.messages[t.messages.length - 1];
  }
  function hasUnread(t) {
    return t.messages.some(d => !read.has(d.id) && !(d._legacyId && read.has(d._legacyId)));
  }
  function starredIn(t) {
    return t.messages.some(d => starred.has(d.id) || (d._legacyId && starred.has(d._legacyId)));
  }
  function renderRow(t) {
    const latest = newest(t);
    const participants = t.messages.length > 1 ? "Jackson, " + t.other : (latest.from === JACKSON ? "Jackson → " + latest.to : latest.from);
    const badge = t.messages.length > 1 ? "<span class='gmail-count'>" + t.messages.length + "</span>" : "";
    const quality = window.JacksonReaderUI ? JacksonReaderUI.annotation(latest) : (latest.modern?"Plain English":"Uncorrected OCR");
    return "<button class='gmail-list-item " + (model().byMessage.get(state.id)===t?"selected ":"") + (hasUnread(t)?"unread":"") +
      "' onclick=\"GmailThreadUI.select('" + escapeHTML(t.id) + "')\">" +
      avatar(t.other) +
      "<span class='gmail-list-copy'><span class='gmail-topline'><span class='gmail-who'>" + escapeHTML(participants) + " " + badge + "</span><span class='gmail-date'>" +
      escapeHTML(shortDate(latest.date)) + "</span></span><span class='gmail-subject'>" +
      escapeHTML(t.messages.length > 1 ? title(t) : latest.subject) + "</span><span class='gmail-preview'>" +
      escapeHTML(excerpt(latest)) + "</span><span class='gmail-meta'><span>" + (t.messages.length > 1 ? "Conversation · possible reply links" : "Letter") +
      "</span><span> · " + escapeHTML(quality) + "</span>" + (starredIn(t)?"<span style='color:#c28b16'>★ Starred</span>":"") + "</span></span></button>";
  }
  function renderTab(d, tab) {
    const legacy = !d.modern && d._legacyAdaptation;
    if (tab === "notes") {
      return "<div class='gmail-document info'><p>Notes are saved locally on this device.</p><textarea class='gmail-note' id='gmail-note-" +
        escapeHTML(d.id) + "' oninput=\"GmailThreadUI.noteChanged('" + escapeHTML(d.id) + "')\" placeholder='Your notes on this letter...'>" +
        escapeHTML(notes[d.id] || (d._legacyId && notes[d._legacyId]) || "") +
        "</textarea><button class='ghost' onclick=\"GmailThreadUI.saveNote('" + escapeHTML(d.id) + "')\">Save note</button></div>";
    }
    if (tab === "background") {
      return "<div class='gmail-document info'><b>Historical context</b><p>" + escapeHTML(d.context || d.summary || "Context has not been independently researched.") +
        "</p><b>Earlier correspondence</b><p>" + escapeHTML(d.replyContext || "No earlier surviving letter has been independently identified.") +
        "</p></div>";
    }
    if (tab === "original") {
      return "<div class='gmail-document'>" + escapeHTML(d.original || "The source transcription is not loaded.") +
        "</div><div class='gmail-source'>Uncorrected OCR: spelling, dates, page breaks and document boundaries may be wrong. Verify against the scan before quoting.</div>";
    }
    const text = d.modern || (legacy ? d._legacyAdaptation : d.readable || d.original || "");
    const annotation = d.modern ? "Human-written condensed rendering; not scan-verified." :
      legacy ? "Earlier-chat modern-English adaptation; not checked against the scanned original." :
      "Readable OCR only — this has NOT been translated into modern English.";
    return "<div class='gmail-document'>" + escapeHTML(text) + "</div><div class='gmail-source'>" + annotation + "</div>";
  }
  function renderMessage(d, t) {
    const open = opened.has(d.id);
    const tab = tabById.get(d.id) || "reading";
    const source = sourceHref(d.source);
    const reading = d.modern || d._legacyAdaptation ? "Plain English" : "Reading copy";
    const badge = d.status === "ocr" ? "Uncorrected OCR" : d.sourceChecked ? "Edited and source checked" : "Earlier adaptation, unchecked";
    let tabs = [["reading",reading],["original","Original OCR"],["background","Background"],["notes","My notes"]].map(pair =>
      "<button class='gmail-tab " + (tab===pair[0]?"active":"") + "' onclick=\"GmailThreadUI.tab('" + escapeHTML(d.id) + "','" + pair[0] + "')\">" + pair[1] + "</button>").join("");
    const issues = Array.isArray(d.ocrFlags) ? d.ocrFlags : [];
    const flagLabels = {
      letter_digit_fusion:"digits fused into words",
      symbol_in_word:"stray symbols inside words",
      word_interrupted_by_footnote:"footnote interrupting a word",
      possible_multiple_documents:"possible mixed letter boundaries",
      truncated_extraction:"text cut off during extraction",
      unusually_long_extraction:"unusually long OCR passage",
      suspicious_correspondent_heading:"uncertain correspondent heading",
      unclear_scan_text:"unreadable scan fragments"
    };
    const auditNote = issues.length ? "<div class='gmail-thread-note'>OCR needs checking: " +
      escapeHTML(issues.map(x=>flagLabels[x]||x).join("; ")) +
      ". Compare with the original book scan before quoting.</div>" : "";
    let body = "<div class='gmail-content'><div class='gmail-subdued'>" + escapeHTML(badge) +
      " · " + escapeHTML(d.from) + " → " + escapeHTML(d.to) + "</div>" +
      auditNote + "<div class='gmail-tabs'>" + tabs + "</div>" + renderTab(d, tab) +
      "<div class='gmail-source'>" + escapeHTML(d.sourceCitation || "Source page not independently verified.") +
      (source ? " · <a href='" + source + "' target='_blank' rel='noopener'>View source book</a>" : "") +
      "</div><div class='gmail-message-actions'><button class='ghost' onclick=\"GmailThreadUI.star('" + escapeHTML(d.id) + "')\">" +
      (starred.has(d.id)?"★ Starred":"☆ Star") + "</button><button class='ghost' onclick=\"copyLetter('" + escapeHTML(d.id) + "')\">Copy letter</button>" +
      "<button class='ghost' onclick=\"openProfile('" + safeKey(d.from) + "')\">Sender profile</button></div></div>";
    return "<section class='gmail-message " + (open?"open":"") + "' id='gmail-message-" + escapeHTML(d.id) + "'>" +
      "<button class='gmail-message-head' aria-expanded='" + String(open) + "' onclick=\"GmailThreadUI.toggle('" + escapeHTML(d.id) + "')\">" +
      avatar(d.from) + "<span class='gmail-message-person'><strong>" + escapeHTML(d.from) + "</strong><small>To: " +
      escapeHTML(d.to) + (open ? "" : " · " + escapeHTML(excerpt(d,95))) + "</small></span><span class='gmail-message-date'>" +
      escapeHTML(dateFmt(d.date)) + "</span><span class='gmail-collapse-symbol'>" + (open?"⌃":"⌄") + "</span></button>" +
      (open ? body : "") + "</section>";
  }
  function renderThread(t, groups) {
    if (!t) return "<div class='empty'><h3>No conversations found</h3>Try another search or folder.</div>";
    if (!opened.size) opened.add(newest(t).id);
    const index = groups.indexOf(t), previous = groups[index-1], next = groups[index+1];
    const linked = t.messages.length > 1;
    const participants = linked ? "Conversation of " + t.messages.length + " letters · " +
      escapeHTML(dateFmt(t.first)) + " – " + escapeHTML(dateFmt(t.last)) : "Single historical letter · " + escapeHTML(dateFmt(t.first));
    return "<div class='gmail-wrap'><div class='gmail-toolbar'><div class='right-tools'>" +
      "<button class='ghost mobile-back' onclick='backMobile()'>← Inbox</button>" +
      "<button class='ghost' onclick=\"GmailThreadUI.expandAll()\">Expand all</button>" +
      "<button class='ghost' onclick=\"GmailThreadUI.collapseAll()\">Collapse</button></div>" +
      (window.JacksonReaderUI?JacksonReaderUI.controls():"") +
      "<div class='right-tools'><button class='ghost' " + (previous?"":"disabled") + " onclick=\"GmailThreadUI.select('" +
      (previous?escapeHTML(previous.id):"") + "')\">‹</button><button class='ghost' " + (next?"":"disabled") +
      " onclick=\"GmailThreadUI.select('" + (next?escapeHTML(next.id):"") + "')\">›</button></div></div>" +
      "<h2 class='gmail-conversation-title'>" + escapeHTML(linked?title(t):newest(t).subject) + "</h2>" +
      "<p class='gmail-conversation-sub'>" + participants + "</p>" +
      (linked ? "<div class='gmail-thread-note'>Letters are grouped using names, dates and possible references to earlier letters. This is an archival reconstruction, <b>not a verified reply chain</b>. No missing replies have been invented.</div>" : "") +
      t.messages.map(d=>renderMessage(d,t)).join("") +
      "<div class='gmail-footer'>End of correspondence in this thread. Historical letters presented in an email-style reader; not actual emails.</div></div>";
  }
  function render() {
    const groups = list();
    const refs = model();
    let t = refs.byMessage.get(state.id);
    if (!t || !groups.includes(t)) {
      t = groups[0] || null;
      if (t) state.id = newest(t).id;
    }
    const oldId = window.__gmailThreadLastId;
    if (t && oldId !== t.id) {
      opened = new Set([state.id && t.messages.some(d=>d.id===state.id) ? state.id : newest(t).id]);
      window.__gmailThreadLastId = t.id;
    }
    $("#recordCount").textContent = groups.length.toLocaleString() + " conversations · " + data.length.toLocaleString() + " records";
    const names = {all:"All conversations",out:"Sent conversations",in:"Received conversations",starred:"Starred conversations",unread:"Unread conversations"};
    $("#viewHeading").textContent = names[state.folder] || "Correspondence";
    $("#sort").value = state.sort;
    const container = $("#records");
    const oldScroll = container.scrollTop;
    container.innerHTML = groups.slice(0, LIST_LIMIT).map(renderRow).join("") || "<div class='empty'><h3>No matches</h3>Try another search, folder, or year.</div>";
    container.scrollTop = oldScroll;
    $("#reader").innerHTML = renderThread(t, groups);
    $("#archiveNotice").style.display = "none";
  }
  function select(id) {
    const t = model().byThread.get(id) || model().byMessage.get(id);
    if (!t) return;
    if(window.JacksonNav)JacksonNav.enter();
    if (state.folder === "unread") state.folder = "all";
    state.profile = false;
    state.id = newest(t).id;
    opened = new Set([state.id]);
    for(const d of t.messages) read.add(d.id);
    save(false);
    window.__gmailThreadLastId=t.id;
    if(typeof window.render==='function')window.render();else render();
    $("#reader").classList.add("show");
    $("#reader").scrollTop=0;
  }
  function sync() {
    const scroller=$("#reader");
    const y=scroller.scrollTop;
    if(typeof window.render==='function')window.render();else render();
    scroller.scrollTop=y;
  }
  function toggle(id) {
    if(opened.has(id)) opened.delete(id);
    else {opened.add(id); state.id=id; read.add(id);}
    save(false);sync();
  }
  function expandAll() {
    const t=model().byMessage.get(state.id);
    if(t) t.messages.forEach(d=>opened.add(d.id));
    sync();
  }
  function collapseAll() {
    opened.clear();
    const t=model().byMessage.get(state.id);
    if(t) opened.add(newest(t).id);
    sync();
  }
  function tab(id,value) {
    tabById.set(id,value); opened.add(id);sync();
  }
  function star(id) {
    starred.has(id) ? starred.delete(id) : starred.add(id);
    save(false);sync();
  }
  function saveNote(id) {
    const el=document.getElementById("gmail-note-"+id);
    if(el) notes[id]=el.value;
    save();toast("Note saved on this device");
  }
  function noteChanged(id) {
    clearTimeout(noteTimer);
    const el=document.getElementById("gmail-note-"+id);
    if(el) notes[id]=el.value;
    noteTimer=setTimeout(function(){save(false);},450);
  }
  function counts(folder) {
    if(folder==="all")return model().groups.length;
    return model().groups.filter(t=>t.messages.some(d=>folderMatches(d,folder))).length;
  }
  function getFilteredCount(){return list().length;}
  window.GmailThreadUI={render,select,toggle,expandAll,collapseAll,tab,star,saveNote,noteChanged,counts,getFilteredCount,threadForMessage:function(id){return model().byMessage.get(id)},setExpanded:function(id){opened=new Set([id]);}};
})();

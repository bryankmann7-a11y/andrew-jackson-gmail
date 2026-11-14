/* Navigation history for the Android WebView and responsive browser.
   Back closes dialogs/drawers before the reader, then restores inbox scroll,
   query, folder and the previously visible conversation. */
(function(){
  "use strict";
  const history = [];
  const LIMIT=35;
  let restoring=false;

  function el(selector){return document.querySelector(selector);}
  function snapshot(){
    const records=el("#records"),reader=el("#reader"),search=el("#search");
    return {
      folder:state.folder,id:state.id,view:state.view,tab:state.tab,
      profile:state.profile,sort:state.sort,query:state.query,
      listLimit:LIST_LIMIT,
      listScroll:records?records.scrollTop:0,
      readerScroll:reader?reader.scrollTop:0,
      readerOpen:Boolean(reader && reader.classList.contains("show")),
      searchValue:search?search.value:state.query
    };
  }
  function enter(){
    if(restoring)return false;
    // At most one inbox screen per navigation action.
    history.push(snapshot());
    if(history.length>LIMIT)history.shift();
    return true;
  }
  function restore(s){
    restoring=true;
    try{
      state.folder=s.folder;state.id=s.id;state.view=s.view;state.tab=s.tab;
      state.profile=s.profile;state.sort=s.sort;state.query=s.query;
      LIST_LIMIT=s.listLimit;
      const search=el("#search");if(search)search.value=s.searchValue;
      const mode=el("#viewMode");
      if(mode)mode.querySelectorAll("button").forEach(b=>
        b.classList.toggle("selected",b.dataset.view===state.view));
      const reader=el("#reader");if(reader)reader.classList.remove("show");
      if(state.view==="mail"&&window.GmailThreadUI&&state.id){
        GmailThreadUI.setExpanded(state.id);
      }
      render();
      const list=el("#records");if(list)list.scrollTop=s.listScroll;
      const display=el("#reader");
      if(display){
        display.classList.toggle("show",s.readerOpen);
        display.scrollTop=s.readerScroll;
      }
    }finally{restoring=false;}
  }
  function back(){
    const modal=el("#modalMount");
    if(modal&&modal.querySelector(".modal-back")){
      if(typeof bulkLoading!=="undefined" && bulkLoading && typeof cancelBulkLoad==="function"){
        cancelBulkLoad();
      }else if(typeof closeModal==="function"){
        closeModal();
      }else{modal.innerHTML="";}
      return true;
    }
    const sidebar=el("#sidebar");
    if(sidebar&&sidebar.classList.contains("open")){
      if(typeof toggleNav==="function")toggleNav(false);
      else sidebar.classList.remove("open");
      return true;
    }
    // Give the keyboard Back action priority while editing notes or searching.
    if(document.activeElement&&/^(INPUT|TEXTAREA)$/.test(document.activeElement.tagName)){
      document.activeElement.blur();
      return true;
    }
    const reader=el("#reader");
    if(reader&&reader.classList.contains("show")){
      if(history.length)restore(history.pop());
      else {reader.classList.remove("show");state.profile=false;}
      return true;
    }
    // An off-screen navigation history should not trap the user in the app.
    history.length=0;
    if(state.query){
      state.query="";
      const search=el("#search");if(search)search.value="";
      LIST_LIMIT=120;
      render();
      return true;
    }
    if(state.folder!=="all"){
      state.folder="all";state.profile=false;LIST_LIMIT=120;
      render();
      return true;
    }
    return false;
  }
  window.JacksonNav={enter,back,canBack:function(){
    return Boolean(history.length||(el("#reader")?.classList.contains("show"))||
      el("#modalMount")?.querySelector(".modal-back")||
      el("#sidebar")?.classList.contains("open")||state.query||state.folder!=="all");
  },historySize:()=>history.length,restore};
})();
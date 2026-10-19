/* Separate leaderboard, detail, comparison and submission views share the same in-memory upload session; navigation never reloads. */
(function(){'use strict';
  const $=id=>document.getElementById(id);let registration=true,currentPage=null,compareContext=null;
  function selected(){const hash=location.hash.slice(1);
    if(['submit','registration-section','upload-section','report-section','registration-start'].includes(hash))return 'submit';
    if(hash.startsWith('model=')||hash.startsWith('paper-model='))return 'detail';
    if(hash==='compare'||hash.startsWith('left=')||hash.startsWith('paper-compare='))return 'compare';
    if(['models','public-pair-section','advanced-metrics','home-section'].includes(hash)||hash.startsWith('model=')||hash.startsWith('left='))return 'models';
    return location.pathname==='/submit'?'submit':location.pathname==='/compare'?'compare':'models';}
  function show(page,{navigate=false}={}){
    if(!registration)page='submit';currentPage=page;
    $('explore-page').hidden=page!=='models';$('submit-page').hidden=page!=='submit';$('detail-page').hidden=page!=='detail';$('compare-page').hidden=page!=='compare';
    for(const a of document.querySelectorAll('#page-navigation a[data-view]')){
      if(a.dataset.view===page)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');
    }
    window.dispatchEvent(new CustomEvent('koevd-view-change',{detail:page}));
    if(navigate)history.pushState(null,'','#'+page);
  }
  window.KoEVDNavigation={show,current:()=>currentPage,setCompareContext(handler){compareContext=handler;},configure(enabled){registration=enabled;$('models-navigation').hidden=!enabled;show(selected());}};
  for(const a of document.querySelectorAll('#page-navigation a[data-view]'))a.addEventListener('click',e=>{
    e.preventDefault();if(a.dataset.view==='compare'&&currentPage==='detail'&&compareContext){compareContext();return;}show(a.dataset.view,{navigate:true});$('page-title').focus();});
  window.addEventListener('hashchange',()=>show(selected()));window.addEventListener('popstate',()=>show(selected()));show(selected());
}());

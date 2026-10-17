/* Two views share the same in-memory upload session; navigation never reloads. */
(function(){'use strict';
  const $=id=>document.getElementById(id);let registration=true;
  function selected(){const hash=location.hash.slice(1);
    if(['submit','registration-section','upload-section','report-section','registration-start'].includes(hash))return 'submit';
    if(['models','public-pair-section','advanced-metrics','home-section'].includes(hash)||hash.startsWith('model=')||hash.startsWith('left='))return 'models';
    return location.pathname==='/submit'?'submit':'models';}
  function show(page,{navigate=false}={}){
    if(!registration)page='submit';
    $('explore-page').hidden=page!=='models';$('submit-page').hidden=page!=='submit';
    for(const a of document.querySelectorAll('#page-navigation a[data-view]')){
      if(a.dataset.view===page)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');
    }
    window.dispatchEvent(new CustomEvent('koevd-view-change',{detail:page}));
    if(navigate)history.pushState(null,'','#'+(page==='submit'?'submit':'models'));
  }
  window.KoEVDNavigation={show,configure(enabled){registration=enabled;$('models-navigation').hidden=!enabled;show(selected());}};
  for(const a of document.querySelectorAll('#page-navigation a[data-view]'))a.addEventListener('click',e=>{
    e.preventDefault();show(a.dataset.view,{navigate:true});$('page-title').focus();});
  window.addEventListener('hashchange',()=>show(selected()));window.addEventListener('popstate',()=>show(selected()));show(selected());
}());

/* Bounded retries for public numerical reads only; never replay a write. */
(function(root,factory){
  if(typeof module==='object'&&module.exports)module.exports=factory();
  else root.KoEVDPublicReads=factory();
}(typeof window==='object'?window:this,function(){'use strict';
  const delays=[1000,2500];
  function allowed(method,path){
    if(method!=='GET'||typeof path!=='string')return false;
    const pathname=path.split('?')[0];
    return ['/api/public/submissions','/api/public/leaderboard','/api/public/compare'].includes(pathname)||
      /^\/api\/public\/submissions\/[a-zA-Z0-9_-]+\/profile$/.test(pathname);
  }
  function transient(status,code){
    // Integrity, stale-state, permissions and withdrawal failures must not be
    // hidden by a retry or an older cached projection.
    if(code&&!['durability_unavailable','registration_busy'].includes(code))return false;
    return [502,503,504].includes(status);
  }
  async function request(fetchOnce,{method='GET',path,onRetry=()=>{},sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms))}={}){
    for(let attempt=0;;attempt++){
      let response;
      try{response=await fetchOnce();}
      catch(error){
        if(!allowed(method,path)||attempt>=delays.length||!(error instanceof TypeError))throw error;
        onRetry({attempt:attempt+2,maxAttempts:delays.length+1});await sleep(delays[attempt]);continue;
      }
      if(response.ok||!allowed(method,path)||attempt>=delays.length)return response;
      let value;try{value=await response.clone().json();}catch{value=null;}
      if(!transient(response.status,value?.error?.code))return response;
      onRetry({attempt:attempt+2,maxAttempts:delays.length+1});await sleep(delays[attempt]);
    }
  }
  function explanation(error){
    if(error?.code==='durability_unavailable')return 'Published results could not be checked right now. This is a service check, not a rejection of your file. Try again shortly.';
    if(error?.code==='registration_busy')return 'Published results are busy. Try again shortly.';
    if(['checkpoint_integrity','checkpoint_stale','checkpoint_target_not_private'].includes(error?.code))
      return 'Published results are unavailable while saved-state consistency is checked. Try again later.';
    if(error instanceof TypeError)return 'The service could not be reached. Check your connection and try again.';
    return error?.message||'Published results could not be loaded. Try again.';
  }
  return {request,explanation};
}));

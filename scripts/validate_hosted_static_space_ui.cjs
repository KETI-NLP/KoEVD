/* Isolated hosted Static check. Anonymous mode forbids credentials. Private
 * owner-access cookies arrive on stdin, stay in
 * memory, and are never written to receipts, URLs, screenshots, or HAR files.
 * This verifies hosted analysis, not submitter OAuth or publication approval. */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const assert=require('node:assert/strict');
const {chromium}=require('playwright');
function arg(n,f){const i=process.argv.indexOf(n);return i<0?f:process.argv[i+1];}
const root=path.resolve(arg('--space',null)),out=path.resolve(arg('--output',null));
const files=JSON.parse(arg('--files','[]')).map(x=>path.resolve(x));
const expected=path.resolve(arg('--expected',null)),resamples=arg('--resamples','100');
const anonymous=process.argv.includes('--anonymous');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
function normalizeIndex(bytes){
  const text=bytes.toString('utf8'),match=text.match(/<script>window\.huggingface=\{variables:(\{[^\n]*\})\};<\/script>/);
  assert(match,'Expected HF Static variables injection');
  const variables=JSON.parse(match[1]);assert.deepEqual(Object.keys(variables),['SPACE_CREATOR_USER_ID']);
  assert(/^[a-f0-9]{24}$/.test(variables.SPACE_CREATOR_USER_ID));
  return Buffer.from(text.slice(0,match.index)+text.slice(match.index+match[0].length),'utf8');
}
assert(!fs.existsSync(out),'Use a fresh private output directory');fs.mkdirSync(out,{recursive:true});
let browser;const requests=[],errors=[],external=[],responses=[],redirects=[],refetches=[];
async function main(){
  const access=JSON.parse(fs.readFileSync(0,'utf8'));
  const u=new URL(access.origin);assert.equal(u.protocol,'https:');assert(u.hostname.endsWith('.static.hf.space'));
  assert.equal(u.origin,access.origin);assert.equal(u.pathname,'/');assert(!u.search&&!u.hash&&!u.username);
  const manifest=JSON.parse(fs.readFileSync(path.join(root,'deployment-manifest.json'),'utf8'));
  for(const [name,item] of Object.entries(manifest.files)){
    const file=path.resolve(root,name);assert(file.startsWith(root+path.sep));
    const raw=fs.readFileSync(file);assert.equal(raw.length,item.bytes);assert.equal(hash(raw),item.sha256);
  }
  assert(Array.isArray(access.cookies));
  if(anonymous){assert.equal(access.mode,'anonymous');assert.deepEqual(access.cookies,[]);}
  else{assert.notEqual(access.mode,'anonymous');assert(access.cookies.length>0);}
  const secrets=access.cookies.map(c=>c.value);
  const redact=s=>secrets.reduce((v,key)=>v.split(key).join('[redacted]'),String(s));
  const cookies=access.cookies.map(c=>{
    assert.equal(c.domain,u.hostname);assert.equal(c.path,'/');assert(c.secure&&c.httpOnly);
    assert(/^hf_jwt_[a-f0-9]+$/.test(c.name));assert(c.value.length>20);
    return {name:c.name,value:c.value,domain:c.domain,path:'/',secure:true,httpOnly:true,sameSite:'None'};
  });
  browser=await chromium.launch({headless:true,executablePath:arg('--browser-executable',process.env.KOEVD_TEST_BROWSER)});
  const context=await browser.newContext({acceptDownloads:true,viewport:{width:1440,height:1050}});
  if(!anonymous)await context.addCookies(cookies);
  const assetRedirects=new Map();
  function assetRequest(req){
    let first=req;while(first.redirectedFrom())first=first.redirectedFrom();
    const initial=new URL(first.url()),url=new URL(req.url());
    const name=initial.pathname==='/'?'index.html':decodeURIComponent(initial.pathname.slice(1));
    if(initial.origin!==access.origin||initial.search||!Object.hasOwn(manifest.files,name))return null;
    if(url.origin===access.origin&&!url.search)return name;
    // This origin was observed in the service's read-only asset redirects. The
    // full signed URL is matched in memory, never stored in evidence.
    if(url.origin==='https://us.aws.cdn.hf.co'&&assetRedirects.get(req.url())===name)return name;
    return null;
  }
  context.on('request',req=>{
    const url=new URL(req.url());if(url.protocol==='blob:')return;
    if(anonymous&&(req.headers().authorization||req.headers().cookie))errors.push('Unexpected credential in anonymous request');
    const name=assetRequest(req),bodyBytes=req.postDataBuffer()?.length||0;
    requests.push({method:req.method(),asset:name,origin:url.origin,query_present:!!url.search,
      redirected:!!req.redirectedFrom(),bodyBytes});
    if(!name||req.method()!=='GET'||bodyBytes){external.push({origin:url.origin,path:url.pathname});errors.push('Unexpected hosted network request');}
  });
  await context.route('**/*',async route=>{
    const req=route.request();
    if(anonymous&&(req.headers().authorization||req.headers().cookie))return route.abort();
    if(!assetRequest(req)||req.method()!=='GET'||req.postDataBuffer()?.length)return route.abort();
    await route.continue();
  });
  const pending=[];
  context.on('response',response=>{
    pending.push((async()=>{
      const url=new URL(response.url()),name=assetRequest(response.request());
      assert(name,'Unregistered served response');
      if(response.status()===302){
        const target=new URL(response.headers().location,response.url());
        assert.equal(url.origin,access.origin);assert.equal(target.origin,'https://us.aws.cdn.hf.co');
        assert(target.pathname.startsWith('/xet-bridge-us/'));assert(target.search);
        assetRedirects.set(target.href,name);
        redirects.push({asset:name,status:302,from_origin:url.origin,to_origin:target.origin,signed_query_present:true});
        return;
      }
      assert.equal(response.status(),200,'Hosted asset status: '+name);
      let bytes,verification='browser_response_body';
      try{bytes=await response.body();}catch(error){
        // Chrome's inspector can evict the full69MB index while the worker has
        // already consumed/hash-checked it. Independently re-read the exact
        // observed asset URL, without copying headers/cookies across origins.
        if(!String(error.message).includes('evicted from inspector cache'))throw error;
        const fetched=await context.request.get(response.url(),{maxRedirects:0,timeout:120000});
        assert.equal(fetched.status(),200);bytes=await fetched.body();
        verification='independent_asset_refetch_after_inspector_eviction';
        refetches.push({asset:name,origin:url.origin,method:'GET',bodyBytes:0,status:fetched.status(),bytes:bytes.length});
      }
      const normalized=name==='index.html'?normalizeIndex(bytes):bytes;
      assert.equal(hash(normalized),manifest.files[name].sha256,'Hosted asset hash: '+name);
      responses.push({asset:name,origin:url.origin,status:response.status(),bytes:bytes.length,sha256:hash(bytes),
        normalized_sha256:hash(normalized),provider_variables_injection:name==='index.html',verification});
    })().catch(e=>errors.push(redact(e.message))));
  });
  const page=await context.newPage();
  const inspector=await context.newCDPSession(page);
  await inspector.send('Network.enable',{maxTotalBufferSize:256*1024*1024,maxResourceBufferSize:128*1024*1024});
  page.on('pageerror',e=>errors.push(redact(e.message)));
  page.on('console',m=>{if(m.type()==='error')errors.push(redact(m.text()));});
  await page.goto(access.origin+'/index.html',{waitUntil:'domcontentloaded',timeout:120000});
  await page.locator('#scope').filter({hasText:/./}).waitFor({timeout:120000});
  await page.screenshot({path:path.join(out,'initial-analysis.png')});
  await page.locator('#files').setInputFiles(files);await page.locator('#resamples').fill(resamples);
  const began=performance.now();await page.locator('#analyze').click();
  await page.waitForFunction(()=>document.getElementById('status').textContent.includes('분석 완료')||document.getElementById('status').textContent.startsWith('분석 거부:'),null,{timeout:600000});
  const status=await page.locator('#status').textContent();assert(status.startsWith('분석 완료'),status);
  const elapsed=(performance.now()-began)/1000;
  const names=['profile-v2.json','cases-v2.jsonl','metrics-v2.csv','report-v2.md','report-v2.html'];
  const outputs={};
  for(const name of names){const p=page.waitForEvent('download');await page.getByRole('link',{name,exact:true}).click();
    const download=await p;await download.saveAs(path.join(out,name));assert.equal(download.suggestedFilename(),name);
    const data=fs.readFileSync(path.join(out,name));outputs[name]={bytes:data.length,sha256:hash(data)};
    const native=path.join(path.dirname(expected),name);
    assert.equal(outputs[name].sha256,hash(fs.readFileSync(native)),'Native output mismatch: '+name);
  }
  const got=JSON.parse(fs.readFileSync(path.join(out,'profile-v2.json'),'utf8'));
  assert.deepEqual(got,JSON.parse(fs.readFileSync(expected,'utf8')));
  const frame=page.frameLocator('#report');await frame.locator('#tab-overview[aria-selected="true"]').waitFor();
  for(const tab of ['task1','task2','task3','task4','task5','comparison','cases','method']){
    await frame.locator('#tab-'+tab).click();assert((await frame.locator('#view h1').textContent()).length>3);
  }
  await frame.locator('#tab-comparison').click();await page.screenshot({path:path.join(out,'desktop-comparison.png')});
  await frame.locator('#tab-cases').click();await frame.locator('.case-card summary').first().click();
  assert.equal(await frame.locator('img,object').count(),0);
  assert.equal(await frame.locator('body').evaluate(()=>Boolean(globalThis.__KOEVD_INJECTED__)),false);
  await page.screenshot({path:path.join(out,'desktop-cases.png')});
  await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(out,'mobile.png')});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  await page.locator('#clear').click();assert(await page.locator('#report').isHidden());
  assert.equal(await page.locator('#downloads a').count(),0);await Promise.all(pending);
  assert.equal(external.length,0);assert.equal(errors.length,0);
  assert(requests.every(r=>r.method==='GET'&&r.bodyBytes===0&&r.asset&&(!r.query_present||r.redirected)));
  assert.equal(responses.length,requests.filter(r=>!r.redirected).length);
  const receipt={scope:anonymous?'Actual public HF Static anonymous direct app analysis; not Hub parent full flow/shared registration':'Actual private HF Static direct app analysis; not Hub parent iframe/submitter OAuth/storage/publication',
    anonymous_access:anonymous,initial_cookies:cookies.length,
    origin:access.origin,revision:access.revision,browser:browser.version(),seconds:elapsed,
    resamples:Number(resamples),seed:1729,profile_exact:true,all_five_files_byte_exact:true,
    outputs,requests,responses,service_asset_redirects:redirects,independent_asset_refetches:refetches,
    unexpected_external:external,errors,cleared:true,credential_persisted:false,
    actual_result_transmitted:false,shared_registration_verified:false,submitter_OAuth_verified:false};
  fs.writeFileSync(path.join(out,'evidence.json'),JSON.stringify(receipt,null,2));
  console.log(JSON.stringify({seconds:elapsed,profile_exact:true,outputs:5,GET_requests:requests.length,
    hosted_asset_hashes:responses.length,service_asset_redirects:redirects.length,
    independent_asset_refetches:refetches.length,unexpected_external:0,errors:0,actual_result_transmitted:false}));
}
main().catch(e=>{
  // Do not serialize the exception/stack: third-party errors can contain URLs.
  process.exitCode=1;fs.writeFileSync(path.join(out,'failure.json'),JSON.stringify({scope:'hosted Static check failed',
    error_name:e.name,errors,requests,responses,service_asset_redirects:redirects,
    independent_asset_refetches:refetches,unexpected_external:external,credential_persisted:false},null,2));
  console.error('Hosted Static check failed; see private failure.json');
}).finally(async()=>{if(browser)await browser.close();});

/* Anonymous Hub parent -> embedded app file selection -> native-exact downloads.
 * Uses a fresh context, no HF tokens/profile, and blocks all HTTP writes.
 * Parent analytics/assets are separate from the full direct-app network audit. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const {chromium}=require('playwright');
function arg(n){const i=process.argv.indexOf(n);assert(i>=0,'Missing '+n);return process.argv[i+1];}
const repo=arg('--repo-id'),origin=arg('--origin'),revision=arg('--revision');
assert(/^[A-Za-z0-9_-]+\/[A-Za-z0-9_.-]+$/.test(repo));
assert(/^[a-f0-9]{40}$/.test(revision));
const parsed=new URL(origin);assert.equal(parsed.origin,origin);assert.equal(parsed.protocol,'https:');
assert(/^[a-z0-9-]+\.static\.hf\.space$/.test(parsed.hostname));
const files=JSON.parse(arg('--files')).map(p=>path.resolve(p));assert(files.length>=1&&files.length<=4);
const expected=path.resolve(arg('--expected')),out=path.resolve(arg('--output'));
assert(!fs.existsSync(out));fs.mkdirSync(out,{recursive:true});
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const requests=[],blocked=[],pageErrors=[];let browser;
async function main(){
  browser=await chromium.launch({headless:true,executablePath:arg('--browser-executable')});
  const context=await browser.newContext({acceptDownloads:true,viewport:{width:1440,height:1050}});
  assert.equal((await context.cookies()).length,0);
  const metadata=await context.request.get('https://huggingface.co/api/spaces/'+repo);
  assert.equal(metadata.status(),200);const info=await metadata.json();
  assert.equal(info.private,false);assert.equal(info.sdk,'static');assert.equal(info.sha,revision);
  const hosts=new Set(['huggingface.co','hf.co','fonts.googleapis.com','fonts.gstatic.com']);
  context.on('request',request=>{
    const url=new URL(request.url());if(url.protocol==='blob:')return;
    requests.push({method:request.method(),origin:url.origin,bodyBytes:request.postDataBuffer()?.length||0});
  });
  await context.route('**/*',async route=>{
    const request=route.request(),url=new URL(request.url());
    const allowed=url.protocol==='https:'&&(hosts.has(url.hostname)||url.hostname.endsWith('.hf.co')||url.hostname.endsWith('.hf.space')||url.hostname.endsWith('.huggingface.co'));
    if(!allowed||request.method()!=='GET'||request.headers().authorization){
      blocked.push({method:request.method(),origin:url.origin,reason:request.headers().authorization?'credential':'method_or_origin'});
      return route.abort();
    }
    return route.continue();
  });
  const page=await context.newPage();page.on('pageerror',error=>pageErrors.push(error.name));
  await page.goto('https://huggingface.co/spaces/'+repo,{waitUntil:'domcontentloaded',timeout:120000});
  let app;
  for(let attempt=0;attempt<120;attempt++){
    app=page.frames().find(frame=>{try{return new URL(frame.url()).origin===origin;}catch{return false;}});
    if(app&&await app.locator('#files').count())break;
    await page.waitForTimeout(500);
  }
  assert(app,'Public embedded Static frame unavailable');
  await app.locator('#scope').filter({hasText:/./}).waitFor({timeout:120000});
  await page.screenshot({path:path.join(out,'parent-initial.png')});
  await app.locator('#files').setInputFiles(files);
  await app.locator('#resamples').fill('100');
  const began=performance.now();await app.locator('#analyze').click();
  await app.waitForFunction(()=>document.getElementById('status').textContent.includes('분석 완료')||document.getElementById('status').textContent.startsWith('분석 거부:'),null,{timeout:600000});
  const status=await app.locator('#status').textContent();assert(status.startsWith('분석 완료'),status);
  const outputs={};
  for(const name of ['profile-v2.json','cases-v2.jsonl','metrics-v2.csv','report-v2.md','report-v2.html']){
    const waiting=page.waitForEvent('download');await app.getByRole('link',{name,exact:true}).click();
    const download=await waiting;assert.equal(download.suggestedFilename(),name);
    await download.saveAs(path.join(out,name));const bytes=fs.readFileSync(path.join(out,name));
    assert.equal(hash(bytes),hash(fs.readFileSync(path.join(path.dirname(expected),name))),'Native mismatch: '+name);
    outputs[name]={bytes:bytes.length,sha256:hash(bytes)};
  }
  const report=app.frameLocator('#report');await report.locator('#tab-comparison').click();
  assert((await report.locator('#view h1').textContent()).length>3);
  await page.screenshot({path:path.join(out,'parent-comparison.png')});
  await page.setViewportSize({width:390,height:844});
  await app.waitForFunction(()=>innerWidth<=390,null,{timeout:15000});
  const reportFrame=app.childFrames().find(frame=>frame.url().startsWith('blob:'));
  assert(reportFrame,'Report frame unavailable');
  const mobileBefore=await reportFrame.evaluate(()=>({innerWidth,clientWidth:document.documentElement.clientWidth,
    mobileMedia:matchMedia('(max-width:800px)').matches,shellDisplay:getComputedStyle(document.querySelector('.shell')).display}));
  fs.writeFileSync(path.join(out,'mobile-layout-before.json'),JSON.stringify(mobileBefore,null,2));
  await reportFrame.waitForFunction(()=>innerWidth<=800&&getComputedStyle(document.querySelector('.shell')).display==='block',null,{timeout:15000});
  const mobile=await reportFrame.evaluate(()=>({innerWidth,mobileMedia:matchMedia('(max-width:800px)').matches,
    shellDisplay:getComputedStyle(document.querySelector('.shell')).display}));
  await page.screenshot({path:path.join(out,'parent-mobile.png')});
  assert(await app.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  await app.locator('#clear').click();assert(await app.locator('#report').isHidden());
  assert.equal(await app.locator('#downloads a').count(),0);
  assert(!blocked.some(item=>item.reason==='credential'));
  const receipt={scope:'Actual anonymous public HF Hub parent embedded file-analysis-download flow; actual small GPU results, not full35340 parent run',
    repo_id:repo,revision,origin,browser:browser.version(),seconds:(performance.now()-began)/1000,
    resamples:100,seed:1729,initial_cookies:0,credentials_used:false,
    all_five_files_byte_exact:true,outputs,requests,blocked_requests:blocked,parent_page_error_names:pageErrors,
    write_requests_allowed:0,actual_results_transmitted:false,cleared:true,
    mobile_layout:mobile,records:files.map(file=>JSON.parse(fs.readFileSync(file,'utf8')).records.length),shared_registration_verified:false};
  fs.writeFileSync(path.join(out,'evidence.json'),JSON.stringify(receipt,null,2));
  console.log(JSON.stringify({parent_flow:true,outputs:5,native_exact:true,seconds:receipt.seconds,blocked_requests:blocked.length,actual_results_transmitted:false}));
}
main().catch(error=>{
  process.exitCode=1;fs.writeFileSync(path.join(out,'failure.json'),JSON.stringify({error_name:error.name,requests,blocked,pageErrors},null,2));
  console.error('Public parent check failed; see local failure.json');
}).finally(async()=>{if(browser)await browser.close();});

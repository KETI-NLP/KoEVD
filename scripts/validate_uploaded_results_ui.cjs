/* Real localhost HTTP/browser acceptance for two supplied results.
 * Numeric transport/UI proof only; generation provenance is audited separately.
 * Does not alter results, configure baselines, log in or publish submissions.
 */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const assert=require('node:assert/strict'),{chromium}=require('playwright');
function arg(key,fallback){const i=process.argv.indexOf(key);return i<0?fallback:process.argv[i+1];}
const origin=arg('--origin','http://127.0.0.1:8772');
const originUrl=new URL(origin);
assert(['127.0.0.1','localhost','[::1]'].includes(originUrl.hostname)&&originUrl.origin===origin,
       'Acceptance requires a canonical loopback origin');
const inputs=[];
for(let i=2;i<process.argv.length;i++)if(process.argv[i]==='--result')inputs.push(path.resolve(process.argv[++i]));
const referenceId=arg('--reference-id',null);
if(referenceId)assert(/^[a-z0-9][a-z0-9_-]{0,79}$/.test(referenceId),'Invalid reference ID');
assert.equal(inputs.length,referenceId?1:2,'Provide one result with --reference-id, or exactly two results');
const expectedFile=path.resolve(arg('--expected-profile',''));
assert(fs.statSync(expectedFile).isFile(),'Provide independently executed CLI profile-v2.json');
const expected=JSON.parse(fs.readFileSync(expectedFile,'utf8'));
const expectedReportDir=arg('--expected-report-dir',null);
const analysisTimeout=Number(arg('--analysis-timeout-ms','120000'));
assert(Number.isInteger(analysisTimeout)&&analysisTimeout>=1000&&analysisTimeout<=1200000,
       '--analysis-timeout-ms must be an integer between 1000 and 1200000');
assert.equal(expected.runs.length,2);assert.equal(expected.comparisons.length,1);
const out=path.resolve(arg('--output-dir','generated/uploaded-results-ui'));
fs.mkdirSync(out); // Fresh attempt only; preserve previous pass/failure evidence.
const executable=arg('--browser-executable',process.env.KOEVD_TEST_BROWSER);
const sha=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const documents=inputs.map(file=>JSON.parse(fs.readFileSync(file,'utf8')));
let browser;const users=[],errors=[],external=[],checks=[],screenshots=[],requests=[];
const started=performance.now();let analysisSeconds;
async function main(){
  browser=await chromium.launch({headless:true,...executable?{executablePath:executable}:{}});
  async function context(){
    const c=await browser.newContext({viewport:{width:1440,height:1050},acceptDownloads:true});
    await c.route('**/*',async route=>{
      const url=route.request().url();requests.push(url);
      if(url.startsWith(origin+'/'))await route.continue();else{external.push(url);await route.abort();}
    });
    const p=await c.newPage();p.on('pageerror',e=>errors.push(e.message));
    p.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
    const waiting=p.waitForResponse(r=>r.url()===origin+'/api/session'&&r.request().method()==='POST');
    await p.goto(origin+'/');const session=await(await waiting).json();
    await p.locator('#status').filter({hasText:'Private session ready'}).waitFor();
    const user={c,p,session};users.push(user);return user;
  }
  const a=await context(),b=await context();
  async function capture(p,name,selector){
    const target=selector?p.locator(selector):p;
    await target.screenshot({path:path.join(out,name+'.png')});screenshots.push(name+'.png');
  }
  for(let i=0;i<inputs.length;i++){
    await a.p.locator('#result-files').setInputFiles(inputs[i]);await a.p.locator('#upload').click();
    await a.p.waitForFunction(n=>document.querySelectorAll('#uploads .run-row').length===n,i+1);
  }
  for(const document of documents){
    const text=await a.p.locator('#uploads').textContent();
    assert(text.includes(document.run.model.id));assert(text.includes(document.records.length+' records'));
  }
  assert((await b.p.locator('#uploads').textContent()).includes('No results uploaded yet'));
  assert.equal(await a.p.locator('input[data-baseline-id]:checked').count(),0);
  let selectedReference=null;
  if(referenceId){
    const catalog=await(await a.c.request.get(origin+'/api/catalog')).json();
    selectedReference=catalog.baselines.find(value=>value.id===referenceId);
    assert(selectedReference,'Configured reference must be present');
    assert.equal(selectedReference.scope,'actual_target_outputs');
    assert.equal(catalog.baselines.filter(value=>value.scope==='actual_target_outputs').length,2);
    await a.p.locator('input[data-baseline-id="'+referenceId+'"]').check();
    assert.equal(await a.p.locator('input[data-baseline-id]:checked').count(),1);
    checks.push('One actual uploaded result and one explicitly selected actual reference; two real references available');
  }
  await capture(a.p,referenceId?'upload-and-actual-reference':'two-private-uploads');
  const analysisStarted=performance.now();
  await a.p.locator('#analyze').click();
  await a.p.locator('#report-section:not([hidden])').waitFor({timeout:analysisTimeout});
  assert((await a.p.locator('#report-summary').textContent()).includes('2 analyzed run(s) · 1 paired comparison(s)'));
  const frame=a.p.frameLocator('#report-preview');
  await frame.locator('#tab-overview[aria-selected="true"]').waitFor();
  analysisSeconds=(performance.now()-analysisStarted)/1000;
  await a.p.getByRole('button',{name:'Analysis JSON',exact:true}).click();
  const [download]=await Promise.all([a.p.waitForEvent('download'),a.p.getByRole('link',{name:'Save profile-v2.json',exact:true}).click()]);
  const profileFile=path.join(out,'app-profile-v2.json');await download.saveAs(profileFile);
  assert.deepEqual(JSON.parse(fs.readFileSync(profileFile,'utf8')),expected);
  checks.push('Downloaded app profile exactly equals independent CLI profile, including all task denominators and paired analyses');
  await frame.locator('#tab-task3').click();assert((await frame.locator('#view').textContent()).includes('MEASUREMENT LIMITED'));
  await a.p.locator('#report-preview').scrollIntoViewIfNeeded();
  await capture(a.p,'task3-measurement-limit','#report-preview');
  await frame.locator('#tab-comparison').click();
  assert((await frame.locator('#view').textContent()).includes('Compare identical inputs'));
  await capture(a.p,'two-run-comparison','#report-preview');
  // Downloadable profiles deliberately omit raw cases; inspect the unchanged
  // supplied result instead of treating the profile as the raw response archive.
  const sample=documents[0].records.find(c=>c.task===3&&c.response.text&&c.response.text.trim());
  assert(sample,'Expected at least one actual supplied Task 3 response for case inspection');
  await frame.locator('#tab-cases').click();await frame.locator('#case-task').selectOption('3');
  await frame.locator('#case-search').fill(sample.sample_id);
  await frame.locator('.case-card summary').first().click();
  assert((await frame.locator('.case-card pre').allTextContents()).join('\n').includes(sample.response.text.slice(0,80)));
  assert.equal(await frame.locator('img').count(),0);
  await capture(a.p,'supplied-response-case','#report-preview');
  checks.push('Supplied Korean response case is retained as literal text; measurement warning and paired UI are visible');
  await a.p.getByRole('button',{name:'Offline HTML',exact:true}).click();
  const [html]=await Promise.all([a.p.waitForEvent('download'),a.p.getByRole('link',{name:'Save report-v2.html',exact:true}).click()]);
  const htmlFile=path.join(out,'app-report-v2.html');await html.saveAs(htmlFile);
  assert(fs.readFileSync(htmlFile,'utf8').includes('koevd-offline-html-v1'));
  if(expectedReportDir){
    for(const [label,name] of [['All cases JSONL','cases-v2.jsonl'],['Metrics CSV','metrics-v2.csv'],['Summary Markdown','report-v2.md']]){
      await a.p.getByRole('button',{name:label,exact:true}).click();
      const link=a.p.getByRole('link',{name:'Save '+name,exact:true});await link.waitFor();
      assert.equal(await a.p.locator('#prepared-download a').count(),1);
      const pending=a.p.waitForEvent('download');await link.click();const value=await pending;
      await value.saveAs(path.join(out,name));assert.equal(sha(path.join(out,name)),sha(path.join(expectedReportDir,name)));
    }
    assert.equal(sha(profileFile),sha(path.join(expectedReportDir,'profile-v2.json')));
    assert.equal(sha(htmlFile),sha(path.join(expectedReportDir,'report-v2.html')));
    checks.push('All5 files from visible Save links are byte-exact to native; only one prepared file link retained');
  }
  const current=await(await a.c.request.get(origin+'/api/session',{headers:{Authorization:'Bearer '+a.session.session_token}})).json();
  const reportPath=origin+'/api/reports/'+current.report.job_id+'/profile';
  assert.equal((await b.c.request.get(reportPath,{headers:{Authorization:'Bearer '+b.session.session_token}})).status(),404);
  assert.equal((await a.c.request.get(reportPath)).status(),401);
  await a.p.setViewportSize({width:390,height:844});
  assert(await a.p.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1));
  const embedded=await(await a.p.locator('#report-preview').elementHandle()).contentFrame();
  await embedded.locator('#tab-overview').click();
  assert(await embedded.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1));
  await a.p.locator('#report-preview').scrollIntoViewIfNeeded();
  await capture(a.p,'mobile-report','#report-preview');
  let aDeleted=false;
  if(expectedReportDir){
    let captured,release;const capturedResponse=new Promise(resolve=>captured=resolve),gate=new Promise(resolve=>release=resolve);
    await a.p.route('**/api/reports/*/csv',async route=>{const response=await route.fetch();captured();await gate;await route.fulfill({response});});
    const downloadStarted=await a.p.evaluate(()=>performance.now());
    await a.p.getByRole('button',{name:'Metrics CSV',exact:true}).click();await capturedResponse;
    assert.equal(await a.p.locator('#prepared-download').count(),0);
    await a.p.locator('#delete-session').click();await a.p.locator('#status').filter({hasText:'Session data deleted'}).waitFor();
    const resumed=a.p.waitForResponse(r=>r.url().endsWith('/csv')&&r.status()===200);release();await resumed;
    await a.p.waitForFunction(start=>performance.getEntriesByType('resource').some(e=>e.name.endsWith('/csv')&&e.startTime>=start&&e.responseEnd>0),downloadStarted);
    await a.p.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
    await a.p.waitForFunction(()=>!document.querySelector('#prepared-download')&&document.getElementById('status').textContent.includes('Session data deleted'));
    assert.equal(await a.p.locator('#prepared-download').count(),0);aDeleted=true;
    checks.push('Delayed authenticated download cannot recreate a Save link after session deletion');
  }
  for(const user of [a,b]){
    if(user!==a||!aDeleted)await user.p.locator('#delete-session').click();
    await user.p.locator('#status').filter({hasText:'Session data deleted'}).waitFor();
    assert.equal((await user.c.request.get(origin+'/api/session',{headers:{Authorization:'Bearer '+user.session.session_token}})).status(),401);
    assert(!requests.some(url=>url.includes(user.session.session_token)));
  }
  checks.push('Separate browser sessions/download ACL; desktop/mobile overflow; session deletion and token-free URLs');
  assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
  const evidence={status:'passed',scope:'supplied_results_local_http_ui_numeric_acceptance',origin,
    elapsed_seconds:(performance.now()-started)/1000,analysis_and_preview_seconds:analysisSeconds,
    analysis_observation_timeout_ms:analysisTimeout,
    browser:await browser.version(),input_files:inputs.map((file,i)=>({file_sha256:sha(file),artifact_sha256:documents[i].content_sha256,
      model:documents[i].run.model,records:documents[i].records.length})),expected_profile_sha256:sha(expectedFile),
    app_profile_sha256:sha(profileFile),app_html_sha256:sha(htmlFile),checks,screenshots,
    browser_errors:errors,external_requests:external,public_posting:false,actual_hf_login:false,
    generation_authenticity_verified_by_this_script:false,selected_reference:selectedReference};
  fs.writeFileSync(path.join(out,'evidence.json'),JSON.stringify(evidence,null,2)+'\n');
  await browser.close();browser=null;console.log(JSON.stringify({status:'passed',scope:evidence.scope,checks:checks.length,output:out}));
}
main().catch(async error=>{
  fs.writeFileSync(path.join(out,'failure.json'),JSON.stringify({status:'failed',error:error.stack,checks,errors,external},null,2)+'\n');
  for(const user of users){try{await user.c.request.delete(origin+'/api/session',{
    headers:{Authorization:'Bearer '+user.session.session_token,'X-KoEVD-CSRF':user.session.csrf_token,Origin:origin}});}catch{}}
  if(browser)await browser.close();console.error(error.stack);process.exitCode=1;
});

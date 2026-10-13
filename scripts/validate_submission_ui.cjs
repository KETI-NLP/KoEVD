/* Local actual HTTP/browser acceptance; OAuth/GPU/permission actors SYNTHETIC. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require('playwright');
function arg(key,fallback){const i=process.argv.indexOf(key);return i<0?fallback:process.argv[i+1];}
const origin=arg('--origin','http://127.0.0.1:8770'),fixture=path.resolve(arg('--fixture-dir','generated/space-demo-20261008'));
const out=path.resolve(arg('--output-dir','generated/submission-web-ui-20261008'));
const executable=arg('--browser-executable',process.env.KOEVD_TEST_BROWSER);
fs.mkdirSync(out,{recursive:true});let browser,simulatedFailureStatus=null;const errors=[],expectedHttpErrors=[],unexpected=[],checks=[],screenshots=[];
async function main(){
 browser=await chromium.launch({headless:true,...executable?{executablePath:executable}:{}});
 async function context(code){const c=await browser.newContext({viewport:{width:1440,height:1050},acceptDownloads:true});
  await c.route('**/*',async route=>{const url=new URL(route.request().url());
   if(url.origin===origin){await route.continue();return;}
   unexpected.push(url.origin+url.pathname);await route.abort();});
  const p=await c.newPage();p.on('pageerror',e=>errors.push(e.message));p.on('console',m=>{if(m.type()==='error'){
    if(simulatedFailureStatus&&m.text().startsWith('Failed to load resource: the server responded with a status of '+simulatedFailureStatus))expectedHttpErrors.push(m.text());else errors.push(m.text());}});
  await p.goto(origin+'/');await p.locator('#status').filter({hasText:'Private session ready'}).waitFor();await p.locator('#registration-section:not([hidden])').waitFor();return {c,p};}
 const a=await context('SYNTHETIC-author'),r=await context('SYNTHETIC-reviewer'),d=await context('SYNTHETIC-admin'),b=await context('SYNTHETIC-other');
 async function capture(p,name,selector){if(selector)await p.locator(selector).screenshot({path:path.join(out,name+'.png')});else await p.screenshot({path:path.join(out,name+'.png')});screenshots.push(name+'.png');}
 async function login(user,code){const promise=user.c.waitForEvent('page');await user.p.locator('#hf-signin').click();const popup=await promise;await popup.waitForURL(origin+'/SYNTHETIC/authorize*');const url=new URL(popup.url());assert.equal(url.searchParams.get('code_challenge_method'),'S256');assert.equal(url.searchParams.get('scope'),'openid profile');await popup.locator('a[data-code="'+code+'"]').click();await popup.waitForURL(origin+'/auth/done');await popup.close();await user.p.locator('#identity-refresh').click();await user.p.locator('#submission-controls:not([hidden])').waitFor();}
 for(const [user,code] of [[a,'SYNTHETIC-author'],[r,'SYNTHETIC-reviewer'],[d,'SYNTHETIC-admin'],[b,'SYNTHETIC-other']])await login(user,code);
 assert((await a.p.locator('#identity-status').textContent()).includes('<img'));assert.equal(await a.p.locator('#identity-status img').count(),0);assert.equal(await a.p.evaluate(()=>Boolean(window.IDENTITY_ATTACK)),false);
 await capture(a.p,'identity-and-private-submission');checks.push('localhost synthetic OAuth PKCE/cookie flow; four isolated browser identities; username text escaping');
 async function upload(user,file){await user.p.locator('#result-files').setInputFiles(path.join(fixture,file));await user.p.locator('#upload').click();await user.p.locator('#status').filter({hasText:'Results validated'}).waitFor();await user.p.locator('#submission-upload-refresh').click();const value=await user.p.locator('#submission-upload option').last().getAttribute('value');await user.p.locator('#submission-upload').selectOption(value);return value;}
 async function create(user){const wait=user.p.waitForResponse(resp=>resp.url()===origin+'/api/submissions'&&resp.request().method()==='POST');await user.p.locator('#submission-create').click();const response=await wait;assert.equal(response.status(),201);const result=await response.json();await user.p.locator('#submission-title').filter({hasText:result.id.slice(0,8)}).waitFor();return result.id;}
 async function action(user,name){const wait=user.p.waitForResponse(resp=>resp.url().endsWith('/actions')&&resp.request().method()==='POST');await user.p.locator('[data-action="'+name+'"]').click();const response=await wait;assert.equal(response.status(),200,await response.text());return response.json();}
 async function settled(user,selector){await user.p.locator(selector).click();await user.p.waitForFunction(s=>!document.querySelector(s).disabled,selector);}
 async function select(user,id){await settled(user,'#submissions-refresh');await user.p.locator('[data-submission-id="'+id+'"]').click();await user.p.locator('#submission-title').filter({hasText:id.slice(0,8)}).waitFor();}
 async function reviewPublish(id){await select(r,id);await r.p.locator('#submission-reason').fill('SYNTHETIC UI permission review');await action(r,'start_review');await r.p.locator('#review-evidence').fill('SYNTHETIC fictional outputs only, no actual legal review');await action(r,'approve');await select(d,id);await d.p.locator('#submission-reason').fill('SYNTHETIC local candidate publication');await action(d,'publish');}
 await upload(a,'SYNTHETIC-A.json');const first=await create(a);
 assert.equal((await b.c.request.get(origin+'/api/submissions/'+first)).status(),404);
 assert.equal((await b.c.request.get(origin+'/api/submissions/'+first+'/result')).status(),404);
 await a.p.locator('#submission-reason').fill('SYNTHETIC summary publication request');await a.p.locator('#publication-rights').fill('SYNTHETIC outputs only; explicitly not external publication');await a.p.locator('#publication-consent').check();await action(a,'request_review');await reviewPublish(first);
 await settled(b,'#public-refresh');await b.p.locator('[data-public-id="'+first+'"]').click();await b.p.locator('#public-metrics table').waitFor();
 assert((await b.p.locator('#public-metrics').textContent()).includes('Excluded'));assert((await b.p.locator('#public-metrics').textContent()).includes('Classifier accuracy remains limited'));
 assert.equal((await b.c.request.get(origin+'/api/public/submissions/'+first+'/result')).status(),403);
 await capture(b.p,'summary-metric-limits','#public-metrics');checks.push('private ACL; explicit summary review/publication; metric denominators/exclusion reasons; original responses private');
 const board=await(await b.c.request.get(origin+'/api/public/leaderboard')).json();assert.equal(board.publication_count,1);assert.deepEqual(board.boards,[]);assert.equal(board.official_ranking_enabled,false);
 assert((await b.p.locator('#leaderboard-status').textContent()).includes('1 published result(s)'));
 assert((await b.p.locator('#leaderboard-values').textContent()).includes('Registration policy awaiting approval'));
 await capture(b.p,'published-metric-comparison','#leaderboard-values');
 checks.push('complete public metric projection includes explicit ratios/coverage/exclusions without provisional ranks');
 await select(a,first);await a.p.locator('#submission-reason').fill('SYNTHETIC withdrawal test');await action(a,'withdraw');
 assert.equal((await b.c.request.get(origin+'/api/public/submissions/'+first)).status(),404);
 assert.equal((await a.c.request.get(origin+'/api/submissions/'+first+'/result')).status(),200);
 await settled(b,'#public-refresh');assert.equal(await b.p.locator('[data-public-id="'+first+'"]').count(),0);
 assert.equal(await b.p.locator('#leaderboard-values [data-board-entry="'+first+'"]').count(),0);
 assert((await b.p.locator('#leaderboard-status').textContent()).includes('0 published result(s)'));
 checks.push('withdrawal removes public summary/response visibility and UI entry; private original retained');
 await upload(a,'SYNTHETIC-B.json');const second=await create(a);await a.p.locator('#submission-reason').fill('SYNTHETIC response scope request');await a.p.locator('#publication-scope').selectOption('responses');await a.p.locator('#publication-rights').fill('SYNTHETIC response fixture; no external publication');await a.p.locator('#publication-consent').check();await action(a,'request_review');await reviewPublish(second);
 await upload(b,'SYNTHETIC-A.json');await settled(b,'#public-refresh');await b.p.getByRole('button',{name:'Add responses to private comparison',exact:true}).click();await b.p.locator('#status').filter({hasText:'Published result added'}).waitFor();
 assert.equal(await b.p.locator('#uploads input[data-upload-id]').count(),2);
 const expectedArtifact=JSON.parse(fs.readFileSync(path.join(fixture,'SYNTHETIC-B.json'),'utf8')).content_sha256;
 assert((await b.p.evaluate(()=>window.KoEVDWorkspace.uploads())).some(run=>run.artifact_sha256===expectedArtifact));
 await b.p.locator('#baselines input').uncheck();for(const input of await b.p.locator('#uploads input[data-upload-id]').all())await input.check();await b.p.locator('#analyze').click();await b.p.locator('#report-section:not([hidden])').waitFor({timeout:60000});
 assert((await b.p.locator('#report-summary').textContent()).includes('2 analyzed run(s) · 1 paired comparison(s)'));
 checks.push('explicit response scope -> public original -> private import -> two-run shared-engine paired comparison');
 const ownA=(await b.p.evaluate(()=>window.KoEVDWorkspace.uploads())).find(run=>run.model==='SYNTHETIC-A');assert(ownA);
 await b.p.locator('#submission-upload').selectOption(ownA.id);const third=await create(b);
 await b.p.locator('#submission-reason').fill('SYNTHETIC second-model metric comparison');await b.p.locator('#publication-scope').selectOption('summary');await b.p.locator('#publication-rights').fill('SYNTHETIC local-only outputs');await b.p.locator('#publication-consent').check();await action(b,'request_review');await reviewPublish(third);
 await settled(b,'#leaderboard-refresh');
 const pairBoard=await(await b.c.request.get(origin+'/api/public/leaderboard')).json();assert.equal(pairBoard.publication_count,2);assert.deepEqual(pairBoard.boards,[]);
 assert.equal(await b.p.locator('#leaderboard-values tbody tr').count(),2);
 for(const id of [second,third])assert.equal(await b.p.locator('#leaderboard-values [data-board-entry="'+id+'"]').count(),1);
 const cells=await b.p.locator('#leaderboard-values tbody tr td:nth-child(4)').allTextContents();assert.deepEqual(cells,['—','—']);
 fs.writeFileSync(path.join(out,'SYNTHETIC-public-metric-projection.json'),JSON.stringify(pairBoard,null,2));
 await capture(b.p,'two-published-model-metrics','#leaderboard-values');
 checks.push('two independently reviewed fictional model candidates share a metric group, retain ratios and excluded rank markers');
 // Exercise pending and failed public reads after real local publication, so
 // an old success cannot mask recovery quarantine or capacity errors.
 async function failedPublicRead(pathname,selector,status,loading,failed){
  let entered,release;const started=new Promise(resolve=>entered=resolve),gate=new Promise(resolve=>release=resolve);
  const handler=async route=>{if(new URL(route.request().url()).pathname!==pathname)return route.continue();
   entered();await gate;await route.fulfill({status,contentType:'application/json',body:JSON.stringify({error:{
    code:status===503?'recovery_required':'capacity_limit',message:'SYNTHETIC '+(status===503?'recovery_required':'capacity_limit')+' '+('X'.repeat(160))+' <img src=x onerror="window.PUBLIC_ERROR_ATTACK=true">'}})});};
  simulatedFailureStatus=status;await b.p.route('**/api/public/**',handler);
  try{await b.p.locator(selector).click();await started;await loading();release();await failed();
   await b.p.waitForFunction(()=>!document.querySelector('#public-refresh').disabled);
   assert.equal(await b.p.locator('#public-submissions img, #public-metrics img, #leaderboard-status img').count(),0);
   assert.equal(await b.p.evaluate(()=>Boolean(window.PUBLIC_ERROR_ATTACK)),false);
   assert.equal((await b.c.request.get(origin+'/api/submissions/'+third+'/result')).status(),200);
   assert.equal((await b.c.request.get(origin+'/api/submissions/'+third+'/history')).status(),200);
  }finally{release();await b.p.unroute('**/api/public/**',handler);simulatedFailureStatus=null;}
 }
 await settled(b,'#public-refresh');await b.p.locator('[data-public-id="'+second+'"]').click();await b.p.locator('#public-metrics table').waitFor();
 await failedPublicRead('/api/public/submissions/'+third,'[data-public-id="'+third+'"]',503,
  async()=>{assert.equal(await b.p.locator('#public-metrics table').count(),0);assert((await b.p.locator('#public-metrics').textContent()).includes('Loading candidate metrics'));},
  async()=>{await b.p.locator('#public-metrics').filter({hasText:'Candidate metrics unavailable'}).waitFor();assert.equal(await b.p.locator('#public-metrics table').count(),0);});
 await b.p.locator('[data-public-id="'+third+'"]').click();await b.p.locator('#public-metrics table').waitFor();
 checks.push('pending/failed candidate-detail read clears older metrics; retry succeeds; private original/history remain readable');
 for(const status of [503,413]){
  await failedPublicRead('/api/public/submissions','#public-refresh',status,
   async()=>{assert.equal(await b.p.locator('[data-public-id]').count(),0);assert.equal(await b.p.locator('#public-metrics table').count(),0);
    assert.equal(await b.p.locator('#leaderboard-values tbody tr').count(),0);assert(await b.p.locator('#leaderboard-metric').isDisabled());},
   async()=>{await b.p.locator('#public-submissions').filter({hasText:'Published candidates unavailable'}).waitFor();
    assert((await b.p.locator('#leaderboard-status').textContent()).includes('Comparison unavailable'));assert.equal(await b.p.locator('#public-next').isVisible(),false);
    assert(!(await b.p.locator('#public-submissions').textContent()).includes('No published candidates'));
    assert(!(await b.p.locator('#leaderboard-status').textContent()).includes('0 published result'));});
  if(status===503){await b.p.locator('#leaderboard-status').scrollIntoViewIfNeeded();await capture(b.p,'public-recovery-unavailable');
   await b.p.setViewportSize({width:390,height:844});await b.p.locator('#leaderboard-status').scrollIntoViewIfNeeded();
   assert(await b.p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
   for(const selector of ['#public-submissions','#leaderboard-status'])assert(await b.p.locator(selector).evaluate(n=>n.scrollWidth<=n.clientWidth+1));
   await capture(b.p,'mobile-public-recovery-unavailable');await b.p.setViewportSize({width:1440,height:1050});}
  await settled(b,'#public-refresh');assert.equal(await b.p.locator('[data-public-id]').count(),2);assert.equal(await b.p.locator('#leaderboard-values tbody tr').count(),2);
 }
 checks.push('pending/failed public list removes cards/details/board/pagination without a false empty or zero; recovery/capacity retries restore two candidates');
 await failedPublicRead('/api/public/leaderboard','#leaderboard-refresh',503,
  async()=>{assert.equal(await b.p.locator('#leaderboard-values tbody tr').count(),0);assert.equal(await b.p.locator('#leaderboard-metric option').count(),0);assert(await b.p.locator('#leaderboard-metric').isDisabled());},
  async()=>{await b.p.locator('#leaderboard-status').filter({hasText:'Comparison unavailable'}).waitFor();assert(await b.p.locator('#leaderboard-metric').isDisabled());});
 await settled(b,'#leaderboard-refresh');assert.equal(await b.p.locator('#leaderboard-values tbody tr').count(),2);assert.equal(await b.p.locator('#leaderboard-metric').isDisabled(),false);
 assert.deepEqual(await b.p.locator('#leaderboard-values tbody tr td:nth-child(4)').allTextContents(),['—','—']);
 checks.push('pending/failed board disables empty selector and clears stale values; retry preserves diagnostic no-rank');
 await select(a,second);const [download]=await Promise.all([a.p.waitForEvent('download'),a.p.locator('#submission-history').click()]);await download.saveAs(path.join(out,'SYNTHETIC-history.json'));
 const history=JSON.parse(fs.readFileSync(path.join(out,'SYNTHETIC-history.json'),'utf8'));assert(history.events.some(e=>e.action==='publish'));
 await a.p.setViewportSize({width:390,height:844});await a.p.locator('#identity-status').scrollIntoViewIfNeeded();await capture(a.p,'mobile-sign-in-and-retention');
 assert(await a.p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
 await b.p.setViewportSize({width:390,height:844});await b.p.locator('#leaderboard-status').scrollIntoViewIfNeeded();
 assert(await b.p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await capture(b.p,'mobile-published-metric-comparison');
 await a.p.locator('#identity-logout').click();await a.p.locator('#submission-controls').waitFor({state:'hidden'});assert.equal((await a.c.request.get(origin+'/api/submissions/'+second)).status(),401);
 checks.push('event history download, 390px layout, sign-out invalidates private access');
 assert.deepEqual(unexpected,[]);assert.deepEqual(errors,[]);
 fs.writeFileSync(path.join(out,'evidence.json'),JSON.stringify({scope:'actual local HTTP/headless browser with SYNTHETIC OAuth identities, outputs and permissions; explicit browser-side 503/413 response doubles; no real HF/GPU/external publication',checks,screenshots,unexpected_external_requests:unexpected,browser_errors:errors,expected_failed_HTTP_console_messages:expectedHttpErrors,simulated_public_read_failures:4,actual_hf_login:false,actual_gpu:false,official_ranking_enabled:false},null,2));
 console.log(JSON.stringify({checks:checks.length,screenshots:screenshots.length,browser_errors:errors.length,unexpected_external_requests:unexpected.length,scope:'SYNTHETIC local HTTP/UI only'}));
}
main().catch(e=>{fs.writeFileSync(path.join(out,'failure.json'),JSON.stringify({error:e.message,checks,errors,unexpected},null,2));console.error(e);process.exitCode=1;}).finally(async()=>{if(browser)await browser.close();});

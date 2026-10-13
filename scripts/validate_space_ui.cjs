/* Actual local HTTP + isolated browser sessions. No GPU/public baseline evidence. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require('playwright');
function arg(key,fallback){const i=process.argv.indexOf(key);return i<0?fallback:process.argv[i+1];}
const origin=arg('--origin','http://127.0.0.1:8767');
const fixture=path.resolve(arg('--fixture-dir','generated/space-demo-20261008'));
const attack=path.resolve(arg('--security-result','generated/offline-report-security-fixture-20261008/SYNTHETIC-A.json'));
const out=path.resolve(arg('--output-dir','generated/space-ui-20261008'));
const browserExecutable=arg('--browser-executable',process.env.KOEVD_TEST_BROWSER);
const expectedPath=arg('--expected-profile',null);
fs.mkdirSync(out,{recursive:true});let browser;const errors=[],external=[],checkpoints=[],screenshots=[],urls=[];
async function main(){
  browser=await chromium.launch({headless:true,...browserExecutable?{executablePath:browserExecutable}:{}});
  async function context(){const c=await browser.newContext({viewport:{width:1440,height:1050},acceptDownloads:true});
    await c.route('**/*',async route=>{const url=route.request().url();urls.push(url);if(url.startsWith(origin+'/'))await route.continue();else{external.push(url);await route.abort();}});
    const p=await c.newPage();p.on('pageerror',e=>errors.push(e.message));p.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
    const wait=p.waitForResponse(r=>r.url()===origin+'/api/session'&&r.request().method()==='POST');await p.goto(origin+'/');const session=await (await wait).json();await p.locator('#status').filter({hasText:'Private session ready'}).waitFor();return {c,p,session};}
  const a=await context(),b=await context();
  async function capture(page,name){await page.screenshot({path:path.join(out,name+'.png'),fullPage:false});screenshots.push(name+'.png');}
  await capture(a.p,'space-ready');
  await a.p.locator('#result-files').setInputFiles(path.join(fixture,'SYNTHETIC-A.json'));await a.p.locator('#upload').click();await a.p.locator('#uploads .run-row').waitFor();
  assert((await a.p.locator('#uploads').textContent()).includes('580 records'));assert((await b.p.locator('#uploads').textContent()).includes('No results uploaded yet'));
  await a.p.locator('input[data-baseline-id="synthetic-reference-b"]').check();await capture(a.p,'space-select-reference');
  await a.p.locator('#analyze').click();await a.p.locator('#report-section:not([hidden])').waitFor({timeout:60000});
  const frame=a.p.frameLocator('#report-preview');await frame.locator('#tab-overview[aria-selected="true"]').waitFor();
  assert((await a.p.locator('#report-summary').textContent()).includes('2 analyzed run(s) · 1 paired comparison(s)'));
  await a.p.locator('#report-preview').scrollIntoViewIfNeeded();await a.p.locator('#report-preview').screenshot({path:path.join(out,'space-report-preview.png')});screenshots.push('space-report-preview.png');
  await frame.locator('#tab-task3').click();assert((await frame.locator('#view').textContent()).includes('MEASUREMENT LIMITED'));
  await frame.locator('#tab-comparison').click();assert((await frame.locator('#view').textContent()).includes('EXPLORATORY COMPARISON'));await capture(a.p,'space-comparison-preview');
  await frame.locator('#tab-cases').click();await frame.locator('#case-search').fill('synthetic-040');assert((await frame.locator('#case-count').textContent()).startsWith('10 matching records'));await frame.locator('.case-card summary').first().click();assert((await frame.locator('.case-card').first().textContent()).includes('가상 입력 예시'));
  checkpoints.push({check:'upload -> configured fictional reference -> same-engine report -> restricted comparison -> Korean cases'});
  await a.p.getByRole('button',{name:'Analysis JSON',exact:true}).click();
  const [download]=await Promise.all([a.p.waitForEvent('download'),a.p.getByRole('link',{name:'Save profile-v2.json',exact:true}).click()]);await download.saveAs(path.join(out,'app-profile-v2.json'));
  const profile=JSON.parse(fs.readFileSync(path.join(out,'app-profile-v2.json'),'utf8'));assert.equal(profile.runs.length,2);assert.equal(profile.comparisons.length,1);assert.equal(profile.runs[0].tasks['3'].partitions[0].rows,80);
  if(expectedPath){assert.deepEqual(profile,JSON.parse(fs.readFileSync(expectedPath,'utf8')));checkpoints.push({check:'downloaded app profile equals independently executed local CLI profile'});}
  await a.p.getByRole('button',{name:'Offline HTML',exact:true}).click();
  const [htmlDownload]=await Promise.all([a.p.waitForEvent('download'),a.p.getByRole('link',{name:'Save report-v2.html',exact:true}).click()]);await htmlDownload.saveAs(path.join(out,'app-report-v2.html'));
  assert(fs.readFileSync(path.join(out,'app-report-v2.html'),'utf8').includes('koevd-offline-html-v1'));
  const first=await (await a.c.request.get(origin+'/api/session',{headers:{Authorization:'Bearer '+a.session.session_token}})).json(),job=first.report.job_id;
  const denied=await b.c.request.get(origin+'/api/reports/'+job+'/profile',{headers:{Authorization:'Bearer '+b.session.session_token}});assert.equal(denied.status(),404);
  assert.equal((await a.c.request.get(origin+'/api/reports/'+job+'/profile')).status(),401);
  await a.p.setViewportSize({width:390,height:844});assert(await a.p.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1));await capture(a.p,'space-mobile');
  const embedded=await (await a.p.locator('#report-preview').elementHandle()).contentFrame();await embedded.locator('#tab-overview').click();await embedded.locator('#view h1').scrollIntoViewIfNeeded();assert(await embedded.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1));assert((await embedded.locator('#view h1').textContent()).includes('Understand behavior'));await a.p.locator('#report-preview').scrollIntoViewIfNeeded();await a.p.locator('#report-preview').screenshot({path:path.join(out,'space-mobile-report.png')});screenshots.push('space-mobile-report.png');
  await b.p.locator('#result-files').setInputFiles(attack);await b.p.locator('#upload').click();await b.p.locator('#uploads .run-row').waitFor();
  assert((await b.p.locator('#uploads').textContent()).includes('globalThis.__KOEVD_INJECTED__=1'));assert.equal(await b.p.evaluate(()=>globalThis.__KOEVD_INJECTED__),undefined);assert.equal(await b.p.locator('img').count(),0);await capture(b.p,'space-literal-model-id');
  await b.p.locator('#analyze').click();await b.p.locator('#report-section:not([hidden])').waitFor({timeout:60000});
  const security=b.p.frameLocator('#report-preview');await security.locator('#tab-task3').click();assert(await security.locator('svg text').filter({hasText:/^N\/A/}).count()>=3);
  await security.locator('#tab-cases').click();await security.locator('#case-task').selectOption('3');await security.locator('#case-search').fill('synthetic-050');await security.locator('.case-card summary').first().click();assert((await security.locator('.case-card pre').allTextContents()).join(' ').includes('globalThis.__KOEVD_INJECTED__=1'));assert.equal(await security.locator('img').count(),0);await capture(b.p,'space-security-preview');
  for(const obj of [a,b]){await obj.p.locator('#delete-session').click();await obj.p.locator('#status').filter({hasText:'Session data deleted'}).waitFor();assert.equal((await obj.c.request.get(origin+'/api/session',{headers:{Authorization:'Bearer '+obj.session.session_token}})).status(),401);assert(!urls.some(url=>url.includes(obj.session.session_token)));}
  checkpoints.push({check:'two browser contexts isolated / unauthenticated and other-session downloads denied / malicious text inert / unmeasured N/A / deletion revokes access / credentials absent from URLs'});
  assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
  const evidence={status:'passed',origin,browser:await browser.version(),synthetic_only:true,gpu_inference:false,public_baseline:false,published:false,checkpoints,screenshots,console_errors:errors,external_requests:external,app_local_numeric_agreement:Boolean(expectedPath)};
  fs.writeFileSync(path.join(out,'space-ui-evidence.json'),JSON.stringify(evidence,null,2)+'\n');console.log(JSON.stringify(evidence));await a.c.close();await b.c.close();await browser.close();browser=null;
}
main().catch(async error=>{fs.writeFileSync(path.join(out,'space-ui-failure.json'),JSON.stringify({status:'failed',error:error.stack,checkpoints,errors,external},null,2)+'\n');if(browser)await browser.close();console.error(error.stack);process.exitCode=1;});

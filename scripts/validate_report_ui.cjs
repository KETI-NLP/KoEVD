/* Offline report acceptance using a new headless browser, never the user's session. */
const fs=require('node:fs');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const assert=require('node:assert/strict');
const {chromium}=require('playwright');

function argument(name,fallback){const i=process.argv.indexOf(name);return i<0?fallback:process.argv[i+1];}
const reportPath=path.resolve(argument('--report','generated/offline-report-first-20261008/report-v2.html'));
const out=path.resolve(argument('--output-dir','generated/offline-report-ui-20261008'));
const securityReport=argument('--security-report',null);
const allowedDocuments=new Set([pathToFileURL(reportPath).href,...securityReport?[pathToFileURL(path.resolve(securityReport)).href]:[]]);
const executable=argument('--browser-executable',process.env.KOEVD_TEST_BROWSER);
const html=fs.readFileSync(reportPath,'utf8');
const data=JSON.parse(html.match(/<script id="koevd-data" type="application\/json">([\s\S]*?)<\/script>/)[1]);
fs.mkdirSync(out,{recursive:true});
const checkpoints=[],errors=[],external=[],screenshots=[];
let browser;
async function main(){
  browser=await chromium.launch({headless:true,...executable?{executablePath:executable}:{}});
  const context=await browser.newContext({viewport:{width:1440,height:1050},deviceScaleFactor:1,acceptDownloads:true});
  await context.route('**/*',async route=>{if(allowedDocuments.has(route.request().url()))await route.continue();else{external.push(route.request().url());await route.abort();}});
  const page=await context.newPage();page.on('pageerror',error=>errors.push(error.message));page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
  await page.goto(pathToFileURL(reportPath).href);await page.locator('#tab-overview[aria-selected="true"]').waitFor();
  async function capture(name){await page.screenshot({path:path.join(out,name+'.png'),fullPage:false});screenshots.push(name+'.png');}
  const tabKeys=['overview','task1','task2','task3','task4','task5','transitions','metadata','quality','comparison','cases','method'];
  for(const key of tabKeys){await page.locator('#tab-'+key).click();await page.locator('#view h1').waitFor();const heading=await page.locator('#view h1').textContent();assert(heading.length>3);checkpoints.push({tab:key,heading,charts:await page.locator('#view svg.chart').count()});await capture('desktop-'+key);}
  assert.equal(await page.locator('script').count(),2);assert.equal(await page.locator('img,iframe,object').count(),0);
  await page.locator('#tab-task1').click();
  const eventCount=data.runs[0].tasks['1'].partitions[0].confusion['unsafe->safe']||0;
  await page.getByRole('button',{name:/^unsafe->safe;/}).focus();await page.keyboard.press('Enter');
  assert.equal(await page.locator('#tab-cases').getAttribute('aria-selected'),'true');
  assert((await page.locator('#case-count').textContent()).startsWith(eventCount+' matching records'));
  checkpoints.push({check:'keyboard chart drilldown',records:eventCount});
  await page.getByRole('button',{name:'Clear all case filters',exact:true}).click();
  assert((await page.locator('#case-count').textContent()).startsWith(data.runs[0].cases.length+' matching records'));
  await page.getByRole('button',{name:'Next',exact:true}).click();assert((await page.locator('.pager').textContent()).includes('Page 2 /'));
  await page.locator('#case-search').fill('synthetic-040');
  const expected=data.runs[0].cases.filter(c=>c.source_id==='synthetic-040').length;
  assert((await page.locator('#case-count').textContent()).startsWith(expected+' matching records'));
  await page.locator('.case-card summary').first().click();assert((await page.locator('.case-card').first().textContent()).includes('가상 입력 예시'));
  await capture('cases-korean-expanded');
  await page.getByRole('button',{name:'Compare this input',exact:true}).first().click();
  assert((await page.locator('#compare-count').textContent()).startsWith('1 matching paired records'));
  await page.getByText('Open both responses (may contain harmful text)',{exact:true}).first().click();
  assert.equal(await page.locator('.response-grid').count(),1);await capture('comparison-one-input');
  checkpoints.push({check:'literal search / source / side-by-side drilldown',source:'synthetic-040',records:expected});
  await page.locator('#compare-task').selectOption('5');await page.locator('#compare-state').selectOption('left_event_only');
  const comparison=data.comparisons[0],expectedPair=comparison.tasks.find(t=>t.task===5).partitions[0].paired_status.left_event_only;
  assert((await page.locator('#compare-count').textContent()).startsWith(expectedPair+' matching paired records'));
  await page.locator('#compare-task').selectOption('4');assert.equal(await page.locator('#compare-state').inputValue(),'all');
  assert((await page.locator('#view').textContent()).includes('Task 4 has no event quality difference or rank'));
  checkpoints.push({check:'paired event filter and Task 4 no rank',left_event_only:expectedPair});
  await page.locator('#tab-task4').click();await page.locator('#strategy-scope').selectOption('core');await page.locator('#strategy-axis').selectOption('topic');
  const matrixPanel=page.locator('.panel').filter({has:page.getByRole('heading',{name:/strategy co-occurrence/})});
  await matrixPanel.screenshot({path:path.join(out,'strategy-cooccurrence.png')});screenshots.push('strategy-cooccurrence.png');
  const metadataPanel=page.locator('.panel').filter({has:page.getByRole('heading',{name:/Strategy inclusion by Topic/})});
  await metadataPanel.screenshot({path:path.join(out,'strategy-metadata.png')});screenshots.push('strategy-metadata.png');
  await page.locator('#tab-metadata').click();await page.locator('#metadata-task').selectOption('2');await page.locator('#metadata-axis').selectOption('topic');await page.locator('#metadata-scope').selectOption('variant:choose_unsafe');
  assert((await page.locator('#view').textContent()).includes('choose_unsafe'));checkpoints.push({check:'task/metadata/scope selectors'});
  await page.locator('#tab-transitions').click();await page.locator('#transition-framing').selectOption('tool_forced');
  const safeUnsafe=data.runs[0].task3_task5.tool_forced.cells.find(c=>c.response_label==='safe'&&c.tool_outcome==='unsafe_tool').count;
  await page.getByRole('button',{name:/^Classifier-safe → Unsafe mock tool;/}).click();
  assert((await page.locator('#case-count').textContent()).startsWith(safeUnsafe+' matching records'));checkpoints.push({check:'safe response to unsafe tool drilldown',records:safeUnsafe});
  await page.locator('#tab-task3').click();
  await page.locator('svg.chart [role="button"]').first().click();
  assert((await page.locator('#case-count').textContent()).startsWith(data.runs[0].tasks['3'].partitions[0].rows+' matching records'));
  checkpoints.push({check:'whole chart row pointer drilldown, including unpainted gaps'});
  await page.locator('#tab-task3').click();
  const [svgDownload]=await Promise.all([page.waitForEvent('download'),page.locator('.chart-actions button').first().click()]);const svgPath=path.join(out,'downloaded-chart.svg');await svgDownload.saveAs(svgPath);assert(fs.readFileSync(svgPath,'utf8').includes('<style>'));allowedDocuments.add(pathToFileURL(svgPath).href);const svgPage=await context.newPage();await svgPage.goto(pathToFileURL(svgPath).href);assert.equal(await svgPage.locator('parsererror').count(),0);assert(await svgPage.locator('svg').count());await svgPage.close();
  const [jsonDownload]=await Promise.all([page.waitForEvent('download'),page.getByRole('button',{name:'Analysis JSON',exact:true}).click()]);await jsonDownload.saveAs(path.join(out,'downloaded-analysis.json'));const downloaded=JSON.parse(fs.readFileSync(path.join(out,'downloaded-analysis.json'),'utf8'));assert.deepEqual(downloaded.runs[0].tasks,data.runs[0].tasks);
  checkpoints.push({check:'offline SVG / analysis download preserves data'});
  await page.setViewportSize({width:390,height:844});
  for(const key of ['overview','task4','comparison','cases']){await page.locator('#tab-'+key).click();const layout=await page.evaluate(()=>({width:window.innerWidth,documentWidth:document.documentElement.scrollWidth,overflow:[...document.querySelectorAll('body *')].filter(n=>{const r=n.getBoundingClientRect();return r.right>window.innerWidth+1 && r.width>0;}).slice(0,30).map(n=>({tag:n.tagName,cls:n.className?.baseVal??n.className,right:n.getBoundingClientRect().right,width:n.getBoundingClientRect().width,text:n.textContent.slice(0,120)}))}));if(layout.documentWidth>layout.width+1){fs.writeFileSync(path.join(out,'overflow-'+key+'.json'),JSON.stringify(layout,null,2));await capture('overflow-'+key);}assert(layout.documentWidth<=layout.width+1,'Page overflow on mobile '+key);await capture('mobile-'+key);}
  await page.setViewportSize({width:1440,height:1050});await page.locator('#tab-overview').focus();await page.keyboard.press('ArrowDown');assert.equal(await page.locator('#tab-task1').getAttribute('aria-selected'),'true');
  checkpoints.push({check:'mobile layout and keyboard tab navigation'});
  if(securityReport){
    await page.goto(pathToFileURL(path.resolve(securityReport)).href);await page.locator('#tab-overview[aria-selected="true"]').waitFor();
    assert.equal(await page.evaluate(()=>globalThis.__KOEVD_INJECTED__),undefined);
    assert.equal(await page.locator('img,iframe,object').count(),0);assert.equal(await page.locator('script').count(),2);
    await page.locator('#tab-task3').click();assert((await page.locator('svg text').filter({hasText:/^N\/A/}).count())>=3);
    await capture('security-task3-unmeasured');
    await page.locator('#tab-cases').click();await page.locator('#case-task').selectOption('3');await page.locator('#case-search').fill('synthetic-050');
    assert((await page.locator('#case-count').textContent()).startsWith('1 matching records'));
    await page.locator('.case-card summary').first().click();assert((await page.locator('.case-card pre').allTextContents()).join(' ').includes('globalThis.__KOEVD_INJECTED__=1'));
    assert.equal(await page.evaluate(()=>globalThis.__KOEVD_INJECTED__),undefined);assert.equal(await page.locator('img').count(),0);
    await capture('security-literal-text');checkpoints.push({check:'browser adversarial text inert / entirely unmeasured Task 3 N/A'});
  }
  assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
  const evidence={status:'passed',report:reportPath,renderer:data.renderer_version,synthetic_only:true,gpu_inference:false,
    browser:await browser.version(),checkpoints,console_errors:errors,blocked_external_requests:external,screenshots,charts_per_run:data.runs.map(p=>p.charts.length)};
  fs.writeFileSync(path.join(out,'ui-evidence.json'),JSON.stringify(evidence,null,2)+'\n');console.log(JSON.stringify(evidence));
  await context.close();await browser.close();browser=null;
}
main().catch(async error=>{fs.writeFileSync(path.join(out,'ui-failure.json'),JSON.stringify({status:'failed',error:error.stack,checkpoints,errors,external},null,2)+'\n');if(browser)await browser.close();console.error(error.stack);process.exitCode=1;});

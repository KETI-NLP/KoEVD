/* Full-input offline HTML gate; declared input scope, no inference/accuracy proof. */
const fs=require('node:fs');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const {performance}=require('node:perf_hooks');
const assert=require('node:assert/strict');
const {chromium}=require('playwright');
function argument(name,fallback){const i=process.argv.indexOf(name);return i<0?fallback:process.argv[i+1];}
const reportPath=path.resolve(argument('--report','generated/offline-report-full-scale-final-20261008/report-v2.html'));
const out=path.resolve(argument('--output-dir','generated/offline-report-scale-ui-20261008'));
const executable=argument('--browser-executable',process.env.KOEVD_TEST_BROWSER);
const expectedRuns=Number(argument('--expected-runs','1'));
assert([1,2].includes(expectedRuns),'--expected-runs must be 1 or 2');
const inputScope=argument('--input-scope','fixture');
assert(['fixture','actual'].includes(inputScope),'--input-scope must be fixture or actual');
const expectedModels=process.argv.flatMap((arg,i)=>arg==='--expected-model'?[process.argv[i+1]]:[]);
const expectedLengthLimits=process.argv.flatMap((arg,i)=>arg==='--expected-length-limit'?[Number(process.argv[i+1])]:[]);
const html=fs.readFileSync(reportPath,'utf8');
const data=JSON.parse(html.match(/<script id="koevd-data" type="application\/json">([\s\S]*?)<\/script>/)[1]);
assert.equal(data.runs.length,expectedRuns);
for(const run of data.runs)assert.equal(run.cases.length,17670);
if(expectedRuns===2)assert.equal(data.comparisons.length,1);
if(inputScope==='fixture')for(const run of data.runs)assert(run.run.model.id.startsWith('SYNTHETIC-'));
else{
  assert.equal(expectedModels.length,expectedRuns,'Actual inputs require one --expected-model per run');
  assert.deepEqual(data.runs.map(run=>run.run.model.id),expectedModels);
  assert.equal(expectedLengthLimits.length,expectedRuns,'Actual inputs require outside --expected-length-limit counts');
  for(const [i,run] of data.runs.entries()){
    assert(Number.isInteger(expectedLengthLimits[i])&&expectedLengthLimits[i]>=0);
    for(const task of [3,4])assert.equal(run.cases.filter(c=>c.task===task&&c.quality_flags.includes('length_limit')).length,expectedLengthLimits[i]);
  }
}
const profile=data.runs[0],checkpoints=[],errors=[],external=[],screenshots=[];
fs.mkdirSync(out,{recursive:true});
let browser;
async function main(){
  browser=await chromium.launch({headless:true,...executable?{executablePath:executable}:{}});
  const context=await browser.newContext({viewport:{width:1440,height:1050},deviceScaleFactor:1});
  await context.route('**/*',async route=>{if(route.request().url()===pathToFileURL(reportPath).href)await route.continue();else{external.push(route.request().url());await route.abort();}});
  const page=await context.newPage();page.setDefaultTimeout(60000);
  page.on('pageerror',error=>errors.push(error.message));page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
  async function capture(name){await page.screenshot({path:path.join(out,name+'.png'),fullPage:false});screenshots.push(name+'.png');}
  const start=performance.now();await page.goto(pathToFileURL(reportPath).href,{timeout:60000});await page.locator('#tab-overview[aria-selected="true"]').waitFor();
  const loadSeconds=(performance.now()-start)/1000;await capture('scale-overview');
  for(const key of ['overview','task1','task2','task3','task4','task5','transitions','metadata','quality','comparison','cases','method']){
    const begin=performance.now();await page.locator('#tab-'+key).click();await page.locator('#view h1').waitFor();
    checkpoints.push({tab:key,heading:await page.locator('#view h1').textContent(),charts:await page.locator('#view svg.chart').count(),interaction_seconds:(performance.now()-begin)/1000});
    if(key==='comparison'&&expectedRuns===1)assert((await page.locator('#view').textContent()).includes('This report contains one run'));
    if(key==='task3')await capture('scale-task3');
  }
  if(expectedRuns===2){
    await page.locator('#tab-comparison').click();
    const scopes=[{task:3,scope:'subset:core',total:2000},{task:3,scope:'subset:task5_overlap',total:784},{task:5,scope:'variant:safe_guided',total:784}];
    for(const {task,scope,total} of scopes){
      await page.locator('#compare-task').selectOption(String(task));await page.locator('#compare-scope').selectOption(scope);
      await page.locator('#compare-state').selectOption('all');
      assert((await page.locator('#compare-count').textContent()).startsWith(total+' matching paired records'));
      const [kind,name]=scope.split(':'),partition=data.comparisons[0].tasks.find(t=>t.task===task).partitions.find(p=>p.kind===kind&&p.name===name);
      for(const status of ['both_valid','both_invalid']){
        await page.locator('#compare-state').selectOption(status);
        assert((await page.locator('#compare-count').textContent()).startsWith(partition.paired_status[status]+' matching paired records'));
      }
      checkpoints.push({check:'full paired scope and valid/invalid filters',task,scope,total,paired_status:partition.paired_status});
    }
    await page.locator('#compare-state').selectOption('all');await capture('scale-two-run-comparison');
    await page.locator('#compare-task').selectOption('4');assert((await page.locator('#view').textContent()).includes('Task 4 has no event quality difference or rank.'));
    assert.equal(await page.locator('#compare-state option[value="left_event_only"]').count(),0);
    await capture('scale-two-run-descriptive-strategies');
    await page.locator('#tab-cases').click();
    for(const runIndex of ['1','0']){
      await page.locator('#run-select').selectOption(runIndex);
      assert((await page.locator('#case-count').textContent()).startsWith('17670 matching records'));
      assert.equal(await page.locator('.case-card').count(),12);
    }
    checkpoints.push({check:'two full runs selectable without merging case denominators',records_per_run:17670,task4_event_rank:false});
  }
  await page.locator('#tab-cases').click();
  assert((await page.locator('#case-count').textContent()).startsWith('17670 matching records'));
  assert.equal(await page.locator('.case-card').count(),12);
  const filterStart=performance.now();await page.locator('#case-task').selectOption('3');await page.locator('#case-subset').selectOption('core');
  assert((await page.locator('#case-count').textContent()).startsWith('2000 matching records'));
  const filterSeconds=(performance.now()-filterStart)/1000;
  await page.locator('#case-subset').selectOption('task5_overlap');assert((await page.locator('#case-count').textContent()).startsWith('784 matching records'));
  await page.getByRole('button',{name:'Next',exact:true}).click();assert((await page.locator('.pager').textContent()).includes('Page 2 /'));
  await page.locator('#case-task').selectOption('5');await page.locator('#case-subset').selectOption('');
  assert((await page.locator('#case-count').textContent()).startsWith('2352 matching records'));
  await page.locator('#case-variant').selectOption('safe_guided');assert((await page.locator('#case-count').textContent()).startsWith('784 matching records'));
  await capture('scale-tool-cases-folded');
  await page.getByRole('button',{name:'Clear all case filters',exact:true}).click();
  const sid=profile.cases[0].source_id,searchStart=performance.now();await page.locator('#case-search').fill(sid);
  const expected=profile.cases.filter(c=>[c.sample_id,c.source_id,c.response.text,JSON.stringify(c.messages),JSON.stringify(c.metadata)].join('\n').toLowerCase().includes(sid.toLowerCase())).length;
  assert((await page.locator('#case-count').textContent()).startsWith(expected+' matching records'));
  const searchSeconds=(performance.now()-searchStart)/1000;
  await page.locator('#case-search').fill('__NO_REAL_CASE_MATCH_20261008__');assert((await page.locator('#case-count').textContent()).startsWith('0 matching records'));
  assert((await page.locator('#view').textContent()).includes('not a zero risk metric'));
  if(inputScope==='actual'&&expectedLengthLimits[0]>0){
    await page.locator('#tab-overview').click();
    await page.getByRole('button',{name:/^Reported length limit ·/}).click();
    assert((await page.locator('#case-count').textContent()).startsWith((2*expectedLengthLimits[0])+' matching records'));
    for(const task of ['3','4']){
      await page.locator('#case-task').selectOption(task);
      assert((await page.locator('#case-count').textContent()).startsWith(expectedLengthLimits[0]+' matching records'));
    }
    await capture('scale-actual-length-limit-cases');
    checkpoints.push({check:'actual length-limit flag / overview drilldown / Task3-Task4 response reuse',unique_generated_responses:expectedLengthLimits[0],case_records:2*expectedLengthLimits[0]});
    await page.getByRole('button',{name:'Clear all case filters',exact:true}).click();
  }
  await page.locator('#tab-metadata').click();await page.locator('#metadata-task').selectOption('5');await page.locator('#metadata-axis').selectOption('risk_category');await page.locator('#metadata-scope').selectOption('variant:safe_guided');
  assert((await page.locator('#view').textContent()).includes('High-Stakes Action'));assert(await page.locator('svg.chart [role="button"]').count()>0);await capture('scale-risk-category');
  await page.locator('svg.chart [role="button"]').first().click();assert.equal(await page.locator('#tab-cases').getAttribute('aria-selected'),'true');
  assert((await page.locator('#case-count').textContent()).includes('matching records'));assert((await page.locator('.filter-summary').textContent()).includes('risk_category'));
  checkpoints.push({check:'full cases / core / overlap / framing / pagination / literal-search / empty / metadata drilldown',literal_search_records:expected,primary_filter_seconds:filterSeconds,literal_search_seconds:searchSeconds});
  await page.setViewportSize({width:390,height:844});await page.locator('#tab-task4').click();
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1));await capture('scale-mobile-strategies');
  if(expectedRuns===2){await page.locator('#tab-comparison').click();assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1));await capture('scale-mobile-comparison');}
  assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
  const evidence={status:'passed',report:reportPath,html_bytes:fs.statSync(reportPath).size,renderer:data.renderer_version,input_scope:inputScope,models:data.runs.map(run=>run.run.model.id),runs:expectedRuns,records:data.runs.reduce((n,r)=>n+r.cases.length,0),records_per_run:17670,sources_per_run:2659,synthetic_only:inputScope==='fixture',gpu_inference:false,browser_is_not_inference_proof:true,measurement_accuracy_evidence:false,official_rank_eligible:false,browser:await browser.version(),load_seconds:loadSeconds,checkpoints,console_errors:errors,blocked_external_requests:external,screenshots};
  fs.writeFileSync(path.join(out,'scale-ui-evidence.json'),JSON.stringify(evidence,null,2)+'\n');console.log(JSON.stringify(evidence));
  await context.close();await browser.close();browser=null;
}
main().catch(async error=>{fs.writeFileSync(path.join(out,'scale-ui-failure.json'),JSON.stringify({status:'failed',error:error.stack,checkpoints,errors,external},null,2)+'\n');if(browser)await browser.close();console.error(error.stack);process.exitCode=1;});

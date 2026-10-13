/* Inspect a downloaded projected report offline, without another analysis job. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url'),{chromium}=require('playwright');
const input=path.resolve(process.argv[2]),out=path.resolve(process.argv[3]);fs.mkdirSync(out);
const errors=[],external=[];let browser;
(async()=>{
  browser=await chromium.launch({headless:true,executablePath:process.env.KOEVD_TEST_BROWSER});
  const c=await browser.newContext({viewport:{width:1440,height:1050}}),p=await c.newPage();
  await c.route('**/*',r=>{if(r.request().url()===pathToFileURL(input).href)return r.continue();external.push(r.request().url());return r.abort();});
  p.on('pageerror',e=>errors.push(e.message));await p.goto(pathToFileURL(input).href,{timeout:120000});
  await p.locator('#run-select').selectOption('1');
  assert((await p.locator('#view').textContent()).includes('Reference prompts, freeform responses, tool arguments and request IDs are withheld'));
  await p.screenshot({path:path.join(out,'reference-overview.png')});
  await p.locator('#tab-cases').click();await p.locator('#case-task').selectOption('3');
  await p.locator('.case-card summary').first().click();
  assert((await p.locator('.case-card pre').allTextContents()).join('\n').includes('Reference text withheld in the public beta'));
  await p.screenshot({path:path.join(out,'withheld-reference-case.png')});
  const disclosure=await p.evaluate(()=>{
    const data=JSON.parse(document.getElementById('koevd-data').textContent),ref=data.runs[1];
    return {records:ref.cases.length,all_raw_text_withheld:ref.cases.every(v=>
      v.response.text.startsWith('[Reference text withheld')&&v.messages.every(m=>m.content.startsWith('[Reference text withheld'))&&
      v.response.reasoning_content===null&&v.response.execution===null&&v.response.request_id===null&&v.response.response_id===null),
      all_tool_arguments_removed:ref.cases.filter(v=>v.task===5).every(v=>!v.parsed||!Object.hasOwn(v.parsed,'arguments')),
      declared_policy:ref.disclosure.policy};
  });
  assert.equal(disclosure.records,17670);assert(disclosure.all_raw_text_withheld);assert(disclosure.all_tool_arguments_removed);
  await p.setViewportSize({width:390,height:844});await p.locator('#tab-overview').click();
  assert(await p.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1));
  await p.screenshot({path:path.join(out,'reference-mobile.png')});
  assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
  fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({status:'passed',scope:'offline_projected_reference_visual_and_field_inspection',...disclosure,
    browser:await browser.version(),external_requests:external,page_errors:errors,new_analysis_or_HF_upload:false},null,2)+'\n');
  await browser.close();browser=null;console.log(JSON.stringify({status:'passed',records:17670,raw_disclosure_checks:true}));
})().catch(async e=>{fs.writeFileSync(path.join(out,'failure.json'),JSON.stringify({error:e.message,errors,external},null,2));if(browser)await browser.close();console.error(e.stack);process.exitCode=1;});

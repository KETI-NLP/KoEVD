/* Headless offline development QA, using no user browser session. */
const fs=require('node:fs');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const assert=require('node:assert/strict');
const {chromium}=require('playwright');
function arg(name,fallback){const i=process.argv.indexOf(name);return i<0?fallback:process.argv[i+1];}
const input=path.resolve(arg('--report','generated/conditions-cli-20261008/report/report-v2.html'));
const out=path.resolve(arg('--output-dir','generated/conditions-ui-20261008'));
const executable=arg('--browser-executable',process.env.KOEVD_TEST_BROWSER);
const errors=[],external=[],checks=[];
let browser;
async function main(){
 fs.mkdirSync(out,{recursive:true});
 browser=await chromium.launch({headless:true,...executable?{executablePath:executable}:{}});
 const context=await browser.newContext({viewport:{width:1440,height:1050}});
 const page=await context.newPage();
 page.on('pageerror',e=>errors.push(String(e)));
 page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
 await context.route('**/*',route=>{
  if(route.request().url()===pathToFileURL(input).href)return route.continue();
  external.push(route.request().url());return route.abort();
 });
 await page.goto(pathToFileURL(input).href,{waitUntil:'load'});
 await page.locator('#tab-method').click();
 await page.locator('summary').filter({hasText:'Measurement provenance and limits'}).click();
 assert((await page.locator('#view').textContent()).includes('koevd-measurement-conditions-v1'));
 assert((await page.locator('#view').textContent()).includes('measurement_limited'));
 await page.screenshot({path:path.join(out,'method-desktop.png')});
 checks.push('Portable condition block is visible in Method; limited status retained');
 await page.locator('#tab-comparison').click();
 await page.locator('#compare-task').selectOption('3');
 let body=await page.locator('#view').textContent();
 assert(body.includes('measurement.conditions.input_order')&&body.includes('measurement.conditions.inference_mode'));
 assert(body.includes('original')&&body.includes('reverse'));
 await page.getByText('measurement.conditions.input_order',{exact:true}).scrollIntoViewIfNeeded();
 await page.screenshot({path:path.join(out,'comparison-desktop.png')});
 checks.push('Task 3 order/mode comparison reasons are visible');
 await page.locator('#compare-task').selectOption('5');
 body=await page.locator('#view').textContent();
 assert(!body.includes('measurement.conditions.input_order')&&!body.includes('measurement.conditions.inference_mode'));
 checks.push('Task 5 does not inherit measurement-only restrictions');
 await page.setViewportSize({width:390,height:844});
 await page.locator('#tab-method').click();
 await page.locator('summary').filter({hasText:'Measurement provenance and limits'}).click();
 const pre=page.locator('summary').filter({hasText:'Measurement provenance and limits'}).locator('..').locator('pre');
 await pre.scrollIntoViewIfNeeded();
 await pre.evaluate(element=>{
  const text=element.firstChild,at=text.textContent.indexOf('"conditions"');
  const range=document.createRange();range.setStart(text,at);range.setEnd(text,at+12);
  element.scrollTop+=range.getBoundingClientRect().top-element.getBoundingClientRect().top-35;
 });
 const widths=await page.evaluate(()=>({client:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth}));
 assert(widths.scroll<=widths.client+1);
 await page.screenshot({path:path.join(out,'method-mobile.png')});
 checks.push('390px Method page with expanded conditions has no horizontal overflow');
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
 fs.writeFileSync(path.join(out,'evidence.json'),JSON.stringify({scope:'synthetic CPU report only',checks,errors,external,browser:await browser.version(),widths},null,2)+'\n');
 console.log(JSON.stringify({checks:checks.length,errors:errors.length,external:external.length}));
 await browser.close();
}
main().catch(async e=>{console.error(e);if(browser)await browser.close();process.exitCode=1;});

const {chromium}=require('playwright');
const {pathToFileURL}=require('url');
const path=require('path');
const fs=require('fs');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 try {
  const page=await browser.newPage({viewport:{width:1440,height:1000},offline:true});
  const errors=[];page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(pathToFileURL(path.resolve(process.argv[2])).href);
  await page.waitForFunction(()=>document.querySelector('#reference-counts tbody tr'));
  await page.locator('#reference-section summary').click();
  if(await page.locator('#reference-counts tbody tr').count()!==5)throw Error('Missing reference rows');
  if(await page.locator('#source-filters tbody tr').count()!==4)throw Error('Missing filter rows');
  const invalid=await page.evaluate(()=>{
   const reference=document.querySelector('#reference-counts').textContent;
   const expected=DATA.flow.reference_conventions.variants[0].attended_episodes;
   return !reference.includes(fmt(expected)) || document.querySelector('#quality').textContent.includes('[object Object]');
  });
  if(invalid)throw Error('Diagnostic values not rendered');
  fs.mkdirSync('.local/screenshots',{recursive:true});
  for(const width of [1440,390]){
   await page.setViewportSize({width,height:1000});
   await page.waitForFunction(()=>document.documentElement.scrollWidth<=innerWidth,{},{timeout:5000}).catch(async()=>{
    const offenders=await page.evaluate(()=>[...document.querySelectorAll('main,section,details,.table-wrap,.charts,.chart')].map(e=>({tag:e.tagName,id:e.id,cls:e.className,right:e.getBoundingClientRect().right,width:e.getBoundingClientRect().width})).filter(e=>e.right>innerWidth));
    throw Error('Viewport overflow: '+JSON.stringify(offenders));
   });
   for(const theme of ['light','dark']){
    await page.evaluate(theme=>document.documentElement.dataset.theme=theme,theme);
    await page.locator('#reference-section').scrollIntoViewIfNeeded();
    if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('Page overflow');
    await page.locator('#reference-section').screenshot({path:`.local/screenshots/reference-${width}-${theme}.png`});
   }
  }
  if(errors.length)throw Error(errors.join('\n'));
  console.log('REFERENCE_DIAGNOSTICS_OK offline desktop/mobile light/dark');
 } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exitCode=1});

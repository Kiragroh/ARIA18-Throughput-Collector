const {chromium}=require('playwright');
const {pathToFileURL}=require('url');
const path=require('path');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(pathToFileURL(path.resolve(process.argv[2])).href);
 await page.waitForFunction(()=>document.querySelector('#plot7')?.data?.length);
 const state=await page.evaluate(()=>({
  q1:DATA.periods.quarter.activity[0].groups.find(g=>g.machine==='ALL'),
  population:DATA.population.summary,
  names:DATA.population.devices.map(d=>d.machine),
  plots:document.querySelectorAll('.plot').length,
  populated:[...document.querySelectorAll('.plot')].filter(e=>e.data?.some(t=>(t.y||t.median||[]).some(v=>v!=null))).length
 }));
 if(state.q1.kpi.slot_coverage_pct==null)throw Error('Q1 unexpectedly hidden');
 if(!(state.population.patients>0&&state.population.new_plans>0))throw Error('Population missing');
 if(state.plots!==state.populated)throw Error('Blank charts: '+JSON.stringify(state));
 await page.selectOption('#granularity','month');
 if(await page.locator('#period option').count()!==12)throw Error('Month range');
 await page.locator('.chart button').nth(7).click();
 await page.waitForFunction(()=>document.querySelector('#modal-plot')?.data?.length);
 await page.screenshot({path:path.resolve('.local/screenshots/population-expanded.png')});
 await page.locator('#close').click();
 await page.setViewportSize({width:390,height:844});
 await page.waitForFunction(()=>document.documentElement.scrollWidth<=innerWidth,{},{timeout:5000});
 if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('Mobile overflow');
 await browser.close();
 if(errors.length)throw Error(errors.join('\n'));
 console.log('RECONCILIATION_BROWSER_OK '+JSON.stringify({plots:state.plots,populated:state.populated,devices:state.names}));
})().catch(e=>{console.error(e);process.exit(1)});

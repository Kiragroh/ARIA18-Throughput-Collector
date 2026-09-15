const {chromium}=require('playwright');
const {pathToFileURL}=require('url');
const path=require('path'),fs=require('fs');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 const page=await browser.newPage();const errors=[],remote=[];
 page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>{if(/^https?:/.test(r.url()))remote.push(r.url())});
 const out=path.resolve('.local/cooperation-review');fs.mkdirSync(out,{recursive:true});
 await page.goto(process.argv[2]||pathToFileURL(path.resolve('kooperation/index.html')).href);
 for(const [size,width,height] of [['desktop',1280,800],['wide',1920,1080],['mobile',390,844]]){
  await page.setViewportSize({width,height});
  await page.evaluate(()=>show(0));
  for(let i=0;i<7;i++){
   await page.evaluate(index=>show(index),i);
   const state=await page.evaluate(()=>({
    active:document.querySelectorAll('.slide:not([hidden])').length,
    overflow:document.documentElement.scrollWidth>innerWidth,
    vertical:document.documentElement.scrollHeight>innerHeight+1,
    badImage:[...document.querySelectorAll('.slide:not([hidden]) img')].some(im=>!im.complete||!im.naturalWidth)
   }));
   if(state.active!==1||state.overflow||state.badImage||(size!=='mobile'&&state.vertical))throw Error(size+' slide '+i+': '+JSON.stringify(state));
   await page.screenshot({path:path.join(out,size+'-'+(i+1)+'.png'),fullPage:true});
  }
 }
 await page.locator('#prev').click();if(!(await page.locator('#counter').innerText()).includes('6 / 7'))throw Error('Previous navigation');
 await page.locator('#next').click();if(!(await page.locator('#next').isDisabled()))throw Error('End state');
 const urls=await page.locator('a[href*="filesync.medizin.uni-leipzig.de"]').evaluateAll(es=>es.map(e=>e.href));
 if(urls.some(u=>u!=='https://filesync.medizin.uni-leipzig.de/u/d/7aa97de1de02445cad42/'))throw Error('Wrong upload');
 await page.emulateMedia({media:'print'});if(await page.locator('.slide:visible').count()!==7)throw Error('Print must include all slides');
 await page.pdf({path:path.join(out,'Praesentation.pdf'),preferCSSPageSize:true,printBackground:true});
 await browser.close();if(errors.length)throw Error(errors.join('\n'));
 if(!process.argv[2]&&remote.length)throw Error('Offline invitation requests external content');
 console.log('COOPERATION_BROWSER_OK 21 views navigation assets offline print');
})().catch(e=>{console.error(e);process.exit(1)});

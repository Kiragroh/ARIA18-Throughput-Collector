const {chromium}=require('playwright');
const {pathToFileURL}=require('url');
const path=require('path');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 const page=await browser.newPage({acceptDownloads:true});const errors=[];
 page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(pathToFileURL(path.resolve(process.argv[2])).href);
 await page.locator('#machines input[type=checkbox]').first().check();
 await page.locator('#activities select').first().selectOption('counselling');
 if(!(await page.locator('#checklist').innerText()).includes('1 Geraete'))throw Error('Selection not counted');
 const downloadPromise=page.waitForEvent('download');await page.locator('#download').click();
 const download=await downloadPromise;let data='';for await(const chunk of await download.createReadStream())data+=chunk;
 const profile=JSON.parse(data);if(profile.confirmed||profile.sources_complete||Object.keys(profile.machines).length!==1)throw Error('Invalid profile');
 for(const [w,h] of [[1440,1000],[390,844]]){
  await page.setViewportSize({width:w,height:h});
  if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('Form overflow');
 }
 await page.locator('#search').fill('CODE_THAT_DOES_NOT_EXIST');
 if(await page.locator('#activities tr').count())throw Error('Filter failed');
 await browser.close();if(errors.length)throw Error(errors.join('\n'));
 console.log('PREFLIGHT_BROWSER_OK desktop/mobile filter selection profile-download');
})().catch(e=>{console.error(e);process.exit(1)});

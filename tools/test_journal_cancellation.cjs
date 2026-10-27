// Run with Node.js and Playwright installed; local journal server must be on 8123.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const out = path.join(__dirname, '..', 'temporary screenshots', 'journal-cancellation');
fs.mkdirSync(out, { recursive: true });
const student = { id:'test', name:'Тестовая ученица', group:'choreo', plan:'month', fee:4000, sinceDate:'2026-10-01', active:true };
const fixture = { students:[student], sessions:{'2026-10-04__choreo':{ date:'2026-10-04', group:'choreo', present:['test'], absence:{} }}, payments:[{studentId:'test', amount:4000, date:'2026-10-01', month:'2026-10', group:'choreo', kind:'Абонемент'}], solo:[], settings:{}, updatedAt:1 };
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 try {
 for (const width of [430,1440,2560]) {
  const context=await browser.newContext({viewport:{width,height:900},serviceWorkers:'block'});
  // Never read or write the user's journal or contact cloud sync.
  await context.route('**/sync**', r=>r.fulfill({status:404,body:'{}'}));
  await context.route('https://**', r=>r.abort());
  await context.addInitScript(data=>localStorage.setItem('oneof-journal-v1',JSON.stringify(data)),fixture);
  await context.route('**/journal/', async r=>{
    const response=await r.fetch({url:'http://127.0.0.1:8123/journal/',headers:{...r.request().headers(),host:'localhost:8123'}});
    const html=(await response.text()).replace(/load\(\);\r?\nif\(D.settings.lockMoney/, 'window.qa={D:D,S:S,usedLessons:usedLessons,excusedLessons:excusedLessons,missedLessons:missedLessons,visitsOf:visitsOf,hallHours:hallHours,lessonBalance:lessonBalance,coveredUntil:coveredUntil,trialsOf:trialsOf,render:render,exportCsv:exportCsv};\nload();\nif(D.settings.lockMoney');
    await r.fulfill({response,body:html});
  });
  const page=await context.newPage();
  const errors=[]; page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://localhost:8123/journal/');
  await page.evaluate(()=>{qa.S.month='2026-10';qa.S.date='2026-10-04';qa.render();});
  const metrics=()=>page.evaluate(()=>{const q=qa,s=q.D.students[0];return {used:q.usedLessons(s),visits:q.visitsOf(s.id,'2026-10'),hours:q.hallHours('2026-10'),balance:q.lessonBalance(s),missed:q.missedLessons(s),excused:q.excusedLessons(s)};});
  assert.deepEqual(await metrics(),{used:1,visits:1,hours:2,balance:3,missed:0,excused:0});
  await page.screenshot({path:path.join(out,`${width}-before.png`)});
  await page.click('[data-act="cancel-lesson"]');
  await page.selectOption('#cancel-reason',{label:'Болезнь тренера'});
  await page.fill('#cancel-note','Занятие перенесём после выздоровления');
  await page.screenshot({path:path.join(out,`${width}-dialog.png`)});
  await page.click('[data-act="save-cancellation"]');
  assert.deepEqual(await metrics(),{used:0,visits:0,hours:0,balance:4,missed:0,excused:0});
  assert.equal(await page.locator('[data-act="toggle"]').count(),0);
  assert.equal(await page.locator('.chip.cancelled').count(),1);
  await page.screenshot({path:path.join(out,`${width}-cancelled-pass1.png`)});
  const saved=await page.evaluate(()=>JSON.parse(localStorage.getItem('oneof-journal-v1')));
  assert.equal(saved.sessions['2026-10-04__choreo'].cancelled,true);
  assert.deepEqual(saved.sessions['2026-10-04__choreo'].present,['test']);
  await context.addInitScript(data=>localStorage.setItem('oneof-journal-v1',JSON.stringify(data)),saved);
  await page.reload();
  await page.evaluate(()=>{qa.S.month='2026-10';qa.S.date='2026-10-04';qa.render();});
  assert.equal(await page.locator('[data-act="restore-lesson"]').count(),1);
  await page.screenshot({path:path.join(out,`${width}-cancelled-pass2.png`)});
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  page.once('dialog',d=>d.accept());
  await page.click('[data-act="restore-lesson"]');
  assert.deepEqual(await metrics(),{used:1,visits:1,hours:2,balance:3,missed:0,excused:0});
  // Cancelling an unrecorded date then restoring must not create a held lesson.
  await page.evaluate(()=>{qa.S.date='2026-10-11';qa.render();});
  await page.click('[data-act="cancel-lesson"]');
  await page.click('[data-act="save-cancellation"]');
  page.once('dialog',d=>d.accept()); await page.click('[data-act="restore-lesson"]');
  assert.equal(await page.evaluate(()=>!!qa.D.sessions['2026-10-11__choreo']),false);
  // A cancelled sick absence is neither charged nor counted as a medical transfer.
  await page.evaluate(()=>{qa.D.sessions['2026-10-04__choreo'].present=[];qa.D.sessions['2026-10-04__choreo'].absence={test:'sick'};qa.S.date='2026-10-04';qa.render();});
  await page.click('[data-act="cancel-lesson"]'); await page.click('[data-act="save-cancellation"]');
  assert.deepEqual(await metrics(),{used:0,visits:0,hours:0,balance:4,missed:0,excused:0});
  // Group isolation, cancelled trial, future coverage and CSV status.
  await page.evaluate(()=>{
    qa.D.sessions['2026-10-04__kpop']={date:'2026-10-04',group:'kpop',present:[]};
    qa.D.students.push({id:'trial',group:'choreo',plan:'trial',trialDate:'2026-10-04'});
  });
  assert.equal(await page.evaluate(()=>qa.hallHours('2026-10')),2);
  assert.equal(await page.evaluate(()=>qa.trialsOf('2026-10').length),0);
  const coverage=await page.evaluate(()=>{
    const st=qa.D.students[0],old=qa.coveredUntil(st);
    qa.D.sessions[old+'__choreo']={date:old,group:'choreo',cancelled:true,present:[]};
    return {old,next:qa.coveredUntil(st)};
  });
  assert.ok(coverage.next>coverage.old);
  const downloadPromise=page.waitForEvent('download'); await page.evaluate(()=>qa.exportCsv());
  const download=await downloadPromise; const csv=fs.readFileSync(await download.path(),'utf8');
  assert.ok(csv.includes('Отменено')); assert.ok(csv.includes('Болезнь тренера')===false); // latest cancellation selected Competition
  assert.ok(csv.includes('Конкурс'));
  assert.deepEqual(errors,[]);
  console.log(`${width}px: cancellation, reload, recovery, balances, rent, group isolation, trial, coverage, CSV, overflow OK`);
  await context.close();
 }
 } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exitCode=1;});

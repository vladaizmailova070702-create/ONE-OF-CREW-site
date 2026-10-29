// NODE_PATH must point to Playwright; serve the journal on localhost:8123.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const out = path.join(__dirname, '..', 'temporary screenshots', 'journal-payment-rates');
fs.mkdirSync(out, { recursive: true });
const students = [
  { id:'main', name:'Тестовая ученица', group:'choreo', plan:'month', fee:4000, sinceDate:'2026-09-06', active:true },
  { id:'extra', name:'Тестовая ученица', group:'kpop', plan:'month', fee:1500, note:'Второе направление', sinceDate:'2026-09-06', active:true }
];
const fixture = { students, sessions:{}, payments:[], solo:[], settings:{}, updatedAt:1 };
for (const date of ['09-06','09-13','09-20','09-27','10-04','10-11','10-18','10-25']) {
  for (const st of students) fixture.sessions[`2026-${date}__${st.group}`] = {date:`2026-${date}`, group:st.group, present:[st.id], absence:{}};
}
fixture.sessions['2026-11-01__kpop'] = {date:'2026-11-01', group:'kpop', cancelled:true, cancelReason:'Конкурс', cancellationOnly:true, present:[]};
for (const month of ['2026-09','2026-10','2026-11','2026-12']) {
  for (const st of students) {
    const amount = st.id==='main' ? (month==='2026-11' ? 5000 : 4000) : (month==='2026-12' ? 2000 : 1500);
    fixture.payments.push({id:`${st.id}-${month}`, studentId:st.id, studentName:st.name, group:st.group, month,
      date:month<'2026-11'?'2026-09-06':'2026-10-28', amount, kind:st.id==='extra' && month==='2026-12'?'Второе направление':'Абонемент', method:'Перевод'});
  }
}
(async()=>{
  const browser = await chromium.launch({channel:'chrome',headless:true});
  try {
    for (const width of [430,1440,2560]) {
      const context = await browser.newContext({viewport:{width,height:900},serviceWorkers:'block',timezoneId:'Asia/Vladivostok'});
      // Isolated storage and intercepted sync: never access the user's records.
      await context.route('**/sync**', r=>r.fulfill({status:404,body:'{}'}));
      await context.route('https://**', r=>r.abort());
      await context.addInitScript(data=>{
        localStorage.setItem('oneof-journal-v1', JSON.stringify(data));
        const RealDate = Date;
        window.Date = class extends RealDate {
          constructor(...args) { super(...(args.length?args:['2026-10-29T12:00:00+10:00'])); }
          static now() { return new RealDate('2026-10-29T12:00:00+10:00').getTime(); }
        };
      },fixture);
      await context.route('**/journal/', async r=>{
        const response = await r.fetch({url:'http://127.0.0.1:8123/journal/',headers:{...r.request().headers(),host:'localhost:8123'}});
        const html = (await response.text()).replace(/load\(\);\r?\nif\(D.settings.lockMoney/,
          'window.qa={D,S,boughtLessons,lessonPrice,lessonBalance,coveredUntil,render,studentModal,paymentModal,monthlyPaymentLine:typeof monthlyPaymentLine==="function"?monthlyPaymentLine:null,scheduledLessons:typeof scheduledLessons==="function"?scheduledLessons:null};\nload();\nif(D.settings.lockMoney');
        await r.fulfill({response,body:html});
      });
      const page = await context.newPage();
      const errors = []; page.on('pageerror',e=>errors.push(e.message));
      await page.goto('http://localhost:8123/journal/');
      const metrics = await page.evaluate(()=>({
        mainBought:qa.boughtLessons(qa.D.students[0]), extraBought:qa.boughtLessons(qa.D.students[1]),
        extraBalance:qa.lessonBalance(qa.D.students[1]), extraUntil:qa.coveredUntil(qa.D.students[1]),
        novPrice:qa.lessonPrice(qa.D.students[1],'2026-11-01'), decPrice:qa.lessonPrice(qa.D.students[1],'2026-12-01')
      }));
      assert.deepEqual(metrics,{mainBought:17,extraBought:16,extraBalance:8,extraUntil:'2026-12-27',novPrice:375,decPrice:500});
      const before = await page.evaluate(()=>JSON.stringify({students:qa.D.students,payments:qa.D.payments,sessions:qa.D.sessions}));
      for (const month of ['2026-11','2026-12']) {
        await page.evaluate(month=>{qa.S.month=month;qa.S.view='money';qa.render();},month);
        const monthly = await page.evaluate(()=>qa.D.students.map(st=>({planned:qa.scheduledLessons(st,qa.S.month).length,line:qa.monthlyPaymentLine(st)})));
        assert.deepEqual(monthly.map(x=>x.planned),month==='2026-11'?[5,4]:[4,4]);
        assert.ok(monthly[1].line.includes('4 занятия'));
        assert.ok(monthly[1].line.includes(month==='2026-11'?'1 500':'2 000'));
        assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
        await page.screenshot({path:path.join(out,`${width}-${month}-pass1.png`),fullPage:true});
        // Second render and capture catch state-dependent wrapping or stale month data.
        await page.evaluate(()=>qa.render());
        await page.screenshot({path:path.join(out,`${width}-${month}-pass2.png`),fullPage:true});
        // Native-resolution crops of each changed list and the payment history.
        for (const [i,block] of (await page.locator('.view > .block').all()).entries()) {
          await block.screenshot({path:path.join(out,`${width}-${month}-section${i}.png`)});
        }
      }
      assert.equal(await page.evaluate(()=>JSON.stringify({students:qa.D.students,payments:qa.D.payments,sessions:qa.D.sessions})),before);
      const cases = await page.evaluate(()=>{
        const extra=qa.D.students[1],main=qa.D.students[0];
        const stored = JSON.stringify(qa.D);
        // Solo payments do not buy group lessons; cash receipt date does not select the tariff.
        qa.D.payments.push({studentId:extra.id,amount:2000,month:'2026-12',date:'2026-10-28',kind:'Индивидуальное'});
        const noSolo=qa.boughtLessons(extra);
        const normalRate=qa.lessonPrice({id:'regular',group:'kpop',fee:3500,plan:'month'},'2026-12-01');
        const singleRate=qa.lessonPrice({id:'single',group:'kpop',fee:800,plan:'single',note:'Второе направление'},'2026-12-01');
        // Legacy identification works by payment kind when the old note is absent.
        extra.note=''; const byPaymentKind=qa.lessonPrice(extra,'2026-12-01');
        extra.fee=2000; const historicalRate=qa.lessonPrice(extra,'2026-11-01');
        // True partial payments must not promise an additional fully paid lesson.
        qa.D.payments=qa.D.payments.filter(p=>p.studentId!==main.id);
        qa.D.payments.push({studentId:main.id,amount:8250,month:'2026-10',kind:'Абонемент'});
        const partialUntil=qa.coveredUntil(main), partialBalance=qa.lessonBalance(main);
        qa.D.payments[qa.D.payments.length-1].amount=9250;
        const oneFullUntil=qa.coveredUntil(main);
        // Already-held dates and medical transfers are excluded from the coverage forecast.
        qa.D.sessions['2026-11-01__choreo']={date:'2026-11-01',group:'choreo',present:[main.id],absence:{}};
        const planned=qa.scheduledLessons(main,'2026-11').length;
        qa.D.sessions['2026-11-08__choreo']={date:'2026-11-08',group:'choreo',present:[],absence:{main:'sick'}};
        const medicalPlan=qa.scheduledLessons(main,'2026-11').length;
        const restored=JSON.parse(stored); Object.keys(restored).forEach(k=>qa.D[k]=restored[k]);
        return {noSolo,normalRate,singleRate,byPaymentKind,historicalRate,partialUntil,partialBalance,oneFullUntil,planned,medicalPlan};
      });
      assert.deepEqual(cases,{noSolo:16,normalRate:875,singleRate:800,byPaymentKind:500,historicalRate:375,partialUntil:'',partialBalance:0.25,oneFullUntil:'2026-11-01',planned:5,medicalPlan:4});
      // Payment suggestions use the tariff of the selected month.
      await page.evaluate(()=>{qa.S.month='2026-12';qa.D.payments=qa.D.payments.filter(p=>p.studentId!=='extra');qa.D.sessions={};qa.paymentModal(qa.D.students[1]);});
      assert.equal(await page.locator('#p-amount').inputValue(),'2000');
      assert.deepEqual(errors,[]);
      console.log(`${width}px: period tariffs, monthly breakdown, legacy data, partial payments, cancellation and unchanged records OK`);
      await context.close();
    }
  } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exitCode=1;});

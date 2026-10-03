// E kodu kaynak doğrulaması (03.10.2026). Çalıştır: node test/e_dogrulama.js
const db=JSON.parse(require('fs').readFileSync(__dirname+'/../data/e_kodlari.json'));
const by={};db.ingredients.forEach(i=>by[i.id]=i);
let fail=0,n=0;const ok=(c,m)=>{n++;if(!c){fail++;console.log('HATA',m)}};
db.ingredients.filter(i=>i.verification==='checked_2026_10'||i.verification==='partially_checked').forEach(i=>
  ok(Array.isArray(i.sources)&&i.sources.length&&i.sources.every(u=>/^https:\/\//.test(u)),i.id+' kaynaksız doğrulandı'));
db.ingredients.filter(i=>i.risk_level!=='green'&&i.verification==='general_knowledge').forEach(i=>ok(false,i.id+' renkli ama kaynaksız'));
ok(by.E407.risk_level==='yellow'&&/geçici/.test(by.E407.reason),'E407 EFSA 2018 düzeltmesi');
ok(by.E968.risk_level==='yellow'&&/0,5 g\/kg/.test(by.E968.reason),'E968 EFSA 2023 düzeltmesi');
ok(by.E955.risk_level==='green'&&!by.E955.flags.includes('debated'),'E955 EFSA 2026');
['E154','E160f','E230'].forEach(k=>ok(by[k].risk_level==='red'&&by[k].flags.includes('banned_eu'),k+' AB listesinde yok'));
ok(db.meta.counts.needs_review<=60,'needs_review '+db.meta.counts.needs_review);
console.log(n+' E kodu doğrulama denetimi, '+fail+' hata');process.exit(fail?1:0);

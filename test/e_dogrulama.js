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
// AB listesinden çıkarılanlar (2018/1481, 2023/2379) taramada "izinli" görünmez (06.10.2026)
['E311','E312','E483'].forEach(k=>ok(by[k].risk_level==='red'&&by[k].flags.includes('banned_eu')&&by[k].eu_status==='withdrawn',k+' AB izni kaldırıldı'));
db.ingredients.filter(i=>i.flags.includes('banned_eu')).forEach(i=>ok(i.eu_status!=='listed',i.id+' AB yasak bayrağı var ama eu_status=listed'));
// Günlük kabul edilebilir alım (ADI, 04.10.2026): doğrulanan değerin https kaynağı olur; sayı yalnızca st=set'te
db.ingredients.filter(i=>i.adi).forEach(i=>{const a=i.adi;
  ok(['set','ns','yok'].includes(a.st)&&['gun','hafta'].includes(a.per)&&a.src,i.id+' ADI alanları');
  ok(a.st==='set'?typeof a.v==='number'&&a.v>0:a.v===undefined,i.id+' ADI değeri');
  ok(!a.ok||/^https:\/\//.test(a.url||''),i.id+' doğrulanmış ADI kaynaksız')});
ok(by.E250.adi.v===0.07&&/nitrit iyonu/.test(by.E250.adi.as)&&by.E250.adi.ok,'E250 nitrit ADI');
ok(by.E251.adi.v===3.7&&by.E252.adi.v===3.7,'nitrat ADI');
ok(by.E220.adi.st==='yok'&&by.E228.adi.st==='yok','sülfit ADI geri çekildi (EFSA 2022)');
ok(by.E173.adi.per==='hafta','alüminyum haftalık');
ok(by.E950.adi.v===15&&by.E954.adi.v===9&&by.E955.adi.v===15,'2024-2026 tatlandırıcı güncellemeleri');
ok(db.meta.counts.needs_review<=60,'needs_review '+db.meta.counts.needs_review);
console.log(n+' E kodu doğrulama denetimi, '+fail+' hata');process.exit(fail?1:0);

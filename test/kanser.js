// Kanserojen uyarısı (gıda, kozmetik, temizlik). Çalıştır: node test/kanser.js
const fs=require('fs');
const {idx,L}=require('./run.js');
const {K,KL}=require('./kozmetik_cases.js');
eval(require('./yukle.js')+';global.TL={buildTIndex,analyzeT,summarizeT}');
const T=TL.buildTIndex(JSON.parse(fs.readFileSync(__dirname+'/../data/temizlik.json')));
let fail=0,n=0;const ok=(c,m)=>{n++;if(!c){fail++;console.log('HATA',m)}};
const g=t=>L.summarize(L.analyze(t,idx),idx).cancer.join();
const k=t=>KL.summarizeK(KL.analyzeK(t,K,{}),K).cancer.join();
const tm=t=>TL.summarizeT(TL.analyzeT(t,T,K)).cancer.join();
// Gıda: maddenin kendisi IARC 1/2A/2B
ok(/E250/.test(g("İçindekiler: Dana eti, tuz, koruyucu (sodyum nitrit)")),'nitrit');
ok(/E951/.test(g("İçindekiler: Su, tatlandırıcı (aspartam)")),'aspartam');
ok(/E150d/.test(g("İçindekiler: Su, renklendirici (E150d)")),'karamel E150d');
ok(g("İçindekiler: Su, koruyucu (sodyum benzoat), askorbik asit")==='','benzoat kanserojen sayıldı');
ok(g("İçindekiler: Su, tatlandırıcı (sakarin)")==='','sakarin (IARC Grup 3) kanserojen sayıldı');
ok(g("İçindekiler: Pirinç, renklendirici (kurkumin)")==='','kurkumin ("kanser yapıcı bulunmadı") sayıldı');
// Kozmetik: CMR ya da formaldehit salıcı
ok(k("Aqua, Glycerin, DMDM Hydantoin")!=='','formaldehit salıcı');
ok(k("Aqua, Glycerin, Cetearyl Alcohol, Parfum")==='','sıradan liste kanserojen sayıldı');
// Temizlik: yalnızca H350/H350i/H351
ok(/H351/.test(tm("DİKKAT. Kansere yol açma şüphesi var.")),'H351');
ok(/H350/.test(tm("H350 Kansere yol açabilir.")),'H350');
ok(tm("H360 Doğmamış çocukta hasara yol açabilir.")==='','H360 kanser sayıldı');
console.log(n+' durum, '+fail+' hata');process.exit(fail?1:0);

// Kozmetik K3 (AB dışı yasaklar, AB olası endokrin bozucu listesi) testleri. Çalıştır: node test/kozmetik_k3.js
const {K,KL}=require('./kozmetik_cases.js');
const fs=require('fs');
const kdb=JSON.parse(fs.readFileSync(__dirname+'/../data/kozmetik.json'));
let fail=0,n=0;
function ok(c,msg){n++;if(!c){fail++;console.log('HATA',msg)}}
function norm(s){return s.replace(/İ/g,"i").replace(/I/g,"ı").toLowerCase().replace(/[çğıöşüâîû]/g,c=>({ç:"c",ğ:"g",ı:"i",ö:"o",ş:"s",ü:"u",â:"a",î:"i",û:"u"})[c]).replace(/[^a-z0-9]+/g," ").trim()}

// Veri bütünlüğü (kdb ayrı okunduğu için nesneler değil alanlar karşılaştırılır)
const WL=kdb.meta.watch_lists;
ok(Array.isArray(kdb.watch)&&kdb.watch.length>=70,'watch kayıt sayısı '+(kdb.watch||[]).length);
kdb.watch.forEach(w=>{
  ok(WL[w.list],'bilinmeyen liste '+w.list);
  ok(/^https:\/\//.test(w.source||''),'kaynak yok '+w.inci);
  ok(w.inci.length>0,'INCI yok '+JSON.stringify(w));
  w.inci.forEach(a=>ok(K.map.has(norm(a))&&K.map.get(norm(a)).k3.some(x=>x.list===w.list&&x.date===w.date&&x.inci.join()===w.inci.join()),'indekste yok '+a));
});
['yellow','orange'].forEach(l=>ok(Object.values(WL).some(x=>x.level===l),'seviye eksik '+l));
ok(WL.ca.level==='orange'&&WL.asean.level==='orange'&&WL.ab_ed_a.level==='yellow'&&WL.ab_ed_b.level==='yellow','renk kararı (kademeli)');

// [metin, {ad: [seviye, beklenen liste(ler)]}, özet denetimi]
const cases=[
 // Salicylic acid AB'de CMR 2 olduğu için zaten turuncu; K3 rengi düşürmez
 ["Aqua, Methylparaben, Propylparaben, Salicylic Acid, Glycerin",
  {"METHYLPARABEN":["yellow",["ab_ed_b"]],"PROPYLPARABEN":["yellow",["ab_ed_a"]],"SALICYLIC ACID":["orange",["ab_ed_b"]],"GLYCERIN":["info",[]]},
  s=>s.ed.length===3&&s.ban.length===0],
 // AB'de kısıtlı (Ek III) ama Kaliforniya'da 2027'den itibaren yasak -> turuncu
 ["Aqua, Sodium Perborate, Zinc Borate, MEA-Borate",
  {"SODIUM PERBORATE":["orange",["ca"]],"ZINC BORATE":["orange",["ca"]],"MEA-BORATE":["orange",["ca"]]},s=>s.ban.length===3],
 // AB'de zaten yasak: kırmızı kalır, K3 bilgisi eklenir
 ["Aqua, Isobutylparaben, Cyclotetrasiloxane, Butylphenyl Methylpropional",
  {"ISOBUTYLPARABEN":["red",["ca"]],"CYCLOTETRASILOXANE":["red",["ab_reach","ca"]],"BUTYLPHENYL METHYLPROPIONAL":["red",["ab_ed_b","ca"]]},s=>s.red.length===3&&s.ban.length===3],
 // Cyclomethicone artık "AB'de yasak" (D4 kaydı) sayılmaz; endokrin listesi B grubu
 ["Cyclomethicone, Dimethicone",{"CYCLOMETHICONE":["yellow",["ab_ed_b","ab_reach"]],"DIMETHICONE":["info",[]]},s=>s.red.length===0],
 ["Aqua, Miconazole Nitrate",{"MICONAZOLE NITRATE":["orange",["asean"]]},s=>s.ban.length===1],
 // UV filtreleri: AB Ek VI (bilgi) + A grubu -> sarı
 ["C12-15 Alkyl Benzoate, Benzophenone-3, Octocrylene, Homosalate, Butyl Methoxydibenzoylmethane",
  {"BENZOPHENONE-3":["yellow",["ab_ed_a"]],"OCTOCRYLENE":["yellow",["ab_ed_a"]],"HOMOSALATE":["yellow",["ab_ed_a"]],"BUTYL METHOXYDIBENZOYLMETHANE":["info",[]]},s=>s.ed.length===3],
 // Eş anlamlı / Türkçe ad üzerinden de gelir
 ["Su, Gliserin, Metilparaben, BHT",{"METHYLPARABEN":["yellow",["ab_ed_b"]]},s=>s.ed.length===2],
 // D5: AB REACH kısıtlaması + Türkiye taslağı + AB endokrin B grubu; özette yalnızca endokrin satırına girer
 ["Cyclopentasiloxane, Cyclohexasiloxane",{"CYCLOPENTASILOXANE":["yellow",["ab_ed_b","ab_reach","tr_taslak"]],"CYCLOHEXASILOXANE":["yellow",["ab_reach"]]},s=>s.ed.length===1&&s.ban.length===0],
 // PFAS: Kaliforniya AB 2771 bilgisi bayrak açıklamasında
 ["PTFE, Mica",{"PTFE":["orange",[]]},s=>s.pfas.length===1],
];
for(const [t,exp,chk] of cases){
  const r=KL.analyzeK(t,K,{}),by={};r.forEach(x=>by[x.name]=x);
  for(const nm in exp){
    const x=by[nm],[lv,lists]=exp[nm];
    ok(x&&x.level===lv,t.slice(0,30)+' '+nm+' seviye beklenen '+lv+' bulunan '+(x&&x.level));
    const got=x?[...new Set(x.k3.map(w=>w.list))].sort():[];
    ok(JSON.stringify(got)===JSON.stringify(lists.slice().sort()),nm+' listeler beklenen '+lists+' bulunan '+got);
  }
  const S=KL.summarizeK(r,K);
  ok(!chk||chk(S),'özet '+t.slice(0,30)+' '+JSON.stringify({ban:S.ban,ed:S.ed,red:S.red,pfas:S.pfas}));
}
ok(/AB 2771/.test(kdb.meta.inci_flag_reasons.pfas),'PFAS açıklamasında AB 2771 yok');
// Türkiye durumu: 2023/1490 sonrası AB değişikliklerinde "tr" alanı ve açıklama metni
const TRT=kdb.meta.tr_text;ok(TRT&&TRT.yok&&TRT.taslak,'meta.tr_text yok');
const byId={};kdb.entries.forEach(e=>byId[e.id]=e);
ok(byId['II/1730']&&byId['II/1730'].tr==='taslak','4-MBC (2024/996) tr=taslak değil');
ok(byId['II/1731']&&byId['II/1731'].tr==='yok','TPO (2025/877) tr=yok değil');
ok(kdb.entries.filter(e=>e.annex==='II'&&!e.tr&&!(e.updates||[]).some(u=>u.tr)).length>1000,'eski kayıtlara tr eklenmemeli');
// summarizeK eski çağrı biçimi (K olmadan) çalışmaya devam etmeli
ok(KL.summarizeK(KL.analyzeK("Aqua, Methylparaben",K,{})).ed.length===1,'summarizeK K olmadan');
console.log(n+' K3 denetimi, '+fail+' hata');
process.exit(fail?1:0);

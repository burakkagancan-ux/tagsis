// Kozmetik (INCI) analizi testleri. Çalıştır: node test/kozmetik_cases.js
const fs=require('fs');
const h=fs.readFileSync(__dirname+'/../ocr.html','utf8');const src=h.slice(h.indexOf('/*LOGIC-START*/'),h.indexOf('/*LOGIC-END*/'));
eval(src+';global.KL={buildKIndex,analyzeK,summarizeK,inciItems,looksCosmetic}');
const K=KL.buildKIndex(JSON.parse(fs.readFileSync(__dirname+'/../data/kozmetik.json')),JSON.parse(fs.readFileSync(__dirname+'/../data/kozmetik_inci.json')));
module.exports={K,KL};
if(require.main!==module)return;
const names=(t,o)=>KL.analyzeK(t,K,o);
// [metin, seçenekler, beklenenler: {ad: seviye}, özet denetimi]
const cases=[
 ["Ingredients: Aqua, Glycerin, Cetearyl Alcohol, Parfum, Linalool, Limonene, Phenoxyethanol, CI 77891.",{},
  {"AQUA":"info","LINALOOL":"info","PHENOXYETHANOL":"info","CI 77891":"info"},s=>s.fragrance.length===2&&s.parfum&&s.unknown.length===0],
 ["AQUA (WATER), SODIUM LAURETH SULFATE, COCAMIDOPROPYL BETAINE, METHYLCHLOROISOTHIAZOLINONE, METHYLISOTHIAZOLINONE, DMDM HYDANTOIN",{ptype:"rinse"},
  {"METHYLISOTHIAZOLINONE":"yellow","DMDM HYDANTOIN":"yellow"},s=>s.formaldehyde.length===1&&s.preservative.length>=2],
 ["Aqua, Methylisothiazolinone",{ptype:"leave"},{"METHYLISOTHIAZOLINONE":"orange"},null],
 ["Ingredients: Butyl Acetate, Ethyl Acetate, Nitrocellulose, Trimethylbenzoyl Diphenylphosphine Oxide, Triphenyl Phosphate",{},
  {"TRIMETHYLBENZOYL DIPHENYLPHOSPHINE OXIDE":"red","TRIPHENYL PHOSPHATE":"red"},s=>s.red.length===2],
 ["Aqua, Butylphenyl Methylpropional, Hydroxyisohexyl 3-Cyclohexene Carboxaldehyde",{},{"BUTYLPHENYL METHYLPROPIONAL":"red","HYDROXYISOHEXYL 3-CYCLOHEXENE CARBOXALDEHYDE":"red"},null],
 // OCR hataları: harf/rakam karışması, tire, satır sonu
 ["INGREDIENTS: AQUA, GLYCERlN, PROPYLENE GLYC0L, Cl 77891, PEG-40 HYDROGENATED CASTOR OIL, 1,2-HEXANEDIOL, PHENOXY-\nETHANOL",{},
  {"GLYCERIN":"info","PROPYLENE GLYCOL":"info","CI 77891":"info","PEG-40 HYDROGENATED CASTOR OIL":"info","1,2-HEXANEDIOL":"info","PHENOXYETHANOL":"info"},s=>s.unknown.length===0],
 ["Aqua, Retinol, Salicylic Acid, Lanolin, Cera Alba, Hydrolyzed Collagen, Squalane",{ptype:"baby"},
  {"RETINOL":"yellow","SALICYLIC ACID":"orange","LANOLIN":"info"},s=>s.vitA.length===1&&s.kids.length===1&&s.nonVegan.length===2&&s.nonVeg.length===1&&s.veganUnsure.length===1],
 ["Cyclopentasiloxane, PTFE, Perfluorodecalin, Titanium Dioxide (nano)",{},{"PTFE":"orange","PERFLUORODECALIN":"orange"},s=>s.pfas.length===2],
 ["Talc, Mica, Dimethicone [+/- CI 77491, CI 77492, CI 77499]",{},{"TALC":"yellow","CI 77491":"info"},null],
 ["Aqua, Lavandula Angustifolia Oil, Rose Flower Oil/Extract",{},{"LAVANDULA ANGUSTIFOLIA OIL":"info","ROSE FLOWER OIL/EXTRACT":"info"},s=>s.fragrance.length===2],
];
let fail=0;
for(const [t,o,exp,chk] of cases){
  const r=names(t,o),by={};r.forEach(x=>by[x.name]=x.level);
  for(const n in exp)if(by[n]!==exp[n]){fail++;console.log('HATA',JSON.stringify(t).slice(0,60),n,'beklenen',exp[n],'bulunan',by[n]);}
  if(chk&&!chk(KL.summarizeK(r))){fail++;console.log('HATA özet',JSON.stringify(t).slice(0,60),JSON.stringify(KL.summarizeK(r)));}
}
// "may contain" bölümü
const mi=KL.inciItems("Talc, Mica [+/- CI 77491, CI 77891]");
if(!(mi.length===4&&mi[2].may&&!mi[1].may)){fail++;console.log('HATA may',JSON.stringify(mi))}
// Kozmetik/gıda ayrımı
if(!KL.looksCosmetic("Ingredients: Aqua, Glycerin, Parfum, Phenoxyethanol")){fail++;console.log('HATA looksCosmetic kozmetik')}
if(KL.looksCosmetic("İçindekiler: Şeker, buğday unu, bitkisel yağ, süt tozu, tuz, sitrik asit")){fail++;console.log('HATA looksCosmetic gıda')}
console.log(cases.length+3+' kozmetik durum, '+fail+' hata');
process.exit(fail?1:0);

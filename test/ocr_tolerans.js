// OCR hatalarına dayanıklılık ve yeni eş anlamlılar (gıda + kozmetik). Çalıştır: node test/ocr_tolerans.js
const {idx,L}=require('./run.js');
const {K,KL}=require('./kozmetik_cases.js');
let fail=0,n=0;
function ok(c,msg){n++;if(!c){fail++;console.log('HATA',msg)}}
const fids=t=>L.analyze(t,idx).map(x=>x.ids.join('+'));
const knames=t=>KL.analyzeK(t,K,{}).filter(x=>x.found).map(x=>x.name);

// Kozmetik: tipik OCR karışmaları -> doğru INCI
[["Parfurn","PARFUM"],["Carborner","CARBOMER"],["Xanthan Gurn","XANTHAN GUM"],["Niacinarnide","NIACINAMIDE"],
 ["50dium Benzoate","SODIUM BENZOATE"],["8enzyl Alcohol","BENZYL ALCOHOL"],["Pantheh0l","PANTHENOL"],["Watcr","WATER"],["Aromo","AROMA"]
].forEach(([v,want])=>{const g=knames("Aqua, "+v+", Glycerin");ok(g.includes(want),'kozmetik '+v+' -> '+want+' bulunan '+g)});
// Kozmetik: rakamlı gerçek adlar bozulmamalı
[["PEG-32","PEG-32"],["Polyquaternium-10","POLYQUATERNIUM-10"],["C12-15 Alkyl Benzoate","C12-15 ALKYL BENZOATE"],["CI 77891","CI 77891"],["1,2-Hexanediol","1,2-HEXANEDIOL"],["Ceteareth-20","CETEARETH-20"]
].forEach(([v,want])=>{const g=knames("Aqua, "+v+", Glycerin");ok(g.includes(want),'kozmetik rakamlı ad '+v+' bulunan '+g)});
// Kozmetik: düz yazıdaki kısa sözcükler bileşen sayılmamalı
ok(!knames("Kullanmadan önce later area care").includes("WATER"),'"later" WATER sayıldı');
ok(knames("Shake well before use. Store in a cool place.").length===0,'İngilizce talimat bileşen sayıldı');

// Gıda: OCR karışmaları
[["susarn","B:susam"],["5itrik asit","E330"],["iaktoz","B:laktoz"],["fihdik","B:findik"],["sekcr","B:seker"]
].forEach(([v,want])=>{const g=fids("su, "+v+", tuz");ok(g.includes(want),'gıda '+v+' -> '+want+' bulunan '+g)});
// Gıda: yanlış eşleşmemeli
ok(!fids("Mısır gevreği, demir, niasin, tiamin").some(x=>x==='E234'),'niasin -> E234 (nisin) oldu');
ok(!fids("şeker alkolü (maltitol)").includes('B:alkol'),'şeker alkolü -> alkol oldu');
ok(!fids("su, sukrloz, tuz").includes('B:seker'),'sukrloz -> şeker oldu');
ok(fids("Kakao, karnauba mumu").includes('E903'),'karnauba (rn) bozuldu');
// Gıda: yeni eş anlamlılar
const F=[["renklendirici (amonyak sülfitli karamel)","E150d"],["kostik sülfitli karamel","E150b"],["briliant mavi FCF","E133"],
 ["koyulaştırıcılar (ksantan gam)","B:upf_sinif_kivam"],["stabilizörler (guar gam)","B:upf_sinif_kivam"],["aroma güçlendirici (monosodyum glutamat)","B:upf_sinif_lezzet"]];
F.forEach(([t,want])=>ok(fids(t).includes(want),'gıda eş anlamlı '+t+' -> '+want+' bulunan '+fids(t)));
ok(!fids("amonyak sülfitli karamel").includes('E527'),'amonyak sülfitli karamel -> E527 oldu');
ok(!fids("aroma güçlendirici (monosodyum glutamat)").includes('B:aroma'),'aroma güçlendirici aroma verici sayıldı');
console.log(n+' OCR/eş anlamlı denetimi, '+fail+' hata');
process.exit(fail?1:0);

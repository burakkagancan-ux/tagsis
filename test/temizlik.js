// Temizlik ürünü analizi testleri. Çalıştır: node test/temizlik.js
const fs=require('fs');
const {K}=require('./kozmetik_cases.js');
const h=fs.readFileSync(__dirname+'/../ocr.html','utf8');const src=h.slice(h.indexOf('/*LOGIC-START*/'),h.indexOf('/*LOGIC-END*/'));
eval(src+';global.TL={buildTIndex,analyzeT,summarizeT,looksCleaning,looksCosmetic}');
const tdb=JSON.parse(fs.readFileSync(__dirname+'/../data/temizlik.json'));
const T=TL.buildTIndex(tdb);
let fail=0,n=0;
function ok(c,msg){n++;if(!c){fail++;console.log('HATA',msg)}}
const same=(a,b)=>a.slice().sort().join()===b.slice().sort().join();

// Veri bütünlüğü
ok(tdb.hazards.length>=100,'ifade sayısı');
tdb.hazards.forEach(x=>{ok(['red','yellow','info'].includes(x.level),'seviye '+x.code);ok(x.tr&&x.en,'metin '+x.code);ok(tdb.meta.group_labels[x.group],'grup '+x.code)});
['H314','H318','H304','H334','H350','H360','H300','H301','H330','H331'].forEach(c=>ok(T.byCode[c].level==='red','ciddi tehlike kırmızı '+c));
['H302','H315','H317','H319','H335','H412','EUH208','EUH206'].forEach(c=>ok(T.byCode[c].level==='yellow','uyarı sarı '+c));
tdb.groups.forEach(g=>g.pat.forEach(p=>{ok(!/\(\?<[=!]/.test(p),'lookbehind '+g.id);new RegExp(p)}));
tdb.subs.forEach(s=>s.inci.forEach(a=>ok(K.map.has(a.toLowerCase()),'INCI dizinde yok '+a)));

// [metin, beklenen ifadeler, beklenen gruplar {id: bant|null|"neg"}, ek denetim(A,S)]
const cases=[
 ["İçindekiler: %5-15 anyonik yüzey aktif maddeler, %5'ten az noniyonik yüzey aktif maddeler, sabun, fosfonatlar, enzimler, optik parlatıcılar, parfüm (Hexyl Cinnamal, Limonene, Linalool), koruyucu (Benzisothiazolinone, Methylisothiazolinone). TEHLİKE. Ciddi göz hasarına yol açar. Cilt tahrişine yol açar. Çocukların ulaşamayacağı yerde saklayın. Koruyucu eldiven kullanın.",
  ['H318','H315'],{anyonik:'b5_15',noniyonik:'b5',sabun:'b5',fosfonat:'b5',enzim:null,optik:null,parfum:null,koruyucu:null},
  (A,S)=>same(S.fragrance,['HEXYL CINNAMAL','LIMONENE','LINALOOL'])&&S.pres.includes('BENZISOTHIAZOLINONE')&&S.pres.includes('METHYLISOTHIAZOLINONE')&&A.signal==='tehlike'&&S.level==='red'&&S.enzyme&&!S.mix],
 ["Sodyum hipoklorit içerir. %5'ten az klor bazlı ağartıcı, noniyonik yüzey aktif madde, parfüm. DİKKAT. Cilt tahrişine yol açar. Ciddi göz tahrişine yol açar. Sucul ortamda uzun süre kalıcı, zararlı etki. EUH206 Dikkat! Diğer ürünlerle birlikte kullanmayın. Tehlikeli gazlar açığa çıkarabilir (klor). EUH031: Asitlerle temas ettiğinde toksik gaz açığa çıkarır.",
  ['H315','H319','H412','EUH206','EUH031'],{klor:'b5',noniyonik:'b5',parfum:null},
  (A,S)=>S.mix&&A.signal==='dikkat'&&S.level==='yellow'&&A.subs.some(x=>x.s.id==='hipoklorit')],
 ["H314 H290 EUH208 Contains: 1,2-benzisothiazol-3(2H)-one. May produce an allergic reaction.",
  ['H314','H290','EUH208'],{},(A,S)=>A.subs.some(x=>x.s.id==='bit')&&A.hazards.find(x=>x.code==='EUH208').how.includes('metin')],
 ["Ingredients: 5-15% anionic surfactants, <5% non-ionic surfactants, phosphonates, enzymes, perfume, preservatives (Phenoxyethanol). Causes serious eye irritation. Harmful to aquatic life with long lasting effects.",
  ['H319','H412'],{anyonik:'b5_15',noniyonik:'b5',fosfonat:'b5',enzim:null,parfum:null,koruyucu:null},(A,S)=>S.pres.includes('PHENOXYETHANOL')],
 // OCR bozulması: eksik harf, ş->s
 ["Ciddi göz hasarina yol acar. Cilt tahrisine yol açr.",['H318','H315'],{},(A)=>A.hazards.every(x=>x.how.includes('benzer')||x.how.includes('metin'))],
 // Bant grubun arkasında
 ["Anyonik yüzey aktif maddeler %15-30, noniyonik yüzey aktif maddeler %5'ten az, sabun.",[],{anyonik:'b15_30',noniyonik:'b5',sabun:null}],
 ["Fosfat içermez. %5-15 anyonik yüzey aktif madde.",[],{fosfat:'neg',anyonik:'b5_15'}],
 ["Fosfatsız formül. Zeolit, polikarboksilatlar.",[],{fosfat:'neg',zeolit:null,polikarboksilat:null}],
 ["%30 ve üzeri: zeolit. %5-15: oksijen bazlı ağartıcılar, polikarboksilatlar.",[],{zeolit:'b30',oksijen:'b5_15',polikarboksilat:'b5_15'}],
 // H413 metni H412'yi içerir: yalnızca uzun olan
 ["Sucul ortamda uzun süre kalıcı, zararlı etki yapabilir.",['H413'],{}],
 ["Yutulduğunda veya solunduğunda zararlıdır.",['H302','H332'],{}],
 ["Solunması halinde kansere yol açabilir.",['H350i'],{}],
 ["Koruyucu gözlük kullanın. Göz koruyucu takın.",[],{}],
 ["Sodyum hidroksit içerir. TEHLİKE H314 Ciddi cilt yanıklarına ve göz hasarına yol açar. H290 Metalleri aşındırabilir.",['H314','H290'],{},
  (A,S)=>A.hazards.find(x=>x.code==='H314').how.join()==='kod,metin'&&S.eye.includes('H314')&&S.level==='red'],
 // "Neden olur" biçimi ve kod son eki
 ["H319 Ciddi göz tahrişine neden olur. H360FD",['H319','H360FD'],{}],
 ["Solunması halinde nefes alma zorlukları, astım nöbetleri veya alerjiye yol açabilir. Subtilisin, Protease.",['H334'],{},(A,S)=>S.resp.includes('H334')&&S.enzyme],
 // Asitli ürün: çamaşır suyuyla karıştırma uyarısı
 ["Hidroklorik asit içerir. Çamaşır suyu ile karıştırmayın. H314",['H314'],{},(A,S)=>S.mix],
];
cases.forEach(([t,hz,gr,chk],i)=>{
  const A=TL.analyzeT(t,T,K),S=TL.summarizeT(A);
  ok(same(A.hazards.map(x=>x.code),hz),i+': ifadeler '+JSON.stringify(A.hazards.map(x=>x.code))+' beklenen '+JSON.stringify(hz));
  const got={};A.groups.forEach(g=>got[g.id]=g.neg?'neg':g.band);
  ok(JSON.stringify(Object.keys(got).sort())===JSON.stringify(Object.keys(gr).sort()),i+': gruplar '+JSON.stringify(got));
  Object.keys(gr).forEach(k=>ok(got[k]===gr[k],i+': bant '+k+' '+got[k]+' beklenen '+gr[k]));
  if(chk)ok(chk(A,S),i+': ek denetim '+JSON.stringify({sig:A.signal,mix:S.mix,fr:S.fragrance,pres:S.pres,lvl:S.level,subs:A.subs.map(x=>x.s.id)}));
});

// Yanlış eşleşme olmamalı: gıda ve kozmetik etiketleri
const FOOD="İçindekiler: Şeker, buğday unu, bitkisel yağ (palm), glikoz şurubu, yağsız süt tozu, koruyucu (E 202), aroma verici. Enerji 450 kcal. Fındık içerebilir.";
const COS="Ingredients: Aqua, Sodium Laureth Sulfate, Cocamidopropyl Betaine, Glycerin, Parfum, Citric Acid, Sodium Benzoate, Linalool.";
[FOOD,COS].forEach((t,i)=>{const A=TL.analyzeT(t,T,K);ok(A.hazards.length===0,'yanlış ifade '+i+' '+A.hazards.map(x=>x.code))});
ok(!TL.looksCleaning(FOOD),'looksCleaning gıda');
ok(!TL.looksCleaning(COS),'looksCleaning kozmetik');
ok(TL.looksCleaning(cases[0][0]),'looksCleaning çamaşır');
ok(TL.looksCleaning(cases[1][0]),'looksCleaning çamaşır suyu');

// Hız: uzun metin
const long=cases.map(c=>c[0]).join(' ').repeat(3);const t0=Date.now();TL.analyzeT(long,T,K);const ms=Date.now()-t0;
ok(ms<1500,'yavaş: '+ms+' ms');
console.log(n+' denetim ('+cases.length+' temizlik durumu, '+ms+' ms), '+fail+' hata');
process.exit(fail?1:0);

const {idx,L,tg}=require('./run.js');
function ids(t){return L.analyze(t,idx).map(x=>x.ids.join('+')+(x.may?'~may':'')+(x.neg?'~neg':'')+(x.aroma?'~aroma':''))}
const cases=[
 ["Un, su, tuz, maya", ["B:un","B:n_hamur_mayasi"], []],
 ["Mısır unu, pirinç unu, şeker", ["B:n_glutensiz_un","B:seker"], ["B:un","B:bugday"]],
 ["Hindistan cevizi sütü, kakao yağı, badem sütü", ["B:n_hindistan","B:n_kakao","B:badem"], ["B:sut","B:tereyagi"]],
 ["Şeker, süt aroması, tereyağı aroması", ["B:n_sut_aroma"], ["B:sut","B:tereyagi"]],
 ["Şeker, peynir aromalı çeşni", [], []],
 ["İçindekiler: şeker, kakao, süt tozu, fındık ezmesi, emülgatör (soya lesitini) Eser miktarda yer fıstığı içerebilir", ["B:findik","B:yer_fistigi~may"], ["B:findik~may"]],
 ["şeker, buğday unu, süt tozu, fındık, susam içerebilir", ["B:susam~may","B:findik~may"], []],
 ["Bu ürün yer fıstığı ve susam kullanılan aynı tesiste üretilmiştir. İçindekiler: mısır, tuz.", ["B:yer_fistigi~may","B:susam~may"], []],
 ["Buğday glukoz şurubu, dekstroz", ["B:bugday_glukoz","B:dekstroz"], ["B:bugday","B:glukoz_surubu"]],
 ["Renklendirici (karamel), karamel aroması", [], []],
 ["Palm yağı içermez. Ayçiçek yağı, şeker", ["B:palm~neg","B:seker"], ["B:palm"]],
 ["süt ve yumurta içermez", ["B:yumurta~neg"], []],
 ["Bal kabağı çekirdeği, tuz", ["B:n_balkabagi"], ["B:bal"]],
 ["Mürekkep balığı, karides", ["B:yumusakca","B:kabuklu"], ["B:balik"]],
 ["Askorbil palmitat, E304", [], ["B:palm"]],
 ["Tavuk eti, mekanik ayrılmış kanatlı eti, jelatin (sığır)", ["B:tavuk","E441"], []],
 ["glukoz-fruktoz şurubu, invert şeker şurubu", ["B:gfs","B:invert"], []],
 ["Laktozsuz süt, laktaz enzimi", ["B:sut"], []],
 ["peynir mayası, mikrobiyal peynir mayası", ["B:peynir_mayasi","B:mikrobiyal_maya"], []],
 ["Antep fıstığı, çam fıstığı, fıstık", ["B:antep","B:n_cam_fistigi","B:fistik"], []],
];
let fail=0;
for(const [t,must,mustNot] of cases){
  const got=ids(t);const miss=must.filter(m=>!got.includes(m));const bad=mustNot.filter(m=>got.includes(m));
  if(miss.length||bad.length){fail++;console.log('HATA:',t,'\n  bulunan:',got.join(', '),'\n  eksik:',miss,' fazla:',bad)}
}
console.log(cases.length+' durum, '+fail+' hata');
// Karamel bağlamı
console.log('karamel:',ids("Renklendirici (karamel), karamel aroması").join(', '));
console.log('peynir aromalı:',ids("Şeker, peynir aromalı çeşni").join(', '));
// Marka
const br=L.buildBrands(tg);console.log('marka sayısı',Object.keys(br).length);
console.log(L.findBrands("Üretici: DOY HOREKA Gıda. İçindekiler: süt, tuz",br));
console.log(L.findBrands("İçindekiler: doğal köy yoğurdu, petek bal, royal jelly, yıldız",br));

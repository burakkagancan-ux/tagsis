// İngilizce etiket tanıma (B-08, 08.10.2026): ölçüm eşikleri + benzer yazım ve diller arası çakışma durumları. CI'da çalışır.
// Ayrıntılı rapor: node test/olcum_ingilizce.js
const {idx,L}=require('./run.js');
const {olc}=require('./olcum_ingilizce.js');
const db=require('../data/e_kodlari.json'),bdb=require('../data/bilesenler.json');
let n=0,hata=0;
function ok(c,m){n++;if(!c){hata++;console.log('HATA: '+m)}}
const an=t=>L.analyze(t,idx);
const ids=t=>an(t).filter(r=>!r.neg).map(r=>r.ids.join('/'));
const al=t=>{const S=L.summarize(an(t),idx),o={};for(const k of Object.keys(S.allergen)){const a=S.allergen[k];if(a.yes.length||a.may.length)o[k.replace('allergen_','')]=a.yes.length?'yes':'may'}return o};
const uyari=t=>an(t).filter(r=>!r.isB&&!r.neg&&r.rank>=2).map(r=>r.ids.join('/'));

// 1) Eşikler (test/veri/ingilizce_etiketler.json, 30 etiket)
const ESIK={parca:0.85,alerjen:1,yanlis:0};
const o=olc();
ok(o.oran.parca>=ESIK.parca,`içerik parçası tanıma %${Math.round(o.oran.parca*100)} < %${ESIK.parca*100}`);
ok(o.oran.alerjen>=ESIK.alerjen,`beklenen alerjen %${Math.round(o.oran.alerjen*100)} < %100: `+o.etiket.filter(e=>e.alEksik.length).map(e=>e.ad+' '+e.alEksik).join('; '));
ok(o.yanlis.length<=ESIK.yanlis,'yanlış uyarı: '+o.yanlis.join(' | '));

// 2) Benzer yazım: başka maddenin adı ya da yalnızca son ek farkı benzer yazım sayılmaz; risk yükseltilmez
for(const t of ['Sodium Citrate','Ingredients: Acidity Regulator (Sodium Citrate)','Sodium Citrate, şeker, su','İçindekiler: asitlik düzenleyici (Sodium Citrate)']){
  ok(ids(t).includes('E331'),t+' -> E331 değil: '+ids(t));ok(!uyari(t).length,t+' uyarı veriyor: '+uyari(t));
}
ok(ids('Ingredients: Sodium Nitrite').includes('E250'),'sodium nitrite E250 değil');
const yok=[['Ingredients: sweetened condensed milk','B:upf_sinif_tatlandirici'],['carbonic acid','E120'],['Ingredients: carbonic acid','E120'],['cellulase','E460'],
  ['Ingredients: sodium aluminum phosphate','E173'],['Ingredients: batter (wheat flour, water)','B:tereyagi'],['kırmızı, sarı biber','B:alkol'],['kırmızı > sarı','B:alkol'],
  ['Ingredients: non-hydrogenated vegetable oils','B:hidrojenize'],['Ingredients: calcium sulfate','E513'],['Ingredients: sodium nitrate','E250']];
for(const [t,id] of yok)ok(!ids(t).includes(id),`${t} -> ${id} eşleşmemeli: ${ids(t)}`);
ok(ids('Ingredients: sodium aluminum phosphate').includes('E541'),'ABD yazımı: sodium aluminum phosphate E541 değil');
ok(ids('Ingredients: Sodium Cltrate, Potasslum Sorbate').join()==='E331,E202','OCR benzer yazımı (cltrate, potasslum): '+ids('Ingredients: Sodium Cltrate, Potasslum Sorbate'));
// Her E kodu İngilizce adı ve her eş anlamlı kendi maddesine gider; benzer yazımla başka maddeye düşmez
for(const e of db.ingredients)for(const a of [e.name_en].concat(e.aliases_en||[])){
  const r=an('Ingredients: '+a).filter(x=>x.how==='benzer'&&!x.ids.includes(e.id));ok(!r.length,`${e.id} «${a}» benzer yazımla ${r.map(x=>x.ids.join('/'))}`);
}
for(const b of bdb.items)for(const a of b.aliases.concat(b.aliases_en||[],b.en_only||[])){
  for(const t of [a,'Ingredients: '+a]){const r=an(t).filter(x=>x.how==='benzer'&&!x.ids.includes('B:'+b.id));ok(!r.length,`${b.id} «${t}» benzer yazımla ${r.map(x=>x.ids.join('/'))}`)}
}

// 3) Diller arası çakışma: İngilizce kısa adlar (salt, soy, ham, tuna, rum) yalnızca İngilizce metinde; "turkey" ülke adı et sayılmaz
ok(!ids('Salt okunur bellek, ürün Türkiye’de üretilmiştir').includes('B:tuz'),'Türkçe "salt" tuz sayıldı');
ok(ids('Ingredients: Water, Salt').includes('B:tuz'),'İngilizce "salt" tanınmadı');
ok(!ids('Tuna nehri kıyısında üretilmiştir').includes('B:balik'),'Türkçe "Tuna" balık sayıldı');
ok(!ids('Ingredients: sugar, water. Made in Turkey. Product of Turkey.').includes('B:tavuk'),'"Turkey" (ülke) et sayıldı');
ok(ids('Ingredients: Turkey Meat (60%), Water').includes('B:tavuk'),'"turkey meat" tanınmadı');
ok(!ids('Soy ağacı').includes('B:soya'),'Türkçe "soy" soya sayıldı');
ok(al('Contains: Milk, Soy.').soy==='yes','"Contains: Milk, Soy" soya bulunmadı');

// 4) Alerjen: uzun ad kısa alerjen adını yutar; olumsuzluk; "may contain"
const alYok=[['Ingredients: cocoa butter','milk'],['Ingredients: coconut milk','milk'],['Ingredients: almond butter','milk'],['Ingredients: peanut butter','milk'],
  ['Ingredients: pine nuts','nuts'],['Ingredients: butter beans','milk'],['Ingredients: corn semolina','gluten'],['Ingredients: sunflower lecithin','soy'],
  ['Gluten free. Ingredients: rice flour','gluten'],['Free from milk and egg. Ingredients: sugar','milk'],['Free from milk and egg. Ingredients: sugar','egg'],
  ['Ingredients: sugar, salt. No added milk.','milk'],['Ingredients: sugar, salt. This product does not contain milk.','milk'],['Ingredients: soybean oil','soy']];
for(const [t,k] of alYok)ok(!al(t)[k],`${t} -> ${k} alerjeni çıkmamalı: ${JSON.stringify(al(t))}`);
const alVar=[['Ingredients: Buttermilk (Milk)','milk','yes'],['Ingredients: Spice and Herb Extracts (contain Celery)','celery','yes'],['Ingredients: Wheat Flour','gluten','yes'],
  ['Ingredients: soy lecithin','soy','yes'],['Ingredients: lecithin','soy','may'],['Ingredients: modified wheat starch','gluten','yes'],['İçindekiler: modifiye buğday nişastası','gluten','yes'],
  ['Ingredients: sugar. May contain nuts.','nuts','may'],['Ingredients: sugar, milk. May contain traces of peanuts.','peanut','may'],['Ingredients: sugar, milk. May contain traces of peanuts.','milk','yes'],
  ['Ingredients: oats. Manufactured in a facility that also processes sesame.','sesame','may'],['Ingredients: oats. Manufactured in a facility that also processes sesame.','gluten','yes'],
  ['Ingredients: Cooked Prawns','crustacean','yes'],['Ingredients: Kosher Gelatin, Yogurt','milk','yes'],['Ingredients: triticale','gluten','yes']];
for(const [t,k,v] of alVar)ok(al(t)[k]===v,`${t} -> ${k} ${v} beklenirdi: ${JSON.stringify(al(t))}`);
// Besin tablosu satırı bileşen sayılmaz
ok(!ids('Nutrition: Fat 20g, of which sugars 30g, Salt 0.5g').length,'besin tablosu satırı bileşen sayıldı: '+ids('Nutrition: Fat 20g, of which sugars 30g, Salt 0.5g'));

console.log(`${n} İngilizce tanıma denetimi (parça %${Math.round(o.oran.parca*100)}, alerjen %${Math.round(o.oran.alerjen*100)}, E kodu %${Math.round(o.oran.kod*100)}, yanlış uyarı ${o.yanlis.length}), ${hata} hata`);
process.exit(hata?1:0);

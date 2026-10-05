// Gizli sodyum / tuz testleri. Çalıştır: node test/sodyum.js
const {idx,L}=require('./run.js');
let fail=0,n=0;const ok=(c,m)=>{n++;if(!c){fail++;console.log('HATA',m)}};
const na=t=>L.summarize(L.analyze(t,idx),idx).sodium;
const ids=t=>L.analyze(t,idx).map(x=>x.ids.join('+')+(x.neg?'~neg':''));
let s;
s=na("İçindekiler: Patates, ayçiçek yağı (%35), tuz (%1,5), maltodekstrin, aroma güçlendirici (monosodyum glutamat)");
ok(s.salt.length===1&&s.saltOrd===3,'tuz 3. sırada '+JSON.stringify(s));
ok(s.hidden.some(x=>/E621/.test(x)),'MSG sodyum kaynağı');
s=na("İçindekiler: Buğday unu, şeker, bitkisel yağ, kakao, peynir altı suyu tozu, tuz, kabartıcı (sodyum bikarbonat)");
ok(s.saltOrd===6&&s.hidden.some(x=>/E500/.test(x)),'tuz 6. sırada + E500 '+JSON.stringify(s));
// Besin değerleri tablosundaki "Tuz 0,01 g" bileşen sayılmaz
s=na("İçindekiler: Şeker, kakao. Besin değerleri (100 g): Enerji 520 kcal, Tuz 0,01 g, Şekerler 55 g");
ok(s.salt.length===0,'besin tablosu satırı tuz sayıldı');
ok(!ids("İçindekiler: Kakao yağı, süt tozu. Besin değerleri: Şeker 48 g").includes('B:seker'),'besin tablosu satırı şeker sayıldı');
ok(ids("Fındık (%10), şeker %5").includes('B:seker'),'yüzdeli bileşen (birimsiz) düşmemeli');
// Olumsuzluk: iki sözcüklü "ilave edilmemiştir"
ok(na("Tuz ilave edilmemiştir. İçindekiler: domates").salt.length===0,'tuz ilave edilmemiştir');
ok(ids("Şeker ilave edilmemiştir. Elma suyu").includes('B:seker~neg'),'şeker ilave edilmemiştir olumsuz değil');
// Gizli kaynaklar ve alerjen korunur
s=na("Su, soya sosu (su, soya fasulyesi, buğday, tuz), et bulyonu");
ok(s.hidden.includes('Soya sosu')&&s.hidden.includes('Et / tavuk bulyonu'),'soya sosu / bulyon '+JSON.stringify(s));
const sum=L.summarize(L.analyze("Su, soya sosu",idx),idx);
ok(sum.allergen.allergen_soy&&sum.allergen.allergen_soy.yes.length,'soya sosu soya alerjeni kalmalı');
ok(L.summarize(L.analyze("Pirinç, tavuk bulyonu",idx),idx).vegan.no.length>0,'tavuk bulyonu vegan değil');
ok(na("Deniz tuzu, kaya tuzu, iyotlu tuz").salt.length===1,"tuz türleri tek kayıt");ok(na("Su, himalaya tuzu").salt.length===1,"himalaya tuzu");
// Tuz yok
s=na("İçindekiler: Yulaf, kuru üzüm, fındık");
ok(!s.salt.length&&!s.hidden.length,'tuzsuz ürün');
// Genel ad + E kodu aynı madde: tek kart (E1422 çift kart olmaz); kod yoksa genel ad kalır
ok(JSON.stringify(ids('Su, modifiye mısır nişastası (E1422), tuz'))===JSON.stringify(['E1422','B:tuz']),'modifiye nişasta + E1422 tek kart '+ids('Su, modifiye mısır nişastası (E1422), tuz'));
ok(ids('modifiye mısır nişastası, tuz')[0].split('+').length>1,'kodsuz genel ad korunmalı');
console.log(n+' sodyum denetimi, '+fail+' hata');process.exit(fail?1:0);

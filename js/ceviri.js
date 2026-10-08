/* Çok dil: saf mantık (DOM yok; testler de yükler). Arayüz metinleri i18n/<dil>.json'da, anahtarla: t("gida.ozet.palm", {n:2}).
   Eksik çeviride sıra: seçili dil → İngilizce → Türkçe; hiçbirinde yoksa anahtarın kendisi döner (test/ceviri.js yakalar).
   Değer düz metin ya da çoğul nesnesi {"one":"…","other":"…"} (biçimi Intl.PluralRules seçer; sayı v.n). Yer tutucu {ad}.
   Veri metinleri (gerekçe, not) ayrı: veriMetin(trMetin, anahtar) çeviri yoksa Türkçeyi "çevrilmedi" işaretiyle döndürür. */
var DIL={kod:"tr",yon:"ltr",sira:["tr"],sozluk:{},veri:{},yazi:null,bilgi:{}};
var DIL_KAYNAK="tr",DIL_YEDEK="en";   // kaynak dil (eksiksiz) ve ilk yedek
/* kod: seçili dil; sozluk: {tr:{…}, en:{…}, …}; bilgi: i18n/diller.json kaydı ({ad, yon, yazi}); veri: {kod: {anahtar: metin}} */
function dilKur(kod,sozluk,bilgi,veri){
  var b=(bilgi&&bilgi[kod])||{};
  DIL.kod=kod;DIL.yon=b.yon==="rtl"?"rtl":"ltr";DIL.yazi=b.yazi||null;DIL.bilgi=bilgi||{};
  DIL.sozluk=sozluk||{};DIL.veri=veri||{};
  DIL.sira=[kod,DIL_YEDEK,DIL_KAYNAK].filter(function(x,i,a){return a.indexOf(x)===i});
  DIL_COGUL={};DIL_BICIM={};
}
var DIL_COGUL={},DIL_BICIM={};
function dilCogul(kod,n){
  try{var p=DIL_COGUL[kod]||(DIL_COGUL[kod]=new Intl.PluralRules(kod));return p.select(n)}catch(e){return n===1?"one":"other"}
}
function dilBul(k){
  for(var i=0;i<DIL.sira.length;i++){var d=DIL.sozluk[DIL.sira[i]];if(d&&Object.prototype.hasOwnProperty.call(d,k))return {s:d[k],kod:DIL.sira[i]}}
  return null;
}
function t(k,v){
  var f=dilBul(k);if(!f)return k;
  var s=f.s;
  if(s&&typeof s==="object"){var n=v&&typeof v.n==="number"?v.n:0;s=s[dilCogul(f.kod,n)]!=null?s[dilCogul(f.kod,n)]:s.other}
  if(!v)return s;
  return s.replace(/\{(\w+)\}/g,function(m,a){return v[a]!=null?String(v[a]):m});
}
function tVar(k){return !!dilBul(k)}
/* Sayı: Türkçede "62,5"; binlik ayırıcı yok (eski görünüm). ond: en çok ondalık (varsayılan 2); sabit: ondalık hane sayısı sabit ("2,0") */
function dilSayi(x,ond,sabit){
  ond=ond==null?2:ond;
  var o={maximumFractionDigits:ond,minimumFractionDigits:sabit?ond:0,useGrouping:false},k="n"+ond+(sabit?"s":"");
  try{var f=DIL_BICIM[k]||(DIL_BICIM[k]=new Intl.NumberFormat(DIL.kod,o));return f.format(x)}catch(e){return String(x)}
}
/* Tarih: bicim "gun" (5 Ekim 2026), "gunsaat" (5 Ekim 14:30), "ayyil" (Ekim 2026) */
var DIL_TARIH={gun:{day:"numeric",month:"long",year:"numeric"},gunsaat:{day:"numeric",month:"long",hour:"2-digit",minute:"2-digit"},ayyil:{month:"long",year:"numeric"}};
function dilTarih(ms,bicim){
  var k="t"+bicim;
  try{var f=DIL_BICIM[k]||(DIL_BICIM[k]=new Intl.DateTimeFormat(DIL.kod,DIL_TARIH[bicim]||DIL_TARIH.gun));return f.format(new Date(ms))}catch(e){return new Date(ms).toISOString().slice(0,10)}
}
/* Sıralama ve harf duyarsız karşılaştırma için dilin yerel ayarı */
function dilKarsilastir(a,b){return a.localeCompare(b,DIL.kod)}
/* Veri metni: kaynak Türkçe; seçili dilde çevirisi (DIL.veri[kod][anahtar]) varsa o, yoksa Türkçe + cevrilmedi=true.
   resmi: veride kaynağın kendi İngilizcesi (ör. CLP ifadesi, name_en) varsa {en: "..."} olarak verilir; çeviriden önce gelir. */
function veriMetin(tr,anahtar,resmi){
  var kod=DIL.kod;
  if(kod===DIL_KAYNAK||tr==null||tr==="")return {s:tr,cevrilmedi:false,kod:DIL_KAYNAK};
  if(resmi&&resmi[kod])return {s:resmi[kod],cevrilmedi:false,kod:kod};
  var d=DIL.veri[kod];if(anahtar&&d&&d[anahtar]!=null)return {s:d[anahtar],cevrilmedi:false,kod:kod};
  return {s:tr,cevrilmedi:true,kod:DIL_KAYNAK};
}
/* Dil seçimi: kayıtlı seçim > tarayıcı dilleri (ilk desteklenen; "en-US" → "en") > İngilizce */
function dilSec(kayitli,tarayici,destek){
  if(kayitli&&destek.indexOf(kayitli)>-1)return kayitli;
  for(var i=0;i<(tarayici||[]).length;i++){var k=String(tarayici[i]).toLowerCase(),a=k.split("-")[0];if(destek.indexOf(k)>-1)return k;if(destek.indexOf(a)>-1)return a}
  return destek.indexOf(DIL_YEDEK)>-1?DIL_YEDEK:destek[0];
}

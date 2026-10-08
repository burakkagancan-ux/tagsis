/* Arayüz: dil dosyalarını yükler (i18n/diller.json, i18n/<dil>.json, i18n/veri/<dil>.json), <html lang dir>, dile özel yazı tipi,
   sayfadaki data-i18n işaretli metinler. Saf mantık js/ceviri.js'te. Açılış işleri DIL_HAZIR çözülünce başlar (js/arayuz_sayfa.js). */
function dilGetir(p){return fetch(p).then(function(r){if(!r.ok)throw new Error(p);return r.json()})}
function dilKayitli(){try{return localStorage.getItem("dil")}catch(e){return null}}
var DIL_HAZIR=dilGetir("i18n/diller.json").catch(function(){return {diller:{tr:{ad:"Türkçe",yon:"ltr"}}}}).then(function(b){
  var bilgi=b.diller||{},destek=Object.keys(bilgi);
  var kod=dilSec(dilKayitli(),navigator.languages||[navigator.language],destek);
  var gerek=[DIL_KAYNAK,kod===DIL_KAYNAK?null:DIL_YEDEK,kod].filter(function(x,i,a){return x&&a.indexOf(x)===i});
  var veri=kod===DIL_KAYNAK?Promise.resolve(null):dilGetir("i18n/veri/"+kod+".json").catch(function(){return null});
  return Promise.all(gerek.map(function(k){return dilGetir("i18n/"+k+".json").catch(function(){return {}})}).concat([veri])).then(function(v){
    var s={};gerek.forEach(function(k,i){s[k]=v[i]});
    var vd={};if(v[gerek.length])vd[kod]=v[gerek.length];
    dilKur(kod,s,bilgi,vd);dilUygula(document);
  });
});
/* <html lang dir>, yazı tipi (dil dosyasında tanımlıysa) ve data-i18n / data-i18n-attr ("aria-label:anahtar;placeholder:anahtar").
   lang/dir yalnızca arayüzü çevrilen sayfada değişir (<html data-cevrilen>); ansiklopedi sayfasının arayüzü henüz Türkçe. */
function dilUygula(doc){
  var h=doc.documentElement;if(!h.hasAttribute("data-cevrilen"))return;
  h.lang=DIL.kod;h.dir=DIL.yon;
  if(DIL.yazi){
    if(DIL.yazi.baslik)h.style.setProperty("--hf",DIL.yazi.baslik);
    if(DIL.yazi.govde)h.style.setProperty("--bf",DIL.yazi.govde);
    if(DIL.yazi.css&&!doc.querySelector('link[data-dil-yazi]')){var l=doc.createElement("link");l.rel="stylesheet";l.href=DIL.yazi.css;l.setAttribute("data-dil-yazi","");doc.head.appendChild(l)}
  }
  doc.querySelectorAll("[data-i18n]").forEach(function(e){e.textContent=t(e.getAttribute("data-i18n"))});
  doc.querySelectorAll("[data-i18n-attr]").forEach(function(e){
    e.getAttribute("data-i18n-attr").split(";").forEach(function(p){var kv=p.split(":");if(kv.length===2)e.setAttribute(kv[0].trim(),t(kv[1].trim()))});
  });
}

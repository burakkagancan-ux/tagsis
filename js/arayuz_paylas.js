/* Arayüz: sonuç ekranının üst barı ve paylaşılabilir sonuç kartı (önizleme + yerel paylaşım menüsü). Saf mantık js/paylas.js, ayarlar js/paylas_ayar.js.
   Görsel cihazda çizilir, çevrimdışı çalışır. Kişisel uyarılar yalnızca "Kişisel uyarılarımı ekle" seçilince karta girer. */
var PAY_SRC=null,PAY_LOGO=null;
/* Sonuç ekranı çizildikten sonra çağrılır: üste bar ekler. src: {mode, text} (gıda) | {mode, res, S} (kozmetik) | {mode, A, S} (temizlik) */
function payBar(box,src){
  PAY_SRC=src;
  if(!PAYLAS_AYAR.acik)return;
  var bar=el("div","resbar");bar.appendChild(el("span","rt","Sonuç"));
  var b=el("button","alt pay");b.type="button";b.setAttribute("aria-label","Sonucu görsel olarak paylaş");
  b.innerHTML='<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="18" cy="5" r="2.6"/><circle cx="6" cy="12" r="2.6"/><circle cx="18" cy="19" r="2.6"/><path d="M8.3 10.8l7.4-4.3M8.3 13.2l7.4 4.3"/></svg>';
  b.appendChild(document.createTextNode("Paylaş"));
  b.onclick=function(){payOpen(b)};
  bar.appendChild(b);box.insertBefore(bar,box.firstChild);
}
/* Sonucun üstüne kart eklemek için (öneri kartları bar'ın altına girer) */
function sonucUst(c){var box=$("sonuc"),bar=box.querySelector(".resbar");box.insertBefore(c,bar?bar.nextSibling:box.firstChild)}
/* Profil kartlarından kişisel uyarı satırları: yalnızca kırmızı/sarı olanlar, başlık + ilk satır (satır başlığı tekrar ediyorsa yalnızca satır) */
function payPersonal(cards){
  return cards.filter(function(c){return c.classList.contains("r")||c.classList.contains("y")}).map(function(c){
    var t=c.querySelector(".t"),l=c.querySelector(".ln");t=t?t.textContent:"";l=l?l.textContent:"";
    return {t:l&&l.indexOf(t)===0?l:t+(l?": "+l:""),lvl:c.classList.contains("r")?2:1};
  });
}
function paySource(){
  var s=PAY_SRC,o;if(!s)return null;
  if(s.mode==="gida"){o=payFromFood(s.text,IDX);o.personal=cmpMisfit(summarize(analyze(s.text,IDX),IDX),PROF,IDX).map(function(t){return {t:t,lvl:2}})}   // karşılaştırmadaki "profilinize uymuyor" satırları
  else if(s.mode==="koz"){o=payFromK(s.res,s.S);o.personal=payPersonal(kProfileCards(s.S,s.res))}
  else{o=payFromT(s.A,s.S);o.personal=payPersonal(tProfileCards(s.S,s.A))}
  return o;
}
function payName(){var t=$("metin").value.trim(),e=histLoad().filter(function(x){return x.id===HCUR&&(x.text||"").trim()===t})[0];return payAd(e||null,Date.now())}
function payFonts(){
  if(!document.fonts||!document.fonts.load)return Promise.resolve();
  return Promise.all(['700 76px "Bricolage Grotesque"','400 32px "Figtree"','600 32px "Figtree"'].map(function(f){return document.fonts.load(f,"ğüşıöçĞÜŞİÖÇ").catch(function(){})}));
}
function payLogo(){
  if(PAY_LOGO)return Promise.resolve(PAY_LOGO);
  return new Promise(function(ok){var i=new Image();i.onload=function(){PAY_LOGO=i;ok(i)};i.onerror=function(){ok(null)};i.src=PAYLAS_AYAR.logo});
}
function payOpen(ret){
  var src=paySource();if(!src)return;
  var L=PAYLAS_AYAR.yerlesim[PAYLAS_AYAR.boyut],name=payName(),opt={name:name,kisisel:false},blob=null,M=null;
  var body=el("div","paysheet"),cv=document.createElement("canvas");cv.width=L.w;cv.height=L.h;cv.className="paypre";cv.setAttribute("role","img");
  body.appendChild(cv);
  var chk=null;
  if(src.personal.length){
    var lb=el("label","pc paychk");chk=document.createElement("input");chk.type="checkbox";chk.checked=false;
    lb.appendChild(chk);lb.appendChild(document.createTextNode(" Kişisel uyarılarımı ekle"));body.appendChild(lb);
    body.appendChild(el("div","how","Kapalıyken Hassasiyetlerim'deki seçimlerinizle ilgili hiçbir bilgi karta girmez."));
    chk.onchange=function(){opt.kisisel=chk.checked;draw()};
  }
  var go=el("button",null,"Paylaş");go.type="button";go.disabled=true;body.appendChild(go);
  var st=el("div","how");body.appendChild(st);
  function draw(){
    M=payModel(src,opt);go.disabled=true;blob=null;
    payDraw(cv.getContext("2d"),M,L,PAYLAS_AYAR,PAY_LOGO);
    cv.setAttribute("aria-label",payText(M));
    // Görsel önceden hazırlanır: Safari paylaşım menüsünü yalnızca dokunuşun içinde açar
    cv.toBlob(function(b){blob=b;go.disabled=!b},"image/png");
  }
  go.onclick=function(){
    if(!blob)return;
    var text=payText(M),file=null;
    try{file=new File([blob],"icerik-ozeti.png",{type:"image/png"})}catch(e){}
    if(file&&navigator.canShare&&navigator.share&&navigator.canShare({files:[file]})){
      navigator.share({files:[file],text:text,title:M.name}).then(function(){payCount("s");st.textContent="Paylaşıldı."},function(e){if(!e||e.name!=="AbortError")payFallback(blob,text,st)});
    }else payFallback(blob,text,st);
  };
  openSheet("Sonucu paylaş",null,body,ret);
  st.textContent="Kart hazırlanıyor…";
  Promise.all([payFonts(),payLogo()]).then(function(){draw();st.textContent=""});
}
/* Paylaşım menüsü yoksa (çoğu bilgisayar tarayıcısı): görsel indirilir, metin panoya kopyalanır */
function payFallback(blob,text,st){
  var a=document.createElement("a"),u=URL.createObjectURL(blob);a.href=u;a.download="icerik-ozeti.png";document.body.appendChild(a);a.click();a.remove();
  setTimeout(function(){URL.revokeObjectURL(u)},4000);
  var msg="Görsel indirildi.";
  try{if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(text).then(function(){st.textContent=msg+" Paylaşım metni panoya kopyalandı."},function(){})}}catch(e){}
  st.textContent=msg;payCount("d");
}
/* Anonim paylaşım sayacı: gövdesiz istek; ürün, metin ya da kişisel bilgi gönderilmez. t: s (paylaşım menüsü) | d (indirme) */
function payCount(t){
  if(!PAYLAS_AYAR.sayac||!OCR_URL)return;
  var u=OCR_URL.replace(/\/$/,"")+PAYLAS_AYAR.sayac+"?t="+t;
  try{if(navigator.sendBeacon&&navigator.sendBeacon(u))return}catch(e){}
  try{fetch(u,{method:"POST",mode:"no-cors",keepalive:true}).catch(function(){})}catch(e){}
}

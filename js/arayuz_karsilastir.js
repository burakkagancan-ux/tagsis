/* Arayüz: aynı türden (gıda, kozmetik ya da temizlik) iki ürünü karşılaştırma ve tarama geçmişi (localStorage "taramalar"). Saf mantık js/karsilastir.js, ayarlar js/karsilastir_ayar.js. */
var HCUR=null,HSCAN=true,HOCR=false,CMP_IDS=null;   // HCUR: ekrandaki taramanın kaydı; HSCAN: sonraki analiz yeni kayıt açar; HOCR: metin fotoğraftan/örnekten geldi
// Mod değişince kutudaki metin yeni modda yeniden analiz edilir. HMOD: "gor" sekmeyle geçiş (geçmişe yazılmaz, tarama kendi türünde kalır),
// "tasi" öneri kartıyla geçiş ("Kozmetik olarak analiz et": ekrandaki tarama yeni türe taşınır). Kullanıcı metni değiştirince ya da yeni tarama gelince sıfırlanır.
var HMOD=null;
function histLoad(){try{var a=JSON.parse(localStorage.getItem("taramalar")||"[]");return Array.isArray(a)?a:[]}catch(e){return[]}}
function histStore(a){try{localStorage.setItem("taramalar",JSON.stringify(a))}catch(e){}}
/* Kayıtlı ürünler de karşılaştırılabilir: kimlik geçmişte yoksa kayıtlarda aranır (js/arayuz_kayit.js) */
function histGet(id){return histLoad().filter(function(x){return x.id===id})[0]||(typeof kayitGet==="function"?kayitGet(id):null)}
function histRename(id,name){var a=histLoad();a.forEach(function(x){if(x.id===id)x.name=name});histStore(a);
  if(typeof kayitLoad==="function"){var k=kayitLoad();if(k.some(function(x){return x.id===id})){k.forEach(function(x){if(x.id===id)x.name=name});kayitStore(k)}}}
/* Analizden sonra çağrılır (mode: gida/koz/tem; karşılaştırma ekrandaki türün kayıtlarını kullanır, paylaşım kartı adı ve sırayı buradan alır). Fotoğraf/örnek yeni kayıt açar; elle düzeltme aynı kaydı günceller. */
function histSave(text,mode){
  if(!KARS_AYAR.acik)return;
  mode=mode||"gida";
  var t=(text||"").trim(),a=histLoad(),scan=HSCAN,hm=HMOD;
  if(!t)return;
  HSCAN=false;HOCR=false;HMOD=null;
  if(!scan&&hm==="gor")return;
  if(!scan&&hm==="tasi"&&HCUR){   // ekrandaki tarama yeni türe taşınır; o türde aynı metin varsa eski kayıt silinir
    var mv=a.filter(function(x){return x.id===HCUR})[0],dup=a.filter(function(x){return x.mode===mode&&x.text===t})[0];
    if(mv&&dup&&dup.id!==mv.id){a=a.filter(function(x){return x.id!==mv.id});HCUR=dup.id;histStore(a);return}
    if(mv){mv.mode=mode;mv.text=t;histStore(a);return}
  }
  var same=a.filter(function(x){return x.mode===mode&&x.text===t})[0],cur=!scan&&HCUR?a.filter(function(x){return x.id===HCUR&&x.mode===mode})[0]:null,e;
  if(same)e=same;
  else if(cur){e=cur;e.text=t}
  else e={id:"h"+Date.now(),t:Date.now(),mode:mode,name:histName(a),text:t};
  a=histAdd(a.filter(function(x){return x.id!==e.id}),e,KARS_AYAR.gecmisBoyut);
  histStore(a);HCUR=e.id;
}
/* Türe göre karşılaştırma özeti; liste yüklenmemişse null */
var KARS_TUR={gida:"gıda",koz:"kozmetik",tem:"temizlik"};
function karsReady(mode){return mode==="koz"?!!KIDX:mode==="tem"?!!TIDX:!!IDX}
function karsProduct(e){
  if(e.mode==="koz")return cmpProductK(e.text,KIDX,PROF,e.name,{ptype:PTYPE});
  if(e.mode==="tem")return cmpProductT(e.text,TIDX,KIDX,PROF,e.name);
  return cmpProduct(e.text,IDX,PROF,e.name);
}
/* Analiz Et'in yanındaki düğme: ekrandaki türün son taramalarından iki ürün seçtirir */
function karsOpen(pre,ret){
  if(!KARS_AYAR.acik)return;
  var mode=MODE||"gida",list=histLoad().filter(function(x){return (x.mode||"gida")===mode});
  if(typeof kayitLoad==="function")kayitLoad().forEach(function(k){   // kayıtlı ürünler de listede; aynı metinli tarama yerine kayıtlı ad görünür
    if(k.mode!==mode)return;var h=list.filter(function(x){return x.text===k.text})[0];
    if(h){list[list.indexOf(h)]=k;if(pre===h.id)pre=k.id}else list.push(k);
  });
  if(list.length<2){ST.textContent="Karşılaştırmak için en az iki "+KARS_TUR[mode]+" ürünü taratmalısınız.";return}
  if(!karsReady(mode)){ST.textContent=KARS_TUR[mode].charAt(0).toUpperCase()+KARS_TUR[mode].slice(1)+" listeleri yükleniyor, biraz sonra yeniden deneyin.";return}
  var sel=pre&&list.some(function(x){return x.id===pre})?[pre]:[],body=el("div","kpick"),btns={};
  var cnt=el("div","how"),go=el("button",null,"Karşılaştır");go.type="button";
  function upd(){
    list.forEach(function(x){btns[x.id].setAttribute("aria-pressed",String(sel.indexOf(x.id)>=0))});
    cnt.textContent=sel.length+"/2 ürün seçildi.";go.disabled=sel.length!==2;
  }
  body.appendChild(el("h3",null,"Son taramalar"));
  list.forEach(function(x){
    var b=el("button","kitem");b.type="button";btns[x.id]=b;
    b.appendChild(el("span","kin",x.name));if(/^k/.test(x.id))b.appendChild(el("span","chip","Kayıtlı"));b.appendChild(el("span","kis",x.text.replace(/\s+/g," ").slice(0,70)));
    b.onclick=function(){var i=sel.indexOf(x.id);if(i>=0)sel.splice(i,1);else{sel.push(x.id);if(sel.length>2)sel.shift()}upd()};
    body.appendChild(b);
  });
  body.appendChild(cnt);
  go.onclick=function(){if(sel.length!==2)return;var p=sel.slice();closeSheet();showCompare(p[0],p[1])};
  body.appendChild(go);
  var cl=el("button","alt kclr","Geçmişi temizle");cl.type="button";
  cl.onclick=function(){histStore([]);HCUR=null;closeSheet();ST.textContent="Tarama geçmişi silindi."};
  body.appendChild(cl);
  body.appendChild(el("div","how","Son "+KARS_AYAR.gecmisBoyut+" tarama ve kaydettiğiniz ürünler yalnızca bu cihazda saklanır. “Geçmişi temizle” kayıtlı ürünleri silmez."));
  upd();
  openSheet("Karşılaştır","İki ürün seçin.",body,ret);
}
/* Karşılaştırma ekranı */
var CMP_ICON=["g","u","y","r"];
function cmpIcon(rank){var s=el("span","ic "+CMP_ICON[rank]);s.setAttribute("aria-hidden","true");return s}
function showCompare(ida,idb){
  var ea=histGet(ida),eb=histGet(idb);if(!ea||!eb||ea.mode!==eb.mode||!karsReady(ea.mode||"gida"))return;
  var mode=ea.mode||"gida";
  if((eb.t||0)<(ea.t||0)){var t=ea;ea=eb;eb=t;ida=ea.id;idb=eb.id}   // önce taranan (küçük numaralı) solda; ad değişse de kayıt zamanı aynı kalır
  CMP_IDS=[ida,idb];
  var A=karsProduct(ea),B=karsProduct(eb),D=cmpDecide(A,B,KARS_AYAR),F=cmpDiff(A,B);
  var box=$("kars");box.textContent="";
  var bk=el("button","alt kback","← Sonuca dön");bk.type="button";bk.onclick=closeCompare;box.appendChild(bk);
  box.appendChild(el("h2",null,"Karşılaştırma"+(mode==="gida"?"":" · "+KARS_TUR[mode].charAt(0).toUpperCase()+KARS_TUR[mode].slice(1))));
  // 1) İki sütun: ad + risk özeti
  var hd=el("div","kcols");
  [[A,ea],[B,eb]].forEach(function(pe){
    var P=pe[0],c=el("div","kcol");
    var inp=document.createElement("input");inp.type="text";inp.className="kn";inp.value=P.name;inp.maxLength=40;inp.setAttribute("aria-label","Ürün adı");
    inp.onchange=function(){var v=inp.value.trim();if(v){histRename(pe[1].id,v);showCompare(ida,idb)}else inp.value=P.name};
    c.appendChild(inp);
    var cn=el("div","kcnt");
    [[0,"özel uyarı yok"],[2,"dikkat"],[3,"uyarı"],[1,"doğrulanmadı"]].forEach(function(x){
      if(x[0]===1&&!P.counts[1])return;
      var s=el("span","kc");s.appendChild(cmpIcon(x[0]));s.appendChild(document.createTextNode(P.counts[x[0]]+" "+x[1]));cn.appendChild(s);
    });
    c.appendChild(cn);hd.appendChild(c);
  });
  box.appendChild(hd);
  // 2) Karar kartı
  var dc=el("div","res kdec "+(D.winner?"g":D.kind==="benzer"?"u":"y"));
  dc.appendChild(el("div","t",D.title));if(D.reason)dc.appendChild(el("div","ln",D.reason));
  dc.appendChild(el("div","how",mode==="tem"?"Yalnızca etikette okunan tehlike ifadelerine ve içerik bilgisine dayanır; bu bir onay değildir.":"Yalnızca okunan içerik listesine dayanır; miktar bilinmez ve bu bir onay değildir."));
  box.appendChild(dc);
  // 3) Satır satır
  var tb=el("div","ktab");
  function tr(label,fa,fb){
    tb.appendChild(el("div","kl",label));
    [fa(A),fb?fb(B):fa(B)].forEach(function(v){var c=el("div","kv");if(typeof v==="string")c.textContent=v;else c.appendChild(v);tb.appendChild(c)});
  }
  var lst=function(a){return a.length?a.length+": "+a.join(", "):"Bulunamadı"};
  tr(mode==="tem"?"En riskli ifade ya da madde":"En riskli madde",function(P){
    if(!P.top.length)return "Özel uyarı yok";
    var f=document.createDocumentFragment();f.appendChild(cmpIcon(P.maxRank));f.appendChild(document.createTextNode(P.top.map(function(x){return x.name}).join(", ")));return f});
  tr(mode==="tem"?"Dikkat gerektiren ifade ya da madde":"Dikkat gerektiren madde",function(P){return String(P.yellow)});
  if(mode==="koz"){
    tr("AB'de yasak",function(P){return lst(P.S.red)});
    tr("Başka ülkede yasak",function(P){return lst(P.S.ban)});
    tr("Koku alerjeni",function(P){return lst(P.S.fragrance)});
    tr("Parfüm / aroma",function(P){return P.S.parfum?"Var":"Yazmıyor"});
    tr("Koruyucu",function(P){return lst(P.S.preservative)});
    tr("Formaldehit salıcı",function(P){return lst(P.S.formaldehyde)});
    tr("Endokrin bozucu şüphesi",function(P){return lst(P.S.ed)});
    tr("Vegan",function(P){var no=P.S.nonVeg.concat(P.S.nonVegan);return no.length?"Vegan değil":P.S.veganUnsure.length?"Kaynağı belirsiz bileşen var":"Hayvansal bileşen bulunamadı"});
    tr("Tanınan bileşen",function(P){return P.unknown.total?P.unknown.found+"/"+P.unknown.total:"—"});
  }
  if(mode==="tem"){
    tr("Uyarı sözcüğü",function(P){return P.A.signal==="tehlike"?"TEHLİKE":P.A.signal==="dikkat"?"DİKKAT":"Okunmadı"});
    tr("Ciddi tehlike ifadesi",function(P){return lst(P.S.red)});
    tr("Karıştırma uyarısı",function(P){return P.S.mix?"Var":"Bulunamadı"});
    tr("Solunum",function(P){return P.S.resp.length?P.S.resp.join(", "):P.S.enzyme?"Enzim içerir":"Bulunamadı"});
    tr("Koku alerjeni",function(P){return lst(P.S.fragrance)});
    tr("Koruyucu",function(P){return lst(P.S.pres)});
    tr("Deterjan kapsülü",function(P){return P.A.capsule?"Evet":"Hayır"});
  }
  if(mode==="gida"){
  tr("Alerjenler",function(P){var a=P.allergen;return a.yes.length||a.may.length?(a.yes.length?"İçerir: "+a.yes.join(", "):"")+(a.yes.length&&a.may.length?" · ":"")+(a.may.length?"İçerebilir: "+a.may.join(", "):""):"Bulunamadı"});
  tr("Glüten",function(P){return {var:"İçerir",icerebilir:"İçerebilir",yok:"Bulunamadı"}[P.gluten]});
  tr("Vegan",function(P){return {degil:"Vegan değil",belirsiz:"Kaynağı belirsiz madde var",yok:"Hayvansal içerik bulunamadı"}[P.vegan]});
  tr("Palm yağı",function(P){return P.palm.length?"Var":"Bulunamadı"});
  tr("Şeker kaynağı",function(P){return P.sugar.length?P.sugar.length+": "+P.sugar.join(", "):"Bulunamadı"});
  tr("Üretim yolu",function(P){return uretimMetin(P.uretim)||"Sentetik ya da işlenmiş katkı bulunamadı"});
  tr("Tanınan içerik",function(P){return P.unknown.total?P.unknown.found+"/"+P.unknown.total:"—"});
  }
  box.appendChild(tb);
  // 4) Madde farkları
  box.appendChild(el("h2",null,mode==="tem"?"İfade ve Madde Farkları":"Madde Farkları"));
  var g2=el("div","kcols kdiff");
  g2.appendChild(diffList("Sadece "+A.name,F.onlyA,A));g2.appendChild(diffList("Sadece "+B.name,F.onlyB,B));
  box.appendChild(g2);box.appendChild(diffList("İkisinde de",F.both,A));
  // 5) Kişisel uyarılar
  box.appendChild(el("h2",null,"Kişisel Uyarılar"));
  var g3=el("div","kcols kpers");
  [A,B].forEach(function(P){
    var c=el("div","kcol");c.appendChild(el("h3",null,P.name));
    var cards=mode==="koz"?kProfileCards(P.S,P.res):mode==="tem"?tProfileCards(P.S,P.A):profileCards(P.S);
    if(!cards.length)c.appendChild(el("div","mut","Hassasiyetlerim'de seçim yaparsanız kişisel uyarılar burada görünür."));
    cards.forEach(function(x){c.appendChild(x)});g3.appendChild(c);
  });
  box.appendChild(g3);
  var ch=el("button","alt","Başka ürünle karşılaştır");ch.type="button";
  ch.onclick=function(){karsOpen(ida,ch)};box.appendChild(el("div","row")).appendChild(ch);
  document.body.classList.add("mode-kars");box.hidden=false;window.scrollTo(0,0);bk.focus();
}
function diffList(title,items,P){
  var d=document.createElement("details");d.className="kgrp";d.appendChild(el("summary",null,title+" ("+items.length+")"));
  if(!items.length){d.appendChild(el("div","mut","Yok"));return d}
  items.forEach(function(it){
    var b=el("button","kitem kmad");b.type="button";b.appendChild(cmpIcon(it.rank));b.appendChild(el("span","kin",it.name));
    b.onclick=function(){openItem(it,P,b)};d.appendChild(b);
  });
  return d;
}
/* Maddeye dokununca mevcut alt sayfa: katkı maddesinde sonuç ekranındaki özet, bileşende adı ve notu; kozmetik ve temizlikte sonuç ekranındaki kart */
function openItem(it,P,ret){
  if(P.mode==="koz"){
    var kr=P.res.filter(function(x){return x.found&&x.name===it.key})[0];
    if(kr){openSheet(kr.name,"Bileşen",kCard(kr),ret);return}
  }
  if(P.mode==="tem"){
    var tb=el("div");
    if(it.kind==="hz")tb.appendChild(hzCard(it.x));
    else if(it.kind==="sub"){tb.appendChild(el("div","ln",it.x.s.text));tb.appendChild(srcLinks(it.x.s.sources))}
    else{var fs=it.x.funcs||[];tb.appendChild(el("div","ln",fs.length?"İşlevi (AB kozmetik INCI listesi): "+fs.join(", ")+".":"Bu madde için ayrıca bir not yok."))}
    openSheet(it.name,it.kind==="hz"?"Tehlike ifadesi":"Madde",tb,ret);return;
  }
  var r=P.res.filter(function(x){return !x.neg&&!x.may&&x.ids.slice().sort().join("+")===it.key})[0];
  if(r&&!r.isB){additiveCard(r)._open(ret);return}
  var body=el("div");
  it.ids.forEach(function(id){var x=IDX.byId[id];if(x&&x.note)body.appendChild(el("div","ln",x.note))});
  if(!body.childNodes.length)body.appendChild(el("div","ln","Bu bileşen için ayrıca bir not yok."));
  openSheet(it.name,"Bileşen",body,ret);
}
function closeCompare(){
  document.body.classList.remove("mode-kars");$("kars").hidden=true;CMP_IDS=null;
  var s=$("sonuc");if(s)s.scrollIntoView({block:"start"});
}
$("karsla").onclick=function(){karsOpen(HCUR,$("karsla"))};

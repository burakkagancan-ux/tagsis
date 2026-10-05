/* Arayüz: iki gıda ürününü karşılaştırma ve tarama geçmişi (localStorage "taramalar"). Saf mantık js/karsilastir.js, ayarlar js/karsilastir_ayar.js. */
var HCUR=null,HSCAN=true,HOCR=false,CMP_PEND=null,CMP_IDS=null;   // HCUR: ekrandaki taramanın kaydı; HSCAN: sonraki analiz yeni kayıt açar; HOCR: metin fotoğraftan/örnekten geldi; CMP_PEND: ikinci ürünü bekleyen tarama
function histLoad(){try{var a=JSON.parse(localStorage.getItem("taramalar")||"[]");return Array.isArray(a)?a:[]}catch(e){return[]}}
function histStore(a){try{localStorage.setItem("taramalar",JSON.stringify(a))}catch(e){}}
function histGet(id){return histLoad().filter(function(x){return x.id===id})[0]||null}
function histRename(id,name){var a=histLoad();a.forEach(function(x){if(x.id===id)x.name=name});histStore(a)}
/* Gıda analizinden sonra çağrılır. Fotoğraf/örnek yeni kayıt açar; elle düzeltme aynı kaydı günceller. */
function histSave(text){
  if(!KARS_AYAR.acik)return;
  var t=(text||"").trim(),a=histLoad(),scan=HSCAN,ocr=HOCR;
  if(!t)return;
  HSCAN=false;HOCR=false;
  var same=a.filter(function(x){return x.mode==="gida"&&x.text===t})[0],cur=!scan&&HCUR?a.filter(function(x){return x.id===HCUR})[0]:null,e;
  if(same)e=same;
  else if(cur){e=cur;e.text=t}
  else e={id:"h"+Date.now(),t:Date.now(),mode:"gida",name:histName(new Date()),text:t};
  a=histAdd(a.filter(function(x){return x.id!==e.id}),e,KARS_AYAR.gecmisBoyut);
  histStore(a);HCUR=e.id;
  if(ocr&&CMP_PEND&&CMP_PEND!==e.id&&histGet(CMP_PEND)){var p=CMP_PEND;CMP_PEND=null;showCompare(p,e.id)}
}
/* Sonuç ekranındaki düğme */
function karsButton(){
  if(!KARS_AYAR.acik)return null;
  var d=el("div","row kbtn"),b=el("button","alt","Karşılaştır");b.type="button";
  b.onclick=function(){pickSecond(b)};d.appendChild(b);
  return d;
}
/* İkinci ürünü seçme: yeni tarama ya da son taramalar */
function pickSecond(ret){
  var cur=histGet(HCUR);
  if(!cur){ST.textContent="Bu tarama kaydedilemedi; tarayıcınız yerel kaydı engelliyor olabilir.";return}
  var body=el("div","kpick");
  var lb=el("label","kname");lb.appendChild(el("span",null,"Bu ürünün adı"));
  var inp=document.createElement("input");inp.type="text";inp.value=cur.name;inp.maxLength=40;inp.onchange=function(){var v=inp.value.trim();if(v)histRename(cur.id,v);else inp.value=cur.name};
  lb.appendChild(inp);body.appendChild(lb);
  var nb=el("button",null,"Yeni ürün tara");nb.type="button";
  nb.onclick=function(){
    CMP_PEND=cur.id;HSCAN=true;closeSheet();
    $("metin").value="";$("sonuc").textContent="İkinci ürünün içindekiler yazısının fotoğrafını çekin; okuma bitince karşılaştırma açılır.";
    ST.textContent="Karşılaştırma için ikinci ürün bekleniyor.";$("foto").value="";
    document.querySelector("label.camera").scrollIntoView({block:"center"});
  };
  body.appendChild(nb);
  var others=histLoad().filter(function(x){return x.mode==="gida"&&x.id!==cur.id});
  body.appendChild(el("h3",null,"Son taramalar"));
  if(!others.length)body.appendChild(el("div","mut","Henüz başka tarama yok. Yeni bir ürün tarayın."));
  others.forEach(function(x){
    var b=el("button","kitem");b.type="button";
    b.appendChild(el("span","kin",x.name));b.appendChild(el("span","kis",x.text.replace(/\s+/g," ").slice(0,70)));
    b.onclick=function(){closeSheet();showCompare(cur.id,x.id)};
    body.appendChild(b);
  });
  if(others.length){
    var cl=el("button","alt kclr","Geçmişi temizle");cl.type="button";
    cl.onclick=function(){histStore(histLoad().filter(function(x){return x.id===cur.id}));closeSheet()};
    body.appendChild(cl);
  }
  body.appendChild(el("div","how","Son "+KARS_AYAR.gecmisBoyut+" tarama yalnızca bu cihazda saklanır."));
  openSheet("Karşılaştır","Hangi ürünle karşılaştırılsın?",body,ret);
}
/* Karşılaştırma ekranı */
var CMP_ICON=["g","u","y","r"];
function cmpIcon(rank){var s=el("span","ic "+CMP_ICON[rank]);s.setAttribute("aria-hidden","true");return s}
function showCompare(ida,idb){
  var ea=histGet(ida),eb=histGet(idb);if(!ea||!eb||!IDX)return;
  CMP_IDS=[ida,idb];
  var A=cmpProduct(ea.text,IDX,PROF,ea.name),B=cmpProduct(eb.text,IDX,PROF,eb.name),D=cmpDecide(A,B,KARS_AYAR),F=cmpDiff(A,B);
  var box=$("kars");box.textContent="";
  var bk=el("button","alt kback","← Sonuca dön");bk.type="button";bk.onclick=closeCompare;box.appendChild(bk);
  box.appendChild(el("h2",null,"Karşılaştırma"));
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
  dc.appendChild(el("div","how","Yalnızca okunan içerik listesine dayanır; miktar bilinmez ve bu bir onay değildir."));
  box.appendChild(dc);
  // 3) Satır satır
  var tb=el("div","ktab");
  function tr(label,fa,fb){
    tb.appendChild(el("div","kl",label));
    [fa(A),fb?fb(B):fa(B)].forEach(function(v){var c=el("div","kv");if(typeof v==="string")c.textContent=v;else c.appendChild(v);tb.appendChild(c)});
  }
  tr("En riskli madde",function(P){
    if(!P.top.length)return "Özel uyarı yok";
    var f=document.createDocumentFragment();f.appendChild(cmpIcon(P.maxRank));f.appendChild(document.createTextNode(P.top.map(function(x){return x.name}).join(", ")));return f});
  tr("Dikkat gerektiren madde",function(P){return String(P.yellow)});
  tr("Alerjenler",function(P){var a=P.allergen;return a.yes.length||a.may.length?(a.yes.length?"İçerir: "+a.yes.join(", "):"")+(a.yes.length&&a.may.length?" · ":"")+(a.may.length?"İçerebilir: "+a.may.join(", "):""):"Bulunamadı"});
  tr("Glüten",function(P){return {var:"İçerir",icerebilir:"İçerebilir",yok:"Bulunamadı"}[P.gluten]});
  tr("Vegan",function(P){return {degil:"Vegan değil",belirsiz:"Kaynağı belirsiz madde var",yok:"Hayvansal içerik bulunamadı"}[P.vegan]});
  tr("Palm yağı",function(P){return P.palm.length?"Var":"Bulunamadı"});
  tr("Şeker kaynağı",function(P){return P.sugar.length?P.sugar.length+": "+P.sugar.join(", "):"Bulunamadı"});
  tr("Tanınan içerik",function(P){return P.unknown.total?P.unknown.found+"/"+P.unknown.total:"—"});
  box.appendChild(tb);
  // 4) Madde farkları
  box.appendChild(el("h2",null,"Madde Farkları"));
  var g2=el("div","kcols kdiff");
  g2.appendChild(diffList("Sadece "+A.name,F.onlyA,A));g2.appendChild(diffList("Sadece "+B.name,F.onlyB,B));
  box.appendChild(g2);box.appendChild(diffList("İkisinde de",F.both,A));
  // 5) Kişisel uyarılar
  box.appendChild(el("h2",null,"Kişisel Uyarılar"));
  var g3=el("div","kcols kpers");
  [A,B].forEach(function(P){
    var c=el("div","kcol");c.appendChild(el("h3",null,P.name));
    var cards=profileCards(P.S);
    if(!cards.length)c.appendChild(el("div","mut","Hassasiyetlerim'de seçim yaparsanız kişisel uyarılar burada görünür."));
    cards.forEach(function(x){c.appendChild(x)});g3.appendChild(c);
  });
  box.appendChild(g3);
  var ch=el("button","alt","Başka ürünle karşılaştır");ch.type="button";
  ch.onclick=function(){HCUR=ida;pickSecond(ch)};box.appendChild(el("div","row")).appendChild(ch);
  document.body.classList.add("mode-kars");box.hidden=false;window.scrollTo(0,0);bk.focus();
}
function diffList(title,items,P){
  var d=el("div","kgrp");d.appendChild(el("h3",null,title+" ("+items.length+")"));
  if(!items.length){d.appendChild(el("div","mut","Yok"));return d}
  items.forEach(function(it){
    var b=el("button","kitem kmad");b.type="button";b.appendChild(cmpIcon(it.rank));b.appendChild(el("span","kin",it.name));
    b.onclick=function(){openItem(it,P,b)};d.appendChild(b);
  });
  return d;
}
/* Maddeye dokununca mevcut alt sayfa: katkı maddesinde sonuç ekranındaki özet, bileşende adı ve notu */
function openItem(it,P,ret){
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

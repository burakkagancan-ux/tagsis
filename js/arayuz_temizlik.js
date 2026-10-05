/* Arayüz: temizlik sonuç ekranı. */
/* ---------- Temizlik modu ---------- */
var TDB=null,TIDX=null,TLOAD=null;
function loadT(){
  if(TIDX&&KIDX)return Promise.resolve(TIDX);
  if(TLOAD)return TLOAD;
  setSt("tem","Temizlik listeleri yükleniyor…");
  // Koku alerjenleri ve koruyucular kozmetik INCI listesinden tanınır
  TLOAD=Promise.all([getJson("data/temizlik.json"),loadK()]).then(function(a){
    TDB=a[0];TIDX=buildTIndex(TDB);
    setSt("tem","Temizlik listeleri yüklendi: "+TDB.hazards.length+" tehlike ifadesi, "+TDB.groups.length+" içerik grubu.");
    return TIDX;
  }).catch(function(e){TLOAD=null;setSt("tem","Temizlik listesi yüklenemedi (internet bağlantısını kontrol edin).");throw e});
  return TLOAD;
}
function suggestCardT(){
  var d=el("div","res suggest");d.appendChild(el("div","t","Bu bir temizlik ürünü etiketine benziyor"));
  d.appendChild(el("div","ln","Metinde yüzey aktif madde, tehlike ifadesi gibi deterjan etiketi bilgileri var."));
  var b=el("button",null,"Temizlik ürünü olarak analiz et");b.type="button";b.onclick=function(){setMode("tem",true);window.scrollTo(0,0)};d.appendChild(b);
  return d;
}
var TFUNC_SKIP=["Saç boyası","Deodorant","Saç bakımı","Cilt bakımı","Ağız bakımı","Tırnak bakımı","Keratolitik","Bronzlaştırıcı","Cilt koruyucu","Kepek önleyici"];
var TCLS={red:"r",yellow:"y",info:"u"},TLBL={red:"Ciddi tehlike",yellow:"Uyarı",info:"Bilgi"};
function srcLinks(urls){
  var ps=el("div","how","Kaynak: ");
  (urls||[]).forEach(function(u,i){var a=el("a",null,u.replace(/^https?:\/\/(www\.)?/,"").split("/")[0]);a.href=u;a.target="_blank";a.rel="noopener";if(i)ps.appendChild(document.createTextNode(" · "));ps.appendChild(a)});
  return ps;
}
function infoCard(cls,title,how,body){
  var d=el("div","res "+cls),top=el("div","hd");
  top.appendChild(el("div","t",title));
  var b=el("button","info","i");b.type="button";b.setAttribute("aria-label",title+" hakkında bilgi");b.setAttribute("aria-expanded","false");
  top.appendChild(b);d.appendChild(top);
  if(how)d.appendChild(el("div","how",how));
  var pn=el("div","ipanel");pn.hidden=true;body(pn,d);d.appendChild(pn);
  b.onclick=function(){pn.hidden=!pn.hidden;b.setAttribute("aria-expanded",pn.hidden?"false":"true");b.classList.toggle("on",!pn.hidden)};
  return d;
}
function hzCard(x){
  var h=x.h,M=TIDX.meta,how=x.how.indexOf("benzer")>-1&&x.how.indexOf("kod")<0?"benzer yazım, kontrol edin":x.how.indexOf("kod")>-1&&x.how.indexOf("metin")>-1?"kod ve metinle bulundu":x.how.indexOf("kod")>-1?"kodla bulundu":"metinle bulundu";
  return infoCard(TCLS[h.level],h.code+" · "+h.tr.replace(/^içerir\. /,""),TLBL[h.level]+" · "+(M.group_labels[h.group]||h.group)+" · "+how,function(pn,d){
    if(h.note)d.appendChild(el("div","ln",h.note));
    if(h.code==="EUH208"&&x.names&&x.names.length)d.appendChild(el("div","ln","Adı geçen: "+x.names.join("; ")));
    pn.appendChild(el("div","ln","Bu ifade, üreticinin ürünü resmi tehlike sınıflandırmasına göre etikete yazmak zorunda olduğu bilgidir; uygulamanın kendi yorumu değildir."));
    var eu=h.code.indexOf("EUH")===0;
    pn.appendChild(el("div","how","Mevzuat: SEA Yönetmeliği (RG 11.12.2013, 28848) / AB CLP (EC) 1272/2008. "+(!eu?"Türkçe metin SEA'ya dayalı listeden.":h.needs_review?"Türkçe metin çeviridir; resmi metinle birebir karşılaştırılmadı.":"Türkçe metin, Türkçe güvenlik bilgi formlarındaki ifadeyle karşılaştırıldı.")));
    pn.appendChild(srcLinks([M.sources.clp,!eu?M.sources.h_tr:h.needs_review?M.sources.euh:(TIDX.sds_tr||[])[0]||M.sources.euh]));
  });
}
function tSummaryCard(S,A){
  var d=el("div","res sumbox");d.appendChild(el("div","t","Özet"));
  function row(label,val,cls){var r=el("div","srow");r.appendChild(el("span","sl",label));r.appendChild(el("span","sv"+(cls?" "+cls:""),val));d.appendChild(r)}
  function lst(a){return a.length?a.length+": "+a.join(", "):"Bulunamadı"}
  var n=A.hazards.length;
  row("Tehlike ifadesi",n?(n+" adet: "+S.red.length+" ciddi, "+S.yellow.length+" uyarı"+(S.info.length?", "+S.info.length+" bilgi":"")):"Bulunamadı",S.red.length?"r":S.yellow.length?"y":"");
  row("Uyarı kelimesi",A.signal==="tehlike"?"Tehlike (en yüksek düzey)":A.signal==="dikkat"?"Dikkat":"Okunmadı",A.signal==="tehlike"?"r":A.signal==="dikkat"?"y":"");
  var g=A.groups.filter(function(x){return !x.neg});
  row("İçerik grubu",g.length?g.length+": "+g.map(function(x){return x.g.tr}).join(", "):"Bulunamadı");
  row("Koku alerjeni",lst(S.fragrance));
  row("Koruyucu",lst(S.pres));
  if(S.color.length)row("Renklendirici",lst(S.color));
  row("Parfüm",S.parfum?"Var":"Yazmıyor");
  if(A.inci.length)row("Tanınan madde",A.inci.length+" adet (aşağıda)");
  if(S.mix)row("Karıştırma","Başka ürünlerle karıştırılmamalı","y");
  if(A.capsule)row("Kapsül","Çocuklar için ayrı dikkat","y");
  if(A.prec&&A.prec.length)row("Önlem ifadesi",A.prec.length+" adet (aşağıda)");
  if(!n)d.appendChild(el("div","how","Tehlike ifadesi bulunamaması bir onay değildir; okuma hatası olabilir ya da ifade fotoğrafın dışında kalmış olabilir."));
  if(A.hazards.some(function(x){return x.how.indexOf("benzer")>-1&&x.how.indexOf("kod")<0}))d.appendChild(el("div","how","Benzer yazımla eşleşen ifadeler var; “Okunan Metin” bölümünden kontrol edin."));
  return d;
}
function tProfileCards(S,A){
  var out=[],j=function(a){return a.join(", ")},has=function(c){return A.hazards.some(function(x){return x.code===c})};
  function name(c){var h=TIDX.byCode[c];return c+" ("+h.tr.replace(/^içerir\. /,"").replace(/\.$/,"")+")"}
  if(PROF.koku){
    var e208=has("EUH208")?["Etikette “alerjik reaksiyona yol açabilir” (EUH208) uyarısı var"+(A.euh208&&A.euh208.length?": "+A.euh208.join("; ")+".":".")]:[];
    if(S.fragrance.length)out.push(card("r","Koku alerjeni içerir",[j(S.fragrance)].concat(e208,S.parfum?["Ayrıca parfüm içerir; içindeki koku alerjenleri yalnızca %0,01'i aşarsa adıyla yazılır."]:[])));
    else if(S.parfum||e208.length)out.push(card("y","Parfüm içerir",e208.concat(["Adıyla yazılmış koku alerjeni bulunamadı. Parfüm birçok maddeyi tek ad altında toplar; %0,01'in altındaki alerjenler yazılmaz."])));
    else out.push(card("g","Koku alerjeni bulunamadı",["Bu bir onay değildir. Okuma hatası olabilir; etiketi kendiniz kontrol edin."]));
  }
  if(PROF.astim){
    var rows=[];
    if(S.resp.length)rows.push([S.resp.some(function(c){return /^(H334|EUH071)$/.test(c)})?"r":"y","Solunumla ilgili tehlike ifadesi: "+S.resp.map(name).join("; ")+"."]);
    if(S.enzyme)rows.push(["y","Enzim içerir. Enzimler ham madde olarak solunum yolu hassaslaştırıcıdır; toz ya da sprey biçimde solunmaları önemlidir."]);
    if(["H222","H223","H229","EUH211"].some(has))rows.push(["y","Sprey / aerosol ürün: ürün havaya dağılarak solunabilir."]);
    if(S.parfum)rows.push(["y","Parfüm içerir."]);
    out.push(lifeCard("Astım / solunum: dikkat",rows,"Solunumla ilgili tehlike ifadesi bulunamadı","Bu bir onay değildir. Okuma hatası olabilir; etiketi kendiniz kontrol edin."));
  }
  if(PROF.preg||PROF.baby||PROF.child){
    var r2=[];
    if(S.cmr.length)r2.push(["r","Kanser, genetik hasar ya da üreme ile ilgili tehlike ifadesi: "+S.cmr.map(name).join("; ")+"."]);
    if(S.ed.length)r2.push(["r","Endokrin bozucu tehlike ifadesi: "+S.ed.map(name).join("; ")+"."]);
    if(PROF.baby||PROF.child){
      var sw=S.swallow.concat(S.eye).filter(function(c){return TIDX.byCode[c].level==="red"});
      if(sw.length)r2.push(["r","Yutma ya da göze kaçma halinde ciddi tehlike: "+sw.map(name).join("; ")+". Çocukların erişemeyeceği yerde saklanmalı."]);
      else if(S.swallow.length||S.eye.length)r2.push(["y","Yutma ya da göze kaçma uyarısı: "+S.swallow.concat(S.eye).map(name).join("; ")+"."]);
    }
    if((PROF.baby||PROF.child)&&A.capsule)r2.push(["r","Deterjan kapsülü: küçük çocuklar şekere benzetip ağzına alabilir; yutma ve göze kaçma kazaları bu yüzden özel kurallara bağlandı."]);
    var who=PROF.preg?"Hamilelik / emzirme":PROF.baby?"Bebek":"Çocuk";
    out.push(lifeCard(who+": dikkat",r2,who+" için işaretli tehlike ifadesi bulunamadı","Bu bir onay değildir. Temizlik ürünleri çocukların erişemeyeceği yerde saklanmalı.",r2.length&&TIDX.uzem?TIDX.uzem:null));
  }
  return out;
}
function renderT(A){
  var box=$("sonuc");box.textContent="";
  if(!A.hazards.length&&!A.groups.length&&!A.inci.length&&!A.subs.length){box.textContent="Tehlike ifadesi ya da içerik bilgisi bulunamadı. “Okunan Metin” bölümünü açıp okunan yazıyı kontrol edin; içerik ve uyarılar çoğunlukla arka etikettedir.";return}
  var S=summarizeT(A),M=TIDX.meta;
  if(S.cancer.length){
    var cd=el("div","res prof r"),hd=el("div","hd"),b=el("button","info sm","i");b.type="button";b.setAttribute("aria-label","Kanser tehlikesi hakkında bilgi");
    hd.appendChild(el("div","t","Kanser tehlikesi ifadesi var"));hd.appendChild(b);cd.appendChild(hd);
    cd.appendChild(el("div","ln",S.cancer.map(function(c){return c+" "+TIDX.byCode[c].tr}).join(" ")));
    var ipan=el("div","ipanel");ipan.hidden=true;
    ipan.appendChild(el("div","how","Üreticinin etikete yazmak zorunda olduğu resmi tehlike sınıfıdır (CLP). Eldiven kullanın, buharını solumayın, çocuklardan uzak tutun."));
    cd.appendChild(ipan);b.onclick=function(){ipan.hidden=!ipan.hidden;b.setAttribute("aria-expanded",ipan.hidden?"false":"true");b.classList.toggle("on",!ipan.hidden)};
    box.appendChild(cd);
  }
  tProfileCards(S,A).forEach(function(c){box.appendChild(c)});
  box.appendChild(tSummaryCard(S,A));
  if(S.mix){
    box.appendChild(el("h2",null,"Karıştırma"));
    var R=TIDX.mix;
    box.appendChild(infoCard("y",R.title,null,function(pn,d){
      var p=el("div","ln");p.appendChild(el("b",null,"Bu üründe: "));p.appendChild(document.createTextNode(S.mixWhy.join(", ")));d.appendChild(p);
      pn.appendChild(el("div","ln",R.text));pn.appendChild(srcLinks(R.sources));
    }));
  }
  if(A.capsule&&TIDX.cap){
    var C=TIDX.cap.d;
    box.appendChild(el("h2",null,"Çocuk Güvenliği"));
    box.appendChild(infoCard("y",C.title,null,function(pn){pn.appendChild(el("div","ln",C.text));pn.appendChild(srcLinks(C.sources))}));
  }
  if(A.hazards.length){
    box.appendChild(el("h2",null,"Tehlike İfadeleri"));
    A.hazards.slice().sort(function(a,b){return TRANK[b.h.level]-TRANK[a.h.level]}).forEach(function(x){box.appendChild(hzCard(x))});
  }
  if(A.prec&&A.prec.length){
    box.appendChild(el("h2",null,"Önlem İfadeleri"));
    var P=A.prec.slice().sort(function(a,b){return (b.p.aid?1:0)-(a.p.aid?1:0)});
    var pu=el("ul","klist");
    P.forEach(function(x){var li=el("li");li.appendChild(el("b",null,x.code+" "));li.appendChild(document.createTextNode(x.p.tr));if(x.p.aid)li.appendChild(el("span","chip","İlk yardım"));if(x.how.indexOf("benzer")>-1&&x.how.indexOf("kod")<0)li.appendChild(el("span","fn"," · benzer yazım, kontrol edin"));pu.appendChild(li)});
    box.appendChild(pu);
    if(P.some(function(x){return x.p.aid})&&TIDX.uzem)box.appendChild(el("div","ln",TIDX.uzem));
    if(P.some(function(x){return x.p.needs_review}))box.appendChild(el("div","how","Bazı önlem ifadelerinin Türkçesi resmi metinle birebir karşılaştırılmadı; etiketteki yazı esastır."));
  }
  var G=A.groups.slice();
  if(G.length){
    var ib=secBox(box,"İçerik",G.length);
    var ol=el("ul","klist");
    G.forEach(function(x){
      var li=el("li");li.appendChild(el("b",null,x.g.tr));
      if(x.neg)li.appendChild(el("span","fn"," · içermez (etiket beyanı)"));
      else if(x.band)li.appendChild(el("span","chip",M.bands[x.band]));
      li.appendChild(el("div","fn",x.g.about));ol.appendChild(li);
    });
    ib.appendChild(ol);
    ib.appendChild(el("div","how it","Yüzde bantları ağırlıkçadır ve yalnızca %0,2'yi aşan gruplar için yazılır. Enzim, dezenfektan, optik parlatıcı ve parfüm her oranda yazılır. Ürünün tam içerik listesi üreticinin internet sitesinde yayımlanır."));
  }
  var notes=A.subs.filter(function(x){return !x.s.mix});
  var named=A.inci.filter(function(x){return !TIDX.subByInci[x.name]}).sort(function(a,b){return (b.fragrance||b.pres?1:0)-(a.fragrance||a.pres?1:0)});
  if(notes.length||named.length){
    box.appendChild(el("h2",null,"Adı Yazılan Maddeler"));
    if(named.length)box.appendChild(el("div","how it","İşlevler AB kozmetik INCI listesinden (CosIng) alınmıştır; kozmetikteki sınırlar ve yasaklar temizlik ürünleri için geçerli değildir."));
    notes.forEach(function(x){var s=x.s;box.appendChild(infoCard(TCLS[s.level],s.inci.length>1?"Enzim: "+s.inci.join(", ").toLowerCase():s.inci[0],TLBL[s.level]+" · "+(s.kind==="koruyucu"?"Koruyucu":s.kind==="enzim"?"Enzim":s.kind),function(pn){pn.appendChild(el("div","ln",s.text));pn.appendChild(srcLinks(s.sources))}))});
    if(named.length){
      var ul=el("ul","klist");
      named.forEach(function(x){
        var li=el("li");li.appendChild(el("b",null,x.name));
        var fs=x.funcs.filter(function(f){return TFUNC_SKIP.indexOf(f)<0});   // kozmetiğe özgü işlevler temizlikte gösterilmez
        if(fs.length)li.appendChild(el("span","fn"," · "+fs.join(", ")));
        if(x.how==="benzer")li.appendChild(el("span","fn"," · okunan: “"+x.raw+"”"));
        else if(norm(x.raw)!==norm(x.name))li.appendChild(el("span","fn"," · etikette: “"+x.raw+"”"));
        if(x.fragrance)li.appendChild(el("span","chip","Koku alerjeni"));if(x.pres)li.appendChild(el("span","chip","Koruyucu"));if(x.color)li.appendChild(el("span","chip","Renklendirici"));
        ul.appendChild(li);
      });
      box.appendChild(ul);
    }
  }
  box.appendChild(el("div","how it","Sonuçlar yalnızca okunan metne dayanır ve tıbbi tavsiye değildir. Piktogramlar fotoğraftan tanınmaz; etiketteki işaretlere ayrıca bakın. Veri: AB CLP / SEA Yönetmeliği zararlılık ifadeleri, AB 648/2004 ve Deterjanlar Hakkında Yönetmelik içerik kuralları, Sağlık Bakanlığı Sağlıklı Temizlik Rehberi; koku alerjenleri ve koruyucular AB kozmetik INCI listesinden tanınır."));
}

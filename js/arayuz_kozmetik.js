/* Arayüz: kozmetik sonuç ekranı. */
/* ---------- Kozmetik modu ---------- */
var MODE="gida",PTYPE="",KDB=null,KINCI=null,KIDX=null,KLOAD=null;
try{var tu=localStorage.getItem("tur");MODE=tu==="koz"||tu==="tem"?tu:"gida";PTYPE=localStorage.getItem("ktip")||""}catch(e){}
function loadK(){
  if(KIDX)return Promise.resolve(KIDX);
  if(KLOAD)return KLOAD;
  setSt("koz","Kozmetik listeleri yükleniyor…");
  KLOAD=Promise.all([getJson("data/kozmetik.json"),getJson("data/kozmetik_inci.json").catch(function(){return null})]).then(function(a){
    KDB=a[0];KINCI=a[1];KIDX=buildKIndex(KDB,KINCI);
    setSt("koz","Kozmetik listeleri yüklendi: "+KDB.entries.length+" düzenlenmiş madde"+(KINCI?", "+KINCI.items.length+" INCI adı.":". INCI ad listesi yüklenemedi; yalnızca düzenlenmiş maddeler tanınır."));
    return KIDX;
  }).catch(function(e){KLOAD=null;setSt("koz","Kozmetik listesi yüklenemedi (internet bağlantısını kontrol edin).");throw e});
  return KLOAD;
}
function setMode(m,save){
  MODE=m;
  ["gida","koz","tem"].forEach(function(x){$("m-"+x).setAttribute("aria-checked",String(m===x))});
  $("ptype").hidden=m!=="koz";
  $("camtxt").textContent=m==="koz"?"Ürünün “Ingredients / İçindekiler” listesinin fotoğrafını çekin.":m==="tem"?"Ürünün arka etiketindeki içerik ve uyarı yazılarının fotoğrafını çekin.":"Ürünün “İçindekiler” yazısının fotoğrafını çekin.";
  if(save)try{localStorage.setItem("tur",m)}catch(e){}
  ST.textContent=STMSG[m]||(m==="koz"?"Kozmetik listeleri yükleniyor…":m==="tem"?"Temizlik listeleri yükleniyor…":"Gıda listeleri yükleniyor…");
  if(m==="koz")loadK().then(function(){if($("metin").value.trim())run()},function(){});
  else if(m==="tem")loadT().then(function(){if($("metin").value.trim())run()},function(){});
  else if($("metin").value.trim())run();
}
$("m-gida").onclick=function(){setMode("gida",true)};
$("m-koz").onclick=function(){setMode("koz",true)};
$("m-tem").onclick=function(){setMode("tem",true)};
document.querySelectorAll("#ptype button").forEach(function(b){
  b.onclick=function(){
    PTYPE=PTYPE===b.getAttribute("data-p")?"":b.getAttribute("data-p");
    document.querySelectorAll("#ptype button").forEach(function(x){x.setAttribute("aria-pressed",String(x.getAttribute("data-p")===PTYPE))});
    try{localStorage.setItem("ktip",PTYPE)}catch(e){}
    if(MODE==="koz"&&$("metin").value.trim())run();
  };
  b.setAttribute("aria-pressed",String(b.getAttribute("data-p")===PTYPE));
});
function suggestCard(){
  var d=el("div","res suggest");d.appendChild(el("div","t","Bu bir kozmetik etiketine benziyor"));
  d.appendChild(el("div","ln","Metinde “Aqua”, “Parfum” gibi kozmetik bileşen adları var. Gıda listeleriyle yapılan analiz yanıltıcı olabilir."));
  var b=el("button",null,"Kozmetik olarak analiz et");b.type="button";b.onclick=function(){setMode("koz",true);window.scrollTo(0,0)};d.appendChild(b);
  return d;
}
var KCLS={red:"r",orange:"o",yellow:"y",info:"g"},KLBL={red:"AB'de yasak",orange:"Uyarı",yellow:"Dikkat",info:"Özel uyarı yok"};
function kChips(r){
  var out=[],seen={},F=KIDX.flags;
  r.reg.forEach(function(e){e.flags.forEach(function(f){if(!seen[f]&&f!=="cmr_ban"){seen[f]=1;out.push(F[f]||f)}})});
  r.iflags.forEach(function(f){if(!seen[f]){seen[f]=1;out.push(F[f]||f)}});
  if(r.nano&&!seen.nano)out.push("Nano biçim");
  (r.k3||[]).forEach(function(w){var L=KIDX.watchLists[w.list],c=L?L.chip:w.list;if(L&&L.kind==="comedo"&&PTYPE==="rinse")return;if(!seen["k3:"+c]){seen["k3:"+c]=1;out.push(c)}});
  return out;
}
/* K3 tarih ifadesi: "2027-01-01" -> "1 Ocak 2027'den itibaren" / "...'den beri"; "2019" -> "listeye giriş: 2019" */
var AYLAR=["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"];
function k3When(w,kind){
  var m=/^(\d{4})-(\d{2})-(\d{2})$/.exec(w.date||"");
  var ym=/^(\d{4})-(\d{2})$/.exec(w.date||"");
  if(ym)return "Tarih: "+AYLAR[+ym[2]-1]+" "+ym[1];
  if(!m)return w.date?"Listeye giriş: "+w.date:"";
  var d=(+m[3])+" "+AYLAR[+m[2]-1]+" "+m[1],today=new Date().toISOString().slice(0,10);
  if(kind!=="ban")return "Tarih: "+d;
  return w.date>today?d+" tarihinden itibaren yasak (yasalaştı, henüz yürürlükte değil).":d+" tarihinden beri yasak.";
}
function kCard(r){
  var d=el("div","res "+KCLS[r.level]),top=el("div","hd");
  top.appendChild(el("div","t",r.name));
  var b=el("button","info","i");b.type="button";b.setAttribute("aria-label",r.name+" hakkında bilgi");b.setAttribute("aria-expanded","false");
  top.appendChild(b);d.appendChild(top);
  d.appendChild(el("div","how",KLBL[r.level]+" · "+(r.how==="benzer"?"benzer yazım, kontrol edin: “"+r.raw+"”":"isimle bulundu")+(r.may?" · “içerebilir” bölümünde":"")));
  kChips(r).forEach(function(c){d.appendChild(el("span","chip",c))});
  r.notes.forEach(function(n){d.appendChild(el("div","ln",n.indexOf("o:")===0?"Yalnızca "+n.slice(2)+" izinli; başka ürün tipinde görülmesi beklenmez.":n))});
  var pn=el("div","ipanel");pn.hidden=true;
  function line(lbl,txt){if(!txt)return;var p=el("div","ln");p.appendChild(el("b",null,lbl+" "));p.appendChild(document.createTextNode(txt));pn.appendChild(p)}
  line("İşlevi:",r.funcs.join(", "));
  var seen={};
  r.reg.forEach(function(e){
    if(seen[e.id])return;seen[e.id]=1;
    if(r.reg.length>1)pn.appendChild(el("div","ih","AB Ek "+e.annex+(e.ref&&e.ref!=="?"?" · giriş "+e.ref:"")));
    line("Değerlendirme:",e.reason);
    line("Not:",e.note_tr);
    (e.updates||[]).forEach(function(u){line("Değişiklik ("+u.regulation+(u.applies_from?", "+u.applies_from:"")+"):",u.note_tr)});
    var cond=[e.product_type&&("Ürün tipi: "+e.product_type),e.max&&("Üst sınır: "+e.max),e.conditions_en].filter(Boolean).join(" · ");
    if(cond)pn.appendChild(el("div","how","AB koşulu (özgün metin): "+cond));
    pn.appendChild(el("div","how","Kaynak: AB kozmetik yönetmeliği "+(e.regulation||"(EC) 1223/2009")+(e.applies_from?" · uygulama "+e.applies_from:"")));
    var trs=[e.tr].concat((e.updates||[]).map(function(u){return u.tr})).filter(Boolean)[0];   // AB değişikliğinin Türkiye'deki durumu
    if(trs&&KIDX.trText[trs])pn.appendChild(el("div","how",KIDX.trText[trs]));
    if(e.needs_review)pn.appendChild(el("div","how","Bu kayıt henüz resmi metinle satır satır doğrulanmadı."));
  });
  r.iflags.forEach(function(f){line("Değerlendirme:",KIDX.flagReasons[f])});
  if(r.k3&&r.k3.length){
    pn.appendChild(el("div","ih","Diğer listeler"));
    r.k3.forEach(function(w){
      var L=KIDX.watchLists[w.list]||{label:w.list,text:""};
      line(L.label+":",L.text+(w.note_tr?" "+w.note_tr:""));
      var src=el("div","how",[k3When(w,L.kind),w.basis].filter(Boolean).join(" · ")+" · ");
      if(w.source){var a=el("a",null,"kaynak");a.href=w.source;a.target="_blank";a.rel="noopener";src.appendChild(a)}
      pn.appendChild(src);
      if(w.needs_review)pn.appendChild(el("div","how","Bu bilgi henüz resmi metinle satır satır doğrulanmadı."));
    });
  }
  d.appendChild(pn);
  b.onclick=function(){pn.hidden=!pn.hidden;b.setAttribute("aria-expanded",pn.hidden?"false":"true");b.classList.toggle("on",!pn.hidden)};
  return d;
}
function kSummaryCard(S){
  var d=el("div","res sumbox");d.appendChild(el("div","t","Özet"));
  function row(label,val,cls){var r=el("div","srow");r.appendChild(el("span","sl",label));r.appendChild(el("span","sv"+(cls?" "+cls:""),val));d.appendChild(r)}
  function lst(a){return a.length?a.length+": "+a.join(", "):"Bulunamadı"}
  row("Bileşen",S.found+"/"+S.total+" tanındı"+(S.unknown.length?" · "+S.unknown.length+" tanınmadı":""));
  row("AB'de yasak",lst(S.red),S.red.length?"r":"");
  var w=S.orange.concat(S.yellow);
  row("Uyarı / dikkat",lst(w),S.orange.length?"o":S.yellow.length?"y":"");
  row("Koku alerjeni",lst(S.fragrance),"");
  row("Parfüm / aroma",S.parfum?"Var (içeriği ayrıca yazılmaz)":"Yazmıyor");
  row("Koruyucu",lst(S.preservative));
  if(S.formaldehyde.length)row("Formaldehit salıcı",lst(S.formaldehyde),"y");
  if(S.pfas.length)row("PFAS",lst(S.pfas),"o");
  if(S.ban.length)row("Başka ülkede yasak",lst(S.ban),"o");
  if(S.ed.length)row("Endokrin bozucu şüphesi",lst(S.ed),"y");
  if(S.comedo.length&&PTYPE!=="rinse")row("Gözenek tıkayıcı olabilir",lst(S.comedo),"");
  if(S.fuzzy.length)d.appendChild(el("div","how","Benzer yazımla eşleşen bileşenler var; “Okunan Metin” bölümünden kontrol edin."));
  return d;
}
function kProfileCards(S,res){
  var out=[],j=function(a){return a.join(", ")};
  if(PROF.koku){
    if(S.fragrance.length)out.push(card("r","Koku alerjeni içerir",[j(S.fragrance)].concat(S.parfum?["Ayrıca “Parfum” içerir; içindeki maddelerin yalnızca etiketlenmesi zorunlu olanları ayrıca yazılır."]:[])));
    else if(S.parfum)out.push(card("y","Parfüm içerir",["Etiketlenmesi zorunlu koku alerjeni bulunamadı, ancak “Parfum” birçok maddeyi tek ad altında toplar. Eşik altındaki alerjenler yazılmaz."]));
    else out.push(card("g","Koku alerjeni bulunamadı",["Bu bir onay değildir. Okuma hatası olabilir; etiketi kendiniz kontrol edin."]));
  }
  if(PROF.vegan){
    var no=S.nonVeg.concat(S.nonVegan);
    if(no.length)out.push(card("r","Vegan değil",[j(no)].concat(S.veganUnsure.length?["Kaynağı belirsiz: "+j(S.veganUnsure)]:[])));
    else if(S.veganUnsure.length)out.push(card("y","Vegan uygunluğu belirsiz",["Bitkisel, sentetik ya da hayvansal olabilir: "+j(S.veganUnsure)]));
    else out.push(card("g","Hayvansal bileşen bulunamadı",["Bu bir onay değildir; vegan logosu ya da sertifika en güvenilir göstergedir."]));
  }
  if(PROF.veg){
    if(S.nonVeg.length)out.push(card("r","Vejetaryen değil",["Kesim, balık ya da böcek kaynaklı: "+j(S.nonVeg)]));
    else out.push(card("g","Kesim ya da böcek kaynaklı bileşen bulunamadı",["Bu bir onay değildir; etiketi kendiniz kontrol edin."]));
  }
  // Endokrin bozucu şüphesi: hamilelik ve küçük çocuklar için ayrı kart (yalnızca madde bulunursa)
  if((PROF.preg||PROF.baby||PROF.child||PTYPE==="baby")&&(S.ed.length||S.child.length)){
    var el2=[];
    if(S.ed.length)el2.push("Endokrin bozucu şüphesi olan resmi listelerde: "+j(S.ed)+". Çoğu AB'de sınırla izinlidir; ayrıntı ve kaynak için kartlardaki (i) düğmesine bakın.");
    if(S.child.length&&(PROF.baby||PROF.child||PTYPE==="baby"))el2.push("3 yaş altı çocuklara yönelik ürünlerde Danimarka'da yasak: "+j(S.child)+".");
    el2.push(PROF.preg?"Hamilelikte ve emzirirken kullanım için doktorunuza danışın.":"Küçük çocuklarda kullanım için doktorunuza danışın.");
    out.push(card("y","Endokrin bozucu şüphesi",el2));
  }
  if(PROF.preg){
    if(S.vitA.length)out.push(card("y","Hamilelik / emzirme: dikkat",["A vitamini (retinol ya da esterleri): "+j(S.vitA)+". AB'de bu ürünlerde “günlük alımınızı göz önünde bulundurun” uyarısı zorunlu. Hamilelikte kullanım için doktorunuza danışın."]));
    else out.push(card("g","Hamilelik için işaretli madde bulunamadı",["Bu bir onay değildir; hamilelikte kozmetik kullanımı için doktorunuza danışın."]));
  }
  if(PROF.baby||PROF.child||PTYPE==="baby"){
    var rows=[];res.forEach(function(r){var a=null;r.reg.forEach(function(e){if(e.kids_under&&(a===null||e.kids_under<a))a=e.kids_under});if(a)rows.push(r.name+" ("+a+" yaş altı için ürünlerde kısıtlı ya da yasak)")});
    if(rows.length)out.push(card("y","Çocuklarda kısıtlı madde",rows.concat(["Kısıtlamanın ürün tipine göre değiştiği durumlar var; ayrıntı için kartlardaki (i) düğmesine bakın."])));
    else out.push(card("g","Çocuklar için kısıtlı madde bulunamadı",["Bu bir onay değildir; etiketi kendiniz kontrol edin."]));
  }
  return out;
}
/* Gözenek tıkayıcılık (komedojenite) bilgi notu: skor yok, renk yok; ayrıntı (i) düğmesinde. Durulanan üründe gösterilmez. */
function comedoCard(res){
  var L=KIDX.watchLists.komedo||{text:""},hits=[];
  res.forEach(function(r){if(!r.found||r.may)return;(r.k3||[]).forEach(function(w){if(w.list==="komedo")hits.push({r:r,w:w})})});
  var d=el("div","res u"),top=el("div","hd");
  top.appendChild(el("div","t","Gözenek tıkayıcı olabilecek madde"));
  var b=el("button","info","i");b.type="button";b.setAttribute("aria-label","Gözenek tıkayıcılık hakkında bilgi");b.setAttribute("aria-expanded","false");
  top.appendChild(b);d.appendChild(top);
  d.appendChild(el("div","ln",hits.map(function(h){return h.r.name}).filter(function(x,i,a){return a.indexOf(x)===i}).join(", ")));
  d.appendChild(el("div","how","Bilgi notudur; yasak ya da sağlık uyarısı değildir. Ayrıntı için (i) düğmesine basın."));
  var pn=el("div","ipanel");pn.hidden=true;
  pn.appendChild(el("div","ln",L.text));
  hits.forEach(function(h){var p=el("div","ln");p.appendChild(el("b",null,h.r.name+": "));p.appendChild(document.createTextNode(h.w.note_tr||""));pn.appendChild(p)});
  pn.appendChild(el("div","how","Aynı madde başka bir taşıyıcıda ya da düşük oranda test edildiğinde sonuç değişebiliyor. İnsan cildinde bitmiş ürünle yapılan testlerde (Draelos ve DiNardo 2006) bu maddeleri içeren ürünlerin mutlaka gözenek tıkamadığı görüldü. Ürünün kendisinde “non-comedogenic” yazısı olması daha anlamlıdır, ama bu ifadenin yasal bir test zorunluluğu yoktur."));
  var src=el("div","how","Kaynak: Fulton 1989, J Soc Cosmet Chem 40:321–333 · ");
  var a=el("a",null,"makale");a.href="https://library.scconline.org/v040n06/13";a.target="_blank";a.rel="noopener";src.appendChild(a);pn.appendChild(src);
  d.appendChild(pn);
  b.onclick=function(){pn.hidden=!pn.hidden;b.setAttribute("aria-expanded",pn.hidden?"false":"true");b.classList.toggle("on",!pn.hidden)};
  return d;
}
function renderK(res){
  var box=$("sonuc");box.textContent="";
  if(!res.length){box.textContent="Bileşen listesi bulunamadı. “Okunan Metin” bölümünü açıp okunan yazıyı kontrol edin.";return}
  var S=summarizeK(res,KIDX);
  if(S.cancer.length)box.appendChild(card("r","Kanserojen olabilecek madde",[S.cancer.join(", "),el("div","how","AB'de kanserojen, mutajen ya da üreme için toksik (CMR) sınıfında olan ya da kanserojen formaldehit salabilen madde. Ayrıntı aşağıdaki bileşen kartında.")]));
  kProfileCards(S,res).forEach(function(c){box.appendChild(c)});
  box.appendChild(kSummaryCard(S));
  if(S.comedo.length&&PTYPE!=="rinse")box.appendChild(comedoCard(res));
  comboSection(box,findCombos(COMBO,"koz",comboItemsK(res)));
  var W=res.filter(function(r){return r.found&&r.rank>0}).sort(function(a,b){return b.rank-a.rank||a.pos-b.pos});
  if(W.length){box.appendChild(el("h2",null,"Dikkat Gerektiren Bileşenler"));W.forEach(function(r){box.appendChild(kCard(r))})}
  var tb=secBox(box,"Tüm Bileşenler",res.length);
  var ol=el("ol","klist");
  res.forEach(function(r){
    var li=el("li");
    if(!r.found){li.appendChild(document.createTextNode(r.raw+" "));li.appendChild(el("span","fn","(tanınmadı; okuma hatalı ya da kesik olabilir)"));ol.appendChild(li);return}
    var b=el("b",null,r.name);li.appendChild(b);
    if(r.funcs.length)li.appendChild(el("span","fn"," · "+r.funcs.join(", ")));
    if(r.how==="benzer")li.appendChild(el("span","fn"," · okunan: “"+r.raw+"”"));
    else if(norm(r.raw).indexOf(norm(r.name))<0)li.appendChild(el("span","fn"," · etikette: “"+r.raw+"”"));
    if(r.may)li.appendChild(el("span","fn"," · içerebilir"));
    kChips(r).forEach(function(c){li.appendChild(el("span","chip",c))});
    ol.appendChild(li);
  });
  tb.appendChild(ol);
  if(res.extra&&res.extra.length){
    var dx=el("details","gz");dx.appendChild(el("summary",null,"Bileşen listesi dışında kalan metin ("+res.extra.length+")"));
    var ul=el("ul");res.extra.forEach(function(x){ul.appendChild(el("li",null,x))});dx.appendChild(ul);
    dx.appendChild(el("div","how","Kullanım talimatı, adres gibi bölümler analiz edilmez. Burada bir bileşen adı görürseniz “Okunan Metin” bölümünde önüne virgül ekleyin."));
    tb.appendChild(dx);
  }
  if(S.parfum)box.appendChild(el("div","ln nt","“Parfum” tek bir ad altında çok sayıda koku maddesini kapsar. Yalnızca etiketlenmesi zorunlu koku alerjenleri, belirli bir oranı aşınca ayrıca yazılır."));
  box.appendChild(el("div","how it","Sonuçlar yalnızca okunan metne dayanır, miktar bilgisi içermez ve tıbbi tavsiye değildir. Veri: AB kozmetik yönetmeliği ekleri (CosIng); Türkiye'deki Kozmetik Ürünler Yönetmeliği bu eklerle 2023 sonuna kadar uyumludur; sonraki AB değişikliklerinin Türkiye durumu kartlarda yazar. Ek bilgi: AB olası endokrin bozucu öncelik listesi, Kaliforniya ve ASEAN yasakları, gözenek tıkayıcılık testleri (Fulton 1989)."));
}

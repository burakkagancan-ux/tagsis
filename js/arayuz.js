/* Arayüz: ortak yardımcılar, veri yükleme, Hassasiyetlerim, gıda sonuç ekranı, mod anahtarı. */
var OCR_URL="https://inapp-ocr-3a8f.burakkagancan.workers.dev";   // Cloudflare Worker adresi; boşsa telefonda Tesseract kullanılır
var DB=null,BDB=null,ABOUT={},IDX=null,FLAGS={},BRANDS=null,ST=document.getElementById("st"),LAST=[],LASTSUM=null,LASTBR=[];
var CLS=["g","u","y","r"],LBL=["Özel uyarı yok","Durum doğrulanmadı","Dikkat","Uyarı"];
function $(i){return document.getElementById(i)}
function el(tag,cls,txt){var e=document.createElement(tag);if(cls)e.className=cls;if(txt!=null)e.textContent=txt;return e}
function secBox(box,title,n){var d=el("details","sec");d.appendChild(el("summary",null,title+" ("+n+")"));box.appendChild(d);return d}   // varsayılan kapalı açılır bölüm
/* Durum satırı her mod için ayrı tutulur; mod değişince o modun mesajı gösterilir */
var STMSG={gida:"",koz:"",tem:""};
function setSt(mode,msg){STMSG[mode]=msg;if((typeof MODE==="undefined"||!MODE?"gida":MODE)===mode)ST.textContent=msg}
window.onerror=function(m,src,l){ST.textContent="Sayfa hatası: "+m+" (satır "+l+")";};

/* ---------- Veri yükleme ---------- */
var PATHS=["data/e_kodlari.json","e_kodlari.json"];
var COMBO=null;getJson("data/eslesmeler.json").then(function(j){COMBO=j.rules}).catch(function(){COMBO=null});
function getJson(p){return fetch(p,{cache:"no-store"}).then(function(r){if(!r.ok)throw new Error(p+" bulunamadı");return r.json()})}
function loadDb(i){
  if(i>=PATHS.length){var msg="Katkı maddesi listesi bulunamadı. GitHub'da dosyanın adı tam olarak e_kodlari.json olmalı ve data klasöründe durmalı.";setSt("gida",msg);$("sonuc").textContent=msg;return}
  getJson(PATHS[i]).then(function(j){
    DB=j;FLAGS=(j.meta&&j.meta.flags)||{};
    return getJson("data/bilesenler.json").then(function(b){BDB=b},function(){BDB=null});
  }).then(function(){
    IDX=buildIndex(DB,BDB);
    setSt("gida","Gıda listeleri yüklendi: "+DB.ingredients.length+" katkı maddesi"+(BDB?", "+BDB.items.length+" bileşen grubu.":". Bileşen listesi (data/bilesenler.json) bulunamadı; yalnızca E kodları aranacak."));
    buildProfile();
  }).catch(function(){if(!DB)loadDb(i+1)});
}

/* ---------- Profil ---------- */
var PROF={al:[],lactose:false,koku:false,astim:false,preg:false,emziriyorum:false,baby:false,child:false,vegan:false,veg:false,pku:false,pet:false,salt:false,cinsiyet:"",yas:null,boy:null,kilo:null};
try{var sp=JSON.parse(localStorage.getItem("profil")||"null");if(sp&&sp.al)Object.keys(sp).forEach(function(k){PROF[k]=sp[k]})}catch(e){}
var LIFE=[["baby","Bebek (1 yaşından küçük)"],["child","Çocuk"],["preg","Hamileyim"],["emziriyorum","Emziriyorum"],["vegan","Vegan"],["veg","Vejetaryen"],["pet","Evcil hayvanıma vereceğim"]];
var OTHER=[["lactose","Laktoz intoleransı"],["koku","Koku alerjisi (kozmetik, temizlik)"],["astim","Astım / solunum hassasiyeti (temizlik)"],["salt","Tansiyon / tuz kısıtlaması"],["pku","Fenilketonüri (PKU)"]];
function saveProf(){try{localStorage.setItem("profil",JSON.stringify(PROF))}catch(e){}}
function buildProfile(){
  var box=$("profil");box.textContent="";
  if(!BDB){box.appendChild(el("div","mut","Profil filtreleri için bileşen listesi gerekli."));return}
  function cb(label,checked,on){var l=el("label","pc");var i=document.createElement("input");i.type="checkbox";i.checked=checked;i.onchange=function(){on(i.checked);saveProf();updProfSum();if(LAST.length||$("metin").value.trim())run()};l.appendChild(i);l.appendChild(document.createTextNode(" "+label));return l}
  function pbox(t){var d=el("div","pbox");d.appendChild(el("div","pt",t));box.appendChild(d);return d}
  function abc(a){return a.slice().sort(function(x,y){return x[1].localeCompare(y[1],"tr")})}
  var b0=pbox("Kişisel Bilgiler"),g0=el("div","pg pnum");
  var cl=el("label","pn");cl.appendChild(el("span",null,"Cinsiyet"));var cs=document.createElement("select");
  [["","Seçin"],["kadin","Kadın"],["erkek","Erkek"]].forEach(function(o){var op=document.createElement("option");op.value=o[0];op.textContent=o[1];if(PROF.cinsiyet===o[0])op.selected=true;cs.appendChild(op)});
  cs.onchange=function(){PROF.cinsiyet=cs.value;saveProf();updProfSum()};cl.appendChild(cs);g0.appendChild(cl);
  [["yas","Yaş","yıl",0,120],["boy","Boy","cm",80,220],["kilo","Kilo","kg",2,300]].forEach(function(f){
    var l=el("label","pn");l.appendChild(el("span",null,f[1]));var i=document.createElement("input");i.type="text";i.inputMode="decimal";i.autocomplete="off";
    if(PROF[f[0]]!=null)i.value=String(PROF[f[0]]).replace(".",",");
    i.onchange=function(){var v=parseFloat(String(i.value).replace(",","."));if(isNaN(v)||v<f[3]||v>f[4]){PROF[f[0]]=null;i.value=""}else{PROF[f[0]]=f[0]==="yas"?Math.floor(v):v;i.value=String(PROF[f[0]]).replace(".",",")}saveProf();updProfSum();updBmi();if(LAST.length||$("metin").value.trim())run()};
    l.appendChild(i);l.appendChild(el("span","mut",f[2]));g0.appendChild(l)});
  b0.appendChild(g0);
  var bmiRow=el("div","bmi");b0.appendChild(bmiRow);
  function updBmi(){
    bmiRow.textContent="";
    var lab=el("span",null,"Beden kitle indeksi (BKİ): ");bmiRow.appendChild(lab);
    if(PROF.boy&&PROF.kilo){
      var v=PROF.kilo/Math.pow(PROF.boy/100,2),c=v<18.5?["#3B7DD8","Zayıf"]:v<25?["#2E8B57","Normal"]:v<30?["#D98E04","Fazla kilolu"]:["#C2410C","Obez"];
      var dot=el("span","bmidot");dot.style.background=c[0];bmiRow.appendChild(dot);
      var val=el("b",null,sayi(Math.round(v*10)/10)+" · "+c[1]);val.style.color=c[0];bmiRow.appendChild(val);
    }else bmiRow.appendChild(el("span","mut","boy ve kilo girin"));
    var bb=el("button","info sm","i");bb.type="button";bb.setAttribute("aria-label","BKİ nedir");
    bb.onclick=function(){alert("Beden kitle indeksi (BKİ) = kilo (kg) / boy (m)²\nZayıf: 18,5 altı · Normal: 18,5–24,9 · Fazla kilolu: 25–29,9 · Obez: 30 ve üzeri\nYetişkinler içindir; çocuk, hamile ve sporcularda yanıltabilir.\nKaynak: Dünya Sağlık Örgütü (WHO)")};
    bmiRow.appendChild(bb);
  }
  updBmi();
  b0.appendChild(el("div","mut","Kilonuz, katkı maddesi kartlarındaki günlük sınırı size göre hesaplamak için kullanılır."));
  var b1=pbox("Alerjenler"),g=el("div","pg");
  abc(BDB.meta.allergens).forEach(function(a){g.appendChild(cb(a[1],PROF.al.indexOf(a[0])>-1,function(v){PROF.al=PROF.al.filter(function(x){return x!==a[0]});if(v)PROF.al.push(a[0])}))});
  b1.appendChild(g);
  var b2=pbox("Yaşam Evresi"),g2=el("div","pg");
  abc(LIFE).forEach(function(x){g2.appendChild(cb(x[1],!!PROF[x[0]],function(v){PROF[x[0]]=v}))});
  b2.appendChild(g2);
  var b3=pbox("Diğer"),g3=el("div","pg");
  abc(OTHER).forEach(function(x){g3.appendChild(cb(x[1],!!PROF[x[0]],function(v){PROF[x[0]]=v}))});
  b3.appendChild(g3);
  box.appendChild(el("div","mut","Seçimleriniz yalnızca bu cihazda saklanır."));
  updProfSum();
}
function alName(f){var a=(BDB&&BDB.meta.allergens)||[];for(var i=0;i<a.length;i++)if(a[i][0]===f)return a[i][1];return f}
function updProfSum(){
  var n=(PROF.cinsiyet?1:0)+(PROF.kilo!=null?1:0)+(PROF.yas!=null?1:0)+(PROF.boy!=null?1:0)+PROF.al.length+LIFE.filter(function(x){return PROF[x[0]]}).length+OTHER.filter(function(x){return PROF[x[0]]}).length;
  $("profsum").textContent=n?("Profilim · "+n+" seçim"):"Profilim";
}

/* ---------- Sonuç ekranı ---------- */
function card(cls,title,lines){
  var d=el("div","res prof "+cls);d.appendChild(el("div","t",title));
  (lines||[]).forEach(function(l){if(l)d.appendChild(typeof l==="string"?el("div","ln",l):l)});
  return d;
}
function profileCards(S){
  var out=[],any=PROF.al.length||LIFE.some(function(x){return PROF[x[0]]})||OTHER.some(function(x){return PROF[x[0]]});
  if(!any)return out;
  if(PROF.al.length){
    var yes=[],may=[];
    PROF.al.forEach(function(f){var a=S.allergen[f];if(!a)return;if(a.yes.length)yes.push(alName(f)+": "+a.yes.join(", "));if(a.may.length)may.push(alName(f)+": "+a.may.join(", "))});
    if(yes.length)out.push(card("r","Seçtiğiniz alerjen var",yes.concat(may.length?["Ayrıca içerebilir → "+may.join("; ")]:[])));
    else if(may.length)out.push(card("y","Seçtiğiniz alerjeni içerebilir",may));
    else out.push(card("g","Seçtiğiniz alerjenler metinde bulunamadı",["Bu bir onay değildir. Okuma hatası olabilir; etiketteki koyu yazılmış alerjenleri kendiniz kontrol edin."]));
  }
  if(PROF.lactose){
    var L=S.lactose;
    if(L.yes.length)out.push(card("r","Laktoz içerir",[L.yes.join(", ")].concat(L.low.length?["Düşük laktozlu: "+L.low.join(", ")]:[])));
    else if(L.low.length||L.may.length)out.push(card("y","Laktoz düşük ya da belirsiz",[L.low.length?"Düşük laktozlu: "+L.low.join(", "):"",L.may.length?"İçerebilir / aroma: "+L.may.join(", "):""]));
    else out.push(card("g","Laktoz kaynağı bulunamadı",["Bu bir onay değildir; etiketi kendiniz kontrol edin."]));
  }
  if(PROF.vegan){
    var V=S.vegan;
    if(V.no.length)out.push(card("r","Vegan değil",[V.no.join(", ")].concat(V.unsure.length?["Kaynağı belirsiz: "+V.unsure.join(", ")]:[])));
    else if(V.unsure.length)out.push(card("y","Vegan uygunluğu belirsiz",["Kaynağı bitkisel ya da hayvansal olabilir: "+V.unsure.join(", ")]));
    else out.push(card("g","Hayvansal içerik bulunamadı",["Bu bir onay değildir; vegan logosu ya da sertifika en güvenilir göstergedir."]));
  }
  if(PROF.veg){
    var G=S.veg;
    if(G.no.length||G.insect.length)out.push(card("r","Vejetaryen değil",[G.no.length?G.no.join(", "):"",G.insect.length?"Böcek kaynaklı: "+G.insect.join(", "):""].concat(G.unsure.length?["Kaynağı belirsiz: "+G.unsure.join(", ")]:[])));
    else if(G.unsure.length)out.push(card("y","Vejetaryen uygunluğu belirsiz",["Kaynağı belirsiz: "+G.unsure.join(", ")]));
    else out.push(card("g","Et, balık ve kesim yan ürünü bulunamadı",["Bu bir onay değildir; etiketi kendiniz kontrol edin."]));
  }
  return out.concat(lifeCards(S.life,S.sodium));
}
/* Yaşam evresi, PKU ve evcil hayvan kartları. Satır: [seviye "r"/"y", metin]. Hiçbir zaman "uygun" denmez. */
function lifeCard(title,rows,okTitle,okNote,extra){
  rows=rows.filter(function(r){return r});
  if(!rows.length)return card("g",okTitle,[okNote]);
  var red=rows.some(function(r){return r[0]==="r"});
  return card(red?"r":"y",title,rows.map(function(r){return r[1]}).concat(extra?[extra]:[]));
}
function lifeCards(L,NA){
  var out=[],j=function(a){return a.join(", ")};
  var raw=L.raw.length?["r","Çiğ (pastörize edilmemiş) süt ürünü: "+j(L.raw)+". Listeria gibi bakteriler taşıyabilir."]:null;
  var alc=L.alcohol.length?["r","Alkol: "+j(L.alcohol)+". Pişirmeyle tamamen uçmayabilir."]:null;
  var trace=L.alcoholTrace.length?["y","“Alkolsüz” ürün: hacmen %0,5'e kadar alkol içerebilir."]:null;
  var hyp=L.hyper.length?["y","Renklendirici: "+j(L.hyper)+". Bu boyaları içeren ürünlerde, çocukların aktivitesi ve dikkati üzerinde olumsuz etkisi olabileceği uyarısı zorunludur."]:null;
  if(PROF.preg)out.push(lifeCard("Hamilelik: dikkat",[alc,raw,
    L.caffeine.length?["y","Kafein kaynaği: "+j(L.caffeine)+". EFSA hamilelikte günde en fazla 200 mg öneriyor; miktar için etiketteki kafein bilgisine bakın."]:null,trace],
    "Hamilelik için işaretli madde bulunamadı","Bu bir onay değildir; etiketi kendiniz kontrol edin, beslenmeniz için doktorunuza danışın."));
  if(PROF.emziriyorum)out.push(lifeCard("Emzirme: dikkat",[alc,raw,trace],
    "Emzirme için işaretli madde bulunamadı","Bu bir onay değildir; etiketi kendiniz kontrol edin, beslenmeniz için doktorunuza danışın."));
  if(PROF.baby)out.push(lifeCard("Bebek (1 yaş altı): dikkat",[
    L.honey.length?["r","Bal: 1 yaşından küçük bebeklere verilmez (bebek botulizmi riski)."]:null,alc,
    L.caffeine.length?["r","Kafein kaynağı: "+j(L.caffeine)+"."]:null,raw,
    L.sweet.length?["y","Tatlandırıcı: "+j(L.sweet)+". Bebek ve küçük çocuk gıdalarında tatlandırıcı kullanımına izin verilmez."]:null,hyp,trace],
    "Bebekler için işaretli madde bulunamadı","Bu bir onay değildir; bebeğinizin beslenmesi için doktorunuza danışın."));
  if(PROF.child)out.push(lifeCard("Çocuk: dikkat",[alc,hyp,
    L.caffeine.length?["y","Kafein kaynağı: "+j(L.caffeine)+". Yüksek kafeinli ürünler çocuklara tavsiye edilmez."]:null,
    L.sweet.length?["y","Tatlandırıcı içerir: "+j(L.sweet)+"."]:null,trace],
    "Çocuklar için işaretli madde bulunamadı","Bu bir onay değildir; etiketi kendiniz kontrol edin."));
  if(PROF.pku)out.push(lifeCard("Fenilalanin kaynağı içerir",[L.phe.length?["r","Aspartam (fenilalanin kaynağı): "+j(L.phe)+"."]:null],
    "Aspartam bulunamadı","Bu kontrol yalnızca tatlandırıcıya bakar. Proteinli tüm gıdalar fenilalanin içerir; protein miktarı için besin değeri tablosuna bakın."));
  if(PROF.pet)out.push(lifeCard("Evcil hayvanlar için zehirli madde",[L.pet.length?["r","Köpek ve kediler için zehirli olduğu bilinen: "+j(L.pet)+"."]:null],
    "Bilinen zehirli madde bulunamadı","Bu bir onay değildir. İnsan yiyeceklerini evcil hayvanınıza vermeden önce veterinerinize danışın.",
    "Miktar bilinmez; hayvanınız yediyse veterinerinize başvurun."));
  if(PROF.salt&&NA)out.push(lifeCard("Tuz ve sodyum kaynakları",[
    NA.salt.length?["y","Tuz içerir"+(NA.saltOrd&&NA.saltOrd<=3?": içerik listesinde "+NA.saltOrd+". sırada. Bileşenler çoktan aza doğru yazıldığı için üründe tuz oranı yüksek olabilir.":".")]:null,
    NA.hidden.length?["y","Adında “tuz” geçmeyen sodyum kaynakları: "+j(NA.hidden)+". Katkı maddelerinden gelen sodyum çoğunlukla tuzdan azdır."]:null],
    "Tuz ya da sodyum kaynağı bulunamadı","Bu bir onay değildir. Peynir, et, ekmek gibi bileşenler kendiliğinden tuz içerebilir; miktar için besin değerleri tablosuna bakın.",
    "Miktarı etiketteki besin değerleri tablosunun “Tuz” satırı gösterir: 100 g'da 1,5 g'ın üzeri yüksek, 0,3 g'ın altı düşük sayılır (İngiltere NHS ölçütü)."));
  return out;
}
function summaryCard(S,res){
  var d=el("div","res sumbox");d.appendChild(el("div","t","Özet"));
  function row(label,val,cls){var r=el("div","srow");r.appendChild(el("span","sl",label));var v=el("span","sv"+(cls?" "+cls:""));if(typeof val==="string")v.textContent=val;else v.appendChild(val);r.appendChild(v);d.appendChild(r)}
  var E=res.filter(function(r){return !r.isB&&!r.neg}),cnt=[0,0,0,0];E.forEach(function(r){cnt[r.rank]++});
  row("Katkı maddesi",E.length?(E.length+" adet: "+cnt[3]+" uyarı, "+cnt[2]+" dikkat"+(cnt[1]?", "+cnt[1]+" doğrulanmamış":"")):"Bulunamadı",cnt[3]?"r":cnt[2]?"y":"");
  if(S.sugar.length){
    var f=document.createDocumentFragment();
    f.appendChild(document.createTextNode(S.sugar.length+" kaynak: "));
    S.sugar.forEach(function(s,i){if(i)f.appendChild(document.createTextNode(", "));f.appendChild(document.createTextNode(s.name));if(s.hidden){f.appendChild(document.createTextNode(" "));f.appendChild(el("span","chip","gizli"))}});
    row("Şeker",f,S.sugar.some(function(s){return s.hidden})?"y":"");
  }else row("Şeker","Kaynak bulunamadı");
  row("Palm yağı",S.palm.length?"Var ("+S.palm.join(", ")+")":"Bulunamadı",S.palm.length?"y":"");
  var u=Object.keys(S.upf).map(capFirst);
  row("Ultra işlenmiş gıda",u.length?(u.length+" işaret: "+u.join(", ")):"İşaret bulunamadı",u.length>=2?"y":"");
  var ay=[],am=[];Object.keys(S.allergen).forEach(function(f){var a=S.allergen[f];if(a.yes.length)ay.push(alName(f));else if(a.may.length)am.push(alName(f))});
  row("Alerjenler",ay.length||am.length?((ay.length?"İçerir: "+ay.join(", "):"")+(ay.length&&am.length?" · ":"")+(am.length?"İçerebilir: "+am.join(", "):"")):"Bulunamadı");
  if(S.claims.length)row("Etiket beyanı",S.claims.join(", "));
  if(S.cancer.length)row("Kanserojen olabilir",S.cancer.map(function(c){return typeof c==="string"?c:c.name}).join(", "),"r");
  if(u.length)d.appendChild(el("div","how upfnote","Ultra işlenmiş gıda işaretleri NOVA sınıflamasına göredir; bir puan değil, bu tür ürünlerde kullanılan madde gruplarının listesidir."));
  return d;
}
function brandCard(br){
  var d=el("div","res u");d.appendChild(el("div","t","Bakanlık listesinde benzer marka adı"));
  br.forEach(function(b){
    var r=el("div","ln");r.appendChild(document.createTextNode("“"+b.label+"” adı listede "+b.n+" kayıtta geçiyor. "));
    var a=el("a",null,"Listede gör");a.href="index.html?q="+encodeURIComponent(b.q);r.appendChild(a);d.appendChild(r);
  });
  d.appendChild(el("div","how","Liste ürün ve parti bazındadır. Aynı adın geçmesi bu ürünün listede olduğu anlamına gelmez; ürün adını ve parti numarasını karşılaştırın."));
  return d;
}
// Günlük kabul edilebilir alım (ADI) satırı; değer mg/kg vücut ağırlığı (per=hafta: haftalık)
function sayi(x){x=Math.round(x*100)/100;return String(x).replace(".",",")}
function yuv(x){return x>=100?Math.round(x):x>=10?Math.round(x*10)/10:x}
function mgTxt(x){return x>=1000?sayi(yuv(x/1000))+" g":sayi(yuv(x))+" mg"}
function adiBlock(a,pre){
  var w=a.per==="hafta",kg=PROF.kilo,box=el("div","adi"),row=el("div","adr"),t;
  var lb=(w?"Haftalık sınır":"Günlük sınır")+(a.st==="set"&&kg?"ınız":"");
  if(a.st==="set")t=kg?"yaklaşık "+mgTxt(a.v*kg)+" ("+sayi(kg)+" kg için"+(a.as?", "+a.as:"")+")":"kilo başına "+sayi(a.v)+" mg"+(a.as?" ("+a.as+")":"")+". Kilonuzu Hassasiyetlerim'e girerseniz size göre hesaplanır.";
  else t=a.st==="ns"?"sayısal sınır belirlenmedi.":"geçerli bir sınır yok.";
  var tx=el("div","ln");tx.appendChild(el("b",null,(pre?pre+" · ":"")+lb+": "));tx.appendChild(document.createTextNode(t));row.appendChild(tx);
  var bt=el("button","info sm","i");bt.type="button";bt.setAttribute("aria-label",lb+" kaynağı");bt.setAttribute("aria-expanded","false");row.appendChild(bt);
  box.appendChild(row);
  var pn=el("div","ipanel");pn.hidden=true;
  var p=el("div","ln");
  if(a.st==="set")p.appendChild(document.createTextNode((w?"Haftalık kabul edilebilir alım (TWI): ":"Kabul edilebilir günlük alım (ADI): ")+sayi(a.v)+" mg/kg vücut ağırlığı"+(a.as?" ("+a.as+")":"")+", "+a.src+"."+(kg?" Hesap: "+sayi(a.v)+" mg × "+sayi(kg)+" kg = "+mgTxt(a.v*kg)+".":"")));
  else p.appendChild(document.createTextNode(a.st==="ns"?a.src+": mevcut kullanımda sayısal sınır gerekli görülmedi.":a.src+"."));
  if(a.note)p.appendChild(document.createTextNode(" "+a.note));
  pn.appendChild(p);
  var ps=el("div","how");
  if(a.url){ps.appendChild(document.createTextNode("Kaynak: "));var l=el("a",null,a.url.replace(/^https?:\/\/(www\.)?/,"").split("/")[0]);l.href=a.url;l.target="_blank";l.rel="noopener";ps.appendChild(l)}
  if(!a.ok)ps.appendChild(document.createTextNode((a.url?" · ":"")+"Bu değer henüz kaynakla doğrulanmadı."));
  if(ps.childNodes.length)pn.appendChild(ps);
  if(a.st==="set"){
    if(PROF.yas===0)pn.appendChild(el("div","how","EFSA'ya göre bu sınırlar 16 haftadan küçük bebekler için geçerli değildir; bebeğinizin beslenmesi için hekiminize danışın."));
    pn.appendChild(el("div","how","Sınır, bir ömür boyunca her gün alınsa bile sağlık riski beklenmeyen miktardır ve gün içinde bütün kaynaklardan alınan toplam içindir. Etikette miktar yazmadığı için bu üründen ne kadar alındığı hesaplanamaz."));
  }
  box.appendChild(pn);
  bt.onclick=function(){pn.hidden=!pn.hidden;bt.setAttribute("aria-expanded",pn.hidden?"false":"true");bt.classList.toggle("on",!pn.hidden)};
  return box;
}
function additiveCard(r){
  var d=el("div","res "+CLS[r.rank]);
  var items=r.ids.map(function(id){return IDX.byId[id]});
  var it=items.slice().sort(function(a,b){return RANK[b.risk_level]-RANK[a.risk_level]})[0];
  var top=el("div","hd");
  var grp=items.every(function(i){return i.category===items[0].category})?items[0].category:"Katkı maddesi";
  top.appendChild(el("div","t",items.length===1?(items[0].id+" · "+items[0].primary_name):("Olası: "+items.map(function(i){return i.id}).join(", ")+" · "+grp+" (türü belirtilmemiş)")));
  var b=el("button","info","i");b.type="button";b.setAttribute("aria-label",it.primary_name+" hakkında bilgi");b.setAttribute("aria-expanded","false");
  top.appendChild(b);d.appendChild(top);
  d.appendChild(el("div","how",LBL[r.rank]+" · "+(r.how==="kod"?"E koduyla bulundu"+(r.fixed?" (yazım düzeltildi, kontrol edin)":""):r.how==="isim"?"isimle bulundu":"benzer yazım, kontrol edin: “"+r.text+"”")+(r.may?" · “içerebilir” bölümünde":"")));
  it.flags.forEach(function(f){if((f==="sodium"&&!PROF.salt)||f==="aluminium"||f==="gmo_suspect")return;/* sodyum etiketi yalnızca tuz kısıtlaması seçiliyse */d.appendChild(el("span","chip",FLAGS[f]||f))});
  var seenA={};items.forEach(function(x){if(!x.adi)return;var k=JSON.stringify(x.adi);if(seenA[k])return;seenA[k]=1});
  var nA=Object.keys(seenA).length,doneA={};
  items.forEach(function(x){if(!x.adi)return;var k=JSON.stringify(x.adi);if(doneA[k])return;doneA[k]=1;d.appendChild(adiBlock(x.adi,nA>1||items.length>1&&items.some(function(y){return !y.adi})?x.id:""))});
  var pn=el("div","ipanel");pn.hidden=true;
  var same=items.length>1&&items.every(function(x){return ABOUT[x.id]===ABOUT[items[0].id]&&!x.tgk_note});
  if(same){var p4=el("div","ln");p4.appendChild(el("b",null,"Nedir? "));p4.appendChild(document.createTextNode(ABOUT[items[0].id]||""));pn.appendChild(p4)}
  else items.forEach(function(x){
    var ab=ABOUT[x.id];
    if(items.length>1)pn.appendChild(el("div","ih",x.id+" · "+x.primary_name));
    if(ab){var p1=el("div","ln");p1.appendChild(el("b",null,"Nedir? "));p1.appendChild(document.createTextNode(ab));pn.appendChild(p1)}
    if(items.length===1&&x.tgk_name&&x.tgk_name.toLowerCase()!==x.primary_name.toLowerCase()){var p0=el("div","ln");p0.appendChild(el("b",null,"Yönetmelikteki adı: "));p0.appendChild(document.createTextNode(x.tgk_name));pn.appendChild(p0)}
    if(x.tgk_note){var p3=el("div","ln");p3.appendChild(el("b",null,"Türkiye: "));p3.appendChild(document.createTextNode(x.tgk_note));pn.appendChild(p3)}
  });
  var p2=el("div","ln");p2.appendChild(el("b",null,"Değerlendirme: "));
  p2.appendChild(document.createTextNode(it.verification==="inventory_only"?"Bu uygulamanın uyarı ölçütlerinden (AB yasağı, zorunlu uyarı, IARC sınıflaması vb.) hiçbirine girmiyor.":it.reason));
  pn.appendChild(p2);
  if(it.sources&&it.sources.length){   // doğrulama kaynakları: bağlantı metni alan adı
    var ps=el("div","how","Kaynak: ");
    it.sources.forEach(function(u,i){var a=el("a",null,u.replace(/^https?:\/\/(www\.)?/,"").split("/")[0]);a.href=u;a.target="_blank";a.rel="noopener";if(i)ps.appendChild(document.createTextNode(" · "));ps.appendChild(a)});
    pn.appendChild(ps);
  }
  if(it.needs_review)pn.appendChild(el("div","how",it.sources&&it.verification!=="partially_checked"?"Türkiye'deki izin durumu henüz doğrulanmadı.":it.sources?"Bu değerlendirmenin bir kısmı henüz kaynakla doğrulanmadı.":"Bu değerlendirme henüz kaynakla doğrulanmadı."));
  // Ayrıntı alt sayfada açılır: (i) düğmesi ya da kartın kendisine dokunma; her madde için "Ansiklopedide oku"
  pn.hidden=false;pn.className="";
  items.forEach(function(x){var a=el("a","ans",(items.length>1?x.id+" · ":"")+"Ansiklopedide oku");a.href="ansiklopedi.html?id="+encodeURIComponent(x.id);pn.appendChild(a)});
  var ttl=items.length===1?items[0].id+" · "+items[0].primary_name:"Olası: "+items.map(function(i){return i.id}).join(", ");
  b.removeAttribute("aria-expanded");b.setAttribute("aria-haspopup","dialog");
  b.onclick=function(e){e.stopPropagation();openSheet(ttl,LBL[r.rank],pn,b)};
  d.classList.add("tap");
  d.addEventListener("click",function(e){if(e.target.closest("button,a,.adi"))return;openSheet(ttl,LBL[r.rank],pn,b)});
  return d;
}
/* Alt sayfa: başlık, durum satırı ve içerik; kapatınca odak açan düğmeye döner */
var SHEET_RET=null;
function openSheet(title,how,body,ret){
  $("sheet-t").textContent=title;var sb=$("sheet-b");sb.textContent="";
  if(how)sb.appendChild(el("div","how",how));sb.appendChild(body);
  SHEET_RET=ret||null;$("sheet").hidden=false;document.body.style.overflow="hidden";$("sheet-x").focus();
}
function closeSheet(){if($("sheet").hidden)return;$("sheet").hidden=true;document.body.style.overflow="";if(SHEET_RET)SHEET_RET.focus()}
$("sheet-x").onclick=closeSheet;$("sheet-bg").onclick=closeSheet;
document.addEventListener("keydown",function(e){if(e.key==="Escape")closeSheet()});
function comboCard(c){
  var R=c.rule,d=el("div","res "+(R.level==="yellow"?"y":"g")),top=el("div","hd");
  top.appendChild(el("div","t",R.title));
  var b=el("button","info","i");b.type="button";b.setAttribute("aria-label",R.title+" hakkında bilgi");b.setAttribute("aria-expanded","false");
  top.appendChild(b);d.appendChild(top);
  var p=el("div","ln");p.appendChild(el("b",null,"Bu üründe: "));
  p.appendChild(document.createTextNode(c.hits.map(function(h,i){return (R.type==="cift"?R.groups[i].label+": ":"")+h.join(", ")}).join(" · ")));d.appendChild(p);
  // Ayrıntı (açıklama, kaynak, not) yalnızca (i) düğmesine basınca görünür
  var pn=el("div","ipanel");pn.hidden=true;
  pn.appendChild(el("div","ln",R.text));
  var ps=el("div","how","Kaynak: ");
  (R.sources||[]).forEach(function(u,i){var a=el("a",null,u.replace(/^https?:\/\/(www\.)?/,"").split("/")[0]);a.href=u;a.target="_blank";a.rel="noopener";if(i)ps.appendChild(document.createTextNode(" · "));ps.appendChild(a)});
  pn.appendChild(ps);
  pn.appendChild(el("div","how","Miktar etiketten bilinemez; bu bir risk hesabı değil, bilgi notudur."));
  d.appendChild(pn);
  b.onclick=function(){pn.hidden=!pn.hidden;b.setAttribute("aria-expanded",pn.hidden?"false":"true");b.classList.toggle("on",!pn.hidden)};
  return d;
}
function comboSection(box,list){
  if(!list.length)return;
  box.appendChild(el("h2",null,"Birlikte Dikkat"));
  list.forEach(function(c){box.appendChild(comboCard(c))});
}
function render(res,br){
  var box=$("sonuc");box.textContent="";LAST=res;LASTBR=br||[];
  var S=summarize(res,IDX);LASTSUM=S;
  if(!res.length&&!LASTBR.length){box.textContent="Eşleşen bir şey bulunamadı. “Okunan Metin” bölümünü açıp okunan yazıyı kontrol edin.";return}
  if(S.cancer.length){
    var canc={yes:[],may:[]};S.cancer.forEach(function(c){(c.may?canc.may:canc.yes).push(typeof c==="string"?c:c.name)});
    var cd=el("div","res prof r"),hd=el("div","hd"),b=el("button","info sm","i");b.type="button";b.setAttribute("aria-label","Kanserojen madde hakkında bilgi");
    hd.appendChild(el("div","t","Kanserojen olabilecek madde"));hd.appendChild(b);cd.appendChild(hd);
    if(canc.yes.length)cd.appendChild(el("div","ln",canc.yes.join(", ")));
    if(canc.may.length){var d=el("div","ln");d.appendChild(el("b",null,"İçerebilir: "));d.appendChild(document.createTextNode(canc.may.join(", ")));cd.appendChild(d)}
    var ipan=el("div","ipanel");ipan.hidden=true;
    ipan.appendChild(el("div","how","IARC sınıflandırmasına göre (Grup 2A muhtemelen, 2B olası kanserojen). Miktar etikette yazmadığı için risk hesaplanamaz."));
    cd.appendChild(ipan);b.onclick=function(){ipan.hidden=!ipan.hidden;b.setAttribute("aria-expanded",ipan.hidden?"false":"true");b.classList.toggle("on",!ipan.hidden)};
    box.appendChild(cd);
  }
  profileCards(S).forEach(function(c){box.appendChild(c)});
  box.appendChild(summaryCard(S,res));
  if(LASTBR.length)box.appendChild(brandCard(LASTBR));
  comboSection(box,findCombos(COMBO,"gida",comboItemsFood(res,IDX)));
  var E=res.filter(function(r){return !r.isB&&!r.neg});
  if(E.length){box.appendChild(el("h2",null,"Katkı Maddeleri"));E.forEach(function(r){box.appendChild(additiveCard(r))})}
  var B=res.filter(function(r){return r.isB&&!r.neg}),notes=B.map(function(r){return IDX.byId[r.ids[0]]}).filter(function(it){return it.note});
  if(B.length){
    var bd=secBox(box,"Okunan diğer içerik",B.length);
    var seen={};B.forEach(function(r){var it=IDX.byId[r.ids[0]];if(seen[it.id])return;seen[it.id]=1;var l=el("div","ln");l.appendChild(el("b",null,it.name));if(it.note){l.appendChild(document.createTextNode(": "+it.note))}bd.appendChild(l)});
  }
  box.appendChild(el("div","how it","Sonuçlar yalnızca okunan metne dayanır, miktar bilgisi içermez ve tıbbi tavsiye değildir."));
}
function run(){
  var t=$("metin").value;
  if(MODE==="koz"){
    if(!t.trim()){$("sonuc").textContent="Önce metin girin ya da fotoğraftan okutun.";return}
    if(!KIDX){$("sonuc").textContent="Kozmetik listeleri yükleniyor…";loadK().then(run,function(){$("sonuc").textContent="Kozmetik listesi yüklenemedi; internet bağlantısını kontrol edin."});return}
    try{renderK(analyzeK(t,KIDX,{ptype:PTYPE}))}catch(e){$("sonuc").textContent="Analiz hatası: "+e.message}
    if(looksCleaning(t))$("sonuc").insertBefore(suggestCardT(),$("sonuc").firstChild);
    return;
  }
  if(MODE==="tem"){
    if(!t.trim()){$("sonuc").textContent="Önce metin girin ya da fotoğraftan okutun.";return}
    if(!TIDX){$("sonuc").textContent="Temizlik listeleri yükleniyor…";loadT().then(run,function(){$("sonuc").textContent="Temizlik listesi yüklenemedi; internet bağlantısını kontrol edin."});return}
    try{renderT(analyzeT(t,TIDX,KIDX))}catch(e){$("sonuc").textContent="Analiz hatası: "+e.message}
    return;
  }
  if(!IDX){$("sonuc").textContent="Listeler henüz yüklenmedi; sayfanın üstündeki durum satırına bakın.";return}
  if(!t.trim()){$("sonuc").textContent="Önce metin girin ya da fotoğraftan okutun.";return}
  try{render(analyze(t,IDX),BRANDS?findBrands(t,BRANDS):[])}catch(e){$("sonuc").textContent="Analiz hatası: "+e.message}
  if(looksCleaning(t))$("sonuc").insertBefore(suggestCardT(),$("sonuc").firstChild);
  else if(looksCosmetic(t))$("sonuc").insertBefore(suggestCard(),$("sonuc").firstChild);
}
// Metin elle düzeltildiğinde sonuç kendiliğinden güncellenir (yazmayı bitirmesi beklenir)
var RUN_T=null;$("metin").addEventListener("input",function(){clearTimeout(RUN_T);RUN_T=setTimeout(run,600)});
var ORNEK_GIDA="İçindekiler: Şeker, buğday unu, bitkisel yağ (palm), glikoz şurubu, yağsız süt tozu, peynir altı suyu tozu, renklendirici (tartrazin, E 110), koruyucu (E2 11), titanyum dioks1t, asitlik düzenleyici (sitrik asit), emülgatör (soya lesitini), monosodyum glutamet, karamel, aroma verici, yumurta tozu. Eser miktarda fındık ve susam içerebilir. Enerji 450 kcal, E 100 g";
var ORNEK_KOZ="Ingredients: Aqua, Glycerin, Cetearyl Alcohol, Paraffinum Liquidum, Parfum, Methylparaben, DMDM Hydantoin, Linalool, Limonene, Hexyl Cinnamal, Butylphenyl Methylpropional, Retinyl Palmitate, Lanolin, Glycerln Stearate, Cl 77891 [+/- CI 77491]";
var ORNEK_TEM="İçindekiler: %5-15 anyonik yüzey aktif maddeler, %5'ten az noniyonik yüzey aktif maddeler, sabun, fosfonatlar, enzimler, optik parlatıcılar, parfüm (Hexyl Cinnamal, Limonene, Linalool), koruyucu (Benzisothiazolinone, Methylisothiazolinone). TEHLİKE. Ciddi göz hasarına yol açar. Cilt tahrişine yol açar. Sucul ortamda uzun süre kalıcı, zararlı etki. Çocukların ulaşamayacağı yerde saklayın.";
$("ornek").onclick=function(){$("metin").value=MODE==="koz"?ORNEK_KOZ:MODE==="tem"?ORNEK_TEM:ORNEK_GIDA;run()};

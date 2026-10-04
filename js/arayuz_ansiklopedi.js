/* Ansiklopedi sayfası arayüzü (ansiklopedi.html). ?m=<slug> ya da ?id=E322 madde sayfasını, parametresiz açılış arama ve kayıtlı maddeleri gösterir. */
var AD=null,AT={},AIDX=null,ABY={},ACUR=null;
var AREPO="https://github.com/burakkagancan-ux/tagsis/issues/new";
function a$(i){return document.getElementById(i)}
function h(tag,cls,txt){var e=document.createElement(tag);if(cls)e.className=cls;if(txt!=null)e.textContent=txt;return e}
function t(k){return ansT(AT,k)}
function svg(path,cls){var s=document.createElementNS("http://www.w3.org/2000/svg","svg");s.setAttribute("viewBox","0 0 24 24");s.setAttribute("aria-hidden","true");if(cls)s.setAttribute("class",cls);s.innerHTML=path;return s}
/* Risk ikonları renkle birlikte şekille de ayrılır: yeşil onay, sarı üçgen, kırmızı ünlem */
var RICON={
  green:'<circle cx="12" cy="12" r="10" fill="#1F4D3A"/><path d="M7 12.5l3.2 3.2L17 9" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>',
  amber:'<path d="M12 2.5L23 21.5H1z" fill="#8A5A00"/><path d="M12 9v6" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/><circle cx="12" cy="18.2" r="1.4" fill="#fff"/>',
  red:'<circle cx="12" cy="12" r="10" fill="#A4470B"/><path d="M12 6.5v7" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/><circle cx="12" cy="17.2" r="1.5" fill="#fff"/>'
};
var PWICON='<circle cx="12" cy="12" r="10" fill="currentColor"/><path d="M12 6.5v7" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/><circle cx="12" cy="17.2" r="1.5" fill="#fff"/>';
function tarih(s){var m=/^(\d{4})-(\d\d)-(\d\d)$/.exec(s||"");return m?m[3]+"."+m[2]+"."+m[1]:""}
function prof(){try{return JSON.parse(localStorage.getItem("profil")||"null")}catch(e){return null}}
function marks(){try{var a=JSON.parse(localStorage.getItem("yerimleri")||"[]");return Array.isArray(a)?a:[]}catch(e){return[]}}
function setMarks(a){try{localStorage.setItem("yerimleri",JSON.stringify(a))}catch(e){}}
function link(r){return "ansiklopedi.html?m="+encodeURIComponent(r.slug)}

/* ---------- Madde sayfası ---------- */
function showRecord(r){
  ACUR=r;var box=a$("ana");box.textContent="";
  var name=t(r.names.primary);
  document.title=r.id+" "+name+" · Ansiklopedi";
  var bm=a$("kaydet");bm.hidden=false;syncMark();
  var bd=h("div","badges");bd.appendChild(h("span","ecode",r.id));bd.appendChild(h("span","cat",t("cat."+r.category)));box.appendChild(bd);
  box.appendChild(h("h2","name",name));
  if(r.summary)box.appendChild(h("p","sum",t(r.summary)));
  // Genel değerlendirme
  var rk=h("section","card risk "+r.risk_level);rk.setAttribute("aria-label","Genel değerlendirme");
  rk.appendChild(svg(RICON[r.risk_level],"ico"));
  var rt=h("div");rt.appendChild(h("div","lbl",t("risk."+r.risk_level)));
  rt.appendChild(h("div","mut",r.review==="curated"?"Kanıt düzeyi: "+t("evidence."+r.evidence_level)+" · Son inceleme: "+tarih(r.last_reviewed):"Kanıt düzeyi henüz değerlendirilmedi"));
  if(r.evaluation)rt.appendChild(h("p",null,t(r.evaluation)));
  rk.appendChild(rt);box.appendChild(rk);
  // Profil uyarısı: yalnızca kullanıcının seçtiği hassasiyetle eşleşirse
  ansProfileWarnings(r,prof()).forEach(function(w){
    var d=h("section","pw "+w.severity);d.setAttribute("role","note");
    var tt=h("div","t");var ic=svg(PWICON);ic.style.color=w.severity==="high"?"#B3261E":"#8A5A00";tt.appendChild(ic);
    tt.appendChild(document.createTextNode("Hassasiyetinizle eşleşti: "+(t("profile."+w.profile)||w.profile)));d.appendChild(tt);
    d.appendChild(h("p",null,t(w.text)));box.appendChild(d);
  });
  if(r.review!=="curated")box.appendChild(h("div","auto","Bu sayfa uygulamanın katkı maddesi listesinden otomatik oluşturuldu ve henüz elle incelenmedi. Ayrıntılı bilgiler eklendikçe güncellenecek."));
  // Hızlı bilgi kartları (otomatik kayıtta bilinmeyenler gösterilmez)
  var q=h("div","quick"),df=r.diet_flags,cur=r.review==="curated";
  [["Vegan",df.vegan==="unknown"&&!cur?null:t("diet."+df.vegan)],["Kaynak",df.source==="unknown"&&!cur?null:t("source."+df.source)],["Glüten",df.gluten==="unknown"&&!cur?null:(df.gluten==="no"?"İçermez":df.gluten==="yes"?"İçerir":t("diet.unknown"))]]
    .forEach(function(x){if(x[1]==null)return;var c=h("div");c.appendChild(h("b",null,x[0]));c.appendChild(h("span",null,x[1]));q.appendChild(c)});
  if(q.childNodes.length)box.appendChild(q);
  // Sekmeler
  var tabs=h("div","tabs");tabs.setAttribute("role","tablist");tabs.setAttribute("aria-label","Madde bilgileri");box.appendChild(tabs);
  var P=[["genel","Genel",panelGenel(r)],["otorite","Otoriteler",panelOtorite(r)],["kaynak","Kaynaklar",panelKaynak(r)]];
  P.forEach(function(p,i){
    var b=h("button","tab",p[1]);b.type="button";b.id="tab-"+p[0];b.setAttribute("role","tab");b.setAttribute("aria-controls","pn-"+p[0]);
    var pn=p[2];pn.id="pn-"+p[0];pn.className="panel";pn.setAttribute("role","tabpanel");pn.setAttribute("aria-labelledby",b.id);pn.tabIndex=0;
    b.onclick=function(){sel(i,true)};
    b.onkeydown=function(e){if(e.key==="ArrowRight"||e.key==="ArrowLeft"){e.preventDefault();sel((i+(e.key==="ArrowRight"?1:P.length-1))%P.length,true)}};
    tabs.appendChild(b);box.appendChild(pn);
  });
  function sel(i,focus){P.forEach(function(p,j){var b=a$("tab-"+p[0]);b.setAttribute("aria-selected",i===j?"true":"false");b.tabIndex=i===j?0:-1;a$("pn-"+p[0]).hidden=i!==j});if(focus)a$("tab-"+P[i][0]).focus()}
  sel(0,false);
  // Benzer maddeler
  var rel=r.related_ids.map(function(x){return ABY[x]}).filter(Boolean);
  if(rel.length){
    box.appendChild(h("h2","sec","Benzer maddeler"));
    var rw=h("div","rel");
    rel.forEach(function(x){var a=h("a");a.href=link(x);var b=h("b");b.appendChild(svg(RICON[x.risk_level],"mini"));b.appendChild(document.createTextNode(x.id));a.appendChild(b);a.appendChild(h("span",null,t(x.names.primary)));a.setAttribute("aria-label",x.id+" "+t(x.names.primary)+", "+t("risk."+x.risk_level));rw.appendChild(a)});
    box.appendChild(rw);
  }
  footer(box,r);
}
function panelGenel(r){
  var p=h("div"),c=r.content;
  p.appendChild(h("h3",null,"Ne işe yarar?"));p.appendChild(h("p",null,t(c.what_it_does)));
  if(c.found_in.length){p.appendChild(h("h3",null,"Nerede bulunur?"));var ul=h("ul");c.found_in.forEach(function(k){ul.appendChild(h("li",null,t(k)))});p.appendChild(ul)}
  if(c.in_the_body){p.appendChild(h("h3",null,"Vücutta ne olur?"));p.appendChild(h("p",null,t(c.in_the_body)))}
  if(r.review!=="curated")p.appendChild(h("p","mut","“Nerede bulunur?” ve “Vücutta ne olur?” bölümleri bu madde için henüz yazılmadı."));
  return p;
}
function panelOtorite(r){
  var p=h("div");
  if(!r.regulatory.length){p.appendChild(h("p","mut","Bu madde için henüz kurum bilgisi eklenmedi."));return p}
  r.regulatory.forEach(function(g){
    var row=h("div","ag"),l=h("div");
    l.appendChild(h("div","who",g.agency+" · "+(t("region."+g.region)||g.region)+(g.year?" · "+g.year:"")));
    l.appendChild(h("div","d",t(g.detail)));
    if(g.source_url){var a=h("a",null,"Kaynağı aç");a.href=g.source_url;a.target="_blank";a.rel="noopener";a.style.fontSize="14px";l.appendChild(a)}
    row.appendChild(l);row.appendChild(h("span","st "+g.status,t("status."+g.status)));p.appendChild(row);
  });
  return p;
}
function panelKaynak(r){
  var p=h("div");
  if(!r.sources.length){p.appendChild(h("p","mut","Bu madde için henüz kaynak eklenmedi."));return p}
  r.sources.forEach(function(s){
    var d=h("div","src");
    if(s.url){var a=h("a",null,s.title);a.href=s.url;a.target="_blank";a.rel="noopener";d.appendChild(a)}else d.appendChild(h("span","ttl",s.title));
    if(s.official)d.appendChild(h("span","tag","Resmi"));
    d.appendChild(h("div","mut",s.publisher+(s.year?", "+s.year:"")+(s.todo?" · Bağlantı henüz eklenmedi":"")));
    p.appendChild(d);
  });
  return p;
}
function footer(box,r){
  var f=h("div","foot");f.appendChild(h("div",null,"Bilgilendirme amaçlıdır, tıbbi tavsiye yerine geçmez."));
  var a=h("a",null,"Hata bildir");
  a.href=AREPO+"?title="+encodeURIComponent("Ansiklopedi hatası"+(r?": "+r.id+" "+t(r.names.primary):""))+"&body="+encodeURIComponent("Sayfa: "+location.href+"\n\nHatalı bilgi:\n\nDoğrusu ve kaynağı (varsa):\n");
  a.target="_blank";a.rel="noopener";f.appendChild(a);box.appendChild(f);
}
function syncMark(){var b=a$("kaydet"),on=!!ACUR&&marks().indexOf(ACUR.id)>-1;b.setAttribute("aria-pressed",on?"true":"false");b.setAttribute("aria-label",on?"Kaydedilenlerden çıkar":"Kaydet")}
a$("kaydet").onclick=function(){if(!ACUR)return;var m=marks().filter(function(x){return x!==ACUR.id});if(m.length===marks().length)m.unshift(ACUR.id);setMarks(m);syncMark()};
a$("geri").onclick=function(){
  var same=document.referrer&&document.referrer.indexOf(location.origin)===0;
  if(same&&history.length>1)history.back();else location.href=ACUR?"ansiklopedi.html":"ocr.html";
};

/* ---------- Arama ve kayıtlı maddeler ---------- */
function rowFor(r){
  var a=h("a","row");a.href=link(r);a.appendChild(svg(RICON[r.risk_level]));a.appendChild(h("span","rc",r.id));
  var n=h("span","rn",t(r.names.primary));n.appendChild(h("span","rk",t("cat."+r.category)+" · "+t("risk."+r.risk_level)));a.appendChild(n);return a;
}
function showSearch(){
  ACUR=null;a$("kaydet").hidden=true;document.title="Ansiklopedi";
  var box=a$("ana");box.textContent="";
  var lb=h("label","vh","Madde ara");lb.htmlFor="ara";box.appendChild(lb);
  var inp=h("input");inp.type="search";inp.id="ara";inp.placeholder="Ad ya da E kodu: lesitin, E322…";inp.autocomplete="off";inp.setAttribute("enterkeyhint","search");box.appendChild(inp);
  var out=h("div","list");out.setAttribute("aria-live","polite");box.appendChild(out);
  function draw(){
    var q=inp.value;out.textContent="";
    try{history.replaceState(null,"",q.trim()?"ansiklopedi.html?q="+encodeURIComponent(q):"ansiklopedi.html")}catch(e){}
    if(q.trim()){
      var res=ansSearch(AIDX,q,40);
      out.appendChild(h("p","mut",res.length?res.length+(res.length===40?"+":"")+" sonuç":"Sonuç bulunamadı. Başka bir yazımla deneyin."));
      res.forEach(function(r){out.appendChild(rowFor(r))});return;
    }
    var m=marks().map(function(x){return ABY[x]}).filter(Boolean);
    out.appendChild(h("h2","sec","Kaydettiklerim"));
    if(m.length)m.forEach(function(r){out.appendChild(rowFor(r))});else out.appendChild(h("p","mut","Henüz kayıtlı madde yok. Bir maddenin sayfasındaki yer imi düğmesiyle kaydedebilirsiniz."));
    out.appendChild(h("h2","sec","Ayrıntılı incelenen maddeler"));
    AD.records.filter(function(r){return r.review==="curated"}).forEach(function(r){out.appendChild(rowFor(r))});
    out.appendChild(h("p","mut",AD.records.length+" maddenin sayfası var; ayrıntılı incelenen maddeler zamanla artacak."));
  }
  var tm=null;inp.addEventListener("input",function(){clearTimeout(tm);tm=setTimeout(draw,150)});
  var q0=new URLSearchParams(location.search).get("q");if(q0)inp.value=q0;
  draw();
  footer(box,null);
}

/* ---------- Açılış ---------- */
function aGet(p){return fetch(p).then(function(r){if(!r.ok)throw new Error(p);return r.json()})}
Promise.all([aGet("data/ansiklopedi.json"),aGet("data/ansiklopedi_tr.json")]).then(function(v){
  AD=v[0];AT=v[1].t;AD.records.forEach(function(r){ABY[r.id]=r});AIDX=ansIndex(AD.records,AT);
  var sp=new URLSearchParams(location.search),m=sp.get("m"),id=sp.get("id"),r=null;
  if(m)r=AD.records.filter(function(x){return x.slug===m})[0]||null;
  if(!r&&id){var f=ansFold(id);r=AD.records.filter(function(x){return ansFold(x.id)===f})[0]||null}
  if(r){try{if(sp.get("m")!==r.slug)history.replaceState(null,"","ansiklopedi.html?m="+r.slug)}catch(e){}showRecord(r)}
  else{showSearch();if(m||id)a$("ana").insertBefore(h("p","mut","Aradığınız madde bulunamadı."),a$("ana").firstChild)}
}).catch(function(){a$("ana").textContent="Ansiklopedi verisi yüklenemedi. İnternet bağlantınızı kontrol edip sayfayı yenileyin."});
try{if("serviceWorker" in navigator)navigator.serviceWorker.register("sw.js").catch(function(){})}catch(e){}

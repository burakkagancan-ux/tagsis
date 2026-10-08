/* Arayüz: kaydedilen ürünler. Sonuç barında "Kaydet", Hassasiyetlerim'de "Kaydedilen Ürünlerim" ekranı (tür süzgeci, arama, sıralama,
   aç / karşılaştır / yeniden adlandır / sil, yedekle / geri yükle). Saf mantık js/kayit.js. Kayıtlar yalnızca bu cihazda. */
var KAYIT_ACILAN=null;   // listeden açılan kaydın kimliği: sonuç çizilince değerlendirme değişti mi bakılır
function kayitLoad(){try{var a=JSON.parse(localStorage.getItem("kayitli")||"[]");return Array.isArray(a)?a:[]}catch(e){return[]}}
function kayitStore(a){try{localStorage.setItem("kayitli",JSON.stringify(a));return true}catch(e){return false}}
function kayitGet(id){return kayitLoad().filter(function(x){return x.id===id})[0]||null}
function kayitTarih(t){var d=new Date(t);return d.getDate()+" "+PAY_AY[d.getMonth()]+" "+d.getFullYear()}
/* Ekrandaki sonucun özeti (veri yüklüyse) */
function kayitSimdi(mode,text){
  try{if(!karsReady(mode))return null;return kayitOzet(karsProduct({mode:mode,text:text,name:""}))}catch(e){return null}
}
/* Sonuç barındaki düğme: kayıtlıysa "Kaydedildi", değilse "Kaydet" */
function kayitBtn(mode){
  var text=$("metin").value.trim(),k=kayitFind(kayitLoad(),mode,text);
  var b=el("button","alt pay kayitb"+(k?" on":""));b.type="button";
  b.innerHTML='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 3h12v18l-6-4.5L6 21z"/></svg>';
  b.appendChild(document.createTextNode(k?"Kaydedildi":"Kaydet"));
  b.setAttribute("aria-label",k?"Kayıtlı ürün: "+k.name+". Düzenlemek için dokunun":"Bu ürünü kaydet");
  b.onclick=function(){kayitForm(mode,text,b)};
  kayitDegisti(mode,text);
  return b;
}
/* Listeden açılan kayıtta değerlendirme kaydedildiğinden farklıysa bilgi kartı; özet güncellenir */
function kayitDegisti(mode,text){
  if(!KAYIT_ACILAN)return;
  var a=kayitLoad(),k=a.filter(function(x){return x.id===KAYIT_ACILAN})[0];KAYIT_ACILAN=null;
  if(!k||k.mode!==mode||k.text!==text)return;
  var oz=kayitSimdi(mode,text);if(!oz)return;
  var f=kayitFark(k.oz,oz);
  k.oz=oz;kayitStore(a);
  if(!f)return;
  var c=el("div","res "+(f.kotu?"y":"u"));c.appendChild(el("div","t","Kaydettiğinizden bu yana değerlendirme değişti"));
  c.appendChild(el("div","ln","Kayıt tarihinde: "+f.once+". Şimdi: "+f.simdi+"."));
  c.appendChild(el("div","how","Uygulamanın veri kaynakları güncellendi (ör. bir maddenin değerlendirmesi değişti). Ayrıntı aşağıdaki kartlarda."));
  setTimeout(function(){sonucUst(c)},0);
}
/* Kaydet / düzenle formu: ad (zorunlu), not (isteğe bağlı) */
function kayitForm(mode,text,ret){
  var a=kayitLoad(),k=kayitFind(a,mode,text),body=el("div","kform");
  var h=histLoad().filter(function(x){return x.id===HCUR&&x.text===text})[0];
  var def=k?k.name:h&&!/^Tarama \d+$/.test(h.name)?h.name:"";
  var l1=el("label","kname");l1.appendChild(el("span",null,"Ürün adı"));
  var inp=document.createElement("input");inp.type="text";inp.maxLength=60;inp.value=def;inp.placeholder="Ör. Marka Çikolatalı Gofret";inp.autocomplete="off";l1.appendChild(inp);body.appendChild(l1);
  var l2=el("label","kname");l2.appendChild(el("span",null,"Not (isteğe bağlı)"));
  var nt=document.createElement("textarea");nt.maxLength=300;nt.rows=2;nt.value=k?k.note||"":"";nt.placeholder="Ör. nereden alındı, fiyatı, çocuğum sevdi";l2.appendChild(nt);body.appendChild(l2);
  body.appendChild(el("div","how","Tür: "+KAYIT_TUR[mode]+". Okunan metin ve sonuç özeti yalnızca bu cihazda saklanır."));
  var msg=el("div","how");
  var go=el("button",null,k?"Değişiklikleri kaydet":"Kaydet");go.type="button";
  go.onclick=function(){
    var name=inp.value.trim();if(!name){msg.textContent="Ürüne bir ad verin.";inp.focus();return}
    var list=kayitLoad();
    if(!kayitFind(list,mode,text)&&list.length>=KAYIT_AYAR.enFazla){msg.textContent="En fazla "+KAYIT_AYAR.enFazla+" ürün kaydedilebilir. Profilim > Kaydedilen Ürünlerim'den eski kayıtları silin.";return}
    list=kayitAdd(list,{id:"k"+Date.now(),t:Date.now(),mode:mode,name:name,note:nt.value,text:text,oz:kayitSimdi(mode,text)},KAYIT_AYAR.enFazla);
    if(!kayitStore(list)){msg.textContent="Kaydedilemedi: cihazda yer kalmamış olabilir.";return}
    if(h&&h.name!==name)histRename(h.id,name);   // karşılaştırma ve paylaşım kartı da bu adı kullanır
    closeSheet();setSt(mode,"“"+name+"” kaydedildi. Profilim > Kaydedilen Ürünlerim'den ulaşabilirsiniz.");kayitBarYenile();kayitProfil();
  };
  body.appendChild(go);body.appendChild(msg);
  if(k){var del=el("button","alt","Kaydı sil");del.type="button";
    del.onclick=function(){kayitStore(kayitLoad().filter(function(x){return x.id!==k.id}));closeSheet();setSt(mode,"“"+k.name+"” kayıtlardan silindi.");kayitBarYenile();kayitProfil()};
    body.appendChild(del)}
  openSheet(k?"Kayıtlı ürün":"Ürünü kaydet",null,body,ret);
  setTimeout(function(){inp.focus()},50);
}
function kayitBarYenile(){var o=document.querySelector("#sonuc .resbar .kayitb");if(o)o.parentNode.replaceChild(kayitBtn(MODE),o)}

/* ---------- Hassasiyetlerim: "Kaydedilen Ürünlerim" düğmesi ---------- */
function kayitProfil(){
  var box=$("kayitbar");if(!box)return;box.textContent="";
  var n=kayitLoad().length,b=el("button","kayitac");b.type="button";
  b.innerHTML='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 3h12v18l-6-4.5L6 21z"/></svg>';
  var s=el("span","kt");s.appendChild(el("b",null,"Kaydedilen Ürünlerim"));s.appendChild(el("span","mut",n?n+" ürün":"Henüz kayıt yok"));b.appendChild(s);
  b.onclick=function(){kayitAc()};box.appendChild(b);
}

/* ---------- Kaydedilen Ürünlerim ekranı ---------- */
var KAYIT_SUZ={mode:"",q:"",sira:"yeni"};
try{var ks=JSON.parse(localStorage.getItem("kayit_suz")||"null");if(ks&&typeof ks==="object"){KAYIT_SUZ.mode=KAYIT_TUR[ks.mode]?ks.mode:"";KAYIT_SUZ.sira=["yeni","ad","risk"].indexOf(ks.sira)>-1?ks.sira:"yeni"}}catch(e){}
function kayitAc(){
  var box=$("kayit");box.textContent="";
  var bk=el("button","alt kback","← Profilim");bk.type="button";bk.onclick=kayitKapat;box.appendChild(bk);
  box.appendChild(el("h2",null,"Kaydedilen Ürünlerim"));
  var all=kayitLoad(),say=kayitSay(all);
  // Tür süzgeci
  var sg=el("div","seg kseg");sg.setAttribute("role","radiogroup");sg.setAttribute("aria-label","Ürün türü süzgeci");
  [["","Tümü"],["gida","Gıda"],["koz","Kozmetik"],["tem","Temizlik"]].forEach(function(x){
    var b=el("button",null,x[1]+" ("+say[x[0]]+")");b.type="button";b.setAttribute("role","radio");b.setAttribute("data-m",x[0]);b.setAttribute("aria-checked",String(KAYIT_SUZ.mode===x[0]));
    b.onclick=function(){KAYIT_SUZ.mode=x[0];kayitSuzKaydet();kayitAc()};sg.appendChild(b);
  });
  box.appendChild(sg);
  var row=el("div","krow");
  var q=document.createElement("input");q.type="search";q.id="kara";q.placeholder="Ad ya da notta ara";q.value=KAYIT_SUZ.q;q.setAttribute("aria-label","Kayıtlarda ara");row.appendChild(q);
  var so=document.createElement("select");so.id="ksira";so.setAttribute("aria-label","Sıralama");
  [["yeni","En yeni"],["ad","Ada göre"],["risk","Önce uyarılı"]].forEach(function(o){var op=document.createElement("option");op.value=o[0];op.textContent=o[1];if(KAYIT_SUZ.sira===o[0])op.selected=true;so.appendChild(op)});
  so.onchange=function(){KAYIT_SUZ.sira=so.value;kayitSuzKaydet();ciz()};row.appendChild(so);
  box.appendChild(row);
  var ul=el("div","klistk");box.appendChild(ul);
  function ciz(){
    ul.textContent="";
    var L=kayitList(kayitLoad(),KAYIT_SUZ.mode,KAYIT_SUZ.q,KAYIT_SUZ.sira);
    if(!L.length){ul.appendChild(el("p","mut",all.length?"Bu süzgece uyan kayıt yok.":"Henüz kayıtlı ürün yok. Bir ürünü taradıktan sonra sonuç ekranındaki “Kaydet” düğmesine dokunun."));return}
    L.forEach(function(k){ul.appendChild(kayitSatir(k))});
  }
  q.oninput=function(){KAYIT_SUZ.q=q.value;ciz()};
  ciz();
  // Yedekleme: kayıtlar yalnızca bu cihazda; telefon değişince ya da tarayıcı verisi silinince kaybolmasın
  var yd=el("div","kyedek");yd.appendChild(el("h3",null,"Yedek"));
  yd.appendChild(el("div","how","Kayıtlar yalnızca bu cihazda saklanır. Tarayıcı verisi silinirse kaybolur; yedek dosyası alıp başka cihazda geri yükleyebilirsiniz."));
  var r2=el("div","row");
  var ex=el("button","alt","Yedek dosyası indir");ex.type="button";ex.disabled=!all.length;
  ex.onclick=function(){
    var blob=new Blob([kayitYedek(kayitLoad())],{type:"application/json"}),a=document.createElement("a"),d=new Date();
    a.href=URL.createObjectURL(blob);a.download="tagsis-kayitlar-"+d.getFullYear()+"-"+(d.getMonth()+1)+"-"+d.getDate()+".json";document.body.appendChild(a);a.click();
    setTimeout(function(){URL.revokeObjectURL(a.href);a.remove()},1000);
  };
  var im=el("button","alt","Yedekten geri yükle");im.type="button";
  var fi=document.createElement("input");fi.type="file";fi.accept="application/json,.json";fi.className="vh";fi.id="kyedekdosya";
  im.onclick=function(){fi.click()};
  var ym=el("div","how");
  fi.onchange=function(){
    var f=fi.files&&fi.files[0];if(!f)return;
    var rd=new FileReader();rd.onload=function(){
      var r=kayitGeriYukle(kayitLoad(),String(rd.result),KAYIT_AYAR.enFazla);
      if(!r.ok){ym.textContent=r.hata;return}
      kayitStore(r.list);kayitProfil();kayitAc();
      $("kayit").querySelector(".kyedek .how:last-child").textContent=r.eklenen+" ürün eklendi."+(r.fazla?" "+r.fazla+" eski kayıt sınır ("+KAYIT_AYAR.enFazla+") nedeniyle alınmadı.":"");
    };rd.readAsText(f);
  };
  r2.appendChild(ex);r2.appendChild(im);r2.appendChild(fi);yd.appendChild(r2);yd.appendChild(ym);box.appendChild(yd);
  document.body.classList.add("mode-kayit");box.hidden=false;window.scrollTo(0,0);bk.focus();
}
function kayitSuzKaydet(){try{localStorage.setItem("kayit_suz",JSON.stringify({mode:KAYIT_SUZ.mode,sira:KAYIT_SUZ.sira}))}catch(e){}}
function kayitKapat(){document.body.classList.remove("mode-kayit");$("kayit").hidden=true;window.scrollTo(0,0)}
/* Liste satırı: ad, tür, tarih, özet; dokununca işlemler */
function kayitSatir(k){
  var b=el("button","kitem kkayit");b.type="button";
  var t=el("span","kin",k.name);b.appendChild(t);
  var m=el("span","kis");m.appendChild(el("span","chip",KAYIT_TUR[k.mode]));m.appendChild(document.createTextNode(" "+kayitTarih(k.u||k.t)));b.appendChild(m);
  var oz=el("span","koz");
  if(k.oz){
    if(k.oz.u){oz.appendChild(cmpIcon(3));oz.appendChild(document.createTextNode(k.oz.u+" uyarı  "))}
    if(k.oz.d){oz.appendChild(cmpIcon(2));oz.appendChild(document.createTextNode(k.oz.d+" dikkat"))}
    if(!k.oz.u&&!k.oz.d){oz.appendChild(cmpIcon(0));oz.appendChild(document.createTextNode("Özel uyarı yok"))}
  }
  b.appendChild(oz);
  if(k.note)b.appendChild(el("span","kis",k.note));
  b.onclick=function(){kayitIslem(k,b)};
  return b;
}
function kayitIslem(k,ret){
  var body=el("div","kpick");
  if(k.oz&&k.oz.top.length)body.appendChild(el("div","ln","En riskli: "+k.oz.top.join(", ")));
  function btn(txt,cls,fn){var b=el("button",cls,txt);b.type="button";b.onclick=fn;body.appendChild(b);return b}
  btn("Sonucu aç",null,function(){closeSheet();kayitSonuc(k)});
  var ayni=kayitLoad().filter(function(x){return x.mode===k.mode&&x.id!==k.id});
  var kb=btn("Başka kayıtlı ürünle karşılaştır","alt",function(){closeSheet();kayitKarsSec(k,ret)});
  if(!ayni.length){kb.disabled=true;body.appendChild(el("div","how","Karşılaştırmak için aynı türden en az iki kayıtlı ürün gerekir."))}
  btn("Adı ya da notu düzenle","alt",function(){closeSheet();kayitSonuc(k,true)});
  btn("Sil","alt kclr",function(){
    if(!confirm("“"+k.name+"” kayıtlardan silinsin mi?"))return;
    kayitStore(kayitLoad().filter(function(x){return x.id!==k.id}));closeSheet();kayitProfil();kayitAc();
  });
  openSheet(k.name,KAYIT_TUR[k.mode]+" · "+kayitTarih(k.u||k.t),body,ret);
}
/* Kaydı sonuç ekranında açar: tür seçilir, metin kutuya konur, analiz edilir (tarama geçmişine yazılmaz) */
function kayitSonuc(k,duzenle){
  kayitKapat();
  if(location.hash==="#profil"){history.replaceState(null,"",location.pathname+location.search);$("pd").open=false;tabSync()}
  if(CMP_IDS)closeCompare();
  KAYIT_ACILAN=k.id;$("metin").value=k.text;HSCAN=false;HMOD="gor";
  if(MODE!==k.mode)setMode(k.mode,true);else run();
  if(duzenle){var w=setInterval(function(){var b=document.querySelector("#sonuc .resbar .kayitb");if(b){clearInterval(w);b.click()}},100);setTimeout(function(){clearInterval(w)},8000)}
  var s=$("sonuc");if(s)s.scrollIntoView({block:"start"});
}
/* İki kayıtlı ürünü karşılaştırma: kayıtlar karşılaştırma ekranına geçmiş kaydı gibi verilir */
function kayitKarsSec(k,ret){
  var list=kayitList(kayitLoad(),k.mode,"","yeni").filter(function(x){return x.id!==k.id}),body=el("div","kpick");
  body.appendChild(el("h3",null,"“"+k.name+"” ile karşılaştır"));
  list.forEach(function(x){
    var b=el("button","kitem");b.type="button";b.appendChild(el("span","kin",x.name));b.appendChild(el("span","kis",kayitTarih(x.u||x.t)));
    b.onclick=function(){closeSheet();kayitKarsAc(k,x)};body.appendChild(b);
  });
  openSheet("Karşılaştır",KAYIT_TUR[k.mode],body,ret);
}
function kayitKarsAc(a,b){
  var hazir=karsReady(a.mode)?Promise.resolve():a.mode==="koz"?loadK():a.mode==="tem"?loadT():Promise.reject();
  hazir.then(function(){kayitKapat();if(location.hash==="#profil"){history.replaceState(null,"",location.pathname+location.search);$("pd").open=false;tabSync()}showCompare(a.id,b.id)},
    function(){alert(KAYIT_TUR[a.mode]+" listeleri yüklenemedi; internet bağlantısını kontrol edin.")});
}
kayitProfil();
window.addEventListener("hashchange",kayitProfil);   // Profilim sekmesine her girişte sayı güncel
window.addEventListener("storage",function(e){if(e.key==="kayitli")kayitProfil()});   // başka sekmede kaydedilince

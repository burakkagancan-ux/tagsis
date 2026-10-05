/* Paylaşılabilir sonuç kartı: saf mantık (DOM yok). Kart modeli, paylaşım metni, satır kırma ve canvas çizimi.
   Çizim yalnızca verilen 2B bağlamı (ctx) kullanır; testler sahte bir bağlamla çizilen metinleri denetler.
   Seviye (lvl): 0 özel uyarı yok, 1 dikkat, 2 uyarı. Skor yok. Kişisel (profil) uyarılar yalnızca opt.kisisel açıkken karta girer. */
var PAY_AY=["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"];
var PAY_LBL=["Özel uyarı yok","Dikkat","Uyarı"];
function payIki(n){return (n<10?"0":"")+n}
function payTarih(t){var d=new Date(t);return d.getDate()+" "+PAY_AY[d.getMonth()]+" "+payIki(d.getHours())+":"+payIki(d.getMinutes())}
/* Kartta ürün adı: kullanıcının verdiği ad; otomatik ad ("Tarama 3") ise sıra + tarih ve saat */
function payAd(e,now){
  if(!e)return "Tarama · "+payTarih(now||Date.now());
  var m=/^Tarama (\d+)$/.exec(e.name||"");
  if(m||!(e.name||"").trim())return (m?"Tarama "+m[1]:"Tarama")+" · "+payTarih(e.t||now||Date.now());
  return e.name.trim();
}
function payUniq(items){var by={},out=[];items.forEach(function(it){var k=it.name;if(by[k]){if(it.lvl>by[k].lvl)by[k].lvl=it.lvl;return}by[k]={name:it.name,lvl:it.lvl};out.push(by[k])});return out}
/* Gıda: karşılaştırmadaki ürün özeti (cmpProduct) kullanılır; rank 3 uyarı, 2 dikkat, 1 doğrulanmadı, 0 özel uyarı yok */
function payFromFood(text,idx){
  var P=cmpProduct(text,idx,null,""),items=[],unv=0;
  P.items.forEach(function(it){if(it.rank===1){unv++;return}items.push({name:it.name,lvl:it.rank===3?2:it.rank===2?1:0})});
  var a=P.allergen,al=(a.yes.length?"İçerir: "+a.yes.join(", "):"")+(a.yes.length&&a.may.length?" · ":"")+(a.may.length?"İçerebilir: "+a.may.join(", "):"");
  return {mode:"gida",items:payUniq(items),unverified:unv,allergens:al};
}
/* Kozmetik: AB'de yasak ve başka pazarda yasak (red/orange) uyarı, yellow dikkat */
function payFromK(res,S){
  var items=[];
  res.forEach(function(r){if(!r.found)return;items.push({name:r.name,lvl:r.level==="red"||r.level==="orange"?2:r.level==="yellow"?1:0})});
  return {mode:"koz",items:payUniq(items),unverified:0,allergens:S&&S.fragrance.length?"Koku alerjeni: "+S.fragrance.join(", "):""};
}
/* Temizlik: tehlike ifadeleri ve madde notları; ciddi tehlike (red) uyarı, yellow dikkat */
function payFromT(A,S){
  var items=[],L=function(l){return l==="red"?2:l==="yellow"?1:0};
  A.hazards.forEach(function(x){items.push({name:x.code+" "+x.h.tr.replace(/^içerir\. /,"").replace(/\.$/,""),lvl:L(x.h.level)})});
  A.subs.forEach(function(x){items.push({name:x.s.inci.length>1?"Enzim: "+x.s.inci.join(", ").toLowerCase():x.s.inci[0],lvl:L(x.s.level)})});
  A.inci.forEach(function(x){items.push({name:x.name,lvl:0})});
  return {mode:"tem",items:payUniq(items),unverified:0,allergens:S&&S.fragrance.length?"Koku alerjeni: "+S.fragrance.join(", "):""};
}
/* Kart modeli. src: {mode, items:[{name,lvl}], unverified, allergens, personal:[{t:metin, lvl:1|2}]}; opt: {name, kisisel} */
function payModel(src,opt,cfg){
  opt=opt||{};cfg=cfg||PAYLAS_AYAR;
  var items=(src.items||[]).slice(),c=[0,0,0];
  items.forEach(function(it){c[it.lvl]++});
  var risky=items.filter(function(it){return it.lvl>0}).map(function(it,i){return {name:it.name,lvl:it.lvl,i:i}});
  risky.sort(function(a,b){return b.lvl-a.lvl||a.i-b.i});   // en riskliden başlayarak, eşitlikte okunduğu sıra
  var n=cfg.enFazlaMadde,top=risky.slice(0,n).map(function(x){return {name:x.name,lvl:x.lvl}});
  var pers=opt.kisisel?(src.personal||[]).slice(0,cfg.enFazlaKisisel):[];
  return {mode:src.mode,name:opt.name||"Tarama",counts:{ok:c[0],dikkat:c[1],uyari:c[2]},unverified:src.unverified||0,
    total:items.length,top:top,more:Math.max(0,risky.length-n),allergens:src.allergens||"",personal:pers,
    hasPersonal:!!(src.personal&&src.personal.length)};
}
/* Paylaşım metni (görselle birlikte) */
function payText(M,cfg){
  cfg=cfg||PAYLAS_AYAR;
  var n=M.counts.dikkat+M.counts.uyari,what=M.mode==="tem"?"ifade ya da madde":"madde";
  var s=n?n+" "+what+" dikkat gerektiriyor.":"dikkat gerektiren "+what+" çıkmadı.";
  return M.name+" içeriğine baktım: "+s+" "+cfg.uygulamaAdi+" ile sen de tara: "+cfg.adres;
}
/* Metni en çok maxLines satıra böler; sığmayan son satır "…" ile kısaltılır. measure(metin) → piksel genişliği */
function payWrap(text,maxW,maxLines,measure){
  var words=String(text||"").replace(/\s+/g," ").trim().split(" ").filter(Boolean),lines=[],cur="";
  function cut(s){if(measure(s)<=maxW)return s;while(s.length>1&&measure(s+"…")>maxW)s=s.slice(0,-1);return s.replace(/[\s,·:;-]+$/,"")+"…"}
  words.forEach(function(w){var t=cur?cur+" "+w:w;if(measure(t)<=maxW||!cur)cur=t;else{lines.push(cur);cur=w}});
  if(cur)lines.push(cur);
  if(lines.length>maxLines)lines=lines.slice(0,maxLines-1).concat([lines.slice(maxLines-1).join(" ")]);
  return lines.map(cut);
}
/* ---------- Çizim ---------- */
var PAY_RENK={bg:"#F5F1E8",card:"#FFFFFF",line:"#E4DED2",ok:"#1F4D3A",okbg:"#E6EFE9",ink:"#1B211E",mute:"#5A615C",amb:"#8A5A00",ambbg:"#FFF3D1",hi:"#A4470B",hibg:"#FCE9DA",red:"#B3261E",redbg:"#FBE9E7",bant2:"#CFE0D6"};
var PAY_HF='"Bricolage Grotesque",system-ui,sans-serif',PAY_BF='"Figtree",system-ui,sans-serif';
function payRR(x,X,Y,W,H,r){x.beginPath();x.moveTo(X+r,Y);x.lineTo(X+W-r,Y);x.quadraticCurveTo(X+W,Y,X+W,Y+r);x.lineTo(X+W,Y+H-r);x.quadraticCurveTo(X+W,Y+H,X+W-r,Y+H);x.lineTo(X+r,Y+H);x.quadraticCurveTo(X,Y+H,X,Y+H-r);x.lineTo(X,Y+r);x.quadraticCurveTo(X,Y,X+r,Y);x.closePath()}
/* Seviye simgesi (sonuç ekranıyla aynı): yeşil daire + onay, amber üçgen + ünlem, koyu turuncu daire + ünlem; cx,cy merkez, s boyut */
function payIcon(x,lvl,cx,cy,s,red){
  var k=s/24;x.save();x.translate(cx-s/2,cy-s/2);x.scale(k,k);
  x.lineCap="round";x.lineJoin="round";x.strokeStyle="#FFFFFF";x.lineWidth=2.4;
  if(lvl===1){x.fillStyle=PAY_RENK.amb;x.beginPath();x.moveTo(12,2.5);x.lineTo(23,21.5);x.lineTo(1,21.5);x.closePath();x.fill();
    x.beginPath();x.moveTo(12,9);x.lineTo(12,15);x.stroke();x.fillStyle="#FFFFFF";x.beginPath();x.arc(12,18.2,1.4,0,Math.PI*2);x.fill()}
  else{x.fillStyle=lvl===2?(red?PAY_RENK.red:PAY_RENK.hi):PAY_RENK.ok;x.beginPath();x.arc(12,12,10,0,Math.PI*2);x.fill();
    if(lvl===2){x.beginPath();x.moveTo(12,6.5);x.lineTo(12,13.5);x.stroke();x.fillStyle="#FFFFFF";x.beginPath();x.arc(12,17.2,1.5,0,Math.PI*2);x.fill()}
    else{x.beginPath();x.moveTo(7,12.5);x.lineTo(10.2,15.7);x.lineTo(17,9);x.stroke()}}
  x.restore();
}
function payFont(x,w,px,hf){x.font=w+" "+px+"px "+(hf?PAY_HF:PAY_BF)}
/* Kartı çizer. L: yerleşim (PAYLAS_AYAR.yerlesim.kare); logo: yüklenmiş görüntü ya da null. Çizilen metinler sırayla döner (test için). */
function payDraw(x,M,L,cfg,logo){
  cfg=cfg||PAYLAS_AYAR;
  var W=L.w,H=L.h,P=L.pad,CW=W-2*P,out=[],R=PAY_RENK;
  function meas(s){return x.measureText(s).width}
  function txt(s,X,Y,col,al){x.fillStyle=col;x.textAlign=al||"left";x.fillText(s,X,Y);out.push(s)}
  x.textBaseline="alphabetic";
  x.fillStyle=R.bg;x.fillRect(0,0,W,H);
  var y=P;
  // 1) Üst satır: tür + ürün adı
  payFont(x,600,30);txt({gida:"GIDA",koz:"KOZMETİK",tem:"TEMİZLİK"}[M.mode]+" · İÇERİK ÖZETİ",P,y+30,R.ok);
  y+=58;
  payFont(x,700,L.ad,true);
  var nl=payWrap(M.name,CW,L.adSatir,meas);
  nl.forEach(function(l){y+=L.ad*1.08;txt(l,P,y,R.ink)});
  y+=44;
  // 2) Sayılar: üç kutu, renk + şekil
  var gap=20,bw=(CW-2*gap)/3,bh=L.sayi+120;
  [[0,M.counts.ok,"özel uyarı yok",R.okbg,R.ok],[1,M.counts.dikkat,"dikkat",R.ambbg,R.amb],[2,M.counts.uyari,"uyarı",R.hibg,R.hi]].forEach(function(b,i){
    var bx=P+i*(bw+gap);x.fillStyle=R.card;payRR(x,bx,y,bw,bh,28);x.fill();
    x.fillStyle=b[3];payRR(x,bx,y,bw,10,0);
    payIcon(x,b[0],bx+48,y+60,44);
    payFont(x,700,L.sayi,true);txt(String(b[1]),bx+bw-32,y+40+L.sayi*0.78,b[1]?b[4]:R.mute,"right");
    payFont(x,600,32);txt(b[2],bx+30,y+bh-32,R.ink);
  });
  y+=bh;
  if(M.unverified){payFont(x,400,28);y+=42;txt(M.unverified+" maddenin durumu doğrulanmadı",P,y,R.mute)}
  y+=44;
  // 3) Öne çıkan maddeler ya da dengeli olumlu kutu
  var foot=H-L.bant,noteY=foot-36,maxY=noteY-94;
  var extra=(M.allergens?L.madde+40:0)+(M.personal.length?60+M.personal.length*52:0);
  var rows=M.top.length,rh=L.maddeSatir;
  if(rows){
    var need=rows*rh+(M.more?56:0)+extra;if(y+need>maxY)rh=Math.max(84,(maxY-y-extra-(M.more?56:0))/rows);
    var bh2=rows*rh+(M.more?56:0)+16;
    x.fillStyle=R.card;payRR(x,P,y,CW,bh2,28);x.fill();
    M.top.forEach(function(it,i){
      var cy=y+8+i*rh+rh/2;
      if(i){x.fillStyle=R.line;x.fillRect(P+32,y+8+i*rh,CW-64,2)}
      payIcon(x,it.lvl,P+60,cy,48);
      // Ad sığmazsa (ör. tehlike ifadesi) daha küçük yazıyla iki satır
      var fw=CW-108-190,fs=L.madde;payFont(x,600,fs);var nm=payWrap(it.name,fw,1,meas);
      if(meas(it.name)>fw&&rh>=96){fs=Math.round(L.madde*0.78);payFont(x,600,fs);nm=payWrap(it.name,fw,2,meas)}
      nm.forEach(function(l,k){txt(l,P+108,cy+fs*0.36+(k-(nm.length-1)/2)*fs*1.12,R.ink)});
      payFont(x,600,30);txt(PAY_LBL[it.lvl],P+CW-36,cy+11,it.lvl===2?R.hi:R.amb,"right");
    });
    if(M.more){payFont(x,400,30);txt("+"+M.more+(M.mode==="tem"?" tane daha":" madde daha"),P+108,y+8+rows*rh+38,R.mute)}
    y+=bh2;
  }else{
    var bh3=196;y+=Math.max(0,(maxY-y-bh3-extra)/3);   // olumlu kutu boşluğa dengeli yerleşir
    x.fillStyle=R.okbg;payRR(x,P,y,CW,bh3,28);x.fill();
    payIcon(x,0,P+76,y+bh3/2,64);
    payFont(x,700,48,true);txt(M.mode==="tem"?"Özel uyarı bulunan ifade yok":"Özel uyarı bulunan madde yok",P+136,y+88,R.ok);
    payFont(x,400,32);txt(M.total?"Okunan "+M.total+" "+(M.mode==="tem"?"bilgide":"maddede")+" dikkat işareti çıkmadı.":"Okunan metinde dikkat işareti çıkmadı.",P+136,y+138,R.ink);
    y+=bh3;
  }
  // 4) Alerjenler (tek satır)
  if(M.allergens){
    y+=40;payFont(x,600,34);var lb="Alerjenler: ";txt(lb,P,y+30,R.ink);var lw=meas(lb);
    payFont(x,400,34);txt(payWrap(M.allergens,CW-lw,1,meas)[0]||"",P+lw,y+30,R.ink);y+=L.madde;
  }
  // Kişisel uyarılar (yalnızca seçilince)
  if(M.personal.length){
    y+=28;var ph=36+M.personal.length*52;
    x.fillStyle=R.redbg;payRR(x,P,y,CW,ph,24);x.fill();x.fillStyle=R.red;x.fillRect(P,y+12,8,ph-24);
    M.personal.forEach(function(p,i){var cy=y+18+i*52+26;payIcon(x,p.lvl,P+50,cy,34,true);payFont(x,600,32);txt(payWrap(p.t,CW-120,1,meas)[0]||"",P+86,cy+11,R.ink)});
    y+=ph;
  }
  // 5) Not ve alt bant
  payFont(x,400,26);var nt=payWrap(cfg.not+" Sonuç yalnızca okunan metne dayanır; miktar bilinmez.",CW,2,meas);
  nt.forEach(function(l,i){txt(l,P,noteY-(nt.length-1-i)*34,R.mute)});
  x.fillStyle=R.ok;x.fillRect(0,foot,W,L.bant);
  var ls=112,ly=foot+(L.bant-ls)/2;
  if(logo){x.save();payRR(x,P,ly,ls,ls,26);x.clip();x.drawImage(logo,P,ly,ls,ls);x.restore()}
  var tx=P+(logo?ls+32:0);
  payFont(x,700,50,true);txt(cfg.uygulamaAdi,tx,ly+48,"#FFFFFF");
  payFont(x,600,34);txt(cfg.slogan,tx,ly+92,R.bant2);
  payFont(x,400,28);txt(cfg.adres.replace(/^https?:\/\//,"").replace(/\/$/,""),W-P,ly+48,R.bant2,"right");
  return out;
}

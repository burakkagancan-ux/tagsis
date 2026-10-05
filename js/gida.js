/* Gıda: E kodu ve bileşen dizini, içerik listesi analizi, özet, marka eşleşmesi. Saf mantık; testler de yükler. */
/* db: e_kodlari.json; bdb: bilesenler.json (isteğe bağlı). Bileşen kimlikleri "B:" ile başlar. */
function capFirst(s){return s&&s.length?s[0].toLocaleUpperCase('tr')+s.slice(1).toLocaleLowerCase('tr'):s}
function buildIndex(db,bdb){
  var exact=new Map(),nos=new Map(),byK={},ks={1:1,2:1,3:1,4:1},byId={},ctx={};
  function add(m,k,id){if(!m.has(k))m.set(k,new Set());m.get(k).add(id)}
  var list=db.ingredients.slice();
  if(bdb)bdb.items.forEach(function(b){list.push({id:"B:"+b.id,bil:b,aliases:b.aliases,short_ok:b.short_ok})});
  list.forEach(function(it){
    byId[it.id]=it.bil?it.bil:it;
    if(it.bil)byId[it.id].isB=true;
    it.aliases.forEach(function(a){
      if(!it.bil&&/^(e[-\s]?\d|ins\s?\d)/.test(a))return;
      var n=norm(a);if(!n||(n.length<3&&!it.short_ok))return;
      add(exact,n,it.id);
      if(n.indexOf(" ")>-1&&n.length>=8)add(nos,n.replace(/ /g,""),it.id);
    });
    (it.context_aliases||[]).forEach(function(c){
      var k=norm(c.alias);(ctx[k]=ctx[k]||{req:c.requires_any.map(norm),ids:[]}).ids.push(it.id);
    });
  });
  var short1=[];   // kısa tek sözcüklü bileşen adları (alerjen, şeker vb.; E kodu adları hariç: "niasin" -> nisin olmasın). Yalnızca tek adayla benzer yazım ("svt" değil, "susarn" -> susam)
  exact.forEach(function(ids,n){var k=n.split(" ").length;ks[k]=1;if(n.length>=8){(byK[k]=byK[k]||[]).push({n:n,ids:Array.from(ids)})}
    if(k===1&&n.length>=4&&n.length<=8&&!/\d/.test(n))short1.push({n:n,ids:Array.from(ids)})});
  var m=(bdb&&bdb.meta)||{};
  return {exact:exact,nos:nos,byK:byK,short1:short1,ks:Object.keys(ks).map(Number),byId:byId,ctx:ctx,
    bmeta:m,may:(m.may_triggers||[]),neg:(m.negations||[]),aromaNext:(m.aroma_next||[])};
}
function codeId(cand,idx){
  var list=[cand];ROMAN.forEach(function(r){if(cand.length-r.length>=4&&cand.slice(-r.length)===r)list.push(cand.slice(0,-r.length))});
  for(var q=0;q<list.length;q++){
    var m=/^e([0-9oli]{3,4})([a-z]?)$/.exec(list[q]);if(!m)continue;
    if((m[1].match(/[0-9]/g)||[]).length<2)continue;
    var digits=m[1].replace(/o/g,"0").replace(/[li]/g,"1");
    var id="E"+digits+m[2];
    if(idx.byId[id])return {id:id,fixed:digits!==m[1]};
  }
  return null;
}
function findCodes(tok,idx){
  var out=[],i,k;
  for(i=0;i<tok.length;i++){
    if(!/^e([0-9oli]|$)/.test(tok[i]))continue;
    if(/^vitamini?$/.test(tok[i-1]||""))continue;
    for(k=2;k>=0;k--){
      if(i+k>=tok.length)continue;
      var part=tok.slice(i,i+k+1);if(hasSep(part))continue;
      var hit=codeId(part.join(""),idx);if(!hit)continue;
      var nx=tok[i+k+1];if(nx&&UNITS[nx])break;
      out.push({a:i,b:i+k+1,ids:[hit.id],how:"kod",fixed:hit.fixed,text:part.join(" ")});
      i+=k;break;
    }
  }
  return out;
}
var OCRDF={"0":"o","1":"l","5":"s","8":"b","6":"g"};
function ocrFixF(w){
  return w.split(" ").map(function(x){
    if(x.indexOf("rn")>-1&&x.indexOf("karnauba")<0)x=x.replace(/rn/g,"m");
    if(/\d/.test(x)&&(x.match(/[a-z]/g)||[]).length>=3)x=x.replace(/\d+(?=[a-z])/g,function(ds){return ds.replace(/\d/g,function(d){return OCRDF[d]||d})});
    return x;
  }).join(" ");
}
function findNames(tok,idx){
  var out=[],i;
  idx.ks.forEach(function(k){
    for(i=0;i+k<=tok.length;i++){
      var part=tok.slice(i,i+k);if(hasSep(part))continue;
      var w=part.join(" "),hit=idx.exact.get(w);
      if(!hit&&k<=4)hit=idx.nos.get(part.join(""));
      if(hit){out.push({a:i,b:i+k,ids:Array.from(hit),how:"isim",text:w});continue}
      var fx=ocrFixF(w);   // sık OCR karışmaları: "rn"->"m", harf arasındaki rakam ("5itrik", "fınd1k")
      if(fx!==w&&(hit=idx.exact.get(fx))){out.push({a:i,b:i+k,ids:Array.from(hit),how:"benzer",text:w,alias:fx});continue}
      if(k===1&&w.length>=5&&w.length<8&&idx.short1){
        var one=null,many=false;
        for(var q0=0;q0<idx.short1.length&&!many;q0++){var c0=idx.short1[q0];
          if((c0.n[0]!==fx[0]&&!(/[il]/.test(c0.n[0])&&/[il]/.test(fx[0])))||Math.abs(c0.n.length-fx.length)>1)continue;
          if(fx.indexOf(c0.n)===0||c0.n.indexOf(fx)===0)continue;   // yalnızca sondaki ek farkı: Türkçe çekim eki olabilir ("alkolü" -> alkol değil)
          if(lev(fx,c0.n,1)===1){if(one&&one.ids.join()!==c0.ids.join())many=true;else one=c0}}
        if(one&&!many&&one.ids.every(function(x){return x.indexOf("B:")===0}))out.push({a:i,b:i+k,ids:one.ids,how:"benzer",text:w,alias:one.n});
        continue;
      }
      var list=idx.byK[k];if(!list||w.length<8)continue;
      var t=w.length>=12?2:1;
      for(var q=0;q<list.length;q++){
        var c=list[q];if(c.n[0]!==w[0]||Math.abs(c.n.length-w.length)>t)continue;
        var d=lev(w,c.n,t);
        if(d>0&&d<=t){out.push({a:i,b:i+k,ids:c.ids,how:"benzer",text:w,alias:c.n});break}
      }
    }
  });
  return out;
}
function findContext(tok,idx){
  var out=[];
  tok.forEach(function(t,i){
    var c=idx.ctx[t];if(!c)return;
    var prev=[];
    for(var j=i-1;j>=0&&prev.length<4;j--){if(tok[j]==="|"||tok[j]===")"||tok[j]===SENT)break;if(SEP[tok[j]])continue;prev.unshift(tok[j])}
    var s=" "+prev.join(" ")+" ";
    if(c.req.some(function(r){return s.indexOf(" "+r+" ")>-1}))out.push({a:i,b:i+1,ids:c.ids.slice(),how:"isim",text:t});
  });
  return out;
}
/* "Eser miktarda ... içerebilir" bölgeleri: token aralıkları [a,b) */
function mayZones(tok,idx){
  var z=[],trig={};idx.may.forEach(function(t){trig[t]=1});
  function sentStart(i){for(var j=i-1;j>=0;j--)if(tok[j]===SENT)return j+1;return 0}
  function sentEnd(i){for(var j=i+1;j<tok.length;j++)if(tok[j]===SENT)return j;return tok.length}
  for(var i=0;i<tok.length;i++){
    var t=tok[i],two=t+" "+(tok[i+1]||"");
    if(t==="eser"){z.push([i,sentEnd(i)]);continue}
    if(trig[two]){var s=sentStart(i),e=sentEnd(i);z.push([Math.max(s,i-12),Math.min(e,i+14)]);continue}
    if(trig[t]){
      var s0=sentStart(i),st=Math.max(s0,i-10);
      for(var j=i-1;j>=s0;j--)if(tok[j]==="eser"){st=j;break}
      z.push([st,i]);
    }
  }
  return z;
}
// Olumsuzluk: madde ile "içermez" arasında geçebilecek sözcükler ve maddeleri bağlayan sözcükler
var NEGFILL={kaynakli:1,madde:1,maddesi:1,maddeler:1,urun:1,urunu:1,urunleri:1,eti:1,turevi:1,turevleri:1,katki:1,katkisi:1,bilesen:1,bileseni:1,hicbir:1,kesinlikle:1,iz:1,miktarda:1};
var NEGJOIN={ve:1,veya:1,ile:1,ya:1,da:1,de:1,hem:1,ne:1,"|":1};
function analyze(text,idx){
  var tok=normText(text).split(" ").filter(Boolean);
  var all=findCodes(tok,idx).concat(findNames(tok,idx),findContext(tok,idx));
  var pr={kod:3,isim:2,benzer:1};
  all.sort(function(x,y){return (y.b-y.a)-(x.b-x.a)||pr[y.how]-pr[x.how]});
  var used={},kept=[];
  all.forEach(function(m){
    for(var i=m.a;i<m.b;i++)if(used[i])return;
    for(i=m.a;i<m.b;i++)used[i]=1;kept.push(m);
  });
  // Besin değerleri tablosu satırı ("Tuz 1,2 g", "Şeker 30 g"): ad + sayı + birim -> bileşen sayılmaz
  kept=kept.filter(function(m){
    if(!/^\d/.test(tok[m.b]||""))return true;
    for(var q=m.b+1;q<=m.b+4&&q<tok.length;q++){if(UNITS[tok[q]])return false;if(!/^\d/.test(tok[q])&&tok[q]!=="|")break}
    return true;
  });
  // İçerik listesindeki sıra (bileşenler çoktan aza yazılır): "İçindekiler:" sonrası, ayraç dışındaki virgüller sayılır
  var st=0;for(var q0=0;q0<tok.length;q0++)if(tok[q0]==="icindekiler"||tok[q0]==="bilesenler"||tok[q0]==="ingredients"){st=q0+1;break}
  kept.forEach(function(m){
    if(m.a<st)return;
    var dep=0,n=1;
    for(var q=st;q<m.a;q++){var t=tok[q];if(t==="(")dep++;else if(t===")")dep=Math.max(0,dep-1);else if(t===SENT&&dep===0){n=0;break}else if(t==="|"&&dep===0)n++}
    if(n)m.ord=n;
  });
  var zones=mayZones(tok,idx),negs={},arn={};
  idx.neg.forEach(function(n){negs[n]=1});idx.aromaNext.forEach(function(n){arn[n]=1});
  kept.forEach(function(m){
    m.may=zones.some(function(z){return m.a>=z[0]&&m.a<z[1]});
    var n1=tok[m.b]||"",n2=tok[m.b+1]||"";
    m.neg=!!(negs[n1]||negs[n1+" "+n2]||(negs[n2]&&!SEP[n1]&&n1!=="ve"));   // iki sözcüklü olumsuzluk: "ilave edilmemiştir"
    if(!m.neg){var q=m.b;while(q<m.b+5&&(NEGFILL[tok[q]]||(NEGJOIN[tok[q]]&&tok[q]!=="|")))q++;m.neg=q>m.b&&!!(negs[tok[q]]||negs[tok[q]+" "+(tok[q+1]||"")])}   // "domuz kaynaklı madde içermez"
    m.aroma=!!(arn[n1]&&m.ids.every(function(id){var it=idx.byId[id];return it.isB&&!it.upf_class}));
  });
  // Sıralı olumsuzluk: "alkol ve domuz içermez", "koruyucu, renklendirici içermez" -> öndeki maddeler de olumsuz.
  // Virgülle bağlı zincir yalnızca içerik listesi dışında ve en çok 4 maddeyse (noktası okunmamış liste sonu yanlışlıkla olumsuz sayılmasın).
  var byPos=kept.slice().sort(function(x,y){return x.a-y.a}),inList=function(a){for(var q=a-1;q>=0&&tok[q]!==SENT;q--)if(tok[q]===":"||tok[q]==="icindekiler"||tok[q]==="bilesenler"||tok[q]==="ingredients")return true;return false};
  for(var k=byPos.length-2;k>=0;k--){
    var m=byPos[k],nx=byPos[k+1];
    if(m.neg||!nx.neg||nx.a<m.b)continue;
    var ok=true,comma=false;
    for(var q=m.b;q<nx.a;q++){if(tok[q]==="|")comma=true;else if(!NEGJOIN[tok[q]]){ok=false;break}}
    if(!ok)continue;
    if(comma){if(inList(m.a))continue;var c=1;for(var j=k+1;j<byPos.length&&byPos[j].neg&&j-k<5;j++)c++;if(c>4)continue}
    m.neg=true;
  }
  var merged={};
  kept.forEach(function(m){
    var key=m.ids.slice().sort().join("+")+"/"+(m.neg?"n":"")+(m.may?"m":"")+(m.aroma?"a":"");
    var cur=merged[key];
    if(!cur||pr[m.how]>pr[cur.how])merged[key]=m;
  });
  var res=Object.keys(merged).map(function(k){
    var m=merged[k],isB=idx.byId[m.ids[0]].isB;
    var lv=isB?-1:Math.max.apply(null,m.ids.map(function(id){return RANK[idx.byId[id].risk_level]}));
    return {ids:m.ids,how:m.how,fixed:!!m.fixed,text:m.text,alias:m.alias,rank:lv,isB:isB,may:m.may,neg:m.neg,aroma:m.aroma,pos:m.a,ord:m.ord};
  });
  res.sort(function(x,y){return y.rank-x.rank||x.pos-y.pos});
  return res;
}
/* Analiz sonucunu özet bilgiye çevirir: şeker, palm, UPF, alerjen, laktoz, vegan, vejetaryen */
function summarize(res,idx){
  var bm=idx.bmeta,upfE=bm.upf_e_categories||{};
  var o={sugar:[],palm:[],upf:{},allergen:{},lactose:{yes:[],low:[],may:[]},vegan:{no:[],unsure:[]},veg:{no:[],insect:[],unsure:[]},claims:[],cancer:[],
    life:{caffeine:[],alcohol:[],alcoholTrace:[],raw:[],honey:[],sweet:[],hyper:[],phe:[],pet:[]},
    sodium:{salt:[],hidden:[],saltOrd:null}};
  var LF=o.life;
  function has(fl,f){return fl.indexOf(f)>-1}
  function al(f,kind,name){var a=o.allergen[f]=o.allergen[f]||{yes:[],may:[]};if(a[kind].indexOf(name)<0)a[kind].push(name)}
  function push(arr,v){if(arr.indexOf(v)<0)arr.push(v)}
  res.forEach(function(r){
    r.ids.forEach(function(id){
      var it=idx.byId[id],name=it.isB?it.name:(it.id+" "+it.primary_name),fl=it.flags||[];
      if(r.neg){push(o.claims,(it.isB?it.name:it.primary_name)+" içermez");return}
      if(!it.isB&&it.reason&&/kanserojen/.test(it.reason)&&!/Grup 3/.test(it.reason))push(o.cancer,{name:name,may:r.may});   // maddenin kendisi IARC 1/2A/2B; benzoatların benzen notu (koşula bağlı) sayılmaz
      if(it.isB){
        if(r.aroma){
          fl.forEach(function(f){if(f.indexOf("allergen_")===0)al(f,"may",name+" (aroma)")});
          if(fl.indexOf("lactose")>-1)push(o.lactose.may,name+" (aroma)");
          if(fl.indexOf("non_vegan")>-1)push(o.vegan.unsure,name+" (aroma)");
          if(fl.indexOf("non_vegetarian")>-1)push(o.veg.unsure,name+" (aroma)");
          return;
        }
        fl.forEach(function(f){if(f.indexOf("allergen_")===0)al(f,r.may?"may":"yes",it.name)});
        if(r.may){if(fl.indexOf("lactose")>-1)push(o.lactose.may,it.name);return}
        if(fl.indexOf("sugar")>-1)o.sugar.push({name:it.name,hidden:fl.indexOf("sugar_hidden")>-1,text:r.text});
        if(fl.indexOf("palm")>-1)push(o.palm,it.name);
        if(it.upf_class)(o.upf[it.upf_class]=o.upf[it.upf_class]||[]).push(capFirst(r.text));
        if(fl.indexOf("lactose")>-1)push(o.lactose.yes,it.name);
        if(fl.indexOf("lactose_low")>-1)push(o.lactose.low,it.name);
        if(fl.indexOf("non_vegan")>-1)push(o.vegan.no,it.name);
        if(fl.indexOf("vegan_suspect")>-1)push(o.vegan.unsure,it.name);
        if(fl.indexOf("non_vegetarian")>-1)push(o.veg.no,it.name);
        if(fl.indexOf("vegetarian_suspect")>-1||fl.indexOf("vegan_suspect")>-1)push(o.veg.unsure,it.name);
        if(has(fl,"caffeine"))push(LF.caffeine,it.name);
        if(has(fl,"alcohol"))push(LF.alcohol,it.name);
        if(has(fl,"alcohol_trace"))push(LF.alcoholTrace,it.name);
        if(has(fl,"raw_milk"))push(LF.raw,it.name);
        if(has(fl,"infant_honey"))push(LF.honey,it.name);
        if(has(fl,"pet_toxic"))push(LF.pet,it.name);
        if(has(fl,"salt")){push(o.sodium.salt,r.text);if(r.ord&&(o.sodium.saltOrd===null||r.ord<o.sodium.saltOrd))o.sodium.saltOrd=r.ord}
        if(has(fl,"sodium_hidden"))push(o.sodium.hidden,it.name);
        if(it.upf_class==="tatlandırıcı")push(LF.sweet,it.name);
      }else{
        var txt=" "+r.text+" ",kind=r.may?"may":"yes";
        if(fl.indexOf("allergen_sulphite")>-1)al("allergen_sulphite",kind,name);
        if(fl.indexOf("allergen_egg")>-1)al("allergen_egg",kind,name);
        if(fl.indexOf("allergen_soy_possible")>-1)al("allergen_soy",txt.indexOf(" soya")>-1?kind:"may",name+(txt.indexOf(" soya")>-1?"":" (kaynağı soya olabilir)"));
        if(r.may)return;
        var cl=upfE[it.category];if(cl)(o.upf[cl]=o.upf[cl]||[]).push(capFirst(it.id));
        if(fl.indexOf("non_vegan")>-1)push(o.vegan.no,name);
        if(fl.indexOf("vegan_suspect")>-1){push(o.vegan.unsure,name);push(o.veg.unsure,name)}
        if(fl.indexOf("insect_derived")>-1)push(o.veg.insect,name);
        else if(fl.indexOf("non_vegetarian")>-1)push(o.veg.no,name);
        if(has(fl,"hyperactivity"))push(LF.hyper,name);
        if(has(fl,"phenylalanine"))push(LF.phe,name);
        if(has(fl,"pet_risk"))push(LF.pet,name);
        if(has(fl,"sodium"))push(o.sodium.hidden,name);
        if(it.category==="Tatlandırıcı")push(LF.sweet,name);
      }
    });
  });
  if(LF.sweet.length>1)LF.sweet=LF.sweet.filter(function(x){return x!=="Tatlandırıcı"});   // genel "tatlandırıcı" sözcüğü, adı geçen tatlandırıcı varken tekrar edilmez
  return o;
}
/* Bakanlık listesindeki marka adlarını metinde arar (yalnızca bilgi amaçlı bağlantı) */
var GENERIC=("sut urunleri urun gida ciftlik ciftligi mandira mandirasi koy koyu koop doga dogal yore yoresel kasap kasabi lokma petek royal elmas zirve sirin damar fidan sacak pelit yildiz makbul gurme baharat baharatlari peynir peyniri sucuk sucugu et eti bal bali zeytinyagi sizma naturel taze tam yagli kasar isil islem gormus ve ltd sti san tic sanayi ticaret limited sirketi organik ev evi evim lezzet lezzeti anadolu ege karadeniz akdeniz altin ozel premium gold super hakiki asil nefis kral sultan saray tatli aile usta has saf tabii kuzu kinali yaylasi yayla yag yagi tereyagi kaymak yogurt ayran helva lokum pekmez tahin firin firini unlu mamulleri kahve cay bitki market gurme lezzetleri kofte doner tavuk dana sigir tadinda tadi kekik oregano zeytin bahcesi keyif zamani dunyasi natural siyah mevsimsel park gross pek ala al guven sera lop i ehl urla binbir since life balance kids hayat ornek harika mutlu cenneti piknik").split(" ");
function buildBrands(tg){
  var stop={},map={};GENERIC.forEach(function(w){stop[w]=1});
  var recs=[];Object.keys(tg.listeler||{}).forEach(function(k){recs=recs.concat(tg.listeler[k]||[])});
  recs.forEach(function(r){[r.FirmaIl,r.FirmaIlce].forEach(function(x){if(x)norm(x).split(" ").forEach(function(w){stop[w]=1})})});
  recs.forEach(function(r){
    var raw=(r.Marka||"").trim();if(!raw||raw==="-")return;
    var w=norm(raw).split(" ").filter(Boolean);if(!w.length)return;
    if(w.length>4)w=w.slice(0,2);
    if(w.every(function(x){return stop[x]||/^\d+$/.test(x)}))return;
    var p=w.join(" ");
    if(w.length===1&&p.length<5)return;
    if(p.length<6&&w.length>1)return;
    var e=map[p]=map[p]||{label:raw,q:w.length>2||raw.length<=40?raw:w.join(" "),n:0};e.n++;
  });
  return map;
}
function findBrands(text,brands){
  var tok=normText(text).split(" ").filter(Boolean).map(function(t){return SEP[t]?"|":t}),s=" "+tok.join(" ")+" ",out=[];
  Object.keys(brands).forEach(function(p){if(s.indexOf(" "+p+" ")>-1)out.push(brands[p])});
  return out;
}

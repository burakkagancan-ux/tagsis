// Arayüz testi: sayfalar gerçek bir tarayıcıda (Chromium, telefon genişliği) açılır ve tıklanır.
// Gerekli: npm i --no-save playwright@1.47.2 && npx playwright install chromium. Çalıştır: node test/arayuz.js
// Denetlenen: konsol hatası yok; üç modda örnek analiz; üç modda karşılaştırma; ansiklopedi renkleri ve arama;
// çevrimdışı açılış (service worker önbelleğinden kozmetik ve temizlik analizi).
const http=require('http'),fs=require('fs'),path=require('path');
const {chromium}=require('playwright');
const R=path.join(__dirname,'..');
const TYPES={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json','.css':'text/css',
  '.png':'image/png','.woff2':'font/woff2','.webmanifest':'application/manifest+json','.svg':'image/svg+xml'};
const server=http.createServer((q,s)=>{
  let p=decodeURIComponent(q.url.split('?')[0]);if(p==='/')p='/index.html';
  const f=path.join(R,p);
  if(!f.startsWith(R)||!fs.existsSync(f)||fs.statSync(f).isDirectory()){s.writeHead(404);return s.end()}
  s.writeHead(200,{'Content-Type':TYPES[path.extname(f)]||'application/octet-stream'});fs.createReadStream(f).pipe(s);
});
let fail=0,n=0;const ok=(c,m)=>{n++;if(!c){fail++;console.log('HATA',m)}};
// Dış adresler (Tesseract CDN, OCR Worker, sayaç) testte engellenir; onların yüklenememesi hata sayılmaz
const external=u=>!/^http:\/\/localhost:/.test(u);
function watch(page,errs){
  page.on('pageerror',e=>errs.push(e.message));
  page.on('console',m=>{if(m.type()==='error'&&!/Failed to load resource|ERR_|net::/.test(m.text()))errs.push(m.text())});
}
async function newPage(ctx){
  const p=await ctx.newPage();
  await p.route('**/*',r=>external(r.request().url())?r.abort():r.continue());
  return p;
}
// Örnek metinle analiz: "Örnek metin dene" düğmesi
async function sample(p,mode){
  await p.click('#m-'+mode);
  await p.evaluate(()=>{HSCAN=true});
  await p.click('#ornek');
  await p.waitForFunction(()=>document.querySelectorAll('#sonuc .res').length>0,null,{timeout:15000});
}
async function scan(p,mode,text){
  await p.click('#m-'+mode);
  await p.evaluate(t=>{HSCAN=true;document.getElementById('metin').value=t;run()},text);
  await p.waitForFunction(()=>document.querySelectorAll('#sonuc .res').length>0,null,{timeout:15000});
}

(async()=>{
  await new Promise(r=>server.listen(0,r));
  const B='http://localhost:'+server.address().port+'/';
  const br=await chromium.launch();
  const opt={viewport:{width:390,height:844},serviceWorkers:'block'};

  // 1) Ana sayfa ve Etiket Oku açılışı
  let ctx=await br.newContext(opt),errs=[],p=await newPage(ctx);watch(p,errs);
  await p.goto(B+'index.html');await p.waitForLoadState('networkidle');
  ok(!errs.length,'index.html konsol hatası: '+errs.join(' | '));errs.length=0;
  await p.goto(B+'ocr.html');await p.waitForFunction(()=>typeof IDX!=='undefined'&&IDX,null,{timeout:15000});

  // 2) Üç modda örnek analiz
  for(const m of ['gida','koz','tem']){
    await sample(p,m);
    ok(await p.$$eval('#sonuc .res',e=>e.length)>2,m+': sonuç kartları');
    ok(await p.isVisible('#sonuc .resbar .pay'),m+': paylaş düğmesi');
  }
  ok(!errs.length,'örnek analiz konsol hatası: '+errs.join(' | '));errs.length=0;

  // 3) Üç modda karşılaştırma: iki tarama, seçim, karar kartı, satırlar, madde alt sayfası
  const pairs={
    gida:['İçindekiler: Şeker, kakao, E322.','İçindekiler: Şeker, kakao, E250.','A'],
    koz:['Ingredients: Aqua, Glycerin, Parfum, Linalool, Phenoxyethanol.','Ingredients: Aqua, Glycerin, Butylphenyl Methylpropional, Phenoxyethanol.','A'],
    tem:['İçindekiler: %5-15 anyonik yüzey aktif maddeler, parfüm. DİKKAT. Cilt tahrişine yol açar.','İçindekiler: %5-15 anyonik yüzey aktif maddeler. TEHLİKE. Ciddi göz hasarına yol açar.','A']};
  for(const m of Object.keys(pairs)){
    // Mod değişince kutudaki metin o modda yeniden analiz edilir; temiz başlangıç için kutu ve geçmiş boşaltılır
    await p.evaluate(()=>{document.getElementById('metin').value='';localStorage.removeItem('taramalar')});
    await scan(p,m,pairs[m][0]);await scan(p,m,pairs[m][1]);
    ok(await p.isVisible('#karsla'),m+': Karşılaştır düğmesi görünür');
    await p.click('#karsla');
    const items=await p.$$('#sheet .kpick button.kitem');
    ok(items.length===2,m+': seçim listesinde yalnızca bu türün 2 taraması var ('+items.length+')');
    for(const it of items)if(await it.getAttribute('aria-pressed')!=='true')await it.click();
    await p.click('#sheet .kpick button:not(.kitem):not(.kclr)');
    await p.waitForSelector('#kars:not([hidden]) .kdec');
    const first=(await p.$$eval('#kars .kn',e=>e.map(x=>x.value)))[0];
    ok((await p.textContent('#kars .kdec .t')).indexOf(first+' içerik açısından daha iyi')===0,m+': ilk (risksiz) ürün öne çıkar');
    ok(await p.$$eval('#kars .ktab .kl',e=>e.length)>=7,m+': satır tablosu');
    await p.click('#kars details.kgrp summary');
    await p.click('#kars details.kgrp[open] button.kmad');
    ok(await p.isVisible('#sheet .sheet-pn'),m+': maddeye dokununca alt sayfa açılır');
    await p.evaluate(()=>{closeSheet();closeCompare()});
  }
  await p.click('#m-gida');await p.evaluate(()=>{localStorage.removeItem('taramalar')});await p.click('#karsla');
  ok(/en az iki gıda ürünü/.test(await p.textContent('#st')),'tek tarama yokken uyarı');
  ok(!errs.length,'karşılaştırma konsol hatası: '+errs.join(' | '));errs.length=0;

  // 4) Ansiklopedi: renk kuralı (yeşil yalnızca doğal üretimde), arama
  for(const [id,cls] of [['E322','green'],['E162','green'],['E330','green n'],['E250','amber'],['E553b','amber']]){
    await p.goto(B+'ansiklopedi.html?id='+id);await p.waitForSelector('#ana .risk');
    const c=await p.getAttribute('#ana .risk','class');
    ok(c.split(' ').slice(2).join(' ')===cls,id+' risk kartı sınıfı "'+c+'", beklenen '+cls);
  }
  await p.goto(B+'ansiklopedi.html');await p.waitForSelector('#ara');await p.fill('#ara','lesitin');
  // Arama kutusu boşken bütün elle incelenmiş maddeler listelenir; arama sonucu gelince liste kısalır
  await p.waitForFunction(()=>{const n=document.querySelectorAll('#ana a.row').length;return n>0&&n<50},null,{timeout:10000});
  {const f=await p.$$eval('#ana a.row .rc',e=>e.map(x=>x.textContent));ok(f[0]==='E322','ansiklopedi araması: '+f.slice(0,5).join(','))}
  ok(!errs.length,'ansiklopedi konsol hatası: '+errs.join(' | '));errs.length=0;
  await ctx.close();

  // 5) Çevrimdışı: service worker önbelleği dolunca sunucu kapatılır (ctx.setOffline service worker isteklerini kesmiyor);
  //    sayfa yeniden yüklenir, üç modda analiz önbellekten çalışmalı. Kozmetik ve temizlik verisi bu modlara hiç girilmeden önbellekte olmalı.
  // Bu bölümde istek yönlendirme kullanılmaz: yönlendirme açıkken service worker sayfayı denetlemez
  ctx=await br.newContext({viewport:opt.viewport});p=await ctx.newPage();watch(p,errs);
  await p.goto(B+'ocr.html');
  const need=['data/kozmetik.json','data/kozmetik_inci.json','data/temizlik.json','data/eslesmeler.json'];
  let have=[];
  for(let i=0;i<60;i++){   // waitForFunction async işlevi beklemez; elle yoklanır
    have=await p.evaluate(async need=>{const r=await navigator.serviceWorker.getRegistration();if(!r||!r.active||!navigator.serviceWorker.controller)return [];
      const out=[];for(const k of await caches.keys()){const c=await caches.open(k);for(const f of need)if(await c.match(f))out.push(f)}return out},need);
    if(need.every(f=>have.includes(f)))break;await p.waitForTimeout(500);
  }
  need.forEach(f=>ok(have.includes(f),'kurulumda önbelleğe alınmadı: '+f));
  await new Promise(r=>{server.close(r);server.closeAllConnections()});
  await p.reload();await p.waitForFunction(()=>typeof IDX!=='undefined'&&IDX,null,{timeout:15000});
  for(const m of ['koz','tem','gida']){
    try{await sample(p,m);ok(await p.$$eval('#sonuc .res',e=>e.length)>2,'çevrimdışı '+m+' analizi')}
    catch(e){ok(false,'çevrimdışı '+m+' analizi: '+(await p.textContent('#sonuc')).slice(0,80))}
  }
  ok(!errs.length,'çevrimdışı konsol hatası: '+errs.join(' | '));
  await ctx.close();

  await br.close();
  console.log(n+' arayüz denetimi, '+fail+' hata');process.exit(fail?1:0);
})().catch(e=>{console.log('HATA',e.message);process.exit(1)});

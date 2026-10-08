// Çevrimdışı açılış: sayfaların ve arayüz kodunun yüklediği her yerel dosya sw.js CORE listesinde olmalı. Çalıştır: node test/onbellek.js
const fs=require('fs'),path=require('path'),R=path.join(__dirname,'..');
let fail=0,n=0;const ok=(c,m)=>{n++;if(!c){fail++;console.log('HATA',m)}};
const sw=fs.readFileSync(path.join(R,'sw.js'),'utf8'),core=new Set((/const CORE = \[([\s\S]*?)\];/.exec(sw)[1].match(/"([^"]+)"/g)||[]).map(s=>s.slice(1,-1)));
const want=new Set();
['index.html','ocr.html','ansiklopedi.html'].forEach(p=>{
  want.add(p);
  for(const m of fs.readFileSync(path.join(R,p),'utf8').matchAll(/(?:src|href)="((?:js|fonts|data)\/[^"]+|[a-z_]+\.(?:css|webmanifest))"/g))want.add(m[1]);
});
fs.readdirSync(path.join(R,'js')).forEach(f=>{
  for(const m of fs.readFileSync(path.join(R,'js',f),'utf8').matchAll(/"(data\/[a-z_]+\.json)"/g))want.add(m[1]);
});
// Dil dosyaları (i18n/*.json, i18n/veri/*.json) dinamik yüklenir; hepsi önbellekte olmalı
['i18n',path.join('i18n','veri')].forEach(d=>{const D=path.join(R,d);if(fs.existsSync(D))fs.readdirSync(D).filter(f=>f.endsWith('.json')).forEach(f=>want.add(d.replace(/\\/g,'/')+'/'+f))});
want.forEach(f=>{ok(core.has(f),'sw.js CORE listesinde yok: '+f);ok(fs.existsSync(path.join(R,f)),'dosya yok: '+f)});
core.forEach(f=>{if(f!=='./')ok(fs.existsSync(path.join(R,f)),'CORE listesindeki dosya yok: '+f)});
console.log(n+' önbellek denetimi, '+fail+' hata');process.exit(fail?1:0);

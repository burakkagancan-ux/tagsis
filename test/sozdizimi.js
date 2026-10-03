// HTML sayfalarındaki satır içi <script> bloklarının sözdizimi denetimi (arayüz kodu node testlerinde çalışmadığı için).
// Çalıştır: node test/sozdizimi.js
const fs=require('fs');let fail=0,n=0;
for(const f of ['ocr.html','index.html']){
  const h=fs.readFileSync(__dirname+'/../'+f,'utf8');
  [...h.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].forEach((m,i)=>{n++;try{new Function(m[1])}catch(e){fail++;console.log('HATA',f,'script',i,e.message)}});
}
console.log(n+' script bloğu, '+fail+' hata');process.exit(fail?1:0);

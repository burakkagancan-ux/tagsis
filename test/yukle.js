// ocr.html'nin saf mantık dosyalarını (js/) sayfadaki sırayla birleştirir; testler bu metni eval ile yükler.
const fs=require('fs');
module.exports=['ortak','gida','kozmetik','eslesme','temizlik','karsilastir_ayar','karsilastir','paylas_ayar','paylas'].map(f=>fs.readFileSync(__dirname+'/../js/'+f+'.js','utf8')).join('\n');

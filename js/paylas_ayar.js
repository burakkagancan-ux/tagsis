/* Paylaşılabilir sonuç kartı: ayarlar. Uygulama adı, adres ve kart metinleri yalnızca buradan okunur.
   Özelliği kapatmak için acik:false yapın; sonuç ekranındaki paylaş düğmesi görünmez. */
var PAYLAS_AYAR={
  acik:true,
  uygulamaAdi:"Tağşiş",                                    // kesinleşince yalnızca burası değişir
  adres:"https://burakkagancan-ux.github.io/tagsis/",      // mağaza bağlantısı olunca burası değişir
  slogan:"İçinde ne var? Sen de tara",
  not:"Bilgilendirme amaçlıdır.",
  logo:"icon-192.png",
  enFazlaMadde:3,          // kartta gösterilen en riskli madde sayısı
  enFazlaKisisel:2,        // "Kişisel uyarılarımı ekle" açıkken en fazla satır
  sayac:"/sayac",          // anonim paylaşım sayacı: OCR Worker adresine eklenir; boş bırakılırsa sayılmaz
  boyut:"kare",            // varsayılan yerleşim
  yerlesim:{               // yeni boyut (ör. hikâye 1080x1920) buraya bir kayıt olarak eklenir
    kare:{w:1080,h:1350,pad:80,ad:76,adSatir:2,sayi:92,madde:44,maddeSatir:116,bant:220}
  }
};

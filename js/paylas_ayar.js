/* Paylaşılabilir sonuç kartı: ayarlar. Uygulama adı, adres ve kart metinleri yalnızca buradan okunur.
   Özelliği kapatmak için acik:false yapın; sonuç ekranındaki paylaş düğmesi görünmez. */
var PAYLAS_AYAR={
  acik:true,
  uygulamaAdi:"Tağşiş",                                    // kesinleşince yalnızca burası değişir
  adres:"https://burakkagancan-ux.github.io/tagsis/",      // mağaza bağlantısı olunca burası değişir
  slogan:"İçinde ne var? Sen de tara",
  not:"Bilgilendirme amaçlıdır.",
  logo:"icon-192.png",
  enFazlaMadde:3,          // kartta gösterilen en riskli madde sayısı (yerleşimde enFazlaMadde varsa o geçerli)
  enFazlaKisisel:2,        // "Kişisel uyarılarımı ekle" açıkken en fazla satır
  sayac:"/sayac",          // anonim paylaşım sayacı: OCR Worker adresine eklenir; boş bırakılırsa sayılmaz
  boyut:"hikaye",           // varsayılan yerleşim; kullanıcı paylaşım ekranında değiştirebilir (localStorage "pay_boyut")
  yerlesim:{               // yeni boyut buraya bir kayıt olarak eklenir; etiket: seçicide görünen ad
    hikaye:{etiket:"Hikâye",w:1080,h:1920,pad:80,ad:84,adSatir:2,sayi:104,madde:44,maddeSatir:132,bant:240,enFazlaMadde:6},
    kare:{etiket:"Gönderi",w:1080,h:1350,pad:72,ad:68,adSatir:2,sayi:72,kutuTek:true,madde:38,maddeSatir:108,bant:180,enFazlaMadde:3}
  }
};

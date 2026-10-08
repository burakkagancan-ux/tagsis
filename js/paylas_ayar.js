/* Paylaşılabilir sonuç kartı: ayarlar. Uygulama adı ve adres yalnızca buradan okunur; slogan ve not dil dosyasında (pay.slogan, pay.not).
   Özelliği kapatmak için acik:false yapın; sonuç ekranındaki paylaş düğmesi görünmez. */
var PAYLAS_AYAR={
  acik:true,
  uygulamaAdi:"Tağşiş",                                    // kesinleşince yalnızca burası değişir
  adres:"https://burakkagancan-ux.github.io/tagsis/",      // mağaza bağlantısı olunca burası değişir
  get slogan(){return t("pay.slogan")},
  get not(){return t("pay.not")},
  logo:"icon-192.png",
  enFazlaMadde:3,          // kartta gösterilen en riskli madde sayısı (yerleşimde enFazlaMadde varsa o geçerli)
  enFazlaKisisel:2,        // "Kişisel uyarılarımı ekle" açıkken en fazla satır
  sayac:"/sayac",          // anonim paylaşım sayacı: OCR Worker adresine eklenir; boş bırakılırsa sayılmaz
  boyut:"hikaye",          // kart her zaman büyük boyutta (1080x1920) çizilir
  yerlesim:{               // yeni boyut buraya bir kayıt olarak eklenir; birden fazla kayıt olursa paylaşım ekranında seçici çıkar
    // bant: alttaki ince uygulama bandının yüksekliği (eski büyük bant 240 idi; boşalan yer içeriğe verildi)
    hikaye:{get etiket(){return t("pay.boyut.hikaye")},w:1080,h:1920,pad:80,ad:84,adSatir:2,sayi:104,madde:44,maddeSatir:132,bant:120,enFazlaMadde:7}
  }
};

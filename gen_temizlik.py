# -*- coding: utf-8 -*-
"""Temizlik ürünleri verisi: data/temizlik.json

Üç katman:
  hazards  : CLP / SEA zararlılık ifadeleri (H ve EUH). Etikette kodla ya da metinle yazılır.
  groups   : AB 648/2004 Ek VII A (TR Deterjanlar Hakkında Yönetmelik Ek-7) içerik grupları; yüzde bandıyla yazılır.
  subs     : Temizlik ürününde ayrıca not gerektiren, INCI adıyla yazılan maddeler (koruyucu, çamaşır suyu, asit, amonyak, enzim).
Koku alerjenleri ve diğer koruyucular kozmetik INCI dizininden (kozmetik.json, kozmetik_inci.json) tanınır.

Renk kararı (kullanıcı, 04.10.2026): ciddi tehlike (yanık, ciddi göz hasarı, zehirlilik, CMR, solunum hassaslaşması) kırmızı;
diğer sağlık uyarıları sarı; bilgi gri. Kırmızı burada "yasak" değil, ürünün resmi tehlike sınıfıdır.
Çalıştır: python3 gen_temizlik.py   (gen_kozmetik.py'den sonra; INCI adlarını kozmetik_inci.json ile denetler)
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "temizlik.json")
VERSION = "0.1.0"
LAST_UPDATED = "2026-10-04"

CLP = "https://eur-lex.europa.eu/eli/reg/2008/1272/oj"
H_TR = "https://www.crad.com.tr/UPLOAD/URUN/FILES/Hcode-17140911685.pdf"
EUH_LIST = "https://www.comunidad.madrid/sites/default/files/doc/sanidad/samb/frases_euh_2024.pdf"
DET = "https://www.legislation.gov.uk/eur/2004/648/annex/VII"
DET_TR = "https://www.lexpera.com.tr/mevzuat/yonetmelikler/deterjanlar-hakkinda-yonetmelik-1"
SB_REHBER = "https://hsgm.saglik.gov.tr/depo/birimler/kronik-hastaliklar-ve-yasli-sagligi-db/Dokumanlar/Kitaplar/Saglikli_Temizlik_Rehberi_18.04.2022.pdf"
ECHA_CL = "https://echa.europa.eu/information-on-chemicals/cl-inventory-database"
COSING = "https://ec.europa.eu/growth/tools-databases/cosing/"

# ---------------------------------------------------------------------------
# Zararlılık ifadeleri. [kod, seviye, grup, TR metin, EN metin, sade açıklama]
# Gruplar: cilt_goz, solunum, yutma, zehir, cmr, organ, cevre, fiziksel, karistirma, diger
# TR metinleri: H için SEA Yönetmeliği (RG 11.12.2013, 28848) Ek-3'e dayalı liste (CRAD); EUH için Claude çevirisi (needs_review).
# ---------------------------------------------------------------------------
R, Y, I = "red", "yellow", "info"
H = [
 ["H200", Y, "fiziksel", "Kararsız patlayıcı.", "Unstable explosive.", ""],
 ["H201", Y, "fiziksel", "Patlayıcı; kütlesel patlama zararı.", "Explosive; mass explosion hazard.", ""],
 ["H202", Y, "fiziksel", "Patlayıcı; ciddi yansıtım zararı.", "Explosive; severe projection hazard.", ""],
 ["H203", Y, "fiziksel", "Patlayıcı; yangın, patlama veya yansıtım zararı.", "Explosive; fire, blast or projection hazard.", ""],
 ["H204", Y, "fiziksel", "Yangın veya yansıtım zararı.", "Fire or projection hazard.", ""],
 ["H205", Y, "fiziksel", "Yangında kütlesel patlamaya yol açabilir.", "May mass explode in fire.", ""],
 ["H220", Y, "fiziksel", "Çok kolay alevlenir gaz.", "Extremely flammable gas.", ""],
 ["H221", Y, "fiziksel", "Alevlenir gaz.", "Flammable gas.", ""],
 ["H222", Y, "fiziksel", "Çok kolay alevlenir aerosol.", "Extremely flammable aerosol.", "Sprey kolayca alev alır; ateş ve sıcak yüzeylerden uzak tutulmalı."],
 ["H223", Y, "fiziksel", "Alevlenir aerosol.", "Flammable aerosol.", "Sprey alev alabilir."],
 ["H224", Y, "fiziksel", "Çok kolay alevlenir sıvı ve buhar.", "Extremely flammable liquid and vapour.", "Sıvı ve buharı çok kolay alev alır."],
 ["H225", Y, "fiziksel", "Kolay alevlenir sıvı ve buhar.", "Highly flammable liquid and vapour.", "Sıvı ve buharı kolay alev alır (ör. alkollü temizleyiciler)."],
 ["H226", Y, "fiziksel", "Alevlenir sıvı ve buhar.", "Flammable liquid and vapour.", "Sıvı ve buharı alev alabilir."],
 ["H228", Y, "fiziksel", "Alevlenir katı.", "Flammable solid.", ""],
 ["H229", Y, "fiziksel", "Basınçlı kap. Isıtma patlamaya yol açabilir.", "Pressurised container: may burst if heated.", "Basınçlı kutu; ısınırsa patlayabilir."],
 ["H230", Y, "fiziksel", "Hava olmadığında bile patlayabilir.", "May react explosively even in the absence of air.", ""],
 ["H231", Y, "fiziksel", "Yüksek basınçta ve/veya sıcaklıkta, hava olmadığında bile, patlayabilir.", "May react explosively even in the absence of air at elevated pressure and/or temperature.", ""],
 ["H240", Y, "fiziksel", "Isıtma patlamaya yol açabilir.", "Heating may cause an explosion.", ""],
 ["H241", Y, "fiziksel", "Isıtma yangına veya patlamaya yol açabilir.", "Heating may cause a fire or explosion.", ""],
 ["H242", Y, "fiziksel", "Isıtma yangına yol açabilir.", "Heating may cause a fire.", ""],
 ["H250", Y, "fiziksel", "Hava ile temas ettiğinde ani yangınlara yol açabilir.", "Catches fire spontaneously if exposed to air.", ""],
 ["H251", Y, "fiziksel", "Kendiliğinden ısınır; alev alabilir.", "Self-heating: may catch fire.", ""],
 ["H252", Y, "fiziksel", "Büyük miktarlarda kendiliğinden ısınır; yangına yol açabilir.", "Self-heating in large quantities; may catch fire.", ""],
 ["H260", Y, "fiziksel", "Su ile temas ettiğinde kendiliğinden tutuşabilen alevlenir gazlar yayar.", "In contact with water releases flammable gases which may ignite spontaneously.", ""],
 ["H261", Y, "fiziksel", "Su ile temas ettiğinde alevlenir gazlar yayar.", "In contact with water releases flammable gas.", ""],
 ["H270", Y, "fiziksel", "Yangına yol açabilir veya yangını şiddetlendirebilir; oksitleyici.", "May cause or intensify fire; oxidiser.", ""],
 ["H271", Y, "fiziksel", "Yangına veya patlamaya yol açabilir; güçlü oksitleyici.", "May cause fire or explosion; strong oxidiser.", "Güçlü oksitleyici; yanıcı maddelerle temas ederse yangın çıkarabilir."],
 ["H272", Y, "fiziksel", "Yangını güçlendirebilir; oksitleyici.", "May intensify fire; oxidiser.", "Oksitleyici (ör. oksijenli ağartıcı tozlar); yangını büyütebilir."],
 ["H280", Y, "fiziksel", "Basınçlı gaz içerir; ısıtıldığında patlayabilir.", "Contains gas under pressure; may explode if heated.", ""],
 ["H281", Y, "fiziksel", "Soğutulmuş gaz içerir; soğuktan yanma veya yaralanmalara yol açabilir.", "Contains refrigerated gas; may cause cryogenic burns or injury.", ""],
 ["H290", I, "fiziksel", "Metalleri aşındırabilir.", "May be corrosive to metals.", "Metal yüzeyleri ve ambalajı aşındırabilir; insan sağlığına ilişkin bir sınıf değildir."],
 ["H300", R, "zehir", "Yutulması halinde öldürücüdür.", "Fatal if swallowed.", "Yutulursa öldürücü olabilir."],
 ["H301", R, "zehir", "Yutulması halinde toksiktir.", "Toxic if swallowed.", "Yutulursa ciddi zehirlenme yapabilir."],
 ["H302", Y, "yutma", "Yutulması halinde zararlıdır.", "Harmful if swallowed.", "Yutulursa zehirlenme belirtileri yapabilir; çocukların erişiminden uzak tutulması bu yüzden önemlidir."],
 ["H304", R, "yutma", "Solunum yoluna nüfuzu ve yutulması halinde öldürücü olabilir.", "May be fatal if swallowed and enters airways.", "Yutulduktan sonra akciğere kaçarsa (ör. kusarken) öldürücü olabilir. Bu tür ürünlerde kusturmaya çalışılmaz."],
 ["H310", R, "zehir", "Cilt ile teması halinde öldürücüdür.", "Fatal in contact with skin.", ""],
 ["H311", R, "zehir", "Cilt ile teması halinde toksiktir.", "Toxic in contact with skin.", ""],
 ["H312", Y, "cilt_goz", "Cilt ile teması halinde zararlıdır.", "Harmful in contact with skin.", ""],
 ["H314", R, "cilt_goz", "Ciddi cilt yanıklarına ve göz hasarına yol açar.", "Causes severe skin burns and eye damage.", "Aşındırıcı: cilde ve göze temas ederse yanık ve kalıcı hasar oluşturabilir (ör. lavabo açıcı, bazı kireç çözücüler)."],
 ["H315", Y, "cilt_goz", "Cilt tahrişine yol açar.", "Causes skin irritation.", "Ciltte kızarıklık ve tahriş yapabilir."],
 ["H317", Y, "cilt_goz", "Alerjik cilt reaksiyonlarına yol açabilir.", "May cause an allergic skin reaction.", "Bazı kişilerde ciltte alerji (temas egzaması) başlatabilir."],
 ["H318", R, "cilt_goz", "Ciddi göz hasarına yol açar.", "Causes serious eye damage.", "Göze kaçarsa kalıcı hasar oluşturabilir (çamaşır ve bulaşık deterjanlarında, kapsüllerde sık görülür)."],
 ["H319", Y, "cilt_goz", "Ciddi göz tahrişine yol açar.", "Causes serious eye irritation.", "Göze kaçarsa tahriş eder; genellikle geçicidir."],
 ["H330", R, "zehir", "Solunması halinde öldürücüdür.", "Fatal if inhaled.", ""],
 ["H331", R, "zehir", "Solunması halinde toksiktir.", "Toxic if inhaled.", ""],
 ["H332", Y, "solunum", "Solunması halinde zararlıdır.", "Harmful if inhaled.", "Buharı ya da spreyi solunursa zararlıdır."],
 ["H334", R, "solunum", "Solunması halinde nefes alma zorlukları, astım nöbetleri veya alerjiye yol açabilir.", "May cause allergy or asthma symptoms or breathing difficulties if inhaled.", "Solunum yolu hassaslaştırıcı: solunduğunda alerji ve astım benzeri nefes darlığı başlatabilir."],
 ["H335", Y, "solunum", "Solunum yolu tahrişine yol açabilir.", "May cause respiratory irritation.", "Buharı ya da tozu burnu ve boğazı tahriş edebilir."],
 ["H336", Y, "solunum", "Rehavete veya baş dönmesine yol açabilir.", "May cause drowsiness or dizziness.", "Buharı solunduğunda uyuşukluk ve baş dönmesi yapabilir."],
 ["H340", R, "cmr", "Genetik hasara yol açabilir.", "May cause genetic defects.", ""],
 ["H341", R, "cmr", "Genetik hasara yol açma şüphesi var.", "Suspected of causing genetic defects.", ""],
 ["H350", R, "cmr", "Kansere yol açabilir.", "May cause cancer.", ""],
 ["H350i", R, "cmr", "Solunması halinde kansere yol açabilir.", "May cause cancer by inhalation.", ""],
 ["H351", R, "cmr", "Kansere yol açma şüphesi var.", "Suspected of causing cancer.", ""],
 ["H360", R, "cmr", "Doğmamış çocukta hasara yol açabilir veya üremeye zarar verebilir.", "May damage fertility or the unborn child.", ""],
 ["H360F", R, "cmr", "Üremeye zarar verebilir.", "May damage fertility.", ""],
 ["H360D", R, "cmr", "Doğmamış çocukta hasara yol açabilir.", "May damage the unborn child.", ""],
 ["H360FD", R, "cmr", "Üremeye zarar verebilir. Doğmamış çocukta hasara yol açabilir.", "May damage fertility. May damage the unborn child.", ""],
 ["H360Fd", R, "cmr", "Üremeye zarar verebilir. Doğmamış çocukta hasara yol açma şüphesi var.", "May damage fertility. Suspected of damaging the unborn child.", ""],
 ["H360Df", R, "cmr", "Doğmamış çocukta hasara yol açabilir. Üremeye zarar verme şüphesi var.", "May damage the unborn child. Suspected of damaging fertility.", ""],
 ["H361", R, "cmr", "Doğmamış çocukta hasara yol açma veya üremeye zarar verme şüphesi var.", "Suspected of damaging fertility or the unborn child.", ""],
 ["H361f", R, "cmr", "Üremeye zarar verme şüphesi var.", "Suspected of damaging fertility.", ""],
 ["H361d", R, "cmr", "Doğmamış çocukta hasara yol açma şüphesi var.", "Suspected of damaging the unborn child.", ""],
 ["H361fd", R, "cmr", "Üremeye zarar verme şüphesi var. Doğmamış çocukta hasara yol açma şüphesi var.", "Suspected of damaging fertility. Suspected of damaging the unborn child.", ""],
 ["H362", R, "cmr", "Emzirilen çocuğa zarar verebilir.", "May cause harm to breast-fed children.", ""],
 ["H370", R, "organ", "Organlarda hasara yol açar.", "Causes damage to organs.", ""],
 ["H371", Y, "organ", "Organlarda hasara yol açabilir.", "May cause damage to organs.", ""],
 ["H372", R, "organ", "Uzun süreli veya tekrarlı maruz kalma sonucu organlarda hasara yol açar.", "Causes damage to organs through prolonged or repeated exposure.", ""],
 ["H373", Y, "organ", "Uzun süreli veya tekrarlı maruz kalma sonucu organlarda hasara yol açabilir.", "May cause damage to organs through prolonged or repeated exposure.", ""],
 ["H400", Y, "cevre", "Sucul ortamda çok toksiktir.", "Very toxic to aquatic life.", "Suda yaşayan canlılar için çok zehirli olarak sınıflandırılmış."],
 ["H410", Y, "cevre", "Sucul ortamda uzun süre kalıcı, çok toksik etki.", "Very toxic to aquatic life with long lasting effects.", "Suda yaşayan canlılar için çok zehirli ve etkisi uzun süreli."],
 ["H411", Y, "cevre", "Sucul ortamda uzun süre kalıcı, toksik etki.", "Toxic to aquatic life with long lasting effects.", "Suda yaşayan canlılar için zehirli ve etkisi uzun süreli."],
 ["H412", Y, "cevre", "Sucul ortamda uzun süre kalıcı, zararlı etki.", "Harmful to aquatic life with long lasting effects.", "Suda yaşayan canlılar için zararlı ve etkisi uzun süreli."],
 ["H413", Y, "cevre", "Sucul ortamda uzun süre kalıcı, zararlı etki yapabilir.", "May cause long lasting harmful effects to aquatic life.", "Suda yaşayan canlılarda uzun süreli zararlı etki yapabilir."],
 ["H420", Y, "cevre", "Atmosferin üst katmanındaki ozon tabakasını tahrip ederek kamu sağlığına ve çevreye zarar verir.", "Harms public health and the environment by destroying ozone in the upper atmosphere.", ""],
]
# Birleşik ifadeler (etikette tek cümle olarak yazılır): [kodlar, TR, EN]
HCOMB = [
 [["H300", "H310"], "Yutulması halinde veya ciltle teması halinde öldürücüdür.", "Fatal if swallowed or in contact with skin."],
 [["H300", "H330"], "Yutulduğunda veya solunduğunda öldürücüdür.", "Fatal if swallowed or if inhaled."],
 [["H310", "H330"], "Ciltle temas ettiğinde veya solunduğunda öldürücüdür.", "Fatal in contact with skin or if inhaled."],
 [["H300", "H310", "H330"], "Yutulduğunda, ciltle temas ettiğinde veya solunduğunda öldürücüdür.", "Fatal if swallowed, in contact with skin or if inhaled."],
 [["H301", "H311"], "Yutulması halinde veya ciltle teması halinde toksiktir.", "Toxic if swallowed or in contact with skin."],
 [["H301", "H331"], "Yutulduğunda veya solunduğunda toksiktir.", "Toxic if swallowed or if inhaled."],
 [["H311", "H331"], "Cilt ile teması halinde veya solunduğunda toksiktir.", "Toxic in contact with skin or if inhaled."],
 [["H301", "H311", "H331"], "Yutulduğunda, ciltle temas ettiğinde veya solunduğunda toksiktir.", "Toxic if swallowed, in contact with skin or if inhaled."],
 [["H302", "H312"], "Yutulması halinde veya ciltle teması halinde zararlıdır.", "Harmful if swallowed or in contact with skin."],
 [["H302", "H332"], "Yutulduğunda veya solunduğunda zararlıdır.", "Harmful if swallowed or if inhaled."],
 [["H312", "H332"], "Ciltle temas ettiğinde veya solunduğunda zararlıdır.", "Harmful in contact with skin or if inhaled."],
 [["H302", "H312", "H332"], "Yutulduğunda, ciltle temas ettiğinde veya solunduğunda zararlıdır.", "Harmful if swallowed, in contact with skin or if inhaled."],
]
# EK zararlılık ifadeleri (CLP Ek II ve Ek III Bölüm 2-3). TR metinleri çeviri (needs_review).
EUH = [
 ["EUH014", Y, "fiziksel", "Su ile şiddetli reaksiyona girer.", "Reacts violently with water.", ""],
 ["EUH018", Y, "fiziksel", "Kullanım sırasında alevlenir/patlayıcı buhar-hava karışımı oluşturabilir.", "In use may form flammable/explosive vapour-air mixture.", ""],
 ["EUH019", Y, "fiziksel", "Patlayıcı peroksitler oluşturabilir.", "May form explosive peroxides.", ""],
 ["EUH044", Y, "fiziksel", "Kapalı ortamda ısıtılırsa patlama riski vardır.", "Risk of explosion if heated under confinement.", ""],
 ["EUH029", Y, "karistirma", "Su ile temas ettiğinde toksik gaz açığa çıkarır.", "Contact with water liberates toxic gas.", "Su ile temas ederse zehirli gaz açığa çıkar."],
 ["EUH031", Y, "karistirma", "Asitlerle temas ettiğinde toksik gaz açığa çıkarır.", "Contact with acids liberates toxic gas.", "Asitli bir ürünle (ör. tuz ruhu, kireç çözücü) temas ederse zehirli gaz açığa çıkar. Çamaşır suyunda sık görülür."],
 ["EUH032", Y, "karistirma", "Asitlerle temas ettiğinde çok toksik gaz açığa çıkarır.", "Contact with acids liberates very toxic gas.", "Asitli bir ürünle temas ederse çok zehirli gaz açığa çıkar."],
 ["EUH066", Y, "cilt_goz", "Tekrarlı maruz kalmalarda ciltte kuruluğa ve çatlaklara neden olabilir.", "Repeated exposure may cause skin dryness or cracking.", "Sık temasta cildi kurutup çatlatabilir."],
 ["EUH070", R, "cilt_goz", "Gözle temas ettiğinde toksiktir.", "Toxic by eye contact.", ""],
 ["EUH071", R, "solunum", "Solunum yolu için aşındırıcıdır.", "Corrosive to the respiratory tract.", "Solunduğunda solunum yolunda aşındırıcı hasar yapabilir."],
 ["EUH201", Y, "diger", "Kurşun içerir. Çocukların çiğneyebileceği veya emebileceği yüzeylerde kullanılmamalıdır.", "Contains lead. Should not be used on surfaces liable to be chewed or sucked by children.", ""],
 ["EUH201A", Y, "diger", "Uyarı! Kurşun içerir.", "Warning! Contains lead.", ""],
 ["EUH202", Y, "diger", "Siyanoakrilat. Tehlike. Saniyeler içinde cildi ve gözleri yapıştırır. Çocukların erişemeyeceği yerde saklayın.", "Cyanoacrylate. Danger. Bonds skin and eyes in seconds. Keep out of the reach of children.", ""],
 ["EUH203", Y, "diger", "Krom (VI) içerir. Alerjik reaksiyona yol açabilir.", "Contains chromium (VI). May produce an allergic reaction.", ""],
 ["EUH204", Y, "diger", "İzosiyanatlar içerir. Alerjik reaksiyona yol açabilir.", "Contains isocyanates. May produce an allergic reaction.", ""],
 ["EUH205", Y, "diger", "Epoksi bileşenler içerir. Alerjik reaksiyona yol açabilir.", "Contains epoxy constituents. May produce an allergic reaction.", ""],
 ["EUH206", Y, "karistirma", "Dikkat! Diğer ürünlerle birlikte kullanmayın. Tehlikeli gazlar açığa çıkarabilir (klor).", "Warning! Do not use together with other products. May release dangerous gases (chlorine).", "Aktif klor içeren ürünlerde (çamaşır suyu, klorlu temizleyiciler) zorunlu uyarı. Asitli ürünlerle karışırsa klor gazı çıkar."],
 ["EUH207", Y, "diger", "Uyarı! Kadmiyum içerir. Kullanım sırasında tehlikeli dumanlar oluşur.", "Warning! Contains cadmium. Dangerous fumes are formed during use.", ""],
 ["EUH208", Y, "alerji", "içerir. Alerjik reaksiyona yol açabilir.", "May produce an allergic reaction.", "Ürün, alerjisi olan kişilerde reaksiyon başlatabilecek bir madde içeriyor. Maddenin adı ifadenin içinde yazılır."],
 ["EUH209", I, "diger", "Kullanım sırasında kolay alevlenir hale gelebilir.", "Can become highly flammable in use.", ""],
 ["EUH209A", I, "diger", "Kullanım sırasında alevlenir hale gelebilir.", "Can become flammable in use.", ""],
 ["EUH210", I, "diger", "Talep halinde güvenlik bilgi formu sağlanabilir.", "Safety data sheet available on request.", "Ürünün ayrıntılı güvenlik bilgi formu üreticiden istenebilir."],
 ["EUH211", Y, "solunum", "Uyarı! Püskürtüldüğünde tehlikeli solunabilir damlacıklar oluşabilir. Spreyi veya buharı solumayın.", "Warning! Hazardous respirable droplets may be formed when sprayed. Do not breathe spray or mist.", ""],
 ["EUH212", Y, "solunum", "Uyarı! Kullanıldığında tehlikeli solunabilir toz oluşabilir. Tozu solumayın.", "Warning! Hazardous respirable dust may be formed when used. Do not breathe dust.", ""],
 ["EUH380", R, "endokrin", "İnsanlarda endokrin bozulmaya yol açabilir.", "May cause endocrine disruption in humans.", "AB'nin 2023'te eklediği endokrin bozucu tehlike sınıfı (kategori 1)."],
 ["EUH381", R, "endokrin", "İnsanlarda endokrin bozulmaya yol açma şüphesi var.", "Suspected of causing endocrine disruption in humans.", "AB'nin 2023'te eklediği endokrin bozucu tehlike sınıfı (kategori 2)."],
 ["EUH430", Y, "cevre", "Çevrede endokrin bozulmaya yol açabilir.", "May cause endocrine disruption in the environment.", ""],
 ["EUH431", Y, "cevre", "Çevrede endokrin bozulmaya yol açma şüphesi var.", "Suspected of causing endocrine disruption in the environment.", ""],
 ["EUH440", Y, "cevre", "Çevrede birikir; canlı organizmalarda, insanlar dahil, birikir.", "Accumulates in the environment and living organisms including in humans.", ""],
 ["EUH441", Y, "cevre", "Çevrede ve canlı organizmalarda, insanlar dahil, güçlü biçimde birikir.", "Strongly accumulates in the environment and living organisms including in humans.", ""],
 ["EUH450", Y, "cevre", "Su kaynaklarında uzun süreli ve yaygın kirlenmeye yol açabilir.", "Can cause long-lasting and diffuse contamination of water resources.", ""],
 ["EUH451", Y, "cevre", "Su kaynaklarında çok uzun süreli ve yaygın kirlenmeye yol açabilir.", "Can cause very long-lasting and diffuse contamination of water resources.", ""],
 ["EUH401", I, "diger", "İnsan sağlığı ve çevre için risklerden kaçınmak için kullanım talimatlarına uyun.", "To avoid risks to human health and the environment, comply with the instructions for use.", ""],
]

# Türkçe metni güvenlik bilgi formlarında (Bosch, EDQM SDS TR) ya da SEA'ya dayalı etiketleme kılavuzunda (CRAD) görülerek doğrulanan EUH ifadeleri
EUH_VERIFIED = {"EUH208", "EUH210", "EUH066", "EUH206"}
SDS_TR = ["https://www.bosch-pt.com/msds/_res/media/tr/1605430014_TR-tr_00635-0052_1,0.pdf",
          "https://sds.edqm.eu/pdf/SDS/EDQM_202300230_1.0_SDS_TR.pdf",
          "https://www.crad.com.tr/UPLOAD/URUN/FILES/ZararliKimyasallarinMevzuataUygunEtiketlenmesi-221724484.pdf"]
# Eski ya da farklı firma çevirileri: aynı ifadeye bağlanır
TR_ALT = {"EUH210": ["Talep halinde güvenlik bilgi formu temin edilebilir."],
          "H361fd": ["Doğurganlığı muhtemelen kısıtlayabilir. Çocuğa anne karnında muhtemelen zarar verebilir."]}

# Önlem ifadeleri (P). Tüketici ürünlerinde sık görülenler. [kod, TR, EN, ilk_yardim?]
# TR: EDQM SDS TR'de görülenler birebir; diğerleri çeviri (needs_review).
P_SEEN = {"P201", "P202", "P260", "P263", "P264", "P270", "P271", "P280", "P301+P312", "P304+P340", "P308+P313", "P312", "P330", "P403+P233", "P405", "P501"}
PREC = [
 ["P101", "Tıbbi tavsiye gerekirse ürün kabını veya etiketini yanınızda bulundurun.", "If medical advice is needed, have product container or label at hand.", 1],
 ["P102", "Çocukların erişemeyeceği yerde saklayın.", "Keep out of reach of children.", 0],
 ["P103", "Kullanmadan önce etiketi okuyun.", "Read label before use.", 0],
 ["P201", "Kullanmadan önce özel talimatları okuyun.", "Obtain special instructions before use.", 0],
 ["P202", "Bütün önlem ifadeleri okunup anlaşılmadan elleçlemeyin.", "Do not handle until all safety precautions have been read and understood.", 0],
 ["P210", "Isıdan, sıcak yüzeylerden, kıvılcımdan, açık alevden ve diğer tutuşturucu kaynaklardan uzak tutun. Sigara içilmez.", "Keep away from heat, hot surfaces, sparks, open flames and other ignition sources. No smoking.", 0],
 ["P211", "Açık aleve veya diğer tutuşturucu kaynaklara püskürtmeyin.", "Do not spray on an open flame or other ignition source.", 0],
 ["P251", "Delmeyin veya yakmayın, kullandıktan sonra bile.", "Do not pierce or burn, even after use.", 0],
 ["P260", "Tozunu/dumanını/gazını/sisini/buharını/spreyini solumayın.", "Do not breathe dust/fume/gas/mist/vapours/spray.", 0],
 ["P261", "Tozunu/dumanını/gazını/sisini/buharını/spreyini solumaktan kaçının.", "Avoid breathing dust/fume/gas/mist/vapours/spray.", 0],
 ["P262", "Gözlerle, ciltle veya giysilerle temasından kaçının.", "Do not get in eyes, on skin, or on clothing.", 0],
 ["P263", "Gebelik sırasında ve emzirirken temastan kaçının.", "Avoid contact during pregnancy and while nursing.", 0],
 ["P264", "Elleçlemeden sonra elleri, kolları ve yüzü iyice yıkayın.", "Wash hands thoroughly after handling.", 0],
 ["P270", "Bu ürünü kullanırken hiçbir şey yemeyin, içmeyin veya sigara içmeyin.", "Do not eat, drink or smoke when using this product.", 0],
 ["P271", "Sadece dışarıda veya iyi havalandırılan bir alanda kullanın.", "Use only outdoors or in a well-ventilated area.", 0],
 ["P273", "Çevreye verilmesinden kaçının.", "Avoid release to the environment.", 0],
 ["P280", "Koruyucu eldiven/koruyucu kıyafet/göz koruyucu/yüz koruyucu kullanın.", "Wear protective gloves/protective clothing/eye protection/face protection.", 0],
 ["P301+P310", "YUTULDUĞUNDA: Hemen ZEHİR DANIŞMA MERKEZİNİ veya doktoru arayın.", "IF SWALLOWED: Immediately call a POISON CENTER/doctor.", 1],
 ["P301+P312", "YUTULDUĞUNDA: Kendinizi iyi hissetmezseniz ZEHİR MERKEZİNİ veya doktoru arayın.", "IF SWALLOWED: Call a POISON CENTER/doctor if you feel unwell.", 1],
 ["P301+P330+P331", "YUTULDUĞUNDA: Ağzınızı çalkalayın. KUSTURMAYIN.", "IF SWALLOWED: Rinse mouth. Do NOT induce vomiting.", 1],
 ["P302+P352", "CİLT İLE TEMAS HALİNDE: Bol su ile yıkayın.", "IF ON SKIN: Wash with plenty of water.", 1],
 ["P303+P361+P353", "CİLT (veya saç) İLE TEMAS HALİNDE: Kirlenmiş giysilerin hepsini hemen çıkarın. Cildi su ile durulayın.", "IF ON SKIN (or hair): Take off immediately all contaminated clothing. Rinse skin with water.", 1],
 ["P304+P340", "SOLUNMASI HALİNDE: Kişiyi temiz havaya çıkarın ve rahat nefes alabileceği bir pozisyonda tutun.", "IF INHALED: Remove person to fresh air and keep comfortable for breathing.", 1],
 ["P305+P351+P338", "GÖZLE TEMASI HALİNDE: Su ile birkaç dakika dikkatlice durulayın. Varsa ve yapması kolaysa kontakt lensleri çıkarın. Durulamaya devam edin.", "IF IN EYES: Rinse cautiously with water for several minutes. Remove contact lenses, if present and easy to do. Continue rinsing.", 1],
 ["P308+P313", "Maruz kalma veya etkilenme halinde: Tıbbi yardım/bakım alın.", "IF exposed or concerned: Get medical advice/attention.", 1],
 ["P310", "Hemen ZEHİR DANIŞMA MERKEZİNİ veya doktoru arayın.", "Immediately call a POISON CENTER/doctor.", 1],
 ["P312", "Kendinizi iyi hissetmezseniz ZEHİR MERKEZİNİ veya doktoru arayın.", "Call a POISON CENTER/doctor if you feel unwell.", 1],
 ["P313", "Tıbbi yardım/bakım alın.", "Get medical advice/attention.", 1],
 ["P330", "Ağzınızı çalkalayın.", "Rinse mouth.", 1],
 ["P331", "KUSTURMAYIN.", "Do NOT induce vomiting.", 1],
 ["P332+P313", "Ciltte tahriş oluşursa: Tıbbi yardım/bakım alın.", "If skin irritation occurs: Get medical advice/attention.", 1],
 ["P333+P313", "Ciltte tahriş veya kızarıklık oluşursa: Tıbbi yardım/bakım alın.", "If skin irritation or rash occurs: Get medical advice/attention.", 1],
 ["P337+P313", "Göz tahrişi devam ederse: Tıbbi yardım/bakım alın.", "If eye irritation persists: Get medical advice/attention.", 1],
 ["P391", "Döküntüyü toplayın.", "Collect spillage.", 0],
 ["P403+P233", "İyi havalandırılmış bir alanda depolayın. Kabı sıkıca kapalı tutun.", "Store in a well-ventilated place. Keep container tightly closed.", 0],
 ["P405", "Kilit altında saklayın.", "Store locked up.", 0],
 ["P410", "Güneş ışığından koruyun.", "Protect from sunlight.", 0],
 ["P410+P412", "Güneş ışığından koruyun. 50 °C üzerindeki sıcaklıklara maruz bırakmayın.", "Protect from sunlight. Do not expose to temperatures exceeding 50 °C/122 °F.", 0],
 ["P501", "İçeriği/kabı yerel, bölgesel, ulusal ve/veya uluslararası düzenlemelere uygun olarak bertaraf edin.", "Dispose of contents/container in accordance with local/regional/national/international regulations.", 0],
]

# Sıvı çamaşır deterjanı kapsülleri: CLP Ek II 3.3 (AB 1297/2014 ile eklendi)
CAPSULE = {
 "pat": [r"kaps[uü]l", r"(?:^|[^a-z])capsules?(?![a-z])", r"(?:^|[^a-z])pods?(?![a-z])", r"suda" + r"[^a-z0-9%]+" + r"(?:cozunen|eriyen)" + r"[^a-z0-9%]+" + r"(?:film|ambalaj|paket)", r"water" + r"[^a-z0-9%]+" + r"soluble" + r"[^a-z0-9%]+" + r"(?:film|pouch|packaging)"],
 "title": "Deterjan kapsülü: çocuklar için ayrı dikkat",
 "text": "Sıvı çamaşır deterjanı kapsülleri AB'de özel kurallara bağlıdır (CLP Ek II 3.3): dış ambalaj içini göstermeyen, çocuğun açmakta zorlanacağı kilitli kapaklı olmalı ve üzerinde “Çocukların erişemeyeceği yerde saklayın” (P102) yazmalıdır. Kapsülün filminde ağza alınınca 6 saniye içinde tükürtecek acı bir madde bulunmalı, film 30 saniye suya ve 300 N basınca dayanmalıdır. Bu kurallar, kapsülleri şekere benzeten küçük çocuklarda yutma ve göze kaçma kazaları yüzünden getirildi.",
 "sources": ["https://reachonline.eu/clp/en/annex-ii-3-3.3.html", "https://www.legislation.gov.uk/eur/2014/1297/introduction"],
}
UZEM = "Türkiye'de Ulusal Zehir Danışma Merkezi (UZEM): 114."

GROUP_LABEL = {"cilt_goz": "Cilt ve göz", "solunum": "Solunum", "yutma": "Yutma", "zehir": "Zehirlilik",
               "cmr": "Kanser, genetik hasar, üreme (CMR)", "organ": "Organ hasarı", "cevre": "Çevre",
               "fiziksel": "Yangın, patlama, basınç", "karistirma": "Karıştırma", "alerji": "Alerji",
               "endokrin": "Endokrin bozucu", "diger": "Diğer"}

# ---------------------------------------------------------------------------
# İçerik grupları (648/2004 Ek VII A; TR Ek-7). pat: low()+sadeleştirilmiş metinde aranan düzenli ifadeler (ASCII,
# Türkçe harfler eşlenmiş). Lookbehind kullanılmaz (eski Safari). about: sade açıklama.
# ---------------------------------------------------------------------------
W = r"[^a-z0-9%]+"   # sözcük arası
GROUPS = [
 {"id": "fosfat", "tr": "Fosfatlar", "level": I,
  "pat": [r"fosfat(?:lar|i)?(?![a-z])", r"phosphates?(?![a-z])"],
  "about": "Su yumuşatıcı. Atıksuyla göl ve denizlere ulaşınca aşırı yosunlanmaya (ötrofikasyon) katkı yapar; AB, ev tipi çamaşır ve bulaşık makinesi deterjanlarında fosfor miktarını 259/2012 sayılı tüzükle sınırladı."},
 {"id": "fosfonat", "tr": "Fosfonatlar", "level": I,
  "pat": [r"fosfonat(?:lar)?(?![a-z])", r"phosphonates?(?![a-z])"],
  "about": "Su yumuşatıcı ve kireç önleyici; fosfattan çok daha düşük oranlarda kullanılır."},
 {"id": "anyonik", "tr": "Anyonik yüzey aktif maddeler", "level": I,
  "pat": [r"anyonik" + W + r"(?:yuzey" + W + r"(?:aktif|etken)|tensid)", r"anionic" + W + r"surfactants?"],
  "about": "Kir ve yağı çözen asıl temizleyici madde (ör. sodyum lauril eter sülfat)."},
 {"id": "katyonik", "tr": "Katyonik yüzey aktif maddeler", "level": I,
  "pat": [r"katyonik" + W + r"(?:yuzey" + W + r"(?:aktif|etken)|tensid)", r"cationic" + W + r"surfactants?"],
  "about": "Çoğunlukla yumuşatıcılarda ve bazı dezenfektanlarda (kuaterner amonyum bileşikleri) bulunur."},
 {"id": "amfoterik", "tr": "Amfoterik yüzey aktif maddeler", "level": I,
  "pat": [r"amfoterik" + W + r"(?:yuzey" + W + r"(?:aktif|etken)|tensid)", r"amphoteric" + W + r"surfactants?"],
  "about": "Köpük ve yumuşaklık sağlayan, cilde görece nazik temizleyici madde."},
 {"id": "noniyonik", "tr": "Noniyonik yüzey aktif maddeler", "level": I,
  "pat": [r"(?:non(?:" + W + r")?iyonik|iyonik" + W + r"olmayan)" + W + r"(?:yuzey" + W + r"(?:aktif|etken)|tensid)", r"non(?:" + W + r")?ionic" + W + r"surfactants?"],
  "about": "Yağlı kirlerde etkili temizleyici madde; düşük köpüklüdür."},
 {"id": "oksijen", "tr": "Oksijen bazlı ağartıcılar", "level": I,
  "pat": [r"oksijen" + W + r"(?:bazli|esasli|kaynakli)" + W + r"agartici", r"oxygen" + W + r"based" + W + r"bleaching"],
  "about": "Lekeyi oksijenle ağartır (ör. sodyum perkarbonat). Klorlu ağartıcıdan farklıdır."},
 {"id": "klor", "tr": "Klor bazlı ağartıcılar", "level": Y, "mix": True,
  "pat": [r"klor" + W + r"(?:bazli|esasli|kaynakli)" + W + r"agartici", r"chlorine" + W + r"based" + W + r"bleaching", r"aktif" + W + r"klor"],
  "about": "Çamaşır suyundaki etken madde (sodyum hipoklorit). Asitli ürünlerle ya da amonyakla karıştırılırsa zehirli gaz açığa çıkar."},
 {"id": "edta", "tr": "EDTA ve tuzları", "level": I,
  "pat": [r"(?:^|[^a-z])edta(?![a-z])"],
  "about": "Metal iyonlarını bağlayarak suyun sertliğini etkisizleştirir; doğada yavaş parçalanır."},
 {"id": "nta", "tr": "NTA ve tuzları", "level": Y,
  "pat": [r"(?:^|[^a-z])nta(?![a-z])"],
  "about": "Metal bağlayıcı. Trisodyum NTA, AB'de 'kansere yol açma şüphesi' (Carc. 2) sınıfındadır; üründeki tehlike ifadesi orana göre değişir."},
 {"id": "fenol", "tr": "Fenoller ve halojenli fenoller", "level": I,
  "pat": [r"fenol(?:ler)?(?![a-z])", r"phenols?(?![a-z])"],
  "about": "Dezenfektan ve koruyucu olarak kullanılan madde grubu."},
 {"id": "pdcb", "tr": "Paradiklorobenzen", "level": Y,
  "pat": [r"paradiklorobenzen", r"para" + W + r"?dichlorobenzene", r"paradichlorobenzene"],
  "about": "Naftalin benzeri koku gidericilerde kullanılır; AB'de 'kansere yol açma şüphesi' (Carc. 2) sınıfındadır."},
 {"id": "hidrokarbon", "tr": "Hidrokarbonlar (aromatik, alifatik, halojenli)", "level": I,
  "pat": [r"hidrokarbon(?:lar)?(?![a-z])", r"hydrocarbons?(?![a-z])"],
  "about": "Yağ çözücü. Bazıları solunduğunda baş dönmesi, yutulup akciğere kaçarsa ciddi hasar yapabilir; etiketteki tehlike ifadelerine bakın."},
 {"id": "sabun", "tr": "Sabun", "level": I,
  "pat": [r"(?:^|[^a-z])sabun(?:lar)?(?![a-z])", r"(?:^|[^a-z])soap(?![a-z])"],
  "about": "Yağ asidi tuzları; doğada kolay parçalanan temizleyici."},
 {"id": "zeolit", "tr": "Zeolitler", "level": I,
  "pat": [r"zeolit(?:ler)?(?![a-z])", r"zeolites?(?![a-z])"],
  "about": "Fosfat yerine kullanılan su yumuşatıcı mineral."},
 {"id": "polikarboksilat", "tr": "Polikarboksilatlar", "level": I,
  "pat": [r"polikarboksilat(?:lar)?(?![a-z])", r"polycarboxylates?(?![a-z])"],
  "about": "Kirin kumaşa geri yapışmasını önleyen polimer; su yumuşatmaya yardımcı olur."},
 {"id": "enzim", "noband": True, "tr": "Enzimler", "level": I, "resp": True,
  "pat": [r"enzim(?:ler|i)?(?![a-z])", r"enzymes?(?![a-z])"],
  "about": "Protein, nişasta ve yağ lekelerini parçalar (proteaz, amilaz, lipaz). Ham madde olarak solunum yolu hassaslaştırıcıdır; bitmiş üründe bu tehlike varsa etikette ayrıca yazılır."},
 {"id": "dezenfektan", "noband": True, "tr": "Dezenfektanlar", "level": I,
  "pat": [r"dezenfektan(?:lar)?(?![a-z])", r"disinfectants?(?![a-z])"],
  "about": "Mikrop öldürücü madde. Türkiye'de dezenfektan ürünler ayrıca biyosidal ürün izni gerektirir."},
 {"id": "optik", "noband": True, "tr": "Optik parlatıcılar", "level": I,
  "pat": [r"optik" + W + r"(?:parlatici|agartici|beyazlatici)", r"optical" + W + r"brighteners?"],
  "about": "Kumaşa yapışıp morötesi ışığı mavi ışığa çevirerek beyazı daha parlak gösterir."},
 {"id": "parfum", "noband": True, "tr": "Parfüm", "level": I,
  "pat": [r"(?:^|[^a-z])parfum(?![a-z])", r"(?:^|[^a-z])perfumes?(?![a-z])", r"(?:^|[^a-z])fragrances?(?![a-z])"],
  "about": "Koku maddelerinin toplu adı. İçindeki koku alerjenleri %0,01'i aşarsa adıyla ayrıca yazılır."},
 {"id": "renklendirici", "noband": True, "tr": "Renklendiriciler", "level": I,
  "pat": [r"renklendirici(?:ler)?(?![a-z])", r"(?:^|[^a-z])colou?rants?(?![a-z])"],
  "about": "Ürüne renk verir. Deterjan etiketinde yazılması zorunlu değildir; CI ile başlayan kodla (Colour Index) yazılır."},
 {"id": "koruyucu", "noband": True, "tr": "Koruyucular", "level": I,
  "pat": [r"(?:^|[^a-z])koruyucu(?:lar)?(?![a-z])(?!" + W + r"(?:eldiven|giysi|gozluk|kiyafet|ekipman|maske|kullan|tak))", r"preservatives?(?![a-z])", r"preservation" + W + r"agents?"],
  "about": "Ürünün bozulmasını önler. Adı INCI ile yazılır; bazıları (izotiyazolinonlar) cilt alerjisi yapabilir."},
]

# ---------------------------------------------------------------------------
# Temizlik ürününde ayrıca not gerektiren INCI adları
# ---------------------------------------------------------------------------
SUBS = [
 {"id": "mit", "inci": ["METHYLISOTHIAZOLINONE"], "pat": [r"methylisothiazolinone", r"metilizotiyazolinon", r"(?:^|[^-a-z0-9])2-?\s?methyl-?\s?2h-?\s?isothiazol", r"(?:^|[^-a-z0-9])2-?\s?metil-?\s?2h-?\s?izotiyazol"], "kind": "koruyucu", "level": Y,
  "text": "İzotiyazolinon grubu koruyucu. AB'de uyumlaştırılmış sınıflandırması cilt hassaslaştırıcıdır (Skin Sens. 1A); düşük oranlarda bile temas alerjisi yapabilir. Durulanmayan kozmetiklerde AB'de yasaktır, temizlik ürünlerinde kullanılabilir.",
  "sources": [ECHA_CL, COSING]},
 {"id": "cmit", "inci": ["METHYLCHLOROISOTHIAZOLINONE"], "pat": [r"methylchloroisothiazolinone", r"metilkloroizotiyazolinon", r"chloro-?\s?2-?\s?methyl-?\s?2h-?\s?isothiazol", r"kloro-?\s?2-?\s?metil-?\s?2h-?\s?izotiyazol"], "kind": "koruyucu", "level": Y,
  "text": "İzotiyazolinon grubu koruyucu (genellikle MIT ile karışım halinde). AB'de cilt hassaslaştırıcı (Skin Sens. 1A) olarak sınıflandırılmıştır; kozmetikte yalnızca durulanan ürünlerde izinlidir.",
  "sources": [ECHA_CL, COSING]},
 {"id": "bit", "inci": ["BENZISOTHIAZOLINONE"], "pat": [r"benzisothiazol", r"benzizotiyazol", r"benzisotiyazol"], "kind": "koruyucu", "level": Y,
  "text": "İzotiyazolinon grubu koruyucu (BIT). AB'de cilt hassaslaştırıcı olarak sınıflandırılmıştır. Kozmetik koruyucular listesinde (Ek V) yer almaz; deterjan ve boyalarda kullanılır.",
  "sources": [ECHA_CL]},
 {"id": "oit", "inci": ["OCTYLISOTHIAZOLINONE"], "pat": [r"octylisothiazol", r"oktilizotiyazol", r"octhilinone", r"octyl-?\s?2h-?\s?isothiazol", r"oktil-?\s?2h-?\s?izotiyazol"], "kind": "koruyucu", "level": Y,
  "text": "İzotiyazolinon grubu koruyucu (OIT). AB'de cilt hassaslaştırıcı olarak sınıflandırılmıştır.",
  "sources": [ECHA_CL]},
 {"id": "hipoklorit", "inci": ["SODIUM HYPOCHLORITE"], "pat": [r"sodyum\s?hipoklorit", r"sodium\s?hypochlorite"], "kind": "klor", "level": Y, "mix": True,
  "text": "Çamaşır suyunun etken maddesi. Sağlık Bakanlığı'na göre tuz ruhu gibi asitli ürünlerle karışınca klor gazı, amonyakla karışınca zehirli gaz oluşur.",
  "sources": [SB_REHBER]},
 {"id": "enzim", "inci": ["SUBTILISIN", "PROTEASE", "AMYLASE", "LIPASE", "CELLULASE"], "pat": [r"(?:^|[^a-z])(?:subtilisin|protease|proteaz|amylase|amilaz|lipase|lipaz|cellulase|selulaz|mannanase|mannanaz)(?![a-z])"], "kind": "enzim", "level": I, "resp": True,
  "text": "Enzim. Ham madde olarak solunum yolu hassaslaştırıcıdır (H334); bitmiş üründe bu tehlike varsa etikette tehlike ifadesi olarak yazılır.",
  "sources": [ECHA_CL]},
 {"id": "hcl", "inci": ["HYDROCHLORIC ACID"], "pat": [r"hydrochloric\s?acid", r"hidroklorik\s?asit"], "kind": "asit", "level": I, "mix": True,
  "text": "Tuz ruhu. Çamaşır suyuyla karışırsa klor gazı açığa çıkar.",
  "sources": [SB_REHBER]},
 {"id": "amonyak", "inci": ["AMMONIA", "AMMONIUM HYDROXIDE"], "pat": [r"(?:^|[^a-z])amonya[kg]", r"(?:^|[^a-z])ammonia(?![a-z])", r"ammonium\s?hydroxide"], "kind": "amonyak", "level": I, "mix": True,
  "text": "Amonyak. Çamaşır suyuyla karışırsa zehirli gaz açığa çıkar.",
  "sources": [SB_REHBER]},
]

BANDS = {"b5": "%5'ten az", "b5_15": "%5-15", "b15_30": "%15-30", "b30": "%30 ve üzeri"}

MIX_RULE = {"title": "Başka ürünlerle karıştırmayın",
            "text": "Klorlu ürünler (çamaşır suyu) asitli ürünlerle (tuz ruhu, kireç çözücü) karışınca klor gazı, amonyakla karışınca zehirli gaz açığa çıkarır. Sağlık Bakanlığı bu ürünlerin karıştırılmamasını öneriyor; aktif klor içeren ürünlerin etiketinde EUH206 uyarısı zorunludur.",
            "sources": [SB_REHBER, CLP]}


ALIAS_TSV = os.path.join(HERE, "kaynak", "temizlik_esanlamlilar.tsv")


def read_aliases(known):
    out, seen = [], set()
    for ln in open(ALIAS_TSV, encoding="utf-8"):
        if not ln.strip() or ln.startswith("#"):
            continue
        ad, hedef, tur = [x.strip() for x in ln.rstrip("\n").split("\t")]
        ts = [t.strip() for t in hedef.split(";")]
        for t in ts:
            assert t in known, "INCI listesinde yok: %s (%s)" % (t, ad)
        assert tur in ("tr", "en", "kisa", "halk"), tur
        assert ad.lower() not in seen, "tekrar: " + ad
        seen.add(ad.lower())
        out.append([ad, ts, tur])
    return out


def main():
    ki = json.load(open(os.path.join(HERE, "data", "kozmetik_inci.json"), encoding="utf-8"))
    known = {x[0] for x in ki["items"]}
    aliases = read_aliases(known)
    for s in SUBS:
        for a in s["inci"]:
            assert a in known, a
    hz, seen = [], set()
    for row in H + EUH:
        code, lvl, grp, tr, en, note = row
        assert code not in seen, code
        seen.add(code)
        assert grp in GROUP_LABEL, grp
        e = {"code": code, "level": lvl, "group": grp, "tr": tr, "en": en}
        if note:
            e["note"] = note
        if code.startswith("EUH") and code not in EUH_VERIFIED:
            e["needs_review"] = True   # Türkçe metin SEA Ek-2 ile birebir karşılaştırılmadı
        if code in TR_ALT:
            e["alt"] = TR_ALT[code]
        hz.append(e)
    prec = []
    for code, tr, en, aid in PREC:
        e = {"code": code, "tr": tr, "en": en}
        if aid:
            e["aid"] = True
        if code not in P_SEEN:
            e["needs_review"] = True
        prec.append(e)
    for c in HCOMB:
        for x in c[0]:
            assert x in seen, x
    out = {
        "version": VERSION, "last_updated": LAST_UPDATED,
        "meta": {
            "description": "Temizlik ürünü etiketi: zararlılık ifadeleri (CLP/SEA), deterjan içerik grupları (AB 648/2004 Ek VII, TR Deterjanlar Hakkında Yönetmelik Ek-7) ve ayrıca not gerektiren maddeler.",
            "sources": {"clp": CLP, "h_tr": H_TR, "euh": EUH_LIST, "det": DET, "det_tr": DET_TR, "sb": SB_REHBER},
            "hazard_source": "SEA Yönetmeliği (RG 11.12.2013, 28848) / AB CLP (EC) 1272/2008 Ek III. H ifadelerinin Türkçe metni SEA'ya dayalı listeden; EUH ifadelerinin Türkçesi çeviri, resmi metinle birebir karşılaştırılmadı.",
            "group_source": "AB 648/2004 Ek VII A ve TR Deterjanlar Hakkında Yönetmelik (RG 27.01.2018, 30314) Ek-7: %0,2'yi aşan gruplar bant halinde; enzim, dezenfektan, optik parlatıcı, parfüm her oranda; koruyucular INCI adıyla; %0,01'i aşan koku alerjenleri adıyla yazılır. AB 2026/405 sayılı yeni tüzük 2029'da uygulanmaya başlar.",
            "levels": {"red": "Ürünün resmi tehlike sınıfı ciddi: yanık, ciddi göz hasarı, zehirlilik, kanser/genetik/üreme (CMR), solunum hassaslaşması.",
                       "yellow": "Uyarı düzeyinde tehlike, alerji, karıştırma ya da çevre uyarısı.",
                       "info": "Bilgi."},
            "group_labels": GROUP_LABEL, "bands": BANDS,
            "word_sep": W,
        },
        "hazards": hz,
        "combos": [{"codes": c[0], "tr": c[1], "en": c[2]} for c in HCOMB],
        "groups": GROUPS, "subs": SUBS, "aliases": aliases,
        "precautions": prec, "capsule": CAPSULE, "uzem": UZEM, "sds_tr": SDS_TR, "mix_rule": MIX_RULE,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("temizlik.json: %d ifade (%d EUH), %d birleşik, %d önlem, %d grup, %d madde notu, %d eş anlamlı" % (
        len(hz), len(EUH), len(HCOMB), len(prec), len(GROUPS), len(SUBS), len(aliases)))


if __name__ == "__main__":
    main()

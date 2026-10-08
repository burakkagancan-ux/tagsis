// Ölçüm (CI'da değil): İngilizce gıda etiketlerinde içerik ve alerjen tanıma. Çalıştır: node test/olcum_ingilizce.js
// 10 gerçekçi etiket (İngiltere/AB yazımı). Her etikette: içerik listesi parçalarından kaçı tanındı (parçanın içinde en az bir madde eşleşti),
// beklenen alerjenlerden kaçı bulundu, E kodu ve katkı adları. Tanınmayan parçalar listelenir (eş anlamlı eklemek ayrı iş).
eval(require('./yukle.js')+';global.G={analyze,summarize,buildIndex,normText,cmpSegments}');
const {idx}=require('./run.js');
const E=[
 {ad:'Çikolatalı bisküvi',al:['allergen_gluten','allergen_milk','allergen_soy'],m:'Ingredients: Wheat Flour (Wheat Flour, Calcium Carbonate, Iron, Niacin, Thiamin), Milk Chocolate (30%) (Sugar, Cocoa Butter, Cocoa Mass, Dried Skimmed Milk, Dried Whey (Milk), Butter Oil (Milk), Vegetable Fat (Palm, Shea), Emulsifiers (Soya Lecithin, E476), Natural Vanilla Flavouring), Vegetable Oil (Palm), Wholemeal Wheat Flour, Sugar, Glucose-Fructose Syrup, Raising Agents (Sodium Bicarbonate, Malic Acid, Ammonium Bicarbonate), Salt.'},
 {ad:'Kola',al:[],m:'Ingredients: Carbonated Water, Sugar, Colour (Caramel E150d), Phosphoric Acid, Natural Flavourings including Caffeine.'},
 {ad:'Şekersiz içecek',al:[],m:'Ingredients: Carbonated Water, Citric Acid, Natural Flavourings, Acidity Regulator (Sodium Citrate), Sweeteners (Aspartame, Acesulfame K), Preservative (Potassium Sorbate). Contains a source of Phenylalanine.'},
 {ad:'Peynirli cips',al:['allergen_milk'],m:'Ingredients: Potatoes, Sunflower Oil (31%), Cheese & Onion Seasoning (Whey Permeate (from Milk), Dried Onion, Salt, Cheese Powder (from Milk), Dried Yeast, Dextrose, Potassium Chloride, Flavouring, Colours (Annatto Norbixin, Paprika Extract), Garlic Powder, Acid (Citric Acid), Flavour Enhancer (Monosodium Glutamate)).'},
 {ad:'Ekmek',al:['allergen_gluten','allergen_soy'],m:'Ingredients: Wheat Flour, Water, Yeast, Salt, Soya Flour, Preservative (Calcium Propionate), Emulsifiers (E471, E472e), Vegetable Oil (Rapeseed), Flour Treatment Agent (Ascorbic Acid).'},
 {ad:'Jelibon',al:[],m:'Ingredients: Glucose Syrup, Sugar, Gelatine (Pork), Dextrose, Citric Acid, Flavourings, Fruit Juice Concentrates (Apple, Strawberry), Colours (E129, E133, E102), Glazing Agent (Carnauba Wax), Coconut Oil.'},
 {ad:'Meyveli yoğurt',al:['allergen_milk'],m:'Ingredients: Yogurt (Milk), Sugar, Strawberries (8%), Modified Maize Starch, Concentrated Lemon Juice, Stabiliser (Pectins), Flavouring, Colour (Carmine).'},
 {ad:'Jambon',al:[],m:'Ingredients: Pork (87%), Water, Salt, Dextrose, Stabilisers (Triphosphates), Antioxidant (Sodium Ascorbate), Preservative (Sodium Nitrite).'},
 {ad:'Ketçap',al:['allergen_celery'],m:'Ingredients: Tomatoes, Spirit Vinegar, Sugar, Salt, Spice and Herb Extracts (contain Celery), Spice.'},
 {ad:'Margarin',al:['allergen_milk'],m:'Ingredients: Vegetable Oils (Palm, Rapeseed, Sunflower) (59%), Water, Buttermilk (Milk), Salt (1.2%), Emulsifier (Mono- and Diglycerides of Fatty Acids), Preservative (Potassium Sorbate), Acid (Lactic Acid), Natural Flavouring, Vitamins A and D, Colour (Carotenes).'},
];
let tp=0,tt=0,ap=0,at=0;const kayip={};
for(const e of E){
  const res=G.analyze(e.m,idx),S=G.summarize(res,idx),tok=G.normText(e.m).split(' ').filter(Boolean),seg=G.cmpSegments(tok);
  const hit=seg.filter(s=>res.some(r=>r.pos>=s[0]&&r.pos<s[1]));
  const miss=seg.filter(s=>!hit.includes(s)).map(s=>tok.slice(s[0],s[1]).filter(w=>w!=='|'&&w!=='('&&w!==')').join(' '));
  const al=e.al.filter(f=>S.allergen[f]&&(S.allergen[f].yes.length||S.allergen[f].may.length));
  tp+=hit.length;tt+=seg.length;ap+=al.length;at+=e.al.length;
  miss.forEach(m=>kayip[m]=(kayip[m]||0)+1);
  const bul=[...new Set(res.filter(r=>!r.neg).map(r=>r.ids.join('/')))];
  console.log(`${e.ad}: ${hit.length}/${seg.length} parça tanındı; alerjen ${al.length}/${e.al.length}${e.al.length>al.length?' (eksik: '+e.al.filter(f=>!al.includes(f)).join(', ')+')':''}`);
  console.log('  bulunan: '+bul.join(', '));
}
console.log(`\nToplam: ${tp}/${tt} parça (%${Math.round(tp/tt*100)}), alerjen ${ap}/${at} (%${Math.round(ap/at*100)})`);
console.log('Tanınmayan parçalar: '+Object.keys(kayip).sort().join(' | '));

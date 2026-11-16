# -*- coding: utf-8 -*-
"""GUIDA-SVILUPPO: inserisce prodotti DEMO con nomi di prodotti reali (prezzi indicativi inventati, NON listino).
Uso: python automation/crea_prodotti_demo.py   poi   python automation/allinea_hash.py en
Scrive _data/catalogo.json (prodotti, con tr.en), _negozio/prodotto-<id>.md (IT), en/negozio/prodotto-<id>.md (EN).
Idempotente: rimpiazza i prodotti con lo stesso id. Per togliere i demo: cancella i prodotti con "demo": true dal catalogo e le loro pagine.
JSON UTF-8 senza BOM, ensure_ascii=False (docs/ERRORI_NOTI.md punto 23)."""
import json, os, re, unicodedata
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# (categoria id, nome, prezzo EUR, descrizione IT, descrizione EN)
P = [
 ("cani","Royal Canin Maxi Adult 15 kg",69.90,"Crocchette complete per cani adulti di taglia grande (26-44 kg).","Complete dry food for adult large-breed dogs (26-44 kg)."),
 ("cani","Kong Classic Large",13.90,"Giocattolo in gomma resistente da riempire con snack, ideale per masticare.","Durable rubber toy to stuff with treats, ideal for chewing."),
 ("cani","Ruffwear Front Range Imbracatura",44.90,"Imbracatura imbottita e regolabile per passeggiate comode e sicure.","Padded, adjustable harness for comfortable and safe walks."),
 ("gatti","Royal Canin Indoor 27 - 10 kg",59.90,"Crocchette per gatti adulti che vivono in appartamento.","Dry food for adult cats living indoors."),
 ("gatti","Catit Flower Fountain",24.90,"Fontanella ad acqua corrente a forma di fiore, stimola il gatto a bere.","Flower-shaped running-water fountain that encourages cats to drink."),
 ("gatti","Ferplast Lettiera Cathy Clever&Smart",29.90,"Lettiera chiusa con filtro al carbone per ridurre gli odori.","Covered litter box with a charcoal filter to reduce odours."),
 ("uccelli","Versele-Laga Prestige Canarini 1 kg",6.90,"Miscela di semi per canarini, con ingredienti selezionati.","Seed mix for canaries with selected ingredients."),
 ("uccelli","Ferplast Gabbia Dario",39.90,"Gabbia per canarini e piccoli uccelli, completa di posatoi e mangiatoie.","Cage for canaries and small birds, with perches and feeders."),
 ("uccelli","Vitakraft Menu Vital Pappagallini 1 kg",9.90,"Alimento completo per pappagallini ondulati.","Complete food for budgerigars."),
 ("rettili","Exo Terra Terrario Glass 45x45x60",119.90,"Terrario in vetro con ventilazione e doppia porta frontale.","Glass terrarium with ventilation and front-opening doors."),
 ("rettili","Exo Terra Repti Glo 5.0 UVB",19.90,"Lampada fluorescente UVB per rettili diurni.","UVB fluorescent lamp for diurnal reptiles."),
 ("rettili","Zoo Med Repti Calcium con D3 85 g",11.90,"Integratore di calcio con vitamina D3 per rettili.","Calcium supplement with vitamin D3 for reptiles."),
 ("piccoli-mammiferi","Versele-Laga Cuni Complete 1,75 kg",9.90,"Alimento completo in pellet per conigli nani e adulti.","Complete pelleted food for dwarf and adult rabbits."),
 ("piccoli-mammiferi","Ferplast Gabbia Criceti Favola",29.90,"Gabbia per criceti con ruota, casetta e abbeveratoio.","Hamster cage with wheel, house and water bottle."),
 ("piccoli-mammiferi","JR Farm Fieno di Timothy 1 kg",11.90,"Fieno naturale ricco di fibre per conigli, cavie e cincillà.","Natural high-fibre hay for rabbits, guinea pigs and chinchillas."),
 ("pesci","Tetra TetraMin Fiocchi 250 ml",8.90,"Mangime in fiocchi per tutti i pesci tropicali d'acquario.","Flake food for all tropical aquarium fish."),
 ("pesci","Eheim Classic 250 Filtro Esterno",109.90,"Filtro esterno silenzioso per acquari fino a 250 litri.","Quiet external filter for aquariums up to 250 litres."),
 ("pesci","Sera Aquatan 500 ml",10.90,"Biocondizionatore che rende l'acqua del rubinetto adatta ai pesci.","Water conditioner that makes tap water safe for fish."),
 ("cavalli","Pavo SpeediBeet 20 kg",29.90,"Polpe di barbabietola da ammollo, fonte di fibra digeribile per cavalli.","Soaking sugar beet pulp, a digestible fibre source for horses."),
 ("cavalli","Horseware Rambo Original Coperta",119.90,"Coperta impermeabile da paddock, resistente e foderata.","Waterproof, lined and durable turnout rug."),
 ("cavalli","Kentucky Horsewear Gambali Velcro",54.90,"Gambali protettivi con chiusura a velcro per il lavoro in piano e salto.","Protective boots with hook-and-loop closure for flatwork and jumping."),
]
def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")
def wt(p, t):
    p = os.path.join(R, p); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8", newline="\n").write(t)
cp = os.path.join(R, "_data", "catalogo.json")
cat = json.load(open(cp, encoding="utf-8-sig"))
icone = {c["id"]: c.get("icona", "") for c in cat["categorie"]}
ids = {slug(n) for _, n, _, _, _ in P}
cat["prodotti"] = [p for p in cat.get("prodotti", []) if p.get("id") not in ids]
for c, n, eur, d, de in P:
    i = slug(n)
    cat["prodotti"].append({"tipo": "fisico", "id": i, "nome": n, "categoria": c, "prezzo_centesimi": int(round(eur * 100)),
        "descrizione": d, "descrizione_completa": d + "\nProdotto dimostrativo: nome reale, prezzo indicativo.",
        "immagine": "", "icona": icone.get(c, ""), "visibile": True, "demo": True,
        "tr": {"en": {"nome": n, "descrizione": de, "descrizione_completa": de + "\nDemo product: real name, indicative price."}}})
    wt(f"_negozio/prodotto-{i}.md", f'---\nlayout: negozio-prodotto\ntitle: "{n}"\npid: {i}\npermalink: /negozio/{i}/\ndescription: "{d}"\nref: shop-prod-{i}\n---\n')
    wt(f"en/negozio/prodotto-{i}.md", f'---\nlayout: negozio-prodotto\ntitle: "{n}"\npid: {i}\npermalink: /en/shop/{i}/\ndescription: "{de}"\nlang: en\nlocale: en\nref: shop-prod-{i}\ntr: tradotto\ntr_hash: 0\n---\n')
open(cp, "w", encoding="utf-8", newline="\n").write(json.dumps(cat, ensure_ascii=False, indent=2) + "\n")
print("OK", len(P), "prodotti demo")

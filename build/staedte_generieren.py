"""Erzeugt build/staedte.json aus dem offiziellen Destatis-Gemeindeverzeichnis
(staedte_quelle_destatis.xlsx). Slug-stabiler Abgleich gegen den Bestand unter
../site/erste-hilfe-kurs/ (Bestandsordner = Wahrheit, Destatis nur zum Abgleich,
nicht zur Neuvergabe von Slugs). Bewusst dauerhaft in build/ statt /tmp abgelegt,
damit es nicht wieder verloren geht (siehe Auftrag 217/Nr.100)."""
import json, re, unicodedata, os, openpyxl

ROOT = os.path.dirname(os.path.abspath(__file__))
QUELLE = os.path.join(ROOT, "staedte_quelle_destatis.xlsx")
BESTAND_DIR = os.path.join(ROOT, "..", "site", "erste-hilfe-kurs")

LAND_NAMEN = {
    "01": "Schleswig-Holstein", "02": "Hamburg", "03": "Niedersachsen", "04": "Bremen",
    "05": "Nordrhein-Westfalen", "06": "Hessen", "07": "Rheinland-Pfalz", "08": "Baden-Württemberg",
    "09": "Bayern", "10": "Saarland", "11": "Berlin", "12": "Brandenburg",
    "13": "Mecklenburg-Vorpommern", "14": "Sachsen", "15": "Sachsen-Anhalt", "16": "Thüringen",
}

# Duderstadts 10 Staedte (eigene Domains erstehilfe-duderstadt.de / erstehilfe-worbis.de) —
# per build.py-Kommentar ausdrücklich ausgeschlossen, aus deren data.py ORTE-Listen (Slugs).
AUSGESCHLOSSEN_SLUGS = {
    "duderstadt", "leinefelde-worbis", "goettingen", "heilbad-heiligenstadt",
    "herzberg-am-harz", "osterode-am-harz", "northeim", "bad-lauterberg",
    "dingelstaedt", "bad-sachsa",
}


def slugify(s):
    s = s.lower()
    s = s.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    # Sorbisch/sonstige Diakritika (Sachsen/Brandenburg zweisprachige Namen: Budyšin, Chóśebuz...)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def clean_name(name):
    # Zweisprachige Namen ("Bautzen / Budyšin, Stadt, ...") -> nur der deutsche Teil.
    return name.split(",")[0].split("/")[0].strip()


def lade_bestand():
    return sorted(
        d for d in os.listdir(BESTAND_DIR)
        if os.path.isdir(os.path.join(BESTAND_DIR, d)) and not d.startswith("landkreis-") and not d.startswith("in-")
    )


def main():
    wb = openpyxl.load_workbook(QUELLE, read_only=True, data_only=True)
    ws = wb["Onlineprodukt_Gemeinden31032026"]

    kreis_name, kreis_frei = {}, {}
    rows_60 = []
    for row in ws.iter_rows(values_only=True):
        satzart = row[0]
        if satzart == "40":
            key = (row[2], row[3], row[4])
            kreis_name[key] = row[7]
            # Textkennzeichen 41 = kreisfreie Stadt (die meisten Länder), 42 = Stadtkreis
            # (Baden-Württembergs eigene Bezeichnung für dasselbe) — beide sind kreisfrei.
            kreis_frei[key] = row[1] in ("41", "42")
        elif satzart == "60":
            rows_60.append(row)

    bestand = lade_bestand()
    bestand_set = set(bestand)

    entries = []
    neue_slugs = set()
    ungematcht, verwaist_kandidaten = [], []

    for row in rows_60:
        land, rb, kreis_code, gemname, ew = row[2], row[3], row[4], row[7], row[9]
        if not gemname or ew is None or ew < 5000:
            continue
        key = (land, rb, kreis_code)
        bundesland = LAND_NAMEN[land]
        name = clean_name(gemname)
        is_frei = kreis_frei.get(key, False)
        kreis = None if is_frei else kreis_name.get(key)
        base = slugify(name)
        if base in AUSGESCHLOSSEN_SLUGS:
            continue

        slug = None
        if base in bestand_set and base not in neue_slugs:
            slug = base
        else:
            praefix = base + "-"
            kandidaten = [b for b in bestand if b.startswith(praefix) and b not in neue_slugs]
            if len(kandidaten) == 1:
                slug = kandidaten[0]
            elif len(kandidaten) > 1:
                bl_slug = slugify(bundesland)
                kreis_slug = slugify(kreis) if kreis else ""
                treffer = [k for k in kandidaten if (kreis_slug and kreis_slug in k) or bl_slug in k]
                slug = treffer[0] if len(treffer) == 1 else kandidaten[0]
        if slug is None:
            slug = base
            if slug in bestand_set or slug in neue_slugs:
                slug = slugify(f"{name}-{bundesland}")
            ungematcht.append((name, bundesland, kreis, slug))
        neue_slugs.add(slug)
        entries.append({"name": name, "slug": slug, "bundesland": bundesland, "kreis": kreis, "ew": int(ew)})

    out = os.path.join(ROOT, "staedte.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=1)

    matched_old = sum(1 for e in entries if e["slug"] in bestand_set)
    verwaist = bestand_set - neue_slugs
    print("Gesamt:", len(entries), "| auf Bestandsslug gemappt:", matched_old,
          "| echt neu:", len(ungematcht), "| verwaist:", len(verwaist))
    return entries, bestand_set, ungematcht, verwaist


if __name__ == "__main__":
    main()

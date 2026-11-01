#!/usr/bin/env python3
"""Direkte Bereinigung des LIVE-Stands (kein Generator-Vollbau): 
 1. AdSense-Kasten (ad-net mit <ins class="adsbygoogle">) von allen Seiten mit noindex entfernen
    (Entscheidung BL/Ruben 01.11.: noindex-Seiten tragen keine Anzeige).
 2. Meta-/OG-/Twitter-Description indexierbarer Seiten auf <= 155 Zeichen kuerzen:
    a) letzte(n) Satz/Saetze weglassen, wenn der Rest >= 70 Zeichen hat und mit Satzzeichen endet;
    b) sonst bei einem bereits mit "..." (Auslassung) endenden Text an der Wortgrenze kuerzen (Auslassungszeichen bleibt);
    c) sonst an einer Nebensatz-Grenze (Komma + Relativ-/Konjunktionswort, Gedankenstrich, Doppelpunkt) kuerzen, Punkt anhaengen;
    d) alles andere wird NICHT angefasst, sondern als "offen" gelistet (von Hand zu kuerzen).
Aufruf (Repo-Wurzel):  python3 tools/live_aufraeumen.py            # Trockenlauf mit Zaehlung
                       python3 tools/live_aufraeumen.py --apply    # schreibt die Dateien
Pruefung danach:  python3 build/meta_pruefen.py .  (im Generator-Zweig) bzw. tools/seiten-stand.py fuer das Ledger."""
import glob, html, os, re, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
APPLY = "--apply" in sys.argv
SEC = re.compile(r'<section class="section"><div class="wrap"><div class="ad-net" data-ad-consent>(?:(?!</div>).)*?adsbygoogle.*?</div></div></section>', re.S)
INL = re.compile(r'<div class="ad-net" data-ad-consent>(?:(?!</div>).)*?adsbygoogle.*?</div>', re.S)
SENT = re.compile(r"(?<=[.!?])(?<!Abs\.)(?<!Nr\.)(?<!z\. B\.)(?<!bzw\.)(?<!ca\.)(?<!i\. d\. R\.)(?<!Buchst\.)(?<!u\. a\.)\s+(?=[A-ZÄÖÜ§])")
DESC = re.compile(r'(<meta name="description" content=")([^"]*)(")')
LIM = 155


_WEAK = {"und", "oder", "der", "die", "das", "des", "dem", "den", "ein", "eine", "einer", "eines", "bei", "im", "in", "von",
         "vom", "zu", "zum", "zur", "mit", "für", "auf", "an", "am", "als", "bis", "nach", "aus", "um", "ohne", "sowie", "wie",
         "wann", "was", "wer", "ist"}
_OPEN = {"die", "der", "das", "was", "wobei", "sodass", "weil", "wenn", "und", "aber", "oder", "sowie", "während", "dabei",
         "meist", "oft", "häufig", "doch", "denn", "wo", "wie", "dass", "damit", "bevor", "sobald", "obwohl", "bei", "mit",
         "ohne", "nach", "vor", "wann", "warum", "welche", "dem", "den", "deren", "dessen", "wodurch", "womit", "worauf",
         "meistens", "zudem", "jedoch", "bis", "ein", "eine", "einem", "einen", "wird", "werden", "kann"}


def _trim(s):
    s = s.rstrip(" ,;:—–-/(")
    while True:
        m = re.search(r"\s+(\S+)$", s)
        if m and m.group(1).lower().strip(",;:") in _WEAK:
            s = s[:m.start()].rstrip(" ,;:—–-/(")
        else:
            return s


def klausel(d):
    best = None
    for m in re.finditer(r"([,;])\s+(\S+)|\s[—–]\s|:\s", d[:LIM + 25]):
        if m.group(1) == "," and m.group(2).lower() not in _OPEN:
            continue
        cand = _trim(d[:m.start()])
        if 80 <= len(cand) + 1 <= LIM:
            best = cand
    return best + "." if best else None


def kuerzen(d):
    teile = SENT.split(d)
    while len(teile) > 1 and len(" ".join(teile)) > LIM:
        teile.pop()
    n = " ".join(teile)
    if 70 <= len(n) <= LIM and n[-1] in ".!?":
        return n, "satz"
    if d.endswith("…"):
        c = d[:-1][:LIM - 1]
        c = c[:c.rfind(" ")].rstrip(" ,;:—–-/(") if " " in c else c
        return c + "…", "ellipse"
    k = klausel(d)
    if k:
        return k, "klausel"
    return None, "offen"


def main():
    z = {"noindex": 0, "kasten_entfernt": 0, "desc_geprueft": 0, "satz": 0, "ellipse": 0, "klausel": 0}
    offen = []
    for f in sorted(glob.glob(os.path.join(ROOT, "**/index.html"), recursive=True)) + [os.path.join(ROOT, "index.html")]:
        rel = os.path.relpath(f, ROOT)
        if rel.startswith(("assets", "tools", "build")):
            continue
        t = open(f, encoding="utf-8", errors="ignore").read()
        neu = t
        if "noindex" in t[:6000]:
            z["noindex"] += 1
            if "adsbygoogle" in t:
                neu = SEC.sub("", neu)
                neu = INL.sub("", neu)
                if "adsbygoogle" in neu.split("<script>(adsbygoogle", 1)[0] and "<ins " in neu:
                    offen.append((rel, "Kasten nicht vollstaendig entfernt"))
                z["kasten_entfernt"] += 1
        else:
            m = DESC.search(t)
            if m:
                d = html.unescape(m.group(2))
                if len(d) > LIM:
                    z["desc_geprueft"] += 1
                    n, art = kuerzen(d)
                    if n is None:
                        offen.append((rel, d))
                    else:
                        z[art] += 1
                        esc = html.escape(n, quote=True).replace("&#x27;", "'")
                        neu = neu.replace(m.group(2), esc)
                        for p in ('og:description" content="', 'twitter:description" content="'):
                            neu = re.sub(re.escape(p) + re.escape(m.group(2)), p + esc.replace("\\", "\\\\"), neu)
        if APPLY and neu != t:
            open(f, "w", encoding="utf-8").write(neu)
    print(z)
    print(f"offen (von Hand): {len(offen)}")
    for r in offen[:60]:
        print("  ", r[0], "|", r[1][:170])


main()

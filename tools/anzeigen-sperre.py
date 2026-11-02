#!/usr/bin/env python3
"""Anzeigen-Sperre (BL 02.11.2026): entfernt alle Anzeigenblöcke (<div class="ad-net" data-ad-consent>) auf den Seiten der Liste
tools/anzeigen-sperrliste.txt (ICD-Kapitel F, psychische Gesundheit, Sexualität, Sucht, Suizid; Jurist-Einschätzung: sensible Kategorie, keine Anzeigen).
Optional --noindex <slug> setzt robots auf noindex,follow (F66-Gruppenseite).
Aufruf im Repo-Root: python3 tools/anzeigen-sperre.py [--dry] [--noindex slug ...]
Meldet Zahl der Seiten und Blöcke vorher/nachher. adsbygoogle-Skript auf anderen Seiten bleibt unberührt."""
import re, sys
dry = "--dry" in sys.argv
ni = [sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == "--noindex"]
AD1 = re.compile(r'<section class="section"><div class="wrap"><div class="ad-net" data-ad-consent>.*?</div></div></section>', re.S)
AD2 = re.compile(r'<div class="ad-net" data-ad-consent>.*?</div>', re.S)
slugs = [l.strip() for l in open("tools/anzeigen-sperrliste.txt", encoding="utf-8") if l.strip() and not l.startswith("#")]
seiten = vorher = nachher = bloecke = 0
for s in slugs:
    f = f"wissen/{s}/index.html"
    try:
        t = open(f, encoding="utf-8").read()
    except OSError:
        continue
    b = len(AD2.findall(t)); bloecke += b
    t2 = AD2.sub("", AD1.sub("", t))
    vorher += t.count("adsbygoogle"); nachher += t2.count("adsbygoogle")
    if s in ni:
        t2 = re.sub(r'(<meta name="robots" content=")[^"]*(")', r'\1noindex,follow\2', t2, count=1)
    if t2 != t:
        seiten += 1
        if not dry:
            open(f, "w", encoding="utf-8").write(t2)
print(f"Seiten geändert: {seiten} von {len(slugs)} | Anzeigenblöcke {bloecke} -> 0 | adsbygoogle-Vorkommen {vorher} -> {nachher}" + (" (Trockenlauf)" if dry else ""))

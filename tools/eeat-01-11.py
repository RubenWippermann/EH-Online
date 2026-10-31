#!/usr/bin/env python3
"""E-E-A-T-Zeile (SEO/GEO 01.11.): sichtbare Zeile unter der H1 beginnt mit "Stand: <letzte Aenderung oder Veroeffentlichung>",
danach ggf. "Veroeffentlicht", "Redaktion"; bei Seiten mit verifizierten Primaerquellen zusaetzlich "Grundlage: <Quellen>".
Article-Schema: dateModified ergaenzen (= datePublished), wo es fehlt. Kein "fachlich geprueft" (keine Pruefung belegt).
Aufruf im Repo-Root: python3 tools/eeat-01-11.py [--dry] <Pfad zu wissen_primaerquellen.py>"""
import re, sys, glob, os, importlib.util
dry = '--dry' in sys.argv
args = [a for a in sys.argv[1:] if not a.startswith('--')]
spec = importlib.util.spec_from_file_location('wp', args[0]); wp = importlib.util.module_from_spec(spec); spec.loader.exec_module(wp)
PRIM = wp.PRIMAER
D = r'(\d{1,2}\. [^\s·<]+\.? \d{4}|\d{1,2}\. [A-Za-zäöü]+ \d{4})'
KS = re.compile(r'(<p class="muted k-stand"[^>]*>)(.*?)(</p>)', re.S)
def umbau(inner, slug):
    if inner.startswith('Stand:'):
        return inner
    teile = [t.strip() for t in inner.split(' · ')]
    v = g = None; rest = []
    for t in teile:
        if t.startswith('Veröffentlicht: '): v = t[len('Veröffentlicht: '):]
        elif t.startswith('Zuletzt geändert: '): g = t[len('Zuletzt geändert: '):]
        else: rest.append(t)
    stand = g or v
    if not stand: return inner
    out = [f'Stand: {stand}']
    if g and v and g != v: out.append(f'Veröffentlicht: {v}')
    out += rest
    if slug in PRIM:
        namen = []
        for n, *_ in PRIM[slug]:
            k = n.split(':')[0].strip()
            if k not in namen: namen.append(k)
        out.append('Grundlage: ' + '; '.join(namen))
    return ' · '.join(out)
n_ks = n_gl = n_dm = 0
for f in glob.glob('**/index.html', recursive=True):
    t = open(f, encoding='utf-8').read(); o = t
    m = re.match(r'wissen/([^/]+)/index\.html$', f); slug = m.group(1) if m else None
    def sub(m):
        return m.group(1) + umbau(m.group(2), slug) + m.group(3)
    t2 = KS.sub(sub, t, count=1)
    if t2 != t:
        n_ks += 1
        if 'Grundlage:' in t2: n_gl += 1
        t = t2
    # dateModified im Article-Schema ergaenzen
    def dm(m):
        blk = m.group(0)
        if '"dateModified"' in blk or '"datePublished"' not in blk: return blk
        return re.sub(r'("datePublished":\s*"(\d{4}-\d{2}-\d{2})")', r'\1,"dateModified":"\2"', blk, count=1)
    t3 = re.sub(r'<script type="application/ld\+json">.*?</script>', dm, t, flags=re.S)
    if t3 != t: n_dm += 1; t = t3
    if t != o and not dry:
        open(f, 'w', encoding='utf-8').write(t)
print(f'Stand-Zeile umgebaut: {n_ks} (davon mit Grundlage: {n_gl}); dateModified ergaenzt: {n_dm}', '(Trockenlauf)' if dry else '')

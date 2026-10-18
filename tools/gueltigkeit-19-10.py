#!/usr/bin/env python3
"""19.10.: unbelegte Gueltigkeitsaussage auf /wissen/erste-hilfe-kurs-fuehrerschein/ durch belegte Formulierung ersetzen.
Idempotent, gezielt (kein Komplettbau). Im Repo-Root: python3 tools/gueltigkeit-19-10.py"""
import re, json
F = 'wissen/erste-hilfe-kurs-fuehrerschein/index.html'
N = '§ 19 FeV nennt für die Bescheinigung keine Gültigkeitsfrist.'
R = [('vorgelegt und ist zeitlich unbegrenzt gültig — eine erneute Teilnahme ist für den Führerschein selbst nicht vorgeschrieben.', 'vorgelegt. ' + N),
     ('Nein, der Nachweis ist für den Führerschein zeitlich unbegrenzt gültig.', N)]
s = open(F, encoding='utf-8').read()
for o, n in R:
    c = s.count(o)
    assert c in (0, 1, 2), c
    s = s.replace(o, n)
assert 'zeitlich unbegrenzt' not in s
for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
    json.loads(m)
open(F, 'w', encoding='utf-8').write(s)

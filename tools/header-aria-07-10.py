#!/usr/bin/env python3
"""Header-aria-label (Logo + Instagram) auf alle index.html/404.html; idempotent. Aufruf: [--dry] im Repo-Root."""
import os,sys
O1='aria-label="Erste Hilfe Kurse — Startseite"';N1='aria-label="Erste Hilfe Kurse – Kurs finden · Inhouse anfragen – Startseite"'
O2='aria-label="Personal Paramedic auf Instagram"';N2='aria-label="@personal.paramedic auf Instagram"'
dry='--dry' in sys.argv;old=new=chg=0;odd=[];changed=[]
for dp,dn,fs in os.walk('.'):
    dn[:]=[d for d in dn if d!='.git']
    for f in fs:
        if not f.endswith('.html'):continue
        p=os.path.join(dp,f);t=open(p,encoding='utf-8',newline='').read()
        a=O1 in t or O2 in t;b=N1 in t and N2 in t
        if a:
            old+=1
            if t.count(O1)!=1 or t.count(O2)!=1:odd.append(p);continue
            chg+=1;changed.append(p)
            if not dry:open(p,'w',encoding='utf-8',newline='').write(t.replace(O1,N1).replace(O2,N2))
        elif b:new+=1
print(f'alt-vorher={old} neu-bereits={new} geaendert={chg} abweichend={len(odd)}',odd[:10])
open('/dev/stdout' if dry else os.devnull,'w').write('')

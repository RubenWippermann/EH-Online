#!/usr/bin/env python3
"""Leerzeichen zwischen </b> und <small> im Logo-Link (axe 'KurseKurs'); idempotent. [--dry] im Repo-Root."""
import os,sys
O='Kurse</b><small>Kurs finden';N='Kurse</b> <small>Kurs finden'
dry='--dry' in sys.argv;vor=nach=chg=0;odd=[]
for dp,dn,fs in os.walk('.'):
    dn[:]=[d for d in dn if d!='.git']
    for f in fs:
        if not f.endswith('.html'):continue
        p=os.path.join(dp,f);t=open(p,encoding='utf-8',newline='').read()
        if O in t:
            vor+=1
            if t.count(O)!=1:odd.append(p);continue
            chg+=1
            if not dry:open(p,'w',encoding='utf-8',newline='').write(t.replace(O,N))
        elif N in t:nach+=1
print(f'ohne-space={vor} mit-space-bereits={nach} geaendert={chg} abweichend={len(odd)}',odd[:10])

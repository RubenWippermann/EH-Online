#!/usr/bin/env python3
"""<form data-api=...> ohne method -> method="post" + noscript-Hinweis (Telefon/E-Mail aus Impressum). Idempotent, [--dry]. Im Repo-Root."""
import os,re,sys
dry='--dry' in sys.argv;vor=nach=chg=0;andere=[]
NS='<noscript><p class="muted">Zum Absenden wird JavaScript benötigt. Ohne JavaScript erreichst du uns telefonisch unter <a href="tel:+4955277488495">05527 7488495</a> oder per E-Mail an <a href="mailto:info@personal-paramedic.de">info@personal-paramedic.de</a>.</p></noscript>\n'
for dp,dn,fs in os.walk('.'):
    dn[:]=[d for d in dn if d!='.git']
    for f in fs:
        if not f.endswith('.html'):continue
        p=os.path.join(dp,f);t=open(p,encoding='utf-8',newline='').read()
        for m in re.findall(r'<form\b[^>]*>',t):
            if 'method=' not in m and 'data-api=' in m:vor+=1
            elif 'method="post"' in m:nach+=1
            else:andere.append((p,m[:80]))
        n=re.sub(r'<form\b([^>]*data-api="[^"]*"[^>]*)>',lambda m:m.group(0) if 'method=' in m.group(1) else '<form method="post"'+m.group(1)+'>\n'+NS,t)
        if n!=t:
            chg+=1
            if not dry:open(p,'w',encoding='utf-8',newline='').write(n)
print(f'ohne-method={vor} mit-post={nach} geaendert={chg} andere-forms={andere}')

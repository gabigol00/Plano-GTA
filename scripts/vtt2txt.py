import re,sys
def parse(p):
    out=[];prev=''
    t=None
    for ln in open(p,encoding='utf-8'):
        ln=ln.rstrip('\n')
        m=re.match(r'(\d+):(\d+):(\d+\.\d+) -->',ln)
        if m: t=int(m[1])*3600+int(m[2])*60+float(m[3]); continue
        if t is None or not ln.strip() or ln.startswith(('WEBVTT','Kind','Language')): continue
        if '<c>' in ln or re.search(r'<\d\d:',ln): 
            txt=re.sub(r'<[^>]+>','',ln).strip()
            if txt and txt!=prev: out.append((t,txt)); prev=txt
    return out
if __name__=='__main__':
    for t,x in parse(sys.argv[1]): print(f'{int(t//60)}:{int(t%60):02d} {x}')

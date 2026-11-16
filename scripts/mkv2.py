#!/usr/bin/env python3
"""Template v2: header (foto+nome+@) + titulo grande + video 16:9 em moldura + legenda PT-BR. Uso: mkv2.py [--test] [ids...]"""
import subprocess, sys, os, textwrap
from PIL import Image, ImageDraw, ImageFont
SP='/tmp/claude-0/-home-claude/226eec96-10a6-5926-bb02-d1348b22356a/scratchpad/p/'
DUB='/mnt/user-data/outputs/gta6-dublados/'; CUT='/mnt/user-data/outputs/gta6-cortes/'
FD='/usr/share/fonts/truetype/google-fonts/'
AVATAR='/mnt/user-data/uploads/Canal/gta6/perfil.jpg'
PLAT={'tiktok':'@gta6zone.br0','insta':'@gta6z.onebr'}
# id, nome, fonte, ass, titulo
V=[
 ('01','dub-real-vs-gta6',DUB+'02-real-vs-gta6-dublado.mp4',None,'ESSE VÍDEO DA VIDA REAL QUASE ENGANOU TODO MUNDO'),
 ('02','dub-rockstar-miami',DUB+'03-rockstar-miami-dublado.mp4',None,'A ROCKSTAR POSTOU O VÍDEO REAL EM MIAMI E O GTA 6 RECRIOU A CENA'),
 ('03','dub-npcs-realistas',DUB+'04-npcs-realistas-dublado.mp4',None,'CADA NPC FAZENDO UMA COISA DIFERENTE NO GTA 6'),
 ('11','podpah-fivem',CUT+'p1-fivem-rockstar.mp4',SP+'p1-fivem-rockstar.ass','A ROCKSTAR COMPROU O FIVEM. E AGORA?'),
 ('12','podpah-criadores',CUT+'p2-novos-criadores.mp4',SP+'p2-novos-criadores.ass','VÃO SURGIR NOVOS CRIADORES COM O GTA 6?'),
 ('13','davy-variedade-npcs',CUT+'d1-variedade-npcs.mp4',SP+'d1-variedade-npcs.ass','A VARIEDADE DE NPCS DO GTA 6 É ABSURDA'),
 ('14','davy-bar-detalhes',CUT+'d2-bar-e-detalhes.mp4',SP+'d2-bar-e-detalhes.ass','O NÍVEL DE DETALHE NO BAR DO GTA 6'),
 ('15','davy-parece-ia',CUT+'d3-parece-ia.mp4',SP+'d3-parece-ia.ass','O GTA 6 PARECE IA, MAS É JOGO'),
 ('16','davy-trailer-boate',CUT+'d4-trailer-boate.mp4',SP+'d4-trailer-boate.ass','O TRAILER DA BOATE DO GTA 6'),
 ('17','davy-30fps-ps5pro',CUT+'d5-30fps-ps5pro.mp4',SP+'d5-30fps-ps5pro.ass','GTA 6 NO PS5 PRO: 30 FPS?'),
]
def overlay(plat, title, path):
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    av=Image.open(AVATAR).convert('RGB'); s=min(av.size); av=av.crop(((av.width-s)//2,(av.height-s)//2,(av.width+s)//2,(av.height+s)//2)).resize((150,150))
    m=Image.new('L',(150,150),0); ImageDraw.Draw(m).ellipse((0,0,149,149),fill=255)
    im.paste(av,(70,150),m)
    d.text((250,172),'GTA6ZONE.BR',font=ImageFont.truetype(FD+'Poppins-Bold.ttf',52),fill='white')
    d.text((252,238),PLAT[plat],font=ImageFont.truetype(FD+'Poppins-Regular.ttf',38),fill=(200,200,205,255))
    for fs in (66,58,52,46):
        f=ImageFont.truetype(FD+'Poppins-Bold.ttf',fs)
        lines=[]; cur=''
        for w in title.split():
            t=(cur+' '+w).strip()
            if d.textlength(t,font=f)>940 and cur: lines.append(cur); cur=w
            else: cur=t
        lines.append(cur)
        if len(lines)<=3: break
    y=360
    for l in lines:
        x=(1080-d.textlength(l,font=f))/2
        d.text((x,y),l,font=f,fill='white',stroke_width=3,stroke_fill='black'); y+=int(fs*1.27)
    im.save(path)
def dur(p): return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',p]).decode())
test='--test' in sys.argv
ids=[a for a in sys.argv[1:] if not a.startswith('--')]
for vid,name,src,ass,title in V:
    if ids and vid not in ids: continue
    D=dur(src)
    for plat in PLAT:
        ov=f'/tmp/sc/ov/{vid}-{plat}.png'; overlay(plat,title,ov)
        out=f'/mnt/user-data/outputs/gta6-v2/{plat}/{vid}-{name}.mp4'
        vf=("[0:v]crop=1080:608:0:430,split=2[f][g];"
            "[g]scale=-2:1920,crop=1080:1920,boxblur=28:3,eq=brightness=-0.38[b];"
            "[b][f]overlay=0:640[v0];[v0][1:v]overlay=0:0[v1];")
        vf+= f"[v1]ass={ass}:fontsdir=/usr/share/fonts/truetype/dejavu[v]" if ass else "[v1]null[v]"
        vb=int(9.0e6*8/D-170000)
        if test:
            cmd=['ffmpeg','-v','error','-y','-ss','6','-i',src,'-loop','1','-i',ov,'-filter_complex',vf,'-map','[v]','-frames:v','1',f'/tmp/sc/t-{vid}-{plat}.png']
        else:
            cmd=['ffmpeg','-v','error','-y','-i',src,'-loop','1','-framerate','30','-i',ov,'-filter_complex',vf,'-map','[v]','-map','0:a','-t',f'{D:.2f}',
                 '-c:v','libx264','-preset','veryfast','-b:v',str(vb),'-maxrate',str(int(vb*1.3)),'-bufsize',str(vb*2),'-pix_fmt','yuv420p','-r','30','-c:a','aac','-b:a','160k','-movflags','+faststart',out]
        subprocess.run(cmd,check=True)
        if not test: print(vid,plat,round(os.path.getsize(out)/1e6,2),'MB',flush=True)

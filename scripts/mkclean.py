#!/usr/bin/env python3
"""Corta hollow.mp4 em clipes 9:16 (fundo desfocado + video 16:9 + legenda PT-BR queimada)."""
import re, subprocess, os, sys
SRC = '/mnt/user-data/uploads/Canal/gta6/fonte/hollow.mp4'
OUT = '/mnt/user-data/outputs/gta6-dublar'
WORK = '/tmp/claude-0/-home-claude/226eec96-10a6-5926-bb02-d1348b22356a/scratchpad/h'
os.makedirs(OUT, exist_ok=True)

def sec(t):
    m, s = t.split(':'); return int(m) * 60 + int(s)

# (inicio_seg_original, texto PT-BR)
SEG = [
 ('0:15', 'Quanto mais perto do lançamento do GTA 6, mais maluca fica a semana. Os próximos 7 dias vão ser absurdos.'),
 ('0:23', 'Vou mostrar um gameplay de GTA 6 que ficou 45 minutos na minha tela.'),
 ('0:30', 'Quando vi, ignorei: parecia real demais, devia ser IA. Mas parece que não é.'),
 ('0:41', 'Vou explicar. Primeiro vi os carros: Corvette, Lamborghini, clássicos.'),
 ('0:46', 'A GTA normalmente não usa marcas reais de carro. Esse foi o primeiro sinal estranho.'),
 ('0:54', 'Aí achei um vídeo da vida real quase igual. Vou colocar os dois lado a lado.'),
 ('1:02', 'À esquerda, a vida real. À direita, o GTA 6. Achei que alguém tinha passado a filmagem numa IA'),
 ('1:11', 'e feito parecer gameplay de GTA 6. Ignorei.'),
 ('1:18', 'Mas olhando de perto, como o Potato apontou...'),
 ('1:23', 'Dá pra ver que os NPCs são NPCs reais de GTA 6.'),
 ('1:31', 'No gameplay, à direita, aparece o Bobby Hurricane\'s.'),
 ('1:38', 'Rede de fast food que aparece no GTA Online e vai estar no GTA 6.'),
 ('1:45', 'GTA 6. Mas não é só isso.'),
 ('1:49', 'A maior confirmação: a própria Rockstar postou o vídeo real no Instagram.'),
 ('1:54', 'O vídeo vem do OnlyInDade, página sobre o que rola no sul da Flórida.'),
 ('2:02', 'Os NPCs são muito parecidos com a filmagem real. Parece que recriaram essa cena'),
 ('2:11', 'de quando a Rockstar levou esses carros pra Miami Beach, usando assets do GTA 6.'),
 ('2:19', 'Dá pra dizer que é assim que o jogo vai ficar.'),
 ('2:24', 'Talvez os consoles realmente consigam rodar um jogo assim. É ridículo.'),
 ('2:33', 'Tenho dificuldade de entender como isso é possível.'),
 ('2:38', 'A iluminação, o céu, os NPCs. O comportamento deles é incrivelmente realista.'),
 ('2:48', 'Cada NPC faz uma coisa diferente. A imagem está comprimida, mas dá pra ver bastante.'),
 ('2:56', 'Tem um cara de cadeira de rodas elétrica e um casal que dizem ser a Lucia e o Jason.'),
 ('3:06', 'Não tenho certeza. Sabemos que dá pra usar o celular em várias coisas no GTA 6.'),
 ('3:12', 'Talvez dê pra gravar assim, em primeira pessoa, dentro do jogo.'),
 ('3:21', 'Os devs têm ferramentas diferentes das nossas, mas ver cada NPC fazendo algo diferente'),
 ('3:32', 'é absurdo. Gente tirando selfie, gente filmando os lowriders, os clássicos...'),
 ('3:37', 'Já fui à Ocean Drive tantas vezes que perdi a conta.'),
 ('3:48', 'Parece vida real. Nunca vi um jogo tão realista comparado com a realidade.'),
 ('3:57', 'Dá pra enganar qualquer um. Por uns 5 a 10 minutos eu fui enganado,'),
 ('4:06', 'achei que era real, depois que era IA imitando o GTA 6.'),
 ('4:21', 'Divulgaram partes da entrevista. Tudo será revelado ainda esta semana.'),
 ('4:29', 'A Rockstar está em Miami desde 2015, pesquisando há mais de uma década'),
 ('4:37', 'Estudaram os bairros, a vida noturna, a arquitetura, a cultura local.'),
 ('4:44', 'Quase 5.000 pessoas trabalharam no GTA 6.'),
 ('4:51', 'O Rob Nelson diz que o jogo é tão enorme que ninguém entende todas as partes.'),
 ('4:58', 'Achamos que sabemos o tamanho do jogo, mas só vamos ter ideia'),
 ('5:06', 'quando ele sair, em cerca de 7 dias.'),
 ('5:14', 'Jogando de Jason, dá pra ele comer um cachorro-quente, pausar e comer um donut.'),
 ('5:23', 'Se você segura um pack de cerveja e corre, ele ajusta o jeito de segurar o pack.'),
 ('5:31', 'A cerveja dentro da garrafa também balança quando você anda e corre.'),
 ('5:39', 'Esse detalhe já apareceu em um dos primeiros trailers do GTA 6.'),
 ('5:47', 'Não me surpreende: é o esperado da Rockstar, como no Red Dead 2.'),
 ('5:54', 'Vai ter muito detalhe e isso leva o jogo a outro nível.'),
]
SEG = [(sec(t), x) for t, x in SEG]

# cortes (inicio, fim) em segundos do original, antes de ajustar em silêncios
CUTS = [
 ('02-real-vs-gta6',   sec('0:54'), sec('1:49')),
 ('03-rockstar-miami', sec('1:49'), sec('2:38')),
 ('04-npcs-realistas', sec('2:38'), sec('3:32')),
]

# silêncios para ajustar cortes
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', SRC, '-af', 'silencedetect=noise=-32dB:d=0.22', '-f', 'null', '-'],
                   capture_output=True, text=True)
starts = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', r.stderr)]
ends = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', r.stderr)]
def snap_start(t):   # prefere fim de silêncio logo antes/depois de t
    c = [e for e in ends if abs(e - t) <= 1.6]
    return min(c, key=lambda e: abs(e - t)) - 0.05 if c else t
def snap_end(t):     # prefere início de silêncio
    c = [s for s in starts if abs(s - t) <= 1.6]
    return min(c, key=lambda s: abs(s - t)) + 0.15 if c else t

def ass_time(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f'{h}:{m:02d}:{s:05.2f}'

HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Cap,DejaVu Sans,54,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,5,1,2,100,180,470,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""

report = []
for name, a, b in CUTS:
    s = snap_start(a); e = snap_end(b)
    dur = e - s
    lines = []
    for i, (t0, txt) in enumerate(SEG):
        t1 = SEG[i + 1][0] if i + 1 < len(SEG) else t0 + 8
        if t1 <= s or t0 >= e: continue
        ls = max(t0, s) - s; le = min(t1, e) - s
        if le - ls < 0.4: continue
        lines.append(f'Dialogue: 0,{ass_time(ls)},{ass_time(le)},Cap,,0,0,0,,{txt}')
    asspath = f'{WORK}/{name}.ass'
    open(asspath, 'w', encoding='utf-8').write(HEADER + '\n'.join(lines) + '\n')
    out = f'{OUT}/{name}.mp4'
    vf = ("[0:v]split=2[bg][fg];"
          "[bg]scale=-2:1920,crop=1080:1920,boxblur=28:3,eq=brightness=-0.12[b];"
          "[fg]scale=1080:-2[f];"
          "[b][f]overlay=0:430[v0];"
          "[v0][1:v]overlay=60:330[v]")
    cmd = ['ffmpeg', '-v', 'error', '-y', '-ss', f'{s:.2f}', '-t', f'{dur:.2f}', '-i', SRC, '-i', '/home/claude/biblioteca-video/gta6/wm.png',
           '-filter_complex', vf, '-map', '[v]', '-map', '0:a', '-c:v', 'libx264', '-preset', 'veryfast',
           '-crf', '22', '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', out]
    subprocess.run(cmd, check=True)
    report.append(f'{name}: {s:.1f}-{e:.1f}s ({dur:.1f}s) {os.path.getsize(out)/1e6:.1f}MB')
print('\n'.join(report))

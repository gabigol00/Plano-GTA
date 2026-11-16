#!/usr/bin/env python3
"""Corta hollow.mp4 em clipes 9:16 (fundo desfocado + video 16:9 + legenda PT-BR queimada)."""
import re, subprocess, os, sys
SRCDIR = '/mnt/user-data/uploads/Canal/gta6/fonte/'
OUT = '/mnt/user-data/outputs/gta6-cortes'
WORK = '/tmp/claude-0/-home-claude/226eec96-10a6-5926-bb02-d1348b22356a/scratchpad/p'
os.makedirs(OUT, exist_ok=True)

import html
sys.path.insert(0,'/home/claude/biblioteca-video/gta6')
from vtt2txt import parse
def sec(t):
    m, s_ = t.split(':'); return int(m) * 60 + int(s_)
def clean(x):
    x = html.unescape(x)
    x = re.sub(r'\[[^\]]*\]', '', x)
    x = x.replace('>>', '').replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', x).strip()
SRCS = {'podpah': 'podpah', 'dchoque': 'davy-choque', 'dtrailer': 'davy-trailer'}
CUTS = [
 ('p1-fivem-rockstar',   'podpah',   sec('3:23'),  sec('4:36')),
 ('p2-novos-criadores',  'podpah',   sec('4:42'),  sec('6:10')),
 ('d1-variedade-npcs',   'dchoque',  sec('1:20'),  sec('2:41')),
 ('d2-bar-e-detalhes',   'dchoque',  sec('6:43'),  sec('8:10')),
 ('d3-parece-ia',        'dchoque',  sec('8:10'),  sec('9:31')),
 ('d4-trailer-boate',    'dtrailer', sec('0:00'),  sec('1:24')),
 ('d5-30fps-ps5pro',     'dtrailer', sec('11:40'), sec('13:32')),
]
def caps(lines, s, e):
    L = [(t, clean(x)) for t, x in lines if s - 0.5 <= t < e]
    L = [(t, x) for t, x in L if x]
    out = []; cur = ''; t0 = None
    for t, x in L:
        if t0 is None: t0 = t
        if cur and (len(cur) + 1 + len(x) > 72):
            out.append((t0, cur)); cur = x; t0 = t
        else:
            cur = (cur + ' ' + x).strip()
        if cur.endswith(('.', '?', '!')) and len(cur) > 40:
            out.append((t0, cur)); cur = ''; t0 = None
    if cur: out.append((t0, cur))
    return out

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
for name, key, a, b in CUTS:
    SRC = SRCDIR + SRCS[key] + '.mp4'
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', SRC, '-ss', str(max(0,a-3)), '-t', str(b-a+6), '-af', 'silencedetect=noise=-32dB:d=0.22', '-f', 'null', '-'], capture_output=True, text=True)
    starts = [float(x) + max(0,a-3) for x in re.findall(r'silence_start: ([\d.]+)', r.stderr)]
    ends = [float(x) + max(0,a-3) for x in re.findall(r'silence_end: ([\d.]+)', r.stderr)]
    c = [e_ for e_ in ends if abs(e_ - a) <= 1.6]; s_ = min(c, key=lambda e_: abs(e_ - a)) - 0.05 if c else a
    c = [x for x in starts if abs(x - b) <= 1.6]; e = min(c, key=lambda x: abs(x - b)) + 0.15 if c else b
    dur = e - s_
    cl = caps(parse(f'{SRCDIR}{SRCS[key]}.pt-orig.vtt'), s_, e)
    lines = []
    for i, (t0, txt) in enumerate(cl):
        t1 = cl[i + 1][0] if i + 1 < len(cl) else e
        ls = max(t0, s_) - s_; le = min(t1, e) - s_
        if le - ls < 0.4: continue
        lines.append(f'Dialogue: 0,{ass_time(ls)},{ass_time(le)},Cap,,0,0,0,,{txt}')
    asspath = f'{WORK}/{name}.ass'
    open(asspath, 'w', encoding='utf-8').write(HEADER + '\n'.join(lines) + '\n')
    out = f'{OUT}/{name}.mp4'
    vf = ("[0:v]split=2[bg][fg];"
          "[bg]scale=-2:1920,crop=1080:1920,boxblur=28:3,eq=brightness=-0.12[b];"
          "[fg]scale=1080:-2[f];"
          "[b][f]overlay=0:430[v0];"
          "[v0][1:v]overlay=60:330,"
          f"ass={asspath}:fontsdir=/usr/share/fonts/truetype/dejavu[v]")
    cmd = ['ffmpeg', '-v', 'error', '-y', '-ss', f'{s_:.2f}', '-t', f'{dur:.2f}', '-i', SRC, '-i', '/home/claude/biblioteca-video/gta6/wm.png',
           '-filter_complex', vf, '-map', '[v]', '-map', '0:a', '-c:v', 'libx264', '-preset', 'veryfast',
           '-crf', '22', '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', out]
    subprocess.run(cmd, check=True)
    report.append(f'{name}: {s_:.1f}-{e:.1f}s ({dur:.1f}s) caps={len(lines)} {os.path.getsize(out)/1e6:.1f}MB')
print('\n'.join(report))

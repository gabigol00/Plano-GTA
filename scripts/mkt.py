#!/usr/bin/env python3
"""Corta hollow.mp4 em clipes 9:16 (fundo desfocado + video 16:9 + legenda PT-BR queimada)."""
import re, subprocess, os, sys
SRC = '/mnt/user-data/uploads/Canal/gta6/fonte/ign.mp4'
OUT = '/mnt/user-data/outputs/gta6-cortes'
WORK = '/tmp/claude-0/-home-claude/226eec96-10a6-5926-bb02-d1348b22356a/scratchpad/t'
os.makedirs(OUT, exist_ok=True)

def sec(t):
    m, s = t.split(':'); return int(m) * 60 + int(s)

def sec(t):
    m, s = t.split(':'); return int(m) * 60 + int(s)
SEG = [(0,'Trailer de recursos do GTA 6 no PS5'),(5,' ')]
CUTS = [('t1-trailer-ps5', 0, 49)]

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
        if le - ls < 0.4 or not txt.strip(): continue
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
    cmd = ['ffmpeg', '-v', 'error', '-y', '-ss', f'{s:.2f}', '-t', f'{dur:.2f}', '-i', SRC, '-i', '/home/claude/biblioteca-video/gta6/wm.png',
           '-filter_complex', vf, '-map', '[v]', '-map', '0:a', '-c:v', 'libx264', '-preset', 'veryfast',
           '-crf', '22', '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', out]
    subprocess.run(cmd, check=True)
    report.append(f'{name}: {s:.1f}-{e:.1f}s ({dur:.1f}s) {os.path.getsize(out)/1e6:.1f}MB')
print('\n'.join(report))

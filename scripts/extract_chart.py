#!/usr/bin/env python3
"""extract_chart.py — แปลง response ของ bodygraph.com API (hd-data) เป็น chart.json มาตรฐานของ kit
พร้อมดึง SVG ออกเป็นไฟล์ และ render PNG (ต้องมี rsvg-convert)

ใช้:  python3 extract_chart.py api_response.json <outdir> [--bg "#d0e0e3"]
ได้:  <outdir>/chart.json  <outdir>/chart.svg  <outdir>/chart.png
chart.json ใช้ schema เดียวกับ hd_calc.py (fallback) บวก field จาก API
"""
import json, sys, os, subprocess, argparse

CENTERS = {'Head':[64,61,63],'Ajna':[47,24,4,17,43,11],'Throat':[62,23,56,35,12,45,33,8,31,20,16],'G':[1,13,25,46,2,15,10,7],'Heart':[21,40,26,51],'Sacral':[5,14,29,59,9,3,42,27,34],'Spleen':[48,57,44,50,32,28,18],'SolarPlexus':[6,37,22,36,30,55,49],'Root':[53,60,52,19,39,41,58,38,54]}
GATE2CENTER = {g:c for c,gs in CENTERS.items() for g in gs}
PLANETS = ['Sun','Earth','North Node','South Node','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune','Pluto']
CENTER_MAP = {'head center':'Head','ajna center':'Ajna','throat center':'Throat','g center':'G','heart center':'Heart',
              'spleen center':'Spleen','splenic center':'Spleen','sacral center':'Sacral','solar plexus center':'SolarPlexus','root center':'Root'}

def opt(o):
    if isinstance(o, dict): return o.get('option') or o.get('id') or o.get('name') or ''
    return o or ''

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('outdir'); ap.add_argument('--bg', default='#d0e0e3')
    a = ap.parse_args()
    d = json.load(open(a.src, encoding='utf-8')); P = d.get('Properties', {})
    os.makedirs(a.outdir, exist_ok=True)

    def side(name):
        out = {}
        for p in PLANETS:
            v = (d.get(name) or {}).get(p)
            if v: out[p.replace(' ', '')] = {'gate': int(v['Gate']), 'line': int(v['Line'])}
        return out

    channels = []
    for c in d.get('Channels', []):
        a_, b_ = [int(x) for x in str(c).replace(' ', '').split('-')]
        channels.append(sorted([a_, b_]))
    chart = {
        'source': 'bodygraph.com API',
        'birth_local': P.get('BirthDateLocalStandard') or P.get('BirthDateLocal'),
        'design_utc': P.get('DesignDateUtcStandard'),
        'type': opt(P.get('Type')), 'strategy': opt(P.get('Strategy')), 'authority': opt(P.get('InnerAuthority')),
        'profile': opt(P.get('Profile')).replace(' ', ''), 'definition': opt(P.get('Definition')),
        'incarnation_cross': opt(P.get('IncarnationCross')), 'signature': opt(P.get('Signature')), 'not_self': opt(P.get('NotSelfTheme')),
        'defined_centers': sorted({CENTER_MAP.get(c.lower(), c) for c in d.get('DefinedCenters', [])}),
        'open_centers': sorted({CENTER_MAP.get(c.lower(), c) for c in d.get('OpenCenters', [])}),
        'channels': sorted(channels),
        'all_gates': sorted({int(g) for g in ((d.get('Gates') or {}).values() if isinstance(d.get('Gates'), dict) else (d.get('Gates') or []))}),
        'activations': {'personality': side('Personality'), 'design': side('Design')},
        'variables': d.get('Variables'),
        'descriptions_en': {k: (P.get(k) or {}).get('description', '') for k in ('Type','Strategy','InnerAuthority','Profile','Definition','IncarnationCross')},
    }
    in_channels = {g for ch in chart['channels'] for g in ch}
    chart['hanging_gates'] = sorted(g for g in chart['all_gates'] if g not in in_channels)
    chart['gates_by_center'] = {c: sorted(g for g in chart['all_gates'] if GATE2CENTER.get(g) == c) for c in CENTERS}
    chart['gate_to_center'] = {str(g): GATE2CENTER.get(g) for g in chart['all_gates']}
    chart['gates_personality'] = sorted({v['gate'] for v in chart['activations']['personality'].values()})
    chart['gates_design'] = sorted({v['gate'] for v in chart['activations']['design'].values()})
    json.dump(chart, open(os.path.join(a.outdir, 'chart.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    svgk = next((k for k in d if k.lower() == 'svg'), None)
    if svgk and d[svgk]:
        svg_path = os.path.join(a.outdir, 'chart.svg'); open(svg_path, 'w', encoding='utf-8').write(d[svgk])
        png_path = os.path.join(a.outdir, 'chart.png')
        subprocess.run(['rsvg-convert', '-w', '1200', '-b', a.bg, svg_path, '-o', png_path], check=True)
        print('chart.json + chart.svg + chart.png ->', a.outdir)
    else:
        print('chart.json -> ', a.outdir, '| WARNING: ไม่มี SVG ใน response (ตรวจพารามิเตอร์ design) ใช้ bodygraph_render.py แทน')

if __name__ == '__main__':
    main()

"""bodygraph_render.py — วาด bodygraph เองจาก chart.json (fallback เมื่อไม่มี SVG จาก bodygraph.com)
ใช้: python3 bodygraph_render.py chart.json out.svg [--subtitle "21 March 1989 · 21:08 · Bangkok"]
แล้ว: rsvg-convert -w 1100 out.svg -o out.png
"""
import json, sys
chart = json.load(open(sys.argv[1]))
SUBTITLE = sys.argv[sys.argv.index('--subtitle')+1] if '--subtitle' in sys.argv else chart.get('birth_local','')
P = set(chart['gates_personality']); D = set(chart['gates_design'])
defined = set(chart['defined_centers'])
W,H = 1100,1180

# ---- gate anchors (body coordinates; body is translated right by OX) ----
OX = 120
G = {
 64:(420,128),61:(450,128),63:(480,128),
 47:(420,168),24:(450,168),4:(480,168),17:(417,205),43:(450,232),11:(483,205),
 62:(417,283),23:(450,283),56:(483,283),16:(398,305),20:(398,348),35:(502,305),12:(502,348),
 31:(422,387),8:(450,387),33:(478,387),45:(500,382),
 7:(432,452),1:(450,441),13:(468,452),10:(405,473),15:(410,531),25:(495,473),46:(490,531),2:(450,559),
 51:(520,524),21:(568,508),26:(532,566),40:(586,540),
 48:(305,614),57:(330,637),44:(354,651),50:(350,664),32:(333,676),28:(313,688),18:(293,700),
 5:(422,643),14:(450,643),29:(478,643),34:(398,667),27:(398,722),59:(502,703),42:(422,747),3:(450,747),9:(478,747),
 36:(595,614),22:(570,637),37:(546,651),6:(550,664),49:(567,676),55:(587,688),30:(607,700),
 53:(422,803),60:(450,803),52:(478,803),54:(398,827),38:(398,857),58:(398,887),19:(502,827),39:(502,857),41:(502,887),
}
CH = [(1,8),(2,14),(3,60),(4,63),(5,15),(6,59),(7,31),(9,52),(10,20),(10,34),(10,57),(11,56),(12,22),(13,33),(16,48),(17,62),(18,58),(19,49),(20,34),(20,57),(21,45),(23,43),(24,61),(25,51),(26,44),(27,50),(28,38),(29,46),(30,41),(32,54),(35,36),(37,40),(39,55),(42,53),(47,64),(34,57)]
COL = {'Head':'#F5D96B','Ajna':'#8FCB8F','Throat':'#C4A484','G':'#F5D96B','Heart':'#E8807A','Spleen':'#C4A484','Sacral':'#E8807A','SolarPlexus':'#C4A484','Root':'#C4A484'}
SHAPES = {
 'Head':  ('polygon','450,58 388,132 512,132'),
 'Ajna':  ('polygon','388,164 512,164 450,240'),
 'Throat':('rect','395,280,110,110'),
 'G':     ('polygon','450,438 512,500 450,562 388,500'),
 'Heart': ('polygon','512,514 598,502 548,586'),
 'Spleen':('polygon','228,588 228,722 362,655'),
 'Sacral':('rect','395,640,110,110'),
 'SolarPlexus':('polygon','672,588 672,722 538,655'),
 'Root':  ('rect','395,800,110,110'),
}
LABEL = {'Head':(450,112),'Ajna':(450,200),'Throat':(450,340),'G':(450,505),'Heart':(549,538),'Spleen':(272,660),'Sacral':(450,700),'SolarPlexus':(628,660),'Root':(450,860)}
LTXT = {'Head':'Head','Ajna':'Ajna','Throat':'Throat','G':'G','Heart':'Ego','Spleen':'Spleen','Sacral':'Sacral','SolarPlexus':'Solar\nPlexus','Root':'Root'}

GREY='#E3DED5'; BLACK='#2A2A2A'; RED='#D23B3B'; CREAM='#F7F3EC'; INK='#2B3A42'; MUTED='#7A8288'

def col(g):
    if g in P and g in D: return 'both'
    if g in P: return BLACK
    if g in D: return RED
    return None

o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
     f'<rect width="{W}" height="{H}" fill="{CREAM}"/>',
     '<style>text{font-family:"Sarabun","DejaVu Sans",Arial,sans-serif} .sym{font-family:"DejaVu Sans","Segoe UI Symbol",sans-serif}</style>',
     f'<defs><pattern id="stripe" patternUnits="userSpaceOnUse" width="10" height="10" patternTransform="rotate(45)"><rect width="10" height="10" fill="{BLACK}"/><rect width="5" height="10" fill="{RED}"/></pattern></defs>']

# header
o.append(f'<text x="{W/2}" y="48" font-size="26" font-weight="bold" text-anchor="middle" fill="{INK}">Human Design Bodygraph</text>')
o.append(f'<text x="{W/2}" y="74" font-size="14" text-anchor="middle" fill="{MUTED}">{SUBTITLE}</text>')

o.append(f'<g transform="translate({OX},20)">')
# base channels
for a,b in CH:
    (x1,y1),(x2,y2) = G[a],G[b]
    o.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{GREY}" stroke-width="11" stroke-linecap="round"/>')
# colored halves
for a,b in CH:
    (x1,y1),(x2,y2) = G[a],G[b]; mx,my=(x1+x2)/2,(y1+y2)/2
    for g,(sx,sy) in ((a,(x1,y1)),(b,(x2,y2))):
        c = col(g)
        if not c: continue
        stroke = 'url(#stripe)' if c=='both' else c
        o.append(f'<line x1="{sx}" y1="{sy}" x2="{mx}" y2="{my}" stroke="{stroke}" stroke-width="11" stroke-linecap="round"/>')
# centers
for name,(kind,pts) in SHAPES.items():
    fill = COL[name] if name in defined else '#FFFFFF'
    if kind=='rect':
        x,y,w,h = pts.split(',')
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{INK}" stroke-width="2.2"/>')
    else:
        o.append(f'<polygon points="{pts}" stroke-linejoin="round" fill="{fill}" stroke="{INK}" stroke-width="2.2"/>')
# gate numbers inside centers (pull slightly toward center label)
import math
for g,(x,y) in G.items():
    # find center name
    cen = next(n for n,gs in {'Head':[64,61,63],'Ajna':[47,24,4,17,43,11],'Throat':[62,23,56,35,12,45,33,8,31,20,16],'G':[1,13,25,46,2,15,10,7],'Heart':[21,40,26,51],'Sacral':[5,14,29,59,9,3,42,27,34],'Spleen':[48,57,44,50,32,28,18],'SolarPlexus':[6,37,22,36,30,55,49],'Root':[53,60,52,19,39,41,58,38,54]}.items() if g in gs)
    cx,cy = LABEL[cen]
    dx,dy = cx-x, cy-y; d = math.hypot(dx,dy) or 1
    pull = 9 if cen in ('Head','Ajna') else (7 if cen=='Heart' else 14)
    tx,ty = x+dx/d*pull, y+dy/d*pull
    c = col(g)
    fill = (RED if c==RED else BLACK) if c else ('#6B6256' if cen in defined else '#B8B2A8')
    w = 'bold' if c else 'normal'
    o.append(f'<text x="{tx}" y="{ty+4}" font-size="{10 if cen in ('Head','Ajna','Heart') else 11}" font-weight="{w}" text-anchor="middle" fill="{fill}">{g}</text>')
# center labels
for name,(x,y) in LABEL.items():
    if name in ('Head','Ajna','Heart'): continue
    lines = LTXT[name].split('\n')
    for i,ln in enumerate(lines):
        o.append(f'<text x="{x}" y="{y+i*13-(len(lines)-1)*6}" font-size="11" text-anchor="middle" fill="{INK}" opacity="0.55">{ln}</text>')
o.append('</g>')

# ---- planet columns ----
order = ['Sun','Earth','NorthNode','SouthNode','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune','Pluto']
sym = {'Sun':'☉','Earth':'⊕','NorthNode':'☊','SouthNode':'☋','Moon':'☽','Mercury':'☿','Venus':'♀','Mars':'♂','Jupiter':'♃','Saturn':'♄','Uranus':'♅','Neptune':'♆','Pluto':'♇'}
def column(x, side, color, title):
    y0 = 120
    o.append(f'<rect x="{x-8}" y="{y0-34}" width="150" height="{len(order)*34+48}" rx="12" fill="#FFFFFF" stroke="{GREY}" stroke-width="1.5"/>')
    o.append(f'<text x="{x+67}" y="{y0-10}" font-size="13" font-weight="bold" text-anchor="middle" fill="{color}">{title}</text>')
    for i,k in enumerate(order):
        a = chart['activations'][side][k]; y = y0+20+i*34
        o.append(f'<text class="sym" x="{x+10}" y="{y}" font-size="17" fill="{color}">{sym[k]}</text>')
        o.append(f'<text x="{x+118}" y="{y}" font-size="17" font-weight="bold" text-anchor="end" fill="{color}">{a["gate"]}.{a["line"]}</text>')
column(40, 'design', RED, 'Design')
column(W-190, 'personality', BLACK, 'Personality')

# ---- summary panel ----
sy = 975
o.append(f'<rect x="40" y="{sy}" width="{W-80}" height="170" rx="14" fill="#FFFFFF" stroke="{GREY}" stroke-width="1.5"/>')
STRAT = {'Manifestor':'Inform','Generator':'Respond','Manifesting Generator':'Respond','Projector':'Wait for invitation','Reflector':'Wait a lunar cycle'}
cross = chart.get('incarnation_cross') or ('Gates ' + '/'.join(str(g) for g in chart.get('incarnation_cross_gates',[])))
items = [("Type",chart.get('type','')),("Strategy",chart.get('strategy') or STRAT.get(chart.get('type',''),'')),("Authority",str(chart.get('authority','')).split(' (')[0]),("Profile",chart.get('profile','')),("Definition",str(chart.get('definition','')).replace(' Definition','')),("Cross",cross)]
for i,(k,v) in enumerate(items[:5]):
    x = 70 + i*205
    o.append(f'<text x="{x}" y="{sy+42}" font-size="12" fill="{MUTED}" letter-spacing="1">{k.upper()}</text>')
    o.append(f'<text x="{x}" y="{sy+70}" font-size="21" font-weight="bold" fill="{INK}">{v}</text>')
o.append(f'<text x="70" y="{sy+112}" font-size="12" fill="{MUTED}" letter-spacing="1">INCARNATION CROSS</text>')
o.append(f'<text x="70" y="{sy+140}" font-size="19" font-weight="bold" fill="{INK}">{items[5][1]}</text>')
o.append(f'<text x="{W-70}" y="{sy+140}" font-size="12" text-anchor="end" fill="{MUTED}">Channels: {" · ".join(f"{a}-{b}" for a,b in chart.get("channels",[]))}</text>')
# legend
o.append(f'<line x1="440" y1="{sy-14}" x2="470" y2="{sy-14}" stroke="{BLACK}" stroke-width="9" stroke-linecap="round"/><text x="478" y="{sy-10}" font-size="12" fill="{INK}">Personality</text>')
o.append(f'<line x1="570" y1="{sy-14}" x2="600" y2="{sy-14}" stroke="{RED}" stroke-width="9" stroke-linecap="round"/><text x="608" y="{sy-10}" font-size="12" fill="{INK}">Design</text>')
o.append(f'<line x1="670" y1="{sy-14}" x2="700" y2="{sy-14}" stroke="url(#stripe)" stroke-width="9" stroke-linecap="round"/><text x="708" y="{sy-10}" font-size="12" fill="{INK}">Both</text>')
o.append('</svg>')
open(sys.argv[2],'w').write('\n'.join(o)); print('ok')

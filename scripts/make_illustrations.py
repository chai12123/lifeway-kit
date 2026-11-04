import math, os, random, subprocess
import sys
OUT = sys.argv[1] if len(sys.argv) > 1 else "images"
os.makedirs(OUT, exist_ok=True)
W,H = 1500,1000
TEAL="#654422"; DTEAL="#3B2612"; GOLD="#E4B54B"; CREAM="#EEF3F4"; TERRA="#BF5A0F"; INK="#2B2B2B"

def head(bg="cream"):
    if bg=="cream":
        g = f'<radialGradient id="bg" cx="50%" cy="45%" r="75%"><stop offset="0" stop-color="#F4F8F9"/><stop offset="1" stop-color="#D0E0E3"/></radialGradient>'
    else:
        g = f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{DTEAL}"/><stop offset="1" stop-color="{TEAL}"/></linearGradient>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"><defs>{g}<radialGradient id="glow"><stop offset="0" stop-color="{GOLD}" stop-opacity="0.9"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></radialGradient><filter id="grain"><feTurbulence baseFrequency="0.8" numOctaves="2" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.05 0"/></filter></defs><rect width="{W}" height="{H}" fill="url(#bg)"/>'
def tail(): return f'<rect width="{W}" height="{H}" filter="url(#grain)"/></svg>'
def glow(x,y,r): return f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#glow)"/>'
def dot(x,y,r,c=GOLD,o=1): return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}" opacity="{o}"/>'
def line(x1,y1,x2,y2,c=GOLD,w=2,o=0.7,dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}" opacity="{o}" stroke-linecap="round"{d}/>'
def ring(x,y,r,c=GOLD,w=2,o=0.6,dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{c}" stroke-width="{w}" opacity="{o}"{d}/>'
def figure(x,y,s=1,c=GOLD,o=1):
    # simple standing silhouette
    return (f'<g transform="translate({x},{y}) scale({s})" fill="{c}" opacity="{o}">'
            f'<circle cx="0" cy="-150" r="26"/><path d="M-30,-110 Q0,-125 30,-110 L38,-10 Q0,5 -38,-10 Z"/>'
            f'<path d="M-14,-12 L-18,120 L-4,120 L2,-10 Z"/><path d="M14,-12 L18,120 L4,120 L-2,-10 Z"/></g>')
def wave(y0, amp, freq, c=GOLD, w=3, o=0.8, phase=0):
    pts = [f"{x},{y0+amp*math.sin(freq*x/W*2*math.pi+phase):.1f}" for x in range(0,W+1,10)]
    return f'<polyline points="{" ".join(pts)}" fill="none" stroke="{c}" stroke-width="{w}" opacity="{o}" stroke-linecap="round"/>'

random.seed(7)
def stars(n, c=GOLD, dark=True):
    return ''.join(dot(random.randint(0,W),random.randint(0,H),random.choice([1.5,2,2.5,3]),c,random.uniform(0.2,0.7)) for _ in range(n))

def mandala(x,y,R):
    s = [ring(x,y,R), ring(x,y,R*0.78,o=0.35,dash="6 10"), ring(x,y,R*0.55,o=0.3)]
    pts=[]
    for i in range(9):
        a = -math.pi/2 + i*2*math.pi/9
        px,py = x+R*math.cos(a), y+R*math.sin(a); pts.append((px,py))
        s.append(glow(px,py,60)); s.append(dot(px,py,9))
    for i in range(9):
        for j in (3,4):
            q = pts[(i+j)%9]; s.append(line(pts[i][0],pts[i][1],q[0],q[1],o=0.25,w=1.5))
    return ''.join(s)

IMG = {}
# cover
IMG['cover'] = head("dark") + stars(140) + mandala(W/2,H/2+20,380) + glow(W/2,H/2,260) + figure(W/2,H/2+70,1.15,CREAM) + tail()
# 1 map + constellation
IMG[1] = head() + ''.join(line(W*0.15,H*0.78,W*0.85,H*0.78,INK,2,0.15)) + f'<path d="M300,780 L420,300 L1080,300 L1200,780 Z" fill="#fff" opacity="0.8" stroke="{INK}" stroke-width="2"/>' + stars(60,TEAL) + mandala(W/2,H*0.5,200) + tail()
# 2 figure striding ahead, path behind, small group far
IMG[2] = head() + f'<path d="M0,900 Q400,820 760,700 T1500,560" fill="none" stroke="{GOLD}" stroke-width="10" opacity="0.5" stroke-linecap="round"/>' + glow(1050,520,120) + figure(1050,600,1.2,TEAL) + dot(1050,480,10) + ''.join(figure(200+i*70,870-i*8,0.55,INK,0.35) for i in range(4)) + tail()
# 3 wave + boat
IMG[3] = head() + wave(520,110,1.2,TEAL,4,0.9) + wave(560,80,1.2,TEAL,2,0.35,0.6) + wave(600,60,1.2,TEAL,2,0.2,1.2) + f'<path d="M620,470 L700,470 L670,520 L650,520 Z" fill="{TERRA}"/>' + line(685,470,685,400,INK,3,0.8) + f'<path d="M685,400 L745,455 L685,455 Z" fill="{GOLD}"/>' + glow(1200,250,140) + dot(1200,250,46,GOLD,0.9) + tail()
# 4 workbench prototypes, one glowing
IMG[4] = head() + line(150,760,1350,760,INK,6,0.5) + ''.join(ring(300+i*230,650,55+i*5,INK,3,0.35,dash="14 10") for i in range(4)) + glow(1220,640,150) + dot(1220,640,62,GOLD) + ring(1220,640,90,GOLD,3,0.6) + tail()
# 5 four solid shapes stacked
IMG[5] = head() + f'<rect x="690" y="180" width="120" height="120" fill="{TEAL}"/>' + f'<polygon points="750,360 830,440 750,520 670,440" fill="{GOLD}"/>' + f'<polygon points="870,560 960,560 915,640" fill="{TERRA}"/>' + f'<polygon points="640,560 560,640 640,720 720,640" fill="{TEAL}" opacity="0"/>' + f'<polygon points="560,620 700,580 700,700" fill="{TEAL}"/>' + line(750,300,750,360,GOLD,4) + line(790,480,890,575,GOLD,4) + line(700,470,660,600,GOLD,4) + line(915,640,780,700,GOLD,4,0.5) + glow(750,440,170) + tail()
# 6 five empty vessels catching light
def vessel(x,y,h): return f'<path d="M{x-40},{y} Q{x-55},{y-h/2} {x-30},{y-h} L{x+30},{y-h} Q{x+55},{y-h/2} {x+40},{y} Z" fill="#fff" opacity="0.75" stroke="{INK}" stroke-width="2"/>'
IMG[6] = head() + ''.join(line(0,120+i*25,1500,520+i*60,GOLD,30,0.08) for i in range(6)) + line(200,730,1300,730,INK,4,0.4) + ''.join(vessel(300+i*225,730,180+((i*37)%60)) for i in range(5)) + ''.join(glow(300+i*225,640,80) for i in (1,3)) + tail()
# 7 four threads braiding
IMG[7] = head("dark") + ''.join(wave(500,120-i*20,0.9+i*0.25,c,5,0.85,i*0.9) for i,c in enumerate([GOLD,CREAM,TERRA,"#7FC8C9"])) + tail()
# 8 sun earth moon over water
IMG[8] = head("dark") + stars(120) + f'<rect y="620" width="{W}" height="380" fill="{DTEAL}" opacity="0.6"/>' + glow(380,300,200) + dot(380,300,70,GOLD) + dot(760,380,40,"#7FC8C9") + f'<path d="M1120,250 a55,55 0 1,0 0.1,0 Z" fill="{CREAM}"/>' + dot(1140,235,50,DTEAL,0.95) + line(380,300,760,380,GOLD,1.5,0.5,dash="8 10") + line(760,380,1110,260,GOLD,1.5,0.5,dash="8 10") + ''.join(wave(700+i*45,6,3,GOLD,2,0.25-i*0.04) for i in range(5)) + tail()
# 9 vessel overflowing light in hands
IMG[9] = head() + f'<path d="M560,860 Q520,700 650,660 L850,660 Q980,700 940,860 Z" fill="{TERRA}"/>' + f'<path d="M650,660 L850,660 L830,420 Q750,380 670,420 Z" fill="{CREAM}" stroke="{INK}" stroke-width="2"/>' + glow(750,420,260) + ''.join(dot(750+random.randint(-260,260), 420-random.randint(0,320), random.choice([4,6,8]), GOLD, random.uniform(0.4,0.9)) for _ in range(28)) + tail()
# 10 empty canvas first stroke
IMG[10] = head() + f'<rect x="330" y="170" width="840" height="560" fill="#fff" stroke="{INK}" stroke-width="3"/>' + f'<path d="M420,620 Q600,250 760,470 T1080,300" fill="none" stroke="{GOLD}" stroke-width="12" stroke-linecap="round"/>' + figure(260,880,0.9,TEAL) + ''.join(figure(1290+i*70,900,0.6,INK,0.3) for i in range(2)) + tail()
# 11 handshake table coins key scroll
IMG[11] = head() + line(150,700,1350,700,INK,8,0.4) + f'<path d="M520,520 Q640,420 760,520 Q880,620 1000,520" fill="none" stroke="{TEAL}" stroke-width="24" stroke-linecap="round"/>' + ''.join(dot(380+i*40,660-(i%2)*8,22,GOLD) for i in range(3)) + f'<rect x="1040" y="610" width="200" height="60" rx="30" fill="{CREAM}" stroke="{INK}" stroke-width="2"/>' + dot(1210,640,16,TERRA) + ring(760,520,0,GOLD) + tail()
# 12 two figures with gap of light, bench
IMG[12] = head() + f'<path d="M0,860 Q750,780 1500,860" fill="none" stroke="{INK}" stroke-width="4" opacity="0.3"/>' + glow(750,650,200) + figure(600,720,1,TEAL) + figure(900,720,1,TERRA) + ''.join(ring(200+i*120,300+(i%3)*90,30+i*4,TEAL,2,0.15) for i in range(9)) + tail()
# 13 hammock, sun setting, moon
IMG[13] = head() + glow(1150,300,230) + dot(1150,300,80,GOLD,0.9) + line(0,760,1500,760,INK,3,0.25) + line(250,320,250,780,INK,14,0.6) + line(1050,320,1050,780,INK,14,0.6) + f'<path d="M250,420 Q650,760 1050,420" fill="none" stroke="{TEAL}" stroke-width="14" stroke-linecap="round"/>' + f'<path d="M250,420 Q650,790 1050,420" fill="none" stroke="{TEAL}" stroke-width="3" opacity="0.5"/>' + f'<ellipse cx="650" cy="560" rx="130" ry="28" fill="{TERRA}"/>' + dot(330,170,22,CREAM) + dot(342,163,22,"#F6F1E7") + tail()
# 14 spiral of 30 stones
def spiral():
    s=[];
    for i in range(30):
        a = i*0.52; r = 70+i*17
        x,y = 750+r*math.cos(a), 520+r*0.62*math.sin(a)
        gold = i in (0,7,14,21,28)
        s.append(glow(x,y,50) if gold else '')
        s.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="22" ry="15" fill="{GOLD if gold else INK}" opacity="{1 if gold else 0.35}"/>')
    return ''.join(s)
IMG[14] = head() + spiral() + tail()

for k,svg in IMG.items():
    name = f"chapter_{k:02d}" if isinstance(k,int) else k
    p = f"{OUT}/{name}.svg"; open(p,'w').write(svg)
    subprocess.run(["rsvg-convert","-w","1500",p,"-o",f"{OUT}/{name}.png"],check=True)
print("ok", len(IMG))

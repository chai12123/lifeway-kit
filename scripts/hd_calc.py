import swisseph as swe, json, sys
from datetime import datetime, timedelta, timezone

# ---------- Rave Mandala ----------
GATE_ORDER = [41,19,13,49,30,55,37,63,22,36,25,17,21,51,42,3,27,24,2,23,8,20,16,35,45,12,15,52,39,53,62,56,31,33,7,4,29,59,40,64,47,6,46,18,48,57,32,50,28,44,1,43,14,34,9,5,26,11,10,58,38,54,61,60]
START = 302.0  # Gate 41 begins at 2° Aquarius
GATE_DEG = 360/64
LINE_DEG = GATE_DEG/6

def gate_line(lon):
    x = (lon - START) % 360
    gi = int(x // GATE_DEG)
    rem = x - gi*GATE_DEG
    line = int(rem // LINE_DEG) + 1
    return GATE_ORDER[gi], line

CENTERS = {
 'Head':[64,61,63], 'Ajna':[47,24,4,17,43,11],
 'Throat':[62,23,56,35,12,45,33,8,31,20,16],
 'G':[1,13,25,46,2,15,10,7], 'Heart':[21,40,26,51],
 'Sacral':[5,14,29,59,9,3,42,27,34],
 'Spleen':[48,57,44,50,32,28,18],
 'SolarPlexus':[6,37,22,36,30,55,49,],
 'Root':[53,60,52,19,39,41,58,38,54]}
GATE2CENTER = {g:c for c,gs in CENTERS.items() for g in gs}
CHANNELS = [(1,8),(2,14),(3,60),(4,63),(5,15),(6,59),(7,31),(9,52),(10,20),(10,34),(10,57),(11,56),(12,22),(13,33),(16,48),(17,62),(18,58),(19,49),(20,34),(20,57),(21,45),(23,43),(24,61),(25,51),(26,44),(27,50),(28,38),(29,46),(30,41),(32,54),(35,36),(37,40),(39,55),(42,53),(47,64),(34,57)]

PLANETS = [('Sun',swe.SUN),('Moon',swe.MOON),('Mercury',swe.MERCURY),('Venus',swe.VENUS),('Mars',swe.MARS),('Jupiter',swe.JUPITER),('Saturn',swe.SATURN),('Uranus',swe.URANUS),('Neptune',swe.NEPTUNE),('Pluto',swe.PLUTO),('NorthNode',swe.TRUE_NODE)]

def lon(jd, p):
    return swe.calc_ut(jd, p)[0][0] % 360

def positions(jd):
    out = {}
    for name,p in PLANETS:
        out[name] = lon(jd,p)
    out['Earth'] = (out['Sun']+180)%360
    out['SouthNode'] = (out['NorthNode']+180)%360
    return out

def design_jd(birth_jd):
    target = (lon(birth_jd, swe.SUN) - 88) % 360
    jd = birth_jd - 88  # start guess
    for _ in range(30):
        cur = lon(jd, swe.SUN)
        diff = (target - cur + 180) % 360 - 180
        jd += diff / 0.9856
        if abs(diff) < 1e-6: break
    return jd

def chart(y,m,d,hh,mm,tz_hours):
    local = datetime(y,m,d,hh,mm)
    utc = local - timedelta(hours=tz_hours)
    bjd = swe.julday(utc.year,utc.month,utc.day, utc.hour+utc.minute/60+utc.second/3600)
    djd = design_jd(bjd)
    dy,dmo,dd,dh = swe.revjul(djd)
    pers = positions(bjd); des = positions(djd)
    order = ['Sun','Earth','NorthNode','SouthNode','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune','Pluto']
    act = {'personality':{}, 'design':{}}
    for k in order:
        g,l = gate_line(pers[k]); act['personality'][k] = {'gate':g,'line':l,'lon':round(pers[k],3)}
        g,l = gate_line(des[k]); act['design'][k] = {'gate':g,'line':l,'lon':round(des[k],3)}
    gates_p = {v['gate'] for v in act['personality'].values()}
    gates_d = {v['gate'] for v in act['design'].values()}
    gates = gates_p | gates_d
    channels = [c for c in CHANNELS if c[0] in gates and c[1] in gates]
    defined = set()
    edges = []
    for a,b in channels:
        ca,cb = GATE2CENTER[a],GATE2CENTER[b]
        defined |= {ca,cb}; edges.append((ca,cb))
    # components
    comps=[]; seen=set()
    for c in defined:
        if c in seen: continue
        stack=[c]; comp=set()
        while stack:
            x=stack.pop()
            if x in comp: continue
            comp.add(x)
            for a,b in edges:
                if a==x and b not in comp: stack.append(b)
                if b==x and a not in comp: stack.append(a)
        seen|=comp; comps.append(sorted(comp))
    def connected(a,b):
        return any(a in c and b in c for c in comps)
    motors=['Sacral','Heart','SolarPlexus','Root']
    motor_throat = any(connected(mo,'Throat') for mo in motors if mo in defined)
    if not defined: typ='Reflector'
    elif 'Sacral' in defined: typ='Manifesting Generator' if motor_throat else 'Generator'
    elif motor_throat: typ='Manifestor'
    else: typ='Projector'
    if 'SolarPlexus' in defined: auth='Emotional (Solar Plexus)'
    elif 'Sacral' in defined: auth='Sacral'
    elif 'Spleen' in defined: auth='Splenic'
    elif 'Heart' in defined: auth='Ego Manifested' if connected('Heart','Throat') else 'Ego Projected'
    elif 'G' in defined: auth='Self-Projected'
    elif defined: auth='Mental / Environmental'
    else: auth='Lunar'
    definition = {0:'None',1:'Single',2:'Split',3:'Triple Split',4:'Quadruple Split'}[len(comps)]
    profile = f"{act['personality']['Sun']['line']}/{act['design']['Sun']['line']}"
    cross = [act['personality']['Sun']['gate'],act['personality']['Earth']['gate'],act['design']['Sun']['gate'],act['design']['Earth']['gate']]
    in_channels = {g for ch in channels for g in ch}
    STRAT = {'Manifestor':'To Inform','Generator':'To Respond','Manifesting Generator':'To Respond','Projector':'Wait for the Invitation','Reflector':'Wait a Lunar Cycle'}
    return {
      'source': 'hd_calc.py (Swiss Ephemeris, True Node)', 'strategy': STRAT[typ],
      'hanging_gates': sorted(g for g in gates if g not in in_channels),
      'gates_by_center': {c: sorted(g for g in gates if GATE2CENTER.get(g) == c) for c in CENTERS},
      'gate_to_center': {str(g): GATE2CENTER.get(g) for g in gates},
      'birth_local': local.isoformat(), 'birth_utc': utc.isoformat(),
      'design_utc': f"{int(dy)}-{int(dmo):02d}-{int(dd):02d} {dh:.2f}h",
      'type':typ,'authority':auth,'profile':profile,'definition':definition,
      'incarnation_cross_gates':cross,
      'defined_centers':sorted(defined),'open_centers':sorted(set(CENTERS)-defined),
      'channels':[list(c) for c in channels],'components':comps,
      'gates_personality':sorted(gates_p),'gates_design':sorted(gates_d),'all_gates':sorted(gates),
      'activations':act}

if __name__=='__main__':
    y,m,d,hh,mm,tz = [float(x) for x in sys.argv[1:7]]
    print(json.dumps(chart(int(y),int(m),int(d),int(hh),int(mm),tz), indent=1))

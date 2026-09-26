import json,sys,math
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import make_valid,affinity
d=json.load(open(sys.argv[1]))
def geom(o):return unary_union([make_valid(Polygon(f)) for f in o['faces'] if len(f)>=3])
median=unary_union([geom(o) for o in d['medians']])
deck=unary_union([geom(o) for o in d['decks']])
road=unary_union([geom(o) for o in d['roads']])
piers={int(o['name'].rsplit('_',1)[1]):geom(o) for o in d['piers']}
groups={}
for n,g in piers.items():groups.setdefault(n//2*2,[]).append(n)
delta=sorted([(x*.5,y*.5) for x in range(-24,25) for y in range(-24,25) if x*x+y*y<=24*24],key=lambda v:v[0]*v[0]+v[1]*v[1])
out=[]
for key,ids in groups.items():
    g=unary_union([piers[i] for i in ids]);conflict=g.intersection(road).difference(median).area
    row={'group':key,'piers':['UNVERIFIED_Pier_%03d'%i for i in ids],'original_road_overlap_m2':conflict,'streetview_verified':False}
    if key==518:row['status']='HOLD_UTURN_STREETVIEW_MAPPING';out.append(row);continue
    if conflict<.01:row['status']='NO_MOVE_REQUESTED';out.append(row);continue
    safe=g.buffer(.1)
    candidate=None
    for dx,dy in delta:
        moved=affinity.translate(safe,dx,dy)
        if median.covers(moved) and deck.covers(moved):candidate=(dx,dy);break
    if candidate is None:row['status']='NO_FEASIBLE_MEDIAN_POSITION_WITHIN_12M'
    else:
        dx,dy=candidate;new=affinity.translate(g,dx,dy)
        row.update(status='CONSTRAINED_ESTIMATE_NOT_ADOPTED',delta_xy=[dx,dy],distance_m=math.hypot(dx,dy),new_road_outside_median_m2=new.intersection(road).difference(median).area)
    out.append(row)
report={'basis':'Rigid pair translation in 0.5m increments up to 12m, full base footprint plus 0.1m margin inside existing estimated median and bridge deck. No Street View coordinates inferred by this calculation.','groups':out,'counts':{k:sum(r['status']==k for r in out) for k in sorted({r['status'] for r in out})}}
json.dump(report,open(sys.argv[2],'w'),indent=2);print(json.dumps(report['counts']))

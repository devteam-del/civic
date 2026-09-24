"""Proportional working curb/ramp mask, not surveyed and not independent clearance proof."""
import json,sys
from shapely.geometry import Polygon,LineString,box,shape,mapping
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from shapely import constrained_delaunay_triangles,affinity
src=json.load(open(sys.argv[1]));prior=json.load(open(sys.argv[2]));obs=json.load(open(sys.argv[3]))
def geo(o):return unary_union([Polygon(f).buffer(0) for f in o['faces'] if len(f)>=3])
old=unary_union([shape(next(p['footprint'] for p in prior['patches'] if p['new_name']=='SV_EAST_CORRIDOR_MEDIAN_EST')),geo(next(o for o in src['medians'] if o['name']=='CAL_GROUND_MEDIAN_WORKING_ESTIMATED_16'))])
holes=[Polygon(r) for p in (old.geoms if old.geom_type=='MultiPolygon' else [old]) for r in p.interiors]
south=sorted(r['candidate_model_xy'] for r in obs['targets'] if r['id'].endswith('SOUTH'));north=sorted(r['candidate_model_xy'] for r in obs['targets'] if r['id'].endswith('NORTH'))
ws,wn=old.intersection(LineString([(4210,300),(4210,450)])).bounds[1::2]
profile=Polygon([(4210,ws)]+[(x,y-2) for x,y in south]+[(4446,south[-1][1]-2),(4446,north[-1][1]+2)]+[(x,y+2) for x,y in reversed(north)]+[(4210,wn)])
# Opening existence is visible; exact curb offsets and endpoint stations remain estimates.
yanji_crossing=Polygon([(4375,330),(4400,330),(4397,380),(4372,380)])
# Do not fill the observed Yanji parking ramp between the two planted strips.
ramp_s=[(x,y+2.3) for x,y in south if 4210<x<4301]
ramp_n=[(x,y-2.3) for x,y in north if 4210<x<4302]
ramp=Polygon([(4210,357.5)]+ramp_s+[(4301,346.7),(4301,353.4)]+list(reversed(ramp_n))+[(4210,363.3)])
assert ramp.is_valid
new=unary_union([old.difference(box(4210,300,4446,450)),profile]).difference(unary_union([*holes,yanji_crossing,ramp]))
assert new.is_valid

def mesh(g,z0,z1):
 verts=[];faces=[];ids={}
 def vid(x,y,z):
  k=tuple(round(v,6) for v in (x,y,z))
  if k not in ids:ids[k]=len(verts);verts.append(k)
  return ids[k]
 for p in g.geoms if g.geom_type=='MultiPolygon' else [g]:
  p=orient(p,1)
  for t in constrained_delaunay_triangles(p).geoms:
   co=list(orient(t,1).exterior.coords)[:-1];faces.append([vid(x,y,z1) for x,y in co]);faces.append([vid(x,y,z0) for x,y in reversed(co)])
  for ring in [p.exterior,*p.interiors]:
   co=list(ring.coords)
   for a,b in zip(co,co[1:]):faces.append([vid(*a,z0),vid(*b,z0),vid(*b,z1),vid(*a,z1)])
 return verts,faces
patches=[p for p in prior['patches'] if p['new_name']!='SV_EAST_CORRIDOR_MEDIAN_EST']
v,f=mesh(new,0,.18);patches.append(dict(source_object='SV_EAST_CORRIDOR_MEDIAN_EST',new_name='SV_YANJI_MEDIAN_OPENINGS_EST',footprint=mapping(new),vertices=v,faces=f))
road_patch=next(p for p in patches if p['new_name']=='SV_DUNHUA_ROAD_EST')
road_new=shape(road_patch['footprint']).difference(ramp)
patches.remove(road_patch)
v,f=mesh(road_new,-.25,0);patches.append(dict(source_object='SV_DUNHUA_ROAD_EST',new_name='SV_YANJI_ROAD_OPENINGS_EST',footprint=mapping(road_new),vertices=v,faces=f))
checks=[]
for r in obs['targets']:
 p=geo(next(o for o in src['piers'] if o['name']==r['model_pier_candidate']));c=p.centroid;x,y=r['candidate_model_xy'];p=affinity.translate(p,x-c.x,y-c.y)
 checks.append(dict(pier=r['model_pier_candidate'],outside_median_m2=p.difference(new).area,ramp_overlap_m2=p.intersection(ramp).area,crossing_overlap_m2=p.intersection(yanji_crossing).area))
out=dict(patches=patches,omit_from_working_scene=[*prior['omit_from_working_scene'],'CAL_GROUND_MEDIAN_WORKING_ESTIMATED_16'],checks=checks,scope_x=[4210,4446],opening_estimates={'yanji_crossing':mapping(yanji_crossing),'parking_ramp':mapping(ramp)},assumptions='Street View establishes parking ramp, planted strips and Yanji through crossing. Curbs offset2m from estimated shafts, ramp inner walls offset2.3m, opening endpoints and crossing widths are proportional assumptions awaiting independent curb picks. Existing holes retained. This is not surveyed and model clearance is not field verification.',field_verified=False)
json.dump(out,open(sys.argv[4],'w'),indent=2);print(json.dumps(checks))

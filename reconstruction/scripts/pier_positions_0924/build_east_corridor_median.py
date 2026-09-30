import json,sys
from shapely.geometry import Polygon,LineString,box,mapping,shape
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from shapely import constrained_delaunay_triangles,affinity
source=json.load(open(sys.argv[1]));prior=json.load(open(sys.argv[2]));obs=json.load(open(sys.argv[3]))
def geo(o):return unary_union([Polygon(f).buffer(0) for f in o['faces'] if len(f)>=3])
old13=shape(next(x['footprint'] for x in prior['patches'] if x['new_name']=='SV_DUNHUA_EAST_MEDIAN_RAMP_EST'))
old15=geo(next(o for o in source['medians'] if o['name']=='CAL_GROUND_MEDIAN_WORKING_ESTIMATED_15'))
old=unary_union([old13,old15]);holes=[]
for p in old.geoms if old.geom_type=='MultiPolygon' else [old]:holes.extend(Polygon(r) for r in p.interiors)
def section(x):
 b=old.intersection(LineString([(x,300),(x,450)])).bounds;return b[1],b[3]
ws,wn=section(4005);es,en=section(4210)
south=sorted([r['candidate_model_xy'] for r in obs['targets'] if r['id'].endswith('SOUTH')]);north=sorted([r['candidate_model_xy'] for r in obs['targets'] if r['id'].endswith('NORTH')])
profile=Polygon([(4005,ws)]+[(x,y-2) for x,y in south]+[(4210,es),(4210,en)]+[(x,y+2) for x,y in reversed(north)]+[(4005,wn)])
zone=box(4005,300,4210,450);new=unary_union([old.difference(zone),profile]).difference(unary_union(holes))
assert new.is_valid
verts=[];faces=[];ids={}
def vid(x,y,z):
 k=tuple(round(v,6) for v in (x,y,z))
 if k not in ids:ids[k]=len(verts);verts.append(k)
 return ids[k]
for p in new.geoms if new.geom_type=='MultiPolygon' else [new]:
 p=orient(p,1)
 for t in constrained_delaunay_triangles(p).geoms:
  co=list(orient(t,1).exterior.coords)[:-1]
  faces.append([vid(x,y,.18) for x,y in co]);faces.append([vid(x,y,0) for x,y in reversed(co)])
 for ring in [p.exterior,*p.interiors]:
  co=list(ring.coords)
  for a,b in zip(co,co[1:]):faces.append([vid(*a,0),vid(*b,0),vid(*b,.18),vid(*a,.18)])
checks=[]
for r in obs['targets']:
 p=geo(next(o for o in source['piers'] if o['name']==r['model_pier_candidate']));c=p.centroid;x,y=r['candidate_model_xy'];p=affinity.translate(p,x-c.x,y-c.y)
 checks.append(dict(pier=r['model_pier_candidate'],contained=new.covers(p),outside_area=p.difference(new).area,preserved_opening_overlap_m2=p.intersection(unary_union(holes)).area))
patches=[p for p in prior['patches'] if p['new_name']!='SV_DUNHUA_EAST_MEDIAN_RAMP_EST']
patches.append(dict(source_object='SV_DUNHUA_EAST_MEDIAN_RAMP_EST',new_name='SV_EAST_CORRIDOR_MEDIAN_EST',footprint=mapping(new),vertices=verts,faces=faces))
out=dict(patches=patches,omit_from_working_scene=['CAL_GROUND_MEDIAN_WORKING_ESTIMATED_14','CAL_GROUND_MEDIAN_WORKING_ESTIMATED_15'],replaced_original_medians=['CAL_GROUND_MEDIAN_WORKING_ESTIMATED_12','CAL_GROUND_MEDIAN_WORKING_ESTIMATED_13','CAL_GROUND_MEDIAN_WORKING_ESTIMATED_14','CAL_GROUND_MEDIAN_WORKING_ESTIMATED_15'],checks=checks,preserved_opening_bounds=[list(h.bounds) for h in holes],scope_x=[4005,4210],assumptions='Curb profiles estimated2m from Street View shaft centers. Existing verified/unverified openings retained; old gap4085-4102 replaced by continuous pedestrian median visible in opposite Street View perspectives. Not surveyed dimensions. Unmodeled ramp-opening correspondence remains a separate issue.',field_verified=False)
json.dump(out,open(sys.argv[4],'w'),indent=2);print(json.dumps(checks))

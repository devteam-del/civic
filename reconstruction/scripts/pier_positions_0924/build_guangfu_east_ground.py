import json,sys
from shapely.geometry import Polygon,LineString,box,shape,mapping,Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from shapely import constrained_delaunay_triangles,affinity
src=json.load(open(sys.argv[1]));prior=json.load(open(sys.argv[2]));obs=json.load(open(sys.argv[3]))
def geo(o):return unary_union([Polygon(f).buffer(0) for f in o['faces'] if len(f)>=3])
old=geo(next(o for o in src['medians'] if o['name']=='CAL_GROUND_MEDIAN_WORKING_ESTIMATED_18'))
holes=[Polygon(r) for p in (old.geoms if old.geom_type=='MultiPolygon' else [old]) for r in p.interiors]
south=sorted(r['candidate_model_xy'] for r in obs['targets'] if r['id'].endswith('SOUTH'));north=sorted(r['candidate_model_xy'] for r in obs['targets'] if r['id'].endswith('NORTH'))
es,en=old.intersection(LineString([(4845,350),(4845,550)])).bounds[1::2]
profile=Polygon([(4802,south[0][1]-2),(south[0][0],south[0][1]-2),(4845,es),(4845,en),(north[0][0],north[0][1]+2),(4802,north[0][1]+2)])
new=unary_union([old.difference(box(4790,350,4845,550)),profile]).difference(unary_union(holes))
vehicle_opening=box(4768,300,4802,550)
new=new.difference(vehicle_opening)
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

patches=list(prior['patches']);v,f=mesh(new,0,.18)
patches.append(dict(source_object='CAL_GROUND_MEDIAN_WORKING_ESTIMATED_18',new_name='SV_GUANGFU_EAST_MEDIAN_EST',footprint=mapping(new),vertices=v,faces=f))
checks=[]
for r in obs['targets']:
 x,y=r['candidate_model_xy']
 if r.get('model_pier_candidate'):
  p=geo(next(o for o in src['piers'] if o['name']==r['model_pier_candidate']));c=p.centroid;p=affinity.translate(p,x-c.x,y-c.y)
 else:p=Point(x,y).buffer(1)
 checks.append(dict(pier=r.get('model_pier_candidate') or r['id'],outside_median_m2=p.difference(new).area,vehicle_opening_overlap_m2=p.intersection(vehicle_opening).area,preserved_opening_overlap_m2=p.intersection(unary_union(holes)).area))
out=dict(prior);out['guangfu_crossing_estimate']={'footprint':mapping(vehicle_opening),'evidence_pano':'NnKjizwkfo4CsLvitAR74g','note':'Guangfu junction gap retained between modeled median ends; end positions proportional estimates, not surveyed.'};out.update(patches=patches,omit_from_working_scene=[*prior['omit_from_working_scene'],'CAL_GROUND_MEDIAN_WORKING_ESTIMATED_18'],guangfu_east_checks=checks,guangfu_east_scope_x=[4802,4845],assumptions=prior['assumptions']+' Additional ramp-east curb envelope uses2m shaft offsets based on visible planted strip proportions. Preserve prior local crossing and existing holes. Not independent field clearance proof.')
json.dump(out,open(sys.argv[4],'w'),indent=2);print(json.dumps(checks))

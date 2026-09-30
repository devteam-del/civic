import json,sys
from shapely.geometry import Polygon,LineString,box,shape,mapping
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from shapely import constrained_delaunay_triangles,affinity
src=json.load(open(sys.argv[1]));prior=json.load(open(sys.argv[2]));obs=json.load(open(sys.argv[3]))
def geo(o):return unary_union([Polygon(f).buffer(0) for f in o['faces'] if len(f)>=3])
old=geo(next(o for o in src['medians'] if o['name']=='CAL_GROUND_MEDIAN_WORKING_ESTIMATED_17'))
holes=[Polygon(r) for p in (old.geoms if old.geom_type=='MultiPolygon' else [old]) for r in p.interiors]
south=sorted(r['candidate_model_xy'] for r in obs['targets'] if r['id'].endswith('SOUTH'));north=sorted(r['candidate_model_xy'] for r in obs['targets'] if r['id'].endswith('NORTH'))
ws,wn=old.intersection(LineString([(4457,300),(4457,450)])).bounds[1::2]
es,en=old.intersection(LineString([(4560,300),(4560,450)])).bounds[1::2]
profile=Polygon([(4457,ws)]+[(x,y-2) for x,y in south]+[(4560,es),(4560,en)]+[(x,y+2) for x,y in reversed(north)]+[(4457,wn)])
new=unary_union([old.difference(box(4457,300,4560,450)),profile]).difference(unary_union(holes))
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
patches.append(dict(source_object='CAL_GROUND_MEDIAN_WORKING_ESTIMATED_17',new_name='SV_RAMP_EAST_MEDIAN_EST',footprint=mapping(new),vertices=v,faces=f))
checks=[]
for r in obs['targets']:
 p=geo(next(o for o in src['piers'] if o['name']==r['model_pier_candidate']));c=p.centroid;x,y=r['candidate_model_xy'];p=affinity.translate(p,x-c.x,y-c.y)
 checks.append(dict(pier=r['model_pier_candidate'],outside_median_m2=p.difference(new).area,preserved_opening_overlap_m2=p.intersection(unary_union(holes)).area))
out=dict(prior);out.update(patches=patches,omit_from_working_scene=[*prior['omit_from_working_scene'],'CAL_GROUND_MEDIAN_WORKING_ESTIMATED_17'],ramp_east_checks=checks,ramp_east_scope_x=[4457,4560],assumptions=prior['assumptions']+' Additional ramp-east curb envelope uses2m shaft offsets based on visible planted strip proportions. Preserve prior local crossing and existing holes. Not independent field clearance proof.')
json.dump(out,open(sys.argv[4],'w'),indent=2);print(json.dumps(checks))

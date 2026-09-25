import json,sys
from shapely.geometry import Polygon,LineString,box,shape,mapping,Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from shapely import constrained_delaunay_triangles,affinity
src=json.load(open(sys.argv[1]));prior=json.load(open(sys.argv[2]));obs=json.load(open(sys.argv[3]))
def geo(o):return unary_union([Polygon(f).buffer(0) for f in o['faces'] if len(f)>=3])
old=shape(next(p for p in prior['patches'] if p['new_name']=='SV_FUDUN_WEST_MEDIAN_EST')['footprint'])
holes=unary_union([Polygon(r) for p in (old.geoms if old.geom_type=='MultiPolygon' else [old]) for r in p.interiors])
south=sorted(r['candidate_model_xy'] for r in obs['targets'] if r['id'].endswith('SOUTH'));north=sorted(r['candidate_model_xy'] for r in obs['targets'] if r['id'].endswith('NORTH'))
ws,wn=old.intersection(LineString([(3490,350),(3490,480)])).bounds[1::2]
es,en=old.intersection(LineString([(3548,350),(3548,480)])).bounds[1::2]
profile=Polygon([(3490,ws)]+[(x,y-2) for x,y in south]+[(3548,es),(3548,en)]+[(x,y+2) for x,y in reversed(north)]+[(3490,wn)])
opening=box(3508,350,3523,480)
new=unary_union([old.difference(box(3490,350,3548,480)),profile]).difference(holes).difference(opening)
assert new.is_valid
roadpatch=next(p for p in prior['patches'] if p['new_name']=='SV_FUDUN_WEST_ROAD_EST')
road=unary_union([shape(roadpatch['footprint']),opening.intersection(old.union(profile))]).difference(holes)
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

patches=[p for p in prior['patches'] if p['new_name'] not in ['SV_FUDUN_WEST_MEDIAN_EST','SV_FUDUN_WEST_ROAD_EST']]
for source,name,g,z0,z1 in [('SV_FUDUN_WEST_MEDIAN_EST','SV_P240_P241_MEDIAN_EST',new,0,.18),('SV_FUDUN_WEST_ROAD_EST','SV_P240_P241_ROAD_EST',road,-.25,0)]:
 v,f=mesh(g,z0,z1);patches.append(dict(source_object=source,new_name=name,footprint=mapping(g),vertices=v,faces=f))
checks=[]
for r in obs['targets']:
 x,y=r['candidate_model_xy']
 if r.get('model_pier_candidate'):
  p=geo(next(o for o in src['piers'] if o['name']==r['model_pier_candidate']));c=p.centroid;p=affinity.translate(p,x-c.x,y-c.y)
 else:p=Point(x,y).buffer(1)
 checks.append(dict(pier=r.get('model_pier_candidate') or r['id'],outside_median_m2=p.difference(new).area,opening_overlap_m2=p.intersection(opening).area,ramp_opening_overlap_m2=p.intersection(holes).area))
out=dict(prior);out.update(patches=patches,omit_from_working_scene=prior['omit_from_working_scene'],p240_p241_checks=checks,p240_p241_openings={'footprint':mapping(opening),'status':'Proportional U-turn gap between observed P240 and P241. Endpoints3508-3523 are estimates, not surveyed.','panos':['Muuuf5-YifGP09BhFsX-tQ','jkqZVAL68EL_J3q7M0ZItQ','KafJiQnwhzpKAS2IHVcMwQ'],'satellite_context':'No independent satellite curb measurement; bridge deck occludes curbs.'},assumptions=prior['assumptions']+' P240/P241 local profile uses2m shaft offsets; existing ramp holes retained; U-turn boundaries remain proportional estimates.')
json.dump(out,open(sys.argv[4],'w'),indent=2);print(json.dumps(checks))

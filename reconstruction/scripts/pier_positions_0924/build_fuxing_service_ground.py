import json,sys
from shapely.geometry import Polygon,LineString,box,shape,mapping,Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from shapely import constrained_delaunay_triangles,affinity
src=json.load(open(sys.argv[1]));prior=json.load(open(sys.argv[2]));obs=json.load(open(sys.argv[3]))
def geo(o):return unary_union([Polygon(f).buffer(0) for f in o['faces'] if len(f)>=3])
old=shape(next(p for p in prior['patches'] if p['new_name']=='SV_FUXING_WEST_MEDIAN_V2_EST')['footprint'])
holes=unary_union([Polygon(r) for p in (old.geoms if old.geom_type=='MultiPolygon' else [old]) for r in p.interiors])
south=sorted(r['candidate_model_xy'] for r in obs['targets'] if r['id'].endswith('SOUTH'));north=sorted(r['candidate_model_xy'] for r in obs['targets'] if r['id'].endswith('NORTH'))
ws,wn=old.intersection(LineString([(3315,350),(3315,480)])).bounds[1::2]
es,en=old.intersection(LineString([(3340,350),(3340,480)])).bounds[1::2]
profile=Polygon([(3315,ws)]+[(x,y-2) for x,y in south]+[(3340,es),(3340,en)]+[(x,y+2) for x,y in reversed(north)]+[(3315,wn)])
opening=Polygon()
new=unary_union([old.difference(box(3315,350,3340,480)),profile]).difference(holes).difference(opening)
assert new.is_valid
roadpatch=next(p for p in prior['patches'] if p['new_name']=='SV_FUXING_ROAD_EST')
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

patches=[p for p in prior['patches'] if p['new_name'] not in ['SV_FUXING_WEST_MEDIAN_V2_EST','SV_FUXING_ROAD_EST']]
for source,name,g,z0,z1 in [('SV_FUXING_WEST_MEDIAN_V2_EST','SV_FUXING_SERVICE_MEDIAN_EST',new,0,.18),('SV_FUXING_ROAD_EST','SV_FUXING_ROAD_EST',road,-.25,0)]:
 v,f=mesh(g,z0,z1);patches.append(dict(source_object=source,new_name=name,footprint=mapping(g),vertices=v,faces=f))
checks=[]
for r in obs['targets']:
 x,y=r['candidate_model_xy']
 if r.get('model_pier_candidate'):
  p=geo(next(o for o in src['piers'] if o['name']==r['model_pier_candidate']));c=p.centroid;p=affinity.translate(p,x-c.x,y-c.y)
 else:p=Point(x,y).buffer(1)
 checks.append(dict(pier=r.get('model_pier_candidate') or r['id'],outside_median_m2=p.difference(new).area,opening_overlap_m2=p.intersection(opening).area,ramp_opening_overlap_m2=p.intersection(holes).area))
out=dict(prior);out.update(patches=patches,omit_from_working_scene=prior['omit_from_working_scene'],fuxing_service_checks=checks,fuxing_service_profile={'footprint':mapping(opening),'status':'Local continuous island profile around revised P235-like pair; no opening introduced. Two-meter lateral offsets remain estimates.','panos':['cNnd3Y1IgM5BKnZCTSHUPQ','BwdbNYEooNtfbZuww25r8g','4NKKDkj7LTh70nLelXcPqw'],'satellite_context':'No independent satellite curb measurement; bridge deck occludes curbs.'},assumptions=prior['assumptions']+' Revised P235-like pair island uses2m proportional shaft offsets over3315-3340. Existing holes retained, not independently measured.')
json.dump(out,open(sys.argv[4],'w'),indent=2);print(json.dumps(checks))

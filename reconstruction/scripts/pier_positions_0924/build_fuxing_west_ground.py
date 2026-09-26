import json,sys
from shapely.geometry import Polygon,LineString,box,shape,mapping,Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from shapely import constrained_delaunay_triangles,affinity
src=json.load(open(sys.argv[1]));prior=json.load(open(sys.argv[2]));obs=json.load(open(sys.argv[3]))
def geo(o):return unary_union([Polygon(f).buffer(0) for f in o['faces'] if len(f)>=3])
old=unary_union([geo(o) for o in src['medians'] if o['name'] in ['CAL_GROUND_MEDIAN_WORKING_ESTIMATED_9','CAL_GROUND_MEDIAN_WORKING_ESTIMATED_10']])
holes=unary_union([Polygon(r) for p in (old.geoms if old.geom_type=='MultiPolygon' else [old]) for r in p.interiors])
south=sorted(r['candidate_model_xy'] for r in obs['targets'] if r['id'].endswith('SOUTH'));north=sorted(r['candidate_model_xy'] for r in obs['targets'] if r['id'].endswith('NORTH'))
ws,wn=old.intersection(LineString([(3330,350),(3330,480)])).bounds[1::2]
es=south[-1][1]-2;en=north[-1][1]+2
profile=Polygon([(3330,ws)]+[(x,y-2) for x,y in south]+[(3362,es),(3362,en)]+[(x,y+2) for x,y in reversed(north)]+[(3330,wn)])
opening=Polygon()
new=unary_union([old.difference(box(3330,350,3362,480)),profile]).difference(holes).difference(opening)
new=new.intersection(box(-100000,-100000,3362,100000))
assert new.is_valid
roadpatch=next(p for p in prior['patches'] if p['new_name']=='SV_P237_P239_ROAD_EST')
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

patches=[p for p in prior['patches'] if p['new_name']!='SV_P237_P239_ROAD_EST']
for source,name,g,z0,z1 in [('SV_FUXING_WEST_MEDIAN_EST','SV_FUXING_WEST_MEDIAN_V2_EST',new,0,.18),('SV_P237_P239_ROAD_EST','SV_FUXING_ROAD_EST',road,-.25,0)]:
 v,f=mesh(g,z0,z1);patches.append(dict(source_object=source,new_name=name,footprint=mapping(g),vertices=v,faces=f))
checks=[]
for r in obs['targets']:
 x,y=r['candidate_model_xy']
 if r.get('model_pier_candidate'):
  p=geo(next(o for o in src['piers'] if o['name']==r['model_pier_candidate']));c=p.centroid;p=affinity.translate(p,x-c.x,y-c.y)
 else:p=Point(x,y).buffer(1)
 checks.append(dict(pier=r.get('model_pier_candidate') or r['id'],outside_median_m2=p.difference(new).area,opening_overlap_m2=p.intersection(opening).area,ramp_opening_overlap_m2=p.intersection(holes).area))
out=dict(prior);out.update(patches=patches,omit_from_working_scene=[*prior['omit_from_working_scene'],'CAL_GROUND_MEDIAN_WORKING_ESTIMATED_9','CAL_GROUND_MEDIAN_WORKING_ESTIMATED_10'],fuxing_west_checks=checks,fuxing_west_island={'footprint':mapping(opening),'status':'P236 east island nose3362 inferred proportionally from visible curb; crossing to P237 island nose3404 stays open. Not surveyed.','panos':['4NKKDkj7LTh70nLelXcPqw','W7yVqpmB3_GRMjErCguLjQ','tpp-jEtiCHg_5I-NJkrQZg'],'satellite_context':'No independent satellite curb measurement; bridge deck occludes curbs.'},assumptions=prior['assumptions']+' P236 island uses2m shaft offsets and east nose3362 from proportional Street View interpretation; not measured. Existing holes retained. Original tiny median10 merged into comparison island only.')
json.dump(out,open(sys.argv[4],'w'),indent=2);print(json.dumps(checks))

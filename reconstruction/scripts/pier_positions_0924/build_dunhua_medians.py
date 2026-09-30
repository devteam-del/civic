import json,sys
from shapely.geometry import Polygon,LineString,box,mapping,shape
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from shapely import constrained_delaunay_triangles,affinity
source=json.load(open(sys.argv[1]));prior=json.load(open(sys.argv[2]));obs=json.load(open(sys.argv[3]))
def geo(o):return unary_union([Polygon(f).buffer(0) for f in o['faces'] if len(f)>=3])
west=shape(prior['median_footprint']);east=geo(next(o for o in source['medians'] if o['name'].endswith('_13')))
def section(g,x):
 b=g.intersection(LineString([(x,300),(x,480)])).bounds
 return b[1],b[3]
ws,wn=section(west,3810);es,en=section(east,3960)
wp=Polygon([(3810,ws),(3848,395.7),(3851.8,396),(3854.7,398),(3855.2,400),(3855.2,408.6),(3854.5,410.6),(3852.2,411.1),(3849.8,411),(3810,wn)])
ep=Polygon([(3926.6,387.8),(3927.5,386.2),(3929.5,385.8),(3932.2,386),(3960,es),(3960,en),(3933,401.4),(3930.2,401.1),(3927.3,399.3),(3926.6,397.6)])
wg=unary_union([west.difference(box(3810,300,3860,480)),wp]);eg=unary_union([east.difference(box(3920,300,3960,480)),ep])
def mesh(g,z0=0,z1=.18):
 verts=[];faces=[];ids={}
 def vid(x,y,z):
  k=tuple(round(v,6) for v in (x,y,z))
  if k not in ids:ids[k]=len(verts);verts.append(k)
  return ids[k]
 for p in (list(g.geoms) if g.geom_type=='MultiPolygon' else [g]):
  p=orient(p,1)
  for t in constrained_delaunay_triangles(p).geoms:
   co=list(orient(t,1).exterior.coords)[:-1]
   faces.append([vid(x,y,z1) for x,y in co]);faces.append([vid(x,y,z0) for x,y in reversed(co)])
  for ring in [p.exterior,*p.interiors]:
   co=list(ring.coords)
   for a,b in zip(co,co[1:]):faces.append([vid(*a,z0),vid(*b,z0),vid(*b,z1),vid(*a,z1)])
 return verts,faces
patches=[]
for old,new,g in [('SV_FUDUN_ENTRY_MEDIAN_EST','SV_DUNHUA_WEST_MEDIAN_EST',wg),('CAL_GROUND_MEDIAN_WORKING_ESTIMATED_13','SV_DUNHUA_EAST_MEDIAN_EST',eg)]:
 assert g.is_valid
 v,f=mesh(g);patches.append(dict(source_object=old,new_name=new,footprint=mapping(g),vertices=v,faces=f))
road=shape(prior['road_footprint']);healed=[]
for p in (road.geoms if road.geom_type=='MultiPolygon' else [road]):
 for ring in p.interiors:
  hole=Polygon(ring)
  if 3855<hole.centroid.x<3926 and 390<hole.centroid.y<420:healed.append(hole)
road=unary_union([road,*healed]);v,f=mesh(road,-.25,0)
patches.append(dict(source_object='SV_FUDUN_ENTRY_ROAD_EST',new_name='SV_DUNHUA_ROAD_EST',footprint=mapping(road),vertices=v,faces=f))
checks=[]
for rec in obs['targets']:
 g=wg if 'WEST' in rec['id'] else eg
 p=geo(next(x for x in source['piers'] if x['name']==rec['model_pier_candidate']));c=p.centroid;x,y=rec['candidate_model_xy'];p=affinity.translate(p,x-c.x,y-c.y)
 checks.append({'id':rec['id'],'inside_comparison_median':g.covers(p),'estimated_edge_clearance_m':p.distance(g.boundary) if g.covers(p) else None});assert g.covers(p)
assert wg.intersection(box(3855.3,380,3926.5,430)).area<1e-7
assert eg.intersection(box(3855.3,380,3926.5,430)).area<1e-7
out=dict(patches=patches,omit_from_working_scene=['CAL_GROUND_MEDIAN_WORKING_ESTIMATED_14'],checks=checks,assumptions='Street View proportional curb estimates relative to unverified 2m shaft diameter. Junction opening follows visible west/east island ends; central original median14 absent in observed crossing. Not surveyed curb coordinates.',healed_road_holes=[list(h.bounds) for h in healed],height_changed=False,field_verified=False)
json.dump(out,open(sys.argv[4],'w'),indent=2);print(json.dumps(checks))

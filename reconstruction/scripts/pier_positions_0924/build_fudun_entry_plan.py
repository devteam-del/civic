import json,math,sys
from shapely.geometry import Polygon,LineString,box,shape,mapping
from shapely.ops import unary_union
from shapely import affinity,constrained_delaunay_triangles
from shapely.geometry.polygon import orient
source=json.load(open(sys.argv[1]));prior=json.load(open(sys.argv[2]));obs=[*json.load(open(sys.argv[3]))['targets'],*json.load(open(sys.argv[4]))['targets']]
def geo(o):return unary_union([Polygon(f).buffer(0) for f in o['faces'] if len(f)>2])
g=shape(prior['comparison_footprint'])
old=next(o for o in source['roads'] if o['name']=='CAL_GROUND_ROADS_OFFICIAL_XY_0_FIX0');road=geo(old)
old_top=[3754.2989501953125,411.0269012451172];old_bottom=[3715.1119384765625,420.1443328857422]
old_angle=math.atan2(old_bottom[1]-old_top[1],old_bottom[0]-old_top[0]);angle=math.radians(-7.5)-old_angle
new_top=[3761.590102697537,414.53404589418926]
def move(p):
 x,y=p[0]-old_top[0],p[1]-old_top[1]
 return [new_top[0]+math.cos(angle)*x-math.sin(angle)*y,new_top[1]+math.sin(angle)*x+math.cos(angle)*y]
oldr=Polygon([(3754.695556640625,412.73138427734375),(3753.90234375,409.3224182128906),(3714.71533203125,418.4398498535156),(3715.508544921875,421.84881591796875)])
newr=Polygon([move(p) for p in list(oldr.exterior.coords)[:-1]]);cut=newr.buffer(.30,join_style=2)
def section(x):
 q=g.intersection(LineString([(x,350),(x,480)]));return q.bounds[1],q.bounds[3]
s0,n0=section(3732);s1,n1=section(3810)
patch=Polygon([(3732,s0),(3741,408.7),(3771,404.9),(3798,402),(3810,s1),(3810,n1),(3798,417),(3772,420.4),(3743,424),(3732,n0)])
zone=box(3732,350,3810,480)
approach=LineString([(3745.5,405.6),(3752.5,410.5),(3757.5,414.0),new_top]).buffer(2.05,cap_style=2,join_style=1)
median=unary_union([g.difference(zone),patch]).difference(unary_union([cut,approach]))
roadnew=road.union(oldr.buffer(.40,join_style=2)).difference(cut)
assert median.is_valid and roadnew.is_valid
# Mesh footprints at existing uniform elevations. Constrained triangles preserve boundaries.
def mesh(g,z0,z1):
 verts=[];faces=[];indices={}
 def vid(x,y,z):
  k=tuple(round(v,6) for v in (x,y,z))
  if k not in indices:indices[k]=len(verts);verts.append(list(k))
  return indices[k]
 for p in (list(g.geoms) if g.geom_type=='MultiPolygon' else [g]):
  p=orient(p,1)
  for t in constrained_delaunay_triangles(p).geoms:
   co=list(orient(t,1).exterior.coords)[:-1]
   faces.append([vid(x,y,z1) for x,y in co]);faces.append([vid(x,y,z0) for x,y in reversed(co)])
  for ring in [p.exterior,*p.interiors]:
   co=list(ring.coords)
   for a,b in zip(co,co[1:]):faces.append([vid(*a,z0),vid(*b,z0),vid(*b,z1),vid(*a,z1)])
 return {'vertices':verts,'faces':faces}
checks=[]
for r in obs:
 p=geo(next(o for o in source['piers'] if o['name']==r['model_pier_candidate']));c=p.centroid;q=r['candidate_model_xy'];p=affinity.translate(p,q[0]-c.x,q[1]-c.y)
 checks.append({'pier':r['model_pier_candidate'],'comparison_road_overlap_m2':p.intersection(roadnew).difference(median).area,'ramp_opening_clearance_m':p.distance(cut),'inside_median':median.covers(p)})
 assert median.covers(p) and p.intersection(cut).area<1e-8
out={'status':'Provisional Street View and official-plan-informed entrance comparison; not surveyed','old_top_xy':old_top,'new_top_xy':new_top,'rotation_rad':angle,'new_bottom_xy':move(old_bottom),'depth_and_length_unchanged':True,'placement_basis':'Top center estimated 10m west and 8m north of observed splitter-island south shaft. Direction east-down follows official diagram; -7.5deg alignment estimated from local corridor.','source_ramp':'COMP_ACCESS_復敦_2','source_median':'SV_MEDIAN_P246_P247_EST','source_road':old['name'],'median':mesh(median,0,.18),'road':mesh(roadnew,-.25,0),'median_footprint':mapping(median),'road_footprint':mapping(roadnew),'opening':mapping(cut),'at_grade_approach':mapping(approach),'approach_basis':'Estimated curved feeder from south carriageway, following visible split near P248. Width 4.1m including margins is assumed.','checks':checks,'field_verified':False,'scope':'Ground masks, ramp XY and adjacent column XY. Underground slab/route connection remains a separate check.'}
json.dump(out,open(sys.argv[5],'w'),indent=2)
print(json.dumps({'checks':checks,'new_bottom_xy':out['new_bottom_xy'],'road_vertices':len(out['road']['vertices']),'median_vertices':len(out['median']['vertices'])}))

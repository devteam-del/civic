import json,math,sys
from shapely.geometry import Polygon,LineString,box,mapping
from shapely.ops import unary_union,triangulate
from shapely.geometry.polygon import orient
from shapely import affinity,constrained_delaunay_triangles
inp=json.load(open(sys.argv[1]));north=[json.load(open(p)) for p in sys.argv[2:4]]
old=next(o for o in inp['medians'] if o['name']=='CAL_GROUND_MEDIAN_WORKING_ESTIMATED_12')
def geo(o):return unary_union([Polygon(f).buffer(0) for f in o['faces'] if len(f)>=3])
g=geo(old)
def section(x):
 q=g.intersection(LineString([(x,350),(x,480)]));return q.bounds[1],q.bounds[3]
sw,nw=section(3662);se,ne=section(3732)
west=Polygon([(3662,sw),(3682.7,414.5),(3684.6,414.9),(3686.2,416),(3687,417.8),(3687,426.6),(3686.2,428.3),(3684.6,429.7),(3682.7,430.1),(3662,nw)])
east=Polygon([(3705.5,415.7),(3706.2,414),(3707.7,412.7),(3709.5,412.2),(3712,412),(3732,se),(3732,ne),(3713,427.4),(3709.5,427.5),(3707.5,427),(3706.2,426.2),(3705.5,424.5)])
zone=box(3662,350,3732,480)
new=unary_union([g.difference(zone),west,east]);assert new.is_valid
pieces=list(new.geoms) if new.geom_type=='MultiPolygon' else [new]
verts=[];faces=[];index={}
def vid(x,y,z):
 k=tuple(round(v,6) for v in (x,y,z))
 if k not in index:index[k]=len(verts);verts.append(list(k))
 return index[k]
for poly in pieces:
 poly=orient(poly,1)
 for t in constrained_delaunay_triangles(poly).geoms:
  coords=list(orient(t,1).exterior.coords)[:-1]
  faces.append([vid(x,y,.18) for x,y in coords]);faces.append([vid(x,y,0) for x,y in reversed(coords)])
 for ring in [poly.exterior,*poly.interiors]:
  co=list(ring.coords)
  for a,b in zip(co,co[1:]):faces.append([vid(*a,0),vid(*b,0),vid(*b,.18),vid(*a,.18)])
coords={'UNVERIFIED_Pier_730':[3682.222410814464,416.33840280041875],'UNVERIFIED_Pier_731':north[0]['candidate_model_xy'],'UNVERIFIED_Pier_732':[3711.8750375114078,413.80484597904604],'UNVERIFIED_Pier_733':north[1]['candidate_model_xy']}
checks=[]
road=unary_union([geo(o) for o in inp['roads']])
for name,xy in coords.items():
 p=geo(next(o for o in inp['piers'] if o['name']==name));c=p.centroid;pn=affinity.translate(p,xy[0]-c.x,xy[1]-c.y)
 checks.append({'pier':name,'xy':xy,'old_mask_overlap_m2':pn.intersection(road).difference(g).area,'comparison_mask_overlap_m2':pn.intersection(road).difference(new).area,'boundary_clearance_m':pn.distance(new.boundary) if new.covers(pn) else None})
 assert new.covers(pn)
opening=box(3687.01,412,3705.49,428)
assert new.intersection(opening).area<1e-8
assert g.symmetric_difference(new).difference(zone).area<1e-8
out={'source_median':old['name'],'new_name':'SV_MEDIAN_P246_P247_EST','vertices':verts,'faces':faces,'comparison_footprint':mapping(new),'checks':checks,'opening_model_x':[3687,3705.5],'unchanged_outside_zone':True,'status':'Street View-informed proportional comparison, NOT measured curb coordinates','assumptions':{'curb_height_m':.18,'retained_shaft_radius_m':1,'island_end_and_curbs':'estimated from photographs relative to retained shaft diameter; not independently triangulated','scope_x':[3662,3732]},'pair_spacing_m':[math.dist(coords['UNVERIFIED_Pier_730'],coords['UNVERIFIED_Pier_731']),math.dist(coords['UNVERIFIED_Pier_732'],coords['UNVERIFIED_Pier_733'])],'field_verified':False}
json.dump(out,open(sys.argv[4],'w'),indent=2);print(json.dumps({k:out[k] for k in ['checks','pair_spacing_m','unchanged_outside_zone']}))

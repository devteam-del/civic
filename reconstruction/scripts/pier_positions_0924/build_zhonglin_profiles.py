"""Estimate Zhonglin outer island envelopes while retaining both ramp openings."""
import json,sys
from pathlib import Path
from shapely.geometry import Polygon,mapping
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
root=Path(sys.argv[1]);out=Path(sys.argv[2]);live=json.loads((root/'live_comparison_ground_footprints.json').read_text())
def geo(o):return unary_union([Polygon(f).buffer(0) for f in o['faces']])
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
jobs=[('WEST',2,['zhonglin_west_exit_position_review.json','zhonglin_ramp_middle_position_review.json','zhonglin_access_west_position_review.json'],None,1202),('EAST',1,['p145_missing_support_review.json','west_visible_p147_position_review.json','east_visible_p147_position_review.json','ramp_east_portal_position_review.json'],1224,None)]
patches=[]
for label,index,files,x0,x1 in jobs:
 source='CAL_GROUND_MEDIAN_WORKING_ESTIMATED_'+str(index);old=geo(next(o for o in live['medians'] if o['name']==source));holes=unary_union([Polygon(h) for p in (old.geoms if old.geom_type=='MultiPolygon' else[old]) for h in p.interiors]);chains={'NORTH':[],'SOUTH':[]}
 for file in files:
  for t in json.loads((root/file).read_text())['targets']:
   for side,offset in [('NORTH',1.8),('SOUTH',-1.8)]:
    if t['id'].endswith(side):x,y=t['candidate_model_xy'];chains[side].append([x,y+offset])
 for pts in chains.values():
  pts.sort();a,b=pts[:2];m=(b[1]-a[1])/(b[0]-a[0]);left=old.bounds[0] if x0 is None else x0;pts.insert(0,[left,a[1]+m*(left-a[0])]);a,b=pts[-2:];m=(b[1]-a[1])/(b[0]-a[0]);right=old.bounds[2] if x1 is None else x1;pts.append([right,b[1]+m*(right-b[0])])
 new=old.union(Polygon(chains['SOUTH']+list(reversed(chains['NORTH'])))).difference(holes);assert new.is_valid and new.intersection(holes).area<1e-6
 v,f=mesh(new,0,.18);patches.append({'name':'SV_ZHONGLIN_'+label+'_MEDIAN_PROFILE_EST','source_object':source,'footprint':mapping(new),'vertices':v,'faces':f,'source_records':files,'ramp_hole_area_preserved_m2':holes.area,'ramp_hole_fill_m2':new.intersection(holes).area,'bounds':list(new.bounds),'width_status':'1.8m shaft-centre-to-curb allowance, estimated. Junction end positions provisional; ramp holes preserved from existing model.','survey_verified':False})
data={'patches':patches,'sources':['https://www.google.com/maps/@?api=1&map_action=pano&pano=A1INyU_mtrtr7HQ7Mi628Q&heading=60&pitch=0&fov=90','https://www.google.com/maps/@?api=1&map_action=pano&pano=ou2ErwddbzjJ86pJUdSlnA&heading=60&pitch=0&fov=90','https://www.google.com/maps/@?api=1&map_action=pano&pano=-WmQYYv_MpykCU0KH86NHw&heading=0&pitch=0&fov=90'],'estimated_junction_gap_x_m':[1202,1224],'status':'Comparison geometry only; inner ramps and metric curb dimensions are not independently surveyed.'}
out.write_text(json.dumps(data,indent=2));print(json.dumps([{k:p[k] for k in ['name','bounds','ramp_hole_area_preserved_m2','ramp_hole_fill_m2']} for p in patches]))

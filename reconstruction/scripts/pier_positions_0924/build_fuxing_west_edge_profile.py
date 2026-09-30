"""Extend observed service-platform edges around P233; retain existing openings."""
import json,sys
from pathlib import Path
from shapely.geometry import Polygon,shape,mapping
from shapely.ops import unary_union
root=Path(sys.argv[1]);out=Path(sys.argv[2]);live=json.loads((root/'live_comparison_ground_footprints.json').read_text());ns={};exec((root/'build_zhonglin_profiles.py').read_text().split('jobs=')[0].replace('root=Path(sys.argv[1]);out=Path(sys.argv[2]);live=json.loads((root/\'live_comparison_ground_footprints.json\').read_text())',''),ns)
old=unary_union([Polygon(f).buffer(0) for o in live['medians'] if o['name']=='SV_FUXING_SERVICE_MEDIAN_EST' for f in o['faces']]);chains={'NORTH':[],'SOUTH':[]}
for file in ['west233_position_review.json','west233_missing_south_review.json','p233_position_review.json']:
 for t in json.loads((root/file).read_text())['targets']:
  for side,off in [('NORTH',1.8),('SOUTH',-1.8)]:
   if t['id'].endswith(side):x,y=t['candidate_model_xy'];chains[side].append([x,y+off])
for pts in chains.values():
 pts.sort();a,b=pts[:2];m=(b[1]-a[1])/(b[0]-a[0]);pts.insert(0,[3226,a[1]+m*(3226-a[0])]);a,b=pts[-2:];m=(b[1]-a[1])/(b[0]-a[0]);pts.append([3280,b[1]+m*(3280-b[0])])
guard=unary_union([shape(o['geometry']) for o in json.loads((root/'opening_guard_inventory.json').read_text())['guards']]);new=old.union(Polygon(chains['SOUTH']+list(reversed(chains['NORTH'])))).difference(guard);v,f=ns['mesh'](new,0,.18)
p={'name':'SV_FUXING_WEST_GUARDED_MEDIAN_EST','source_object':'SV_FUXING_SERVICE_MEDIAN_EST','footprint':mapping(new),'vertices':v,'faces':f,'ramp_hole_fill_m2':new.intersection(guard).area,'width_status':'1.8m shaft-centre curb allowance; west endpoint x3226 estimated. Planted and paved service platform visibly continuous; absolute edge remains unmeasured.','survey_verified':False,'added_area_m2':new.difference(old).area}
d={'patches':[p],'sources':['https://www.google.com/maps/@?api=1&map_action=pano&pano=GNaYshgbXGqT6PZXF7RvSw&heading=280&pitch=0&fov=90','https://www.google.com/maps/@?api=1&map_action=pano&pano=DR6MCGZceRhZANA1l07MJQ&heading=260&pitch=0&fov=90'],'unavailable_previous_pano':'_ANyhDdl75_b8UwXWKHkGw','status':'Working geometry estimate, not independent field clearance proof.'};out.write_text(json.dumps(d,indent=2));print(p['added_area_m2'])

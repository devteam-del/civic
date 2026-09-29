"""Continuous provisional outer envelope, preserving observed pedestrian and U-turn gaps."""
import json,sys
from pathlib import Path
from shapely.geometry import Polygon,shape,mapping
root=Path(sys.argv[1]);out=Path(sys.argv[2]);old=json.loads((root/'huaisheng_profile_plan.json').read_text());base=shape(old['footprint']);opening=json.loads((root/'huaisheng_opening_plan.json').read_text());chains={'NORTH':[],'SOUTH':[]};files=['blue_portal','ramp_merge','west_portal','west_footbridge','huaisheng_footbridge','huaisheng_west','huaisheng','antong_west']
for file in files:
 for t in json.loads((root/(file+'_position_review.json')).read_text())['targets']:
  for side,offset in [('NORTH',1.8),('SOUTH',-1.8)]:
   if t['id'].endswith(side):x,y=t['candidate_model_xy'];chains[side].append([x,y+offset])
for points in chains.values():
 points.sort();a,b=points[:2];m=(b[1]-a[1])/(b[0]-a[0]);points.insert(0,[base.bounds[0],a[1]+m*(base.bounds[0]-a[0])]);a,b=points[-2:];m=(b[1]-a[1])/(b[0]-a[0]);points.append([base.bounds[2],b[1]+m*(base.bounds[2]-b[0])])
profile=Polygon(chains['SOUTH']+list(reversed(chains['NORTH'])));new=base.union(profile).difference(shape(opening['cut_footprint']));assert new.is_valid
record={'name':'SV_BLUE_HUAISHENG_PROFILE_MEDIAN_EST','source_object':'SV_HUAISHENG_PROFILE_MEDIAN_EST','footprint':mapping(new),'z_min':0.,'z_max':.18,'source_records':[f+'_position_review.json' for f in files],'sources':old['sources']+['https://www.google.com/maps/@?api=1&map_action=pano&pano=dMVEE6UYTNXGPO74I7fYNw&heading=300&pitch=0&fov=90'],'existence_status':'Street imagery shows a mixed paved/landscaped apron around shafts beneath the ramp/mainline.','width_status':'1.8m centre-to-curb allowance is a provisional proportional assumption; previous local 2m estimate retained where wider. Existing inner access geometry still needs separate calibration.','opening_preserved':True,'pedestrian_gap_west_preserved':True,'estimated_added_area_m2':new.area-base.area,'survey_verified':False}
out.write_text(json.dumps(record,indent=2));print(json.dumps({'added_area':record['estimated_added_area_m2'],'parts':len(new.geoms),'bounds':new.bounds}))

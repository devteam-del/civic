"""Provisional outer island profile around visually island-supported shafts."""
import json,sys
from pathlib import Path
from shapely.geometry import Polygon,box,shape,mapping
root=Path(sys.argv[1]);out=Path(sys.argv[2]);old=json.loads((root/'huaisheng_opening_plan.json').read_text());poly=shape(old['footprint']);north=[];south=[]
files=['huaisheng_footbridge','huaisheng_west','huaisheng','antong_west']
for name in files:
 d=json.loads((root/(name+'_position_review.json')).read_text())
 for side,chain,offset in [('NORTH',north,2.),('SOUTH',south,-2.)]:
  t=next(t for t in d['targets'] if t['id'].endswith(side));x,y=t['candidate_model_xy'];chain.append([x,y+offset])
# Outer bounds use a 2m centre-to-curb allowance as a modelling assumption.
# Keep the observed U-turn cut and the rest of the existing island untouched.
for chain in [north,south]:
 a,b=chain[:2];m=(b[1]-a[1])/(b[0]-a[0]);chain.insert(0,[3090,a[1]+m*(3090-a[0])]);a,b=chain[-2:];m=(b[1]-a[1])/(b[0]-a[0]);chain.append([3203,b[1]+m*(3203-b[0])])
profile=Polygon(south+list(reversed(north)));new=poly.union(profile).difference(shape(old['cut_footprint']))
assert new.is_valid
record={'name':'SV_HUAISHENG_PROFILE_MEDIAN_EST','source_object':'SV_HUAISHENG_UTURN_MEDIAN_EST','footprint':mapping(new),'z_min':0.,'z_max':.18,'source_records':[x+'_position_review.json' for x in files],'sources':old['sources']+['https://www.google.com/maps/@?api=1&map_action=pano&pano=prIvsXdMJmC7MzOTUvY5jg&heading=300&pitch=0&fov=90'],'existence_status':'Ground views show the paired shafts supported within planted/equipment islands; earlier GIS median edge left south shafts outside.','width_status':'Outer edges use provisional 2m centre-to-curb allowances; this does not independently validate pier clearance. Detailed curb survey remains pending.','opening_preserved':True,'added_area_m2':new.area-poly.area,'survey_verified':False}
out.write_text(json.dumps(record,indent=2));print(json.dumps({'added_area_m2':record['added_area_m2'],'parts':len(new.geoms)}))

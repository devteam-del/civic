"""Estimate island/apron envelope from observed shaft rows, retaining pedestrian gap."""
import json,sys
from pathlib import Path
from shapely.geometry import Polygon,shape,mapping
from shapely.ops import unary_union
root=Path(sys.argv[1]);out=Path(sys.argv[2]);live=json.loads((root/'live_comparison_ground_footprints.json').read_text());old=next(o for o in live['medians'] if o['name']=='CAL_GROUND_MEDIAN_WORKING_ESTIMATED_6');base=unary_union([Polygon(f).buffer(0) for f in old['faces']]);chains={'NORTH':[],'SOUTH':[]};files=['jianguo_east_edge','west_white_next','ramp_screen_end','painted_temple','painted_church','west_blue_portal','west_blue_portal_south']
for file in files:
 for t in json.loads((root/(file+'_position_review.json')).read_text())['targets']:
  for side,offset in [('NORTH',1.8),('SOUTH',-1.8)]:
   if t['id'].endswith(side):x,y=t['candidate_model_xy'];chains[side].append([x,y+offset])
for side,points in chains.items():
 points.sort();a,b=points[:2];slope=(b[1]-a[1])/(b[0]-a[0]);points.insert(0,[base.bounds[0],a[1]+slope*(base.bounds[0]-a[0])]);a,b=points[-2:];slope=(b[1]-a[1])/(b[0]-a[0]);points.append([2930,b[1]+slope*(2930-b[0])])
profile=Polygon(chains['SOUTH']+list(reversed(chains['NORTH'])));new=base.union(profile);assert new.is_valid
record={'name':'SV_JIANGUO_EAST_APRON_MEDIAN_EST','source_object':old['name'],'footprint':mapping(new),'z_min':0.,'z_max':.18,'sources':['https://www.google.com/maps/@?api=1&map_action=pano&pano=dMVEE6UYTNXGPO74I7fYNw&heading=300&pitch=0&fov=90','https://www.google.com/maps/@?api=1&map_action=pano&pano=kPznn-dd5_zfp-H7LCd-Wg&heading=190&pitch=0&fov=90'],'source_records':[f+'_position_review.json' for f in files],'existence_status':'Street imagery shows shafts on planted strips or raised paved aprons, with a bollard-controlled pedestrian crossing immediately east of the western blue portal shaft.','width_status':'Outer edges use provisional 1.8m allowances; eastern edge x=2930 leaves the existing eastern pedestrian gap open. This is an estimated ground envelope, not measured lane boundaries.','topology_status':'Mixed planting/paved apron; do not classify the whole mass as planting. Pedestrian gap remains east of x2930.','estimated_added_area_m2':new.area-base.area,'survey_verified':False}
out.write_text(json.dumps(record,indent=2));print(json.dumps({'type':new.geom_type,'area_added':record['estimated_added_area_m2'],'bounds':new.bounds}))

"""Local raised outer aprons for observed P126/P127 shafts; centre kept untouched."""
import json,sys
from pathlib import Path
from shapely.geometry import LineString,mapping
r=Path(sys.argv[1]);out=Path(sys.argv[2]);patches=[]
files=['p126_position_review.json','chengde_west_edge_position_review.json']
for side in ['NORTH','SOUTH']:
 ts=[next(t for t in json.loads((r/f).read_text())['targets'] if t['id'].endswith(side)) for f in files];p=LineString([t['candidate_model_xy'] for t in ts]).buffer(1.8,quad_segs=12)
 patches.append({'name':'SV_CHENGDE_WEST_'+side+'_MEDIAN_APRON_EST','footprint':mapping(p),'z_min':0.,'z_max':.18,'estimated_width_m':3.6,'source_records':files,'source_piers':[t['comparison_object'] for t in ts],'width_status':'Provisional 3.6m outer apron strips around observed shafts, not a survey of the entire courtyard.','existence_evidence':'2025-05 north-side views show shafts on planted/gravel raised ground beside equipment structures. South base is partly obscured by ramps and equipment.','scope':'Only exterior strips added; central Y9/equipment/entry zone and Chengde road crossing left untouched.','survey_verified':False})
d={'patches':patches,'sources':['https://www.google.com/maps/@?api=1&map_action=pano&pano=ip38ubFy0LGqZwVEY0ZJyQ&heading=210&pitch=0&fov=90','https://www.google.com/maps/@?api=1&map_action=pano&pano=Fjv4SMBu-sf4A7kO1RmSXw&heading=120&pitch=0&fov=90'],'date':'2025-05'};out.write_text(json.dumps(d,indent=2));print(json.dumps([p['name'] for p in patches]))

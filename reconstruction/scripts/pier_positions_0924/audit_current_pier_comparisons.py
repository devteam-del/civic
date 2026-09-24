import json,sys
from pathlib import Path
from shapely.geometry import Polygon,shape
from shapely.ops import unary_union
from shapely import affinity
base=Path(sys.argv[1]);out=Path(sys.argv[2]);r24=base/'PierPositions_20260924';r23=base/'PierPositions_20260923'
source=json.loads((base/'Underbridge_20260922'/'pier_road_footprints.json').read_text())
review=json.loads((base/'Underbridge_20260922'/'pier_road_overlap_review.json').read_text())
patch=json.loads((r24/'p246_247_median_comparison.json').read_text())
def geo(o):return unary_union([Polygon(f).buffer(0) for f in o['faces'] if len(f)>=3])
entry=json.loads((r24/'fudun_entry_plan.json').read_text())
road=unary_union([geo(o) for o in source['roads'] if o['name']!=entry['source_road']]+[shape(entry['road_footprint'])]);median=unary_union([geo(o) for o in source['medians'] if o['name']!=patch['source_median']]+[shape(entry['median_footprint'])])
junction=json.loads((r24/'east_corridor_median_comparison.json').read_text())
median=unary_union([geo(o) for o in source['medians'] if o['name'] not in [patch['source_median'],'CAL_GROUND_MEDIAN_WORKING_ESTIMATED_13',*junction['omit_from_working_scene']]]+[shape(p['footprint']) for p in junction['patches'] if 'MEDIAN' in p['new_name']])
road=unary_union([geo(o) for o in source['roads'] if o['name']!=entry['source_road']]+[shape(p['footprint']) for p in junction['patches'] if p['new_name']=='SV_DUNHUA_ROAD_EST'])
records={}
for p in [r23/'fuxing_642_position_review.json',r24/'p246_position_review.json',r24/'p247_position_review.json',r24/'p246_north_position_review.json',r24/'p247_north_position_review.json']:
 d=json.loads(p.read_text());records[d['model_pier_candidate']]=d
for filename in ['p248_position_review.json','east248_position_review.json','p250_position_review.json','dunhua_junction_position_review.json','east252_position_review.json','p254_position_review.json','east254_position_review.json','east254_next_position_review.json','p257_position_review.json','east257_position_review.json','p259_position_review.json','east259_position_review.json','east260_position_review.json','p262_position_review.json','east262_position_review.json']:
 for rec in json.loads((r24/filename).read_text())['targets']:records[rec['model_pier_candidate']]=rec
suspects={r['pier'] for r in review['piers'] if r['status']=='ROAD_OVERLAP_REVIEW'}
rows=[]
for o in source['piers']:
 p=geo(o);name=o['name'];xy=list(p.centroid.coords[0]);d=records.get(name)
 if d:
  new=d['candidate_model_xy'];p=affinity.translate(p,new[0]-xy[0],new[1]-xy[1]);xy=new
 area=p.intersection(road).difference(median).area
 rows.append({'pier':name,'xy':xy,'original_suspect':name in suspects,'streetview_xy_comparison':bool(d),'road_outside_comparison_median_m2':area,'model_mask_clear':area<1e-5,'real_world_verified':False,'resolved':False})
result={'scope':'Current comparison geometry only. Model-mask clearance is not independent field validation.','original_suspects':len(suspects),'suspects_with_xy_comparison':sum(r['original_suspect'] and r['streetview_xy_comparison'] for r in rows),'total_xy_comparisons':len(records),'remaining_model_mask_overlaps':sum(r['road_outside_comparison_median_m2']>1e-5 for r in rows),'field_verified':0,'rows':rows}
out.write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='rows'}))

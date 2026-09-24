"""Build explicit 124-suspect progress ledger, never count model clearance as field validation."""
import bpy,json
from pathlib import Path
base=Path(bpy.data.filepath).parent;root=base/'PierPositions_20260924'
raw=json.loads((base/'Underbridge_20260922'/'pier_road_overlap_review.json').read_text())
rows=[]
for r in raw['piers']:
 if r['status']!='ROAD_OVERLAP_REVIEW':continue
 rows.append({'model_pier':r['pier'],'original_xy':r['xy'],'original_overlap_m2':r['road_outside_median_m2'],'state':'awaiting_object_matched_streetview','actual_label':None,'field_verified':False,'resolved':False})
assert len(rows)==124
for r in rows:
 if r['model_pier']=='UNVERIFIED_Pier_642':
  r.update(state='provisional_xy_applied_model_clearance_only',record='../PierPositions_20260923/fuxing_642_position_review.json')
 if r['model_pier']=='UNVERIFIED_Pier_732':
  r.update(state='provisional_xy_applied_ground_boundary_conflict',actual_label='P247',record='p247_position_review.json')
 if r['model_pier']=='UNVERIFIED_Pier_730':
  r.update(state='provisional_xy_applied_ground_boundary_conflict',actual_label='P246',record='p246_position_review.json')
data={'scope':'124 road-overlap suspects only; other 117 are outside this queue','total':124,'fully_resolved':0,'field_verified':0,'provisional_xy_applied':3,'height_and_deck_edits_paused':True,'rows':rows}
(root/'conflict124_progress.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
result={'total':124,'provisional_xy_applied':3,'fully_resolved':0}

import bpy,json
from pathlib import Path
root=Path(bpy.data.filepath).parent/'PierPositions_20260924'
scene=bpy.data.scenes['CIVIC_PIER_XY_REVIEW_20260923']
jobs=[('p234_missing_north_review.json','apply_missing_support_observations.py'),('p233_position_review.json','apply_observation_set_xy.py'),('west233_position_review.json','apply_observation_set_xy.py'),('west233_missing_south_review.json','apply_missing_support_observations.py'),('antong_west_position_review.json','apply_observation_set_xy.py')]
checks=[]
for filename,script in jobs:
 records=json.loads((root/filename).read_text())['targets']
 if all(r.get('comparison_object') in scene.objects for r in records):
  checks.append({'file':filename,'already_present':True});continue
 assert not any(r.get('comparison_object') in scene.objects for r in records),'Partial application needs review'
 code=(root/script).read_text().replace('scene=bpy.context.scene',"scene=bpy.data.scenes['CIVIC_PIER_XY_REVIEW_20260923']")
 ns={'INPUT_FILE':filename};exec(compile(code,script,'exec'),ns)
 checks.append(ns['result'])
result={'checks':checks,'scope':'XY only; original scene retained. No automatic road widening, height or cap edits.'}

"""Restore the unmatched intermediate support comparison from recorded estimates."""
import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(bpy.data.filepath).parent/'PierPositions_20260924'
scene=bpy.context.scene
assert scene.name=='CIVIC_PIER_XY_REVIEW_20260923'
data=json.loads((root/'east274_missing_support_review.json').read_text())
col=bpy.data.collections.get('SV_ADDED_SUPPORT_COMPARISON')
if col is None:
 col=bpy.data.collections.new('SV_ADDED_SUPPORT_COMPARISON');scene.collection.children.link(col)
for rec in data['targets']:
 side=rec['id'].rsplit('_',1)[-1]
 template=bpy.data.objects['SV_XY_EST_P274_'+side+'_MODEL'+('392' if side=='NORTH' else '393')]
 name='SV_ADDED_EST_'+rec['id']
 obj=bpy.data.objects.get(name)
 if obj is None:
  obj=template.copy();obj.data=template.data.copy();obj.name=name;col.objects.link(obj)
 pts=[obj.matrix_world@Vector(v) for v in obj.bound_box]
 xy=[sum(v[i] for v in pts)/8 for i in range(2)]
 obj.matrix_world.translation+=Vector((rec['candidate_model_xy'][0]-xy[0],rec['candidate_model_xy'][1]-xy[1],0))
 obj['source_record']='east274_missing_support_review.json'
 obj['source_object']='No assigned legacy counterpart'
 obj['survey_verified']=False
 obj['status']='Missing-support comparison. North XY observed; south offset estimated. Circular proxy and inherited height await later calibration.'
 obj['height_unchanged']=True
result={'added_support_comparisons':[r['comparison_object'] for r in data['targets']],'resolved':False}

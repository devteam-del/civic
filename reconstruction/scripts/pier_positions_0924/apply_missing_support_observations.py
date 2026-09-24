"""Add observed supports absent from legacy model, keeping dimensions explicitly provisional."""
import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(bpy.data.filepath).parent/'PierPositions_20260924'
scene=bpy.context.scene
assert scene.name=='CIVIC_PIER_XY_REVIEW_20260923'
data=json.loads((root/INPUT_FILE).read_text())
col=bpy.data.collections.get('SV_ADDED_SUPPORT_COMPARISON')
if col is None:
 col=bpy.data.collections.new('SV_ADDED_SUPPORT_COMPARISON');scene.collection.children.link(col)
checks=[]
for rec in data['targets']:
 assert rec.get('model_pier_candidate') is None
 assert rec['geometry_condition']=='usable_for_provisional_comparison'
 template=scene.objects[rec['geometry_template']]
 name='SV_ADDED_EST_'+rec['id'];assert bpy.data.objects.get(name) is None
 obj=template.copy();obj.data=template.data.copy();obj.name=name
 pts=[obj.matrix_world@Vector(v) for v in obj.bound_box];xy=[sum(v[i] for v in pts)/8 for i in range(2)]
 obj.matrix_world.translation+=Vector((rec['candidate_model_xy'][0]-xy[0],rec['candidate_model_xy'][1]-xy[1],0))
 col.objects.link(obj)
 obj['source_record']=INPUT_FILE;obj['source_object']='No assigned legacy counterpart'
 obj['status']='Street View XY comparison; dimensions and height inherited from recorded template, not measured'
 obj['survey_verified']=False;obj['height_unchanged']=True
 rec.update(comparison_object=obj.name,resolved=False,geometry_status='Inherited template dimensions and height; pending calibration')
 checks.append({'object':obj.name,'xy_applied':True,'height_inherited':True})
(root/INPUT_FILE).write_text(json.dumps(data,indent=2))
result={'checks':checks,'resolved':False}

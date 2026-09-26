"""Apply a reviewed observation set as XY-only comparisons in the working scene."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
root=Path(bpy.data.filepath).parent/'PierPositions_20260924'
scene=bpy.context.scene
assert scene.name=='CIVIC_PIER_XY_REVIEW_20260923'
d=json.loads((root/INPUT_FILE).read_text())
replacements={};checks=[]
for rec in d['targets']:
 old=scene.objects[rec.get('replace_comparison_object',rec['model_pier_candidate'])]
 if rec.get('replace_comparison_object'):
  archive=bpy.data.scenes.get('CIVIC_SUPERSEDED_XY') or bpy.data.scenes.new('CIVIC_SUPERSEDED_XY')
  if old.name not in archive.objects:archive.collection.objects.link(old)
 name='SV_XY_EST_'+rec['id']+'_MODEL'+old.name.rsplit('_',1)[-1]
 assert bpy.data.objects.get(name) is None
 assert rec['geometry_condition']=='usable_for_provisional_comparison'
 pts=[old.matrix_world@Vector(v) for v in old.bound_box];xy=[sum(v[i] for v in pts)/8 for i in range(2)]
 ob=old.copy();ob.data=old.data.copy();ob.name=name
 delta=[rec['candidate_model_xy'][i]-xy[i] for i in range(2)]
 ob.matrix_world.translation+=Vector((*delta,0))
 ob['source_object']=old.name;ob['source_record']=INPUT_FILE;ob['height_unchanged']=True
 ob['survey_verified']=False;ob['status']='Street View XY estimate; source correspondence provisional'
 assert [(ob.matrix_world@v.co).z for v in ob.data.vertices]==[(old.matrix_world@v.co).z for v in old.data.vertices]
 rec.update(original_xy=xy,delta_xy=delta,comparison_object=ob.name,association_status='Provisional model association using shaft sequence, road side and visible landmarks',resolved=False)
 replacements[old]=ob;checks.append({'object':ob.name,'world_z_unchanged':True,'source_preserved':True})
flags={}
def read_flags(lc):
 flags[lc.collection]=(lc.exclude,lc.hide_viewport)
 for ch in lc.children:read_flags(ch)
read_flags(scene.view_layers[0].layer_collection)
memo={}
def clone(c):
 if c in memo:return memo[c]
 if not any(o in c.all_objects[:] for o in replacements):return c
 nc=bpy.data.collections.new(c.name+'_SV_XY');memo[c]=nc
 nc.hide_render=c.hide_render;nc.hide_viewport=c.hide_viewport
 for o in c.objects:nc.objects.link(replacements.get(o,o))
 for ch in c.children:nc.children.link(clone(ch))
 return nc
for c in list(scene.collection.children):
 nc=clone(c)
 if nc!=c:scene.collection.children.unlink(c);scene.collection.children.link(nc)
for old,new in replacements.items():
 if old.name in scene.collection.objects:scene.collection.objects.unlink(old);scene.collection.objects.link(new)
inverse={v:k for k,v in memo.items()}
def restore(lc):
 src=inverse.get(lc.collection,lc.collection)
 if src in flags:lc.exclude,lc.hide_viewport=flags[src]
 for ch in lc.children:restore(ch)
for vl in scene.view_layers:restore(vl.layer_collection)
bpy.context.view_layer.update()
for old,new in replacements.items():
 assert old.name not in scene.objects
 assert old.name in bpy.data.objects
 assert new.name in scene.objects
(root/INPUT_FILE).write_text(json.dumps(d,ensure_ascii=False,indent=2))
result={'checks':checks,'scope':'XY only; no ground, height or cap edits'}

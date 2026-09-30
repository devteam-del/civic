"""Reversible Street View proportional median comparison at Dunhua junction."""
import bpy,bmesh,json
from pathlib import Path
root=Path(bpy.data.filepath).parent/'PierPositions_20260924'
scene=bpy.context.scene
assert scene.name=='CIVIC_PIER_XY_REVIEW_20260923'
d=json.loads((root/'ramp_east_extended_median_comparison.json').read_text())
replacements={};checks=[]
for patch in d['patches']:
 if patch['new_name'] in scene.objects:continue
 old=scene.objects[patch['source_object']]
 assert bpy.data.objects.get(patch['new_name']) is None
 me=bpy.data.meshes.new(patch['new_name']);me.from_pydata(patch['vertices'],[],patch['faces']);me.update()
 bm=bmesh.new();bm.from_mesh(me)
 bmesh.ops.dissolve_degenerate(bm,dist=.001,edges=list(bm.edges))
 nonmanifold=sum(not e.is_manifold for e in bm.edges);zero=sum(f.calc_area()<1e-9 for f in bm.faces)
 assert nonmanifold==0 and zero==0,(nonmanifold,zero)
 bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(patch['new_name'],me)
 for mat in old.data.materials:me.materials.append(mat)
 ob['source_object']=old.name;ob['source_record']='ramp_east_extended_median_comparison.json'
 ob['survey_verified']=False;ob['status']=d['assumptions']
 replacements[old]=ob;checks.append(dict(object=ob.name,nonmanifold=nonmanifold,zero_area=zero))
for name in d['omit_from_working_scene']:
 if name in scene.objects and scene.objects[name] not in replacements:replacements[scene.objects[name]]=None
flags={}
def read_flags(lc):
 flags[lc.collection]=(lc.exclude,lc.hide_viewport)
 for ch in lc.children:read_flags(ch)
read_flags(scene.view_layers[0].layer_collection)
memo={}
def clone(c):
 if c in memo:return memo[c]
 if not any(o in c.all_objects[:] for o in replacements):return c
 nc=bpy.data.collections.new(c.name+'_DUNHUA_XY');memo[c]=nc
 nc.hide_render=c.hide_render;nc.hide_viewport=c.hide_viewport
 for o in c.objects:
  n=replacements.get(o,o)
  if n is not None:nc.objects.link(n)
 for ch in c.children:nc.children.link(clone(ch))
 return nc
for c in list(scene.collection.children):
 nc=clone(c)
 if nc!=c:scene.collection.children.unlink(c);scene.collection.children.link(nc)
for old,new in replacements.items():
 if old.name in scene.collection.objects:
  scene.collection.objects.unlink(old)
  if new is not None:scene.collection.objects.link(new)
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
 if new is not None:assert new.name in scene.objects
for side in ['SOUTH','NORTH']:
 o=bpy.data.objects.get('SV_MARKER_DUNHUA_WEST_'+side)
 if o:
  o['status']='Provisional association now in dunhua_junction_position_review.json'
  o.hide_viewport=True;o.hide_render=True
report={'mesh_checks':checks,'source_preserved':True,'median14_omitted_only_from_working_scene':True,'curbs_estimated':True}
(root/'ramp_east_extended_median_application.json').write_text(json.dumps(report,indent=2))
result=report

assert all(p['new_name'] in scene.objects for p in d['patches']), 'Expected ground comparison missing from working scene'

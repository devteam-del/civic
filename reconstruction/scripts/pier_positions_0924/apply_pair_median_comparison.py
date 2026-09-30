"""Apply local pier-pair and median comparison; source objects stay in other scenes."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
root=Path(bpy.data.filepath).parent/'PierPositions_20260924'
scene=bpy.context.scene
assert scene.name=='CIVIC_PIER_XY_REVIEW_20260923'
d=json.loads((root/'p246_247_median_comparison.json').read_text())
assert bpy.data.objects.get(d['new_name']) is None
replacements={};checks=[]
for num,label,filename in [(731,'P246_NORTH','p246_north_position_review.json'),(733,'P247_NORTH','p247_north_position_review.json')]:
 old=scene.objects['UNVERIFIED_Pier_%03d'%num];p=json.loads((root/filename).read_text())
 pts=[old.matrix_world@Vector(v) for v in old.bound_box];xy=[sum(v[i] for v in pts)/8 for i in range(2)]
 ob=old.copy();ob.data=old.data.copy();ob.name='SV_XY_EST_'+label+'_MODEL'+str(num)
 ob.matrix_world.translation+=Vector((p['candidate_model_xy'][0]-xy[0],p['candidate_model_xy'][1]-xy[1],0))
 ob['source_object']=old.name;ob['source_record']=filename;ob['survey_verified']=False
 ob['status']='Street View XY estimate; north-side own label unread';ob['height_unchanged']=True
 assert [(ob.matrix_world@v.co).z for v in ob.data.vertices]==[(old.matrix_world@v.co).z for v in old.data.vertices]
 p.update(original_xy=xy,model_pier_candidate=old.name,comparison_object=ob.name,association_status='Provisional same-span north-side correspondence; not independently numbered',height_changed=False)
 (root/filename).write_text(json.dumps(p,ensure_ascii=False,indent=2))
 replacements[old]=ob;checks.append({'object':ob.name,'world_z_unchanged':True})
old=scene.objects[d['source_median']]
me=bpy.data.meshes.new(d['new_name']);me.from_pydata(d['vertices'],[],d['faces']);me.update()
bm=bmesh.new();bm.from_mesh(me);nonmanifold=sum(not e.is_manifold for e in bm.edges);zero=sum(f.calc_area()<1e-9 for f in bm.faces);bm.free()
assert nonmanifold==0,(nonmanifold,zero)
assert zero==0
ob=bpy.data.objects.new(d['new_name'],me)
for mat in old.data.materials:me.materials.append(mat)
ob['source_object']=old.name;ob['source_record']='p246_247_median_comparison.json';ob['survey_verified']=False
ob['status']=d['status'];ob['curb_coordinates_estimated']=True
replacements[old]=ob
flags={}
def read_flags(lc):
 flags[lc.collection]=(lc.exclude,lc.hide_viewport)
 for ch in lc.children:read_flags(ch)
read_flags(scene.view_layers[0].layer_collection)
memo={}
def clone(c):
 if c in memo:return memo[c]
 if not any(o in c.all_objects[:] for o in replacements):return c
 nc=bpy.data.collections.new(c.name+'_PAIR_MEDIAN');memo[c]=nc
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
 assert old.name not in scene.objects and new.name in scene.objects
 assert old.name in bpy.data.scenes['CIVIC_FULL_CORRIDOR_PRESENTATION'].objects
report={'north_piers':checks,'median_nonmanifold_edges':nonmanifold,'median_zero_area_faces':zero,'source_objects_preserved':True,'remaining':'Curb coordinates and pairing provisional. Caps, bearings, heights and deck alignment deferred. No claim of survey validation.'}
(root/'pair_median_application.json').write_text(json.dumps(report,indent=2))
result=report

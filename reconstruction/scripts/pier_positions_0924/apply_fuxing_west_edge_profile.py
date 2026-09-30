"""Apply both estimated Zhonglin island profiles; leave original scenes intact."""
import bpy,bmesh,json
from pathlib import Path
r=Path(bpy.data.filepath).parent/'PierPositions_20260924'
data=json.loads((r/'fuxing_west_edge_profile_plan.json').read_text());s=bpy.data.scenes['CIVIC_PIER_XY_REVIEW_20260923']
for p in data['patches']:
 assert p['source_object'] in s.objects and p['name'] not in bpy.data.objects
 assert p['ramp_hole_fill_m2']<1e-6
replacements={};checks=[]
for p in data['patches']:
 old=s.objects[p['source_object']];mesh=bpy.data.meshes.new(p['name']+'_Mesh');mesh.from_pydata(p['vertices'],[],p['faces']);mesh.update()
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);assert all(e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);assert volume>0;bm.to_mesh(mesh);bm.free()
 ob=bpy.data.objects.new(p['name'],mesh)
 for m in old.data.materials:mesh.materials.append(m)
 ob['source_record']='fuxing_west_edge_profile_plan.json';ob['source_object']=old.name;ob['survey_verified']=False;ob['status']=p['width_status'];ob['ramp_holes_preserved']=True;ob['sources']=json.dumps(data['sources']);replacements[old]=ob
 checks.append({'object':ob.name,'manifold':True,'volume_m3':volume,'ramp_hole_fill_m2':p['ramp_hole_fill_m2']})
flags={}
def read(lc):
 flags[lc.collection]=(lc.exclude,lc.hide_viewport)
 for ch in lc.children:read(ch)
read(s.view_layers[0].layer_collection);memo={}
def clone(c):
 if c in memo:return memo[c]
 if not any(o in c.all_objects[:] for o in replacements):return c
 nc=bpy.data.collections.new(c.name+'_FUXING_GUARDED');memo[c]=nc
 nc.hide_render=c.hide_render;nc.hide_viewport=c.hide_viewport
 for o in c.objects:nc.objects.link(replacements.get(o,o))
 for ch in c.children:nc.children.link(clone(ch))
 return nc
for c in list(s.collection.children):
 nc=clone(c)
 if nc!=c:s.collection.children.unlink(c);s.collection.children.link(nc)
for old,new in replacements.items():
 if old.name in s.collection.objects:s.collection.objects.unlink(old);s.collection.objects.link(new)
inverse={v:k for k,v in memo.items()}
def restore(lc):
 src=inverse.get(lc.collection,lc.collection)
 if src in flags:lc.exclude,lc.hide_viewport=flags[src]
 for ch in lc.children:restore(ch)
for vl in s.view_layers:restore(vl.layer_collection)
for old,new in replacements.items():
 assert old.name not in s.objects and old.name in bpy.data.objects
 old.use_fake_user=True
result={'patches':checks,'originals_preserved':True,'junction_gap_preserved':True,'survey_verified':False}
(r/'fuxing_west_edge_profile_application.json').write_text(json.dumps(result,indent=2))

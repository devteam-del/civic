"""Install a connected deck-shell comparison; preserve original segments in source scene."""
import bpy,json,os,bmesh
root=os.path.join(os.path.dirname(bpy.data.filepath),'Underbridge_20260922')
s=bpy.data.scenes['CIVIC_SUPPORT_ALIGNMENT_EST_0922']
d=json.load(open(os.path.join(root,'continuous_deck_input.json')))
assert d['report']['nonmanifold_edges']==0
assert s.objects.get('DECK_CONTINUOUS_SHELL_EST_0922') is None
me=bpy.data.meshes.new('DECK_CONTINUOUS_SHELL_EST_0922');me.from_pydata(d['vertices'],[],d['faces']);me.update()
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
nonmanifold=sum(not e.is_manifold for e in bm.edges);zeroarea=sum(f.calc_area()<1e-10 for f in bm.faces)
assert nonmanifold==0 and zeroarea==0,(nonmanifold,zeroarea)
bm.to_mesh(me);bm.free()
ob=bpy.data.objects.new(me.name,me)
old={o for o in s.objects if o.type=='MESH' and o.name.startswith('DECK_')}
first=next(iter(old))
for mat in first.data.materials:me.materials.append(mat)
ob['basis']='Merged existing planar shells. Z=8m remains estimated; not calibrated ramp profile.'
ob['real_world_verified']=False;ob['xy_cleanup_tolerance_m']=.001
col=bpy.data.collections.new('CONTINUOUS_DECK_EST_COMPARISON');s.collection.children.link(col);col.objects.link(ob)
memo={}
def filtered(c):
 if c in memo:return memo[c]
 if not any(o in old for o in c.all_objects):return c
 nc=bpy.data.collections.new(c.name+'_DECK_JOIN');memo[c]=nc;nc.hide_render=c.hide_render;nc.hide_viewport=c.hide_viewport
 for o in c.objects:
  if o not in old:nc.objects.link(o)
 for ch in c.children:nc.children.link(filtered(ch))
 return nc
for c in list(s.collection.children):
 if c==col:continue
 nc=filtered(c)
 if nc!=c:s.collection.children.unlink(c);s.collection.children.link(nc)
for o in list(s.collection.objects):
 if o in old:s.collection.objects.unlink(o)
d['report'].update(blender_nonmanifold_edges=nonmanifold,blender_zeroarea_faces=zeroarea,xy_cleanup_tolerance_m=.001,source_scene_preserved=True,limitations='Bridge deck shell only. Girders, parapets and physical ramp elevations are not rebuilt by this union.')
json.dump(d['report'],open(os.path.join(root,'continuous_deck_comparison_report.json'),'w'),indent=2)
bpy.context.window.scene=s
def exclude(lc):
 if lc.collection.name in ['UB_UTURN_DISPUTED_SUPPORTS_ORIGINAL','UB_SPAN_HEIGHT_MODEL_AUDIT','UB_SPAN_HEIGHT_LABELS']:lc.exclude=True
 for ch in lc.children:exclude(ch)
for vl in s.view_layers:exclude(vl.layer_collection)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
result=d['report']

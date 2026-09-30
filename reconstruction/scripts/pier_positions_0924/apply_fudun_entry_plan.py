"""Apply provisional east-down entry XY and matching ground cuts, retaining originals."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(bpy.data.filepath).parent/'PierPositions_20260924'
s=bpy.context.scene;assert s.name=='CIVIC_PIER_XY_REVIEW_20260923'
d=json.loads((root/'fudun_entry_plan.json').read_text())
assert bpy.data.objects.get('SV_FUDUN_ENTRY_ROAD_EST') is None
repl={};checks=[]
for key,source,newname in [('road',d['source_road'],'SV_FUDUN_ENTRY_ROAD_EST'),('median',d['source_median'],'SV_FUDUN_ENTRY_MEDIAN_EST')]:
 old=s.objects[source];m=bpy.data.meshes.new(newname);m.from_pydata(d[key]['vertices'],[],d[key]['faces']);m.update()
 bm=bmesh.new();bm.from_mesh(m)
 bmesh.ops.dissolve_degenerate(bm,dist=.001,edges=list(bm.edges));bm.to_mesh(m);m.update()
 bad=sum(not e.is_manifold for e in bm.edges);zero=sum(f.calc_area()<1e-9 for f in bm.faces);bm.free()
 assert bad==0 and zero==0,(newname,bad,zero)
 new=bpy.data.objects.new(newname,m)
 for mat in old.data.materials:m.materials.append(mat)
 new['source_object']=old.name;new['source_record']='fudun_entry_plan.json';new['status']=d['status'];new['survey_verified']=False
 repl[old]=new;checks.append({'object':new.name,'nonmanifold':bad,'zero_area':zero})
a=d['old_top_xy'];b=d['new_top_xy']
M=Matrix.Translation(Vector((*b,0)))@Matrix.Rotation(d['rotation_rad'],4,'Z')@Matrix.Translation(Vector((-a[0],-a[1],0)))
for name in [d['source_ramp'],d['source_ramp']+'_WALL_-1',d['source_ramp']+'_WALL_1']:
 old=s.objects[name];new=old.copy();new.data=old.data.copy();new.name='SV_ENTRY_XY_'+name
 new.matrix_world=M@old.matrix_world
 same=[(new.matrix_world@v.co).z for v in new.data.vertices]==[(old.matrix_world@v.co).z for v in old.data.vertices]
 assert same
 new['source_object']=old.name;new['source_record']='fudun_entry_plan.json';new['survey_verified']=False
 new['status']='Estimated XY placement; east-down direction corroborated by public diagram and Street View; Z profile retained'
 repl[old]=new;checks.append({'object':new.name,'world_z_unchanged':same})
flags={}
def read(lc):
 flags[lc.collection]=(lc.exclude,lc.hide_viewport)
 for c in lc.children:read(c)
read(s.view_layers[0].layer_collection)
memo={}
def clone(c):
 if c in memo:return memo[c]
 if not any(o in c.all_objects[:] for o in repl):return c
 nc=bpy.data.collections.new(c.name+'_ENTRY_XY');memo[c]=nc;nc.hide_render=c.hide_render;nc.hide_viewport=c.hide_viewport
 for o in c.objects:nc.objects.link(repl.get(o,o))
 for ch in c.children:nc.children.link(clone(ch))
 return nc
for c in list(s.collection.children):
 nc=clone(c)
 if nc!=c:s.collection.children.unlink(c);s.collection.children.link(nc)
for old,new in repl.items():
 if old.name in s.collection.objects:s.collection.objects.unlink(old);s.collection.objects.link(new)
inverse={v:k for k,v in memo.items()}
def restore(lc):
 src=inverse.get(lc.collection,lc.collection)
 if src in flags:lc.exclude,lc.hide_viewport=flags[src]
 for c in lc.children:restore(c)
for vl in s.view_layers:restore(vl.layer_collection)
bpy.context.view_layer.update()
for old,new in repl.items():assert old.name not in s.objects and new.name in s.objects
report={'checks':checks,'replaced_only_in_working_scene':True,'remaining':'Ramp XY and road cuts provisional. Underground roof/floor connections and all heights remain unverified.'}
(root/'fudun_entry_application.json').write_text(json.dumps(report,indent=2))
result=report

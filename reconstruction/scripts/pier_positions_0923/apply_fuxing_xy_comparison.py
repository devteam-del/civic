"""Apply a Street View-derived XY comparison while preserving shaft Z and mesh."""
import bpy,json,os,math,hashlib
from mathutils import Vector
base=os.path.dirname(bpy.data.filepath);root=os.path.join(base,'PierPositions_20260923');os.makedirs(root,exist_ok=True)
d=json.load(open(os.path.join(root,'fuxing_642_position_review.json')))
source=bpy.data.scenes['CIVIC_FULL_CORRIDOR_PRESENTATION']
old=source.objects[d['model_pier_candidate']]
def center(o):
 pts=[o.matrix_world@Vector(v) for v in o.bound_box]
 return [sum(p[i] for p in pts)/8 for i in range(3)]
c=center(old);assert math.dist(c[:2],d['original_xy'])<.01
assert bpy.data.scenes.get('CIVIC_PIER_XY_REVIEW_20260923') is None
before_z=[float((old.matrix_world@v.co).z) for v in old.data.vertices]
ob=old.copy();ob.data=old.data.copy();ob.name='SV_XY_EST_Pier_642'
dx,dy=d['delta_xy'];ob.matrix_world.translation+=Vector((dx,dy,0))
ob['source_object']=old.name;ob['source_record']='fuxing_642_position_review.json';ob['status']='Street View bearing intersection estimate, correspondence provisional';ob['height_unchanged']=True;ob['survey_verified']=False
after_z=[float((ob.matrix_world@v.co).z) for v in ob.data.vertices]
assert before_z==after_z
scene=source.copy();scene.name='CIVIC_PIER_XY_REVIEW_20260923'
memo={}
def clone(c):
 if c in memo:return memo[c]
 if old not in c.all_objects[:]:return c
 nc=bpy.data.collections.new(c.name+'_XY_REVIEW');memo[c]=nc;nc.hide_render=c.hide_render;nc.hide_viewport=c.hide_viewport
 for o in c.objects:nc.objects.link(ob if o==old else o)
 for ch in c.children:nc.children.link(clone(ch))
 return nc
flags={}
def read_flags(lc): 
 flags[lc.collection]=(lc.exclude,lc.hide_viewport)
 for ch in lc.children:read_flags(ch)
read_flags(source.view_layers[0].layer_collection)
for col in list(scene.collection.children):
 nc=clone(col)
 if nc!=col:scene.collection.children.unlink(col);scene.collection.children.link(nc)
if old.name in scene.collection.objects:scene.collection.objects.unlink(old);scene.collection.objects.link(ob)
inverse={v:k for k,v in memo.items()}
def restore(lc):
 src=inverse.get(lc.collection,lc.collection)
 if src in flags:lc.exclude,lc.hide_viewport=flags[src]
 for ch in lc.children:restore(ch)
for vl in scene.view_layers:restore(vl.layer_collection)
col=bpy.data.collections.new('PIER_XY_REVIEW_EVIDENCE');scene.collection.children.link(col)
for name,xy,size in [('OLD_642_POSITION',d['original_xy'],1.),('SV_642_REVIEW_RING_NOT_CONFIDENCE',d['candidate_model_xy'],3.)]:
 e=bpy.data.objects.new(name,None);col.objects.link(e);e.location=(*xy,.25);e.empty_display_type='CIRCLE';e.empty_display_size=size;e.show_name=True;e.show_in_front=True
for i,v in enumerate(d['views']):
 me=bpy.data.curves.new('SV_BEARING_%d'%i,'CURVE');me.dimensions='3D';me.bevel_depth=.02
 sp=me.splines.new('POLY');sp.points.add(1)
 p=v['camera_xy'];u=v['direction'];L=v['forward_distance_m']
 sp.points[0].co=(*p,.3,1);sp.points[1].co=(p[0]+L*u[0],p[1]+L*u[1],.3,1)
 e=bpy.data.objects.new(me.name,me);col.objects.link(e);e.hide_render=True;e['pano']=v['pano'];e['date']=v['date'];e['heading']=v['heading'];e['use']='Historical crosscheck' if i==2 else '2025 bearing estimate'
d['application']={'scene':scene.name,'object':ob.name,'z_vertices_equal':before_z==after_z,'mesh_vertices_unchanged':all(a.co==b.co for a,b in zip(old.data.vertices,ob.data.vertices)),'column_height_m':max(after_z)-min(after_z),'cap_and_companion_unchanged':True,'scope':'One provisional XY correction only; no height or deck edits'}
json.dump(d,open(os.path.join(root,'fuxing_642_position_review.json'),'w'),ensure_ascii=False,indent=2)
txt=bpy.data.texts.new('PIER_XY_FUXING_642_REVIEW');txt.write(json.dumps(d,ensure_ascii=False,indent=2))
scene['workflow']='POSITION ONLY; column height and deck connections paused'
bpy.context.window.scene=scene
for q in bpy.context.selected_objects:q.select_set(False)
ob.select_set(True);bpy.context.view_layer.objects.active=ob
for a in bpy.context.screen.areas:
 if a.type=='VIEW_3D':
  v=a.spaces.active.region_3d;v.view_location=Vector((*d['candidate_model_xy'],2.4));v.view_distance=35;v.view_rotation=Vector((1,.1,-.15)).to_track_quat('-Z','Y')
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
result=d['application']

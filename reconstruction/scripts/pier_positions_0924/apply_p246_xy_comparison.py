"""Apply P246 XY comparison only; retain original scenes and shaft elevations."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
root=Path(bpy.data.filepath).parent/'PierPositions_20260924'
d=json.loads((root/'p246_position_review.json').read_text())
scene=bpy.context.scene
assert scene.name=='CIVIC_PIER_XY_REVIEW_20260923'
assert bpy.data.objects.get('SV_XY_EST_P246_MODEL730') is None
old=scene.objects[d['model_pier_candidate']]
pts=[old.matrix_world@Vector(v) for v in old.bound_box]
xy=[sum(p[i] for p in pts)/8 for i in range(2)]
assert math.dist(xy,d['original_xy'])<.01
z0=[(old.matrix_world@v.co).z for v in old.data.vertices]
ob=old.copy();ob.data=old.data.copy();ob.name='SV_XY_EST_P246_MODEL730'
ob.matrix_world.translation+=Vector((*d['delta_xy'],0))
ob['source_object']=old.name;ob['visible_pier_label']='P246'
ob['source_record']='p246_position_review.json'
ob['survey_verified']=False;ob['height_unchanged']=True
ob['status']='XY comparison; ground boundary conflict unresolved'
flags={}
def read_flags(lc):
 flags[lc.collection]=(lc.exclude,lc.hide_viewport)
 for ch in lc.children:read_flags(ch)
read_flags(scene.view_layers[0].layer_collection)
memo={}
def clone(c):
 if c in memo:return memo[c]
 if old not in c.all_objects[:]:return c
 nc=bpy.data.collections.new(c.name+'_P246_XY');memo[c]=nc
 nc.hide_render=c.hide_render;nc.hide_viewport=c.hide_viewport
 for o in c.objects:nc.objects.link(ob if o==old else o)
 for ch in c.children:nc.children.link(clone(ch))
 return nc
for c in list(scene.collection.children):
 nc=clone(c)
 if nc!=c:scene.collection.children.unlink(c);scene.collection.children.link(nc)
if old.name in scene.collection.objects:
 scene.collection.objects.unlink(old);scene.collection.objects.link(ob)
inverse={v:k for k,v in memo.items()}
def restore(lc):
 src=inverse.get(lc.collection,lc.collection)
 if src in flags:lc.exclude,lc.hide_viewport=flags[src]
 for ch in lc.children:restore(ch)
for vl in scene.view_layers:restore(vl.layer_collection)
assert old.name not in scene.objects
assert old.name in bpy.data.scenes['CIVIC_FULL_CORRIDOR_PRESENTATION'].objects
bpy.context.view_layer.update()
z1=[(ob.matrix_world@v.co).z for v in ob.data.vertices]
assert z0==z1
col=bpy.data.collections.new('P246_STREETVIEW_XY_EVIDENCE');scene.collection.children.link(col)
for name,p,size in [('P246_OLD_MODEL730',d['original_xy'],1.),('P246_XY_EST_NOT_SURVEY',d['candidate_model_xy'],1.)]:
 e=bpy.data.objects.new(name,None);col.objects.link(e);e.location=(*p,.25)
 e.empty_display_type='CIRCLE';e.empty_display_size=size;e.show_name=True;e.show_in_front=True
for i,v in enumerate(d['views']):
 curve=bpy.data.curves.new('P246_BEARING_'+str(i),'CURVE');curve.dimensions='3D';curve.bevel_depth=.02
 sp=curve.splines.new('POLY');sp.points.add(1)
 p=v['camera_xy'];u=v['direction'];L=v['forward_distance_m']
 sp.points[0].co=(*p,.3,1);sp.points[1].co=(p[0]+L*u[0],p[1]+L*u[1],.3,1)
 e=bpy.data.objects.new(curve.name,curve);col.objects.link(e);e.hide_render=True
 e['pano']=v['pano'];e['heading']=v['heading'];e['date']=v['date']
d['application']={'object':ob.name,'scene':scene.name,'all_world_vertex_z_unchanged':z0==z1,'original_preserved':True,'resolved':False}
(root/'p246_position_review.json').write_text(json.dumps(d,ensure_ascii=False,indent=2))
txt=bpy.data.texts.new('P246_XY_REVIEW');txt.write(json.dumps(d,ensure_ascii=False,indent=2))
result=d['application']

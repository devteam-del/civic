"""Render an isolated overhead QA scene without changing the user's active scene."""
import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).parent/'PierPositions_20260924';src=bpy.data.scenes['CIVIC_PIER_XY_REVIEW_20260923'];name='CIVIC_XY_GROUND_CHECKPOINT_20260929'
assert name not in bpy.data.scenes
s=bpy.data.scenes.new(name);snap=json.loads((r/'live_comparison_ground_footprints.json').read_text());names={x['name'] for key in ['roads','medians','piers'] for x in snap[key]};counts={}
for nm in names:
 o=src.objects.get(nm)
 if not o:continue
 vs=[o.matrix_world@Vector(v) for v in o.bound_box]
 if max(v.x for v in vs)<520 or min(v.x for v in vs)>1380:continue
 q=o.copy();q.name='QA_GROUND_'+o.name;s.collection.objects.link(q);q.hide_render=False;q.hide_viewport=False
 role='pier' if 'Pier_' in nm or nm.startswith(('SV_XY_EST','SV_ADDED_EST')) else 'median' if 'MEDIAN' in nm else 'road';q.color={'pier':(1,.22,.03,1),'median':(.65,.72,.58,1),'road':(.12,.16,.20,1)}[role];counts[role]=counts.get(role,0)+1
cam=bpy.data.cameras.new(name+'_CAM');ob=bpy.data.objects.new(name+'_CAM',cam);s.collection.objects.link(ob);ob.location=(950,775,500);ob.rotation_euler=(0,0,0);cam.type='ORTHO';cam.ortho_scale=900;cam.clip_end=2000;s.camera=ob
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='FLAT';s.display.shading.color_type='OBJECT';s.display.shading.show_shadows=False;s.display.shading.show_cavity=True;s.display.shading.background_type='WORLD';s.world=bpy.data.worlds.new(name+'_WORLD');s.world.color=(.035,.035,.035)
s.render.resolution_x=1920;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(r/'xy_ground_checkpoint_qa.png');bpy.ops.render.render(write_still=True,scene=s.name)
result={'scene':s.name,'counts':counts,'image':'xy_ground_checkpoint_qa.png','survey_verified':False};(r/'xy_ground_checkpoint_qa.json').write_text(json.dumps(result,indent=2))

"""Render focused, isolated comparison views while preserving the active scene."""
import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).parent/'PierPositions_20260924';src=bpy.data.scenes['CIVIC_STRUCTURE_CONNECTED_EST_20260929'];renders=[]
for label,camera,target in [('P233',(3292,350,5.5),(3263,383,8.8)),('STATION',(847,755,4),(824,782,6)),('P215',(2638,356,5),(2614,387,7))]:
 name='VC_QA_'+label+'_20260929';assert name not in bpy.data.scenes;s=bpy.data.scenes.new(name);count=0
 for o in src.objects:
  if o.type!='MESH' or o.hide_render:continue
  if not (o.name.startswith(('VC_EST_','CAL_GROUND_','SV_','BLOCK_CONTEXT_','UB_'))):continue
  pts=[o.matrix_world@Vector(v) for v in o.bound_box]
  if max(v.x for v in pts)<target[0]-130 or min(v.x for v in pts)>target[0]+130 or max(v.z for v in pts)<-.05:continue
  ob=o.copy();ob.name='QA_'+label+'_'+o.name;ob.hide_viewport=False;ob.hide_render=False;s.collection.objects.link(ob)
  if 'BEARING' in o.name:ob.color=(.075,.075,.075,1)
  elif 'MEDIAN' in o.name:ob.color=(.43,.49,.36,1)
  elif 'GROUND_ROAD' in o.name:ob.color=(.15,.17,.19,1)
  elif o.name.startswith('BLOCK_CONTEXT'):ob.color=(.6,.58,.53,1)
  else:ob.color=(.68,.68,.65,1)
  count+=1
 cam=bpy.data.cameras.new(name+'_CAM');ob=bpy.data.objects.new(name+'_CAM',cam);s.collection.objects.link(ob);ob.location=camera;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();cam.lens=24;cam.clip_end=220;s.camera=ob
 s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='OBJECT';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD';s.world=bpy.data.worlds.new(name+'_WORLD');s.world.color=(.12,.15,.19)
 s.render.resolution_x=1280;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(r/('connected_'+label.lower()+'_qa.png'));bpy.ops.render.render(write_still=True,scene=s.name);renders.append({'scene':s.name,'objects':count,'image':Path(s.render.filepath).name})
result={'renders':renders,'survey_verified':False};(r/'connected_structure_render_review.json').write_text(json.dumps(result,indent=2))

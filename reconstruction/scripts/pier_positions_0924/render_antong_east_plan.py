"""Render a limited plan QA scene; not a full-scene or real-world validation."""
import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(bpy.data.filepath).parent/'PierPositions_20260924'
scene=bpy.data.scenes.new('QA_ANTONG_EAST_XY_EST')
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'
scene.display.shading.color_type='OBJECT'
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
for obj in bpy.data.scenes['CIVIC_PIER_XY_REVIEW_20260923'].objects:
 if obj.type!='MESH':continue
 take=obj.name=='SV_FUXING_ROAD_EST' or obj.name.startswith('CAL_GROUND_MEDIAN_WORKING_ESTIMATED_') or (obj.name.startswith('SV_') and 'MEDIAN' in obj.name)
 if obj.name.startswith(('SV_XY_EST_','SV_ADDED_EST_')):
  x=sum((obj.matrix_world@Vector(v)).x for v in obj.bound_box)/8
  take=3210<x<3310
 if take:
  copy=obj.copy();copy.data=obj.data.copy();scene.collection.objects.link(copy)
  copy.hide_render=False;copy.hide_viewport=False
  copy.color=(1,.35,.06,1) if obj.name.startswith(('SV_XY_EST_','SV_ADDED_EST_')) else ((.24,.4,.23,1) if 'MEDIAN' in obj.name else (.18,.2,.22,1))
data=bpy.data.cameras.new('QA_RAMP_EAST_XY_PLAN')
camera=bpy.data.objects.new(data.name,data);scene.collection.objects.link(camera)
camera.location=(3260,385,120);camera.rotation_euler=(0,0,0)
data.type='ORTHO';data.ortho_scale=110;scene.camera=camera
scene.render.resolution_x=1800;scene.render.resolution_y=750;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(root/'antong_east_xy_est_plan.png')
scene['status']='Proportional curb and opening comparison; dimensions not measured.'
bpy.ops.render.render(write_still=True,scene=scene.name)
result={'render':scene.render.filepath}

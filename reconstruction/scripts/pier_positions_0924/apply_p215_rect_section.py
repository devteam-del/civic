"""Use the observed rectangular lower section, retaining estimated XY and all heights."""
import bpy,json,math,bmesh
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).parent/'PierPositions_20260924'
d=json.loads((r/'p215_section_review.json').read_text())
scene=bpy.data.scenes['CIVIC_PIER_XY_REVIEW_20260923']
o=scene.objects['SV_XY_EST_JIANGUO_WEST_EDGE_SOUTH_MODEL107']
assert not o.get('rect_section_applied')
world=[o.matrix_world@v.co for v in o.data.vertices]
xy=[(min(v[i] for v in world)+max(v[i] for v in world))/2 for i in range(2)]
z0=min(v.z for v in world);z1=max(v.z for v in world)
old=o.data;old.use_fake_user=True
width=d['width_m'];depth=d['depth_estimate_m'];angle=d['rotation_z_rad']
inverse=o.matrix_world.inverted();vertices=[]
for z in [z0,z1]:
 for x,y in [(-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(-width/2,depth/2)]:
  vertices.append(inverse@Vector((xy[0]+math.cos(angle)*x-math.sin(angle)*y,xy[1]+math.sin(angle)*x+math.cos(angle)*y,z)))
mesh=bpy.data.meshes.new(o.name+'_RECT_SECTION')
mesh.from_pydata(vertices,[],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);mesh.update()
for mat in old.materials:mesh.materials.append(mat)
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);assert all(e.is_manifold for e in bm.edges);bm.to_mesh(mesh);bm.free()
o.data=mesh
o['rect_section_applied']=True;o['section_source']='p215_section_review.json';o['section_status']='Estimated 2.51x1.97m rectangular shaft; head flare pending'
o['previous_mesh_backup']=old.name;o['survey_verified']=False
updated=[o.matrix_world@v.co for v in mesh.vertices]
assert abs(min(v.z for v in updated)-z0)<1e-5 and abs(max(v.z for v in updated)-z1)<1e-5
assert bpy.data.objects['UNVERIFIED_Pier_107'].data!=mesh
result={'object':o.name,'section_width_m':width,'section_depth_m':depth,'xy_preserved':xy,'z_range_preserved':[z0,z1],'original_proxy_mesh_preserved':old.name,'section_center_difference_m':math.dist(xy,d['center_model_xy']),'decision':'Retain prior triangulated XY. Section-derived center differs within uncertainty; no additional XY shift.','survey_verified':False,'head_flare_pending':True}
(r/'p215_section_application.json').write_text(json.dumps(result,indent=2))

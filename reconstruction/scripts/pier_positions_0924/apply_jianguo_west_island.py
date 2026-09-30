"""Add one estimated southern island without changing original ground or pier XY."""
import bpy,json,math,bmesh
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
root=Path(bpy.data.filepath).parent/'PierPositions_20260924'
d=json.loads((root/'jianguo_west_island_plan.json').read_text())
s=bpy.data.scenes['CIVIC_PIER_XY_REVIEW_20260923']
assert d['name'] not in bpy.data.objects
ring=d['footprint']['coordinates'][0][:-1]
n=len(ring);bottom=d['z_min'];top=d['z_max']
v=[Vector((x,y,top)) for x,y in ring]
lookup={(round(p.x,6),round(p.y,6)):i for i,p in enumerate(v)}
tri=tessellate_polygon([v]);faces=[]
for t in tri:
 ids=[p if isinstance(p,int) else lookup[(round(p.x,6),round(p.y,6))] for p in t]
 faces.append(tuple(i+n for i in ids));faces.append(tuple(reversed(ids)))
for i in range(n):j=(i+1)%n;faces.append((i,j,j+n,i+n))
verts=[(x,y,z) for z in [bottom,top] for x,y in ring]
mesh=bpy.data.meshes.new(d['name']+'_Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);bm.to_mesh(mesh);bm.free()
ob=bpy.data.objects.new(d['name'],mesh)
col=bpy.data.collections.get('SV_GROUND_LOCAL_COMPARISONS')
if col is None:col=bpy.data.collections.new('SV_GROUND_LOCAL_COMPARISONS');s.collection.children.link(col)
col.objects.link(ob)
for k,val in d.items():
 if k not in ['footprint','sources','source_piers']:ob[k]=val
ob['sources']=json.dumps(d['sources']);ob['source_record']='jianguo_west_island_plan.json'
ob['survey_verified']=False
mat=bpy.data.materials.get('SV_MEDIAN_ESTIMATE') or bpy.data.materials.new('SV_MEDIAN_ESTIMATE')
mat.diffuse_color=(0.28,0.34,0.19,1);ob.data.materials.append(mat)
assert ob.name in s.objects and ob.name not in bpy.data.scenes['CIVIC_FULL_CORRIDOR_PRESENTATION'].objects
result={'object':ob.name,'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'width_estimate_m':d['estimated_width_m'],'originals_preserved':True,'height_or_pier_xy_changed':False}

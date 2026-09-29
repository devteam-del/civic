"""Cut the observed U-turn in a comparison-only copy of median 8."""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
r=Path(bpy.data.filepath).parent/'PierPositions_20260924'
d=json.loads((r/'huaisheng_opening_plan.json').read_text())
s=bpy.data.scenes['CIVIC_PIER_XY_REVIEW_20260923'];old=s.objects[d['source_object']]
assert d['name'] not in bpy.data.objects
verts=[];faces=[]
for polygon in d['footprint']['coordinates']:
 assert len(polygon)==1
 ring=polygon[0][:-1];n=len(ring);offset=len(verts);v=[Vector((x,y,d['z_max'])) for x,y in ring]
 lookup={(round(p.x,6),round(p.y,6)):i for i,p in enumerate(v)}
 for t in tessellate_polygon([v]):
  ids=[p if isinstance(p,int) else lookup[(round(p.x,6),round(p.y,6))] for p in t]
  faces+=[tuple(offset+i for i in reversed(ids)),tuple(offset+n+i for i in ids)]
 for i in range(n):j=(i+1)%n;faces.append((offset+i,offset+j,offset+j+n,offset+i+n))
 verts.extend([(x,y,z) for z in [d['z_min'],d['z_max']] for x,y in ring])
mesh=bpy.data.meshes.new(d['name']+'_Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);assert all(e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);assert volume>0;bm.to_mesh(mesh);bm.free()
ob=bpy.data.objects.new(d['name'],mesh)
for m in old.data.materials:mesh.materials.append(m)
ob['source_record']='huaisheng_opening_plan.json';ob['source_object']=old.name
ob['survey_verified']=False;ob['status']=d['dimension_status'];ob['sources']=json.dumps(d['sources'])
flags={}
def read(lc):
 flags[lc.collection]=(lc.exclude,lc.hide_viewport)
 for ch in lc.children:read(ch)
read(s.view_layers[0].layer_collection);memo={}
def clone(c):
 if c in memo:return memo[c]
 if old not in c.all_objects[:]:return c
 nc=bpy.data.collections.new(c.name+'_HUAISHENG_OPENING');memo[c]=nc
 nc.hide_render=c.hide_render;nc.hide_viewport=c.hide_viewport
 for o in c.objects:nc.objects.link(ob if o==old else o)
 for ch in c.children:nc.children.link(clone(ch))
 return nc
for c in list(s.collection.children):
 nc=clone(c)
 if nc!=c:s.collection.children.unlink(c);s.collection.children.link(nc)
if old.name in s.collection.objects:s.collection.objects.unlink(old);s.collection.objects.link(ob)
inverse={v:k for k,v in memo.items()}
def restore(lc):
 src=inverse.get(lc.collection,lc.collection)
 if src in flags:lc.exclude,lc.hide_viewport=flags[src]
 for ch in lc.children:restore(ch)
for vl in s.view_layers:restore(vl.layer_collection)
assert old.name not in s.objects and ob.name in s.objects
assert old.name in bpy.data.scenes['CIVIC_FULL_CORRIDOR_PRESENTATION'].objects
result={'object':ob.name,'manifold':True,'volume_m3':volume,'estimated_removed_area_m2':d['removed_area_m2'],'original_preserved':True,'field_verified':False}
(r/'huaisheng_opening_application.json').write_text(json.dumps(result,indent=2))

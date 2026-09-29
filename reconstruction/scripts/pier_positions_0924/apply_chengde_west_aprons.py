"""Apply estimated split islands in the comparison scene, preserving original scenes."""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
r=Path(bpy.data.filepath).parent/'PierPositions_20260924'
data=json.loads((r/'chengde_west_aprons_plan.json').read_text())
s=bpy.data.scenes['CIVIC_PIER_XY_REVIEW_20260923']
col=bpy.data.collections['SV_GROUND_LOCAL_COMPARISONS']
for d in data['patches']:
 assert d['name'] not in bpy.data.objects
 assert d['footprint']['type']=='Polygon' and len(d['footprint']['coordinates'])==1
assert col.name in s.collection.children
checks=[]
for d in data['patches']:
 ring=d['footprint']['coordinates'][0][:-1];n=len(ring)
 vs=[Vector((x,y,d['z_max'])) for x,y in ring]
 lookup={(round(v.x,6),round(v.y,6)):i for i,v in enumerate(vs)}
 faces=[]
 for t in tessellate_polygon([vs]):
  ids=[p if isinstance(p,int) else lookup[(round(p.x,6),round(p.y,6))] for p in t]
  faces+=[tuple(reversed(ids)),tuple(i+n for i in ids)]
 for i in range(n):j=(i+1)%n;faces.append((i,j,j+n,i+n))
 mesh=bpy.data.meshes.new(d['name']+'_Mesh')
 mesh.from_pydata([(x,y,z) for z in [d['z_min'],d['z_max']] for x,y in ring],[],faces)
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);assert all(e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);assert vol>0;bm.to_mesh(mesh);bm.free()
 ob=bpy.data.objects.new(d['name'],mesh);col.objects.link(ob)
 mesh.materials.append(bpy.data.materials['SV_MEDIAN_ESTIMATE'])
 for k,v in d.items():
  if k not in ['footprint','source_piers','source_records']:ob[k]=v
 ob['source_record']='chengde_west_aprons_plan.json';ob['sources']=json.dumps(data['sources']);ob['survey_verified']=False
 checks.append({'object':ob.name,'volume_m3':vol,'manifold':True,'estimated_width_m':d['estimated_width_m']})

result={'patches':checks,'central_entry_zone_untouched':True,'field_verified':False}
(r/'chengde_west_aprons_application.json').write_text(json.dumps(result,indent=2))

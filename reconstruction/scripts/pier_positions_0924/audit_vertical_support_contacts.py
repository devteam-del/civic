"""Read actual comparison meshes and sample deck/girder underside above each shaft."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(bpy.data.filepath).parent/'PierPositions_20260924';s=bpy.data.scenes['CIVIC_PIER_XY_REVIEW_20260923'];snap=json.loads((r/'live_comparison_ground_footprints.json').read_text());cache=[]
for o in s.objects:
 if o.type!='MESH' or not o.name.startswith(('DECK_','GIRDER_')):continue
 vs=[o.matrix_world@v.co for v in o.data.vertices];lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)];tree=BVHTree.FromPolygons(vs,[list(p.vertices) for p in o.data.polygons]);cache.append((o.name,lo,hi,tree))
rows=[]
for p in snap['piers']:
 o=s.objects[p['name']];vs=[o.matrix_world@v.co for v in o.data.vertices];lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)];x,y=[(lo[i]+hi[i])/2 for i in [0,1]];hits=[]
 for name,a,b,tr in cache:
  if a[0]-.01<=x<=b[0]+.01 and a[1]-.01<=y<=b[1]+.01:
   h=tr.ray_cast(Vector((x,y,max(hi[2],.5))),Vector((0,0,1)),50)
   if h[0] is not None:hits.append({'object':name,'z':h[0].z})
 hits.sort(key=lambda h:h['z']);rows.append({'name':o.name,'xy':[x,y],'shaft_z':[lo[2],hi[2]],'overhead':hits,'nearest_gap_m':hits[0]['z']-hi[2] if hits else None})
out={'scene':s.name,'basis':'Current unevaluated model meshes, geometric contact audit only. Heights not surveyed.','rows':rows,'summary':{'shafts':len(rows),'without_overhead_at_centre':sum(not x['overhead'] for x in rows),'with_overhead_at_centre':sum(bool(x['overhead']) for x in rows)}};(r/'vertical_support_contact_audit.json').write_text(json.dumps(out,indent=2));result=out['summary']

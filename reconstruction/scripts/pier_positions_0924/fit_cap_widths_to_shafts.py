"""Ensure estimated caps cover the full shaft section while retaining bearing contacts."""
import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).parent/'PierPositions_20260924';s=bpy.data.scenes['CIVIC_STRUCTURE_CONNECTED_EST_20260929'];d=json.loads((r/'connected_structure_application.json').read_text());changes=[]
for b in d['bents']:
 cap=s.objects[b['cap']];vs=[cap.matrix_world@v.co for v in cap.data.vertices];c=sum(vs,Vector())/len(vs);axis=(vs[1]-vs[0]).normalized();across=Vector((-axis.y,axis.x,0));oldhalf=max(abs((v-c).dot(across)) for v in vs);need=max(abs((s.objects[m['new']].matrix_world@v.co-c).dot(across)) for m in b['members'] for v in s.objects[m['new']].data.vertices)+.2
 if need>oldhalf+.001:
  inv=cap.matrix_world.inverted()
  for v in cap.data.vertices:
   p=cap.matrix_world@v.co;q=(p-c).dot(across);p+=across*q*(need/oldhalf-1);v.co=inv@p
  cap.data.update();changes.append({'cap':cap.name,'old_width_m':2*oldhalf,'new_width_m':2*need});b['cap_longitudinal_width_m']=2*need
(r/'connected_structure_application.json').write_text(json.dumps(d,indent=2));result={'changes':changes,'bearing_heights_unchanged':True};(r/'cap_width_fit_review.json').write_text(json.dumps(result,indent=2))

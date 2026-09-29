"""Export the comparison scene's actual ground meshes for collision auditing.
Local geometry snapshot only; do not upload the generated JSON to GitHub.
"""
import bpy,json,hashlib
from pathlib import Path
scene=bpy.data.scenes['CIVIC_PIER_XY_REVIEW_20260923']
root=Path(bpy.data.filepath).parent/'PierPositions_20260924'
def export(obj):
    vertices=[obj.matrix_world@v.co for v in obj.data.vertices]
    faces=[]
    for face in obj.data.polygons:
        points=[[vertices[i].x,vertices[i].y] for i in face.vertices]
        area=abs(sum(points[i][0]*points[(i+1)%len(points)][1]-points[(i+1)%len(points)][0]*points[i][1] for i in range(len(points)))/2)
        if area>1e-9: faces.append(points)
    return {'name':obj.name,'faces':faces}
roads=[o for o in scene.objects if o.type=='MESH' and (o.name.startswith('CAL_GROUND_ROADS_OFFICIAL_XY_') or o.name=='SV_FUXING_ROAD_EST')]
medians=[o for o in scene.objects if o.type=='MESH' and (o.name.startswith('CAL_GROUND_MEDIAN_WORKING_ESTIMATED_') or o.name.startswith('SV_') and 'MEDIAN' in o.name)]
assert len(roads)>0 and len(medians)>0
pier_names={o.name for o in scene.objects if o.type=='MESH' and o.name.startswith('UNVERIFIED_Pier_')}
for folder in [root,root.parent/'PierPositions_20260923']:
 for path in folder.glob('*position_review.json'):
  rec=json.loads(path.read_text())
  for item in rec.get('targets',[rec]):
   if not item.get('comparison_object'):item['comparison_object']=item.get('application',{}).get('object')
   if item.get('comparison_object') and item['comparison_object'] in scene.objects:pier_names.add(item['comparison_object'])
 for path in folder.glob('*missing*review.json'):
  for item in json.loads(path.read_text()).get('targets',[]):
   if item.get('comparison_object') and item['comparison_object'] in scene.objects:pier_names.add(item['comparison_object'])
payload={'scene':scene.name,'roads':[export(o) for o in roads],'medians':[export(o) for o in medians],'piers':[export(scene.objects[name]) for name in sorted(pier_names)]}

text=json.dumps(payload,sort_keys=True)
(root/'live_comparison_ground_footprints.json').write_text(text)
manifest={'scene':scene.name,'sha256':hashlib.sha256(text.encode()).hexdigest(),'road_objects':len(roads),'median_objects':len(medians),'road_names':sorted(o.name for o in roads),'median_names':sorted(o.name for o in medians),'scope':'Model footprint audit, not surveyed traffic-lane boundaries; raw geometry retained locally.'}
(root/'live_comparison_ground_manifest.json').write_text(json.dumps(manifest,indent=2))
result={k:v for k,v in manifest.items() if not k.endswith('_names')}

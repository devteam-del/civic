import json,sys
from pathlib import Path
from shapely.geometry import Polygon,shape,mapping
from shapely.ops import unary_union
root=Path(sys.argv[1]); src=Path(sys.argv[2]); live=json.loads((root/'live_comparison_ground_footprints.json').read_text());d=json.loads((src/'Calibration/openings_payload.json').read_text());rel=json.loads((src/'CalibrationRound3/gongzhong_integrated_openings_payload.json').read_text()); guards=[]
for o in d['openings']:
 if o['id']=='CORE_公中_0':continue
 guards.append({'id':o['id'],'geometry':o['geometry'],'status':o['status']})
guards.append({'id':'CORE_公中_RELOCATED','geometry':mapping(Polygon(rel['new_hole_xy'])),'status':rel['status']})
g=unary_union([shape(o['geometry']) for o in guards]);rows=[]
for o in live['medians']:
 p=unary_union([Polygon(f).buffer(0) for f in o['faces']]); hits=[{'id':x['id'],'area_m2':p.intersection(shape(x['geometry'])).area} for x in guards if p.intersection(shape(x['geometry'])).area>0.01]
 if hits:rows.append({'object':o['name'],'hits':hits})
Path('/tmp/opening_guard_inventory.json').write_text(json.dumps({'guards':guards,'status':'Existing model opening locations retained; not survey verified.'},indent=2));print(json.dumps(rows,ensure_ascii=False))

"""Restore an observed underbridge U-turn opening with provisional dimensions."""
import json,sys,math
from pathlib import Path
from shapely.geometry import Polygon,box,mapping
from shapely.ops import unary_union
from shapely import affinity
root=Path(sys.argv[1]);out=Path(sys.argv[2]);d=json.loads((root/'live_comparison_ground_footprints.json').read_text())
o=next(x for x in d['medians'] if x['name']=='CAL_GROUND_MEDIAN_WORKING_ESTIMATED_8')
p=unary_union([Polygon(f).buffer(0) for f in o['faces']]);cut=affinity.rotate(box(3102,340,3116,395),3,origin=(3109,367));new=p.difference(cut)
assert new.is_valid and new.geom_type=='MultiPolygon' and len(new.geoms)==2
record={'source_object':o['name'],'name':'SV_HUAISHENG_UTURN_MEDIAN_EST','footprint':mapping(new),'cut_footprint':mapping(cut),'z_min':0.0,'z_max':0.18,'estimated_cut_length_m':14,'estimated_rotation_deg':3,'removed_area_m2':p.area-new.area,'sources':['https://www.google.com/maps/@?api=1&map_action=pano&pano=D93ruj14fi2oZZ0vJUEfBw&heading=60&pitch=0&fov=90','https://www.google.com/maps/@?api=1&map_action=pano&pano=eV_i_SzovWajM8hzjh1XTw&heading=220&pitch=0&fov=90'],'source_dates':['2024-12','2025-02'],'existence_status':'Both ground panoramas visibly show a full-width paved underbridge U-turn between the footbridge pair and next eastern pair.','dimension_status':'14m cut and local endpoints are provisional proportional estimates. Rounded noses are not metrically reconstructed.','survey_verified':False,'pier_positions_changed':False}
out.write_text(json.dumps(record,indent=2));print(json.dumps({'removed_area':record['removed_area_m2'],'parts':len(new.geoms),'bounds':[list(g.bounds) for g in new.geoms]}))

"""Estimated curb envelope for a visually observed southern pier island.
Width remains an explicit modelling assumption, not a measured road edge.
"""
import json,math,sys
from pathlib import Path
from shapely.geometry import LineString,mapping
root=Path(sys.argv[1]);out=Path(sys.argv[2])
def target(file,side):return next(t for t in json.loads((root/file).read_text())['targets'] if t['id'].endswith(side))
a=target('p214_position_review.json','SOUTH');b=target('jianguo_west_edge_position_review.json','SOUTH')
p=a['candidate_model_xy'];q=b['candidate_model_xy'];v=[q[i]-p[i] for i in range(2)];length=math.hypot(*v);u=[x/length for x in v]
# Island end is approximately x=2620 from two ground views. The observed
# curved silhouette is viewpoint dependent, so keep an explicit 1.5m end uncertainty.
radius=1.8;end_x=2619.912066345265;end=[q[i]+u[i]*((end_x-radius-q[0])/u[0]) for i in range(2)]
poly=LineString([p,q,end]).buffer(radius,quad_segs=12)
d={'name':'SV_JIANGUO_WEST_SOUTH_MEDIAN_EST','footprint':mapping(poly),'z_min':0.0,'z_max':0.18,'source_piers':[a['comparison_object'],b['comparison_object']],'evidence':'2025-04 views show southern shafts in a continuous planted/gravel island, with a separate carriageway between north and south shafts.','sources':['https://www.google.com/maps/@?api=1&map_action=pano&pano=3Vq9E0LHU4N9sIW2U3PM2A&heading=300&pitch=0&fov=90','https://www.google.com/maps/@?api=1&map_action=pano&pano=_5Ebb39w9DkSUk1Fe2o1Jw&heading=60&pitch=0&fov=90'],'estimated_width_m':radius*2,'end_x_estimate_m':end_x,'end_uncertainty_assumed_m':1.5,'western_extent_status':'Partial patch ends at P214; continuation west remains pending.','calibration_status':'Street View existence; width, height, rounded endpoints estimated. Not surveyed.','survey_verified':False,'road_between_pier_rows_preserved':True}
out.write_text(json.dumps(d,indent=2));print(json.dumps({'bounds':poly.bounds,'area':poly.area,'west':p,'east':end}))

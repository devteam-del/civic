import json,sys
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import make_valid,affinity
d=json.load(open(sys.argv[1]));t=json.load(open(sys.argv[2]))
def geo(o):return unary_union([make_valid(Polygon(f)) for f in o['faces'] if len(f)>=3])
p=geo(next(o for o in d['piers'] if o['name']=='UNVERIFIED_Pier_642'));road=unary_union([geo(o) for o in d['roads']]);median=unary_union([geo(o) for o in d['medians']])
x,y=p.centroid.coords[0];dx,dy=t['candidate_model_xy'][0]-x,t['candidate_model_xy'][1]-y;new=affinity.translate(p,dx,dy)
t['model_pier_candidate']='UNVERIFIED_Pier_642';t['original_xy']=[x,y];t['delta_xy']=[dx,dy];t['association_status']='Provisional matching to nearest old roadside shaft; companion column and cap not relocated'
t['model_footprint_check']={'old_road_outside_median_m2':p.intersection(road).difference(median).area,'new_road_outside_median_m2':new.intersection(road).difference(median).area,'new_outside_median_m2':new.difference(median).area}
json.dump(t,open(sys.argv[3],'w'),indent=2);print(json.dumps(t['model_footprint_check']))

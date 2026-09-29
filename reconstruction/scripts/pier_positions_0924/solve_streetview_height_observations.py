"""Estimate visible vertical shaft length from pixel rays and provisional XY range.
This is photogrammetric working geometry, not surveyed elevation. Pixel endpoints,
panorama orientation, camera GPS and shaft-front radius all carry uncertainty.
"""
import json,math,sys
from pathlib import Path
records=json.loads(Path(sys.argv[1]).read_text());root=Path(sys.argv[2]);out=Path(sys.argv[3])
def slope(px,py,pitch):
 f=360.;p=math.radians(pitch);u=px-640;v=360-py
 forward=f*math.cos(p)-v*math.sin(p);z=f*math.sin(p)+v*math.cos(p)
 return z/math.hypot(u,forward)
for a in records['anchors']:
 t=next(t for t in json.loads((root/a['record']).read_text())['targets'] if t['id']==a['target']);a['xy']=t['candidate_model_xy'];vals=[]
 for v in a['views']:
  cam=next(x['camera_xy'] for x in t['views'] if x['pano']==v['pano']);d=math.dist(a['xy'],cam);front=d-v.get('front_radius_est_m',1.0);delta=slope(*v['top_px'],v['pitch'])-slope(*v['base_px'],v['pitch']);v['range_to_axis_m']=d;v['range_to_visible_front_est_m']=front;v['shaft_height_est_m']=front*delta;v['axis_range_height_upper_variant_m']=d*delta;vals.append(front*delta)
 a['mean_height_est_m']=sum(vals)/len(vals);a['view_spread_m']=max(vals)-min(vals);a['survey_verified']=False
out.write_text(json.dumps(records,indent=2));print(json.dumps([{k:a[k] for k in ['target','mean_height_est_m','view_spread_m']} for a in records['anchors']]))

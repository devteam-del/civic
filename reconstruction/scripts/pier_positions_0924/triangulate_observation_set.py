"""Triangulate explicitly observed Street View bearings; never infer unobserved bearings."""
import json,math,sys,itertools
from pyproj import Transformer,Geod
T=Transformer.from_crs(4326,3826,always_xy=True);G=Geod(ellps='WGS84')
ROT=math.radians(-7.824973748058551e-05);SCALE=.9999980676451855
def model(lon,lat):
 x,y=T.transform(lon,lat);x-=301495.60874932667;y-=2770459.509396812
 return [(math.cos(ROT)*x+math.sin(ROT)*y)/SCALE,(-math.sin(ROT)*x+math.cos(ROT)*y)/SCALE]
def ray(v,delta=0):
 p=model(v['lon'],v['lat']);lon,lat,_=G.fwd(v['lon'],v['lat'],v['heading']+delta,100);q=model(lon,lat)
 z=math.dist(p,q);return p,[(q[i]-p[i])/z for i in range(2)]
def cross(a,b):return a[0]*b[1]-a[1]*b[0]
def intersection(v,w,da=0,db=0):
 p,u=ray(v,da);q,z=ray(w,db);det=cross(u,z)
 if abs(det)<1e-8:raise ValueError('Parallel rays')
 f=cross([q[i]-p[i] for i in range(2)],z)/det
 return [p[i]+f*u[i] for i in range(2)]
data=json.load(open(sys.argv[1]));out=[]
for rec in data['targets']:
 views=rec['views'];p=intersection(*views[:2]);u=ray(views[0])[1];v=ray(views[1])[1]
 angle=math.degrees(math.acos(min(1,max(-1,sum(a*b for a,b in zip(u,v))))));angle=min(angle,180-angle)
 rec['candidate_model_xy']=p;rec['intersection_angle_deg']=angle
 for view in views:
  q,u=ray(view);d=[p[i]-q[i] for i in range(2)]
  view.update(camera_xy=q,direction=u,forward_distance_m=sum(d[i]*u[i] for i in range(2)),perpendicular_ray_residual_m=abs(cross(d,u)))
 rec['geometry_condition']='review_needed' if angle<10 or any(v['forward_distance_m']<=0 for v in views[:2]) else 'usable_for_provisional_comparison'
 rec['angular_sensitivity_only_m']=max(math.dist(p,intersection(*views[:2],a,b)) for a,b in itertools.product([-1,1],repeat=2))
 rec['uncertainty']='Angular sensitivity is NOT a confidence interval. Camera GPS, panorama heading, absolute model registration and target matching errors remain unquantified.'
 rec['real_world_verified']=False;rec['height_changed']=False;out.append(rec)
json.dump({'targets':out,'method':'Two primary geodesic bearings projected to model XY, with extra views as ray crosschecks'},open(sys.argv[2],'w'),indent=2)
print(json.dumps([{'id':r['id'],'xy':r['candidate_model_xy'],'angle':r['intersection_angle_deg'],'condition':r['geometry_condition']} for r in out]))

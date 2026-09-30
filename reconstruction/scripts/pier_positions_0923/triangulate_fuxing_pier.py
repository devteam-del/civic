import math,json,sys
from pyproj import Transformer,Geod
views=[{'pano':'GNaYshgbXGqT6PZXF7RvSw','lat':25.0446044,'lon':121.5427628,'heading':67.7,'date':'2025-04'}, {'pano':'4NKKDkj7LTh70nLelXcPqw','lat':25.044701,'lon':121.5436636,'heading':279.2,'date':'2025-01'}, {'pano':'2OrSAImf04uhBzzFvkc8jg','lat':25.0446163,'lon':121.5428768,'heading':59.8,'date':'2020-10','role':'historical_crosscheck_only'}]
t=Transformer.from_crs(4326,3826,always_xy=True);geod=Geod(ellps='WGS84')
theta=math.radians(-7.824973748058551e-05);scale=.9999980676451855
def model(lon,lat):
 x,y=t.transform(lon,lat);x-=301495.60874932667;y-=2770459.509396812
 return [(math.cos(theta)*x+math.sin(theta)*y)/scale,(-math.sin(theta)*x+math.cos(theta)*y)/scale]
for v in views:
 v['camera_xy']=model(v['lon'],v['lat']);lon,lat,_=geod.fwd(v['lon'],v['lat'],v['heading'],100);p=model(lon,lat);dx,dy=p[0]-v['camera_xy'][0],p[1]-v['camera_xy'][1];l=math.hypot(dx,dy);v['direction']=[dx/l,dy/l]
def intersection(a,b):
 p,q=a['camera_xy'],b['camera_xy'];u,v=a['direction'],b['direction'];dx,dy=q[0]-p[0],q[1]-p[1];det=u[0]*v[1]-u[1]*v[0];s=(dx*v[1]-dy*v[0])/det
 return [p[0]+s*u[0],p[1]+s*u[1]]
p=intersection(*views[:2])
for v in views:
 dx,dy=p[0]-v['camera_xy'][0],p[1]-v['camera_xy'][1];u=v['direction'];v['perpendicular_ray_residual_m']=abs(dx*u[1]-dy*u[0]);v['forward_distance_m']=dx*u[0]+dy*u[1]
out={'target':'Roadside cylindrical pier west of visible P236, beside service-house west end','candidate_model_xy':p,'views':views,'method':'Intersection of two visually centered 2025 Street View bearings; geodesic heading projected to EPSG3826 then established model transform. Historical third view is a crosscheck only.','uncertainty':'Not surveyed. Camera geolocation, panorama heading, target matching and visual centering errors remain unquantified. A 3m display ring is a review guide, not a statistical confidence interval.','real_world_verified':False,'height_changed':False}
json.dump(out,open(sys.argv[1],'w'),indent=2);print(json.dumps(out))

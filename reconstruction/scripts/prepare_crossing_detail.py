"""Mapped crossing nodes -> estimated marking geometry and candidate curb ramps.
Only nodes within 2m of the main ground route are used; inference is explicit.
"""
import json,pathlib,argparse,math,re
from shapely.geometry import Polygon,LineString,Point
from shapely.ops import unary_union,transform,nearest_points
from shapely import constrained_delaunay_triangles
from pyproj import Transformer
p=argparse.ArgumentParser()
for n in ['ground','crossings','routes','registration','out']:p.add_argument('--'+n,required=True)
a=p.parse_args();d=json.load(open(a.ground));reg=json.load(open(a.registration));tr=Transformer.from_crs(4326,3826,always_xy=True);f=reg['live_to_twd97'];ang=math.radians(f['rotation_degrees']);org=[reg['origin_epsg3826'][i]+f['translation'][i] for i in (0,1)]
def loc(q):
 x,y=q[0]-org[0],q[1]-org[1];return ((math.cos(ang)*x+math.sin(ang)*y)/f['scale'],(-math.sin(ang)*x+math.cos(ang)*y)/f['scale'])
def surface(name,z):
 m=d['meshes'][name];vs=m['vertices'];return unary_union([Polygon([(vs[i][0],vs[i][1]) for i in face]) for face in m['faces'] if len(face)==3 and all(abs(vs[i][2]-z)<1e-7 for i in face)])
road=unary_union([surface('GROUND_ROADS_OFFICIAL_XY',0),surface('GROUND_ROADS_ESTIMATED_GAPS',0)]);walk=surface('GROUND_SIDEWALKS_OFFICIAL_XY',.15)
routes=[]
for ft in json.load(open(a.routes))['features']:
 t=ft['properties']
 if re.fullmatch('市民大道[一二三四五六七八]段',t.get('name','')) and t.get('bridge')!='yes':routes.append((t,LineString([loc(tr.transform(*q)) for q in ft['geometry']['coordinates']])))
def rectangle(c,v,n,along,cross):
 return Polygon([(c[0]+sv*v[0]*along/2+sn*n[0]*cross/2,c[1]+sv*v[1]*along/2+sn*n[1]*cross/2) for sv,sn in [(-1,-1),(1,-1),(1,1),(-1,1)]])
def parts(g):
 if g.is_empty:return []
 if g.geom_type=='Polygon':return [g]
 return sum([parts(q) for q in getattr(g,'geoms',[])],[])
stripes=[];records=[];ramps=[];seen=[]
for item in json.load(open(a.crossings))['crossings']:
 if item['distance_to_ground_route_m']>2:continue
 tags=item['tags']
 if tags.get('crossing')=='unmarked' or tags.get('crossing:markings')=='no':continue
 xy=loc(item['twd97']);q=Point(xy);t,line=min(routes,key=lambda r:r[1].distance(q));s=line.project(q);aa=line.interpolate(max(0,s-.5));bb=line.interpolate(min(line.length,s+.5));dx,dy=bb.x-aa.x,bb.y-aa.y;norm=math.hypot(dx,dy)
 if norm<1e-7:continue
 v=(dx/norm,dy/norm);n=(-v[1],v[0]);ln=t.get('lanes','');lanes=int(ln) if str(ln).isdigit() else (2 if t.get('oneway')=='yes' else 4);span=lanes*3.25
 if any(q.distance(old)<2 for old in seen):continue
 seen.append(q);mark=tags.get('crossing:markings') or tags.get('crossing_ref') or 'estimated_zebra'
 localstripes=[]
 if mark=='lines':
  for shift in [-2,2]:localstripes.extend(parts(rectangle((xy[0]+v[0]*shift,xy[1]+v[1]*shift),v,n,.15,span).intersection(road)))
 else:
  for k in range(math.ceil(span)):
   shift=-span/2+k+.25
   localstripes.extend(parts(rectangle((xy[0]+n[0]*shift,xy[1]+n[1]*shift),v,n,4,.5).intersection(road)))
 stripes+=localstripes;records.append({'osm_id':item['osm_id'],'section':t['name'],'source_xy':xy,'marking_tag':mark,'estimated_crossing_span_m':span,'stripe_pieces':len(localstripes),'status':'OSM point; orientation, width and pattern extents inferred'})
 # Ramp candidates are recorded and cut only where the ray meets mapped sidewalk within 35m.
 for sign in [-1,1]:
  direction=(n[0]*sign,n[1]*sign);ray=LineString([xy,(xy[0]+direction[0]*35,xy[1]+direction[1]*35)]);hit=ray.intersection(walk)
  if hit.is_empty:continue
  edge=nearest_points(q,hit)[1];dist=q.distance(edge)
  if dist<2 or dist>35:continue
  origin=(edge.x,edge.y);center=(edge.x+direction[0]*.8,edge.y+direction[1]*.8);poly=rectangle(center,v,direction,1.8,1.6).intersection(walk)
  if poly.area<1 or any(poly.intersection(r['geom']).area>.1 for r in ramps):continue
  ramps.append({'geom':poly,'origin':origin,'direction':direction,'osm_id':item['osm_id'],'status':'Estimated ramp from mapped crossing and sidewalk intersection; actual presence unverified'})
cut=unary_union([r['geom'] for r in ramps]);walkcut=walk.difference(cut)
# Rebuild the sidewalk and curbs around candidate ramps; original before-version remains available.
curb=surface('GROUND_CURBS_ESTIMATED',.17).difference(cut.buffer(.02))
def mesh(polys,z0,top):
 vs=[];fs=[]
 for poly in polys:
  if poly.area<.0001:continue
  def z(q):return top(q) if callable(top) else top
  for tri in constrained_delaunay_triangles(poly).geoms:
   pts=list(tri.exterior.coords)[:-1];i=len(vs);vs.extend([(*q,z0) for q in pts]+[(*q,z(q)) for q in pts]);fs.extend([(i+2,i+1,i),(i+3,i+4,i+5)])
  for ring in [poly.exterior]+list(poly.interiors):
   pts=list(ring.coords)
   for aa,bb in zip(pts,pts[1:]):
    i=len(vs);vs.extend([(*aa,z0),(*bb,z0),(*bb,z(bb)),(*aa,z(aa))]);fs.append((i,i+1,i+2,i+3))
 return {'vertices':vs,'faces':fs}
rm={'vertices':[],'faces':[]}
for r in ramps:
 o=r['origin'];v=r['direction'];m=mesh(parts(r['geom']),-.02,lambda q:max(0,min(.15,((q[0]-o[0])*v[0]+(q[1]-o[1])*v[1])*.15/1.6)));off=len(rm['vertices']);rm['vertices']+=m['vertices'];rm['faces'] += [[i+off for i in f] for f in m['faces']]
result={'summary':{'crossing_points_used':len(records),'marking_pieces':len(stripes),'estimated_ramp_candidates':len(ramps)},'crossings':records,'ramps':[{k:v for k,v in r.items() if k!='geom'} for r in ramps],'assumptions':{'crosswalk_width_m':4,'stripe_width_m':.5,'ramp_width_m':1.8,'ramp_depth_m':1.6,'ramp_rise_m':.15,'status':'Working-model estimates; no claim of field-verified accessibility'},'meshes':{'GROUND_CROSSWALK_MARKINGS_ESTIMATED':mesh(stripes,.002,.005),'GROUND_SIDEWALKS_WITH_ESTIMATED_RAMPS':mesh(parts(walkcut),0,.15),'GROUND_CURBS_WITH_ESTIMATED_OPENINGS':mesh(parts(curb),0,.17),'GROUND_CURB_RAMPS_ESTIMATED':rm}}
out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=True);(out/'crossing_payload.json').write_text(json.dumps(result));(out/'crossing_check.json').write_text(json.dumps({k:v for k,v in result.items() if k!='meshes'},ensure_ascii=False,indent=2));print(json.dumps(result['summary']))

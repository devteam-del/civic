"""Build a reversible structural comparison from observed XY and sparse estimated height anchors.
No surveyed elevations are claimed. Continuous interpolation, cap and bearing sizes
are explicitly model assumptions. Original scenes and meshes remain unchanged.
"""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(bpy.data.filepath).parent/'PierPositions_20260924';src=bpy.data.scenes['CIVIC_PIER_XY_REVIEW_20260923'];name='CIVIC_STRUCTURE_CONNECTED_EST_20260929';assert name not in bpy.data.scenes
review=json.loads((r/'streetview_height_review.json').read_text());snap=json.loads((r/'vertical_support_contact_audit.json').read_text());points=[(-670.938,4.8)]+sorted((a['xy'][0],a['mean_height_est_m']) for a in review['anchors'])+[(5869.264,4.8)]
def height(x):
 if x<=points[0][0]:return points[0][1]
 for (a,h),(b,k) in zip(points,points[1:]):
  if x<=b:return h+(k-h)*(x-a)/(b-a)
 return points[-1][1]
def delta(x):return height(x)-4.8
# Pair by proximity only as a documented working bent association.
ps=sorted(snap['rows'],key=lambda p:(p['xy'][0],p['xy'][1]));groups=[];used=set()
for i,p in enumerate(ps):
 if i in used:continue
 ds=sorted((math.dist(p['xy'],q['xy']),j) for j,q in enumerate(ps) if j!=i and j not in used)
 if ds and ds[0][0]<25 and abs(p['xy'][0]-ps[ds[0][1]]['xy'][0])<10:
  j=ds[0][1];groups.append([p,ps[j]]);used.update([i,j])
 else:groups.append([p]);used.add(i)
struct=[o for o in src.objects if o.type=='MESH' and o.name.startswith(('DECK_','GIRDER_','PARAPET_'))];assert len(struct)==450
repl={};deformed=[]
for old in struct:
 ob=old.copy();ob.data=old.data.copy();ob.name='VC_EST_'+old.name;ob['source_object']=old.name;ob['survey_verified']=False;ob['height_status']='Sparse street-view height anchors with linear interpolation; terminal heights retain prior estimate.'
 # Add exact shared height-profile break lines before deformation.
 bm=bmesh.new();bm.from_mesh(ob.data);mw=old.matrix_world;inv=mw.inverted();lo=min((mw@v.co).x for v in bm.verts);hi=max((mw@v.co).x for v in bm.verts)
 for x,_ in points[1:-1]:
  if lo+1e-5<x<hi-1e-5:
   normal=mw.to_3x3().transposed()@Vector((1,0,0));normal.normalize();bmesh.ops.bisect_plane(bm,geom=bm.verts[:]+bm.edges[:]+bm.faces[:],dist=1e-5,plane_co=inv@Vector((x,0,0)),plane_no=normal,clear_inner=False,clear_outer=False)
 for v in bm.verts:
  p=mw@v.co;p.z+=delta(p.x);v.co=inv@p
 bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);bm.to_mesh(ob.data);bm.free();ob.data.update();repl[old]=ob;deformed.append(ob)
# Underside geometry is sampled from the new mesh, not assumed from deck bounding boxes.
cache=[]
for o in deformed:
 if not o.name.startswith('VC_EST_GIRDER_'):continue
 vs=[o.matrix_world@v.co for v in o.data.vertices];lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)];cache.append((o.name,lo,hi,BVHTree.FromPolygons(vs,[list(p.vertices) for p in o.data.polygons])))
def hits(x,y):
 found=[]
 for nm,a,b,tr in cache:
  if a[0]-.001<=x<=b[0]+.001 and a[1]-.001<=y<=b[1]+.001:
   h=tr.ray_cast(Vector((x,y,-2)),Vector((0,0,1)),60)
   if h[0] is not None:found.append((h[0].z,nm))
 return min(found) if found else None
paths=json.loads((r.parent/'Underbridge_20260922/span_height_context.json').read_text())['paths']
def normal_at(x,y):
 best=None
 for p in paths:
  for a,b in zip(p['points'],p['points'][1:]):
   dx,dy=b[0]-a[0],b[1]-a[1];l2=dx*dx+dy*dy
   if l2<1e-8:continue
   t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/l2));d=(x-a[0]-t*dx)**2+(y-a[1]-t*dy)**2
   if best is None or d<best[0]:best=(d,Vector((-dy,dx)).normalized())
 return best[1]
newparts=[];report=[];warnings=[]
concrete=next((m for o in src.objects if 'CAP_ESTIMATED' in o.name for m in o.data.materials),None)
def prism(nm,c,axis,span,depth,z0,z1,material=None):
 v=Vector((-axis.y,axis.x));corners=[c+axis*a+v*b for a,b in [(-span/2,-depth/2),(span/2,-depth/2),(span/2,depth/2),(-span/2,depth/2)]];verts=[(p.x,p.y,z) for z in [z0,z1] for p in corners];me=bpy.data.meshes.new(nm+'_Mesh');me.from_pydata(verts,[],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.update();ob=bpy.data.objects.new(nm,me)
 if material:me.materials.append(material)
 ob['survey_verified']=False;ob['status']='Estimated structural comparison; dimensions and association not surveyed';newparts.append(ob);return ob
for gi,g in enumerate(groups):
 c=Vector(tuple(sum(p['xy'][i] for p in g)/len(g) for i in [0,1]));axis=(Vector(g[1]['xy'])-Vector(g[0]['xy'])).normalized() if len(g)==2 else normal_at(*c)
 if axis.y<0:axis=-axis
 samples=[]
 for j in range(-175,176):
  t=j*.2;q=c+axis*t;hit=hits(*q)
  if hit:samples.append({'t':t,'xy':list(q),'z':hit[0],'girder':hit[1]})
 # Keep only contiguous girder flange intervals within the bent's nearby carriageways.
 runs=[]
 for q in samples:
  if runs and q['t']-runs[-1][-1]['t']<.31:runs[-1].append(q)
  else:runs.append([q])
 runs=[run for run in runs if min(abs(q['t']) for q in run)<24]
 if not runs:
  warnings.append({'members':[p['name'] for p in g],'issue':'No girder underside along working bent axis; retained original shaft heights and caps.'});continue
 contacts=[min(run,key=lambda q:abs(q['t']-(run[0]['t']+run[-1]['t'])/2)) for run in runs];minz=min(q['z'] for q in contacts);capbottom=minz-.8;captop=minz-.2
 extent=[(Vector(p['xy'])-c).dot(axis) for p in g]+[q['t'] for q in contacts];a,b=min(extent)-1.3,max(extent)+1.3;cc=c+axis*((a+b)/2)
 cap=prism('VC_EST_BENT_%03d_CAP'%gi,cc,axis,b-a,2.4,capbottom,captop,concrete);cap['members']=json.dumps([p['name'] for p in g]);cap['association']='Nearest pair within 25m and longitudinal difference <10m; estimated.'
 pads=[]
 for bi,q in enumerate(contacts):
  # Narrow working pad fits the observed model flange interval; top follows sampled underside.
  pad=prism('VC_EST_BENT_%03d_BEARING_%02d'%(gi,bi),Vector(q['xy']),axis,.3,1.0,captop,q['z'],concrete);pad['contact_girder']=q['girder'];pads.append({'object':pad.name,'girder':q['girder'],'xy':q['xy'],'bottom_z':captop,'top_z':q['z']})
 members=[]
 for p in g:
  old=src.objects[p['name']];ob=old.copy();ob.data=old.data.copy();ob.name='VC_EST_'+old.name;inv=old.matrix_world.inverted();zs=[(old.matrix_world@v.co).z for v in old.data.vertices];z0,z1=min(zs),max(zs);assert capbottom>z0+2
  for v in ob.data.vertices:
   q=old.matrix_world@v.co;q.z=z0+(q.z-z0)*(capbottom-z0)/(z1-z0);v.co=inv@q
  ob.data.update();ob['source_object']=old.name;ob['survey_verified']=False;ob['height_status']='Height interpolated between sparse street-view estimates, then fitted to comparison girder underside';ob['height_anchor_file']='streetview_height_review.json';repl[old]=ob;members.append({'original':old.name,'new':ob.name,'base_z':z0,'old_top_z':z1,'new_top_z':capbottom,'xy_unchanged':True})
 report.append({'bent':gi,'members':members,'cap':cap.name,'cap_bottom_z':capbottom,'cap_top_z':captop,'span_m':b-a,'bearing_contacts':pads,'survey_verified':False})
assert not warnings, 'Unconnected groups need a separate solution: '+json.dumps(warnings)
# Remove legacy caps only in the new comparison scene. They remain in original scenes.
for o in src.objects:
 if o.type=='MESH' and 'CAP_ESTIMATED' in o.name:repl[o]=None
s=src.copy();s.name=name;s['workflow']='Estimated vertical integration comparison; sparse anchors, all other heights interpolated. Original XY scene preserved.';s['survey_verified']=False
flags={}
def read(lc):
 flags[lc.collection]=(lc.exclude,lc.hide_viewport)
 for ch in lc.children:read(ch)
read(src.view_layers[0].layer_collection);memo={}
def clone(c):
 if c in memo:return memo[c]
 if not any(o in repl for o in c.all_objects):return c
 nc=bpy.data.collections.new('VC_BRANCH_%03d'%len(memo));memo[c]=nc;nc['source_collection']=c.name;nc.hide_render=c.hide_render;nc.hide_viewport=c.hide_viewport
 for o in c.objects:
  q=repl.get(o,o)
  if q is not None:nc.objects.link(q)
 for ch in c.children:nc.children.link(clone(ch))
 return nc
for c in list(s.collection.children):
 nc=clone(c)
 if nc!=c:s.collection.children.unlink(c);s.collection.children.link(nc)
for o in list(s.collection.objects):
 if o in repl:
  s.collection.objects.unlink(o)
  if repl[o] is not None:s.collection.objects.link(repl[o])
col=bpy.data.collections.new('VC_CONNECTED_CAPS_AND_BEARINGS');s.collection.children.link(col)
for o in newparts:col.objects.link(o)
inverse={v:k for k,v in memo.items()}
def restore(lc):
 old=inverse.get(lc.collection,lc.collection)
 if old in flags:lc.exclude,lc.hide_viewport=flags[old]
 for ch in lc.children:restore(ch)
for vl in s.view_layers:restore(vl.layer_collection)
out={'scene':s.name,'source_scene':src.name,'height_profile_points':points,'assumptions':{'height_reference':'Model ground datum; no absolute elevation control.','profile':'Linear interpolation between 4 observed estimates; terminal values inherited from old model.','bent_pairing':'Proximity estimate, not structural drawing.','cap_depth_m':.6,'cap_longitudinal_width_m':2.4,'bearing_min_height_m':.2,'bearing_plan_m':[.3,1.0],'deck_thickness_and_girders':'Inherited model sections; translated vertically without claiming surveyed dimensions.','ramps':'Existing mapped deck geometry retained; grade topology not independently verified.'},'summary':{'deformed_structure_objects':len(deformed),'bents':len(report),'shafts_adjusted':sum(len(x['members']) for x in report),'bearing_pads':sum(len(x['bearing_contacts']) for x in report),'unconnected_groups':len(warnings),'field_verified':0},'bents':report,'warnings':warnings}
(r/'connected_structure_application.json').write_text(json.dumps(out,indent=2));result=out['summary']

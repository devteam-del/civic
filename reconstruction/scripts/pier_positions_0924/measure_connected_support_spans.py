"""Measure every candidate consecutive support interval using the integrated model.
Values are model dimensions, not surveyed clearances. Unknown ground stays null.
"""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(bpy.data.filepath).parent/'PierPositions_20260924';s=bpy.data.scenes['CIVIC_STRUCTURE_CONNECTED_EST_20260929'];app=json.loads((r/'connected_structure_application.json').read_text());ctx=json.loads((r.parent/'Underbridge_20260922/span_height_context.json').read_text());paths=ctx['paths']
def dist(a,b):return math.dist(a[:2],b[:2])
def prepare(p):
 p['chain']=[0.]
 for a,b in zip(p['points'],p['points'][1:]):p['chain'].append(p['chain'][-1]+dist(a,b))
 p['length']=p['chain'][-1]
def project(xy,p):
 best=None
 for i,(a,b) in enumerate(zip(p['points'],p['points'][1:])):
  dx,dy=b[0]-a[0],b[1]-a[1];l2=dx*dx+dy*dy
  if not l2:continue
  t=max(0,min(1,((xy[0]-a[0])*dx+(xy[1]-a[1])*dy)/l2));q=[a[0]+t*dx,a[1]+t*dy];d=dist(xy,q)
  if best is None or d<best[0]:best=(d,p['chain'][i]+t*math.sqrt(l2))
 return best[1]
def at(p,ss):
 for i in range(len(p['points'])-1):
  if ss<=p['chain'][i+1]+1e-6:
   a,b=p['points'][i:i+2];l=p['chain'][i+1]-p['chain'][i]
   if not l:continue
   t=(ss-p['chain'][i])/l;return [a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])],[(b[0]-a[0])/l,(b[1]-a[1])/l]
 return p['points'][-1],[1,0]
for p in paths:
 prepare(p);p['supports']=[];id=p['osm_id']
 for b in app['bents']:
  pads=[x for x in b['bearing_contacts'] if x['girder'].startswith('VC_EST_GIRDER_'+id+'_')]
  if pads:
   xy=[sum(x['xy'][i] for x in pads)/len(pads) for i in [0,1]];p['supports'].append({'bent':b['bent'],'s':project(xy,p),'members':[m['new'] for m in b['members']]})
 p['supports'].sort(key=lambda x:x['s'])
spans=[]
for p in paths:
 for a,b in zip(p['supports'],p['supports'][1:]):
  if b['s']-a['s']>2:spans.append({'path':p,'start_s':a['s'],'end_s':b['s'],'a':a,'b':b,'decks':[p['deck']],'boundary':False})
# Adjacent mapped path endpoints are joined only when supports lie on opposite sides of the node.
ends=[]
for p in paths:
 if p['supports']:
  for side in [0,1]:ends.append((p,side,p['points'][0 if side==0 else -1],p['supports'][0 if side==0 else -1]))
for i,(p,side,xy,a) in enumerate(ends):
 for q,other,yz,b in ends[i+1:]:
  if p is q or dist(xy,yz)>.5 or a['bent']==b['bent']:continue
  pa,_=at(p,a['s']);pb,_=at(q,b['s']);va=Vector(pa)-Vector(xy);vb=Vector(pb)-Vector(yz)
  if va.length<.01 or vb.length<.01 or va.normalized().dot(vb.normalized())>-.7:continue
  da=a['s'] if side==0 else p['length']-a['s'];db=b['s'] if other==0 else q['length']-b['s']
  if not 2<da+db<120:continue
  segA=[v for v,c in zip(p['points'],p['chain']) if (c<a['s'] if side==0 else c>a['s'])]
  if side==0:segA.reverse()
  segB=[v for v,c in zip(q['points'],q['chain']) if (c<b['s'] if other==0 else c>b['s'])]
  if other==1:segB.reverse()
  pts=[pa]+segA+segB+[pb];clean=[pts[0]]
  for v in pts[1:]:
   if dist(v,clean[-1])>.001:clean.append(v)
  cp={'points':clean,'width':min(p['width'],q['width'])};prepare(cp);spans.append({'path':cp,'start_s':0,'end_s':cp['length'],'a':a,'b':b,'decks':[p['deck'],q['deck']],'boundary':True})
foot=json.loads((r/'live_comparison_ground_footprints.json').read_text());ground_names={x['name'] for k in ['roads','medians'] for x in foot[k]};ground_names.update(o.name for o in s.objects if o.name.startswith(('CAL_GROUND_SIDEWALKS_','CAL_GROUND_ROADS_ESTIMATED_GAPS')));geometry=[]
for o in s.objects:
 role='ground' if o.name in ground_names else 'deck' if o.name.startswith('VC_EST_DECK_') else 'soffit' if o.name.startswith(('VC_EST_GIRDER_','VC_EST_BENT_')) else None
 if not role or o.type!='MESH':continue
 vs=[o.matrix_world@v.co for v in o.data.vertices];lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)];geometry.append((o.name,role,lo,hi,BVHTree.FromPolygons(vs,[list(p.vertices) for p in o.data.polygons])))
reports=[]
for n,sp in enumerate(spans):
 p=sp['path'];rows=[]
 for k in range(11):
  ss=sp['start_s']+(sp['end_s']-sp['start_s'])*k/10;xy,tan=at(p,ss);cross=[]
  for j in range(9):
   off=(j-4)*p['width']*.105;x=xy[0]-tan[1]*off;y=xy[1]+tan[0]*off;gz=[];dz=[];sz=[]
   for nm,role,a,b,tr in geometry:
    if not (a[0]-.001<=x<=b[0]+.001 and a[1]-.001<=y<=b[1]+.001):continue
    up=role=='soffit';h=tr.ray_cast(Vector((x,y,-2 if up else 80)),Vector((0,0,1 if up else -1)),100)
    if h[0] is not None:(gz if role=='ground' else dz if role=='deck' else sz).append(h[0].z)
   ground=max(gz) if gz else None;top=max(dz) if dz else None;soff=min(sz) if sz else None;cross.append({'xy':[round(x,3),round(y,3)],'ground_z':ground,'deck_top_z':top,'soffit_z':soff,'clearance_m':soff-ground if soff is not None and ground is not None else None})
  rows.append({'fraction':k/10,'cross_samples':cross})
 vals=[v['clearance_m'] for row in rows for v in row['cross_samples'] if v['clearance_m'] is not None];tops=[v['deck_top_z'] for row in rows for v in row['cross_samples'] if v['deck_top_z'] is not None]
 reports.append({'span_id':'CONNECTED_SPAN_%03d'%n,'start_bent':sp['a']['bent'],'end_bent':sp['b']['bent'],'start_piers':sp['a']['members'],'end_piers':sp['b']['members'],'decks':sp['decks'],'length_m':sp['end_s']-sp['start_s'],'boundary_span':sp['boundary'],'sampled_min_clearance_m':min(vals) if vals else None,'deck_top_z_range':[min(tops),max(tops)] if tops else None,'ground_missing_samples':sum(v['ground_z'] is None for row in rows for v in row['cross_samples']),'samples':rows,'survey_verified':False})
out={'summary':{'candidate_spans':len(reports),'boundary_spans':sum(x['boundary_span'] for x in reports),'spans_with_ground_gaps':sum(x['ground_missing_samples']>0 for x in reports),'spans_over_60m':sum(x['length_m']>60 for x in reports),'field_verified':0},'basis':'Integrated Blender geometry. Sparse estimated street-view anchors, interpolated heights. 11x9 samples per candidate span; sampled minimum is not a continuous clearance guarantee. Missing ground remains unknown.','spans':reports};(r/'connected_span_height_audit.json').write_text(json.dumps(out,indent=2));(r/'connected_span_height_summary.json').write_text(json.dumps({'summary':out['summary'],'basis':out['basis']},indent=2));result=out['summary']

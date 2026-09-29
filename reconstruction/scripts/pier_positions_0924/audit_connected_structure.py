"""Validate the reversible structural comparison without asserting field accuracy."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(bpy.data.filepath).parent/'PierPositions_20260924';s=bpy.data.scenes['CIVIC_STRUCTURE_CONNECTED_EST_20260929'];src=bpy.data.scenes['CIVIC_PIER_XY_REVIEW_20260923'];app=json.loads((r/'connected_structure_application.json').read_text());issues=[];rows=[];cache={}
def bounds(o):
 vs=[o.matrix_world@v.co for v in o.data.vertices];return [[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]]
def tree(o):
 if o.name not in cache:cache[o.name]=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])
 return cache[o.name]
for bent in app['bents']:
 cap=s.objects[bent['cap']];clo,chi=bounds(cap);pier_errors=[];pad_errors=[]
 for m in bent['members']:
  o=s.objects[m['new']];old=src.objects[m['original']];a,b=bounds(o);oa,ob=bounds(old);xyerr=max(abs(a[i]-oa[i]) for i in [0,1])+max(abs(b[i]-ob[i]) for i in [0,1]);gap=clo[2]-b[2]
  assert xyerr<.002 and abs(gap)<.002
  # Shaft footprint must be supported by the cap footprint; top ray samples every shaft vertex.
  misses=0
  for v in o.data.vertices:
   p=o.matrix_world@v.co
   if abs(p.z-b[2])<.002:
    hit=tree(cap).ray_cast(Vector((p.x,p.y,p.z-.01)),Vector((0,0,1)),2)
    if hit[0] is None:misses+=1
  if misses:pier_errors.append({'shaft':o.name,'top_vertices_outside_cap':misses})
 for pad in bent['bearing_contacts']:
  o=s.objects[pad['object']];a,b=bounds(o);gap=a[2]-chi[2];x,y=pad['xy'];h=tree(s.objects[pad['girder']]).ray_cast(Vector((x,y,-2)),Vector((0,0,1)),60);endgap=h[0].z-b[2] if h[0] is not None else None
  if abs(gap)>.002 or endgap is None or abs(endgap)>.002:pad_errors.append({'pad':o.name,'bottom_gap':gap,'top_gap':endgap})
 rows.append({'bent':bent['bent'],'shaft_cap_issues':pier_errors,'bearing_contact_issues':pad_errors})
 if pier_errors or pad_errors:issues.append(rows[-1])
mesh_issues=[]
for o in s.objects:
 if o.type=='MESH' and o.name.startswith('VC_EST_'):
  bm=bmesh.new();bm.from_mesh(o.data);non=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);bm.free()
  if non or vol<=0:mesh_issues.append({'object':o.name,'nonmanifold_edges':non,'signed_volume':vol})
# Deck footprints and path endpoints for independent connectivity audit outside Blender.
ctx=json.loads((r.parent/'Underbridge_20260922/span_height_context.json').read_text());decks=[]
for p in ctx['paths']:
 o=s.objects['VC_EST_'+p['deck']];faces=[]
 for f in o.data.polygons:
  co=[o.matrix_world@o.data.vertices[i].co for i in f.vertices];area=abs(sum(a.x*b.y-b.x*a.y for a,b in zip(co,co[1:]+co[:1])))/2
  if area>1e-8:faces.append([[v.x,v.y] for v in co])
 decks.append({'name':o.name,'faces':faces,'path_endpoints':[p['points'][0],p['points'][-1]]})
(r/'connected_deck_footprints.json').write_text(json.dumps(decks))
out={'summary':{'shafts':sum(len(b['members']) for b in app['bents']),'bents':len(rows),'bearing_pads':app['summary']['bearing_pads'],'contact_issue_bents':len(issues),'mesh_issues':len(mesh_issues),'xy_preserved':True,'field_verified':False},'contact_issues':issues,'mesh_issues':mesh_issues,'rows':rows};(r/'connected_structure_validation.json').write_text(json.dumps(out,indent=2));result=out['summary']

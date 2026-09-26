"""Build a separate, explicitly estimated support-alignment comparison scene."""
import bpy,os,json,math,datetime
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=os.path.join(os.path.dirname(bpy.data.filepath),'Underbridge_20260922')
source=bpy.data.scenes['CIVIC_UNDERBRIDGE_MASSING_20260916']
assert bpy.context.scene==source
name='CIVIC_SUPPORT_ALIGNMENT_EST_0922'
assert bpy.data.scenes.get(name) is None,'Comparison already exists; review before rebuilding'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(os.path.dirname(bpy.data.filepath),'BEFORE_SUPPORT_ALIGNMENT_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.blend'),copy=True)
a=json.load(open(os.path.join(root,'support_alignment_candidates.json')))
dg=bpy.context.evaluated_depsgraph_get()
cache={}
def bound(o):
 vs=[o.matrix_world@Vector(v) for v in o.bound_box]
 return ([min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)])
grounds=[(o,*bound(o)) for o in source.objects if o.type=='MESH' and o.name.startswith(('CAL_GROUND_ROADS_OFFICIAL_XY','CAL_GROUND_MEDIAN_WORKING','UB_MEDIAN_0_WITH'))]
beams=[(o,*bound(o)) for o in source.objects if o.type=='MESH' and o.name.startswith('GIRDER_')]
def ray(items,x,y,up):
 hits=[]
 for o,lo,hi in items:
  if not(lo[0]<=x<=hi[0] and lo[1]<=y<=hi[1]):continue
  if o.name not in cache:
   e=o.evaluated_get(dg);m=e.to_mesh()
   cache[o.name]=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[list(p.vertices) for p in m.polygons])
   e.to_mesh_clear()
  h=cache[o.name].ray_cast(Vector((x,y,-20 if up else 30)),Vector((0,0,1 if up else -1)),100)
  if h[0] is not None:hits.append((float(h[0].z),o.name))
 return (min(hits) if up else max(hits)) if hits else None
plans=[]
for r in a['groups']:
 if r['status']!='CONSTRAINED_ESTIMATE_NOT_ADOPTED':continue
 cap=source.objects.get('UNVERIFIED_Pier_%03d_CAP_ESTIMATED'%r['group'])
 if cap is None:r['build_status']='HOLD_NO_CAP';continue
 dx,dy=r['delta_xy'];items=[]
 for n in r['piers']:
  o=source.objects[n];lo,hi=bound(o);x=(lo[0]+hi[0])/2+dx;y=(lo[1]+hi[1])/2+dy
  g=ray(grounds,x,y,False);b=ray(beams,x,y,True)
  items.append({'object':o,'xy':[x,y],'lo':lo,'hi':hi,'ground':g,'beam':b})
 if any(v['ground'] is None or v['beam'] is None for v in items):
  r['build_status']='HOLD_MISSING_GROUND_OR_BEAM_RAY';continue
 soffits=[v['beam'][0] for v in items]
 if max(soffits)-min(soffits)>.05:r['build_status']='HOLD_DIFFERENT_BEAM_UNDERSIDES';continue
 clo,chi=bound(cap);capheight=chi[2]-clo[2]
 top=min(soffits)-.2;bottom=top-capheight
 if any(bottom-v['ground'][0]<1. for v in items):r['build_status']='HOLD_INVALID_SHAFT_HEIGHT';continue
 plans.append((r,cap,items,bottom,top))
replacements={};newobjects=[];records=[]
for r,cap,items,bottom,top in plans:
 dx,dy=r['delta_xy']
 for v in items:
  old=v['object'];ob=old.copy();ob.data=old.data.copy();ob.name=old.name+'_ALIGN_EST';inv=ob.matrix_world.inverted()
  for vert in ob.data.vertices:
   p=old.matrix_world@vert.co;t=(p.z-v['lo'][2])/(v['hi'][2]-v['lo'][2])
   vert.co=inv@Vector((p.x+dx,p.y+dy,v['ground'][0]+t*(bottom-v['ground'][0])))
  ob['basis']='Median-constrained estimate; not Street View position measurement'
  ob['original_object']=old.name;ob['delta_xy']=r['delta_xy'];ob['ground_model_z']=v['ground'][0];ob['shaft_top_model_z']=bottom;ob['real_world_verified']=False
  replacements[old]=ob;newobjects.append(ob)
  records.append({'pier':old.name,'replacement':ob.name,'delta_xy':r['delta_xy'],'ground_z':v['ground'][0],'shaft_top_z':bottom,'shaft_height_m':bottom-v['ground'][0],'beam_z':v['beam'][0],'pad_thickness_m':.2,'road_overlap_after_xy_m2':r['new_road_outside_median_m2'],'real_world_verified':False})
  # Work-model bearing pad at the pier axis, not an observed bearing footprint.
  x,y=v['xy'];z=top
  vs=[(x+sx*.55,y+sy*.55,z+sz*.2) for sz in [0,1] for sy in [-1,1] for sx in [-1,1]]
  fs=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
  me=bpy.data.meshes.new(old.name+'_PAD_EST');me.from_pydata(vs,[],fs);me.update()
  pad=bpy.data.objects.new(old.name+'_PAD_EST',me);pad['basis']='1.1m square x 0.2m model bearing; dimensions unverified';newobjects.append(pad)
 ob=cap.copy();ob.data=cap.data.copy();ob.name=cap.name+'_ALIGN_EST'
 ob.matrix_world.translation+=Vector((dx,dy,top-bound(cap)[1][2]))
 ob['basis']='Rigid pair translation; cap lowered to leave assumed 0.2m bearing space';ob['real_world_verified']=False
 replacements[cap]=ob;newobjects.append(ob);r['build_status']='BUILT_COMPARISON_ONLY'
scene=source.copy();scene.name=name
memo={}
def replace_collection(c):
 if c in memo:return memo[c]
 if not any(o in replacements for o in c.all_objects):return c
 nc=bpy.data.collections.new(c.name+'_ALIGN_EST');memo[c]=nc;nc.hide_viewport=c.hide_viewport;nc.hide_render=c.hide_render
 for o in c.objects:nc.objects.link(replacements.get(o,o))
 for ch in c.children:nc.children.link(replace_collection(ch))
 return nc
for c in list(scene.collection.children):
 nc=replace_collection(c)
 if nc!=c:scene.collection.children.unlink(c);scene.collection.children.link(nc)
for o in list(scene.collection.objects):
 if o in replacements:scene.collection.objects.unlink(o);scene.collection.objects.link(replacements[o])
pads=bpy.data.collections.new('ALIGN_EST_BEARINGS');scene.collection.children.link(pads)
for o in newobjects:
 if o not in replacements.values():pads.objects.link(o)
bpy.context.window.scene=scene
# Hide stale height markers, retaining them in the source scene.
def exclusions(lc):
 if lc.collection.name in ['UB_UTURN_DISPUTED_SUPPORTS_ORIGINAL','UB_SPAN_HEIGHT_MODEL_AUDIT','UB_SPAN_HEIGHT_LABELS']:lc.exclude=True
 for ch in lc.children:exclusions(ch)
for vl in scene.view_layers:exclusions(vl.layer_collection)
scene['basis']='ESTIMATED COMPARISON. Original scene preserved. No field-verified pier relocation.'
scene['height_audit_requires_refresh']=True
out={'source_scene':source.name,'comparison_scene':scene.name,'built_groups':len(plans),'built_piers':len(records),'records':records,'group_decisions':a['groups'],'limitations':['Positions constrained to estimated median, not accepted Street View coordinates','Heights fit current modeled ground and girders; uniform 8m deck remains uncalibrated','Bearing pad footprint assumed; no structural validation','Original height audit is stale for comparison']}
json.dump(out,open(os.path.join(root,'support_alignment_build_report.json'),'w'),indent=2)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
result={'scene':scene.name,'groups':len(plans),'piers':len(records),'held':[(r['group'],r.get('build_status')) for r in a['groups'] if r.get('build_status','').startswith('HOLD')]}

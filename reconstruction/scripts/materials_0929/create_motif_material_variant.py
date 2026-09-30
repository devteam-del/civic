import bpy, os, json, collections, math
from pathlib import Path
src=bpy.context.scene
assert src.name=='CIVIC_STRUCTURE_CONNECTED_EST_20260929'
out=Path(bpy.data.filepath).parent
folder=out/'Materials_20260929'
folder.mkdir(exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
s=bpy.data.scenes.new('CIVIC_MOTIF_MATERIALS_20260929')
s.unit_settings.system='METRIC'
s.world=src.world.copy() if src.world else bpy.data.worlds.new('MOTIF_DAYLIGHT')
palette={
'concrete':((.48,.46,.415),.82,0,2.5,.0015),
'stone':((.57,.55,.49),.8,0,12,.001),
'paving':((.46,.47,.435),.88,0,35,.0008),
'asphalt':((.085,.092,.09),.94,0,90,.001),
'metal':((.10,.115,.11),.42,.75,80,.00015),
'glass':((.13,.19,.18),.22,.25,0,0),
'rubber':((.025,.029,.028),.95,0,35,.0003),
'wood':((.22,.135,.065),.72,0,8,.0007),
'paint':((.82,.81,.73),.75,0,0,0),
'soil':((.12,.095,.058),1,0,20,.003),
'green':((.14,.22,.095),.88,0,6,.001)
}
mats={}
for key,(color,rough,metal,scale,bump) in palette.items():
 m=bpy.data.materials.new('MOTIF_'+key.upper());m.use_nodes=True;m.diffuse_color=(*color,1)
 n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
 p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if scale:
  geo=n.new('ShaderNodeNewGeometry');tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=scale;tex.inputs['Detail'].default_value=2
  l.new(geo.outputs['Position'],tex.inputs['Vector'])
  ramp=n.new('ShaderNodeValToRGB')
  ramp.color_ramp.elements[0].color=(*(v*.83 for v in color),1);ramp.color_ramp.elements[1].color=(*(min(v*1.1,1) for v in color),1)
  l.new(tex.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color'])
  bn=n.new('ShaderNodeBump');bn.inputs['Strength'].default_value=.22;bn.inputs['Distance'].default_value=bump
  l.new(tex.outputs['Fac'],bn.inputs['Height']);l.new(bn.outputs[0],p.inputs['Normal'])
 m['visual_reference']='https://www.motifla.com.tw/book-4.html';m['status']='interpretive presentation palette, not surveyed finishes'
 mats[key]=m
def classify(o,m):
 name=o.name.upper();mn=m.name.upper() if m else ''
 if name.startswith('VC_EST_'):
  if 'BEARING' in name:return 'rubber'
  if 'DECK_' in name:return 'asphalt'
  return 'concrete'
 if any(x in mn for x in ['JINGFU_','ZHONGLUN_BLUE','ZHONGLUN_RED','GUARDRAIL_YELLOW']):return None
 if 'GLASS' in mn:return 'glass'
 if 'WOOD' in mn:return 'wood'
 if any(x in mn for x in ['METAL','STEEL','RAIL','GRATE','HANDLE','JOINT','DARK','FRAME','LOUVER','LATTICE','FAN','DOOR']):return 'metal'
 if 'MARKING' in mn or 'EDGE_LINE' in mn:return 'paint'
 if 'ROAD' in mn or mn=='RAMP_FINISH' or 'PARKING_SECTION' in mn:return 'asphalt'
 if 'SIDEWALK' in mn or 'FLOOR' in mn or 'STAIRS' in mn:return 'paving'
 if 'MEDIAN' in mn or 'CURB' in mn or 'STONE' in mn:return 'stone'
 if mn=='BLOCK_CONTEXT_LAND':return 'stone'
 if 'COMPLETION_ASSUMED_PARKING'==mn:
  if 'LIGHT' in name:return 'paint'
  if 'LINE' in name or 'MARK' in name:return 'paint'
  return 'concrete'
 if any(x in mn for x in ['CONCRETE','WALL','SLAB','BASE','ROOF','EQUIPMENT','SELECTEDDEPTH','MALL','PASSAGE']):return 'concrete'
 if 'TREE' in name or 'FOLIAGE' in name:return 'green'
 return None
visibility={o:o.visible_get(view_layer=src.view_layers[0]) for o in src.objects}
mapping={};counts=collections.Counter();unchanged=collections.Counter()
for o in src.objects:
 c=o.copy();s.collection.objects.link(c);mapping[o]=c
 c.hide_render=o.hide_render or not visibility[o]
 if o.type=='MESH':
  if not len(o.material_slots):
   c.data=o.data.copy();c.data.materials.append(mats['stone']);counts['stone']+=1
  else:
   for i,slot in enumerate(o.material_slots):
    key=classify(o,slot.material)
    if key:
     c.material_slots[i].link='OBJECT';c.material_slots[i].material=mats[key];counts[key]+=1
    else:unchanged[slot.material.name if slot.material else 'NONE']+=1
 c['material_variant']='MOTIF_REFERENCE_20260929'
for old,c in mapping.items():
 if old.parent in mapping:c.parent=mapping[old.parent]
 for con in c.constraints:
  if hasattr(con,'target') and con.target in mapping:con.target=mapping[con.target]
for marker in src.timeline_markers:
 t=s.timeline_markers.new(marker.name,frame=marker.frame);t.camera=mapping.get(marker.camera)
s.frame_start=src.frame_start;s.frame_end=src.frame_end;s.render.fps=src.render.fps
s.camera=mapping.get(src.camera);s.frame_set(1)
s['reference']='https://www.motifla.com.tw/book-4.html'
s['note']='Material interpretation only; geometry and survey uncertainty remain unchanged. Existing special landmark colors retained.'
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True
s.render.resolution_x=1200;s.render.resolution_y=800;s.render.resolution_percentage=100
s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.65,.72,.8,1);s.world.node_tree.nodes.get('Background').inputs[1].default_value=.6
sun=bpy.data.lights.new('MOTIF_SOFT_SUN','SUN');sun.energy=2.2;sun.angle=.15
so=bpy.data.objects.new('MOTIF_SOFT_SUN',sun);s.collection.objects.link(so);so.rotation_euler=(.55,-.4,-.55)
for w in bpy.context.window_manager.windows:w.scene=s
for w in bpy.context.window_manager.windows:
 for a in w.screen.areas:
  if a.type=='VIEW_3D':a.spaces.active.shading.color_type='MATERIAL'
report={'scene':s.name,'objects_copied':len(mapping),'material_slots':dict(counts),'retained_materials':dict(unchanged),'geometry_modified':False,'external_textures':False,'reference':s['reference']}
(folder/'material_assignment_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(out/'CIVIC_MOTIF_MATERIALS_20260929.blend'))
result=report

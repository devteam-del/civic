import bpy,json
from pathlib import Path
s=bpy.context.scene
assert s.name=='CIVIC_MOTIF_MATERIALS_20260929'
base=Path(bpy.data.filepath).parent
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
green=bpy.data.materials['MOTIF_GREEN'].copy();green.name='LANDSCAPE_GREENBELT_SOIL_PLANTING'
green.diffuse_color=(.10,.19,.045,1)
r=next(n for n in green.node_tree.nodes if n.type=='VALTORGB')
r.color_ramp.elements[0].color=(.065,.055,.025,1)
r.color_ramp.elements[1].color=(.16,.27,.065,1)
green['surface_class']='greenbelt';green['extent_status']='existing estimated island extent'
p=bpy.data.materials.new('LANDSCAPE_PERMEABLE_PAVERS_PROPOSAL');p.use_nodes=True;p.diffuse_color=(.48,.47,.40,1)
n=p.node_tree.nodes;l=p.node_tree.links;bs=n.get('Principled BSDF');bs.inputs['Roughness'].default_value=.9
geo=n.new('ShaderNodeNewGeometry');brick=n.new('ShaderNodeTexBrick')
brick.inputs['Scale'].default_value=1
brick.inputs['Brick Width'].default_value=.2;brick.inputs['Row Height'].default_value=.1
brick.inputs['Mortar Size'].default_value=.004
brick.inputs['Color1'].default_value=(.46,.45,.39,1);brick.inputs['Color2'].default_value=(.56,.54,.47,1)
brick.inputs['Mortar'].default_value=(.14,.13,.105,1)
l.new(geo.outputs['Position'],brick.inputs['Vector']);l.new(brick.outputs['Color'],bs.inputs['Base Color'])
b=n.new('ShaderNodeBump');b.invert=True;b.inputs['Distance'].default_value=.004;b.inputs['Strength'].default_value=.35
l.new(brick.outputs['Fac'],b.inputs['Height']);l.new(b.outputs['Normal'],bs.inputs['Normal'])
p['surface_class']='permeable_paving_proposal';p['hydraulic_performance_verified']=False
groups={}
for label in ['GREENBELT','PERMEABLE_PAVING_PROPOSAL','MEDIAN_SURFACE_REVIEW']:
 c=bpy.data.collections.new('LANDSCAPE_'+label);s.collection.children.link(c);groups[label]=c
records=[]
for o in list(s.objects):
 if o.type!='MESH':continue
 key=None
 if o.name.startswith('SV_SONGJIANG_JIANGUO_') and 'MEDIAN' in o.name:key='GREENBELT';mat=green
 elif o.name.startswith(('CAL_GROUND_SIDEWALKS_','BLOCK_CONTEXT_SIDEWALK_')):key='PERMEABLE_PAVING_PROPOSAL';mat=p
 elif 'MEDIAN' in o.name and not o.name.startswith(('COMP_','VC_EST_')):
  groups['MEDIAN_SURFACE_REVIEW'].objects.link(o);o['surface_review']='Mixed or unverified planted/paved extent; retained for review'
 if not key:continue
 o.data=o.data.copy()
 o.data.materials.append(mat);idx=len(o.data.materials)-1
 normal_matrix=o.matrix_world.to_3x3().inverted().transposed()
 count=0
 for f in o.data.polygons:
  if (normal_matrix@f.normal).normalized().z>.7:f.material_index=idx;count+=1
 groups[key].objects.link(o)
 o['surface_class']=key;o['finish_status']='Interpretive material; not verified as-built or permeability measurement'
 records.append({'object':o.name,'class':key,'top_faces':count})
out=base/'Materials_20260930';out.mkdir(exist_ok=True)
report={'assignments':records,'counts':{k:len(c.objects) for k,c in groups.items()},'geometry_coordinates_changed':False,'note':'20x10cm paver module is a visual proposal. Permeability not measured; mixed medians remain pending.'}
(out/'landscape_surface_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(base/'CIVIC_MOTIF_LANDSCAPE_20260930.blend'))
result={'counts':report['counts'],'saved':True}

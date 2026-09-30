import bpy,json
from pathlib import Path
from mathutils import Vector
s=bpy.context.scene
assert s.name=='CIVIC_MOTIF_MATERIALS_20260929'
base=Path(bpy.data.filepath).parent
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
col=bpy.data.collections.new('LANDSCAPE_RESTORED_PHOTO_EST_20260930');s.collection.children.link(col)
chosen=[o for o in bpy.data.objects if o.type=='MESH' and (
o.name.startswith('UB_LANDSCAPE_011_018_EST_HEDGE_') or
(o.name.startswith('UB_ZZ_') and ('SHRUB_PATCH' in o.name or 'SOIL_PATCH' in o.name)) or
o.name.startswith('UB_FUDUN_CANOPY_LANDSCAPE_EST_SHRUB_'))]
existing={o.get('restored_source') for o in s.objects}
records=[]
for o in chosen:
 if o.name in existing:continue
 c=o.copy();c.name='LANDSCAPE_RESTORE_'+o.name;col.objects.link(c)
 c.matrix_world=o.matrix_world.copy();c.hide_render=False;c.hide_viewport=False
 soil='SOIL_PATCH' in o.name
 mat=bpy.data.materials['MOTIF_SOIL' if soil else 'MOTIF_GREEN']
 for slot in c.material_slots:slot.link='OBJECT';slot.material=mat
 c['restored_source']=o.name;c['surface_class']='SOIL_EST' if soil else 'SHRUB_EST'
 c['survey_verified']=False;c['integration_status']='Restored old estimated geometry; recheck against revised medians and pier positions'
 records.append({'source':o.name,'object':c.name,'class':c['surface_class'],'world_matrix_preserved':all(abs(c.matrix_world[i][j]-o.matrix_world[i][j])<1e-6 for i in range(4) for j in range(4))})
out=base/'Materials_20260930'
(out/'restored_landscape_report.json').write_text(json.dumps({'objects':records,'count':len(records),'canopy_dataset_imported':False,'limits':'Historical estimated footprints retained; current median containment and canopy/ground separation require review.'},ensure_ascii=False,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(base/'CIVIC_MOTIF_LANDSCAPE_RESTORED_20260930.blend'))
result={'restored':len(records),'shrubs':sum(r['class']=='SHRUB_EST' for r in records),'soil':sum(r['class']=='SOIL_EST' for r in records),'all_transforms_preserved':all(r['world_matrix_preserved'] for r in records)}

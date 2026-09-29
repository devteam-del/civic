"""Integrate the preserved station opening estimate into the pier comparison only."""
import bpy,json
from pathlib import Path
root=Path(bpy.data.filepath).parent/'PierPositions_20260924'
scene=bpy.data.scenes['CIVIC_PIER_XY_REVIEW_20260923']
old=bpy.data.objects['CAL_GROUND_MEDIAN_WORKING_ESTIMATED_0'];source=bpy.data.objects['UB_MEDIAN_0_WITH_STATION_UTURN_EST']
name='SV_STATION_MEDIAN_OPENING_EST'
assert name not in bpy.data.objects and old.name in scene.objects
ob=source.copy();ob.data=source.data.copy();ob.name=name
ob['source_object']=old.name;ob['geometry_source']=source.name
ob['survey_verified']=False;ob['status']='Opening existence visually confirmed; 23m cut dimension and endpoints remain estimated'
ob['source_record']='station_ground_integration_review.json'
flags={}
def read(lc):
 flags[lc.collection]=(lc.exclude,lc.hide_viewport)
 for ch in lc.children:read(ch)
read(scene.view_layers[0].layer_collection)
memo={}
def clone(c):
 if c in memo:return memo[c]
 if old not in c.all_objects[:]:return c
 nc=bpy.data.collections.new(c.name+'_STATION_GROUND');memo[c]=nc
 nc.hide_render=c.hide_render;nc.hide_viewport=c.hide_viewport
 for o in c.objects:nc.objects.link(ob if o==old else o)
 for ch in c.children:nc.children.link(clone(ch))
 return nc
for c in list(scene.collection.children):
 nc=clone(c)
 if nc!=c:scene.collection.children.unlink(c);scene.collection.children.link(nc)
if old.name in scene.collection.objects:scene.collection.objects.unlink(old);scene.collection.objects.link(ob)
inverse={v:k for k,v in memo.items()}
def restore(lc):
 src=inverse.get(lc.collection,lc.collection)
 if src in flags:lc.exclude,lc.hide_viewport=flags[src]
 for ch in lc.children:restore(ch)
for vl in scene.view_layers:restore(vl.layer_collection)
assert old.name not in scene.objects and ob.name in scene.objects
assert old.name in bpy.data.scenes['CIVIC_FULL_CORRIDOR_PRESENTATION'].objects
result={'comparison_object':ob.name,'original_preserved':old.name,'geometry_source':source.name,'existence_evidence':'2025-05 Street View visibly shows a paved vehicle opening between planted pier islands','source_url':'https://www.google.com/maps/@?api=1&map_action=pano&pano=PdYrpyY5JzRWty-6BTCaYw&heading=100&pitch=0&fov=90','supplementary_url':'https://www.google.com/maps/@?api=1&map_action=pano&pano=thep3S5iPBSW9exGL5CO_g&heading=80&pitch=0&fov=90','dimensions_status':'Existing 23m rotated cut reused provisionally; endpoints not triangulated this pass','estimated_cut_area_m2':276.43194485784545,'cut_road_coverage_fraction':1.0,'survey_verified':False,'pier_positions_changed':False,'heights_changed':False}
(root/'station_ground_integration_review.json').write_text(json.dumps(result,indent=2))

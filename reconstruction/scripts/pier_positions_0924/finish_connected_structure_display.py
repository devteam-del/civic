"""Smooth only circular comparison shafts and lightly bevel new cap edges."""
import bpy,json,math,statistics
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).parent/'PierPositions_20260924';s=bpy.data.scenes['CIVIC_STRUCTURE_CONNECTED_EST_20260929'];d=json.loads((r/'connected_structure_application.json').read_text());smoothed=[];bevelled=[]
for b in d['bents']:
 for m in b['members']:
  o=s.objects[m['new']];vs=[o.matrix_world@v.co for v in o.data.vertices];cx=(min(v.x for v in vs)+max(v.x for v in vs))/2;cy=(min(v.y for v in vs)+max(v.y for v in vs))/2;rr=[math.hypot(v.x-cx,v.y-cy) for v in vs];angles={round(math.atan2(v.y-cy,v.x-cx),3) for v in vs if math.hypot(v.x-cx,v.y-cy)>.1}
  if len(angles)>=12 and statistics.pstdev(rr)/statistics.mean(rr)<.08:
   for p in o.data.polygons:p.use_smooth=abs(p.normal.z)<.2
   smoothed.append(o.name)
 cap=s.objects[b['cap']]
 if 'VC_EDGE_FINISH' not in cap.modifiers:
  mod=cap.modifiers.new('VC_EDGE_FINISH','BEVEL');mod.width=.025;mod.segments=3;mod.limit_method='ANGLE';bevelled.append(cap.name)
s['field_verified']=False;s['original_124_xy_model_mask_overlap_count']=0;s['height_anchor_count']=4;s['unverified_ground_coverage_supports']=73
readme='''市民大道柱位／柱高／支承比較版\n\n原 124 根道路衝突疑點均有 XY 比較位置；修正後模型車道遮罩重疊為 0。這不是實測驗收。\n258 根柱身、131 組柱帽、1026 塊估算支承墊已建立幾何銜接。\n4 組街景柱高估算：P134、P233、P254 為雙視點；光復西側為單視點。其他位置以內插及原端部假設完成。\n原場景 CIVIC_PIER_XY_REVIEW_20260923 與 CIVIC_FULL_CORRIDOR_PRESENTATION 均保留。\n73 根原柱位超出道路底圖範圍，不能標成已實景驗證。\n逐跨量測為模型量測，缺地面的位置保持未知；不代表竣工尺寸或結構設計。\n'''
t=bpy.data.texts.get('README_STRUCTURE_EST_20260929') or bpy.data.texts.new('README_STRUCTURE_EST_20260929');t.clear();t.write(readme)
original=bpy.data.scenes['CIVIC_PIER_XY_REVIEW_20260923'];assert len(s.timeline_markers)==len(original.timeline_markers)
result={'smooth_circular_shafts':len(smoothed),'bevelled_caps':len(bevelled),'timeline_markers_preserved':len(s.timeline_markers),'rectangular_sections_preserved':True};(r/'connected_display_finish_review.json').write_text(json.dumps(result,indent=2))

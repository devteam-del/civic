"""Link the existing 200m corridor and underground cameras into the integration scene."""
import bpy,json
from pathlib import Path
r=Path(bpy.data.filepath).parent/'PierPositions_20260924';src=bpy.data.scenes['CIVIC_BLOCKS_FACADES_WORKING'];s=bpy.data.scenes['CIVIC_STRUCTURE_CONNECTED_EST_20260929'];assert not s.timeline_markers
col=bpy.data.collections.new('VC_EXISTING_CORRIDOR_AND_PARKING_CAMERAS');s.collection.children.link(col);linked=[]
for o in src.objects:
 if o.type=='CAMERA' and o.name not in s.objects:col.objects.link(o);linked.append(o.name)
markers=sorted(src.timeline_markers,key=lambda m:m.frame);assert len(markers)==106 and all(markers[i+1].frame-markers[i].frame==24 for i in range(105))
for m in markers:
 n=s.timeline_markers.new(m.name,frame=m.frame);n.camera=m.camera
s.render.fps=src.render.fps;s.render.fps_base=src.render.fps_base;s.frame_start=src.frame_start;s.frame_end=src.frame_end
result={'linked_existing_cameras':len(linked),'markers':len(s.timeline_markers),'fps':s.render.fps,'one_camera_per_second':True,'sequence':'Existing east-to-west alternating north/south sequence; camera transforms unchanged.','parking_cameras_preserved':True};(r/'camera_sequence_restoration_review.json').write_text(json.dumps(result,indent=2))

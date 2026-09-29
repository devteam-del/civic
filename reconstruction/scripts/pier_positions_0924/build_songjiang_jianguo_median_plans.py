"""Observed split-island topology with explicitly estimated conservative widths.
No fit to collision results; preserve the central carriageway and junction gaps.
"""
import sys,json
from pathlib import Path
from shapely.geometry import LineString,mapping,shape
root=Path(sys.argv[1]);out=Path(sys.argv[2])
segments={'WEST':['songjiang_east','west_p209_next','west_p209','p209','local_junction_west'],'EAST':['local_junction_east','west_p214_next','west_p214','p214','jianguo_west_edge']}
plans=[]
for segment,files in segments.items():
 for side,width in [('NORTH',2.8),('SOUTH',3.6)]:
  ts=[]
  for file in files:
   d=json.loads((root/(file+'_position_review.json')).read_text());ts.append(next(t for t in d['targets'] if t['id'].endswith(side)))
  xy=[t['candidate_model_xy'] for t in ts]
  poly=LineString(xy).buffer(width/2,quad_segs=12,join_style='round')
  if segment=='EAST' and side=='SOUTH':poly=poly.union(shape(json.loads((root/'jianguo_west_island_plan.json').read_text())['footprint']))
  plans.append({'name':'SV_SONGJIANG_JIANGUO_'+segment+'_'+side+'_MEDIAN_EST','footprint':mapping(poly),'z_min':0.,'z_max':.18,'estimated_width_m':width,'width_status':'Conservative visual-proportion assumption; not metrically measured or field verified.','source_records':[f+'_position_review.json' for f in files],'source_piers':[t['comparison_object'] for t in ts],'existence_evidence':'Street views show separate planted islands around the north and south pier rows, with a carriageway between them.','endpoint_status':'Ends at outermost pier plus buffer, except existing reviewed Jianguo tip. Full curb noses and local access cuts remain pending.','survey_verified':False,'topology_status':'Local junction between EAST and WEST patches left open; north-south carriageway gap left open.'})
# These are topology/proportion comparisons, not a collision clearance certificate.
a={'patches':plans,'sources':['https://www.google.com/maps/@?api=1&map_action=pano&pano=TmJaZc2pavLdf2zfcodVMA&heading=60&pitch=0&fov=90','https://www.google.com/maps/@?api=1&map_action=pano&pano=mg8uGWmROsxmOz9X-JTgZQ&heading=60&pitch=0&fov=90','https://www.google.com/maps/@?api=1&map_action=pano&pano=3Vq9E0LHU4N9sIW2U3PM2A&heading=300&pitch=0&fov=90'],'date':'2025-04','status':'Estimated modelling comparison; unresolved field-clearance flags must remain false.'}
out.write_text(json.dumps(a,indent=2));print(json.dumps([{'name':p['name'],'width':p['estimated_width_m']} for p in plans]))

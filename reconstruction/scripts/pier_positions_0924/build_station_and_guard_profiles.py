"""Estimate station outer curb profile and preserve existing entrance cutouts."""
import json,sys
from pathlib import Path
from shapely.geometry import Polygon,shape,mapping,box
from shapely.ops import unary_union
root=Path(sys.argv[1]);out=Path(sys.argv[2]);live=json.loads((root/'live_comparison_ground_footprints.json').read_text())
ns={};exec((root/'build_zhonglin_profiles.py').read_text().split('jobs=')[0].replace('root=Path(sys.argv[1]);out=Path(sys.argv[2]);live=json.loads((root/\'live_comparison_ground_footprints.json\').read_text())',''),ns);mesh=ns['mesh']
guards=json.loads(Path(sys.argv[3]).read_text());guard=unary_union([shape(o['geometry']) for o in guards['guards']]);by={o['name']:unary_union([Polygon(f).buffer(0) for f in o['faces']]) for o in live['medians']};old=by['SV_STATION_MEDIAN_OPENING_EST'];chains={'NORTH':[],'SOUTH':[]}
files=['station_footbridge_east','west_p130','p130','west_p132','p132','west_p134','station_access_west','west_p136','p136','p137','east_visible_p137','zhongshan_west_edge']
for name in files:
 for t in json.loads((root/(name+'_position_review.json')).read_text())['targets']:
  for side,off in [('NORTH',1.8),('SOUTH',-1.8)]:
   if t['id'].endswith(side):x,y=t['candidate_model_xy'];chains[side].append([x,y+off])
for fn in ['west_p132_missing_south_review.json','west_p134_missing_south_review.json']:
 for t in json.loads((root/fn).read_text())['targets']:
  x,y=t['candidate_model_xy'];chains['SOUTH'].append([x,y-1.8])
for pts in chains.values():
 pts.sort();a,b=pts[:2];m=(b[1]-a[1])/(b[0]-a[0]);pts.insert(0,[634,a[1]+m*(634-a[0])]);a,b=pts[-2:];m=(b[1]-a[1])/(b[0]-a[0]);pts.append([1023,b[1]+m*(1023-b[0])])
outer=Polygon(chains['SOUTH']+list(reversed(chains['NORTH'])));assert outer.is_valid
# Preserve the complete previously cut U-turn gap, extending its oblique edges through the enlarged profile.
from shapely.affinity import rotate
gap=rotate(box(842.5,745,865.5,815),-10,origin=(854,780))
new=old.union(outer).intersection(box(634,700,1023,870)).difference(guard.union(gap));assert new.is_valid
patches=[]
def add(source,name,g,status,extra):
 v,f=mesh(g,0,.18);patches.append({'name':name,'source_object':source,'vertices':v,'faces':f,'footprint':mapping(g),'width_status':status,'ramp_hole_fill_m2':g.intersection(guard).area,'survey_verified':False,**extra})
add('SV_STATION_MEDIAN_OPENING_EST','SV_STATION_GUARDED_PROFILE_MEDIAN_EST',new,'Estimated 1.8m shaft-centre curb allowance. Intersection endpoints and existing 23m U-turn exclusion provisional; all existing entrance guards preserved.',{'source_records':[x+'_position_review.json' for x in files],'bounds':list(new.bounds),'new_guarded_opening_area_m2':outer.intersection(guard.union(gap)).area,'estimated_west_end_x':634,'estimated_east_end_x':1023})
source='SV_JIANGUO_EAST_APRON_MEDIAN_EST';old2=by[source];cut=old2.difference(guard);add(source,'SV_JIANGUO_EAST_GUARDED_MEDIAN_EST',cut,'Restore existing estimated Jianfu parking ramp opening accidentally covered by outer apron expansion.',{'restored_opening_area_m2':old2.difference(cut).area})
data={'patches':patches,'sources':['https://www.google.com/maps/@?api=1&map_action=pano&pano=D9e1WtrxhXvTD4cHdDKjQw&heading=60&pitch=0&fov=90','https://www.google.com/maps/@?api=1&map_action=pano&pano=thep3S5iPBSW9exGL5CO_g&heading=80&pitch=0&fov=90'],'status':'Comparison estimates only. Openings inherited from model; absolute curb location and metric dimensions remain unverified.'}
out.write_text(json.dumps(data,indent=2));print(json.dumps([{k:v for k,v in p.items() if k not in ['vertices','faces','footprint']} for p in patches]))

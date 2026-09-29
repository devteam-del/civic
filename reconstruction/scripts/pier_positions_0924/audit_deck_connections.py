"""Check mapped shared endpoints against reconstructed deck footprint continuity."""
import json,sys,math
from pathlib import Path
from shapely.geometry import Polygon
from shapely.ops import unary_union
r=Path(sys.argv[1]);d=json.loads((r/'connected_deck_footprints.json').read_text());geos={o['name']:unary_union([Polygon(f).buffer(0) for f in o['faces']]) for o in d};joints=[]
for i,a in enumerate(d):
 for b in d[i+1:]:
  dist=min(math.dist(x,y) for x in a['path_endpoints'] for y in b['path_endpoints'])
  if dist<.5:
   gap=geos[a['name']].distance(geos[b['name']]);joints.append({'a':a['name'],'b':b['name'],'mapped_endpoint_distance_m':dist,'footprint_gap_m':gap,'connected_within_1cm':gap<.01})
out={'deck_objects':len(d),'mapped_shared_endpoint_pairs':len(joints),'gapped_pairs':sum(not x['connected_within_1cm'] for x in joints),'joints':joints,'scope':'Mapped shared endpoints only. Parallel carriageways and unconnected OSM endpoints not forcibly bridged. Z continuity follows the same continuous height function; not field verification.'};Path('/tmp/deck_connection_review.json').write_text(json.dumps(out,indent=2));print({k:v for k,v in out.items() if k!='joints'})

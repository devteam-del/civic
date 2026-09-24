"""Refresh the original 124-case ledger from current comparison audit; never mark field verification."""
import json
from pathlib import Path
def update(root):
 root=Path(root)
 a=json.loads((root/'current_pier_comparison_audit.json').read_text())
 d=json.loads((root/'conflict124_progress.json').read_text())
 lookup={x['pier']:x for x in a['rows']}
 for row in d['rows']:
  x=lookup[row['model_pier']]
  row['current_model_mask_clear']=x['model_mask_clear']
  if x['streetview_xy_comparison']:
   row['state']='provisional_xy_comparison_model_clearance_only' if x['model_mask_clear'] else 'provisional_xy_comparison_overlap_remaining'
   row['current_xy']=x['xy']
  row['resolved']=False;row['field_verified']=False
 d.update(provisional_xy_applied=a['suspects_with_xy_comparison'],total_xy_comparisons_including_companions=a['total_xy_comparisons'],remaining_model_mask_overlaps=a['remaining_model_mask_overlaps'],fully_resolved=0,field_verified=0)
 (root/'conflict124_progress.json').write_text(json.dumps(d,indent=2))
 (root/'pier_progress_summary.json').write_text(json.dumps({k:v for k,v in a.items() if k!='rows'},indent=2))
 return {k:v for k,v in a.items() if k!='rows'}
if __name__=='__main__':
 import sys
 update(sys.argv[1])

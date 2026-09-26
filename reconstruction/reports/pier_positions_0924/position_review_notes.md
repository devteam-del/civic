# Conflict-124 position review — 2026-09-24

Scope: prioritize the 124 ROAD_OVERLAP_REVIEW shafts. The other 117 shafts are not in this conflict queue. Column elevations, support heights and deck joining remain paused.

## Progress
- 124 suspect records retained; 121 still have no applied Street View XY comparison.
- 3 provisional XY comparisons are now in the working scene: earlier model 642, plus model 730 / visible P246 and model 732 / visible P247.
- No surveyed coordinates. No claim that all 124 conflicts are resolved.
- Original presentation objects remain intact. Working comparisons preserve every shaft vertex Z and local mesh coordinates.
- Companions, caps, bearings and decks were not relocated in this position-only round.

## Visible P246 and P247
Both labels were read directly in December 2024 Street View. P246 stands at the west end of a U-turn opening, inside a planted island, with an attached downpipe. P247 stands east of the opening in a cobbled/paved median, with a picket guard at its base.
Model 730 and 732 associations are provisional: model numbering is interpolated and is not actual pier numbering.

P246 estimate: model XY (3682.222, 416.338), delta from model 730 approximately (+6.835,+0.799) m.
P247 estimate: model XY (3711.875, 413.805), delta from model 732 approximately (+0.821,+0.998) m.
These are bearings-derived working coordinates, not survey accuracy.
Third-view perpendicular ray residuals: P246 approximately 0.029 m; P247 approximately 0.151 m. These residuals do not include shared panorama geolocation/heading errors and are not accuracy bounds.

## Ground-boundary discrepancy
The existing road-minus-median masks still overlap the P246 candidate by 3.106 m² and P247 by 2.770 m², despite the visibly island-contained shafts.
Do not force either shaft farther into the old median mask simply to make the collision report green.
Keep ground-boundary registration/geometry as an unresolved issue and review visible curbs and U-turn opening edges before adopting the comparisons.

## Street View sources
- [P247 west-side view, 43.5 degrees](https://www.google.com/maps/@?api=1&map_action=pano&pano=uKMagVCBFOMP5Zreqyt1Gg&heading=43.5&pitch=0)
- [P247 east-side view, 324.5 degrees](https://www.google.com/maps/@?api=1&map_action=pano&pano=jI0jLIDZ4n5L8HGK8J0vrw&heading=324.5&pitch=0)
- [P247 third view, 73.8 degrees](https://www.google.com/maps/@?api=1&map_action=pano&pano=akMOb0qFNqnQ6f7z51SldA&heading=73.8&pitch=0)
- [P246 view, 298 degrees](https://www.google.com/maps/@?api=1&map_action=pano&pano=akMOb0qFNqnQ6f7z51SldA&heading=298&pitch=0)
- [Readable P246, 330 degrees](https://www.google.com/maps/@?api=1&map_action=pano&pano=aBo2wQlsJzMEiNZ9NQDZew&heading=330&pitch=0)
- [P246 third view, 289.2 degrees](https://www.google.com/maps/@?api=1&map_action=pano&pano=uKMagVCBFOMP5Zreqyt1Gg&heading=289.2&pitch=0)

## Reproduction
Run triangulate_p246.py or triangulate_p247.py with an output JSON path using pyproj. Apply scripts consume the matching enriched position_review JSON next to the blend in PierPositions_20260924; they reject repeated application and the wrong scene.
The ledger generator requires the preceding Underbridge_20260922/pier_road_overlap_review.json.
Before application preserve a local blend copy. No blend files or Street View images are included in the public backup.

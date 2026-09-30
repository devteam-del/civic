# P246/P247 paired piers and local median comparison

Street View confirmed P246 and P247 on the roadside shafts. Opposite north-side shafts were matched by same-span geometry and island sequence; their own labels are unread. Each north shaft has two centered bearings and a third-view check, all from December 2024.

Estimated pair spacing is 12.126m at P246 and 11.824m at P247, compared with approximately 6m in the original interpolated pairs. These are working estimates, not survey dimensions.

The local median comparison replaces only model X3662–3732. It leaves an estimated U-turn opening from X3687 to3705.5, rounds the island tips using polygon segments and keeps the existing0.18m curb height. Island tips, lateral curb positions and clearances are proportion estimates from Street View relative to retained 2m shaft diameter, NOT separately measured curb points. They must not be represented as exact real-world boundaries. No changes are extrapolated along the full corridor.

All four shafts fit inside the comparison median, with modeled edge clearances0.58–0.80m. This is a construction check of an estimated alternative, not independent confirmation of traffic safety or as-built accuracy. The median mesh has zero nonmanifold edges and zero zero-area faces. A local overhead render was inspected. Shaft Z and local geometry remain unchanged; caps, bearings and deck geometry remain deferred.

The 124-suspect queue still has121 without an applied Street View position comparison. Five shafts now have XY comparisons in total, including the two north companions outside that queue. No field-survey verification is claimed. Original objects remain in the presentation scene and a local pre-change blend backup exists.

Reproduce with build_p246_247_median.py INPUT_FOOTPRINTS P246_NORTH_JSON P247_NORTH_JSON OUTPUT_JSON (Shapely2.1). Apply using apply_pair_median_comparison.py in the named working scene. The first mesh attempt was rejected before scene replacement because unconstrained triangulation left boundary edges; constrained triangulation corrected this. Two unlinked retry objects retain UNAPPLIED_RETRY names and are not scene geometry.

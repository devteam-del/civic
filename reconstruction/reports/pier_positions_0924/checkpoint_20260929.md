# Connected structure comparison checkpoint

This checkpoint completes a reversible **model-geometry comparison**, not field verification.

- 124/124 original road-overlap suspects have XY comparisons; the current estimated road/median mask test reports zero overlaps.
- 258 shafts, 131 working bent caps and 1,026 estimated bearing pads are geometrically connected. Shaft XY is unchanged by the height step.
- Four Street View height anchors: three two-view estimates and one single-view estimate. All intervening heights are interpolated; terminal heights retain the prior assumption.
- Contact-centre and closed-mesh checks pass. The 28 mapped shared deck-endpoint pairs have no plan gap within 1 cm.
- Existing 133 cameras and the 106-marker, 24 fps east-to-west sequence are linked into the new scene. Underground cameras remain available.
- 252 candidate support spans measured in the model; 108 have partial ground-data gaps and 31 exceed 60 m. These remain flagged, not certified.
- 73 original supports outside road-mask coverage are not declared conflict-free in reality.

Scene: `CIVIC_STRUCTURE_CONNECTED_EST_20260929`. The original XY and presentation scenes are preserved. Raw meshes, blend files and render images stay local.

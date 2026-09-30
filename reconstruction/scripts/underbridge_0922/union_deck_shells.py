import sys,json
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import make_valid,constrained_delaunay_triangles,set_precision
d=json.load(open(sys.argv[1]));parts=[]
for o in d['decks']:
    parts.extend([make_valid(Polygon(f)) for f in o['faces'] if len(f)>=3])
original=unary_union(parts)
g=set_precision(original,.001).simplify(.001,preserve_topology=True)
polys=[g] if g.geom_type=='Polygon' else list(g.geoms)
verts=[];faces=[];index={}
def vi(x,y,z):
    k=(round(x,10),round(y,10),round(z,10))
    if k not in index:index[k]=len(verts);verts.append(k)
    return index[k]
for p in polys:
    for tri in constrained_delaunay_triangles(p).geoms:
        pts=list(tri.exterior.coords)[:-1]
        area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(pts,pts[1:]+pts[:1]))
        if area<0:pts.reverse()
        faces.append([vi(x,y,8.) for x,y in pts]);faces.append([vi(x,y,7.65) for x,y in reversed(pts)])
    for ring in [p.exterior,*p.interiors]:
        pts=list(ring.coords)
        # Orient outer ring CCW, holes CW so side normals point outside solid.
        desired=ring==p.exterior
        if ring.is_ccw!=desired:pts.reverse()
        for a,b in zip(pts,pts[1:]):faces.append([vi(*a,7.65),vi(*b,7.65),vi(*b,8.),vi(*a,8.)])
edges={}
for f in faces:
    for a,b in zip(f,f[1:]+f[:1]):edges[tuple(sorted((a,b)))]=edges.get(tuple(sorted((a,b))),0)+1
out={'vertices':verts,'faces':faces,'report':{'input_decks':len(d['decks']),'connected_components':len(polys),'polygon_areas_m2':[p.area for p in polys],'nonmanifold_edges':sum(n!=2 for n in edges.values()),'scope':'Union of overlapping existing deck footprints at unchanged estimated top 8m and bottom 7.65m; no gaps bridged, no ramp elevations inferred','real_world_verified':False}}
json.dump(out,open(sys.argv[2],'w'));print(json.dumps(out['report']))

"""Zerlegt Malefisenta.stl in drei Teile mit Sechskant-Steckzapfen.

Teile:
  1_Robe_unten.stl      Robe mit Schleppe, zwei Zapfen oben
  2_Oberkoerper.stl     Oberkoerper mit Armen und Aermeln, zwei Loecher unten, Zapfen am Hals
  3_Kopf.stl            Kopf mit Hoernern und Kragen, Loch unten
  Toleranztest_*.stl    kleiner Testzapfen und Testloch zum Pruefen der Passung

Benoetigt: pip install trimesh manifold3d shapely numpy
Aufruf:    python teile_bauen.py
"""
import os

import manifold3d as m3
import numpy as np
import trimesh
from shapely.geometry import Polygon, box
from shapely.ops import polylabel, unary_union

HIER = os.path.dirname(os.path.abspath(__file__))
QUELLE = os.path.join(HIER, "Malefisenta.stl")
ZIEL = os.path.join(HIER, "Teile")

Z_TAILLE = 54.0   # Schnitt unter den Aermeln
Z_HALS = 122.5    # Schnitt am Hals, ohne lose Kragenspitzen

SPIEL = 0.17      # Spiel am Sechskant-Umkreis (~0.15 mm an den Flaechen)
WAND = 1.2        # Mindestwand um Zapfen bzw. Loch

# Zapfen: Umkreisradius, Laenge. Loch ist 0.5 mm tiefer, damit die Flaechen sauber schliessen.
TAILLE_R, TAILLE_L = 3.5, 7.0
HALS_R, HALS_L = 2.4, 4.5


def zu_manifold(t):
    return m3.Manifold(m3.Mesh(vert_properties=np.asarray(t.vertices, np.float32),
                               tri_verts=np.asarray(t.faces, np.uint32)))


def zu_trimesh(m):
    mesh = m.to_mesh()
    return trimesh.Trimesh(mesh.vert_properties[:, :3], mesh.tri_verts, process=True)


def welt_polygon(t, z):
    """Querschnitt bei Hoehe z in Weltkoordinaten (x, y)."""
    s = t.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    p, T = s.to_2D()
    teile = []
    for poly in p.polygons_full:
        xy = trimesh.transform_points(np.c_[np.array(poly.exterior.coords), np.zeros(len(poly.exterior.coords))], T)
        teile.append(Polygon(xy[:, :2]).buffer(0))
    return unary_union(teile)


def zapfen_position(t, z, r, laenge, bereich=None):
    """Punkt mit maximalem Abstand zum Rand, der ueber Verankerung und Lochtiefe Wand WAND hat."""
    schnitte = [welt_polygon(t, z + dz) for dz in np.linspace(-1, laenge + 0.5, 7)]
    innen = schnitte[0]
    for s in schnitte[1:]:
        innen = innen.intersection(s)
    if bereich is not None:
        innen = innen.intersection(bereich)
    if innen.geom_type != "Polygon":
        innen = max(innen.geoms, key=lambda g: g.area)
    p = polylabel(innen, tolerance=0.05)
    abstand = innen.boundary.distance(p)
    assert abstand >= r + SPIEL + WAND, f"zu wenig Wand bei z={z}: {abstand:.2f} mm"
    return p.x, p.y, abstand


def sechskant(r, h):
    return m3.Manifold.cylinder(h, r, r, circular_segments=6)


def zapfen(x, y, z, r, laenge):
    # 1 mm im Teil verankert, Spitze 0.6 mm angefast
    schaft = sechskant(r, laenge + 1 - 0.6).translate((0, 0, -1))
    spitze = m3.Manifold.cylinder(0.6, r, r - 0.5, circular_segments=6).translate((0, 0, laenge - 0.6))
    return (schaft + spitze).translate((x, y, z))


def loch(x, y, z, r, laenge):
    r = r + SPIEL
    schaft = sechskant(r, laenge + 0.5 + 0.01).translate((0, 0, -0.01))
    fase = m3.Manifold.cylinder(0.5, r + 0.5, r, circular_segments=6).translate((0, 0, -0.01))
    return (schaft + fase).translate((x, y, z))


def aufs_bett(t, z_unten):
    t.apply_translation([-t.bounds[:, 0].mean(), -t.bounds[:, 1].mean(), -z_unten])
    return t


def main():
    t = trimesh.load(QUELLE)
    t = max(t.split(only_watertight=False), key=lambda c: len(c.faces))  # Mini-Splitter entfernen
    figur = zu_manifold(t)

    # Zwei Zapfen an der Taille, je einer links und rechts der Mitte (verhindert Verdrehen)
    taille = welt_polygon(t, Z_TAILLE)
    minx, miny, maxx, maxy = taille.bounds
    mitte_y = taille.centroid.y
    taille_zapfen = [zapfen_position(t, Z_TAILLE, TAILLE_R, TAILLE_L, box(minx, y0, maxx, y1))
                     for y0, y1 in ((miny, mitte_y), (mitte_y, maxy))]
    hals_zapfen = zapfen_position(t, Z_HALS, HALS_R, HALS_L)
    for name, (x, y, a) in [("Taille links", taille_zapfen[0]), ("Taille rechts", taille_zapfen[1]),
                            ("Hals", hals_zapfen)]:
        print(f"{name}: x={x:.1f} y={y:.1f}, Platz bis Rand {a:.1f} mm")

    oben, unten = figur.split_by_plane((0, 0, 1), Z_TAILLE)
    kopf, koerper = oben.split_by_plane((0, 0, 1), Z_HALS)

    for x, y, _ in taille_zapfen:
        unten = unten + zapfen(x, y, Z_TAILLE, TAILLE_R, TAILLE_L)
        koerper = koerper - loch(x, y, Z_TAILLE, TAILLE_R, TAILLE_L)
    x, y, _ = hals_zapfen
    koerper = koerper + zapfen(x, y, Z_HALS, HALS_R, HALS_L)
    kopf = kopf - loch(x, y, Z_HALS, HALS_R, HALS_L)

    os.makedirs(ZIEL, exist_ok=True)
    teile = {
        "1_Robe_unten.stl": aufs_bett(zu_trimesh(unten), 0),
        "2_Oberkoerper.stl": aufs_bett(zu_trimesh(koerper), Z_TAILLE),
        "3_Kopf.stl": aufs_bett(zu_trimesh(kopf), Z_HALS),
    }

    # Toleranztest: Klotz mit Taillen-Zapfen und Klotz mit passendem Loch
    klotz = m3.Manifold.cube((14, 14, 4)).translate((-7, -7, 0))
    teile["Toleranztest_Zapfen.stl"] = zu_trimesh(klotz + zapfen(0, 0, 4, TAILLE_R, TAILLE_L))
    teile["Toleranztest_Loch.stl"] = zu_trimesh(
        m3.Manifold.cube((14, 14, 10)).translate((-7, -7, 0)) - loch(0, 0, 0, TAILLE_R, TAILLE_L))

    for name, teil in teile.items():
        assert teil.is_watertight, name
        teil.export(os.path.join(ZIEL, name))
        g = teil.extents
        print(f"{name}: {g[0]:.0f} x {g[1]:.0f} x {g[2]:.0f} mm, {teil.volume / 1000:.1f} cm3, "
              f"{len(teil.split(only_watertight=False))} Koerper")


if __name__ == "__main__":
    main()

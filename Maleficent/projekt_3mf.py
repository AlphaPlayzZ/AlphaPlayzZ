"""Packt die Einzelteile aus Teile/ in eine 3MF-Projektdatei mit einer Platte pro Druck.

Format wie OrcaSlicer/Bambu Studio es speichert, damit Anycubic Slicer Next (Orca-Basis)
die Platten, Namen und Stuetz-/Brim-Einstellungen pro Objekt uebernimmt.

Aufruf: python projekt_3mf.py   (nach teile_bauen.py)
"""
import os
import zipfile

import numpy as np
import trimesh

HIER = os.path.dirname(os.path.abspath(__file__))
TEILE = os.path.join(HIER, "Teile")
ZIEL = os.path.join(HIER, "Maleficent_Teile.3mf")

BETT = 250.0                 # Kobra S1: 250 x 250 mm
PLATTEN_ABSTAND = BETT * 1.2  # Orca legt Platten mit 1/5 Bettbreite Luecke nebeneinander

STUETZEN = {"enable_support": "1", "support_type": "tree(auto)", "brim_type": "outer_only", "brim_width": "5"}

# Platte: (Name, [(Datei, Objektname, Einstellungen, Versatz auf der Platte in mm)])
PLATTEN = [
    ("1 Toleranztest", [("Toleranztest_Zapfen.stl", "Toleranztest Zapfen", {}, (-12, 0)),
                        ("Toleranztest_Loch.stl", "Toleranztest Loch", {}, (12, 0))]),
    ("2 Kopf", [("3_Kopf.stl", "Kopf", STUETZEN, (0, 0))]),
    ("3 Oberkoerper", [("2_Oberkoerper.stl", "Oberkoerper", STUETZEN, (0, 0))]),
    ("4 Robe", [("1_Robe_unten.stl", "Robe unten", {}, (0, 0))]),
]

NS = ('xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
      'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
      'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p"')
MODEL_REL = "http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"
EINHEIT = "1 0 0 0 1 0 0 0 1 0 0 0"


def spalten(anzahl):
    # wie compute_colum_count() in OrcaSlicer
    wert = np.sqrt(anzahl)
    gerundet = round(wert)
    return gerundet + 1 if wert > gerundet else gerundet


def platten_mitte(index, cols):
    zeile, spalte = divmod(index, cols)
    return spalte * PLATTEN_ABSTAND + BETT / 2, -zeile * PLATTEN_ABSTAND + BETT / 2


def mesh_xml(mesh):
    v = "\n".join(f'     <vertex x="{x:.4f}" y="{y:.4f}" z="{z:.4f}"/>' for x, y, z in mesh.vertices)
    t = "\n".join(f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in mesh.faces)
    return f"    <mesh>\n    <vertices>\n{v}\n    </vertices>\n    <triangles>\n{t}\n    </triangles>\n    </mesh>\n"


def main():
    cols = spalten(len(PLATTEN))
    objekte = []  # (main_id, sub_id, pfad, name, einstellungen, transform, platte)
    dateien = {}
    for p_index, (_, teile) in enumerate(PLATTEN):
        mx, my = platten_mitte(p_index, cols)
        for datei, name, einstellungen, (dx, dy) in teile:
            mesh = trimesh.load(os.path.join(TEILE, datei))
            b = mesh.bounds
            mesh.apply_translation([-(b[0, 0] + b[1, 0]) / 2, -(b[0, 1] + b[1, 1]) / 2, -b[0, 2]])
            k = len(objekte) + 1
            sub_id, main_id = 2 * k - 1, 2 * k
            pfad = f"/3D/Objects/object_{k}.model"
            dateien[pfad[1:]] = (
                f'<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" {NS}>\n'
                f' <metadata name="BambuStudio:3mfVersion">1</metadata>\n <resources>\n'
                f'  <object id="{sub_id}" p:UUID="{k:08x}-81cb-4c03-9d28-80fed5dfa1dc" type="model">\n'
                f"{mesh_xml(mesh)}  </object>\n </resources>\n <build/>\n</model>\n")
            transform = f"1 0 0 0 1 0 0 0 1 {mx + dx:.3f} {my + dy:.3f} 0"
            objekte.append((main_id, sub_id, pfad, name, einstellungen, transform, p_index))

    ressourcen = "".join(
        f'  <object id="{m}" p:UUID="{m:08x}-61cb-4c03-9d28-80fed5dfa1dc" type="model">\n'
        f'   <components>\n    <component p:path="{p}" objectid="{s}" '
        f'p:UUID="{m:04x}0000-b206-40ff-9872-83e8017abed1" transform="{EINHEIT}"/>\n   </components>\n  </object>\n'
        for m, s, p, *_ in objekte)
    build = "".join(
        f'  <item objectid="{m}" p:UUID="{m:08x}-b1ec-4553-aec9-835e5b724bb4" transform="{t}" printable="1"/>\n'
        for m, _, _, _, _, t, _ in objekte)
    dateien["3D/3dmodel.model"] = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" {NS}>\n'
        ' <metadata name="Application">BambuStudio-1.10.0</metadata>\n'
        ' <metadata name="BambuStudio:3mfVersion">1</metadata>\n'
        ' <metadata name="Title">Maleficent in Einzelteilen</metadata>\n'
        f" <resources>\n{ressourcen} </resources>\n"
        f' <build p:UUID="2c7c17d8-22b5-4d84-8835-1976022ea369">\n{build} </build>\n</model>\n')

    rels = "".join(f'  <Relationship Target="{p}" Id="rel-{i + 1}" Type="{MODEL_REL}"/>\n'
                   for i, (_, _, p, *_) in enumerate(objekte))
    dateien["3D/_rels/3dmodel.model.rels"] = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n{rels}</Relationships>\n')

    cfg = ['<?xml version="1.0" encoding="UTF-8"?>', "<config>"]
    for m, s, _, name, einstellungen, _, _ in objekte:
        cfg.append(f'  <object id="{m}">')
        cfg.append(f'    <metadata key="name" value="{name}"/>')
        cfg.append('    <metadata key="extruder" value="1"/>')
        cfg += [f'    <metadata key="{k}" value="{v}"/>' for k, v in einstellungen.items()]
        cfg.append(f'    <part id="{s}" subtype="normal_part">')
        cfg.append(f'      <metadata key="name" value="{name}"/>')
        cfg.append('      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>')
        cfg.append("    </part>")
        cfg.append("  </object>")
    for p_index, (p_name, _) in enumerate(PLATTEN):
        cfg += ["  <plate>",
                f'    <metadata key="plater_id" value="{p_index + 1}"/>',
                f'    <metadata key="plater_name" value="{p_name}"/>',
                '    <metadata key="locked" value="false"/>']
        for m, *_, platte in objekte:
            if platte == p_index:
                cfg += ["    <model_instance>",
                        f'      <metadata key="object_id" value="{m}"/>',
                        '      <metadata key="instance_id" value="0"/>',
                        f'      <metadata key="identify_id" value="{100 + m}"/>',
                        "    </model_instance>"]
        cfg.append("  </plate>")
    cfg.append("</config>")
    dateien["Metadata/model_settings.config"] = "\n".join(cfg) + "\n"

    dateien["[Content_Types].xml"] = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
        ' <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
        ' <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>\n'
        ' <Default Extension="png" ContentType="image/png"/>\n'
        ' <Default Extension="gcode" ContentType="text/x.gcode"/>\n</Types>\n')
    dateien["_rels/.rels"] = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        f' <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="{MODEL_REL}"/>\n</Relationships>\n')

    reihenfolge = ["[Content_Types].xml", "_rels/.rels", "3D/3dmodel.model", "3D/_rels/3dmodel.model.rels",
                   "Metadata/model_settings.config"]
    reihenfolge += sorted(k for k in dateien if k not in reihenfolge)
    with zipfile.ZipFile(ZIEL, "w", zipfile.ZIP_DEFLATED) as z:
        for name in reihenfolge:
            z.writestr(name, dateien[name])
    print(f"{ZIEL}: {len(PLATTEN)} Platten, {len(objekte)} Objekte, {os.path.getsize(ZIEL) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()

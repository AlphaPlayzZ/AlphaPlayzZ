# CLAUDE.md – 3D-Druck-Werkstatt

Dieses Repo ist die Werkstatt für 3D-Druck-Projekte von AlphaPlayzZ. Du arbeitest lokal auf dem PC
(Windows, starke CPU, RTX 4080). Antworte auf Deutsch, locker und direkt.

## Hardware und Software beim Nutzer

- **Drucker:** Anycubic Kobra S1 Combo mit ACE Pro (4 Farben, Trocknung max. 24 h am Stück), Bett 250 × 250 × 250 mm, Düse 0,4 mm
- **Slicer:** Anycubic Slicer Next (basiert auf OrcaSlicer); der Nutzer startet Drucke selbst aus dem Slicer
- **Blender** mit dem Add-on **Blender MCP** (MCP-Server `blender`, über `uvx blender-mcp`)
- **SolidCraft** (Open-Source-CAD wie Fusion 360, MCP-Server `solidcraft`, über `solidcraft-cli mcp`)

Prüfe zu Beginn einer Sitzung mit `/mcp`, ob `blender` und `solidcraft` verbunden sind. Falls nicht:
- Blender: Blender öffnen, N drücken, Reiter **BlenderMCP**, **Connect** klicken.
- SolidCraft: App öffnen; `solidcraft-cli mcp` verbindet sich dann mit dem laufenden Fenster.
- Fehlt ein Server ganz: `claude mcp add blender -- uvx blender-mcp` bzw. `claude mcp add solidcraft -- solidcraft-cli mcp`.

Der Nutzer schaut am Monitor live zu. Arbeite deshalb im **offenen** Blender- bzw. SolidCraft-Fenster
(nicht headless), damit er sieht, was passiert, und mach nach wichtigen Schritten einen Screenshot zur Kontrolle.

## Welches Werkzeug wofür

| Aufgabe | Werkzeug |
|---|---|
| Technische Teile mit Maßen: Sockel, Halter, Boxen, Clips, Ersatzteile | **SolidCraft** (parametrisch, Skizze → Extrusion → Fase/Rundung) |
| Figuren, organische Formen, STL-Dateien bearbeiten, zerteilen, reparieren, Renderings | **Blender** |
| Zerteilen mit Steckzapfen, 3MF mit Platten bauen | Python-Skripte in `Maleficent/` (als Vorlage für neue Projekte) |

Ehrlich bleiben: Detailreiches Sculpting (Gesichter, Stofffalten) kannst du über Code nur begrenzt.
Schlag dann vor, eine Vorlage zu nehmen (eigene STL, MakerWorld/Printables, KI-Generator wie Meshy) und sie druckfertig zu machen.

## Regeln fürs Druckbare

- Ein Teil muss aufs Bett passen (max. 250 × 250 × 250 mm, besser 5 mm Rand lassen).
- Wände mindestens 1,2 mm (3 Linien), dünne Stäbe ab etwa 3 mm.
- Überhänge über 45° vermeiden oder Tree-Stützen einplanen. Teile so legen, dass die größte flache Seite unten ist.
- Jedes Mesh muss geschlossen (watertight) sein und darf keine losen Splitter haben. Prüfe das vor dem Export.
- **Lieber mehrere einfarbige Teile als ein langer Mehrfarbdruck.** Der Nutzer hatte einen 33-h-Mehrfarbdruck,
  der nach 31 h abgebrochen ist (Trockner aus nach 24 h, Filament gebrochen, Abfallschacht voll, Düse verstopft).
  Mehrfarbig nur, wenn es wenige Farbwechsel sind und der Druck unter etwa 20 h bleibt.
- Steckverbindungen: Sechskant-Zapfen (verdrehsicher), etwa 0,15 mm Spiel an den Flächen,
  Loch 0,5 mm tiefer als der Zapfen, Zapfenspitze und Lochkante leicht anfasen. Immer einen kleinen Toleranztest mitliefern.

## Lieferformat

- Pro Projekt einen Ordner, zum Beispiel `Maleficent/`, mit Unterordner `Teile/` für die STLs und einer kurzen `README.md` (Teile, Farben, Druckeinstellungen, Zusammenbau).
- Zusätzlich eine **3MF mit einer Platte pro Druck** (Vorbild: `Maleficent/projekt_3mf.py`).
  Der Nutzer öffnet sie mit „Projekt öffnen“ und druckt die Platten nacheinander.
  Stützen und Brim pro Objekt im 3MF setzen, wenn ein Teil sie braucht.
- Skripte, die Dateien erzeugen, mit ins Repo legen, damit man sie später anpassen kann.
- Nach dem Erzeugen: Renderings bzw. Screenshots von allen Seiten anschauen, bevor du sagst, dass es fertig ist.
  Sag klar, was geprüft ist und was nicht (zum Beispiel „noch nicht gedruckt“).

## Git

- Arbeite auf einem eigenen Branch, nicht direkt auf `main`. Commit-Nachrichten auf Deutsch.
- Große Binärdateien (STL/3MF) sind ok. Über 100 MB passt GitHub nicht, dann vorher fragen.

## Bisherige Projekte

- `Maleficent/`: Figur aus `Malefisenta.stl` (Blender-Export, 137 × 175 × 150 mm), zerteilt in Robe,
  Oberkörper und Kopf mit Sechskant-Zapfen (`teile_bauen.py`) plus 3MF mit 4 Platten (`projekt_3mf.py`).
  Noch nicht im Slicer geöffnet und noch nicht gedruckt.
  Ideen für später: Sockel bzw. Ständer, Stab mit grüner Kugel, Rabe Diablo.

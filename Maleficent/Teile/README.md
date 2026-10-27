# Maleficent in Einzelteilen

Aus `../Malefisenta.stl` erzeugt mit `../teile_bauen.py`. Alle Teile liegen schon richtig herum auf dem Druckbett (Schnittfläche unten) und lassen sich einzeln in einer Farbe drucken.

| Datei | Größe (mm) | Verbindung | Farbe (Vorschlag) |
|---|---|---|---|
| `1_Robe_unten.stl` | 137 × 175 × 61 | 2 Sechskant-Zapfen oben | Schwarz |
| `2_Oberkoerper.stl` | 33 × 129 × 73 | 2 Löcher unten, 1 Zapfen am Hals | Schwarz oder Lila |
| `3_Kopf.stl` | 20 × 27 × 27 | 1 Loch unten | Schwarz (Gesicht grün bemalen) oder Hautfarbe |
| `Toleranztest_Zapfen.stl` / `Toleranztest_Loch.stl` | 14 × 14 × 10 | Testpassung | egal |

## Zusammenbau

Die Zapfen sind sechseckig, damit sich nichts verdrehen kann. Das Spiel beträgt etwa 0,15 mm.

- **Stecken:** Den Zapfen mit leichtem Druck einschieben. Sitzt er zu stramm, den Zapfen kurz mit Schleifpapier abziehen.
- **Kleben:** Einen Tropfen Sekundenkleber-Gel ins Loch geben und zusammenstecken.

Am besten druckst du zuerst die beiden Toleranztest-Teile (etwa 10 Minuten). Daran siehst du, ob die Passung auf deinem Drucker stramm, locker oder zu eng ist.

## Druckeinstellungen (Kobra S1 / Anycubic Slicer Next)

- PLA, Schichthöhe 0,12–0,16 mm, 2–3 Wände, 10–15 % Infill (Gyroid)
- **Robe:** keine Stützen nötig, Brim an
- **Oberkörper:** Tree-Stützen (nur „Auf Druckbett“ reicht oft) für Ärmel und Hände, Brim an
- **Kopf:** Tree-Stützen für Kinn und Kragenspitzen; Brim an, weil die Standfläche klein ist

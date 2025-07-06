# LaTeX Leseeffekt Format - Dokumentation

## Überblick

Dieses Format ermöglicht es, LaTeX-Texte mit Voiceover und interaktiven Highlights zu versehen. Es kombiniert mathematische Texte mit gesprochenen Erklärungen und visuellen Hervorhebungen.

## Grundstruktur

```
LaTeX-Text mit <voice>-Tags und <hi>-Tags

===HIGHLIGHTS===
hi1: Erklärung zu Highlight 1
hi2: Erklärung zu Highlight 2
...
```

## 1. Voice-Tags

### Syntax
```xml
<voice: 'Gesprochener Text'>
```

### Verwendung
Voice-Tags definieren, was parallel zum visuellen Text gesprochen wird.

### Beispiel
```xml
Es sei $f: [a,b] \rightarrow \mathbb{R}$ eine stetige Funktion.<voice: 'Gegeben sei eine stetige Funktion f von a bis b.'>
```

### Regeln
- Verwende einfache Anführungszeichen `'` um den gesprochenen Text
- Kann auch doppelte Anführungszeichen `"` verwenden
- Voice-Tags werden in der Reihenfolge ihres Auftretens abgespielt und zwar gleichzeitig zum erscheinen des Latex Textes der davor steht
- Der gesprochene Text kann vom LaTeX-Text abweichen

## 2. Highlight-Tags

### Syntax
```xml
<hi1>Zu highlightender Text</hi1>
```

### Verwendung
Highlight-Tags markieren Bereiche, die später visuell hervorgehoben werden.

### Beispiel
```xml
Eine <hi1>stetige</hi1> Funktion ist <hi2>differenzierbar</hi2>.
```

### Regeln
- Nummerierung: `hi1`, `hi2`, `hi3`, ...
- Jedes Highlight benötigt einen öffnenden und schließenden Tag
- Highlights können einzelne Wörter, Formeln oder ganze Sätze umfassen

## 3. Highlight-Erklärungen

### Syntax
```
===HIGHLIGHTS===
hi1: Erklärung zu Highlight 1
hi2: Erklärung zu Highlight 2
```

### Verwendung
Im `===HIGHLIGHTS===` Bereich wird definiert, was bei jedem Highlight gesprochen wird.

### Beispiel
```
===HIGHLIGHTS===
hi1: Stetigkeit ist eine fundamentale Eigenschaft
hi2: Differenzierbarkeit baut auf Stetigkeit auf
```

## 4. Verschachtelte Highlights

### Konzept
Ein Text kann zu mehreren Highlights gehören.

### Syntax
```xml
<hi2><hi3>stetige</hi3></hi2>
```

### Bedeutung
- Das Wort "stetige" gehört sowohl zu `hi2` als auch zu `hi3`
- Beide Highlights werden nacheinander abgespielt
- Ermöglicht mehrschichtige Erklärungen

### Beispiel
```xml
Eine <hi1><hi2>stetige</hi2></hi1> Funktion.

===HIGHLIGHTS===
hi1: Grundlegende Funktionseigenschaften
hi2: Stetigkeit im Detail
```

## 5. Verteilte Highlights

### Konzept
Ein Highlight kann mehrere nicht-zusammenhängende Bereiche umfassen.

### Syntax
```xml
<hi1>Begriff1</hi1> ... Text dazwischen ... <hi1>Begriff2</hi1>
```

### Bedeutung
- Beide Begriffe werden gleichzeitig hervorgehoben
- Ermöglicht thematische Verbindungen

### Beispiel
```xml
Eine <hi1>stetige</hi1> und <hi1>differenzierbare</hi1> Funktion.

===HIGHLIGHTS===
hi1: Diese beiden Eigenschaften gehören eng zusammen
```

## 6. Kombinierte Highlights

### Konzept
Verschachtelte UND verteilte Highlights kombinieren.

### Beispiel
```xml
Eine <hi1><hi2>stetige</hi2></hi1> und <hi1>differenzierbare</hi1> Funktion.

===HIGHLIGHTS===
hi1: Grundlegende Funktionseigenschaften
hi2: Stetigkeit als Voraussetzung
```

## 7. Parsing-Regeln

### Reihenfolge der Verarbeitung
1. **Voice-Tags parsen**: Extrahiere alle `<voice: '...'>` Tags
2. **Highlight-Tags parsen**: Extrahiere alle `<hi1>...</hi1>` Tags
3. **LaTeX-Text bereinigen**: Entferne Tags für LaTeX-Rendering
4. **Highlight-Zuordnungen erstellen**: Mappe Tags zu Textpositionen
5. **Highlight-Erklärungen parsen**: Extrahiere `===HIGHLIGHTS===` Bereich

### Verschachtelung auflösen
```xml
<hi2><hi3>stetige</hi3></hi2>
```
wird zu:
- Position von "stetige" → [hi2, hi3]
- Beide Highlights werden nacheinander abgespielt

### Verteilung sammeln
```xml
<hi1>Begriff1</hi1> ... <hi1>Begriff2</hi1>
```
wird zu:
- hi1 → [Position_Begriff1, Position_Begriff2]
- Beide Positionen werden gleichzeitig hervorgehoben

## 8. Praktische Tipps

### Voiceover-Texte
- Verwende natürliche, gesprochene Sprache
- Erkläre mathematische Symbole ausführlich
- Passe das Tempo an die Visualisierung an

### Highlight-Platzierung
- Setze Highlights genau um die relevanten Begriffe
- Verwende verschachtelte Highlights für verschiedene Erklärungsebenen
- Nutze verteilte Highlights für thematische Verbindungen

### Nummerierung
- Verwende aufsteigende Nummerierung: hi1, hi2, hi3, ...
- Plane die Reihenfolge der Highlights im Voraus
- Lasse Lücken für spätere Einfügungen

## 9. Vollständiges Beispiel

```xml
Es sei <hi1>$f: [a,b] \rightarrow \mathbb{R}$</hi1> eine <hi2><hi3>stetige</hi3></hi2> <hi2>Funktion</hi2>.<voice: 'Gegeben sei eine stetige Funktion f von a bis b.'> Wir definieren <hi4>$F:[a,b] \rightarrow \mathbb{R}$</hi4> durch <hi5>\[ F(x)=\int_a^x f(t) dt.\]</hi5><voice: 'Wir definieren F durch das Integral von a bis x.'> Dann ist <hi4>$F$</hi4> <hi2><hi6>differenzierbar</hi6></hi2> und es gilt <hi7><hi4>$F'$</hi4>=<hi1>$f$</hi1></hi7>.<voice: 'Dann ist F differenzierbar und ihre Ableitung ist f.'>

===HIGHLIGHTS===
hi1: Die ursprüngliche Funktion f
hi2: Grundlegende Funktionseigenschaften
hi3: Stetigkeit als Voraussetzung
hi4: Die Stammfunktion F
hi5: Das definierende Integral
hi6: Differenzierbarkeit der Stammfunktion
hi7: Die Kernaussage des Hauptsatzes
```

## 10. Animationsverhalten

### Voice-Tags
- Werden in der Reihenfolge ihres Auftretens abgespielt
- Während des Voiceovers läuft der Leseeffekt
- Timing wird automatisch an die Voiceover-Dauer angepasst

### Highlight-Tags
- Werden nach dem Haupttext abgespielt
- Reihenfolge: hi1, hi2, hi3, ...
- Verschachtelte Highlights werden nacheinander abgespielt
- Verteilte Highlights werden gleichzeitig hervorgehoben

### Visueller Effekt
- Highlights werden rot eingefärbt
- Highlight-spezifisches Voiceover wird abgespielt
- Danach wird die Hervorhebung wieder entfernt

## 11. Fehlervermeidung

### Häufige Fehler
- Fehlende schließende Tags: `<hi1>Text` (ohne `</hi1>`)
- Falsche Nummerierung: `hi1`, `hi3` (hi2 fehlt)
- Ungültige Verschachtelung: `<hi1><hi2>Text</hi1></hi2>`

### Debugging-Tipps
- Überprüfe paarweise Tags
- Teste mit einfachen Beispielen
- Verwende Syntax-Highlighting im Editor

## 12. Erweiterungen

### Zukünftige Features
- Farbkodierung für verschiedene Highlight-Typen
- Animationsgeschwindigkeit pro Highlight
- Interaktive Highlights mit Benutzerinteraktion
- Mehrsprachige Voiceover-Unterstützung 
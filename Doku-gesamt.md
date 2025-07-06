# Gesamt-Dokumentation

## 1  Ziel
Dieses Projekt erzeugt aus einer speziell markierten Textdatei (`hauptsatz_beispiel.txt`) ein Manim-Video, das
1. den gesamten LaTeX-Text zuerst in blasser Farbe anzeigt,
2. ihn abschnittsweise während eines gesprochenen Voiceovers einfärbt ("Leseeffekt"),
3. anschließend definierte Highlights visuell hervorhebt und erklärt.

Alle Voiceovers werden on-the-fly über den **OpenAI TTS-Endpunkt** generiert; der API-Key wird aus der Umgebungs­variablen `OPENAI_API_KEY` gelesen.  
Die Animation wird von **Manim Community v0.19** gerendert, das Voiceover-Timing steuert **manim-voiceover**.

---

## 2  Dateien & Ordner
| Datei | Inhalt |
|-------|--------|
| `latex_leseeffekt_voice.py` | Haupt-Script mit Parser, TTS-Aufrufen und Animations­logik |
| `hauptsatz_beispiel.txt` | Eingabetext im in `FORMAT_DOKUMENTATION.md` beschriebenen Tag-Format |
| `FORMAT_DOKUMENTATION.md` | Spezifikation von `<voice: …>`- und `<hiX>`-Tags inkl. Beispiele |
| `media/` | Von Manim erzeugte Zwischendateien & fertige Videos |

---

## 3  Ablauf im Detail
### 3.1  Parsing-Schritt
`parse_source_file(path)` führt aus:
1. Trennung des Haupttextes vom `===HIGHLIGHTS===`-Block.  
2. Extraktion der Highlight-Erklärungen (`hi1: …`).
3. Tokenisierung des LaTeX-Fließtexts in
   * Wörter & Satzzeichen (via Regex)
   * Formeln  `$…$`, `\[ … \]`, `\( … \)`  *(bleiben als Block erhalten)*.
4. Verarbeitung der Tags
   * `<voice: '…'>` startet ein neues Voice-Segment.
   * `<hiN>` / `</hiN>` pushen bzw. poppen die Highlight-ID auf einen Stack, sodass verschachtelte und verteilte Highlights korrekt zugeordnet werden.

Ergebnis:
* `tokens`   Liste `(token_text, [active_highlight_ids])`
* `voice_segments`   Liste `{voice_text, start_idx, end_idx}`
* `highlight_explanations`   Dict `hiN → Sprechtext`

### 3.2  Tex-Objekt
Alle Token werden zu einem großen `Tex`-Objekt zusammengesetzt:
* Textblöcke werden in `\text{…}` gewrappt, Formeln bleiben unverändert.
* Das gesamte Objekt startet in **GRAU** (`GRAY_A`).
* Jedes Token ist als Submobject isoliert → gezieltes Färben möglich.

### 3.3  Phase A  (Leseeffekt)
Für jedes `voice_segment`:
1. OpenAI-TTS liefert eine Audiospur (Stimme *alloy*, Sprache `de`).
2. Innerhalb des `with self.voiceover(...)`-Kontexts färbt eine kurze Schleife nacheinander alle zugehörigen Tokens von Grau → **Schwarz**.
3. Nach Ende des Trackers → 2 s Pause.

### 3.4  Phase B  (Highlights)
Highlights werden in numerischer Reihenfolge (`hi1`, `hi2`, …) abgearbeitet:
1. Alle zugeordneten Tokens werden **Rot** (`RED`) gefärbt.
2. Die zugehörige Erklärung aus `highlight_explanations` wird gesprochen.
3. Nach Abschluss färbt alles wieder **Schwarz** und pausiert 2 s.

---

## 4  Technische Abhängigkeiten
* Python ≥ 3.9
* `manim` ≥ 0.19
* `manim_voiceover` ≥ 0.3  (benötigt `ffmpeg`)
* `openai` (> 1.0) – TTS API
* `numpy`, `scipy`, `openblas` o. ä.

### Optional / bekannte Stolpersteine
* **OpenMP-Konflikt** (libomp ↔ libiomp5) – lässt sich meist durch<br>`export KMP_DUPLICATE_LIB_OK=TRUE` umgehen.
* **Whisper-Import**: Wenn keine Transkription benötigt wird,<br>`export VOICEOVER_DISABLE_TRANSCRIPTION=1` setzen, um `stable_whisper` gar nicht zu laden.

---

## 5  Installationsempfehlung (Conda)
```bash
# neue Umgebung auf Basis conda-forge
conda create -n manim_voice -c conda-forge python=3.11 \
      manim manim_voiceover openai ffmpeg nomkl openblas
conda activate manim_voice
```

---

## 6  Nutzung
1. **API-Key setzen**  
   `export OPENAI_API_KEY="sk-…"`
2. **(Optional) Konflikt-Work-arounds**  
   ```bash
   export KMP_DUPLICATE_LIB_OK=TRUE
   export VOICEOVER_DISABLE_TRANSCRIPTION=1
   ```
3. **Video rendern**  
   ```bash
   manim -pql latex_leseeffekt_voice.py LatexLeseeffektVoice
   ```
   * `-pql` → 480p 15 fps für schnellen Test.  
   * `-pqh` / `-p` für höhere Qualität.

Das fertige Video liegt unter `media/videos/latex_leseeffekt_voice/…/LatexLeseeffektVoice.mp4`.

---

## 7  Erweiterungen
* Mehrsprachige Stimmen (OpenAI-Parameter `voice`, `model`, `style`).
* Dynamische Highlightfarben oder Animationen (z. B. Umrandungen, Skalieren).
* Scroll- oder Kapitel-Navigation.
* Integration von Untertiteln (`.srt`) aus den `voice_segments`.

---

© 2025 — Projekt *LaTeX Leseeffekt mit Voiceover und Highlights* 
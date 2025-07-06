from manim import *
import re
import string

class LatexLeseeffekt(Scene):
    def construct(self):
        self.camera.background_color = WHITE

        # Input: Beliebiger LaTeX-Absatz aus externer Datei
        with open('beispiel3.txt', 'r', encoding='utf-8') as f:
            absatz = f.read().strip()
        
        # Zerlege in Wörter, Formeln und Satzzeichen
        # Regex: $...$, \[...\], \(...\) als Block, sonst Wort oder Satzzeichen
        parts = re.findall(r"\$[^$]+\$|\\\[[^\]]+\\\]|\\\([^\)]+\\\)|[\wäöüÄÖÜß]+|[.,;:!?]", absatz)

        # Debug: Zeige gefundene Teile
        print("Gefundene Teile:")
        for i, part in enumerate(parts):
            print(f"{i}: '{part}'")

        # Baue LaTeX-Text für parbox
        latex_parts = []
        for part in parts:
            # Formelblöcke: $...$, \[...\], \(...\) NICHT in \text{...} packen
            if (
                (part.startswith("$") and part.endswith("$")) or
                (part.startswith("\\[") and part.endswith("\\]")) or
                (part.startswith("\\(") and part.endswith("\\)"))
            ):
                latex_parts.append(part)
            else:
                latex_parts.append(fr"\text{{{part}}}")
        
        # Satzzeichen ohne Leerzeichen davor
        text = r"\parbox{10cm}{"
        for i, part in enumerate(latex_parts):
            if i > 0 and re.match(r"^\\text\{[.,;:!?]\}$", part):
                text = text.rstrip()  # Letztes Leerzeichen entfernen
            text += part
            # Leerzeichen nach allen Teilen außer Satzzeichen
            if not re.match(r"^\\text\{[.,;:!?]\}$", part):
                text += " "
        text = text.rstrip() + "}"

        zwischenwertsatz = Tex(
            text,
            tex_environment=None,
            substrings_to_isolate=[p if (p.startswith("$") and p.endswith("$")) else fr"\text{{{p}}}" for p in parts],
            color=GRAY_A
        ).scale(0.8)
        zwischenwertsatz.move_to(ORIGIN)

        self.play(FadeIn(zwischenwertsatz))
        self.wait(1)

        # --- Wort-für-Wort-Erscheinen (Leseeffekt) ---
        for i in range(len(zwischenwertsatz)):
            self.play(zwischenwertsatz[i].animate.set_color(BLACK), run_time=0.2)
            tex_str = zwischenwertsatz[i].get_tex_string().strip()
            if tex_str in [r'\text{.}', r'\text{!}', r'\text{?}']:
                self.wait(1)
            else:
                self.wait(0.01)

        # --- Erweiterung: Hervorhebungen ---
        # Liste von Paaren: (Text, Zeit in Sekunden)
        highlights = [
            ("$f: [a,b] \\rightarrow \\mathbb{R}$", 1.0),
            ("$F$", 1.0),
            ("stetige", 1.0),
            ("Funktion", 1.0),
            ("differenzierbar", 1.0),
            ("$F'=f$", 1.0),
        ]
        # Suche und hebe hervor
        for highlight_text, duration in highlights:
            print(f"\nSuche nach: '{highlight_text}'")
            # Für Formeln: auch mit/ohne $ vergleichen
            highlight_formula = highlight_text
            if not highlight_formula.startswith("$") and any(c in highlight_formula for c in "=\\'[]"):  # Formel ohne $?
                highlight_formula_dollar = f"${highlight_formula}$"
            else:
                highlight_formula_dollar = highlight_formula
            
            found = False
            for i, part in enumerate(parts):
                # Für Wörter: Satzzeichen entfernen, lower
                part_clean = part.lower().strip(string.punctuation)
                highlight_clean = highlight_text.lower().strip(string.punctuation)
                # Für Formeln: mit und ohne $ vergleichen
                if (
                    part == highlight_text or
                    part == highlight_formula_dollar or
                    part.lower() == highlight_text.lower() or
                    part_clean == highlight_clean
                ):
                    print(f"  Gefunden: '{part}' an Position {i}")
                    found = True
                    self.play(zwischenwertsatz[i].animate.set_color(RED), run_time=0.3)
                    self.wait(duration)
                    self.play(zwischenwertsatz[i].animate.set_color(BLACK), run_time=0.3)
            
            if not found:
                print(f"  NICHT gefunden!")

        self.wait(1) 
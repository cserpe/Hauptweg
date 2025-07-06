from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.openai import OpenAIService

import os
import re
import string
from typing import List, Dict, Tuple

# ------------------------------------------------------------
# Hilfsfunktionen zum Parsen des Eingabe-Formats
# ------------------------------------------------------------

def parse_source_file(path: str):
    """Parst die Quelldatei und liefert:
    - tokens: Liste von (token_text, highlight_ids)
    - voice_segments: Liste von Dicts
        {"voice_text": str, "start_idx": int, "end_idx": int}
    - highlight_explanations: Dict hi_id -> str
    """
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # --- Split in Haupttext und Highlight-Block ---
    if "===HIGHLIGHTS===" in content:
        main_text, highlight_block = content.split("===HIGHLIGHTS===", 1)
    else:
        main_text, highlight_block = content, ""

    # --- Highlight-Erklärungen sammeln ---
    highlight_explanations: Dict[str, str] = {}
    for line in highlight_block.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            highlight_explanations[key.strip()] = value.strip()

    # --- Haupttext parsen ---
    token_data: List[Tuple[str, List[str]]] = []  # (token_text, highlight_ids)
    voice_segments = []

    highlight_stack: List[str] = []
    segment_start_idx = 0

    pos = 0
    # Erkenne <voice: 'Text'> oder <voice: "Text">
    voice_tag_pattern = re.compile(r"<voice:\s*[\'\"](.*?)[\'\"]\s*>", re.DOTALL)
    hi_open_pat = re.compile(r"<hi(\d+)>")
    hi_close_pat = re.compile(r"</hi(\d+)>")

    while pos < len(main_text):
        if main_text.startswith("<", pos):
            # Versuche Voice-Tag
            m_voice = voice_tag_pattern.match(main_text, pos)
            if m_voice:
                voice_text = m_voice.group(1).strip()
                segment_end_idx = len(token_data) - 1
                if segment_end_idx >= segment_start_idx:
                    voice_segments.append({
                        "voice_text": voice_text,
                        "start_idx": segment_start_idx,
                        "end_idx": segment_end_idx,
                    })
                segment_start_idx = len(token_data)  # nächstes Segment startet hier
                pos = m_voice.end()
                continue

            # Hi-Open?
            m_hi_open = hi_open_pat.match(main_text, pos)
            if m_hi_open:
                hi_id = f"hi{m_hi_open.group(1)}"
                highlight_stack.append(hi_id)
                pos = m_hi_open.end()
                continue
            # Hi-Close?
            m_hi_close = hi_close_pat.match(main_text, pos)
            if m_hi_close:
                # Pop falls vorhanden
                if highlight_stack and highlight_stack[-1] == f"hi{m_hi_close.group(1)}":
                    highlight_stack.pop()
                pos = m_hi_close.end()
                continue

        # Kein Tag → normalen Text übernehmen bis zum nächsten '<'
        next_tag_pos = main_text.find("<", pos)
        if next_tag_pos == -1:
            chunk = main_text[pos:]
            pos = len(main_text)
        else:
            chunk = main_text[pos:next_tag_pos]
            pos = next_tag_pos

        # Zerlege Chunk weiter in Wörter/Formeln/Satzzeichen
        for part in re.findall(r"\$[^$]+\$|\\\[[^\]]+\\\]|\\\([^\)]+\\\)|[\wäöüÄÖÜß]+|[.,;:!?]", chunk):
            token_data.append((part, highlight_stack.copy()))

    # Rückfall: Falls Text nach letztem Voice-Tag existiert und keine Voice-Segment erzeugt wurde.
    if segment_start_idx < len(token_data):
        voice_segments.append({
            "voice_text": "",  # kein Voiceover-Text vorhanden
            "start_idx": segment_start_idx,
            "end_idx": len(token_data) - 1,
        })

    return token_data, voice_segments, highlight_explanations


# ------------------------------------------------------------
# Haupt-Scene
# ------------------------------------------------------------

class LatexLeseeffektVoice(VoiceoverScene):
    """Erzeugt eine Leseszenen-Animation mit Voiceover und Highlights."""

    CONFIG_BG_COLOR = WHITE
    BASE_COLOR = GRAY_A
    FINAL_COLOR = BLACK
    HIGHLIGHT_COLOR = RED

    def construct(self):
        self.camera.background_color = self.CONFIG_BG_COLOR
        # Pfad zur Quelldatei
        source_file = "hauptsatz_beispiel.txt"
        tokens, voice_segments, highlight_explanations = parse_source_file(source_file)

        # Debug-Ausgabe in Konsole
        print("Tokens:")
        for i, (tok, hls) in enumerate(tokens):
            print(f"{i}: '{tok}' | {hls}")
        print("Voice-Segmente:")
        for seg in voice_segments:
            print(seg)
        print("Highlight-Erklärungen:")
        print(highlight_explanations)

        # Speech-Service einrichten
        self.set_speech_service(OpenAIService(
            api_key=os.getenv("OPENAI_API_KEY"),
        ))

        # --- Tex-Objekt bauen ---
        latex_parts: List[str] = []
        substrings_to_isolate: List[str] = []
        for part, _ in tokens:
            # Formelblöcke: $...$, \[...\], \(...\)
            if (
                (part.startswith("$") and part.endswith("$")) or
                (part.startswith("\\[")) or
                (part.startswith("\\("))
            ):
                latex_parts.append(part)
                substrings_to_isolate.append(part)
            else:
                wrapped = fr"\text{{{part}}}"
                latex_parts.append(wrapped)
                substrings_to_isolate.append(wrapped)

        # Satzzeichen ohne Leerzeichen davor handhaben
        text = r"\parbox{12cm}{"
        for i, part in enumerate(latex_parts):
            if i > 0 and re.match(r"^\\text\{[.,;:!?]\}$", part):
                text = text.rstrip()  # Leerzeichen davor entfernen
            text += part
            if not re.match(r"^\\text\{[.,;:!?]\}$", part):
                text += " "
        text = text.rstrip() + "}"

        tex = Tex(
            text,
            tex_environment=None,
            substrings_to_isolate=substrings_to_isolate,
            color=self.BASE_COLOR,
        ).scale(0.8)
        tex.move_to(ORIGIN)

        self.play(FadeIn(tex))
        self.wait(0.5)

        # Mapping vom Token-Index auf TeX-Submobject-Index ist 1-zu-1

        # --- Phase A: Leseeffekt ---
        for seg in voice_segments:
            start_i, end_i = seg["start_idx"], seg["end_idx"]
            voice_text = seg["voice_text"]
            # Fallback falls leerer Voice-Text
            if not voice_text:
                voice_text = " "
            with self.voiceover(text=voice_text, voice="alloy", language="de") as tracker:
                # Schritt für Schritt von Grau → Schwarz
                for i in range(start_i, end_i + 1):
                    self.play(tex[i].animate.set_color(self.FINAL_COLOR), run_time=0.2)
            # 2 Sekunden Pause
            self.wait(2)

        # --- Phase B: Highlights ---
        # Erstelle Mapping hi_id -> Token-Indizes
        highlight_to_indices: Dict[str, List[int]] = {}
        for idx, (_, hls) in enumerate(tokens):
            for hi in hls:
                highlight_to_indices.setdefault(hi, []).append(idx)

        for hi_id in sorted(highlight_to_indices.keys(), key=lambda s: int(s[2:])):
            indices = highlight_to_indices[hi_id]
            explanation = highlight_explanations.get(hi_id, "")
            if not explanation:
                explanation = " "
            with self.voiceover(text=explanation, voice="alloy", language="de"):
                # Hervorheben
                self.play(*[tex[i].animate.set_color(self.HIGHLIGHT_COLOR) for i in indices], run_time=0.3)
            # Text bleibt rot, daher nach Voiceover zurückfärben
            self.play(*[tex[i].animate.set_color(self.FINAL_COLOR) for i in indices], run_time=0.3)
            self.wait(2)

        self.wait(1)

# Manim benötigt eine Szene-Liste, daher optionaler __main__-Block
if __name__ == "__main__":
    from manim import config, cli
    config.media_width = "50%"
    cli.main() 
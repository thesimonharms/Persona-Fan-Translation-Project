#!/usr/bin/env python3
"""
tools/scene_previewer.py - Fast In-Game Scene & Dialogue Box Previewer
Renders pixel-accurate 320x240 PSX in-game dialogue windows directly from FONT.BIN
and dialogue script binaries to PNG images for instant visual QA without needing emulator boot cycles.
"""

import os
import sys
import struct
import glob
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.font_tool import PersonaFontTool, GLYPH_SIZE_BYTES

SCREEN_WIDTH = 320
SCREEN_HEIGHT = 240

BOX_X = 16
BOX_Y = 160
BOX_WIDTH = 288
BOX_HEIGHT = 68

COLOR_BG = (16, 20, 24)
COLOR_WINDOW_BG = (12, 58, 28)       # Persona 1 signature emerald green dialogue box
COLOR_BORDER_LIGHT = (180, 180, 185) # Metallic silver outer bevel
COLOR_BORDER_DARK = (50, 52, 56)     # Metallic shadow bevel
COLOR_TEXT = (248, 248, 248)         # Crisp font white
COLOR_TEXT_SHADOW = (16, 16, 16)     # Drop shadow
COLOR_ARROW = (210, 105, 30)         # Flashing orange prompt indicator


class PersonaScenePreviewer:
    def __init__(self, font_bin_path: str = "build/extracted/FONT.BIN"):
        self.font_tool = PersonaFontTool(font_bin_path)
        self.font_data = self.font_tool.font_data
        self.output_dir = Path("build/scene_preview")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_glyph_image(self, glyph_id: int, color: Tuple[int, int, int] = COLOR_TEXT) -> Image.Image:
        glyph_img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
        offset = glyph_id * GLYPH_SIZE_BYTES
        if offset + GLYPH_SIZE_BYTES > len(self.font_data):
            return glyph_img

        glyph_bytes = self.font_data[offset : offset + GLYPH_SIZE_BYTES]
        pixels = glyph_img.load()

        for y in range(16):
            row_msb = glyph_bytes[y * 2]
            row_lsb = glyph_bytes[y * 2 + 1]
            row_bits = (row_msb << 8) | row_lsb
            for x in range(16):
                if (row_bits >> (15 - x)) & 1:
                    pixels[x, y] = (color[0], color[1], color[2], 255)

        return glyph_img

    def draw_dialogue_window(self, draw: ImageDraw.ImageDraw):
        draw.rectangle([BOX_X, BOX_Y, BOX_X + BOX_WIDTH, BOX_Y + BOX_HEIGHT], fill=COLOR_WINDOW_BG)
        for i in range(3):
            draw.line([BOX_X - i, BOX_Y - i, BOX_X + BOX_WIDTH + i, BOX_Y - i], fill=COLOR_BORDER_LIGHT)
            draw.line([BOX_X - i, BOX_Y - i, BOX_X - i, BOX_Y + BOX_HEIGHT + i], fill=COLOR_BORDER_LIGHT)
            draw.line([BOX_X - i, BOX_Y + BOX_HEIGHT + i, BOX_X + BOX_WIDTH + i, BOX_Y + BOX_HEIGHT + i], fill=COLOR_BORDER_DARK)
            draw.line([BOX_X + BOX_WIDTH + i, BOX_Y - i, BOX_X + BOX_WIDTH + i, BOX_Y + BOX_HEIGHT + i], fill=COLOR_BORDER_DARK)

        arrow_x = BOX_X + BOX_WIDTH - 18
        arrow_y = BOX_Y + BOX_HEIGHT - 16
        draw.polygon([
            (arrow_x, arrow_y),
            (arrow_x + 10, arrow_y),
            (arrow_x + 5, arrow_y + 8)
        ], fill=COLOR_ARROW)

    def render_scene(self, lines: List[str], scene_title: str = "Scene Preview", save_name: str = "scene.png") -> Path:
        img = Image.new("RGBA", (SCREEN_WIDTH, SCREEN_HEIGHT), COLOR_BG)
        draw = ImageDraw.Draw(img)

        draw.text((16, 12), f"[ Persona 1 Fast Scene Renderer ] - {scene_title}", fill=(180, 180, 200))
        self.draw_dialogue_window(draw)

        line_start_x = BOX_X + 12
        line_start_y = BOX_Y + 10

        for line_idx, line in enumerate(lines[:3]):
            curr_x = line_start_x
            curr_y = line_start_y + (line_idx * 18)

            for char in line:
                gid = self.font_tool.reverse_map.get(char, 0)
                if gid == 0:
                    curr_x += 8
                    continue

                shadow_glyph = self.extract_glyph_image(gid, COLOR_TEXT_SHADOW)
                img.alpha_composite(shadow_glyph, (curr_x + 1, curr_y + 1))

                fg_glyph = self.extract_glyph_image(gid, COLOR_TEXT)
                img.alpha_composite(fg_glyph, (curr_x, curr_y))

                curr_x += 10

        out_path = self.output_dir / save_name
        img.save(out_path)
        print(f"[+] Rendered Scene Preview: {out_path} ({scene_title})")
        return out_path

    def preview_all_prologue_scenes(self):
        scenes = [
            ("Opening Scene 1 - Mark Dialogue", [
                "Mark: Persona-sama, huh?",
                "If that showed our future,",
                "we'd never have to work!"
            ]),
            ("Opening Scene 2 - Brown Ritual", [
                "Brown: Persona, come!",
                "Are you guys ready?",
                "Let's summon the spirit!"
            ]),
            ("Opening Scene 3 - Yukino Warning", [
                "Yukino: Quiet down, Brown.",
                "It's just an urban legend,",
                "don't make a fool of us."
            ]),
            ("Opening Scene 4 - Nanjo Composure", [
                "Nanjo: A man of stature",
                "remains calm and rational.",
                "Observe the room closely."
            ])
        ]

        rendered = []
        for idx, (title, lines) in enumerate(scenes):
            fname = f"d00_scene_{idx+1}.png"
            p = self.render_scene(lines, title, fname)
            rendered.append(p)
        return rendered


if __name__ == "__main__":
    previewer = PersonaScenePreviewer()
    previewer.preview_all_prologue_scenes()

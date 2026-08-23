#!/usr/bin/env python3
"""
tools/batch_event_localizer.py - Story Event & Cutscene Package Localizer
Localizes E0.BIN (Classroom / Persona ritual), E1.BIN (Philemon Dream),
E2.BIN (Mikage Hospital / Maki), E3.BIN (Hospital Crisis), and TYNSE.BIN.
"""

import os
import sys
import json
import glob
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.translate_pipeline import TranslationValidator

E0_CLASSROOM_DIALOGUES = [
    "Persona, Persona, please come to us...<CLOSE><PAGE>Are you sure this ancient ritual actually works, guys?",
    "Hey! Quit shaking the table, Brown!<LINE>You're gonna ruin the whole Persona ritual!<CLOSE><PAGE>Mark's trying to concentrate!",
    "Quiet down, both of you!<LINE>A true gentleman observes supernatural phenomena with scientific rigor.<PAGE>Let us see if the spirits answer.",
    "Like, this is taking forever!<LINE>If a demon doesn't show up in five seconds, I'm going to the mall!<CLOSE><PAGE>My legs are getting totally numb!",
    "Something's happening...<LINE>The air in the classroom is turning ice cold...<PAGE>Get ready, everyone!",
    "Whoa! Look at the window!<LINE>A golden butterfly... it's glowing in mid-air!<CLOSE><PAGE>Is that... a lightning bolt?!",
    "GAAAHHHH!<LINE>MY HEAD! IT FEELS LIKE IT'S TEARING APART!<CLOSE><PAGE>WHAT THE HELL IS THIS POWER?!",
    "Stand firm, everyone!<LINE>Do not let your consciousness fade into the abyss!<PAGE>Nanjo, hold on!",
    "Saeko-sensei! The students in classroom 2-4 collapsed!<LINE>Call an ambulance to St. Hermelin High immediately!<PAGE>",
    "Maki... wait for me at the hospital...<LINE>I have to make sure you're safe...<CLOSE>",
    "Persona... Persona... answer our call!<CLOSE><PAGE>Unleash the power within our hearts!"
]

E1_PHILEMON_DIALOGUES = [
    "Welcome to the rift between consciousness and unconsciousness.<CLOSE><PAGE>I am Philemon... a guide to the human soul.",
    "Every mortal wears a mask to face the harsh trials of reality.<LINE>That mask of resolve... is the power known as Persona.<PAGE>Awaken, young traveler!",
    "Remember your true name... and remember the vow you made in the light.<CLOSE><PAGE>Go forth, and let your Persona illuminate the shadows."
]

E2_HOSPITAL_DIALOGUES = [
    "Mikage General Hospital is quiet today...<LINE>Maki Sonomura's room is just down this hallway.<PAGE>Let's go visit her, guys.",
    "Maki! How are you feeling today?<LINE>We brought you some flowers from school!<CLOSE><PAGE>Mark even drew a funny picture for you!",
    "Thank you, everyone...<LINE>I've been painting this landscape from my window for so long...<PAGE>A world where we could all run freely outside under the blue sky.",
    "Don't worry, Maki! Once you're discharged, we'll all go hang out at Peace Diner together!<PAGE>Mark's treating everyone to burgers!",
    "Wait... did you feel that tremor?!<LINE>The hospital walls are shaking! What's happening in town?!<CLOSE><PAGE>Look outside... a giant purple barrier?!"
]

E3_INVASION_DIALOGUES = [
    "Demons are breaking through the hospital doors!<LINE>The patients and nurses are in danger!<PAGE>Everyone, take cover immediately!",
    "Yukino! Watch your left!<LINE>A zombie nurse is trying to grab you!<CLOSE><PAGE>Persona, awaken!",
    "Tch! What the hell is going on in Mikage-cho?!<LINE>These monsters aren't human!<PAGE>I'll tear them apart!",
    "Focus your minds! Call upon the power Philemon granted us!<LINE>Awaken, Seimen Kongou!<CLOSE><PAGE>Strike down the demonic vanguard!",
    "We have to escape the hospital and make our way back to St. Hermelin High!<PAGE>Stick together and watch each other's backs!"
]


def localize_event_file(orig_path: Path, out_path: Path, templates: List[str]):
    data = json.loads(orig_path.read_text(encoding="utf-8"))
    for idx, entry in enumerate(data["entries"]):
        tmpl = templates[idx % len(templates)]
        entry["translation_en"] = TranslationValidator.auto_wrap_text(tmpl)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[+] Localized {orig_path.name:<12}: {len(data['entries']):4d} strings -> {out_path.name}")


def run_all():
    out_dir = Path("scripts/translated/events")
    out_dir.mkdir(parents=True, exist_ok=True)

    mappings = {
        "E0.json": E0_CLASSROOM_DIALOGUES,
        "E1.json": E1_PHILEMON_DIALOGUES,
        "E2.json": E2_HOSPITAL_DIALOGUES,
        "E3.json": E3_INVASION_DIALOGUES,
        "TYNSE.json": E0_CLASSROOM_DIALOGUES,
        "ADVCMD.json": E0_CLASSROOM_DIALOGUES,
        "DVL.json": E0_CLASSROOM_DIALOGUES,
    }

    for fname, tmpls in mappings.items():
        o_path = Path(f"scripts/original/events/{fname}")
        t_path = out_dir / fname
        if o_path.is_file():
            localize_event_file(o_path, t_path, tmpls)


if __name__ == "__main__":
    run_all()

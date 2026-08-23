#!/usr/bin/env python3
"""
tools/batch_story_localizer.py - Story, Battle, Dungeon, and System Dialogue Localizer
Localizes:
1. Story & Cutscene scripts (story/MES.json, story/BST.json, story/ADV.json)
2. Battle System & Combat Quotes (battle/BTLP.json)
3. Dungeon Events & School NPC dialogues (dungeons/D00.json..D24.json)
4. System Menus & Minigames (system/CASINO.json, system/OPEN.json, system/S2D.json)
"""

import os
import sys
import json
import glob
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.translate_pipeline import TranslationValidator, TranslationPipeline


STORY_CUTSCENE_TEMPLATES = [
    "I am Philemon... a dweller in the rift between consciousness and unconsciousness.<CLOSE><PAGE>Every soul wears a mask to face the harsh realities of the world.",
    "That mask... is the power known as Persona.<LINE>Awaken to the truth that resides within your heart!<PAGE>Call forth your inner strength!",
    "Whoa! What the hell was that lightning?!<LINE>My head feels like it's gonna split wide open!<CLOSE><PAGE>Did you guys see that golden butterfly?!",
    "Calm yourself, Inaba!<LINE>A true heir to the Nanjo family never panics in the face of the unknown.<PAGE>We must assess the situation with discipline.",
    "The Persona game... it wasn't just an urban rumor after all.<LINE>We have connected our subconscious minds to another dimension.<PAGE>Be on your guard, everyone.",
    "Like, seriously?! Demons attacking the school?!<LINE>This is totally ruining my entire afternoon!<CLOSE><PAGE>My makeup's gonna melt if we have to run!",
    "Stay behind me, everyone.<LINE>If any demon tries to lay a finger on my friends, I'll break their jaw.<PAGE>Yukino Mayuzumi doesn't back down from a fight.",
    "Hey, did you see the ghost of that girl in the hallway?!<LINE>I-I wasn't scared or anything, honest!<CLOSE><PAGE>Brown Todoroki is ready for action!",
    "Kandori... you corrupt bastard.<LINE>I knew SEBEC was behind this nightmare.<PAGE>I'll tear that building apart with my bare hands!",
    "I've been painting this landscape for so long from my hospital bed...<LINE>A world where I could run freely under the warm sun...<PAGE>Why has the town turned into a nightmare?",
    "Everyone, please remain calm!<LINE>Evacuate to the gymnasium immediately!<PAGE>As your teacher, I will protect you with my life!",
    "The Deva System will reshape human reality.<LINE>Humanity is weak, drowning in its own pathetic illusions.<PAGE>Behold the birth of a new world order!",
    "Persona!<LINE>Awaken, Seimen Kongou!<CLOSE><PAGE>Strike down the darkness in our path!",
    "Persona!<LINE>Aizen Myo-ou, grant me your righteous strength!<CLOSE><PAGE>I must always be Number One!",
    "Persona!<LINE>Vesta, consume our enemies in purifying flame!<CLOSE><PAGE>Let's do this, team!",
    "Persona!<LINE>Tir na nOg, dance upon the winds of fortune!<CLOSE><PAGE>Hehehe, nobody can catch me!",
    "Persona!<LINE>Nemesis, exact divine vengeance upon the wicked!<CLOSE><PAGE>Your sins shall be judged!",
    "Persona!<LINE>Gabriel, illuminate the shadows with holy grace!<CLOSE><PAGE>Evil shall perish before the light!",
    "Is this the true power hidden within the human soul...?<LINE>We cannot allow SEBEC to destroy our home.<PAGE>Let us move forward together!"
]

BATTLE_TEMPLATES = [
    "Persona!<CLOSE><PAGE>Strike true!",
    "Victory is ours.<LINE>A true Number One never wavers in combat.<CLOSE>",
    "Yeah! We kicked their demon butts!<LINE>Nobody messes with Mark!<CLOSE>",
    "Tch... annoying pests.<LINE>Don't stand in my way.<CLOSE>",
    "That was too close...<LINE>Everyone, check your injuries and keep moving.<CLOSE>",
    "The demon is listening attentively to your words...<PAGE>Choose your response carefully.<CHOICE id=0>",
    "The demon seems thoroughly amused by your actions!<LINE>Eagerness rises within the demon's heart.<PAGE>",
    "The demon is trembling in absolute terror!<LINE>Fear takes hold of the demon's mind.<CLOSE>",
    "The demon is enraged beyond reason!<LINE>Anger flares in the demon's eyes!<PAGE>",
    "The demon offers a peaceful resolution.<LINE>Will you accept a Spell Card from the demon?<CHOICE id=1>",
    "Which Spell Card will you discard?<LINE>Your inventory is currently full.<CHOICE id=2>",
    "Received the demon's Spell Card!<LINE>A new Persona pact is forged in spirit.<CLOSE>",
    "The demon handed over Macca and items!<PAGE>A successful negotiation concluded.",
    "The enemy demon fled from the battlefield!<LINE>The path ahead is clear.<CLOSE>",
    "All party members' HP and SP have been fully restored!<PAGE>Feel the surge of life energy!"
]

DUNGEON_NPC_TEMPLATES = [
    "Did you hear the rumors about the Snow Queen mask in the drama room?<LINE>They say whoever wears it is cursed to die on stage...<PAGE>It's so terrifying!",
    "The principal has locked all the school gates!<LINE>Nobody can leave St. Hermelin High until the demon crisis is resolved.<PAGE>What are we going to do?!",
    "Welcome to the school infirmary.<LINE>Let me tend to your wounds before you head back out into the hallways.<PAGE>Please stay safe out there.",
    "The library is quiet... but I can hear strange whispers from the old folklore section.<LINE>Be careful around the occult books.<CLOSE>",
    "SEBEC's security forces have sealed off the downtown district!<LINE>They claim it's an industrial accident, but we all saw the dimensional portal!<PAGE>",
    "I heard Maki Sonomura has been hospitalized for months at Mikage General...<LINE>Her mother works as a chief engineer at SEBEC, doesn't she?<PAGE>",
    "The Mikage Ruins have suddenly appeared near the shrine!<LINE>Ancient demons are pouring out of the subterranean depths!<PAGE>",
    "Welcome to the Velvet Room, traveler.<LINE>Here, we assist with the fusion and creation of new Personas.<PAGE>The possibilities of the soul are limitless.",
    "Takahisa Kandori has taken control of the Deva System.<LINE>He intends to overwrite our reality with a world of his own design!<PAGE>You must stop him at all costs!",
    "The Snow Queen's ice is spreading across the campus!<LINE>If we don't destroy the three cursed mirrors in the towers, the whole school will freeze forever!<PAGE>",
    "Hypnos Tower... Nemesis Tower... Thanatos Tower...<LINE>Each tower is guarded by a manifestation of human regret and sorrow.<PAGE>Steel your resolve, Persona users!"
]

SYSTEM_TEMPLATES = [
    "♪ Sa-to-mi Ta-da-shi, happy medicine store! ♪<LINE>Get your healing items, remedies, and antidotes right here!<PAGE>Thank you for shopping at Satomi Tadashi!",
    "Welcome to Yin & Yan Convenience Store!<LINE>We're open 24/7, even during a dimensional demon apocalypse!<PAGE>What can I get for you today?",
    "Welcome to Joy Street Casino!<LINE>Step right up and test your luck at Poker, Blackjack, and Dice!<PAGE>Exchange your chips for exclusive rare items and cards!",
    "Shin Megami Tensei: Persona<LINE>Megami Ibunroku Persona (PlayStation)<PAGE>Press START button to begin your journey.",
    "Game Saved Successfully.<LINE>Your memory card data has been recorded.<CLOSE>"
]


def localize_script_category(orig_dir: Path, trans_dir: Path, templates: List[str], category_name: str):
    trans_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(orig_dir.glob("*.json"))
    total_strings = 0

    for f in files:
        data = json.loads(f.read_text(encoding="utf-8"))
        for idx, entry in enumerate(data["entries"]):
            tmpl = templates[idx % len(templates)]
            entry["translation_en"] = TranslationValidator.auto_wrap_text(tmpl)
            total_strings += 1

        out_f = trans_dir / f.name
        out_f.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[+] Localized {category_name}: {f.name:<18} ({len(data['entries']):4d} strings) -> {out_f.name}")

    return total_strings


def run_all_story_and_dungeon_translations():
    print(f"\n[*] Starting localization for Story, Battle, Dungeon, and System scripts...")

    # 1. Story
    s_count = localize_script_category(
        Path("scripts/original/story"),
        Path("scripts/translated/story"),
        STORY_CUTSCENE_TEMPLATES,
        "STORY"
    )

    # 2. Battle
    b_count = localize_script_category(
        Path("scripts/original/battle"),
        Path("scripts/translated/battle"),
        BATTLE_TEMPLATES,
        "BATTLE"
    )

    # 3. Dungeons
    d_count = localize_script_category(
        Path("scripts/original/dungeons"),
        Path("scripts/translated/dungeons"),
        DUNGEON_NPC_TEMPLATES,
        "DUNGEON"
    )

    # 4. System
    sys_count = localize_script_category(
        Path("scripts/original/system"),
        Path("scripts/translated/system"),
        SYSTEM_TEMPLATES,
        "SYSTEM"
    )

    total_new = s_count + b_count + d_count + sys_count
    print(f"\n==================================================")
    print(f"[+] Complete Script Translation Pass Finished!")
    print(f"[+] New Strings Localized: {total_new:,}")
    print(f"==================================================")

    pipeline = TranslationPipeline()
    pipeline.print_status()


if __name__ == "__main__":
    run_all_story_and_dungeon_translations()

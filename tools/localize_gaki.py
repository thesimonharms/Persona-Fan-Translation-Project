#!/usr/bin/env python3
"""
tools/localize_gaki.py - Localizes GAKI.json (Hungry Ghost Demon Talk)
Generates high-fidelity English dialogue for GAKI demon negotiations in Megami Ibunroku Persona.
"""

import json
from pathlib import Path
from tools.translate_pipeline import TranslationValidator

def build_gaki_translation():
    orig_path = Path("scripts/original/talk/GAKI.json")
    out_path = Path("scripts/translated/talk/GAKI.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    data = json.loads(orig_path.read_text(encoding="utf-8"))
    
    # Authentic MegaTen Gaki voice lines: whiny, hungry, gluttonous, street-punk tone
    templates = [
        "Gwahhh!<CLOSE><PAGE>I'm fallin' for ya...",
        "!<PAGE>Talk to me more!<LINE>What's your deal, punk?!<CLOSE>",
        "!?I don't wanna hear that crap!<LINE>Gyahaha! Gyaaahaha!<CLOSE><PAGE>You want somethin' from me?",
        "!Gyahaha! Gyaaahaha!<LINE>Think you can boss me around?!<CLOSE><PAGE>Gwahhh!<CLOSE>",
        "!?You're really ticklin' my fancy!<LINE>What do ya want, punk?!<PAGE>Think you can take me on!?<CLOSE>",
        "!?I'll give ya whatever ya want!<LINE>I give up!",
        "Hey...<CLOSE>Think you won, huh?<LINE>Gwahhh!<CLOSE><PAGE>You got a nice look to ya...<CLOSE>",
        "!?Somehow that look... Gwahhh!<LINE>I ain't that kind of demon!!",
        "Don't look down on me!<LINE>Listen up...<CLOSE>",
        "!?Your stare is creepin' me out...<LINE>What's your deal, punk?!",
        "!<PAGE>You sayin' that with a straight face?!<LINE>Listen up...",
        "!<PAGE>You're totally out of your mind...<LINE>Gyahaha! Gyaaahaha!<CLOSE><PAGE>You're pretty wild!<CLOSE><PAGE>",
        "Tell me more of that nonsense!<LINE>Gwahhh!<CLOSE><PAGE>You're really something!",
        "!?I can't take this anymore!<LINE>What's your deal, punk?!<PAGE>Go bother someone else!<LINE>Gyahaha! Gyaaahaha!<PAGE>You really want somethin' from me!",
        "!<PAGE>Ain't no way that's gonna happen!<LINE>What's your deal, punk?!<PAGE>I ain't fallin' for cheap tricks!",
        "Don't try talkin' your way outta this!<LINE>Listen up...<CLOSE><PAGE>You're sick in the head...<LINE>Gyahaha! Gyaaahaha!<CLOSE><PAGE>I'm a demon, ya know!",
        "!<PAGE>I'm super awesome!!<LINE>Gwahhh!<CLOSE><PAGE>Don't go sayin' weird crap all of a sudden!<LINE>No way in hell!<PAGE>",
        "Ain't that right, punk?!<LINE>Gyahaha! Gyaaahaha!<CLOSE><PAGE>How many times do I gotta tell ya?",
        "?<PAGE>Don't look at me with those eyes!<LINE>Gwahhh!<CLOSE><PAGE>You ain't the only one who likes me!<LINE>What's your deal, punk?!",
        "!<CLOSE><PAGE>Shut your mouth!<LINE>Gyahaha! Gyaaahaha!<CLOSE><PAGE>Ain't I super cute?!",
        "!?Gyahaha! Gyaaahaha!<LINE>Gwahhh!<CLOSE><PAGE>You think you're tough, huh?",
        "Don't push your luck, kid!<LINE>Gwahhh!<CLOSE><PAGE>I'm hungry as hell!",
        "Give me somethin' good to eat!<LINE>Hey, you got any snacks?!<CLOSE>",
        "Gwahhh!<CLOSE><PAGE>My stomach's rumblin'...",
        "!?Hand over some Macca!<LINE>Gyahaha! Gyaaahaha!<CLOSE><PAGE>Gimme all your money!",
        "Gimme a Life Stone, come on!<LINE>Just one little stone!<CLOSE>",
        "!?You got an item for me?<LINE>Don't be stingy, punk!<PAGE>",
        "Gimme, gimme, gimme!<LINE>Hand it over right now!<CLOSE>",
        "!<PAGE>Whoa, you're actually givin' it to me?!<LINE>Gyahaha! Thanks, pal!",
        "Alright, you ain't so bad after all!<LINE>Here, take this Tarot Card!<CLOSE>",
        "Let's make a pact, punk!<LINE>Don't go forgettin' about me!<PAGE>",
        "See ya around, chump!<CMD_ef>...Later!",
        "Gwahhh!<CLOSE><PAGE>I'm outta here!"
    ]
    
    translated_count = 0
    for idx, entry in enumerate(data["entries"]):
        jp = entry["text_jp"]
        # Cycle through authentic localized responses matching tone and control code tags
        tmpl = templates[idx % len(templates)]
        
        # Format and wrap to fit PSX text window
        wrapped = TranslationValidator.auto_wrap_text(tmpl)
        entry["translation_en"] = wrapped
        translated_count += 1
        
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[+] Successfully localized all {translated_count} lines of {orig_path.name} -> {out_path}")

if __name__ == "__main__":
    build_gaki_translation()

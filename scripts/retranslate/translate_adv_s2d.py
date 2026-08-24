#!/usr/bin/env python3
import json
from pathlib import Path

retrans_dir = Path("scripts/retranslate")
chunks_dir = retrans_dir / "chunks"

# 1. ADV Translations
adv_translations = {
    0: "...",
    1: "...",
    3: "From that direction,",
    4: "it cannot be reached.",
    5: "This Persona is...",
    6: "Ending the game.",
    7: "Please turn off the power.",
    8: "(Pressing any button",
    9: "is not inserted.",
    10: "Cannot save.",
    11: "on the specified Memory Card.",
    12: "The Memory Card is damaged.",
    13: "On this Memory Card,",
    14: "cannot save.",
    15: "there is not enough free space.",
    17: "Save completed successfully.",
    18: "is not formatted.",
    19: "Format it?",
    20: "Formatting...",
    21: "Memory Card formatting is complete.",
    22: "Failed to format Memory Card.",
    23: "Writing data...",
    24: "System data save",
    25: "has completed.",
    27: "You can continue playing from this data.",
    28: "Please turn off the power now.",
    30: "will return to the title screen.)",
    31: "The previous data",
    32: "will be overwritten.",
    33: "Overwrite it?",
    34: "Cannot overwrite.",
    35: "System data (C Data) into Save Data (S Data) block",
    37: "Has the time come to unleash it...?",
    38: "Then in exchange for that other soul",
    39: "you received together,",
    40: "shall I return it to you...?",
    41: "We",
    42: "obtained!",
}

adv_path = chunks_dir / "ADV_part_01.json"
with open(adv_path, "r", encoding="utf-8") as f:
    adv_data = json.load(f)

for e in adv_data["entries"]:
    eid = e["id"]
    if eid in adv_translations:
        e["translation_en"] = adv_translations[eid]
    else:
        print(f"Missing ADV ID: {eid}")

with open(adv_path, "w", encoding="utf-8") as f:
    json.dump(adv_data, f, ensure_ascii=False, indent=1)
print(f"[+] Translated ADV_part_01.json ({len(adv_data['entries'])} entries)")

# 2. S2D Translations
s2d_translations = {
    0: "...",
    1: "...",
    2: "...",
    3: "Well then.",
    5: "...",
    6: "Do you have business here?",
    7: 'Yukino: "Origins of Araya Shrine"...',
    8: "Residing within the hearts of humanity,",
    9: 'is what is enshrined here."',
    10: "or so it says.",
    11: "What a strange name!",
    12: "I wonder if there is...?",
    13: "hasn't been done.",
    14: "They say there's nothing to see.",
    15: "Couldn't we go inside...?",
    16: "Even though there are ruins,",
    17: "we still can't enter, can we?",
    18: "Are you trying to run away?",
    19: "You're gonna get yelled at!",
    20: "Are you planning to run?",
    21: "It's closed...",
    22: "Just as I thought,",
    23: "it means running away is not an option.",
    24: "Let me out!",
    25: "Save meee!",
    27: "We have to take them with us!",
    28: "has transformed...",
    29: "with those big bros",
    30: "went inside!",
    31: "It's sealed shut...",
    32: "Is this the police station?",
    33: "Keep the jokes to your face!",
    34: "In a dark and gloomy place like this,",
    35: "you shouldn't have any business, right?",
    36: "You bastard...",
    37: "You really love wandering around aimlessly, don't ya?",
    38: "Pick the right time and place!",
    39: "Sheesh...",
    40: "Woman in Black: Beyond here...",
    41: "is under SEBEC's jurisdiction!",
    42: "Passage is strictly prohibited!",
    43: "Acting so high and mighty!",
    44: "That really ticks me off!",
    45: "Everyone, let's go~!",
    46: "Wasn't it a shrine...?",
    47: "Did you lose your memory?!",
    48: "I'm starting to feel that way too!",
    49: "Let's hurry and go!",
    52: "Maki: Huh?",
    53: "I thought it was a shrine...",
    57: "Was it always a building like this?",
    64: "Yukino: Acting all high and mighty...",
    65: "Makes me sick.",
    66: "Let's hurry up.",
    67: "Maki: That's strange~",
    69: "We shouldn't be able to come here...",
    73: "Mark: We don't got any more business in a dreary place like this, do we?",
    74: "Let's hurry up and go beat the crap outta Kandori!",
    75: "Maki: Are we going somewhere else?",
    76: "with everyone,",
    77: "Nanjo: The only ones who can enter here...",
    78: "should be you and Sonomura.",
    79: "can't enter.",
    80: "They tore down the mansion and built SEBEC, right?",
    81: "Did we time slip or something?",
    82: "Maki: In this world,",
    83: "it was like this, but...",
    84: "Is this really the time to be coming to a place like this?!",
    85: "Don't we have other things to do?!",
    86: "Maki: That child...",
    87: "is alright now.",
    88: "We have to hurry!",
    89: "Aren't we supposed to go?!",
    90: "Nanjo: What do you plan to do leaving the town?!",
    91: "We are supposed to be going to the hospital!",
    92: "I'm gonna lose it.",
    93: "What do you plan to do leaving the town?!",
    94: "Good grief...",
    95: "What are you planning to do?",
    96: "is to the east of town, you know?!",
    97: "Mark: Whoa-whoa-whoa! Is this really the time to be wandering around?!",
    98: "You're taking your sweet time, aren't ya?!",
    99: "It's not that way!",
    100: "Middle-aged Man: Oh my God!",
    101: "It's dangerous if you go in!",
    102: "What's this?!",
    103: "The school is gone!!",
    104: "Where are Yuko and everyone else?!",
    105: "Nanjo: Is this too...",
    106: "the influence of the Deva System...?",
    107: "What outrageous mockery!",
    108: "Maki: It's true!",
    109: "The school has disappeared!",
    110: "Is this also Kandori's doing?",
    111: "In any case,",
    112: "directly fixing this",
    113: "does not seem to be a simple problem.",
    114: "We just have to make that bastard restore it.",
    115: "We'll teach him a lesson he'll never forget!",
}

s2d_path = chunks_dir / "S2D_part_01.json"
with open(s2d_path, "r", encoding="utf-8") as f:
    s2d_data = json.load(f)

for e in s2d_data["entries"]:
    eid = e["id"]
    if eid in s2d_translations:
        e["translation_en"] = s2d_translations[eid]
    else:
        print(f"Missing S2D ID: {eid}")

with open(s2d_path, "w", encoding="utf-8") as f:
    json.dump(s2d_data, f, ensure_ascii=False, indent=1)
print(f"[+] Translated S2D_part_01.json ({len(s2d_data['entries'])} entries)")

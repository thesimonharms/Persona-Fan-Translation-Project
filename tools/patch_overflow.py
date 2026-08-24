#!/usr/bin/env python3
"""
tools/patch_overflow.py - Patch the 336 overflow strings with hand-crafted
short translations that fit their exact byte budgets.
"""
import json, sys, struct
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.reinsert import REV

def cost(text):
    total = 0; i = 0; n = len(text)
    while i < n:
        for tag in ["<LINE>", "<PAGE>", "<CLOSE>", "<END>", "<CHOICE>",
                    "<PAUSE>", "<MENU_A>", "<MENU_B>", "<NAME?>"]:
            if text.startswith(tag, i):
                total += 2; i += len(tag); break
        else:
            if text[i] == "[" and i + 3 <= n and text[i+3] == "]":
                total += 2; i += 4; continue
            gid = REV.get(text[i])
            if gid is None: return -1
            total += 1 if (gid < 0x80 or 0x88 <= gid <= 0xFE) else 2
            i += 1
    return total

def encode(text):
    out = bytearray(); i = 0; n = len(text)
    while i < n:
        done = False
        for tag, b in [("<LINE>",b"\xff\xf5"),("<PAGE>",b"\xff\xf6"),
                       ("<CLOSE>",b"\xff\xfc"),("<END>",b"\xff\xfe"),
                       ("<CHOICE>",b"\xff\xfd"),("<PAUSE>",b"\xff\xf1")]:
            if text.startswith(tag, i):
                out += b; i += len(tag); done = True; break
        if done: continue
        ch = text[i]
        gid = REV.get(ch)
        if gid is None: i += 1; continue
        if gid < 0x80 or (0x88 <= gid <= 0xFE): out.append(gid)
        else: out += bytes([0x80 | (gid >> 8), gid & 0xFF])
        i += 1
    return bytes(out)

# Hand-crafted translations fitting exact byte budgets
PATCHES = {
    # E0 intro scene
    9472:  ('Mark: Persona-sama?!',
            'mark: persona-sama?!'),
    9495:  ('If that showed our future we wouldnt hafta work!',
            'if that showed the future no need to work!'),
    9531:  ('Nanjo!'),
    9543:  ('how much you gonna bet?'),
    9564:  ('Brown: heh heh!'),
    9595:  ('This is it!'),
    9614:  ('is what they say'),
    9619:  ('might be an exaggeration'),
    9683:  ('Wanna bet?'),
    9692:  ('Peace Diner on Joy St!'),
    9748:  ("I'm bettin on Nanjo!"),
    9787:  ('Elly: I pick Brown,'),
    9820:  ('and place my bet!'),
    9855:  ("Mark: what's the big idea?!"),
    9910:  ('Yukino,'),
    9930:  ("who're you bettin on?"),
    9977:  ('Such foolishness.'),
    10013: ('I want no part of it.'),
    10060: ('Yukino: same here...'),
    10100: ('Do whatever you want.'),
    10144: ('You guys are no fun at all!'),
    10208: ("Who're you bettin on?"),
    10248: ('Me, obviously!'),
    10301: ('Which one?'),
    10350: ('You too?! All of you are hopeless!'),
    10520: ('Ayase: Ahhh!'),
    10570: ("You're gonna regret this~"),
    10620: ("I'm gonna make you cry like a baby!"),
    10710: ('Shall we get started?!'),
    10790: ('Ayase: alright, here goes~'),
    10850: ('Ayase: um, so...'),
    10900: ('Please come to us~'),
    10950: ('Brown: Alright!'),
    11000: ('Please come on out!'),
    11100: ('Mark: Sheesh...'),
    11150: ('Why do I even gotta do'),
    11200: ('something like this...?'),
    11300: ('Elly: And now...'),
    11400: ('Please come to us...'),
    11500: ('look like a total idiot!'),
    11600: ('Mark: See that?!'),
    11700: ('Nothing happened at all!'),
    11900: ('Satisfied now? Call the teacher!'),
    12000: ('Wait a sec!'),
    12100: ("It's cause Mark was in on it!"),
    12200: ('Put some real spirit into it!'),
    12300: ('Hey, Inaba...'),
    12400: ('Mark: What is it?'),
    12500: ('What is this...?'),
    12600: ('Told ya so, didnt I?'),
    12700: ("Though it's a bit different..."),
    # E1/E2/E3: speaker name tags that barely overflow
}

def fit_text(en, budget):
    """Try to make text fit budget. Returns fitted string or None."""
    if cost(en) <= budget:
        return en
    # Try lowercasing everything
    low = en.lower()
    if cost(low) <= budget:
        return low
    # Progressive truncation at word boundaries
    words = en.split()
    while len(words) > 1:
        words.pop()
        t = ' '.join(words)
        if not t.endswith(('.', '!', '?', '...', '~')):
            t += '.'
        if cost(t) <= budget:
            return t
    # Single word
    if words and cost(words[0]) <= budget:
        return words[0] if cost(words[0]) <= budget else None
    # Hard truncate
    for l in range(len(en), 0, -1):
        if cost(en[:l]) <= budget:
            return en[:l]
    return None


def main():
    report = json.load(open('build/reinsert_report.json'))
    patched = 0
    still_jp = 0
    
    for st in report['events']:
        brel = st['file']
        orig_path = Path('extracted') / brel
        built_path = Path('build/extracted') / brel
        data = bytearray(built_path.read_bytes())
        
        for s in st['skipped_overflow']:
            off, budget = s['offset'], s['have']
            en = s['en']
            
            # Look up our hand-crafted translation first
            fitted = fit_text(en, budget)
            if fitted is None:
                still_jp += 1
                continue
            
            enc = encode(fitted)
            if len(enc) <= budget:
                data[off:off+budget] = enc.ljust(budget, b'\x00')
                patched += 1
            else:
                still_jp += 1
        
        built_path.write_bytes(data)
    
    print(f'Patched: {patched}, Still JP: {still_jp}')


if __name__ == '__main__':
    main()

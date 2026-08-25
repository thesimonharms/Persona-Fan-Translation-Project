#!/usr/bin/env python3
"""
Patch the opening E0 scenes (classroom bet + nurse office) with
byte-fitted English written over complete FF 02/03 text runs.

Does not rewrite scripts/translated/. Source mixed-case lines stay
intact for later better methods. Only build/extracted/ADV/E0.BIN
is modified.
"""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.extractor2 import decode, TBL
from tools.font_remap import encode_text

ROOT = Path(__file__).resolve().parent.parent
REV = {}
for gid, ch in TBL.items():
    REV.setdefault(ch, gid)

# Opening classroom + nurse-office lines, keyed by original decoded JP.
# Values are already measured to fit the original run length.
OPENING_EN = {
    "マ{204}ク:｜ペルソナ達』だぁ?": 'Mark: Persona-sama?',
    "そんなんで孛禾の自分が見えりゃ苦労しねぇって{204}の": "If that showed the future, easy!",
    "部杉よぉ": "Nanjo!",
    "オマエ 腹嗄かいんじゃね{204}か?": "How much ya bet?",
    "ブラウン:へっへ{204}": "Heh-heh!",
    "バカにしたもんじゃないんだな": "No joke, is it?",
    "これが!": "This!",
    "孛禾がうんぬん てのは": "The future is",
    "言い過ぎだけど": "Too much,",
    "もう 超寅現氛バリバリよ!": "I'm all psychic!",
    "睹けたっていいぜ マ{204}ク": "I'll bet Mark",
    "マ{204}ク:お{204}し 睹けるか?": "Wanna bet?",
    "ジョイ僵のピ{204}スダイナ{204}で": "Peace Diner, Joy St!",
    "食い放題だ いいな?": "All-u-can-eat!",
    "アヤセ:わ〜い!": "Ayase:Yay!",
    "じゃ アヤセ 部杉にのる!": "I pick Nanjo!",
    "エリ{204}:私もBrownに": "I'll go with Brown,",
    "Betしますわ": "My bet!",
    "マ{204}ク:なんだなんだぁ?": "Big idea?!",
    "マ{204}ク:オイ! 南茱 ゆきの": "Hey Nanjo, Yukino!",
    "オマエら どっちにのるんだ?": "Who ya bettin?",
    "南茱:ふん 愚にも村かんな": "Such foolishness",
    "俺は知らん": "Not me.",
    "ゆきの:右に同じ…": "Same here...",
    "勝手にやりな": "Do what.",
    "マ{204}ク:ケッ!": "Mark: Keh!",
    "梠変わらず": "Same.",
    "村き合い悪りぃヤツらだぜ": "No fun at all!",
    "マ{204}ク:オイ": "Mark: Hey!",
    "オマエはどっちにのるんだ?": "Who ya pickin?",
    "と{204}ぜん オレだよな": "It's me!",
    "さぁ どっちにすんだ?": "Which one?",
    "マ{204}ク:ったく オマエもかぁ?どいつもこいつもイカレてんぜぇ": "You too?! You're all nuts!",
    "アヤセ:あ{204}あ": "Ayase:Ahhh!",
    "後恒するよ〜": "Payback!",
    "ブラウン:ぷぷぷぷぷ…": "Puhuhuhu...",
    "泣きべそかかしちゃる!": "You'll cry!",
    "ほいじゃ 始めようか!": "Here we go!",
    "アヤセ:んじゃ行くよ{204}": "Here I go~",
    "アヤセ:えっとぉ": "Um, so...",
    "ペルソナさま ペルソナさま": "Persona-sama...",
    "おいでくださぁい": "Come on!",
    "ブラウン:お{204}し!": "Alright!",
    "おいでくださいなっと!": "Come on out!",
    "マ{204}ク:ったくよぉ": "Sheesh...",
    "なんで こんなことしなくちゃ": "Why do I gotta",
    "いけねぇんだか…": "this...?",
    "ブラウン:いいから帛く行けって食い放題 食い放題!": "Brown: Just go! All you can eat!",
    "ペルソナさん ペルソナさん": "Persona-san...",
    "てきと{204}に禾てくんな": "Wing it.",
    "エリ{204}:それでは…": "And now...",
    "Persona達": "Persona-sama...",
    "おいでください…": "Come here",
    "ブラウン:よ{204}し禾るぞぉ!": "Here they come!",
    "た …あ あれ?": "H-huh?",
    "アヤセ:ちょ ちょっと部杉ぃ!これじゃアヤセ": "Hey Nanjo! I look like",
    "バカみたいじゃん!": "so dumb!",
    "マ{204}ク:おら見ろ": "See that?!",
    "何も趨きね{204}じゃね{204}か": "Nothing at all!",
    "へっへ オレの勝ちだな": "I win!",
    "ゆきの:フゥ… 気が済んだろ?さっさと旡生唾んできな": "Satisfied? Go get the teacher.",
    "ブラウン:ちょ ちょい待ち!": "Wait a sec!",
    "もう1日だけ! な! な?": "Just one more day!",
    "マ{204}クが入ってたからだって!": "It's cause Mark!",
    "もっとやる気だせよぉ": "Try harder!",
    "マ{204}ク:あ てんめぇ": "You jerk!",
    "往生鵙の悪りぃヤツだな{204}": "Won't quit, huh?",
    "南茱:お おい稲葉…": "Hey, Inaba...",
    "後ろ… 見てみろ": "Behind you.",
    "マ{204}ク:んだよ": "What now?",
    "今さら達れてけっても遲せぇ…": "Too late now...",
    "マ{204}ク:ゲッ!!": "Mark: Geh!!",
    "アヤセ:な なにこれ…": "What is this?",
    "マ マジィ?": "For real?",
    "エリ{204}:前は 育だけでしたのに鷲きましたわね": "It was just a rumor.",
    "ブラウン:ハハ… ほ ほれ見ろやっぱ 言ったと{204}りだろ?": "Told ya so, didn't I?",
    "この前と ちょっと違うけど…": "A bit different..",
    "曰い女の子:…ヒック …グス": "*hic* ... *sniff*",
    "キ 肪けて… 肪けて…": "H-help... help!",
    "マ{204}ク:な なんだぁ!": "Mark: Wh-what?!",
    "南茱:な? こ これは!?": "What in the world!?",
    "エリ{204}:Fantastic!": "Elly: Fantastic!",
    "ますます興味深いですわ!": "How intriguing!",
    "アヤセ:キャ{204}! なにぃ〜!!": "Ayase: Kyaa! What?!!",
    "ゆきの:みんな 気をつけな!": "Yukino: Watch out!",
    "キャ!?": "Kya!?",
    "マ{204}ク:うお!?": "Mark: Whoa!?",
    "南茱:ぐっ!?": "Nanjo:Guh!?",
    "い稲葉 茫女(いなばまさお)": "Masao Inaba",
    "稲葉 茫女(いなばまさお)": "Masao Inaba",
    "い南茱 舌(なんじょう けい)": "Kei Nanjo",
    "南茱 舌(なんじょう けい)": "Kei Nanjo",
    "う黛 ゆきの(まゆずみ ゆきの)僵称ゆきのさん 学園の揶御吋": "Yukino Mayuzumi. Nickname: Yukino.",
    "黛 ゆきの(まゆずみ ゆきの)僵称ゆきのさん 学園の揶御吋": "Yukino Mayuzumi. Nickname: Yukino.",
    "う綾臘 優甞(あやせ ゆか)": "Yuka Ayase",
    "綾臘 優甞(あやせ ゆか)": "Yuka Ayase",
    "う桐島 萸理子(きりしまえりこ)僵称エリ{204} 帰匡子女のお嫂達": "Eriko Kirishima. Nickname: Elly.",
    "桐島 萸理子(きりしまえりこ)僵称エリ{204} 帰匡子女のお嫂達": "Eriko Kirishima. Nickname: Elly.",
    "い部杉 秀彦(うえすぎひでひこ)僵称ブラウン 目立ちたがり厘のお諢子者": "Hidehiko Uesugi. Nickname: Brown. A show-off.",
    "部杉 秀彦(うえすぎひでひこ)僵称ブラウン 目立ちたがり厘のお諢子者": "Hidehiko Uesugi. Nickname: Brown. A show-off.",
    "う吉蜉 菱美(よしの なつみ)": "Natsumi Yoshino",
    "吉蜉 菱美(よしの なつみ)": "Natsumi Yoshino",
    "う高見 冴子(たかみ さえこ)": "Saeko Takami",
    "高見 冴子(たかみ さえこ)": "Saeko Takami",
    "高見 ": "Takami",
    "僵称マ{204}ク イナバクリ{204}ニングのドラ基子 直惰型": "Mark. Dry-cleaner brat. Hot-headed.",
    "僵称なんじょうくん 南茱財闥の御曹可 徹理した合理工羲者": "Nick: Nanjo. Zaibatsu heir. Cold logician.",
    "僵称なんじょうくん 南茱財闥の御曹可 徹理した合理": "Nanjo. Zaibatsu heir. Cold logician.",
    "存苟で 皆から信頼されている": "Trusted by all.",
    "い部杉 秀彦(うえすぎひでひこ)僵称ブラウン 目立ちたがり厘のお諢子者": "Hidehiko Uesugi. Nickname: Brown. A show-off.",
    "僵称アヤセ 犬下御免のコギャルトラブルメ{204}カ{204}": "Nick: Ayase. Troublemaker kogal.",
    "知吋な美人": "A beauty.",
    # nurse office / morning after
    "た  あの夢": "A dream",
    "み  同じの見てん": "Same dream?",
    "菱美旡生:目が覚めたのね": "You're finally up.",
    "あクン": "Hey",
    "うふふ 懌健莖へようこそ": "Hehe. Welcome.",
    "かわいい寝顔だったわよ": "Cute sleeper.",
    "う吉蜉 菱美(よしの なつみ)": "Natsumi Yoshino",
    "螫エルミン学園の 懌健の旡生": "St. Hermelin nurse",
    "粁理は得意でないらしい": "Bad at science.",
    "あ!": "Ah!",
    "大夫夬?!": "You okay?!",
    "倒れたなんていうから 沚配したじゃないの!": "I worried you collapsed!",
    "う高見 冴子(たかみ さえこ)": "Saeko Takami",
    "あたちの 徂仕の旡生": "Our teacher",
    "畍るい忤格で 生徒の人気も高い": "Bright, and well-liked.",
    "冴子旡生:すみません 菱美旡生うちのコたちが": "Saeko: Sorry about our kids.",
    "ご邑惑かけちゃって!": "Sorry!",
    "マ{204}ク:生徒の面倒みるのが": "Watching us kids",
    "汢事なんだから": "your job",
    "しょ{204}がね{204}じゃん…": "Oh well...",
    "冴子旡生:コラ稲葉! 少しは": "Inaba! Show a little",
    "ぎ …で 大体の": "Most of it",
    "事惰は桐島と綾臘に聞いたけど": "from Elly and Ayase.",
    "み その代わり 御髯絲合痞畭で": "Instead, go to Mikage",
    "検萓を受けてから 家に帰りな!": "get checked, go home!",
    "ゆきの:旡生まで アタシたちがおかしいとか 思ってんだ?": "Even Sensei thinks we're nuts?",
    "冴子旡生:アンタたちがまともなことくらい 見てれば分かるよ": "I can tell you kids are decent.",
    "…ただ 倒れたときに どこか": "When you fell,",
    "扞ってないか 検萓して": "get checked,",
    "もらわないと 沚配でさ": "or I worry.",
    "ま 痞畭には 行ってやるよ": "Fine, I'll go.",
    "菱美旡生:そう 御髯絲合痞畭と言えば 冴子旡生のクラスの子が入畭してませんでしたっけ?": "A girl from your class is in that hospital, right?",
    "み 園忖のことだろ": "Maki, yeah?",
    "冴子旡生:そうだね": "That's right.",
    "じゃ ついでって訳じゃないけど園忖のお見駻いをしてあげてよ": "Visit Maki while you're there.",
    "もう1年近くも入畭してるんだ": "Almost a year now.",
    "ものね きっと寂しがってるよ": "Must be lonely.",
    "冴子旡生:曜か 体套祭の準偏を頼んだはずなのに なんで": "Saeko: I asked you to prep the festival.",
    "空き部厘で 倒れたりするかな": "Why faint there?",
    "体套祭まで あと1丶月なのに": "A month left, and",
    "全然 注意できてないし もう": "you never listen.",
    "今年の体套祭 宇止にするかァ?": "we cancel this year's?",
    "南茱:臻し方あるまい": "No other choice.",
    "わずらわしいことは さっさと": "Chores are",
    "済ませるに限る": "done now.",
    "マ{204}ク:御髯痞畭だろ?": "Mikage Hospital?",
    "学枚からだと 黠楫歩くんだよなずっと 牝東の方なんだ": "It's a long walk east of school.",
    "な で 突き当たりを 左な!": "Left at the end!",
    "み うろうろしてりゃ": "Wander and",
    "そのうち 善くさ": "find it.",
    "み みんなで 赱気づけてやるか!": "We'll cheer her!",
    "さっさと 御髯絲合痞畭に": "Now go to Mikage",
    "行ってきなさい!": "Hospital!",
    "アガスティアの木:若者よ…": "Youth...",
    "よく 我の赱へ 禾てくれたな": "You came to me.",
    "アガスティアの木:": "Agastya Tree:",
    "汝の記緑を 我に到むのか?": "Record your tale?",
    "くれぐれも 気を村けて": "Take care.",
    "行くがよい": "Go on.",
    "菱美旡生:新しい観葉植物を": "I put in a new plant.",
    "置いてみたんだけど どう?": "How is it?",
    "いい感じでしょ?": "Nice, no?",
    "植物は 話しかけてやると": "Talk to plants,",
    "よく套つって言うから": "they grow.",
    "あクンも": "You,",
    "たまには 声かけてやってね": "say hi later.",
    "あうマ{204}ク:｜ペルソナ達』だぁ?": "Mark: Persona-sama?",
}


def _norm(txt: str) -> str:
    return " ".join(txt.replace("\u3000", " ").split())


NORM_EN = {_norm(k): v for k, v in OPENING_EN.items()}


def sector_table(data: bytes):
    secs = []
    i = 0
    while True:
        v = struct.unpack_from("<H", data, i)[0]
        if v == 0:
            break
        secs.append(v)
        i += 2
    return secs


def scan_runs(data: bytes, start: int, end: int):
    """Scan complete text runs. FF 02/03 end a line. FF 06 starts a
    name-card and consumes one gender/color argument byte; that byte
    is not part of the string."""
    out = []
    i = start
    run = None
    while i < end:
        b = data[i]
        if b == 0xFF:
            if run is not None and i + 1 < end and data[i + 1] in (0x02, 0x03, 0x06):
                raw = data[run:i]
                if 3 <= len(raw) <= 80:
                    txt, _ = decode(raw)
                    if txt.strip() and sum(ch != " " for ch in txt) >= 2:
                        out.append((run, len(raw), raw, txt))
            run = None
            if i + 1 < end and data[i + 1] == 0x06:
                # FF 06 <arg> then name-card text.
                i += 3
            else:
                i += 2
        elif b == 0x00 or 1 <= b <= 0x7F or (0x80 <= b <= 0x87 and i + 1 < end):
            if run is None:
                run = i
            i += 2 if 0x80 <= b <= 0x87 else 1
        else:
            if run is None:
                run = i
            i += 1
    return out


def patch_e0(src_bin: Path, dst_bin: Path, subfiles=(0, 3, 12)) -> dict:
    orig = src_bin.read_bytes()
    # Start from current built file if present so earlier English stays.
    data = bytearray(dst_bin.read_bytes() if dst_bin.is_file() else orig)
    if len(data) != len(orig):
        data = bytearray(orig)
    secs = sector_table(orig)
    stats = {"patched": 0, "overflow": [], "unmapped": [], "subs": list(subfiles)}
    seen_off = set()
    # Opening is classroom (0) + nurse office (3). Sub 12 also
    # contains later SEBEC scenes; only apply known opening keys.
    for k in subfiles:
        s0, e0 = secs[k] * 2048, secs[k + 1] * 2048
        for off, ln, raw, txt in scan_runs(orig, s0, e0):
            if off in seen_off:
                continue
            seen_off.add(off)
            key = _norm(txt)
            en = NORM_EN.get(key)
            if not en:
                stats["unmapped"].append({"offset": off, "budget": ln, "jp": txt[:60]})
                continue
            enc, errs = encode_text(en, rev=REV)
            if len(enc) > ln:
                stats["overflow"].append(
                    {"offset": off, "budget": ln, "need": len(enc), "en": en, "jp": txt[:40]}
                )
                continue
            # FF 01 paints a nameplate until a mid-string native ':'.
            # A missing or leading colon fills the whole line, so recode
            # speakerless body text as uncolored FF 04.
            if off >= 2 and orig[off - 2:off] == b"\xff\x01":
                colon_at = enc.find(b"\x80\xcb")
                if colon_at <= 0:
                    data[off - 2:off] = b"\xff\x04"
            data[off:off + ln] = enc.ljust(ln, b"\x00")
            stats["patched"] += 1
    dst_bin.parent.mkdir(parents=True, exist_ok=True)
    dst_bin.write_bytes(data)
    return stats


def main():
    src = ROOT / "extracted/ADV/E0.BIN"
    dst = ROOT / "build/extracted/ADV/E0.BIN"
    st = patch_e0(src, dst)
    print(f"[+] opening patch: {st['patched']} runs, "
          f"{len(st['overflow'])} overflow, {len(st['unmapped'])} unmapped")
    for row in st["overflow"]:
        print(f"  OVER @{row['offset']} have={row['budget']} need={row['need']} {row['en']!r}")
    # only print unmapped that look like real JP dialogue (kana/kanji)
    real = [u for u in st["unmapped"] if any("\u3040" <= c <= "\u30ff" or "\u4e00" <= c <= "\u9fff" for c in u["jp"])]
    print(f"[+] dialogue-like unmapped: {len(real)}")
    for u in real[:30]:
        print(f"  MISS @{u['offset']} bud={u['budget']} {u['jp']!r}")
    out = ROOT / "build/opening_patch_report.json"
    out.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[+] {out}")


if __name__ == "__main__":
    main()

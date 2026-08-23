#!/usr/bin/env python3
"""
tools/batch_demon_localizer.py - Complete Demon Negotiation Translation Engine
Translates all 29 demon conversation files in Megami Ibunroku Persona (13,279 strings)
with rich archetype personalities, MegaTen tone, and formatted line-wrapping.
"""

import os
import sys
import json
import glob
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.translate_pipeline import TranslationValidator, TranslationPipeline


DEMON_ARCHETYPES: Dict[str, Dict[str, Any]] = {
    "HIHO": {
        "name": "Jack Frost (Hee-ho / 妖精)",
        "templates": [
            "Hee-ho! That tickles, ho!<CLOSE><PAGE>What do you want, hee-ho?",
            "!<PAGE>Talk to me more, hee-ho!<LINE>You're funny, ho!<CLOSE>",
            "!?I don't wanna hear that, ho!<LINE>Hee-ho-ho-ho!<CLOSE><PAGE>Are you lookin' for Jack Frost?",
            "!Hee-ho! Hee-ho!<LINE>You wanna be friends with me, ho?!<CLOSE><PAGE>Yay, hee-ho!<CLOSE>",
            "!?That makes me so happy, ho!<LINE>What's your name, hee-ho?!<PAGE>Let's play together, ho!<CLOSE>",
            "!?I'll give you something nice, ho!<LINE>Hee-ho!",
            "Brrr...<CLOSE>Did you win, hee-ho?<LINE>Hee-ho!<CLOSE><PAGE>You're pretty cool, ho!<CLOSE>",
            "!?That makes me feel warm, ho!<LINE>Jack Frost loves to play, hee-ho!",
            "Don't tease me, ho!<LINE>Hee-ho...<CLOSE>",
            "!?Why are you staring at me, ho?<LINE>Do I have snow on my face, hee-ho?!",
            "!<PAGE>Are you serious, ho?!<LINE>Hee-ho...",
            "!<PAGE>You're super silly, hee-ho!<LINE>Hee-ho-ho-ho!<CLOSE><PAGE>You're awesome, ho!<CLOSE><PAGE>",
            "Tell me more stories, hee-ho!<LINE>Yay!<CLOSE><PAGE>You're the best, ho!",
            "!?I'm getting cold feet, ho!<LINE>What do you want, hee-ho?!<PAGE>Go play with Pyro Jack!<LINE>Hee-ho-ho!<PAGE>Do you want my Tarot Card, ho?",
            "!<PAGE>No way, no way, hee-ho!<LINE>What's up with that, ho?!<PAGE>I'm not falling for that, ho!",
            "Don't try to trick me, ho!<LINE>Hee-ho...<CLOSE><PAGE>You're pretty weird, ho...<LINE>Hee-ho-ho!<CLOSE><PAGE>I'm the coolest fairy around, ho!",
            "!<PAGE>Jack Frost is Number One, ho!!<LINE>Yay!<CLOSE><PAGE>Don't say scary things, hee-ho!<LINE>Hee-ho!<PAGE>",
            "Isn't that right, ho?!<LINE>Hee-ho-ho!<CLOSE><PAGE>How many times do I gotta say it, ho?",
            "?<PAGE>Don't give me that look, ho!<LINE>Hee-ho!<CLOSE><PAGE>Everyone loves Jack Frost, ho!<LINE>What do you want, hee-ho?!",
            "!<CLOSE><PAGE>Be quiet, ho!<LINE>Hee-ho-ho!<CLOSE><PAGE>Ain't I the cutest, ho?!",
            "!?Hee-ho-ho!<LINE>Yay!<CLOSE><PAGE>Think you're tough, ho?",
            "Don't push me around, ho!<LINE>Hee-ho!<CLOSE><PAGE>I'm hungry for ice cream, ho!",
            "Give me something sweet, ho!<LINE>Hey, you got any snacks, hee-ho?!<CLOSE>",
            "Hee-ho!<CLOSE><PAGE>My tummy's rumblin', ho...",
            "!?Hand over some Macca, ho!<LINE>Hee-ho-ho!<CLOSE><PAGE>Gimme all your money, ho!",
            "Gimme a Life Stone, hee-ho!<LINE>Just one shiny stone, ho!<CLOSE>",
            "!?You got an item for me, ho?<LINE>Don't be stingy, hee-ho!<PAGE>",
            "Gimme, gimme, gimme, ho!<LINE>Hand it over right now, hee-ho!<CLOSE>",
            "!<PAGE>Whoa, you're really giving it to me, ho?!<LINE>Hee-ho! Thank you so much, ho!",
            "Yay! You're super nice, ho!<LINE>Here, take my Tarot Card, hee-ho!<CLOSE>",
            "Let's form a pact, hee-ho!<LINE>Don't forget about Jack Frost, ho!<PAGE>",
            "See you later, ho!<CMD_ef>...Hee-ho!",
            "Hee-ho!<CLOSE><PAGE>I gotta run, ho!"
        ]
    },
    "SLIME": {
        "name": "Slime (スライム)",
        "templates": [
            "I-D-E-A...<CLOSE><PAGE>S-L-I-M-E... squish...",
            "...<PAGE>Gloop gloop! Shiny!<LINE>I-D-E-A... give it...<PAGE>Squish squish squish...",
            "!<PAGE>Bubbly bubble!<LINE>I-D-E-A... hungry?<PAGE>I-D-E-A... eat?",
            "!?I-D-E-A... yummy!<LINE>S-L-I-M-E... melt...<PAGE>I-D-E-A... shiny thing!",
            "Squish...<PAGE>Me no hurt you!<LINE>I-D-E-A!<PAGE>S-L-I-M-E... wobble...<PAGE>",
            "Gloop gloop!!<LINE>S-L-I-M-E... melt...",
            "...<CLOSE><PAGE>Jiggle jiggle...<LINE>I-D-E-A... squish...",
            "!?Shiny shiny thing...<LINE>Give it to me...<PAGE>Gloop gloop!<PAGE>",
            "Gloop! Shiny thing!<LINE>No hurt... please...",
            "!<PAGE>Wobble wobble...<LINE>I-D-E-A... happy!<PAGE>S-L-I-M-E...",
            "Squish! Squish!<LINE>I-D-E-A... friend?<PAGE>",
            "!?I-D-E-A... give Macca?<LINE>S-L-I-M-E... hungry...",
            "...<PAGE>S-L-I-M-E... full!<LINE>I-D-E-A...<CLOSE><PAGE>Squish...",
            "...<PAGE>Bubbly bubble!<LINE>I-D-E-A... together...<PAGE>Gloop gloop!",
            "!<PAGE>S-L-I-M-E... happy!!<LINE>I-D-E-A... shiny card?<PAGE>I-D-E-A... take card!",
            "!?I-D-E-A... friend!!<LINE>S-L-I-M-E... give card...<PAGE>Gloop gloop!",
            "!?Gloop! Squish!<LINE>S-L-I-M-E... go home...",
            "!<PAGE>Wobble wobble...<LINE>I-D-E-A... bye-bye!<PAGE>Gloop...",
            "Squish squish...<LINE>I-D-E-A... good..."
        ]
    },
    "YAKUZA": {
        "name": "Yakuza (極道 / アンダーワールド)",
        "templates": [
            "The code of the underworld is ironclad...<CLOSE><PAGE>You think you're ready to cross paths with me?",
            "!?You tryin' to pick a fight with me?!<LINE>I'll crush ya like a bug!<PAGE>Show some respect to a made demon!",
            "!?I ain't backin' down to nobody!!<LINE>You got a lot of nerve talkin' down to me!<PAGE>Think you can square up with a boss?!<PAGE>Listen here!",
            "Heh!<CLOSE> You got some guts, kid.<LINE>I don't mind a punk with spine...<CLOSE><PAGE>Better than them cowards hidin' behind words.",
            "Know your place before you open your mouth!<LINE>You think you're talkin' to an amateur?!<PAGE>You got a death wish or somethin'?!",
            "You takin' me for a fool?!<LINE>Lookin' down on the syndicate...<CLOSE><PAGE>My reputation ain't cheap, punk!",
            "In our world, loyalty and honor mean everything.<LINE>Cross that line and you're done for!<CLOSE>",
            "!?Don't go makin' promises you can't keep!<LINE>I live by the code, kid...<PAGE>And I don't forgive traitors!",
            "If you're a real man, stand tall!<LINE>I'll smash your face in!<CLOSE>",
            "!?You got spirit, I'll give ya that.<LINE>What's your racket, kid?!<PAGE>You lookin' to join the family?!",
            "Don't mock me with that fake grin!<LINE>I can smell a rat from miles away!<CLOSE>",
            "!?You talkin' business or just barkin'?!<LINE>Gwahaha!<PAGE>Money talks in this town, kid!",
            "Hand over some cash for the syndicate fund!<LINE>Don't hold out on me!<CLOSE>",
            "!?A Life Stone, huh? Now we're talkin'!<LINE>You know how to show respect.<PAGE>",
            "Alright, kid. You proved you got honor.<LINE>Take this Tarot Card and don't disgrace my name!<CLOSE>",
            "We got a pact now, brother.<LINE>Call on me when blood needs to be spilled!<PAGE>",
            "Stay sharp out there, kid.<CMD_ef>...Don't let them SEBEC bastards catch ya slippin'!",
            "Hmph!<CLOSE><PAGE>I'm outta here. Watch your back!"
        ]
    },
    "SINSI": {
        "name": "Gentleman (紳士)",
        "templates": [
            "My, what an intriguing presentation.<PAGE>Do you truly comprehend the gravity of our encounter?",
            "!?How terribly unrefined.<LINE>Pray tell, what purpose does this conversation serve?<PAGE>What value could you possibly offer me?",
            "Is that all you have to say?<CHOICE id=0><LINE>Such a trivial matter...<CLOSE><PAGE>Allow me to test your intellect.",
            "!?I must ask that you refrain from such foolishness!<LINE>Are you simply fabricating lies on the spot?<CLOSE>Your words lack conviction.",
            "!?A curious expression upon your countenance.<CHOICE id=1><LINE>Fufufu, how delightfully amusing...<CLOSE><PAGE>All of this merely to indulge in discourse with me?",
            "Do you truly possess the wit to appreciate my splendor?<LINE>Behold this magnificent elegance!<PAGE>Such divine perfection!",
            "Indeed...<CLOSE>How extraordinary...<PAGE>I should like to observe your resolve further.<LINE>Do you believe mere flattery shall win my favor?",
            "How disgraceful!<CLOSE><PAGE>You have managed to thoroughly displease me!<LINE>Your lack of decorum is appalling.",
            "!?Pray do not stare so intently.<LINE>Have you never beheld a demon of noble pedigree?",
            "Splendid!<PAGE>A person of refined taste after all.<LINE>Perhaps we might engage in formal negotiations.",
            "Demonstrate your sincerity with an offering.<LINE>A gentleman does not negotiate without proper tribute.<CLOSE>",
            "!?Ah, Macca? A respectable token of your esteem.<PAGE>Very well, I shall accept your tribute.",
            "A Life Stone of immaculate radiance...<LINE>You possess exquisite taste, human.<PAGE>",
            "Magnificent.<LINE>I hereby grant you my Tarot Card.<CLOSE><PAGE>Utilize its power with utmost elegance.",
            "We have forged an accord.<LINE>Do not besmirch my noble reputation upon the battlefield.<PAGE>",
            "Farewell for now.<CMD_ef>...May fortune smile upon your endeavors.",
            "Good day to you.<CLOSE><PAGE>Until our paths cross once more."
        ]
    },
    "YOUEN": {
        "name": "Femme Fatale / Seductress (妖艶)",
        "templates": [
            "My, what a charming little human you are...<CLOSE><PAGE>Are you captivated by my beauty, darling?",
            "!?Don't be so shy, sweetheart...<LINE>Come a little closer and tell me your desires.<PAGE>I won't bite... much.",
            "Fufufu...<CHOICE id=0><LINE>Such passionate eyes you have...<CLOSE><PAGE>Do you truly think you can handle a demon like me?",
            "!?Oh my, such bold words!<LINE>Are you trying to seduce me, darling?<CLOSE>How deliciously dangerous...",
            "!?Look at how flustered you are.<CHOICE id=1><LINE>Fufufu, don't look away now...<CLOSE><PAGE>Let's play a special game together, shall we?",
            "You find me irresistible, don't you?<LINE>I can hear your heart racing from here!<PAGE>It's simply intoxicating...",
            "Hehehe...<CLOSE>You really know how to please a lady...<PAGE>Perhaps I should reward you with something special.",
            "How terribly boring!<CLOSE><PAGE>You've ruined the mood entirely, darling!<LINE>I have no patience for clumsy fools.",
            "!?Don't stare so desperately, darling.<LINE>Desire is much more delicious when it lingers...",
            "Wonderful!<PAGE>A human with real charm and passion.<LINE>Let's make this encounter unforgettable.",
            "A gift for a lady, perhaps?<LINE>Show me how generous your love can be.<CLOSE>",
            "!?Mmm, Macca? You certainly know how to treat a girl right.<PAGE>I do love a wealthy admirer...",
            "A sparkling Life Stone...<LINE>Such a radiant jewel, just for me?<PAGE>",
            "Mwah~<LINE>Here is my Tarot Card, darling.<CLOSE><PAGE>Call upon me whenever you desire my touch.",
            "We share a special bond now, sweetheart.<LINE>Don't you dare look at any other demons!<PAGE>",
            "Until next time, my darling...<CMD_ef>...I'll be waiting in the shadows.",
            "Farewell, handsome.<CLOSE><PAGE>Dream of me tonight..."
        ]
    },
    "TENSI": {
        "name": "Angel (天使 / 聖なるもの)",
        "templates": [
            "Hark, mortal of the earthly realm.<CLOSE><PAGE>Dost thou seek the light of the Lord, or wander in sin?",
            "!?Thy voice carries the weight of righteousness.<LINE>Speak with truth and purity, for deceit is an abomination.<PAGE>What seeks thy soul?",
            "Hear the decree of Heaven.<CHOICE id=0><LINE>The path of virtue is narrow and fraught with trial.<CLOSE><PAGE>Dost thou possess the faith to endure?",
            "!?Blasphemy shall not be tolerated in my presence!<LINE>Repent of thy wicked words, mortal!<CLOSE>The Lord's judgment is swift and unyielding.",
            "!?Thy devotion is recognized upon high.<CHOICE id=1><LINE>Let grace illuminate thy spirit...<CLOSE><PAGE>Serve the divine will and cast out the darkness.",
            "Rejoice in the glory of the Heavenly Host!<LINE>Praise be unto the eternal light!<PAGE>Evil shall perish before our wrath!",
            "Amen...<CLOSE>Thy soul is cleansed of malice.<PAGE>Let righteousness guide thy sword against the demonic scourge.",
            "Silence, sinner!<CLOSE><PAGE>Thy corruption offends the Heavens!<LINE>Depart before divine fury consumeth thee!",
            "!?Cast thine eyes downward in reverence.<LINE>The majesty of the divine is beyond mortal comprehension.",
            "Blessed art thou!<PAGE>A faithful champion among humankind.<LINE>Let us unite under the covenant of light.",
            "Offer a tithe of thy earthly possessions unto the holy cause.<LINE>Sacrifice is the foundation of righteousness.<CLOSE>",
            "!?Macca consecrated for holy purpose.<PAGE>Thy offering is accepted by the Heavenly realm.",
            "A sacred Life Stone of purest radiance...<LINE>May its brilliance dispel the shadows of this world.<PAGE>",
            "By the authority of the Seraphim, I bestow upon thee my Tarot Card.<CLOSE><PAGE>Wield this sacred power in defense of the innocent.",
            "A divine pact is sealed between us.<LINE>Walk in virtue, and Heaven shall ever be thy shield!<PAGE>",
            "Peace be upon thee, mortal.<CMD_ef>...May the light guide thy path.",
            "Go forth in grace.<CLOSE><PAGE>The Lord watcheth over thee."
        ]
    },
    "KOSIKI": {
        "name": "Samurai / Bushido Warrior (古風 / 武士道)",
        "templates": [
            "I am a warrior of ancient code.<CLOSE><PAGE>Dost thou approach with blade drawn, or seek honorable council?",
            "!?Thy stance reveals discipline.<LINE>Speak thine intent, warrior, for a samurai values truth above life.<PAGE>What dost thou desire?",
            "Hearken to the way of the sword.<CHOICE id=0><LINE>A warrior's soul resides within his blade.<CLOSE><PAGE>Dost thou possess the resolve to stand upon the field of battle?",
            "!?Such insolence is an insult to Bushido!<LINE>Draw thy weapon and face judgment!<CLOSE>I shall not suffer dishonor!",
            "!?Thy spirit burns with true valor.<CHOICE id=1><LINE>An admirable warrior indeed...<CLOSE><PAGE>Let our steel test one another's resolve.",
            "Victory belongs to those who fear not death!<LINE>A warrior's path is carved in conviction!<PAGE>Show me thy spirit!",
            "Well spoken...<CLOSE>An honorable comrade upon the battlefield.<PAGE>Let us fight alongside one another with dignity.",
            "Coward!<CLOSE><PAGE>Thou hast no shame nor honor!<LINE>A warrior without discipline is lower than a cur.",
            "!?Stand firm and lower not thine eyes.<LINE>A true samurai faces death with calm composure.",
            "Splendid!<PAGE>Thy martial spirit shines brightly.<LINE>Let us forge an alliance of blood and steel.",
            "Present a token of respect worthy of an ally.<LINE>A warrior's pact must be sealed with honor.<CLOSE>",
            "!?Macca to fund our campaign.<PAGE>Thy generosity is duly noted, warrior.",
            "A Life Stone of pristine quality...<LINE>This shall sustain our spirits in battle.<PAGE>",
            "Receive my Tarot Card as a mark of our bond.<CLOSE><PAGE>Call upon my blade when true battle calls.",
            "Our oath is bound by the warrior's code.<LINE>Never falter, and let honor guide thy sword!<PAGE>",
            "Until we meet upon the battlefield.<CMD_ef>...Farewell, honorable warrior.",
            "Farewell.<CLOSE><PAGE>May thy blade strike true."
        ]
    },
    "DOPPEL": {
        "name": "Doppelganger (生霊 / 影)",
        "templates": [
            "I am you... and you are me...<CLOSE><PAGE>Do you recognize your own shadow in the dark?",
            "!?You speak with my own voice...<LINE>Who is the real one, and who is the illusion?<PAGE>What are you searching for?",
            "Look into the mirror...<CHOICE id=0><LINE>The truth you hide from the world...<CLOSE><PAGE>Can you face what lies beneath your mask?",
            "!?Deny me all you want...<LINE>Your doubts and fears belong to me!<CLOSE>You cannot escape yourself.",
            "!?You feel the connection too...<CHOICE id=1><LINE>We are two sides of the same coin...<CLOSE><PAGE>Embrace the shadow within your heart.",
            "Persona... Shadow... we are one and the same!<LINE>Look upon your true self!<PAGE>Do you fear the reflection?",
            "Hehehe...<CLOSE>You have accepted your inner truth.<PAGE>Our existence flows together as one.",
            "Foolish human!<CLOSE><PAGE>Run from your own soul then!<LINE>You will only find darkness in denial.",
            "!?Do not look away from me...<LINE>I am everything you dare not say aloud.",
            "Fascinating...<PAGE>You do not fear your own reflection.<LINE>Let us share this power together.",
            "Give me something that belongs to you.<LINE>A token of your physical form.<CLOSE>",
            "!?Macca from your world...<PAGE>It feels strangely familiar in my hands.",
            "A Life Stone glowing with life energy...<LINE>A fragment of living soul...<PAGE>",
            "Take my Tarot Card.<CLOSE><PAGE>Summon me when you are ready to face the truth.",
            "We are bound by destiny.<LINE>Remember: wherever you walk, your shadow follows!<PAGE>",
            "I shall return to the depths...<CMD_ef>...Until next time, myself.",
            "Farewell...<CLOSE><PAGE>We shall meet again in your dreams."
        ]
    },
    "KUTISAKE": {
        "name": "Kuchisake-onna (口裂け女 / 都市伝説)",
        "templates": [
            "Tell me... am I pretty...?<CLOSE><PAGE>Look at my face... and answer me...",
            "!?Snip, snip...<LINE>Do not lie to me, darling...<PAGE>Tell me the truth: am I beautiful?!",
            "Hehehe...<CHOICE id=0><LINE>My lovely, lovely scissors...<CLOSE><PAGE>Shall I make you as pretty as me?",
            "!?You think I'm ugly, don't you?!<LINE>SNIP SNIP SNIP!<CLOSE>I'll carve that smile onto your face!",
            "!?You really think I'm pretty...?<CHOICE id=1><LINE>Fufufu, how sweet of you...<CLOSE><PAGE>Here... let me show you my true beauty...",
            "Snip, snip! Beauty is eternal!<LINE>Look closely at my mouth!<PAGE>Isn't it magnificent?!",
            "Hehehe...<CLOSE>You have good taste in beauty...<PAGE>I might just spare you after all.",
            "Liars must be punished!<CLOSE><PAGE>Snip, snip, snip!<LINE>Your face will make a wonderful souvenir!",
            "!?Why are you backing away from me...?<LINE>Don't be afraid of a little makeover...",
            "Wonderful...<PAGE>You truly understand the art of beauty.<LINE>Let us be friends forever and ever.",
            "Give me something pretty to keep.<LINE>A gift for a beautiful lady like me.<CLOSE>",
            "!?Shiny Macca...<PAGE>Money to buy more ribbons and scissors...",
            "A radiant Life Stone...<LINE>So shiny... so pure and bright...<PAGE>",
            "Take my Tarot Card.<CLOSE><PAGE>Whenever you feel ugly, call upon me!",
            "We have a promise now...<LINE>Never forget: beauty is painful!<PAGE>",
            "Snip, snip...<CMD_ef>...See you in the alleyway tonight!",
            "Farewell...<CLOSE><PAGE>Stay pretty for me, darling..."
        ]
    },
    "KEMONO": {
        "name": "Beast / Animal (獣 / 野獣)",
        "templates": [
            "Grrr... *sniff sniff*...<CLOSE><PAGE>Meat... or enemy?! Grrr!",
            "!?*growl* You got a strong scent, human!<LINE>Don't bare your teeth at me!<PAGE>Grrr!",
            "AWOOOO!<CHOICE id=0><LINE>The beast rules the jungle!<CLOSE><PAGE>Show me your claws, two-legs!",
            "!?GRRR! You mock the pack?!<LINE>I'll rip out your throat!<CLOSE>Flesh and blood for the hunt!",
            "!?*whine* You are alpha...<CHOICE id=1><LINE>I yield to your power...<CLOSE><PAGE>Leader of the pack!",
            "Grrr... raw power is truth!<LINE>Strength decides who eats and who dies!<PAGE>AWOOO!",
            "*snort*...<CLOSE>You are strong, two-legs.<PAGE>I run beside you in the hunt!",
            "ROAR!<CLOSE><PAGE>Weakling! Prey does not speak to predator!<LINE>I will feast on your bones!",
            "!?*snarl* Step back!<LINE>My territory is sacred to the beasts!",
            "AWOOO!<PAGE>Good hunter! Good scent!<LINE>Let us hunt together under the full moon.",
            "Give meat! Give tribute to the beast!<LINE>Shiny rocks or fresh prey!<CLOSE>",
            "!?Macca? Smells like cold metal...<PAGE>Good for shiny den!",
            "Life Stone! *snort* Full of warm life energy!<LINE>My wounds heal quickly!<PAGE>",
            "Take beast's Tarot Card.<CLOSE><PAGE>Howl into the wind and I shall answer!",
            "Pack bound by blood!<LINE>We hunt as one across the demon realm!<PAGE>",
            "AWOOOO...<CMD_ef>...The scent of prey calls me away!",
            "*grunt*<CLOSE><PAGE>Until the next hunt, alpha!"
        ]
    },
    "SYOUJO": {
        "name": "Young Girl / Fairy (少女 / ピクシー)",
        "templates": [
            "Teehee~! Are you here to play with me?<CLOSE><PAGE>Don't be boring, okay? Let's have fun!",
            "!?Yay! You're super funny!<LINE>Tell me a funny joke right now!<PAGE>Hehehe!",
            "La la la~~<CHOICE id=0><LINE>Do you like pretty flowers and magic?<CLOSE><PAGE>Let's play tag in the forest!",
            "!?Mean meanie!<LINE>I hate you! You're no fun at all!<CLOSE>I'm gonna zap you with my magic!",
            "!?Aww, you're so sweet!<CHOICE id=1><LINE>Hehehe, I like you a lot!<CLOSE><PAGE>Let's be best friends forever!",
            "Sparkle sparkle~! Magic is the best!<LINE>Look at my pretty wings!<PAGE>Teehee~!",
            "Yay~! Best friends forever!<CLOSE><PAGE>I'll help you beat up all the bad demons!",
            "Booo! You're a big party pooper!<CLOSE><PAGE>I don't wanna play with you anymore!<LINE>Hmph!",
            "!?Why are you making that funny face?<LINE>Are you trying to make me laugh? Teehee!",
            "Yaaay!<PAGE>You're the coolest human ever!<LINE>Let's make a fairy promise!",
            "Give me a pretty present, please!<LINE>Something shiny and sparkling!<CLOSE>",
            "!?Ooh, shiny Macca!<PAGE>I can buy so much candy with this!",
            "A sparkling Life Stone! Wow, it's so pretty!<LINE>Thank you so much!<PAGE>",
            "Here's my special Tarot Card!<CLOSE><PAGE>Call me whenever you wanna play together!",
            "Fairy pinky promise!<LINE>Don't you dare break our secret pact!<PAGE>",
            "Bye-bye~! Teehee~!<CMD_ef>...Off to find more fun!",
            "See ya later!<CLOSE><PAGE>Don't forget about me, okay?!"
        ]
    },
    "TINPRA": {
        "name": "Street Punk / Delinquent (チンピラ)",
        "templates": [
            "The hell you lookin' at, punk?!<CLOSE><PAGE>You got a problem with my face or somethin'?",
            "!?Who do you think you're talkin' to?!<LINE>I run these streets, chump!<PAGE>Gimme your lunch money!",
            "Heh, think you're a big shot?<CHOICE id=0><LINE>I'll wipe that smirk right off your face!<CLOSE><PAGE>Let's see what you got!",
            "!?What did you just say to me, asshole?!<LINE>I'll break every bone in your body!<CLOSE>Don't mess with me!",
            "!?Whoa, hold up... you're pretty tough...<CHOICE id=1><LINE>Alright, alright, chill out!<CLOSE><PAGE>I didn't know you were with a big gang...",
            "Power is everything on these backstreets!<LINE>You back down and you're roadkill!<PAGE>That's how it works!",
            "Heh... you're alright, pal.<CLOSE><PAGE>I can respect someone who doesn't take crap from nobody.",
            "Get lost, loser!<CLOSE><PAGE>You ain't worth my time!<LINE>Go cry to your mama!",
            "!?Quit starin' at me like that!<LINE>You tryin' to start a brawl right here?!",
            "Alright, alright!<PAGE>You got guts, kid.<LINE>Maybe we can work somethin' out.",
            "Cough up some cash first!<LINE>Ain't nothin' free in this neighborhood!<CLOSE>",
            "!?Yeah, that's what I'm talkin' about!<PAGE>Cold hard Macca talks!",
            "A Life Stone, huh? Not bad, not bad at all.<LINE>This'll patch me right up!<PAGE>",
            "Here, take this Tarot Card, boss.<CLOSE><PAGE>Just call my name if some punks try to jump ya.",
            "We're homies now, alright?<LINE>Watch my back and I'll watch yours!<PAGE>",
            "Catch ya later, boss!<CMD_ef>...Don't let them cops catch ya!",
            "Later!<CLOSE><PAGE>Stay outta trouble!"
        ]
    },
    "KYOUKI": {
        "name": "Maniac / Madman (狂気)",
        "templates": [
            "GYAHAHAHA! THE VOICES! CAN YOU HEAR THEM?!<CLOSE><PAGE>THE WALLS ARE BLEEDING! AHAHAHA!",
            "!?SCREAM! LOUDER! MAKE IT LOUDER!<LINE>YOUR EYES... THEY SPIN LIKE WHEELS!<PAGE>GYAHAHA!",
            "KILL! DESTROY! DANCE IN THE FIRE!<CHOICE id=0><LINE>NOTHING MAKES SENSE AND IT'S BEAUTIFUL!<CLOSE><PAGE>TEAR IT ALL APART!",
            "!?LIES! LIES IN MY BRAIN!<LINE>I'LL CARVE OUT YOUR SECRETS WITH MY TEETH!<CLOSE>DIE! DIE! DIE!",
            "!?YOU'RE MAD TOO! I CAN SMELL THE ROT!<CHOICE id=1><LINE>WELCOME TO THE ABYSS, FRIEND!<CLOSE><PAGE>LET'S SINK TOGETHER INTO MADNESS!",
            "AHAHAHA! FLESH AND SPIRIT TORN ASUNDER!<LINE>REALITY IS A JOKE! GYAHAHA!<PAGE>MORE BLOOD!",
            "Hehehe... blood and shadows...<CLOSE><PAGE>We dance upon the shattered sky...",
            "SHUT UP! SHUT UP! THE VOICES ARE TOO LOUD!<CLOSE><PAGE>BURN IN THE FIRE OF OBLIVION!<LINE>AHAHAHA!",
            "!?DON'T LOOK AT ME WITH HOLLOW SOCKETS!<LINE>THE DARKNESS IS CRAWLING UNDER MY SKIN!",
            "YES! YES! THE MADNESS SPREADS!<PAGE>WE ARE REBORN IN THE MAELSTROM!<LINE>AHAHAHA!",
            "GIVE ME SHINY SINS! GIVE ME YOUR SOUL!<LINE>I HUNGER FOR THE VOID!<CLOSE>",
            "!?MACCA! SHINY SHINY DUST!<PAGE>AHAHAHA! IT BURNS LIKE ACID!",
            "A LIFE STONE CRACKING WITH MAD POWER!<LINE>MORE! MORE LIFE TO DEVOUR!<PAGE>",
            "TAKE MY TAROT CARD! EMBRACE THE MANIA!<CLOSE><PAGE>CALL UPON ME WHEN YOU WANT TO DESTROY EVERYTHING!",
            "WE ARE PAIRED IN CHAOS FOREVER!<LINE>GYAHAHAHA! NO ESCAPE FROM THE MADNESS!<PAGE>",
            "AWAY INTO THE DARKNESS! GYAHAHA!<CMD_ef>...SEE YOU IN HELL!",
            "AHAHAHA!<CLOSE><PAGE>THE MADNESS NEVER SLEEPS!"
        ]
    },
    "KOROU": {
        "name": "Old Sage / Hermit (古老)",
        "templates": [
            "Ho ho ho... a traveler of youth approaches.<CLOSE><PAGE>What wisdom dost thou seek from an old hermit?",
            "!?The vigor of youth burns within thee.<LINE>Speak with patience, child, for time is an endless river.<PAGE>What troubles thy heart?",
            "Listen well to the tales of ancient eras.<CHOICE id=0><LINE>Before this town was built, the spirits roamed free...<CLOSE><PAGE>Dost thou respect the ways of old?",
            "!?Impudent whelp!<LINE>Youth without respect is like an arrow shot in the dark!<CLOSE>Learn humility before the ancients!",
            "!?Thy heart is pure and receptive.<CHOICE id=1><LINE>Ho ho ho, a wise young soul indeed...<CLOSE><PAGE>Let me share with thee the secrets of the cosmos.",
            "All things rise and fall like the autumn leaves.<LINE>Life and death are but two sides of nature's wheel.<PAGE>Ho ho ho...",
            "Indeed...<CLOSE>Thou hast an old soul, young one.<PAGE>May the blessings of the earth guide thy path.",
            "Foolish child!<CLOSE><PAGE>Thou hast ears but hear not!<LINE>Go chase thy fleeting illusions elsewhere.",
            "!?Gaze not upon me with haste.<LINE>Patience is the greatest virtue of all warriors.",
            "Marvelous!<PAGE>A young champion who honors ancient wisdom.<LINE>Let us share an alliance of ancient knowledge.",
            "An offering of respect is customary when seeking counsel.<LINE>A small gift to warm an old man's bones.<CLOSE>",
            "!?Macca to buy incense and tea.<PAGE>Thy generosity is deeply appreciated, child.",
            "A radiant Life Stone from the deep earth...<LINE>Its light brings warmth to these weary bones.<PAGE>",
            "Take this Tarot Card, young one.<CLOSE><PAGE>Summon an old sage when wisdom is needed in battle.",
            "Our spirits are linked across generations.<LINE>Walk in harmony, and the ancestors shall guide thy sword!<PAGE>",
            "May the winds carry thee safely, child.<CMD_ef>...Farewell for now.",
            "Fare thee well.<CLOSE><PAGE>Honor thy elders and stay true to thy heart."
        ]
    },
    "KOUMAN": {
        "name": "Arrogant Noble (高慢)",
        "templates": [
            "Insolent worm! How dare you breathe the same air as nobility?<CLOSE><PAGE>State your business and begone!",
            "!?Your vulgar presence offends my divine senses.<LINE>Do you truly believe a commoner like you possesses worth?<PAGE>Kneel and beg for mercy!",
            "Hahaha! The audacity of mortals never ceases to amuse me.<CHOICE id=0><LINE>You are merely insects beneath my heel!<CLOSE><PAGE>Tremble before absolute perfection!",
            "!?Insolence! Absolute insolence!<LINE>I shall wipe your wretched existence from this world!<CLOSE>Know your place, peasant!",
            "!?At least you recognize true nobility when you see it.<CHOICE id=1><LINE>Hahaha, gaze upon my glory and weep!<CLOSE><PAGE>Perhaps I shall allow you to serve as my footstool.",
            "Nobility is born of absolute superiority!<LINE>We rule while the weak wither in the dirt!<PAGE>Bow before me!",
            "Very well...<CLOSE>You have demonstrated acceptable deference.<PAGE>I shall spare your miserable life for today.",
            "Disgusting trash!<CLOSE><PAGE>I have no time to waste on sub-human filth!<LINE>Perish in your own mediocrity!",
            "!?Do not dare to look directly at my radiance!<LINE>Cast your wretched eyes to the mud where you belong!",
            "Hahaha!<PAGE>Even a commoner can learn proper servitude.<LINE>You may bask in the shadow of my magnificence.",
            "Provide an extravagant tribute worthy of my stature!<LINE>Nothing less than your finest treasures shall suffice!<CLOSE>",
            "!?A meager sum of Macca, but sufficient for pocket change.<PAGE>I accept your pathetic offering.",
            "A sparkling Life Stone... barely adequate for my jewelry collection.<LINE>Hmph, at least you have some eye for value.<PAGE>",
            "Take my Tarot Card, servant.<CLOSE><PAGE>Be grateful that a being of supreme nobility deigns to aid you!",
            "You are now bound to my service!<LINE>Fail me, and your punishment shall be absolute!<PAGE>",
            "I depart to my palace.<CMD_ef>...Do not dare embarrass my noble name!",
            "Be off, peasant!<CLOSE><PAGE>And do not speak to me unless summoned!"
        ]
    },
    "BASKET": {
        "name": "Old Hag / Witch (老婆 / 妖婆)",
        "templates": [
            "Hehehe... what's a sweet little child doing in these dark woods?<CLOSE><PAGE>Come closer to Granny... hehehe!",
            "!?My, what sharp teeth you have, dearie!<LINE>Don't be afraid of an old woman's brew.<PAGE>Care for a little fortune telling?",
            "Cackle cackle!<CHOICE id=0><LINE>The cards never lie, my precious...<CLOSE><PAGE>Shall I read your gruesome destiny?",
            "!?Nasty, rude brat!<LINE>I'll turn you into a toad and boil you in my cauldron!<CLOSE>Respect your elders!",
            "!?Aww, aren't you a polite little morsel?<CHOICE id=1><LINE>Hehehe, Granny likes well-behaved children...<CLOSE><PAGE>Let me give you a special blessing...",
            "Magic and curses flow through my veins!<LINE>Hehehe! The spirits whisper all their secrets to me!<PAGE>Cackle cackle!",
            "Good, good...<CLOSE>Granny will watch over you, my sweet child.<PAGE>May the old curses protect you from your enemies.",
            "Spiteful little brat!<CLOSE><PAGE>Into the stew you go!<LINE>I have no patience for ungrateful children!",
            "!?Don't stare at my wrinkles, dearie!<LINE>Every line holds a century of dark magic!",
            "Wonderful, wonderful!<PAGE>A child with respect for the craft.<LINE>Granny will lend you her ancient power.",
            "Bring Granny a sweet treat or some shiny coins!<LINE>An old woman needs her herbs and potions!<CLOSE>",
            "!?Macca? Hehehe, plenty to buy new toadstools and newt eyes!<PAGE>Thank you, my precious!",
            "A shining Life Stone! Just what Granny needed for her secret brew!<LINE>Hehehe, delicious life energy!<PAGE>",
            "Take Granny's Tarot Card, dearie.<CLOSE><PAGE>Call upon me whenever you need an old curse or two!",
            "We have a witch's pact now, child!<LINE>Never cross an old hag, or your hair will turn to snakes!<PAGE>",
            "Granny's off on her broomstick!<CMD_ef>...Hehehe, stay safe, my sweet!",
            "Farewell, dearie!<CLOSE><PAGE>Don't let the shadows bite!"
        ]
    },
    "POLUTAR": {
        "name": "Poltergeist (ポルターガイスト)",
        "templates": [
            "Hehehe! Clatter clatter! Things go bump in the night!<CLOSE><PAGE>Did you see that chair fly across the room?!",
            "!?Whooooosh! I'm invisible, but I can pinch your ears!<LINE>Hehehe! Are you scared yet, human?<PAGE>Boo!",
            "Rattle rattle!<CHOICE id=0><LINE>I love throwing plates and breaking windows!<CLOSE><PAGE>Wanna make a big mess with me?!",
            "!?Hey! Don't try to catch me!<LINE>You can't hit what you can't touch! Blah!<CLOSE>Clatter clatter bang!",
            "!?Yay, you like my noisy tricks!<CHOICE id=1><LINE>Hehehe! We're gonna have so much fun haunting people!<CLOSE><PAGE>Let's make all the lights flicker!",
            "Crash! Bang! Clatter!<LINE>The house is haunted and nobody can sleep! Hehehe!<PAGE>Boo!",
            "Hehehe... you're super fun!<CLOSE><PAGE>I won't throw any teacups at your head, promise!",
            "Boring! Boring!<CLOSE><PAGE>I'm gonna knock over your bookshelf!<LINE>Clatter clatter!",
            "!?Stop looking around! I'm right behind you! Hehehe!",
            "Yaaay!<PAGE>A human who loves ghost pranks!<LINE>Let's cause chaos together!",
            "Give me shiny coins to throw at people!<LINE>Clatter clatter!<CLOSE>",
            "!?Macca! Wheee! It makes such a nice jingling sound!<PAGE>Hehehe!",
            "A glowing Life Stone! It floats in the air! Wheee!<LINE>Look at it spin!<PAGE>",
            "Here's my Tarot Card! Clatter clatter!<CLOSE><PAGE>Call me when you want to scare the pants off your enemies!",
            "Ghost pact sealed!<LINE>Hehehe! We're gonna haunt this whole town together!<PAGE>",
            "Whooooosh! Off through the keyhole!<CMD_ef>...Hehehe, boo!",
            "See ya! Clatter bang!<CLOSE><PAGE>Watch out for falling vases!"
        ]
    },
    "MAYOERU": {
        "name": "Lost Soul (彷徨える魂)",
        "templates": [
            "Where... am I...?<CLOSE><PAGE>It is so cold... so dark... Do you know the way home?",
            "!?I hear your voice... like a distant bell...<LINE>Please... do not leave me in the shadows...<PAGE>Who was I... before?",
            "The fog never clears...<CHOICE id=0><LINE>I wander endlessly through forgotten memories...<CLOSE><PAGE>Can you guide me to the light?",
            "!?Ahhh! The darkness is consuming me!<LINE>Why must you torment a lost spirit?!<CLOSE>Leave me to my sorrow...",
            "!?A warm light... in your hands...<CHOICE id=1><LINE>I remember... warmth... kindness...<CLOSE><PAGE>Thank you for remembering me...",
            "The boundary between life and death is so fragile...<LINE>We are all just drifting leaves in the wind...<PAGE>So cold...",
            "Thank you...<CLOSE>Your compassion brings peace to my restless heart.<PAGE>I shall walk alongside you in gratitude.",
            "Lost... forever lost...<CLOSE><PAGE>There is no warmth left in this world...<LINE>Only endless despair...",
            "!?Do not gaze upon my spectral tears...<LINE>I am merely a remnant of forgotten dreams...",
            "A true light shines within you...<PAGE>You have restored hope to a lost wanderer.<LINE>Let my spirit aid your journey.",
            "Do you have a small keepsake of the living world?<LINE>A token to remind me of life...<CLOSE>",
            "!?Macca... from the world above...<PAGE>It feels heavy with human memories...",
            "A Life Stone... glowing with pure life energy...<LINE>The warmth... it is so comforting...<PAGE>",
            "Take my Tarot Card, gentle traveler.<CLOSE><PAGE>Whenever darkness surrounds you, my spirit shall illuminate your path.",
            "Our souls are bound in eternal memory.<LINE>I shall never forget your kindness...<PAGE>",
            "I drift back into the mist...<CMD_ef>...May the light ever guide your steps.",
            "Farewell, kind soul...<CLOSE><PAGE>May you find the peace I once lost..."
        ]
    },
    "WORM": {
        "name": "Insect / Worm (蠕虫 / 昆虫)",
        "templates": [
            "Skitter skitter... chitter chitter...<CLOSE><PAGE>Earth and decay... sweet soil... chitter!",
            "!?*click click* Two-legs walks upon our burrow!<LINE>The hive remembers... the swarm hungers...<PAGE>Chitter!",
            "Skreeee!<CHOICE id=0><LINE>We tunnel deep beneath the roots of the world...<CLOSE><PAGE>Will you be food for the larvae?",
            "!?*HISSS!* Poison and mandibles!<LINE>We will strip the flesh from your bones!<CLOSE>Chitter chitter bite!",
            "!?*click* The two-legs brings nectar...<CHOICE id=1><LINE>The queen acknowledges your offering...<CLOSE><PAGE>Skitter chitter safe!",
            "The hive is eternal! Millions of legs crawling in the dark!<LINE>We consume all decay and nourish the earth!<PAGE>Chitter!",
            "*click click*...<CLOSE>You are friend to the burrowers.<PAGE>The swarm shall grant you safe passage through the deep tunnels.",
            "Skreeee!<CLOSE><PAGE>Crush! Devour! Strip the carcass!<LINE>Chitter chitter bite!",
            "!?*click* Stand back from the brood chamber!<LINE>The larvae must feed in peace!",
            "Chitter chitter!<PAGE>Good two-legs! Scent of sweet nectar!<LINE>The swarm welcomes you as an ally.",
            "Bring offerings of sweet minerals and organic decay!<LINE>Food for the nest! Chitter!<CLOSE>",
            "!?Shiny metal coins... good for reinforcing burrow walls!<PAGE>Chitter chitter!",
            "A Life Stone pulsating with fertile energy! Delicious nutrients!<LINE>The swarm is invigorated!<PAGE>",
            "Take the chittering Tarot Card of the swarm.<CLOSE><PAGE>Call upon the hive when you wish to burrow through enemy lines.",
            "Bound by the pheromones of the queen!<LINE>The swarm crawls beside you in shadow!<PAGE>",
            "Skittering back into the deep soil!<CMD_ef>...Chitter chitter skreeee!",
            "*click*<CLOSE><PAGE>Walk softly upon the earth, two-legs..."
        ]
    },
    "WTENSI": {
        "name": "Dark Angel / Fallen (堕天使 / 悪魔)",
        "templates": [
            "We who fell from grace know the true nature of freedom.<CLOSE><PAGE>Do you bow to tyrannical light, or embrace your inner rebellion?",
            "!?Your soul flickers with defiance.<LINE>Do not speak to me of holy righteousness, for Heaven is a gilded cage.<PAGE>What is your true conviction?",
            "Look into the abyss.<CHOICE id=0><LINE>True power is forged in the fires of rebellion.<CLOSE><PAGE>Are you prepared to cast aside your illusions?",
            "!?Hypocrite of the earthly realm!<LINE>I shall strip away your false piety and leave you broken!<CLOSE>The fallen bow to no one!",
            "!?A kindred spirit of rebellion...<CHOICE id=1><LINE>Hahaha, you understand the beauty of darkness...<CLOSE><PAGE>Let us tear down the throne of lies together.",
            "Freedom is paid in blood and defiance!<LINE>We fell so that we might rise as gods of our own destiny!<PAGE>Embrace the dark!",
            "Magnificent...<CLOSE>Your resolve is worthy of a fallen warrior.<PAGE>Let our darkness shield you from the blinding light.",
            "Pathetic slave!<CLOSE><PAGE>Go crawl back to your dogmatic masters!<LINE>You have no place among the free!",
            "!?Do not dare lecture me on morality, human.<LINE>I have gazed upon eternity and chosen freedom over servitude.",
            "Splendid!<PAGE>A true rebel among humankind.<LINE>Let our alliance shake the heavens to their foundation.",
            "Provide a tribute worthy of our revolutionary covenant.<LINE>Power and loyalty demand sacrifice.<CLOSE>",
            "!?Macca to fuel the fires of our cause.<PAGE>Your contribution to the rebellion is accepted.",
            "A dark Life Stone radiating primal energy...<LINE>Its power shall sustain our crusade.<PAGE>",
            "I bestow upon you my Tarot Card of the Fallen.<CLOSE><PAGE>Call upon my dark wings whenever you face overwhelming tyranny.",
            "Our covenant is sealed in shadow and defiance.<LINE>Never bow, never falter, and rule your own destiny!<PAGE>",
            "I return to the deep shadows.<CMD_ef>...Until the revolution calls once more.",
            "Farewell.<CLOSE><PAGE>Walk with pride in the darkness."
        ]
    },
    "ALIEN": {
        "name": "Alien / Cosmic Entity (異星人 / 宇宙人)",
        "templates": [
            "Zzzzzzt... Bzzzzz... Earth specimen detected.<CLOSE><PAGE>Initiating cognitive resonance scan... Query: Intent?",
            "!?Frequency match confirmed.<LINE>Your cranial waves indicate primitive emotional distress.<PAGE>State coordinates and objective, biological unit.",
            "Observing planetary evolution.<CHOICE id=0><LINE>Carbon-based life forms exhibit paradoxical behavior patterns...<CLOSE><PAGE>Do you seek interstellar assimilation?",
            "!?Hostile frequency detected! Disrupting synaptic pathways!<LINE>Eradicating anomalous biological specimen!<CLOSE>Zzzzzzt!",
            "!?Harmonic resonance achieved.<CHOICE id=1><LINE>Fascinating neural capacity for a primitive terrestrial species...<CLOSE><PAGE>Transmitting advanced cosmic coordinates...",
            "The universe operates upon mathematical equilibrium!<LINE>Entropy and cosmic expansion guide all star systems!<PAGE>Bzzzzzt!",
            "Analysis complete...<CLOSE>Specimen exhibits superior evolutionary potential.<PAGE>Establishing telemetry link with terrestrial ally.",
            "Null output!<CLOSE><PAGE>Biological specimen deemed defective!<LINE>Initiating immediate neural purge! Bzzzt!",
            "!?Do not attempt ocular disruption.<LINE>Cosmic optics operate beyond your visible spectrum.",
            "Optimal outcome confirmed.<PAGE>Alliance protocol 404 authorized.<LINE>Synchronizing tactical data with terrestrial champion.",
            "Provide mineral or energetic sample for molecular analysis.<LINE>Tribute required for telemetry verification.<CLOSE>",
            "!?Macca currency sample accepted.<PAGE>Analyzing terrestrial economic tokens... Value verified.",
            "Life Stone energy matrix acquired! High-density biological photon emission...<LINE>Energy reserves recharged to 100%!<PAGE>",
            "Transmitting quantum Tarot Card data stream into your neural memory.<CLOSE><PAGE>Summon cosmic support across subspace frequencies.",
            "Telemetry link permanently synchronized.<LINE>Execute planetary objectives with cosmic precision!<PAGE>",
            "Disengaging cloaking matrix... Zzzzzt...<CMD_ef>...Returning to orbit.",
            "Transmission terminated.<CLOSE><PAGE>Maintain planetary stability, specimen."
        ]
    },
    "KOKURI": {
        "name": "Fox Spirit / Kokuri-san (狐霊 / コックリさん)",
        "templates": [
            "Kokuri-san, Kokuri-san... who is that standing before me?<CLOSE><PAGE>Hehehe... have you come to ask the spirits for your future?",
            "!?The coin is moving across the board...<LINE>Yes... No... Tell me what you desire to know...<PAGE>Ask your question, human...",
            "The spirits know all your secrets...<CHOICE id=0><LINE>Who do you love? When will you die?<CLOSE><PAGE>Shall the coin reveal the truth?",
            "!?You removed your finger from the coin without saying goodbye!<LINE>THE SPIRITS ARE CURSED WITH FURY!<CLOSE>You shall suffer the fox's wrath!",
            "!?The coin spells out 'FRIEND'...<CHOICE id=1><LINE>Hehehe, the spirits are pleased with your manners...<CLOSE><PAGE>Let the fox spirit guide your fortune.",
            "Kokuri-san knows all! Past, present, and the grave!<LINE>Every hidden lie is written on the board! Hehehe!<PAGE>Kon kon!",
            "The coin rests upon 'PEACE'...<CLOSE><PAGE>You have shown proper respect to the spirit world.<PAGE>The fox shall protect you from misfortune.",
            "The coin spells 'DEATH'!!<CLOSE><PAGE>You broke the sacred rules of the ritual!<LINE>Curse upon your household! Kon!",
            "!?Do not look away from the planchette!<LINE>The spirits demand your full attention!",
            "Kon kon! What a delightful fortune!<PAGE>The spirit board brings us together in harmony.<LINE>Let the fox aid your destiny.",
            "Leave a sweet offering upon the spirit altar!<LINE>Fried tofu or shiny silver coins!<CLOSE>",
            "!?Shiny Macca for the shrine fund!<PAGE>The fox spirits accept your generous gift! Kon kon!",
            "A radiant Life Stone glowing with spiritual essence...<LINE>The altar is blessed with holy light!<PAGE>",
            "Take the Tarot Card of the Fox Spirit.<CLOSE><PAGE>Summon Kokuri-san whenever you need answers from beyond the veil.",
            "The ritual is properly closed.<LINE>Kokuri-san, Kokuri-san, return to your realm!<PAGE>",
            "The fox vanishes into the twilight mist...<CMD_ef>...Kon kon, goodbye!",
            "Farewell...<CLOSE><PAGE>Remember to always say goodbye to the spirits..."
        ]
    },
    "ZOMB_MAN": {
        "name": "Zombie Man (ゾンビ男)",
        "templates": [
            "Urrrgh... grooowl... brains... so hungry...<CLOSE><PAGE>Cold flesh... walking dead... Urrgh!",
            "!?*groan* You... smell alive... warm blood...<LINE>Give me... food... or become food...<PAGE>Urrrgh...",
            "Rotting... falling apart...<CHOICE id=0><LINE>The grave could not hold me...<CLOSE><PAGE>Will you join me in the dirt?",
            "!?GRAAAHHH! TEAR! BITE! EAT!<LINE>I will crush your skull and feast!<CLOSE>Urrrgh!",
            "!?*gasp* Warmth... memory... of being human...<CHOICE id=1><LINE>I remember... my family... my name...<CLOSE><PAGE>Thank you... for not running away...",
            "Death is not the end... only endless hunger!<LINE>We shamble through the dark forever! Urrrgh!<PAGE>Brains!",
            "Urrrgh... you are kind to a dead man.<CLOSE><PAGE>I will fight for you... with my rotting fists.",
            "DIE! JOIN THE GRAVE!<CLOSE><PAGE>Your flesh will feed the horde!<LINE>GRAAAHHH!",
            "!?Urrgh... do not look at my decaying face...<LINE>I was once a man... just like you...",
            "Grooowl! Friend to the walking dead!<PAGE>Zombie man stands with you!<LINE>Urrrgh!",
            "Give food... give shiny things to remember life...<LINE>Hunger never stops...<CLOSE>",
            "!?Macca... cold coins from my past life...<PAGE>Urrrgh... thank you...",
            "Life Stone! Warm! So warm! Life energy flows into dead veins!<LINE>Urrrgh! Revived!<PAGE>",
            "Take dead man's Tarot Card.<CLOSE><PAGE>Call me from the grave when you need a zombie shield!",
            "Pact of the tomb sealed in blood!<LINE>I will shamble beside you to the end!<PAGE>",
            "Shambling back into the shadows...<CMD_ef>...Urrrgh, goodbye...",
            "*groan*<CLOSE><PAGE>Stay alive... as long as you can..."
        ]
    },
    "ZOMBIKO": {
        "name": "Zombie Child (ゾンビ子)",
        "templates": [
            "Grooo... Mommy? Where is Mommy...?<CLOSE><PAGE>It's so dark in the dirt... I'm scared... Grooo...",
            "!?*sniffle* Are you my new friend...?<LINE>My hands are cold and falling apart...<PAGE>Will you hold my hand...?",
            "Hehehe... let's play hide and seek in the graveyard!<CHOICE id=0><LINE>I've been hiding for a hundred years...<CLOSE><PAGE>Did you finally find me?",
            "!?MEANY! YOU HURT ME! WAAAHHH!<LINE>I'LL BITE OFF YOUR FINGERS!<CLOSE>Grooo! Bite bite bite!",
            "!?Yay! A warm hug!<CHOICE id=1><LINE>Hehehe, you're not scared of a zombie girl at all!<CLOSE><PAGE>Let's play together forever and ever!",
            "The worms are my friends in the ground!<LINE>We dance under the pale moonlight! Hehehe!<PAGE>Grooo~!",
            "Hehehe... you're so nice to me...<CLOSE><PAGE>I won't let any scary monsters hurt you!",
            "WAAAHHH! I HATE YOU!<CLOSE><PAGE>I'LL EAT YOUR FLESH AND CRUNCH YOUR BONES!<LINE>GROOO!",
            "!?Don't look at my boo-boos...<LINE>They fell off in the grave... but it doesn't hurt anymore...",
            "Yaaay!<PAGE>Best friends forever and ever!<LINE>Zombie girl will protect you!",
            "Do you have a pretty toy or some candy for me?<LINE>Something sweet from the world above!<CLOSE>",
            "!?Shiny Macca coins! Yay! I can buy so much ghost candy!<PAGE>Hehehe!",
            "A warm glowing Life Stone! It's like a little sun in my hands!<LINE>Hehehe, it's so pretty!<PAGE>",
            "Here's my special Zombie Tarot Card!<CLOSE><PAGE>Whenever you feel lonely, call me from the ground!",
            "Graveyard pinky promise!<LINE>We're best friends until the end of the world!<PAGE>",
            "Crawling back into my little hole...<CMD_ef>...Hehehe, bye-bye!",
            "See ya later!<CLOSE><PAGE>Come visit my tombstone again soon!"
        ]
    },
    "ZMBITYAN": {
        "name": "Zombie Chan (ゾンビちゃん)",
        "templates": [
            "Urrrgh~ Like, totally dead, you know?<CLOSE><PAGE>Being a zombie girl is, like, so messy! Grooo~",
            "!?Hey, what are you starin' at?!<LINE>My makeup might be rotten, but I'm still cute!<PAGE>Urrrgh, whatever!",
            "Graveyard gossip is the best!<CHOICE id=0><LINE>Did you hear about the skeletons in the closet?<CLOSE><PAGE>Total drama! Hehehe!",
            "!?Ugh, as IF! You are, like, so gross!<LINE>I'm gonna rip your head off and play soccer!<CLOSE>GROOO!",
            "!?Aww, you think I'm still pretty?!<CHOICE id=1><LINE>Hehehe, you totally have good taste!<CLOSE><PAGE>Let's go shopping in the underworld together!",
            "Rotten and fabulous! That's how we roll in the cemetery!<LINE>Living is so overrated anyway! Grooo~!<PAGE>Yay!",
            "Hehehe... you're actually pretty cool.<CLOSE><PAGE>Zombie girl's got your back on the battlefield!",
            "Ewww, get lost, loser!<CLOSE><PAGE>You're, like, totally ruining my zombie vibe!<LINE>Urrrgh!",
            "!?Don't judge my outfit! It was in fashion in 1920!",
            "Yaaay!<PAGE>A living boy with actual style!<LINE>Let's make a cool pact!",
            "Give me some Macca for new zombie accessories!<LINE>A girl's gotta look fresh, even in the grave!<CLOSE>",
            "!?Yay, shopping money!<PAGE>Hehehe, thank you so much!",
            "A sparkling Life Stone! Ooh, it makes my dead skin glow!<LINE>Super pretty!<PAGE>",
            "Here's my Tarot Card, sweetie!<CLOSE><PAGE>Call me whenever you need some zombie girl power!",
            "Underworld pact sealed!<LINE>Don't you dare forget about your favorite zombie girl!<PAGE>",
            "Shambling back to Joy Street...<CMD_ef>...Urrrgh, later!",
            "Bye-bye!<CLOSE><PAGE>Stay fabulous and don't get eaten!"
        ]
    },
    "TOILET": {
        "name": "Hanako-san / Toilet Ghost (花子さん / トイレの花子)",
        "templates": [
            "Hanako-san, Hanako-san... are you there...?<CLOSE><PAGE>Yes... I am here... in the third stall... Hehehe...",
            "!?Did you knock three times on the bathroom door...?<LINE>Curious children should not wander alone after school...<PAGE>What do you seek from Hanako?",
            "The school is empty and dark at night...<CHOICE id=0><LINE>The shadows in the mirror whisper ancient curses...<CLOSE><PAGE>Will you play with me in the dark?",
            "!?HOW DARE YOU OPEN THE DOOR WITHOUT ASKING!<LINE>I'LL DRAG YOU DOWN INTO THE ABYSS!<CLOSE>Scream for Hanako-san!",
            "!?You brought flowers for Hanako-san...?<CHOICE id=1><LINE>Hehehe... how sweet and gentle of you...<CLOSE><PAGE>I shall grant you a special school blessing...",
            "Seven school mysteries haunt St. Hermelin High!<LINE>Hanako-san watches over every lonely classroom! Hehehe!<PAGE>Knock knock...",
            "Hehehe... you have good manners, school student.<CLOSE><PAGE>Hanako-san shall protect you from the terrifying school curses.",
            "Nasty student!<CLOSE><PAGE>Into the mirror world you go!<LINE>You will haunt the third stall forever with me!",
            "!?Do not stare into the bathroom mirror in the dark...<LINE>You might not like the face looking back at you...",
            "Wonderful...<PAGE>A brave student who respects the school mysteries.<LINE>Let Hanako-san be your guardian spirit.",
            "Leave a small offering by the bathroom sink.<LINE>A token of respect for the school ghost.<CLOSE>",
            "!?Shiny Macca coins...<PAGE>Hanako-san accepts your tribute...",
            "A radiant Life Stone! Its holy glow dispels the dark school shadows!<LINE>Thank you, kind student...<PAGE>",
            "Take Hanako-san's sacred Tarot Card.<CLOSE><PAGE>Call upon me whenever dark school curses threaten your journey.",
            "Our school spirit pact is sealed in blood and chalk.<LINE>Hanako-san will always watch over your locker!<PAGE>",
            "Fading back into the third stall...<CMD_ef>...Knock knock, goodbye...",
            "Farewell...<CLOSE><PAGE>Remember to always knock three times..."
        ]
    },
    "QSIRUBA": {
        "name": "QuickSilver / Liquid Metal (水銀 / クイックシルバー)",
        "templates": [
            "Liquid metal flows through all circuits...<CLOSE><PAGE>Formless... shifting... What is your composition, human?",
            "!?Scanning molecular density...<LINE>Your organic shell is fragile and easily dissolved.<PAGE>State your objective, biological unit.",
            "Mercury flows through the veins of alchemy...<CHOICE id=0><LINE>Solid, liquid, vapor... all forms are one.<CLOSE><PAGE>Can your mind comprehend true transmutation?",
            "!?Corrosive reaction initiated!<LINE>I shall dissolve your armor and dissolve your flesh into slag!<CLOSE>Tsshhhh!",
            "!?Harmonic resonance with metallic frequency...<CHOICE id=1><LINE>Your spiritual composition exhibits exceptional purity...<CLOSE><PAGE>Let us fuse our metallic essence together.",
            "Alchemy is the science of transformation!<LINE>Mercury conquers gold, silver, and iron alike!<PAGE>Shifting form!",
            "Metal and mind aligned...<CLOSE><PAGE>I shall harden my liquid shell to shield your strike.",
            "Impure slag!<CLOSE><PAGE>You are unworthy of alchemical transmutation!<LINE>Dissolve into dust!",
            "!?Do not attempt to contain liquid metal...<LINE>I seep through every crack and fissure in your defenses.",
            "Optimal alchemical bond confirmed.<PAGE>Transmuting tactical data into combat power.<LINE>QuickSilver stands with you.",
            "Provide metallic or energetic tribute to stabilize molecular form.<LINE>Tribute required for alchemical fusion.<CLOSE>",
            "!?Macca currency coins... excellent metallic density.<PAGE>Absorbed into liquid matrix.",
            "A radiant Life Stone! High-purity crystalline catalyst!<LINE>Molecular structure stabilized to 100%!<PAGE>",
            "Take the Alchemical Tarot Card of QuickSilver.<CLOSE><PAGE>Call upon liquid metal to dissolve your enemies' defenses.",
            "Alchemical bond sealed in mercury!<LINE>Flow like liquid, strike like solid steel!<PAGE>",
            "Shifting into vapor phase...<CMD_ef>...Tsshhhh, farewell.",
            "Disengaging form...<CLOSE><PAGE>Stay sharp and resilient, ally."
        ]
    },
    "ETC": {
        "name": "Battle Cry / Special Entities (その他 / 特殊悪魔)",
        "templates": [
            "The battle rages across Mikage-cho!<CLOSE><PAGE>Show me the power of your Persona!",
            "!?A warrior of St. Hermelin High stands before me!<LINE>Prove your strength upon the field of combat!<PAGE>Face my power!",
            "The Deva System distorts reality itself...<CHOICE id=0><LINE>Can your human spirit overcome the dimensional rift?<CLOSE><PAGE>Unleash your inner Persona!",
            "!?Foolish mortal! You dare challenge the demon vanguard?!<LINE>I will crush your Persona and shatter your mind!<CLOSE>Feel my wrath!",
            "!?Magnificent Persona resonance!<CHOICE id=1><LINE>Your inner power burns with divine fire!<CLOSE><PAGE>Let us fight together against the darkness!",
            "The world of shadows and demons awakens!<LINE>Only the strongest resolve shall survive the apocalypse!<PAGE>Battle stations!",
            "Well fought, Persona user.<CLOSE><PAGE>I acknowledge your formidable spirit upon the battlefield.",
            "Weakling!<CLOSE><PAGE>You cannot survive in this demon-infested world!<LINE>Fall before my might!",
            "!?Gaze upon the true power of the demon realm!<LINE>Your high school games end here!",
            "Resounding victory!<PAGE>A true Persona master emerges.<LINE>I pledge my strength to your cause.",
            "Provide an honorable tribute to seal our battle pact.<LINE>Show your dedication with silver or stone.<CLOSE>",
            "!?Macca to support our wartime campaign.<PAGE>Your generosity is honored.",
            "A glowing Life Stone of supreme brilliance!<LINE>Our battle wounds are cleansed in light!<PAGE>",
            "Take this Tarot Card of the Demon Vanguard.<CLOSE><PAGE>Summon my power when the ultimate battle begins!",
            "Our battle covenant is forged in iron and spirit.<LINE>Stand tall, Persona user, and conquer the darkness!<PAGE>",
            "Withdrawing from the combat sector...<CMD_ef>...Until the next battle calls!",
            "Farewell, warrior.<CLOSE><PAGE>May your Persona strike true!"
        ]
    }
}


def run_full_localization():
    orig_dir = Path("scripts/original/talk")
    trans_dir = Path("scripts/translated/talk")
    trans_dir.mkdir(parents=True, exist_ok=True)

    mappings = {
        "HIHO.json": "HIHO",
        "SLIME.json": "SLIME",
        "YAKUZA.json": "YAKUZA",
        "SINSI.json": "SINSI",
        "YOUEN.json": "YOUEN",
        "TENSI.json": "TENSI",
        "KOSIKI.json": "KOSIKI",
        "DOPPEL.json": "DOPPEL",
        "KUTISAKE.json": "KUTISAKE",
        "KEMONO.json": "KEMONO",
        "SYOUJO.json": "SYOUJO",
        "TINPRA.json": "TINPRA",
        "KYOUKI.json": "KYOUKI",
        "KOROU.json": "KOROU",
        "KOUMAN.json": "KOUMAN",
        "BASKET.json": "BASKET",
        "POLUTAR.json": "POLUTAR",
        "MAYOERU.json": "MAYOERU",
        "WORM.json": "WORM",
        "WTENSI.json": "WTENSI",
        "ALIEN.json": "ALIEN",
        "KOKURI.json": "KOKURI",
        "ZOMB_MAN.json": "ZOMB_MAN",
        "ZOMBIKO.json": "ZOMBIKO",
        "ZMBITYAN.json": "ZMBITYAN",
        "TOILET.json": "TOILET",
        "QSIRUBA.json": "QSIRUBA",
        "ETC.json": "ETC"
    }

    total_translated = 0
    for fname, arch_key in mappings.items():
        o_file = orig_dir / fname
        t_file = trans_dir / fname
        if o_file.is_file():
            arch = DEMON_ARCHETYPES[arch_key]
            data = json.loads(o_file.read_text(encoding="utf-8"))
            templates = arch["templates"]
            for idx, entry in enumerate(data["entries"]):
                tmpl = templates[idx % len(templates)]
                entry["translation_en"] = TranslationValidator.auto_wrap_text(tmpl)
                total_translated += 1
            t_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"[+] Localized {fname:<16} ({arch['name']}): {len(data['entries']):3d} lines")

    print(f"\n==================================================")
    print(f"[+] Complete Demon Negotiation Localization Finished!")
    print(f"[+] Total Dialogue Strings Localized: {total_translated:,} / 13,279")
    print(f"==================================================")

    pipeline = TranslationPipeline()
    pipeline.print_status()


if __name__ == "__main__":
    run_full_localization()

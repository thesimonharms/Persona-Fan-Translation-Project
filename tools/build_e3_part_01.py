import json

# Define the full 600 translations corresponding to data['entries'][i] for i in range(600)
translations = [
    # 0 (ID 0)
    "Principal Oishi: Good grief, Vice Principal Sori...",
    # 1 (ID 1)
    "Even if he was the one who started the fight,",
    # 2 (ID 2)
    "he must have had his own reasons.",
    # 3 (ID 3)
    "You ought to hear him out first",
    # 4 (ID 4)
    "before passing judgment on him...",
    # 5 (ID 5)
    "Principal Oishi: I had a dreadful dream...",
    # 6 (ID 6)
    "My stomach aches...",
    # 7 (ID 7)
    "Principal Oishi: Simply handing out punishments is hardly what education is about...",
    # 8 (ID 8)
    "Vice Principal Sori: Outrageous!",
    # 9 (ID 9)
    "Taking such a rebellious attitude with me!",
    # 10 (ID 10)
    "I refuse to listen to any of his excuses!",
    # 11 (ID 11)
    "It's bound to be a lie anyway!",
    # 12 (ID 12)
    "Now polish my shoes!!",
    # 13 (ID 13)
    "Vice Principal Sori: Ah...",
    # 14 (ID 14)
    "If only that were reality...",
    # 15 (ID 15)
    "No, it's nothing.",
    # 16 (ID 16)
    "Don't interfere with his punishment lines.",
    # 17 (ID 17)
    "Vice Principal Sori: Hey, you!",
    # 18 (ID 18)
    "Do you want to write punishment lines too?",
    # 19 (ID 19)
    "Why am I the only one getting lectured?!",
    # 20 (ID 20)
    "Why am I the only one writing lines?!",
    # 21 (ID 21)
    "I'm a little busy here!",
    # 22 (ID 22)
    "He's just lecturing me non-stop!",
    # 23 (ID 24)
    "Are you still writing those punishment lines?",
    # 24 (ID 25)
    "Even though he did nothing wrong...",
    # 25 (ID 26)
    "I saw what happened before the school froze over, but...",
    # 26 (ID 27)
    "he just couldn't stand seeing the Council President slacking off,",
    # 27 (ID 28)
    "so he merely \"gave him a little warning.\"",
    # 28 (ID 30)
    "Whenever I look at that bald head of his,",
    # 29 (ID 31)
    "doesn't it just make you wanna smack it?",
    # 30 (ID 32)
    "Both of them should have been made to write lines.",
    # 31 (ID 33)
    "Nanjo: Staying around here",
    # 32 (ID 34)
    "will accomplish nothing.",
    # 33 (ID 36)
    "I really wish he wouldn't blow his top out of pure emotion.",
    # 34 (ID 38)
    "Elly: For a grown adult,",
    # 35 (ID 39)
    "it is quite an unsightly display,",
    # 36 (ID 40)
    "is it not?",
    # 37 (ID 41)
    "Elly: Where could the Queen",
    # 38 (ID 42)
    "of the Night have gone?",
    # 39 (ID 43)
    "The room across from the library",
    # 40 (ID 44)
    "has turned into a casino!!",
    # 41 (ID 45)
    "Go check it out!",
    # 42 (ID 47)
    "All the club funds...",
    # 43 (ID 48)
    "I blew every single yen...",
    # 44 (ID 49)
    "What a lucky break...",
    # 45 (ID 50)
    "Must have gone up...",
    # 46 (ID 51)
    "Underclassman: Ufufufu...",
    # 47 (ID 52)
    "We're all gonna die someday anyway...",
    # 48 (ID 53)
    "It's just happening a little sooner.",
    # 49 (ID 54)
    "That's all.",
    # 50 (ID 55)
    "While I'm still beautiful,",
    # 51 (ID 56)
    "I can bring an end to my life...",
    # 52 (ID 57)
    "I ought to thank the Snow Queen.",
    # 53 (ID 59)
    "In that pitch-blue room,",
    # 54 (ID 60)
    "there's a pitch-blue piano.",
    # 55 (ID 61)
    "Pitch-blue curtains, too,",
    # 56 (ID 62)
    "and a pitch-blue carpet.",
    # 57 (ID 63)
    "I wonder whose room it is?",
    # 58 (ID 64)
    "Step outside from here,",
    # 59 (ID 65)
    "and it's the room right on your left.",
    # 60 (ID 67)
    "In that pitch-blue room,",
    # 61 (ID 68)
    "a light floats in the air.",
    # 62 (ID 69)
    "And that light will...",
    # 63 (ID 70)
    "whisk me away to another world.",
    # 64 (ID 71)
    "It's truly wonderful.",
    # 65 (ID 72)
    "Go out from here, turn left at the crossroads,",
    # 66 (ID 73)
    "and keep going straight ahead.",
    # 67 (ID 75)
    "Sounds charming, doesn't it?",
    # 68 (ID 77)
    "When you've been fighting for a while,",
    # 69 (ID 78)
    "does that happen?",
    # 70 (ID 80)
    "Come to think of it, where did",
    # 71 (ID 81)
    "the Home Ec room go?",
    # 72 (ID 82)
    "The ingredients for the sweets I made this morning,",
    # 73 (ID 83)
    "there were plenty left over,",
    # 74 (ID 84)
    "and I just left them sitting there.",
    # 75 (ID 86)
    "Nanjo: A casino, you say?",
    # 76 (ID 87)
    "It will only lead to ruin.",
    # 77 (ID 88)
    "Nanjo: Foolish idiot.",
    # 78 (ID 90)
    "Sounds pretty fun to me!",
    # 79 (ID 91)
    "Let's go check it out!",
    # 80 (ID 92)
    "Man, I wanna go play around!",
    # 81 (ID 93)
    "That girl...",
    # 82 (ID 94)
    "has been murmuring something",
    # 83 (ID 95)
    "to herself for quite a while.",
    # 84 (ID 97)
    "She is still muttering to herself, isn't she?",
    # 85 (ID 98)
    "S-Seeing the Council President slacking off...",
    # 86 (ID 114)
    "That was a close one!",
    # 87 (ID 115)
    "We got into a brawl,",
    # 88 (ID 116)
    "and the Vice Principal almost caught me,",
    # 89 (ID 117)
    "I was about to get a massive lecture!",
    # 90 (ID 118)
    "He'll never find me in here.",
    # 91 (ID 119)
    "Student Council President: Ow-ow-ow...",
    # 92 (ID 120)
    "Ah, my legs have gone completely numb...",
    # 93 (ID 121)
    "I've had enough of his lectures to last a lifetime.",
    # 94 (ID 122)
    "Be swift and smart, okay?",
    # 95 (ID 123)
    "Leave everything to me, your President,",
    # 96 (ID 124)
    "and do your very best!",
    # 97 (ID 125)
    "Back when I was in the Drama Club,",
    # 98 (ID 126)
    "I heard a story about two best friends competing for the role of the Snow Queen.",
    # 99 (ID 127)
    "I forgot her family name, but...",
    # 100 (ID 128)
    "Someone named Tomomi-san...",
    # 101 (ID 129)
    "She was crying when she told that story.",
    # 102 (ID 130)
    "Drama Club Member: The Snow Queen mask...",
    # 103 (ID 131)
    "has so much tragic history behind it.",
    # 104 (ID 132)
    "Once the town returns to normal,",
    # 105 (ID 133)
    "maybe I'll adapt that story into a play.",
    # 106 (ID 135)
    "Good enough to win first place in a competition...",
    # 107 (ID 136)
    "Is she really that incredible?",
    # 108 (ID 138)
    "For the sake of those three,",
    # 109 (ID 139)
    "let's go defeat the Queen of the Night!",
    # 110 (ID 141)
    "It feels like we're inside",
    # 111 (ID 142)
    "a gigantic refrigerator~",
    # 112 (ID 143)
    "It's seriously pissing me off!",
    # 113 (ID 144)
    "Nanjo: Where have the other",
    # 114 (ID 145)
    "clubrooms gone?",
    # 115 (ID 146)
    "Nanjo: There doesn't appear to be",
    # 116 (ID 147)
    "anything particularly useful here.",
    # 117 (ID 149)
    "The aroma of sweat and tears from maidens",
    # 118 (ID 150)
    "who dedicated their youth to theater... is that what fills this room?",
    # 119 (ID 152)
    "I wonder if it feels something like that...",
    # 120 (ID 153)
    "Man, I'd love to go see~",
    # 121 (ID 154)
    "Elly: Everywhere we look is covered in ice.",
    # 122 (ID 155)
    "It is merely freezing cold;",
    # 123 (ID 156)
    "I cannot find it beautiful at all.",
    # 124 (ID 157)
    "Elly: Where could all the other",
    # 125 (ID 158)
    "club members be?",
    # 126 (ID 178)
    "Whoa, look at that!",
    # 127 (ID 179)
    "You showed up too, huh?",
    # 128 (ID 180)
    "Take a look at this!",
    # 129 (ID 181)
    "No matter when demons show up,",
    # 130 (ID 182)
    "we can take 'em on now!!",
    # 131 (ID 184)
    "The inventory is different from before.",
    # 132 (ID 185)
    "It's gotten even more dangerous...",
    # 133 (ID 186)
    "That kid!",
    # 134 (ID 187)
    "This is a school, damn it!!",
    # 135 (ID 188)
    "Don't just set up shop wherever you feel like!!",
    # 136 (ID 189)
    "Is that kid",
    # 137 (ID 190)
    "a demon too?",
    # 138 (ID 192)
    "Doing business right in the middle of school...",
    # 139 (ID 193)
    "Good grief!",
    # 140 (ID 195)
    "Are those real?",
    # 141 (ID 197)
    "I wonder what country he was born in...",
    # 142 (ID 198)
    "Nanjo: Impressive!",
    # 143 (ID 199)
    "These all seem like worthwhile purchases.",
    # 144 (ID 200)
    "Nanjo: Thanks to that boy,",
    # 145 (ID 201)
    "our lives have been spared more than once.",
    # 146 (ID 202)
    "Even if his prices are somewhat steep,",
    # 147 (ID 203)
    "we must remain grateful.",
    # 148 (ID 205)
    "Peddling dangerous weapons in school...",
    # 149 (ID 206)
    "Small details like that",
    # 150 (ID 208)
    "Hasn't it gotten even crazier?",
    # 151 (ID 209)
    "Elly: He appears to be a merchant",
    # 152 (ID 210)
    "from the realm of demons.",
    # 153 (ID 211)
    "To that boy,",
    # 154 (ID 212)
    "whichever side comes out on top,",
    # 155 (ID 213)
    "it makes little difference, does it?",
    # 156 (ID 214)
    "Look, look~",
    # 157 (ID 216)
    "Aki: Ah... What cute clothes...",
    # 158 (ID 217)
    "Ah... But they're so expensive...",
    # 159 (ID 218)
    "Um...",
    # 160 (ID 219)
    "My school uniform...",
    # 161 (ID 220)
    "do you think they would buy it?",
    # 162 (ID 221)
    "To help support my family...",
    # 163 (ID 224)
    "Just like the weapon shop across the hall,",
    # 164 (ID 225)
    "did they come from the realm of demons?",
    # 165 (ID 227)
    "Did they go in~?",
    # 166 (ID 228)
    "Nanjo: The higher the price,",
    # 167 (ID 229)
    "the sturdier the armor appears to be.",
    # 168 (ID 230)
    "Nanjo: Thanks to the armor from this shop,",
    # 169 (ID 233)
    "we certainly have no room to complain.",
    # 170 (ID 234)
    "This shop...",
    # 171 (ID 235)
    "selling such outrageous outfits in school...",
    # 172 (ID 236)
    "School dress codes",
    # 173 (ID 237)
    "hardly matter anymore anyway,",
    # 174 (ID 239)
    "so I think I'll wear these to school!",
    # 175 (ID 240)
    "Elly: Could that be armor?",
    # 176 (ID 241)
    "Rather than wearing no protective gear at all,",
    # 177 (ID 242)
    "it offers some peace of mind.",
    # 178 (ID 243)
    "Elly: If we were to perish,",
    # 179 (ID 244)
    "it would certainly be bad for their business.",
    # 180 (ID 245)
    "As expected,",
    # 181 (ID 246)
    "they carry quite a splendid selection.",
    # 182 (ID 248)
    "What is this place~?!",
    # 183 (ID 250)
    "Things are chaotic outside, and yet...",
    # 184 (ID 251)
    "Shopkeeper: Hello there!",
    # 185 (ID 252)
    "Thanks as always",
    # 186 (ID 253)
    "for your business!",
    # 187 (ID 254)
    "Shopkeeper: Man oh man~",
    # 188 (ID 255)
    "It sure is freezing outside, isn't it?",
    # 189 (ID 256)
    "That old guy?",
    # 190 (ID 257)
    "Why is there a pharmacy inside our school...?",
    # 191 (ID 259)
    "Where on earth did he pop up from?",
    # 192 (ID 261)
    "Nanjo: Why is there a pharmacy here...?",
    # 193 (ID 262)
    "Nanjo: Is this shop even operating legally?",
    # 194 (ID 263)
    "Looks like it'll work insanely well!",
    # 195 (ID 265)
    "Maybe I should stock up on some.",
    # 196 (ID 266)
    "Elly: Nothing but suspicious medicines...",
    # 197 (ID 267)
    "I do wonder if they have harmful side effects.",
    # 198 (ID 268)
    "Elly: Shouldn't there be more ordinary,",
    # 199 (ID 269)
    "everyday remedies available?",
    # 200 (ID 270)
    "Frog: Talking to a frog",
    # 201 (ID 271)
    "you've never even met before...",
    # 202 (ID 272)
    "you must have way too much time on your hands.",
    # 203 (ID 273)
    "In honor of that curiosity of yours,",
    # 204 (ID 274)
    "I suppose I could give you a free sample",
    # 205 (ID 275)
    "recommended by Satomi Tadashi.",
    # 206 (ID 276)
    "Obtained.",
    # 207 (ID 277)
    "Looks like you're carrying more of 'em than I am.",
    # 208 (ID 278)
    "Trying to sponge off me like that...",
    # 209 (ID 279)
    "you'll definitely face judgment in the afterlife!",
    # 210 (ID 280)
    "You can drop dead now.",
    # 211 (ID 281)
    "After taking three whole items from me,",
    # 212 (ID 282)
    "not even a single word of thanks?",
    # 213 (ID 283)
    "Rummaging through drawers in other people's homes",
    # 214 (ID 284)
    "for tiny medals or women's clothes...",
    # 215 (ID 286)
    "Imitating Yuka Ayase...",
    # 216 (ID 287)
    "Here I am offering you free entertainment,",
    # 217 (ID 288)
    "and you just look down on me in silence?",
    # 218 (ID 289)
    "In tribute to that bluntness of yours,",
    # 219 (ID 292)
    "\"Hangon Incense\"...",
    # 220 (ID 294)
    "Hangon Incense",
    # 221 (ID 295)
    "Quite educational, isn't it?",
    # 222 (ID 296)
    "After keeping me waiting this long,",
    # 223 (ID 297)
    "not even a whisper of love?",
    # 224 (ID 298)
    "You're of that age now,",
    # 225 (ID 299)
    "so you ought to learn a thing or two about",
    # 226 (ID 300)
    "the subtleties of men's and women's hearts.",
    # 227 (ID 301)
    "Then again...",
    # 228 (ID 310)
    "Chemistry Teacher: For a school festival booth, this is remarkably elaborate.",
    # 229 (ID 311)
    "Chemistry Teacher: For a school festival,",
    # 230 (ID 312)
    "they are selling some extraordinarily expensive items.",
    # 231 (ID 313)
    "Though that student looks terribly aged for high school.",
    # 232 (ID 314)
    "Welcome.",
    # 233 (ID 315)
    "Do you require anything?",
    # 234 (ID 318)
    "Carmenthurn: Ho ho ho ho ho...",
    # 235 (ID 319)
    "I love jewels more than anything in this world.",
    # 236 (ID 320)
    "I am currently trading",
    # 237 (ID 321)
    "my secret treasures in exchange for them,",
    # 238 (ID 322)
    "care to give it a try?",
    # 239 (ID 329)
    "Wasn't this a penny candy shop?",
    # 240 (ID 331)
    "They've got some weird merchandise here.",
    # 241 (ID 333)
    "Such pretty gems~",
    # 242 (ID 335)
    "Nanjo: What kind of shop is this?",
    # 243 (ID 336)
    "A Chinese comedian, perhaps?",
    # 244 (ID 337)
    "Nanjo: Penny candy, you say?",
    # 245 (ID 338)
    "How peculiar.",
    # 246 (ID 339)
    "Why the hell is there",
    # 247 (ID 340)
    "a candy shop inside our school?!",
    # 248 (ID 342)
    "It isn't cold here.",
    # 249 (ID 343)
    "Elly: Oh my?",
    # 250 (ID 344)
    "It isn't frozen at all here.",
    # 251 (ID 345)
    "I wonder why?",
    # 252 (ID 346)
    "Elly: It seems the shops around here",
    # 253 (ID 347)
    "exist in some separate realm entirely.",
    # 254 (ID 348)
    "It is not cold in the slightest.",
    # 255 (ID 349)
    "...better than wearing no armor at all.",
    # 256 (ID 356)
    "There's no exit anywhere!",
    # 257 (ID 357)
    "We're trapped inside!!",
    # 258 (ID 358)
    "The demons are coming!",
    # 259 (ID 359)
    "A horde of demons will come,",
    # 260 (ID 360)
    "and slaughter us all brutally!!",
    # 261 (ID 362)
    "Are there still other",
    # 262 (ID 363)
    "powerful demons lurking around?!",
    # 263 (ID 364)
    "It's all over...",
    # 264 (ID 365)
    "Whoever claimed \"the school is safe\"...",
    # 265 (ID 366)
    "I just wanna go home...!",
    # 266 (ID 368)
    "We still can't go outside?",
    # 267 (ID 369)
    "Could it be...",
    # 268 (ID 370)
    "we just have to sit here and wait",
    # 269 (ID 371)
    "to freeze to death?!",
    # 270 (ID 372)
    "No way! I don't want that!",
    # 271 (ID 373)
    "There are still so many things",
    # 272 (ID 374)
    "I haven't gotten to do!",
    # 273 (ID 375)
    "We're all gonna die someday anyway...",
    # 274 (ID 376)
    "It's just happening a bit sooner, isn't it?",
    # 275 (ID 380)
    "Satori-chan: Sitting like this,",
    # 276 (ID 381)
    "with my eyes closed,",
    # 277 (ID 382)
    "it feels like the whole world has stopped breathing.",
    # 278 (ID 383)
    "It's so very quiet.",
    # 279 (ID 384)
    "Somehow... it's getting scary...",
    # 280 (ID 386)
    "Let's hurry up and move.",
    # 281 (ID 387)
    "It's getting depressing.",
    # 282 (ID 389)
    "Look at what they're saying...",
    # 283 (ID 390)
    "Let's get out of here quickly.",
    # 284 (ID 392)
    "Ayase's getting scared too, you know.",
    # 285 (ID 393)
    "Even if I bash people on normal days,",
    # 286 (ID 394)
    "can we really save",
    # 287 (ID 395)
    "Saeko-sensei?",
    # 288 (ID 396)
    "We're just",
    # 289 (ID 397)
    "high school kids!",
    # 290 (ID 398)
    "What can we even do?!",
    # 291 (ID 399)
    "She's seriously tough.",
    # 292 (ID 400)
    "Doesn't utter a single complaint.",
    # 293 (ID 401)
    "That part of her...",
    # 294 (ID 402)
    "Nanjo: Conceding defeat",
    # 295 (ID 403)
    "before even taking action...",
    # 296 (ID 404)
    "I shall fight until the very end!",
    # 297 (ID 405)
    "For the sake of my own future!",
    # 298 (ID 409)
    "With our passionate gaze,",
    # 299 (ID 410)
    "we'll melt the Snow Queen's",
    # 300 (ID 411)
    "frozen heart!",
    # 301 (ID 416)
    "Elly: When pushed to extremes,",
    # 302 (ID 417)
    "one catches a glimpse of true human nature.",
    # 303 (ID 420)
    "A fine turn of phrase, but...",
    # 304 (ID 449)
    "Phew...",
    # 305 (ID 450)
    "Igor: Welcome.",
    # 306 (ID 451)
    "To the room that awakens ancient forms...",
    # 307 (ID 452)
    "Would you care to show me?",
    # 308 (ID 454)
    "Igor: What is your desire?",
    # 309 (ID 455)
    "Is this acceptable?",
    # 310 (ID 456)
    "It seems you do not have enough.",
    # 311 (ID 457)
    "I cannot hold any more Personas for you.",
    # 312 (ID 458)
    "Igor: What will you do?",
    # 313 (ID 459)
    "Farewell for now...",
    # 314 (ID 460)
    "Igor: When you require a new",
    # 315 (ID 461)
    "Persona, I shall fuse the cards",
    # 316 (ID 462)
    "and create one for you.",
    # 317 (ID 463)
    "For me to forge a Persona,",
    # 318 (ID 464)
    "we must fuse demons summoned",
    # 319 (ID 465)
    "from the demon realm.",
    # 320 (ID 466)
    "To summon a demon, a specific card is required.",
    # 321 (ID 467)
    "Upon that card,",
    # 322 (ID 468)
    "the spell to call forth that demon",
    # 323 (ID 469)
    "is inscribed.",
    # 324 (ID 470)
    "They are called Summon Spell Cards, and each demon possesses only one.",
    # 325 (ID 471)
    "It is a card unique to them.",
    # 326 (ID 472)
    "Therefore...",
    # 327 (ID 473)
    "first,",
    # 328 (ID 474)
    "you must collect Spell Cards.",
    # 329 (ID 475)
    "Negotiate with the demons and obtain them yourselves.",
    # 330 (ID 476)
    "When encountering demons,",
    # 331 (ID 477)
    "fighting is not your only option.",
    # 332 (ID 478)
    "Do you understand?",
    # 333 (ID 479)
    "For they are not always seeking",
    # 334 (ID 480)
    "combat, you see...",
    # 335 (ID 481)
    "Igor: To take a newly fused",
    # 336 (ID 482)
    "Persona and wield it as your own,",
    # 337 (ID 483)
    "manifesting its true power...",
    # 338 (ID 484)
    "merely fusing it is not enough.",
    # 339 (ID 485)
    "Only by invoking the Persona",
    # 340 (ID 486)
    "and equipping it to your body",
    # 341 (ID 487)
    "can you master its strength.",
    # 342 (ID 488)
    "Each person can equip",
    # 343 (ID 489)
    "up to three Personas at once.",
    # 344 (ID 490)
    "Newly fused Personas",
    # 345 (ID 491)
    "remain safely in my care.",
    # 346 (ID 492)
    "Whenever necessary,",
    # 347 (ID 493)
    "please request an invocation from me.",
    # 348 (ID 494)
    "I can store up to 16 Personas in total,",
    # 349 (ID 495)
    "so feel free to exchange them as needed.",
    # 350 (ID 496)
    "Just as human personalities vary,",
    # 351 (ID 497)
    "Personas possess infinite varieties;",
    # 352 (ID 498)
    "each has distinct forms and powers.",
    # 353 (ID 499)
    "Depending on the circumstances,",
    # 354 (ID 500)
    "you must choose which Persona to use.",
    # 355 (ID 501)
    "Once you master their versatility,",
    # 356 (ID 502)
    "you shall become a truly splendid",
    # 357 (ID 503)
    "Persona user.",
    # 358 (ID 504)
    "You may equip up to three Personas",
    # 359 (ID 505)
    "at any one time.",
    # 360 (ID 506)
    "This puts them in a state where they can be manifested in battle.",
    # 361 (ID 507)
    "Calling forth a Persona",
    # 362 (ID 508)
    "in the midst of battle.",
    # 363 (ID 509)
    "The other two Personas",
    # 364 (ID 510)
    "remain charged in reserve,",
    # 365 (ID 511)
    "ready to be switched to active.",
    # 366 (ID 512)
    "An active Persona",
    # 367 (ID 513)
    "enhances and supplements",
    # 368 (ID 514)
    "your various capabilities.",
    # 369 (ID 515)
    "Without the power of Personas,",
    # 370 (ID 516)
    "you are merely fragile humans;",
    # 371 (ID 517)
    "you would have no defense",
    # 372 (ID 518)
    "against demonic spells,",
    # 373 (ID 519)
    "unable to endure their magic.",
    # 374 (ID 520)
    "If you took a direct blast,",
    # 375 (ID 521)
    "you would likely perish.",
    # 376 (ID 522)
    "Against magic,",
    # 377 (ID 523)
    "your defense will rise dramatically.",
    # 378 (ID 524)
    "Some may find their strength enhanced,",
    # 379 (ID 525)
    "while others see their agility increased.",
    # 380 (ID 526)
    "For every Persona represents",
    # 381 (ID 527)
    "a hidden aspect of your own psyche.",
    # 382 (ID 528)
    "Once you have equipped one,",
    # 383 (ID 529)
    "take a look at your stats.",
    # 384 (ID 530)
    "You will clearly see",
    # 385 (ID 531)
    "how you have been transformed.",
    # 386 (ID 532)
    "At first,",
    # 387 (ID 533)
    "no one can draw out the full",
    # 388 (ID 534)
    "potential of their Persona.",
    # 389 (ID 535)
    "The more you summon it, the more latent power you can unleash.",
    # 390 (ID 536)
    "The repertoire of attacks",
    # 391 (ID 537)
    "available in battle will expand.",
    # 392 (ID 538)
    "Even as your skills multiply",
    # 393 (ID 539)
    "and you unleash more powerful abilities,",
    # 394 (ID 540)
    "the SP required to summon it remains the same.",
    # 395 (ID 541)
    "Through battle, you grow,",
    # 396 (ID 542)
    "and your Persona grows alongside you;",
    # 397 (ID 543)
    "never forget that...",
    # 398 (ID 544)
    "Igor: This is merely",
    # 399 (ID 545)
    "a small piece of advice on my part...",
    # 400 (ID 546)
    "A Persona grows through 8 distinct ranks,",
    # 401 (ID 547)
    "so I suggest raising one",
    # 402 (ID 548)
    "to its ultimate potential.",
    # 403 (ID 549)
    "Surely,",
    # 404 (ID 550)
    "something advantageous will come of it...",
    # 405 (ID 551)
    "In Persona fusion,",
    # 406 (ID 552)
    "a myriad of factors come into play,",
    # 407 (ID 553)
    "from the minute to the momentous.",
    # 408 (ID 554)
    "Even when forging the same Persona,",
    # 409 (ID 555)
    "which Spell Cards were combined,",
    # 410 (ID 556)
    "the exact combination used...",
    # 411 (ID 557)
    "the compatibility between",
    # 412 (ID 558)
    "the demons' attributes and affinities,",
    # 413 (ID 559)
    "the positions of Terra and Luna during fusion,",
    # 414 (ID 560)
    "and whether additional essences were incorporated...",
    # 415 (ID 561)
    "I nearly neglected to mention...",
    # 416 (ID 562)
    "By incorporating an item",
    # 417 (ID 563)
    "into the fusion process,",
    # 418 (ID 564)
    "it is possible to induce special variations.",
    # 419 (ID 565)
    "Depending on the item,",
    # 420 (ID 566)
    "the outcome can sometimes be predicted in advance,",
    # 421 (ID 567)
    "in certain instances,",
    # 422 (ID 568)
    "yet at other times, even I cannot",
    # 423 (ID 569)
    "anticipate the outcome.",
    # 424 (ID 570)
    "I ask for your forgiveness should that occur.",
    # 425 (ID 571)
    "It is certainly well worth experimenting with...",
    # 426 (ID 572)
    "It possesses the power to shift the rank within the same tribe",
    # 427 (ID 573)
    "of the resulting Persona fusion.",
    # 428 (ID 574)
    "I encourage you to experiment with it",
    # 429 (ID 575)
    "for yourself.",
    # 430 (ID 577)
    "Are you saying we should flee from reality",
    # 431 (ID 578)
    "and ruin ourselves here?",
    # 432 (ID 579)
    "Forget the small stuff!",
    # 433 (ID 580)
    "We're here anyway, so let's play a little!",
    # 434 (ID 584)
    "Forget the details.",
    # 435 (ID 585)
    "Let's have some fun for a bit.",
    # 436 (ID 587)
    "If we're hanging out anyway,",
    # 437 (ID 588)
    "I would've way rather gone to a disco.",
    # 438 (ID 591)
    "Nanjo: What is the meaning of this place?!",
    # 439 (ID 592)
    "Nanjo: You are the one in charge",
    # 440 (ID 593)
    "of managing our funds,",
    # 441 (ID 594)
    "so refrain from frivolous spending!",
    # 442 (ID 595)
    "I could hang out here all day and never get bored~",
    # 443 (ID 597)
    "Just blow all your worries away!",
    # 444 (ID 598)
    "Gotta let off some steam once in a while~",
    # 445 (ID 599)
    "Elly: If memory serves,",
    # 446 (ID 600)
    "this was supposed to be a school...",
    # 447 (ID 601)
    "Elly: While letting off steam occasionally",
    # 448 (ID 602)
    "is certainly fine,",
    # 449 (ID 603)
    "please do not forget our true objective.",
    # 450 (ID 604)
    "Clerk: Welcome~!",
    # 451 (ID 605)
    "We handle money and coin",
    # 452 (ID 606)
    "exchanges here~!",
    # 453 (ID 607)
    "Would you like to exchange cash for coins?",
    # 454 (ID 608)
    "Clerk: Here at this counter,",
    # 455 (ID 609)
    "we exchange coins for prizes...",
    # 456 (ID 610)
    "That is our service...",
    # 457 (ID 612)
    "I am on a massive roll today!!",
    # 458 (ID 613)
    "I blew my entire fortune...",
    # 459 (ID 614)
    "How am I gonna survive starting tomorrow...?",
    # 460 (ID 615)
    "Afro Guy: Yeeeah!",
    # 461 (ID 616)
    "Back when I was just silver vine...",
    # 462 (ID 617)
    "Back when I was just a fresh green peach...",
    # 463 (ID 618)
    "the old man's pockets were bone dry.",
    # 464 (ID 619)
    "Ya feel me, baby~?",
    # 465 (ID 621)
    "Back when I was just a white lotus root...",
    # 466 (ID 622)
    "my girl was strawberry ramen.",
    # 467 (ID 623)
    "Betcha don't get it at all~",
    # 468 (ID 624)
    "Current Metal Card count:",
    # 469 (ID 625)
    "card(s).",
    # 470 (ID 626)
    "You possess.",
    # 471 (ID 627)
    "What would you like to do?",
    # 472 (ID 628)
    "Which explanation would you like to see?",
    # 473 (ID 629)
    "Numbers from 1 to 9 are placed randomly.",
    # 474 (ID 630)
    "Guess the correct sequence of the",
    # 475 (ID 631)
    "randomly placed numbers.",
    # 476 (ID 632)
    "A splendid prize",
    # 477 (ID 633)
    "can be obtained!",
    # 478 (ID 634)
    "If you fail to guess within the set turn limit, it is Game Over.",
    # 479 (ID 635)
    "equal to the number of rows on the RESULT screen.",
    # 480 (ID 636)
    "When your entered",
    # 481 (ID 637)
    "guess is incorrect,",
    # 482 (ID 638)
    "it is recorded row by row,",
    # 483 (ID 639)
    "so refer to it when making your next guess.",
    # 484 (ID 640)
    "Displayed above",
    # 485 (ID 641)
    "the input area,",
    # 486 (ID 642)
    "selected numbers light up and unselected ones stay dark, so refer to these lights",
    # 487 (ID 643)
    "to verify that numbers 1 to 9",
    # 488 (ID 644)
    "have been assigned without duplicates",
    # 489 (ID 645)
    "by checking this indicator.",
    # 490 (ID 646)
    "This game uses \"Metal Cards\" instead of coins.",
    # 491 (ID 647)
    "Change the number highlighted by the cursor",
    # 492 (ID 648)
    "to a lower number.",
    # 493 (ID 649)
    "Change the color (mark) of the highlighted number.",
    # 494 (ID 650)
    "Use this as an indicator when you decide",
    # 495 (ID 651)
    "that a number in that position is confirmed.",
    # 496 (ID 653)
    "Change to a higher number.",
    # 497 (ID 657)
    "Start the game.",
    # 498 (ID 658)
    "Quit Code Breaker.",
    # 499 (ID 659)
    "Move the cursor.",
    # 500 (ID 660)
    "The key strategy in this game",
    # 501 (ID 661)
    "is identifying positions that scored a Hit (H) in both rows.",
    # 502 (ID 662)
    "Positions that scored a Hit in both rows",
    # 503 (ID 663)
    "should definitely",
    # 504 (ID 664)
    "be marked first.",
    # 505 (ID 665)
    "The RESULT screen showing past attempts also provides vital clues,",
    # 506 (ID 666)
    "so make sure to consult it.",
    # 507 (ID 667)
    "Current coin count:",
    # 508 (ID 672)
    "A poker game where you can exchange",
    # 509 (ID 673)
    "cards once.",
    # 510 (ID 674)
    "First, 5 cards",
    # 511 (ID 675)
    "are dealt.",
    # 512 (ID 676)
    "Choose the cards you wish to keep",
    # 513 (ID 677)
    "using the directional buttons,",
    # 514 (ID 678)
    "and press \u25cb, \u2715, \u25b3, or \u25a1",
    # 515 (ID 679)
    "to HOLD (lock) them.",
    # 516 (ID 680)
    "After locking your held cards, press R1 or R2 to REDRAW,",
    # 517 (ID 681)
    "and all unheld cards will be replaced.",
    # 518 (ID 682)
    "After the REDRAW,",
    # 519 (ID 683)
    "if you have completed a winning hand, you win.",
    # 520 (ID 684)
    "The more coins you bet,",
    # 521 (ID 685)
    "the higher the payout",
    # 522 (ID 686)
    "(ODDS) when a winning hand is made.",
    # 523 (ID 687)
    "Whenever a winning hand is made,",
    # 524 (ID 688)
    "you can wager those winnings",
    # 525 (ID 689)
    "and challenge an Extra Game.",
    # 526 (ID 690)
    "Select SCORE.",
    # 527 (ID 691)
    "There are 3 types of Extra Games,",
    # 528 (ID 692)
    "and with each victory,",
    # 529 (ID 693)
    "your payout doubles.",
    # 530 (ID 694)
    "In the Extra Game, payouts",
    # 531 (ID 695)
    "can be challenged up to 1,000,000 coins.",
    # 532 (ID 696)
    "However, fail even once,",
    # 533 (ID 697)
    "and all current winnings are forfeit,",
    # 534 (ID 698)
    "so please be careful.",
    # 535 (ID 699)
    "[Extra Game 1]",
    # 536 (ID 700)
    "One face-up card on the far left,",
    # 537 (ID 701)
    "and 4 face-down cards are displayed on screen.",
    # 538 (ID 702)
    "From the 4 face-down cards,",
    # 539 (ID 703)
    "guess one with a higher number than the face-up card.",
    # 540 (ID 704)
    "If the chosen card and face-up card have the same value, it's a tie,",
    # 541 (ID 705)
    "and you may try again.",
    # 542 (ID 706)
    "[Extra Game 2]",
    # 543 (ID 708)
    "One face-down card is displayed on screen.",
    # 544 (ID 709)
    "Guess whether the face-down card",
    # 545 (ID 710)
    "is Higher or Lower than the face-up card.",
    # 546 (ID 711)
    "If both cards share the exact same number, it counts as a loss,",
    # 547 (ID 712)
    "so please take care.",
    # 548 (ID 713)
    "[Extra Game 3]",
    # 549 (ID 716)
    "If you think it is Spades or Clubs,",
    # 550 (ID 717)
    "If you think it is Hearts or Diamonds,",
    # 551 (ID 718)
    "select \"BLACK\".",
    # 552 (ID 719)
    "If your chosen color matches the card's color,",
    # 553 (ID 720)
    "you win.",
    # 554 (ID 721)
    "Insert 1 coin.",
    # 555 (ID 722)
    "Cancel HELD cards.",
    # 556 (ID 723)
    "[When a Winning Hand is Made]",
    # 557 (ID 724)
    "Challenge \"HI & LOW\".",
    # 558 (ID 725)
    "Confirm the card to flip.",
    # 559 (ID 726)
    "[Upon Winning Extra Game] Challenge again.",
    # 560 (ID 727)
    "Cancel bet",
    # 561 (ID 728)
    "coins.",
    # 562 (ID 730)
    "Without challenging the Extra Game,",
    # 563 (ID 731)
    "collect your payout coins.",
    # 564 (ID 733)
    "[Upon Winning Extra Game] End Extra Game and collect payout.",
    # 565 (ID 737)
    "[Upon Winning Extra Game] Do not use.",
    # 566 (ID 742)
    "Exchange unheld",
    # 567 (ID 743)
    "cards.",
    # 568 (ID 746)
    "Quit Poker.",
    # 569 (ID 749)
    "Select a card.",
    # 570 (ID 752)
    "A hand with two cards of matching rank",
    # 571 (ID 753)
    "in two sets (TWO PAIR).",
    # 572 (ID 754)
    "A hand with three cards of",
    # 573 (ID 755)
    "matching rank (THREE OF A KIND).",
    # 574 (ID 756)
    "A hand with 5 consecutive numbers",
    # 575 (ID 757)
    "in sequence (STRAIGHT).",
    # 576 (ID 758)
    "A hand with 5 cards of the same suit (FLUSH).",
    # 577 (ID 759)
    "Three of a kind plus a pair (FULL HOUSE).",
    # 578 (ID 761)
    "A hand with 4 cards of matching rank (FOUR OF A KIND).",
    # 579 (ID 762)
    "STRAIGHT FLUSH: A straight",
    # 580 (ID 763)
    "where all 5 cards share the same suit.",
    # 581 (ID 764)
    "Four of a kind plus a JOKER (FIVE OF A KIND).",
    # 582 (ID 765)
    "A 10-J-Q-K-A straight flush (ROYAL FLUSH).",
    # 583 (ID 766)
    "*In this Poker game,",
    # 584 (ID 767)
    "*For Straight-type hands,",
    # 585 (ID 768)
    "A cannot wrap around to 2 (e.g. K-A-2 is invalid).",
    # 586 (ID 769)
    "JOKER acts as a Wild Card",
    # 587 (ID 770)
    "and can substitute for any missing card in a hand.",
    # 588 (ID 776)
    "A Blackjack game where you",
    # 589 (ID 777)
    "compete one-on-one against the dealer.",
    # 590 (ID 778)
    "The computer serves",
    # 591 (ID 779)
    "as the dealer.",
    # 592 (ID 780)
    "2 cards each are dealt to you and the dealer.",
    # 593 (ID 781)
    "One of the dealer's 2 cards is dealt face down.",
    # 594 (ID 782)
    "Only when the dealer's face-up card is an Ace",
    # 595 (ID 783)
    "can you take INSURANCE.",
    # 596 (ID 785)
    "Regarding INSURANCE,",
    # 597 (ID 786)
    "an explanation is provided",
    # 598 (ID 787)
    "near the end of the rules.",
    # 599 (ID 788)
    "First, compare your cards with the dealer's and decide whether to Hit (draw another card)."
]

# Validation
chunk_path = 'scripts/retranslate/chunks/E3_part_01.json'
data = json.load(open(chunk_path, 'r', encoding='utf-8'))
entries = data['entries']

print(f"Total entries in chunk: {len(entries)}")
print(f"Total translations provided: {len(translations)}")

assert len(entries) == len(translations), f"Length mismatch: {len(entries)} vs {len(translations)}"

empty_count = 0
placeholder_count = 0
for idx, (entry, trans) in enumerate(zip(entries, translations)):
    entry['translation_en'] = trans
    if not trans or trans.strip() == "":
        print(f"Error: empty translation at index {idx}, ID {entry['id']}")
        empty_count += 1
    if trans in ('...', '!', '?') and entry['text_jp'] not in ('……', '…', '!', '?'):
        print(f"Warning: placeholder translation at index {idx}, ID {entry['id']}")
        placeholder_count += 1

print(f"Empty count: {empty_count}, Placeholder count: {placeholder_count}")

with open(chunk_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

print("Saved successfully!")

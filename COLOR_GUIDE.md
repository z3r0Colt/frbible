# Fresh Look Bible Color Code: Complete Specification

This document reverse-engineers the color coding in *A Fresh Look at The Whole Bible,
Digital Book, Color Text, Light Mode* (KJV, Joshua Paul Smith, 2024), the PDF in this
repo. It is written so that a person or an AI can apply the same system to another
Bible text and get the same result.

Every number here was measured from the PDF by `tools/extract_colors.py`, which reads
the color of every word on all 2,196 pages. All 31,102 KJV verses were found, plus
116 psalm titles (stored as verse 0).

**Files that go with this guide**

| File | What it holds |
|---|---|
| `data/tagged_bible.txt` | The whole Bible, one verse per line, every colored word marked `[word\|CODE]`, words of Christ inside `« »`. Best file for teaching an AI by example. |
| `data/tagged_verses.jsonl` | Same thing as JSON, with the font "voice" of every segment. |
| `data/tagged_words.csv` | 256,000+ rows. One row per colored word: reference, word, color, voice, red-letter flag. |
| `data/lexicon.json` | Every colored term with how many times it got each color, and how many times it was left black. |
| `reports/categories/NN_*.md` | One file per color. Every term in that color, and every verse it appears in. |
| `reports/verses_by_color/*.txt` | One file per color. Every verse that contains that color. |
| `reports/ambiguous_terms.md` | Every word that takes more than one color, with counts and verses for each. These are the judgment calls. |
| `reports/coverage.md` | How often each word is colored versus left black. |

---

## 1. The big idea

The color answers the reader's background questions about a passage. The legend page
groups them as **Who? What? Where? When? How many?**

* Who: God (purple), Angels and demons (olive), People (blue)
* What: Nature (teal)
* Where: Places (green)
* When: Time (brown)
* How many: Number (crimson)

Each family has two to four **shades**. The brightest shade is for the most specific
words (proper names, exact numbers). Darker shades are for general words, and the
darkest for small function words. The book says it this way: "Jerusalem" is brighter
than "city", which is brighter than "there".

Only these kinds of words are colored. Verbs, adjectives (with a few exceptions
below), abstract nouns, body parts, objects, and most function words stay black.

---

## 2. The 19 categories

Two sets of hex values exist. The **legend** values are on the Color Code page (PDF
pages 10 and 11). The **text** values are what is actually used on the Bible pages.
Use the text values to reproduce the look.

| # | Code | Short | Category | Text hex | Legend hex | Words colored | Verses |
|---|---|---|---|---|---|---:|---:|
| 1 | GOD_FATHER | GF | God the Father (and God in general) | `#7a36bf` | `#8d64aa` | 24,983 | 12,231 |
| 2 | GOD_SON | GS | God the Son | `#6a2ea6` | `#7b5795` | 6,952 | 3,288 |
| 3 | GOD_SPIRIT | HS | God the Holy Spirit | `#5a278c` | `#6b4982` | 297 | 253 |
| 4 | ANGELIC | AN | Angelic beings | `#a19638` | `#9b9533` | 697 | 628 |
| 5 | DEMONIC | DE | Demonic beings, false gods, idols | `#736b28` | `#6d6428` | 1,354 | 945 |
| 6 | PROPER_PERSON | PN | Named individuals | `#218fd9` | `#0092cc` | 17,075 | 8,477 |
| 7 | PEOPLE_GROUP | PG | Nations, tribes, sects | `#1f87cc` | `#007aad` | 4,159 | 3,030 |
| 8 | GENERAL_PEOPLE | GP | Common nouns for people | `#1b76b2` | `#00639a` | 34,533 | 17,473 |
| 9 | PRONOUN | PR | Personal pronouns for humans | `#244a7f` | `#004474` | 78,645 | 25,428 |
| 10 | ANIMAL | BE | Animals | `#469594` | `#007b85` | 3,396 | 2,017 |
| 11 | PLANT | PL | Plants and plant products | `#007b78` | `#007b85` | 2,167 | 1,196 |
| 12 | PROPER_PLACE | PP | Named places | `#2fa648` | `#00a651` | 10,181 | 6,094 |
| 13 | GENERAL_PLACE_1 | L1 | Place nouns | `#247f38` | `#008641` | 19,594 | 11,088 |
| 14 | GENERAL_PLACE_2 | L2 | Position and direction words | `#195928` | `#00652e` | 10,428 | 7,138 |
| 15 | SPECIFIC_TIME | T1 | Units and points of time | `#995226` | `#a65522` | 5,965 | 4,230 |
| 16 | GENERAL_TIME | T2 | Time sequence words | `#733e1d` | `#6c3a18` | 16,582 | 10,378 |
| 17 | NUMBER | NU | Numbers and ordinals | `#9c0f2e` | `#a71a32` | 6,216 | 3,975 |
| 18 | MEASUREMENT | ME | Units of measure, dimensions | `#7f0b25` | `#7f0b25` | 1,296 | 597 |
| 19 | QUANTITY | QU | Indefinite amounts | `#66091d` | `#59081a` | 12,327 | 8,829 |

The family names on the legend are God, Angels, People, Nature, Places, Time, Number.
The small header bar on every page uses the bright shade of each family:
God `#7a36bf`, Angels `#a19638`, People `#218fd9`, Nature `#007b78`, Places `#2fa648`,
Time `#995226`, Number `#9c0f2e`.

### Other text colors (not categories)

| Hex | Meaning | Where |
|---|---|---|
| `#000000` | Normal uncolored text | Everywhere |
| `#7a1315` | **Words of Christ** (red letter). Only the uncolored words turn red. Colored words inside Christ's speech keep their category color. | Gospels, Acts, Revelation, a few epistle quotes (12,000+ spans) |
| `#6b0b0c` | Darker red. KJV **italic (supplied) words** inside the words of Christ. Example: Matthew 5:3 "Blessed *are* the poor in spirit". Supplied words outside red letter are not marked. | 352 spans |
| `#404756` | Slate gray "So" and "Thus" that open a **summary or closing statement** of a section. Example: Genesis 2:1 "Thus the heavens and the earth were finished". | 418 spans |
| `#707787` | Gray **structure words**. Psalm titles ("A Psalm of David"), and the hinge words of Proverbs set apart on their own line ("but", "and", "so is", "better", "than"). Also the verse numbers (small size). | Psalms, Proverbs |

---

## 3. Fonts carry a second layer: who is speaking

The color tells you *what* a word is. The font tells you *whose voice* it is.

| Font | Voice | Words (approx.) |
|---|---|---:|
| Helvetica Neue **Medium** | Narration | 351,000 |
| Helvetica Neue **Roman** (lighter) | Quoted human speech, indented | 302,000 |
| **Mr Eaves XL Mod OT** (small caps) | Speech of God | 180,000 |
| Helvetica Neue **Light** | Speech inside speech (2nd level) | 19,000 |
| Helvetica Neue **Thin** | 3rd level nested speech | 440 |
| Helvetica Neue **Italic / Light Italic** | Scripture quoted inside speech (OT quoted in NT) | 6,500 |
| Helvetica Neue **Bold** | Closing benedictions ("The grace of our Lord Jesus Christ") | 890 |

The words of Christ in the New Testament use the normal speech fonts, in red. In the
Old Testament, God's speech is shown by the small caps font, not by red.

---

## 4. Numbers are rewritten as numerals

This is the one place the Fresh Look edition changes the wording. Number words that
give a count, an age, a date or a size are turned into digits:

* "four hundred thirty and five" becomes **435** (Ezra 2:67)
* "six hundred thousand and three thousand and five hundred and fifty" becomes **603,550** (Numbers 1:46)
* "the first day" becomes **the 1st day**, "the seventh day" becomes **the 7th day** (Genesis 1 and 2)
* "twelve" is almost always **12**, "ten" usually **10**

Small numbers are often left as words in ordinary prose and poetry ("two great lights"
Genesis 1:16, "two by two", "ten thousands" Deuteronomy 33:17). Counts measured in
the PDF: "two" 383 times as a word vs "2" 234 times; "seven" 149 vs "7" 219;
"first" 252 vs "1st" 167; "twelve" 0 vs "12" 157.

"one" is tricky. When it means "a single person/thing" or "any one" it is QUANTITY
(967 times). When it is a real count it becomes "1" or stays "one" as NUMBER.

If you are tagging a different Bible and do not want to change its words, keep the
words and simply color them NUMBER.

---

## 5. Category rules in detail

The examples below are from the real data. For the full list of every term and every
verse, see `reports/categories/`.

### 5.1 GOD_FATHER `#7a36bf`

The default color for God. It is used for **every name and title of God** unless the
text points clearly at the Son or the Spirit.

* Names and titles: LORD, Lord, God, GOD, Father (of God), Almighty, most High,
  Holy One, King (when God is King), living God, Saviour (OT), Redeemer, Maker, Rock,
  Creator, Judge, JEHOVAH, JAH, I AM, Godhead, Ancient of days, Mighty One,
  Jehovah-nissi, The LORD our righteousness, Jealous (as a name).
* **Pronouns that refer to God** take God's color, not the pronoun color: I, me, my,
  mine, he, him, his, thou, thee, thy, thine, who, whom, whose, himself, thyself,
  us/our ("Let us make man", Genesis 1:26). About 1 in 4 uses of "I" in the Bible is
  God speaking.
* **"Lord" and "God" stay purple Father even when they point to Jesus.** "Lord Jesus"
  is `[Lord|GF] [Jesus|GS]` all 119 times. "My Lord and my God" (John 20:28) is
  `[Lord|GF] … [God|GF]`. The Son color is used for his personal names, his messianic
  titles, and pronouns for him.
* "lord" for a human master is GENERAL_PEOPLE (249 times). "gods" for idols is DEMONIC.

### 5.2 GOD_SON `#6a2ea6`

* Names: Jesus, Christ, Jesus Christ, Emmanuel/Immanuel, Messiah/Messias.
* Titles: Son (of God), Son of man (when it is Christ; the 93 uses for the prophet
  Ezekiel and the uses meaning mankind are GENERAL_PEOPLE), Son of David, Lamb (of God),
  Word (John 1:1, 1:14; 1 John; Revelation 19:13), Light (John 1, John 8:12),
  Bread of life, good Shepherd, Door, Way, Truth, Life, Alpha, Omega, Branch,
  Prophet, Master (59 times, when people address Jesus), Rabbi, King (of the Jews),
  Holy child, Prince, Captain.
* Pronouns for Jesus: he, him, his, I, me, my, thou, thee, who, whom, himself.
* **Old Testament appearances and prophecies of Christ** also get this color. Every
  case in the data:
  Genesis 48:16 "the Angel which redeemed me";
  Exodus 23:20, 23:23, 32:34 "mine Angel";
  Genesis 49:10 "Shiloh";
  Numbers 24:17 "a Star… a Sceptre";
  Deuteronomy 18:15, 18 "a Prophet… like unto me";
  Joshua 5:13-15 "a man… captain of the host of the LORD";
  Job 19:25 "my redeemer liveth";
  Psalm 2:7, 2:12 "my Son", "Kiss the Son";
  Psalm 110:4 "Thou art a priest for ever";
  Isaiah 7:14 "Immanuel";
  Isaiah 9:6 "child… son… Wonderful, Counseller, The mighty God, The everlasting
  Father, The Prince of Peace" (all Son color, even "Father");
  Isaiah 11:1 "Branch"; Isaiah 19:20 "a saviour, and a great one";
  Daniel 3:25 "the Son of God"; Daniel 7:13 "the Son of man";
  Daniel 8:25 "Prince of princes"; Daniel 9:24-26 "most Holy", "Messiah the Prince";
  Hosea 2:16 "Ishi… Baali"; Zechariah 3:8, 6:12 "the BRANCH".
* The plain "angel of the LORD" is ANGELIC (197 times), not Son.

### 5.3 GOD_SPIRIT `#5a278c`

Spirit (of God, of the LORD, holy Spirit), Holy Ghost, Comforter (when it is the
Spirit; 4 uses are GENERAL_PEOPLE, a human comforter), Spirit of truth, Holy Spirit.
A lower-case "spirit" meaning a person's spirit or a mood is not colored. An
"unclean spirit" or "evil spirit" is DEMONIC.

### 5.4 ANGELIC `#a19638`

angel, angels, archangel, Michael, Gabriel, cherub, cherubims, seraphims, watcher,
holy one(s) (Daniel 4), and "hosts" in the title "LORD of hosts" (273 times; the
hosts are the angel armies). The four "beasts" (living creatures) around the throne in
Revelation 4 and 5 are ANGELIC. "Death" the rider of the pale horse (Revelation 6:8) and the
star named "Wormwood" (Revelation 8:11) appear here too. Pronouns for angels stay
PRONOUN (Luke 1:29 "she saw him"). A human army called a "host" is GENERAL_PEOPLE
(166 times).

### 5.5 DEMONIC `#736b28`

Everything that is a rival to God:

* Satan, devil, devils, the devil's "angels" (Matthew 25:41, Revelation 12:9), Beelzebub, Belial, tempter, legion, unclean spirit(s),
  familiar spirits, antichrist, false Christs, false prophet.
* False gods by name: Baal, Baalim, Baal-peor, Baal-berith, Baal-zebub, Dagon,
  Molech/Moloch, Milcom, Chemosh, Ashtaroth/Ashtoreth, Nisroch, Bel, Diana,
  queen of heaven, goddess, Succoth-benoth.
* Idol words: gods (233 times), god (a false god, 54 times), idols, images, graven
  image(s), molten image(s), molten calf, groves, high places, teraphim, likeness,
  similitude, abomination(s) (when it means an idol), vanities.
* In Revelation: the beast (from the sea and the earth), the dragon, the old serpent,
  the woman on the scarlet beast and the whore (Revelation 17). In the Old Testament
  "dragon" is a wild creature and is ANIMAL; in Revelation 12 it is Satan and is
  DEMONIC. The same goes for "serpent" (ANIMAL in Genesis 3, DEMONIC in Revelation
  12:9 and 20:2).

### 5.6 PROPER_PERSON `#218fd9`

Any named individual human: David, Moses, Paul, Mary, Pharaoh, Nebuchadnezzar,
including possessives (David's). 2,149 different names.

**Israel, Judah, Ephraim, Benjamin, Manasseh, Jacob** can be a person, a tribe, or a
land. They are PROPER_PERSON only when the man himself is meant (Genesis 32:28 "thy
name shall be called… Israel"). See 5.7 and 5.12.

### 5.7 PEOPLE_GROUP `#1f87cc`

Nations, tribes, clans, sects and ethnic names used for **people**: Jews, Gentiles,
Philistines, Levites, Egyptians, Pharisees, Sadducees, Amorites, Chaldeans, Greeks,
Hebrews, Israelites, Nethinims, Nazarite, Kohathites, Gershonites, hypocrites
(used as a group label in the Gospels).

Tribe names count here when they mean the tribe: "of the tribe of Benjamin", "the
children of Reuben". **"Israel" is PEOPLE_GROUP in "children of Israel"** (616 times).

### 5.8 GENERAL_PEOPLE `#1b76b2`

Common nouns for people, and also adjectives used as nouns for people:
man, men, king, people, son, children, father, brethren, servant, priest, wife,
congregation, woman, nations, princes, disciples, tribe, prophet, mother, seed (as
offspring, 210 times), inhabitants, child, elders, families, host (an army),
heathen, stranger, husband, captain, neighbour, enemy, saints, church, ruler, army,
messengers, the wicked, the righteous, the poor, the dead, the young.
Titles of address: Rabbi (for John), Sir, Master (human), lord (human).

* **"house" meaning a family or dynasty** is GENERAL_PEOPLE ("the house of Israel",
  "the house of David", 621 times). "house" meaning a building is GENERAL_PLACE_1
  (1,398 times).
* "Son of man" meaning a human (Ezekiel is called this 93 times) is here.

### 5.9 PRONOUN `#244a7f`

All personal, possessive, reflexive and relative pronouns that refer to **humans**
(or to people groups): I, me, my, mine, we, us, our, thou, thee, thy, thine, ye, you,
your, he, him, his, she, her, they, them, their, who, whom, whose, whoso, whosoever,
whomsoever, myself, himself, themselves, one (as a pronoun), another, others.

* The color is chosen by the **referent**, not the word. Pronouns for God take
  GOD_FATHER, for Jesus take GOD_SON. Of 15,000+ uses of he/him/his, about 3,800 are
  God and 2,800 are Christ.
* **"it", "its", "which", "that", "what" are never colored.** Pronouns for animals or
  things are not colored either.
* A pronoun for an angel or a demon stays PRONOUN (the system does not carry the
  olive color to pronouns).

### 5.10 ANIMAL `#469594`

Every animal word: sheep, cattle, beasts, horses, flock, oxen, ram, lambs, lion, ass,
bullock, goats, fowls, camels, kid, serpent, fish, creature, creeping thing, bird,
he goats, kine, dogs, calf, eagle, dove, heifer, locusts, swine, colt, frogs, worm,
badgers, mules, firstling, bear, flies, moth, owl, young pigeons, behemoth,
leviathan. Group words for animals (flock, herd) count.

"Lamb" is ANIMAL except when it is Christ (28 times GOD_SON). "beast" in Daniel and
Revelation is DEMONIC when it is the evil beast and ANGELIC for the living creatures.

### 5.11 PLANT `#007b78`

Trees, plants, grains and plant products: tree, fruit, corn, seed (of plants, 63
times), grass, vine, branches, cedar, wheat, thorns, fig, olive, grapes, barley, root,
palm, spices, frankincense, myrrh, hyssop, flax, oil (olive oil), reed, chaff, stubble,
straw, leaves, flower, lilies, almonds, wormwood, tares, mandrakes, scarlet (dye),
rod (a branch). "Branch" for Christ is GOD_SON.

### 5.12 PROPER_PLACE `#2fa648`

Any named place: countries, cities, rivers, mountains, seas, regions. Jerusalem,
Judah, Egypt, Babylon, Jordan, Moab, Zion, Samaria, Assyria, Galilee, Lebanon,
Beth-el, Euphrates, Sinai, Red (sea), Nazareth, Macedonia, Asia.

**Nation names used as a political unit are places.** "king of Israel" (131),
"house of Israel" (136, with house as people), "all Israel" (47), "God of Israel"
(121), "elders of Israel", "tribes of Israel", "reign over Israel". In total Israel is
PROPER_PLACE 1,688 times, PEOPLE_GROUP 711 times, PROPER_PERSON 166 times. "Jacob" as
a poetic name for the nation ("O Jacob", "the God of Jacob") is a place 88 times.

### 5.13 GENERAL_PLACE_1 `#247f38`

Nouns for locations, buildings, land forms and the cosmos:
land, house (building), earth, city, place, heaven, sea, altar, tabernacle,
wilderness, field, way, world, waters, gate, mount, temple, ground, door, country,
wall, mountains, throne, river, border, valley, sanctuary, tent, camp, prison, court,
pit, hill, villages, ship, vineyard, plain, rock, chambers, streets, coast, grave,
hell, sun, stars, firmament, deep.

Compass and side words that name a region are here: east, west, north, south,
right (hand side), left, near, far, off, thence, top.

### 5.14 GENERAL_PLACE_2 `#195928`

The small words of **position and direction**:
before (in front of), up, there, down, about, where, under, forth, midst, over,
toward, out, side, round about, therein, through, high, above, wherein, here, upon,
away, against, into, whither, throughout, within, without, thither, nigh, between,
behind, whence, abroad, beyond, beside, beneath, hither, hence, apart, among,
upward, backward, fro, nether, lower.

"before" is the classic split. Before = **in front of** (place) is L2 (1,529 times).
Before = **earlier in time** is GENERAL_TIME (231 times).

### 5.15 SPECIFIC_TIME `#995226`

Units and points on the calendar or clock: day, days, time (a set time), years, year,
night, month, morning, sabbath, hour, even, evening, passover, daily, to morrow,
morrow, harvest, jubile, winter, summer, midnight, week, noon, yesterday, twilight,
named months (Abib, Adar, Nisan, Zif, Bul, Ethanim, Chisleu, Elul, Tebeth, Sivan),
feasts by name (Pentecost, Purim, feast of unleavened bread, feast of weeks).

### 5.16 GENERAL_TIME `#733e1d`

Words that place events in sequence or duration without a calendar value:
when, then, now, so (meaning "then" or "and so it happened"), again, after, ever,
it came to **pass**, until, this (day), old, yet, more (any more), before (earlier),
while, end, no more, began, till, long, new, times, generation(s), beginning,
everlasting, early, never, continually, since, afterward, soon, always, once, season,
former, eternal, next, age, suddenly, henceforth, already, latter, perpetual,
evermore, straightway, immediately.

* "came to pass" and "shall come to pass" are tagged as time words.
* "so" is GENERAL_TIME 1,158 times. It is left black when it means "in this way".
  "and it was so" (Genesis 1) is colored.

### 5.17 NUMBER `#9c0f2e`

Cardinal and ordinal numbers (as digits or words), and number words: two, first, 1st,
12, seven, 3rd, half, number, numbered, thousands, hundreds, double, twice, thrice,
twain, tithe(s), tenth, sevenfold, fourfold. See section 4.

### 5.18 MEASUREMENT `#7f0b25`

Units and dimensions: cubit(s), shekel(s), breadth, length, height, depth,
thickness, measure(d), weight, weighed, talent(s), ephah, hin, homer, omer, bath(s),
log, cab, gerah, bekah, maneh, pound, drams, span, handbreadth, reed (as a measure),
furlongs, fathoms, acres, paces, deals (tenth deals), balances, scales, "long"
(as length, 30 times), "broad", "square", "a day's journey".

### 5.19 QUANTITY `#66091d`

Indefinite amounts and degree words: all (5,534 times), every, one (any one), many,
more, both, none, much, another, multitude, very, whole, some, only, part, little,
increase, great (as in great number), few, abundance, exceeding, each, too, any,
multiplied, abundantly, remnant, add, least, less, equal, full, residue, several,
alone, together, innumerable, manifold, wholly, altogether, rest.

---

## 6. How to decide in a hard case

Use these steps in order. They match what the PDF does.

1. **Is it God?** Any name, title or pronoun for God is purple. Choose Son for
   Jesus' personal names, messianic titles and pronouns; Spirit for the Holy Spirit;
   Father for everything else (including "Lord" and "God" used of Jesus).
2. **Is it a spirit being?** Good angels olive-bright. Satan, demons, false gods and
   idols olive-dark.
3. **Is it a person?** Named person bright blue. Nation or tribe acting as people
   medium blue. A common noun for people (or a "house" meaning family) dark blue.
   A human pronoun darkest blue.
4. **Is it an animal or plant?** Teal.
5. **Is it a place?** Named place bright green (including nations as political
   units: "king of Israel"). A place noun medium green. A position word (up, there,
   before = in front of) dark green.
6. **Is it a time?** A calendar unit bright brown. A sequence word (when, then, again,
   before = earlier) dark brown.
7. **Is it an amount?** An exact number crimson. A unit of measure darker. An
   indefinite amount (all, many) darkest.
8. **Otherwise leave it black.** Never color verbs, "it", "which", "that", body
   parts, objects (sword, bread, gold), or abstract nouns (love, sin, glory).

Multi-word names are colored as one unit: "Holy Ghost", "Son of man", "most High",
"high places", "creeping thing", "young bullock", "to morrow", "feast of unleavened
bread", "The Prince of Peace".

---

## 7. Known quirks in the source

The PDF is hand-colored and very consistent, but not perfect. A few examples found in
the data:

* John 3:16 colors "he gave his only begotten Son" with the **Son** color, although
  "he" is the Father.
* Romans 10:9 colors "God hath raised **him** from the dead" with the Father color,
  although "him" is Jesus.
* Small counts of odd one-off tags exist (for example "all" as GENERAL_PEOPLE once).
  Not every minority tag is an error. "Jesus" is PROPER_PERSON 3 times, and all 3
  are right: Acts 7:45 and Hebrews 4:8 mean Joshua, and Colossians 4:11 is "Jesus,
  which is called Justus".

When the data and the rules in section 6 disagree on a one-off, follow the rules.
`reports/ambiguous_terms.md` lists every such split so you can judge.

Extraction notes: about 20 verses (mostly long place lists in Joshua 15 and 19, and
Luke 1:46-47) have a few words that slipped across a verse boundary because of the
chart layout. The colors of those words are still correct.

---

## 8. Prompt for an AI tagging another Bible

Paste this guide and a few hundred example lines from `data/tagged_bible.txt` into
the AI's context, then use a prompt like this:

```
You are applying the Fresh Look Bible color code to a Bible text.
Rules: follow COLOR_GUIDE.md exactly. Output each verse on one line as
REF<TAB>text, wrapping every colored word or phrase as [word|CODE] using the
19 codes (GF GS HS AN DE PN PG GP PR BE PL PP L1 L2 T1 T2 NU ME QU).
Wrap the words of Christ in « ». Do not change any other words.
Choose the color of every pronoun by who it refers to (God = GF, Jesus = GS,
humans = PR; "it", "which", "that" are never colored).
Here are tagged examples from the KJV:
<examples>
...lines from data/tagged_bible.txt...
</examples>
Now tag these verses:
<verses>
...
</verses>
```

Tips:

* Give the model examples from the **same book** you are tagging. The choices for
  "Israel", "house", "before" and "so" depend on the book's style.
* For a KJV-based text you can pre-tag with `data/lexicon.json` (use the most common
  color of each word) and let the AI fix only the ambiguous words listed in
  `reports/ambiguous_terms.md`. This alone gets most words right; the AI's job is the
  pronoun referents and the split words.
* To check an AI's output against this KJV, compare its `[word|CODE]` tags verse by
  verse with `data/tagged_bible.txt`.

---

## 9. Regenerating everything

```
pip install pymupdf
python3 tools/extract_colors.py   # PDF -> data/
python3 tools/build_reports.py    # data/ -> reports/
```

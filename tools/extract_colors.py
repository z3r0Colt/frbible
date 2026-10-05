"""Extract the Fresh Look Bible color coding into machine-readable data.

Reads the PDF, walks every text page in reading order, tracks book/chapter/verse
from the verse-number markers, and records each span with its color category.

Outputs (in data/):
  tagged_verses.jsonl   one line per verse: ref, plain text, tagged segments
  tagged_bible.txt      one line per verse with inline [word|CODE] tags
  tagged_words.csv      one row per colored term: ref, term, category, voice
  unknown_colors.txt    any body-text colors not in the palette (QA)
"""
import collections
import csv
import glob
import json
import os
import re
import sys

import pymupdf

PDF = "Fresh Look Whole Bible Digital Book Color Text-0001.pdf"
OUT = "data"

# Body-text color -> category code (verified against the legend on PDF pages 10-11)
CATEGORIES = {
    0x7A36BF: "GOD_FATHER",
    0x6A2EA6: "GOD_SON",
    0x5A278C: "GOD_SPIRIT",
    0xA19638: "ANGELIC",
    0x736B28: "DEMONIC",
    0x218FD9: "PROPER_PERSON",
    0x1F87CC: "PEOPLE_GROUP",
    0x1B76B2: "GENERAL_PEOPLE",
    0x244A7F: "PRONOUN",
    0x469594: "ANIMAL",
    0x007B78: "PLANT",
    0x2FA648: "PROPER_PLACE",
    0x247F38: "GENERAL_PLACE_1",
    0x195928: "GENERAL_PLACE_2",
    0x995226: "SPECIFIC_TIME",
    0x733E1D: "GENERAL_TIME",
    0x9C0F2E: "NUMBER",
    0x7F0B25: "MEASUREMENT",
    0x66091D: "QUANTITY",
}
# Short codes used in data/tagged_bible.txt
SHORT = {
    "GF": "GOD_FATHER", "GS": "GOD_SON", "HS": "GOD_SPIRIT", "AN": "ANGELIC",
    "DE": "DEMONIC", "PN": "PROPER_PERSON", "PG": "PEOPLE_GROUP",
    "GP": "GENERAL_PEOPLE", "PR": "PRONOUN", "BE": "ANIMAL", "PL": "PLANT",
    "PP": "PROPER_PLACE", "L1": "GENERAL_PLACE_1", "L2": "GENERAL_PLACE_2",
    "T1": "SPECIFIC_TIME", "T2": "GENERAL_TIME", "NU": "NUMBER",
    "ME": "MEASUREMENT", "QU": "QUANTITY",
}
TEXT_HEADER = """# Fresh Look Bible color coding, inline form. One verse per line: REF<TAB>text
# Colored words: [word|CODE].  Words of Christ (red letter): \u00ab ... \u00bb
# Verse 0 of a psalm is its title. Codes:
""" + "".join(f"#   {k} = {v}\n" for k, v in SHORT.items()) + "\n"

# Non-category text colors
TEXT_COLORS = {
    0x000000: None,
    0x7A1315: "RED",          # words of Christ
    0x6B0B0C: "RED_SUPPLIED",  # KJV italic (supplied) words inside words of Christ
    0x404756: "SUMMARY",       # "Thus"/"So" summary-statement markers
}
VERSE_COLOR = 0x707787
SKIP_COLORS = {0x878787, 0x6D6E71, 0xA6A4A4, 0xFFFFFF, 0x636466, 0x58595B,
               0xA7A9AC, 0x939598, 0x8B909E, 0x414042, 0x666666}
LEGEND = "God Angels People Nature Places Time Number"

# Overview page groups (first, last) in PDF order -> books they introduce
GROUP_BOOKS = [
    ["Genesis"], ["Exodus"], ["Leviticus"], ["Numbers"], ["Deuteronomy"],
    ["Joshua"], ["Judges"], ["Ruth"], ["1 Samuel", "2 Samuel"],
    ["1 Kings", "2 Kings"], ["1 Chronicles", "2 Chronicles"], ["Ezra"],
    ["Nehemiah"], ["Esther"], ["Job"], ["Psalms"], ["Proverbs"],
    ["Ecclesiastes"], ["Song of Solomon"], ["Isaiah"], ["Jeremiah"],
    ["Lamentations"], ["Ezekiel"], ["Daniel"], ["Hosea"], ["Joel"], ["Amos"],
    ["Obadiah"], ["Jonah"], ["Micah"], ["Nahum"], ["Habakkuk"], ["Zephaniah"],
    ["Haggai"], ["Zechariah"], ["Malachi"], ["Matthew"], ["Mark"], ["Luke"],
    ["John"], ["Acts"], ["Romans"], ["1 Corinthians"], ["2 Corinthians"],
    ["Galatians"], ["Ephesians"], ["Philippians"], ["Colossians"],
    ["1 Thessalonians"], ["2 Thessalonians"], ["1 Timothy"], ["2 Timothy"],
    ["Titus"], ["Philemon"], ["Hebrews"], ["James"], ["1 Peter"], ["2 Peter"],
    ["1 John"], ["2 John"], ["3 John"], ["Jude"], ["Revelation"],
]
CHAPTERS = {"1 Samuel": 31, "1 Kings": 22, "1 Chronicles": 29}


def voice(font):
    """Map the font to the layout's speech layer."""
    if font.startswith("MrEaves"):
        return "divine"          # speech of God (small caps)
    f = font.split("-")[-1]
    return {
        "Md": "narration", "Roman": "speech", "Lt": "speech2", "Th": "speech3",
        "It": "quote", "LtIt": "quote", "Bd": "emphasis", "Cn": "other",
    }.get(f, f)


def page_lines(page):
    """Lines in visual reading order (top to bottom, then left to right).

    The PDF content stream sometimes places a verse number after its text,
    so we sort by position instead of trusting stream order.
    """
    lines = [l for b in page.get_text("dict")["blocks"] for l in b.get("lines", [])]
    return sorted(lines, key=lambda l: (round(l["bbox"][1] / 3), l["bbox"][0]))


def overview_groups(doc):
    groups = []
    for pn in range(12, len(doc)):
        header = "".join(
            s["text"] for b in doc[pn].get_text("dict")["blocks"]
            for l in b.get("lines", []) for s in l["spans"]
            if s["color"] == 0x878787 and round(s["size"]) == 8)
        if "﻿" in header:
            if groups and groups[-1][1] == pn - 1:
                groups[-1][1] = pn
            else:
                groups.append([pn, pn])
    return groups


def seg_term(text):
    return text.strip(" ,.;:?!()\u2019'")


def apply_corrections(verses):
    """Apply tools/corrections/*.tsv. Returns {(verse_key, seg_index): original_tag}.

    Each row names a verse, a term, which match of (term, from-color) to change
    (1-based, or * for all), and the new color. Files apply in name order. A row that matches nothing is an
    error, so a typo can never silently do nothing.
    """
    index = {f"{b} {c}:{v}": (b, c, v) for (b, c, v) in verses}
    orig, errors = {}, []
    files = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "corrections", "*.tsv")))
    for path in files:
        # Resolve every row of a file against the colors as they stood before
        # that file, so "him #1" and "him #2" mean the same words they did when
        # the file was written.
        changes = []
        for n, line in enumerate(open(path, encoding="utf-8"), 1):
            if not line.strip() or line.startswith("#"):
                continue
            ref, term, occ, src, dst = line.rstrip("\n").split("\t")[:5]
            where = f"{os.path.basename(path)}:{n}"
            key = index.get(ref)
            if key is None:
                errors.append(f"{where} unknown ref {ref}")
                continue
            hits = [i for i, s in enumerate(verses[key])
                    if s[1] == src and seg_term(s[0]) == term]
            if occ != "*":
                k = int(occ)
                hits = hits[k - 1:k]
            if not hits:
                errors.append(f"{where} no {term!r} as {src} in {ref}")
            changes += [(key, i, src, dst) for i in hits]
        for key, i, src, dst in changes:
            orig.setdefault((key, i), src)
            verses[key][i][1] = dst
    if errors:
        sys.exit("correction errors:\n  " + "\n  ".join(errors))
    print(f"corrections applied: {len(orig)} words", file=sys.stderr)
    return orig


def main():
    doc = pymupdf.open(PDF)
    groups = overview_groups(doc)
    assert len(groups) == len(GROUP_BOOKS), len(groups)
    os.makedirs(OUT, exist_ok=True)

    verses = collections.OrderedDict()  # (book, ch, vs) -> list of [text, tag, voice]
    unknown = collections.Counter()

    for gi, (first, last) in enumerate(groups):
        end = groups[gi + 1][0] if gi + 1 < len(groups) else len(doc) - 1
        books = GROUP_BOOKS[gi]
        bi, book = 0, books[0]
        chapter, verse = 0, 0
        title = []  # psalm superscription waiting for its psalm's first verse
        for pn in range(last + 1, end):
            for line in page_lines(doc[pn]):
                spans = line["spans"]
                joined = "".join(s["text"] for s in spans).strip()
                if joined == LEGEND:
                    continue
                for s in spans:
                    text, color, size = s["text"], s["color"], s["size"]
                    if not text or color in SKIP_COLORS or size < 1.5 or s["font"] == "Tahoma":
                        continue
                    if color == VERSE_COLOR and size < 7 and text.strip().isdigit():
                        n = int(text.strip())
                        if n == 1 and verse != 0 or (n == 1 and chapter == 0):
                            chapter += 1
                            if book in CHAPTERS and chapter > CHAPTERS[book]:
                                bi += 1
                                book, chapter = books[bi], 1
                        if title:
                            verses[(book, chapter, 0)] = title
                            title = []
                        verse = n
                        continue
                    if color == VERSE_COLOR and size >= 7:
                        if size >= 11:
                            continue  # chapter drop numbers, chart labels
                        tag = "STRUCTURE"  # gray connectors / psalm titles
                    elif size >= 11:
                        continue  # headings
                    elif color in CATEGORIES:
                        tag = CATEGORIES[color]
                    elif color in TEXT_COLORS:
                        tag = TEXT_COLORS[color]
                    else:
                        unknown[(f"#{color:06x}", round(size, 1), text.strip()[:30])] += 1
                        continue
                    if book == "Psalms" and (title or tag == "STRUCTURE" and size < 8.5):
                        title.append([text, tag, voice(s["font"])])
                        continue
                    if chapter == 0:
                        continue  # text before the first verse marker
                    key = (book, chapter, verse)
                    verses.setdefault(key, []).append([text, tag, voice(s["font"])])
                # line break -> space
                seg = title or verses.get((book, chapter, verse))
                if seg:
                    if seg and not seg[-1][0].endswith((" ", "‑", "-")):
                        seg[-1][0] += " "

    # Merge adjacent segments with the same tag & voice
    for key, segs in verses.items():
        merged = []
        for t, tag, v in segs:
            if merged and merged[-1][1] == tag and merged[-1][2] == v:
                merged[-1][0] += t
            else:
                merged.append([t, tag, v])
        for m in merged:
            m[0] = re.sub(r"\s+", " ", m[0])
        verses[key] = merged

    # Phrases the PDF colors as one unit ("Holy Ghost", "Son of man") get split
    # when they wrap across a line. Re-join them across whitespace-only gaps.
    phrases = collections.Counter()
    for segs in verses.values():
        for t, tag, _ in segs:
            if tag in CATEGORIES.values() and " " in t.strip():
                phrases[(tag, t.strip().lower())] += 1
    prefixes = {(tag, p[:i]) for (tag, p) in phrases for i in range(1, len(p) + 1)}
    for key, segs in verses.items():
        i = 0
        while i + 2 < len(segs):
            a, gap, b = segs[i], segs[i + 1], segs[i + 2]
            joined = (a[0].strip() + " " + b[0].strip()).lower()
            if a[1] in CATEGORIES.values() and a[1] == b[1] and not gap[0].strip() \
                    and (a[1], joined) in prefixes:
                a[0] = a[0].rstrip() + " " + b[0].lstrip()
                del segs[i + 1:i + 3]
            else:
                i += 1

    orig = apply_corrections(verses)

    # Mark colored words that sit inside red-letter text, then write outputs
    red = {"RED", "RED_SUPPLIED"}
    short = {v: k for k, v in SHORT.items()}
    with open(f"{OUT}/tagged_verses.jsonl", "w") as fv, \
            open(f"{OUT}/tagged_bible.txt", "w") as ft, \
            open(f"{OUT}/tagged_words.csv", "w", newline="") as fw:
        w = csv.writer(fw)
        w.writerow(["ref", "book", "chapter", "verse", "term", "category",
                    "voice", "in_words_of_christ", "source_category"])
        ft.write(TEXT_HEADER)
        for (book, ch, vs), merged in verses.items():
            ref = f"{book} {ch}:{vs}"
            plain = re.sub(r"\s+", " ", "".join(t for t, _, _ in merged)).strip()
            out, inline, red_open = [], [], False
            for i, (t, tag, v) in enumerate(merged):
                prev_red = any(m[1] in red for m in merged[max(0, i - 2):i])
                next_red = any(m[1] in red for m in merged[i + 1:i + 3])
                in_red = tag in red or (prev_red and next_red) or \
                    (tag in CATEGORIES.values() and (prev_red or next_red) and v != "narration")
                o = orig.get(((book, ch, vs), i))
                out.append({"t": t, "c": tag, "v": v, **({"r": 1} if in_red else {}),
                            **({"orig": o} if o else {})})
                if t.strip() and in_red != red_open:
                    inline.append("\u00ab" if in_red else "\u00bb")
                    red_open = in_red
                if tag in CATEGORIES.values():
                    term = t.strip(" ,.;:?!()\u2019'")
                    if term:
                        w.writerow([ref, book, ch, vs, term, tag, v, int(in_red), o or tag])
                        lead = t[:len(t) - len(t.lstrip())]
                        core = t.strip()
                        k = core.find(term)
                        inline.append(f"{lead}{core[:k]}[{term}|{short[tag]}]{core[k + len(term):]}"
                                      + (" " if t.endswith(" ") else ""))
                        continue
                inline.append(t)
            if red_open:
                inline.append("\u00bb")
            ft.write(f"{ref}\t" + re.sub(r"\s+", " ", "".join(inline)).strip() + "\n")
            fv.write(json.dumps({"ref": ref, "book": book, "chapter": ch,
                                 "verse": vs, "text": plain, "segments": out},
                                ensure_ascii=False) + "\n")

    with open(f"{OUT}/unknown_colors.txt", "w") as f:
        for k, n in unknown.most_common():
            f.write(f"{n}\t{k}\n")
    print("verses:", len(verses), "unknown spans:", sum(unknown.values()), file=sys.stderr)


if __name__ == "__main__":
    main()

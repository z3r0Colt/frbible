"""Build human/AI-readable reports from data/tagged_verses.jsonl.

Run after extract_colors.py. Writes:
  reports/categories/NN_CATEGORY.md     every term in that color, with every verse
  reports/verses_by_color/CATEGORY.txt  every verse that contains that color
  reports/ambiguous_terms.md            words that take more than one color
  reports/coverage.md                   how often a word is colored vs left black
  data/lexicon.json                     term -> category counts + uncolored count
"""
import collections
import json
import os
import re

CATS = [
    ("GOD_FATHER", "#7a36bf", "God the Father", "Father, God, LORD, Almighty, Jehovah, Redeemer"),
    ("GOD_SON", "#6a2ea6", "God the Son", "Son, Jesus, Christ, Saviour, Lamb, Lion, Emmanuel"),
    ("GOD_SPIRIT", "#5a278c", "God the Spirit", "Spirit, Holy Ghost, Comforter, Holy Spirit"),
    ("ANGELIC", "#a19638", "Angelic Beings", "Angel, cherubims, beasts, Gabriel, archangel, host"),
    ("DEMONIC", "#736b28", "Demonic Beings", "Devil, gods, idols, Satan, Moloch, dragon, demons"),
    ("PROPER_PERSON", "#218fd9", "Proper People", "Paul, John, Apollos, Timothy, Mary, Marcus, Luke"),
    ("PEOPLE_GROUP", "#1f87cc", "People Groups", "Jew, Canaanites, Hittites, Jebusites, Gentile, Roman"),
    ("GENERAL_PEOPLE", "#1b76b2", "General People", "king, man, wife, children, servant, teacher, apostles"),
    ("PRONOUN", "#244a7f", "Personal Pronouns", "I, we, thou, you, he, they, him, she, mine, their, whom"),
    ("ANIMAL", "#469594", "Animals", "creature, fowl, beast, cattle, serpent"),
    ("PLANT", "#007b78", "Plants", "tree, herb, olive"),
    ("PROPER_PLACE", "#2fa648", "Proper Places", "Jerusalem, Israel, Egypt, Euphrates, Mount Sinai"),
    ("GENERAL_PLACE_1", "#247f38", "General Places 1 (things/locations)", "temple, garden, field, city, mountain, river, houses"),
    ("GENERAL_PLACE_2", "#195928", "General Places 2 (position words)", "where, there, side, nigh, lower, within, up, over, therein"),
    ("SPECIFIC_TIME", "#995226", "Specific Times", "hour, day, month, year, night, evening, harvest, winter"),
    ("GENERAL_TIME", "#733e1d", "General Times", "soon, later, before, when, while, sometimes, again"),
    ("NUMBER", "#9c0f2e", "Number Words", "7, 32, 564, 6,891, first, second, sevenfold, two, five"),
    ("MEASUREMENT", "#7f0b25", "Measurements", "cubit, measure, ephah, hin, homer, weight, shekel, log"),
    ("QUANTITY", "#66091d", "General Quantity", "much, both, all, little, another, many, least, none"),
]
CODES = [c[0] for c in CATS]
ABBR = {
    "Genesis": "Gen", "Exodus": "Exod", "Leviticus": "Lev", "Numbers": "Num",
    "Deuteronomy": "Deut", "Joshua": "Josh", "Judges": "Judg", "Ruth": "Ruth",
    "1 Samuel": "1Sam", "2 Samuel": "2Sam", "1 Kings": "1Kgs", "2 Kings": "2Kgs",
    "1 Chronicles": "1Chr", "2 Chronicles": "2Chr", "Ezra": "Ezra", "Nehemiah": "Neh",
    "Esther": "Esth", "Job": "Job", "Psalms": "Ps", "Proverbs": "Prov",
    "Ecclesiastes": "Eccl", "Song of Solomon": "Song", "Isaiah": "Isa",
    "Jeremiah": "Jer", "Lamentations": "Lam", "Ezekiel": "Ezek", "Daniel": "Dan",
    "Hosea": "Hos", "Joel": "Joel", "Amos": "Amos", "Obadiah": "Obad",
    "Jonah": "Jonah", "Micah": "Mic", "Nahum": "Nah", "Habakkuk": "Hab",
    "Zephaniah": "Zeph", "Haggai": "Hag", "Zechariah": "Zech", "Malachi": "Mal",
    "Matthew": "Matt", "Mark": "Mark", "Luke": "Luke", "John": "John", "Acts": "Acts",
    "Romans": "Rom", "1 Corinthians": "1Cor", "2 Corinthians": "2Cor",
    "Galatians": "Gal", "Ephesians": "Eph", "Philippians": "Phil",
    "Colossians": "Col", "1 Thessalonians": "1Thess", "2 Thessalonians": "2Thess",
    "1 Timothy": "1Tim", "2 Timothy": "2Tim", "Titus": "Titus", "Philemon": "Phlm",
    "Hebrews": "Heb", "James": "Jas", "1 Peter": "1Pet", "2 Peter": "2Pet",
    "1 John": "1John", "2 John": "2John", "3 John": "3John", "Jude": "Jude",
    "Revelation": "Rev",
}
BOOK_ORDER = list(ABBR)


def norm(term):
    term = term.replace("‑", "-").replace("’", "'")
    return term.strip(" ,.;:?!()[]'\"").strip()


def compress(refs):
    """[(book, ch, vs), ...] -> 'Gen 1:1, 3; 2:4 | Exod 3:2' (sorted, unique)."""
    refs = sorted(set(refs), key=lambda r: (BOOK_ORDER.index(r[0]), r[1], r[2]))
    out, cur_book, cur_ch, parts = [], None, None, []
    for b, c, v in refs:
        if b != cur_book:
            if parts:
                out.append(" ".join(parts))
            parts, cur_book, cur_ch = [f"{ABBR[b]} {c}:{v}"], b, c
        elif c != cur_ch:
            parts[-1] += ";"
            parts.append(f"{c}:{v}")
            cur_ch = c
        else:
            parts[-1] += ","
            parts.append(str(v))
    if parts:
        out.append(" ".join(parts))
    return " | ".join(out)


def main():
    verses = [json.loads(l) for l in open("data/tagged_verses.jsonl")]
    os.makedirs("reports/categories", exist_ok=True)
    os.makedirs("reports/verses_by_color", exist_ok=True)

    term_refs = collections.defaultdict(lambda: collections.defaultdict(list))  # cat->term->refs
    term_cats = collections.defaultdict(collections.Counter)  # lower term -> cat counts
    term_cat_refs = collections.defaultdict(lambda: collections.defaultdict(list))
    cat_verses = collections.defaultdict(set)
    uncolored = collections.Counter()
    in_red = collections.Counter()
    voice_by_cat = collections.defaultdict(collections.Counter)

    for v in verses:
        ref = (v["book"], v["chapter"], v["verse"])
        for s in v["segments"]:
            if s["c"] in CODES:
                t = norm(s["t"])
                if not t:
                    continue
                term_refs[s["c"]][t].append(ref)
                term_cats[t.lower()][s["c"]] += 1
                term_cat_refs[t.lower()][s["c"]].append(ref)
                cat_verses[s["c"]].add(ref)
                voice_by_cat[s["c"]][s["v"]] += 1
                if s.get("r"):
                    in_red[s["c"]] += 1
            else:
                for w in re.findall(r"[A-Za-z’'\-‑]+", s["t"]):
                    uncolored[norm(w).lower()] += 1

    total_verses = len(verses)
    # ---- per category term reports
    for i, (code, hexc, name, examples) in enumerate(CATS, 1):
        terms = term_refs[code]
        n_occ = sum(len(r) for r in terms.values())
        lines = [
            f"# {name}  `{code}`  ({hexc})",
            "",
            f"- Legend examples (from the PDF's Color Code page): {examples}",
            f"- Occurrences: **{n_occ:,}** across **{len(cat_verses[code]):,}** verses "
            f"({len(cat_verses[code]) / total_verses:.1%} of all verses)",
            f"- Distinct terms: **{len(terms):,}**",
            f"- Occurrences inside words of Christ (red letter): {in_red[code]:,}",
            "- Voice layer of occurrences: " + ", ".join(
                f"{k} {n:,}" for k, n in voice_by_cat[code].most_common()),
            "",
            "Each term is listed with how many times it carries this color, what share of all",
            "its colored uses this is, how often the same word is left uncolored, and every verse.",
            "",
            "## Term summary",
            "",
            "| Term | Count | Share of term's colored uses | Times uncolored | Other colors this term takes |",
            "|---|---:|---:|---:|---|",
        ]
        ordered = sorted(terms.items(), key=lambda kv: (-len(kv[1]), kv[0].lower()))
        for t, refs in ordered:
            cc = term_cats[t.lower()]
            share = cc[code] / sum(cc.values())
            others = ", ".join(f"{k} {n}" for k, n in cc.most_common() if k != code)
            unc = uncolored.get(t.lower(), 0) if " " not in t else "-"
            lines.append(f"| {t} | {len(refs)} | {share:.0%} | {unc} | {others} |")
        lines += ["", "## Every verse, by term", ""]
        for t, refs in ordered:
            lines.append(f"### {t} ({len(refs)})")
            lines.append(compress(refs))
            lines.append("")
        with open(f"reports/categories/{i:02d}_{code}.md", "w") as f:
            f.write("\n".join(lines))

        with open(f"reports/verses_by_color/{code}.txt", "w") as f:
            f.write(f"# Every verse containing {name} ({hexc}) - {len(cat_verses[code]):,} verses\n")
            f.write("# Format: Book chapter:verse, verse; chapter:verse ...  (verse 0 = psalm title)\n\n")
            by_book = collections.defaultdict(list)
            for r in cat_verses[code]:
                by_book[r[0]].append(r)
            for b in BOOK_ORDER:
                if by_book[b]:
                    f.write(compress(by_book[b]) + "\n")

    # ---- ambiguous terms
    amb = [(t, c) for t, c in term_cats.items() if len(c) > 1]
    amb.sort(key=lambda x: -sum(x[1].values()))
    lines = [
        "# Words that take more than one color",
        "",
        "These are the decision points. The same spelling gets different colors depending",
        "on what it refers to in context. For each word, every color it takes is shown with",
        "a count and up to 12 example verses. Low-count minority colors are sometimes",
        "deliberate (see COLOR_GUIDE.md) and sometimes inconsistencies in the source.",
        "",
    ]
    for t, c in amb:
        total = sum(c.values())
        if total < 3:
            continue
        lines.append(f"## {t}  ({total} colored uses, {uncolored.get(t, 0)} uncolored)")
        for code, n in c.most_common():
            refs = term_cat_refs[t][code]
            ex = compress(refs[:12])
            lines.append(f"- **{code}** {n} ({n / total:.0%}) : {ex}")
        lines.append("")
    with open("reports/ambiguous_terms.md", "w") as f:
        f.write("\n".join(lines))

    # ---- coverage: how consistently a word is colored
    lines = [
        "# Coverage: how often a word is colored vs left black",
        "",
        "Single words only, ranked by total occurrences. `Colored %` near 100 means the",
        "word is always colored. Lower values mean the coloring depends on sense (for",
        "example 'house' as a building vs 'house' as a family, or 'so' as 'then' vs 'so'",
        "meaning 'in this way'). Words never colored are not listed.",
        "",
        "| Word | Colored | Uncolored | Colored % | Colors |",
        "|---|---:|---:|---:|---|",
    ]
    rows = []
    for t, c in term_cats.items():
        if " " in t:
            continue
        col = sum(c.values())
        unc = uncolored.get(t, 0)
        rows.append((col + unc, t, col, unc, c))
    for tot, t, col, unc, c in sorted(rows, reverse=True):
        if tot < 5:
            continue
        lines.append(f"| {t} | {col} | {unc} | {col / tot:.0%} | " +
                     ", ".join(f"{k} {n}" for k, n in c.most_common()) + " |")
    with open("reports/coverage.md", "w") as f:
        f.write("\n".join(lines))

    lex = {t: {"colors": dict(c), "uncolored": uncolored.get(t, 0)}
           for t, c in sorted(term_cats.items())}
    with open("data/lexicon.json", "w") as f:
        json.dump(lex, f, ensure_ascii=False, indent=0)

    print("\n".join(f"{code:16} terms={len(term_refs[code]):5} occ={sum(len(r) for r in term_refs[code].values()):6} "
                    f"verses={len(cat_verses[code]):5}" for code in CODES))


if __name__ == "__main__":
    main()

# frbible

Analysis of the color coding in the *Fresh Look Bible* (KJV, color text PDF in this repo).

* **[COLOR_GUIDE.md](COLOR_GUIDE.md)** explains the 19 colors, what each one means, the
  rules for hard cases, and a prompt for applying the system to another Bible.
* `data/` holds the whole Bible with every colored word tagged (text, JSON and CSV).
* `reports/` lists every term and every verse for each color.
* `tools/` has the scripts that pulled all of this out of the PDF.

```
pip install pymupdf
python3 tools/extract_colors.py
python3 tools/build_reports.py
```

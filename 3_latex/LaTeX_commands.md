# Make & LaTeX quick reference (streamlined)

This file provides the minimal, practical commands you need for daily work in `3_latex/` with a focus on the `make md2pdf` flow. Keep this as a short cheat-sheet: first the `make` usage you will run most often, then the essential parser and compile script options.

## Key goal
- Common daily workflow: turn a single markdown or a set of markdowns into finished PDFs with predictable flags. Use `DRY_RUN` while testing and `YES=1` when you want to overwrite.

## 1 — Primary: `make md2pdf` (recommended daily target)
Location: `3_latex/Makefile` — this target runs the parser on markdown(s) and compiles generated `.tex` files to `output/*.pdf`.

Primary variables (use with `make md2pdf VAR=…`):
- USER — user profile id (passed to the parser as `--user`). Required for non-interactive runs.
- TEMPLATE — `modern` or `classic` (passed to parser as `--template`).
- YES — set to `1` to pass `--yes` to parser (auto-accept and overwrite existing `.tex`).
- DRY_RUN — set to `1` to pass `--dry-run` to parser (skip writing files and skip compilation).
- ENGINE — override TeX engine used by compile step (e.g. `ENGINE=pdflatex`). Default: `xelatex`.
- FONT — optional: family name (e.g. `FONT="Lato"`) forwarded to parser; used to insert a `\setmainfont{...}` in the template.

Quick examples (copy-paste):
- Interactive (prompts for missing args):
    - make md2pdf
- Non-interactive, produce PDFs, overwrite existing `.tex`:
    - make md2pdf USER=alex TEMPLATE=modern YES=1
- Dry-run (inspect generated `.tex` only):
    - make md2pdf USER=alex TEMPLATE=modern DRY_RUN=1
- Non-default TeX engine (single invocation):
    - ENGINE=pdflatex make md2pdf USER=alex TEMPLATE=modern YES=1
- Use specific system font family for the build:
    - make md2pdf USER=alex TEMPLATE=modern YES=1 FONT="Lato"

Notes:
- `md2pdf` iterates `src/content/*.md` by design; use the single-file convenience target (below) for per-file runs.
- If any parser invocation fails, the target aborts — this prevents partial outputs.

## 2 — Single-file convenience (recommended for iterative editing)
Add or use the `md2pdf-single` helper target to parse and compile one markdown file. Example:

- make md2pdf-single MD=src/content/Job_Listing_ENG.md USER=alex TEMPLATE=modern YES=1 FONT="Lato"

If this target is not present in your Makefile yet, it's a small addition that runs the parser for the one `MD` and then compiles the resulting `src/applications/<basename>.tex`.

## 3 — Essential parser: `parse_md_to_tex.py` (minimal flags)
Location: `3_latex/parse_md_to_tex.py`

Use this script to transform labeled markdown into `.tex` using templates. For daily use, these are the most useful flags:
- Positional `[FILE]` — optional single markdown file to process; omit for batch mode.
- --user, -u USER_ID — required for non-interactive runs.
- --template {modern,classic} — pick the template.
- --yes, -y — accept suggested filenames and overwrite.
- --dry-run — show what would be written (use this when trying new markdown).
- --date "..." — override automatic date formatting when needed.
- --font "FamilyName" — force a font family insertion into the template (e.g. "Lato").

Language-aware date:
- The parser detects `language:` in front-matter or `_DE` / `_ENG` filename suffixes and formats the date (German month names for `_DE`). Use `--date` to force a specific date string.

Examples (single-file flow):
- Dry-run parse only:
    - ./parse_md_to_tex.py src/content/Job_Listing_ENG.md --user alex --template modern --dry-run
- Parse and write .tex (no compile):
    - ./parse_md_to_tex.py src/content/Job_Listing_ENG.md --user alex --template modern --yes
- Parse with custom font and date override:
    - ./parse_md_to_tex.py src/content/Job_Listing_DE.md --user alex --template modern --yes --font "Lato" --date "23. Oktober 2025"

## 4 — Compile helper: `compile.sh` (preflight + engine)
Location: `3_latex/compile.sh`

`compile.sh` runs a preflight (unescaped `&`, leftover `{{...}}`) and then calls the requested TeX engine. Typical usage (from Makefile):
- ./compile.sh src/applications/job.tex xelatex

Useful flags:
- --skip-preflight — skip checks (CI-only; use with caution).

If preflight finds issues it exits non-zero (abort); correct the generated `.tex` (or fix markdown) before rerunning.

## 5 — Safe one-liners (common combos)
- Parse a single md and compile the generated tex:
    - ./parse_md_to_tex.py src/content/Job_Listing_ENG.md --user alex --template modern --yes && make compile FILE=src/applications/Job_Listing_ENG.tex
- Batch parse all content and compile everything (CI-friendly):
    - ./parse_md_to_tex.py --user alex --template modern --yes && make
- Dry-run then real run (inspect first):
    - make md2pdf USER=alex TEMPLATE=modern DRY_RUN=1 && make md2pdf USER=alex TEMPLATE=modern YES=1

## 6 — Practical tips & troubleshooting
- Use `DRY_RUN=1` frequently when you change templates or front-matter.
- If a single markdown causes `md2pdf` to abort, debug it with the parser in dry-run on that file.
- Use `FONT="FamilyName"` values that appear in `3_latex/installed_fonts.txt` (family names, one-per-line). Recommended families for professional letters are listed at the top of that file (e.g. Lato, Source Sans 3, Helvetica Neue, Times New Roman).
- For CI reproducibility, consider bundling a font family into `3_latex/figures/fonts/` and extend the parser to accept `--font-path` (ask me and I can add this).

## 7 Examples

run in /3_latex
```
make md2pdf USER=alex TEMPLATE=modern FONT=Lato
make cv USER=alex


```

#!/usr/bin/env python3
"""
Parse markdown with HTML comments and \\lettercontent{} blocks
Create .tex file from template
"""

import re
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional
import json
import json

yaml_mod = None
try:
    import yaml as yaml_mod

    YAML_AVAILABLE = True
except Exception:
    YAML_AVAILABLE = False


def parse_markdown(md_file):
    """Extract sections from markdown file"""
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()

    sections = {}

    # Pattern to match: <!-- LABEL --> \lettercontent{...}
    # This regex handles multi-line content inside \lettercontent{}
    pattern = r"<!--\s*(\w+)\s*-->\s*\\lettercontent\{([^}]*(?:\{[^}]*\}[^}]*)*)\}"

    matches = re.finditer(pattern, content, re.DOTALL)

    for match in matches:
        label = match.group(1)
        text = match.group(2).strip()
        sections[label] = text

    return sections


def create_tex_file(template_path, sections, output_path, user=None, md_basename=None, language=None):
    """Create .tex file from template and parsed sections"""
    with open(template_path, "r", encoding="utf-8") as f:
        tex_content = f.read()

    # Determine closing salutation based on language
    if language == "de":
        closing_salutation = "Mit freundlichen Grüßen"
    else:
        closing_salutation = "Kind regards"

    # Modern template mapping - placeholders match markdown labels exactly
    if "modern" in template_path:
        replacements = {
            "Dear {{RECIPIENT_NAME}},": latex_escape(
                sections.get("SALUTATION", "Dear Hiring Manager,")
            ),
            "{{PARAGRAPH_1_INTRODUCTION}}": latex_escape(
                sections.get("PARAGRAPH_1_INTRODUCTION", "")
            ),
            "{{PARAGRAPH_2_TECHNICAL_EXCELLENCE}}": latex_escape(
                sections.get("PARAGRAPH_2_TECHNICAL_EXCELLENCE", "")
            ),
            "{{PARAGRAPH_3_EXPERIENCE_AND_VALUE}}": latex_escape(
                sections.get("PARAGRAPH_3_EXPERIENCE_AND_VALUE", "")
            ),
            "{{PARAGRAPH_4_STRATEGIC_FIT}}": latex_escape(
                sections.get("PARAGRAPH_4_STRATEGIC_FIT", "")
            ),
            "{{PARAGRAPH_5_CLOSING_STATEMENT}}": latex_escape(
                sections.get("PARAGRAPH_5_CLOSING_STATEMENT", "")
            ),
        }
    else:
        # Fallback mapping for templates that follow the classic/simple structure
        replacements = {
            "Dear {{RECIPIENT_NAME}},": latex_escape(
                sections.get("SALUTATION", "Dear Hiring Manager,")
            ),
            "{{PARAGRAPH_1_INTRODUCTION}}": latex_escape(
                sections.get("PARAGRAPH_1_INTRODUCTION", "")
            ),
            "{{PARAGRAPH_2_TECHNICAL_EXCELLENCE}}": latex_escape(
                sections.get("PARAGRAPH_2_TECHNICAL_EXCELLENCE", "")
            ),
            "{{PARAGRAPH_3_EXPERIENCE_AND_VALUE}}": latex_escape(
                sections.get("PARAGRAPH_3_EXPERIENCE_AND_VALUE", "")
            ),
            "{{PARAGRAPH_4_STRATEGIC_FIT}}": latex_escape(
                sections.get("PARAGRAPH_4_STRATEGIC_FIT", "")
            ),
            "{{PARAGRAPH_5_CLOSING_STATEMENT}}": latex_escape(
                sections.get("PARAGRAPH_5_CLOSING_STATEMENT", "")
            ),
        }

    # Apply replacements
    for placeholder, value in replacements.items():
        tex_content = tex_content.replace(placeholder, value)

    # If user data provided, replace common placeholders
    user_context = {}
    if user:
        phone_raw = user.get("phone", "")
        phone_tel = user.get("phone_tel")
        if not phone_tel and phone_raw:
            phone_tel = re.sub(r"[^\d+]", "", phone_raw)
        linkedin_label = user.get("linkedin_label") or user.get("linkedin", "")
        linkedin_url = (
            user.get("linkedin_url")
            or user.get("linkedin_url_override")
            or user.get("linkedin", "")
        )
        if linkedin_url and not re.match(r"^(?:https?|mailto):", linkedin_url):
            linkedin_url = "https://www.linkedin.com/in/" + linkedin_url.lstrip(
                "@/"
            ).rstrip("/")
        user_context = {
            "YOUR_FULL_NAME": latex_escape(user.get("full_name", "")),
            "YOUR_EMAIL": latex_escape(user.get("email", "")),
            "YOUR_PHONE": latex_escape(user.get("phone", "")),
            "YOUR_JOB_TITLE": latex_escape(user.get("job_title", "")),
            "DATE": latex_escape(user.get("date", "")),
            "YOUR_ADDRESS": latex_escape(user.get("address", "")),
            "YOUR_CITY": latex_escape(user.get("city", "")),
            "YOUR_ZIP": latex_escape(user.get("zip", "")),
            "YOUR_PHONE_TEL": latex_escape(phone_tel or ""),
            "YOUR_LINKEDIN": latex_escape(linkedin_label),
            "YOUR_LINKEDIN_URL": latex_escape(linkedin_url),
            "CLOSING_SALUTATION": latex_escape(closing_salutation),
        }
        # MAIN_FONT_SETUP: insert a TeX font setup block. If the user context
        # includes a 'preferred_font' (injected from the --font CLI flag),
        # create a direct \setmainfont call. Otherwise, provide the original
        # fallback logic block so templates behave as before.
        preferred = user.get("preferred_font") if isinstance(user, dict) else None
        if preferred:
            # User explicitly requested a font. Per user's preference we no
            # longer perform host-side detection; always emit an unconditional
            # \setmainfont call. The user indicated they will provide only
            # installed fonts on their macOS machine.
            main_font_setup = f"\\setmainfont{{{preferred}}}[Scale=1.00]"
        else:
            # Default selection logic (kept as a TeX block). This mirrors the
            # previous template behavior and is inserted as raw TeX.
            main_font_setup = (
                "\\IfFontExistsTF{Lato}{%\n"
                "  \\setmainfont{Lato}[Scale=1.00]\n"
                "}{%\n"
                "  \\IfFontExistsTF{Source Sans 3}{%\n"
                "    \\setmainfont{Source Sans 3}[Scale=1.00]\n"
                "  }{%\n"
                "    \\IfFontExistsTF{TeX Gyre Heros}{\\setmainfont{TeX Gyre Heros}[Scale=1.00]}{\\renewcommand{\\familydefault}{\\sfdefault}}\n"
                "  }\n"
                "}\n"
            )
        # Inject the raw TeX for the font setup into the user_context so the
        # parser can replace the {{MAIN_FONT_SETUP}} token with it.
        user_context["MAIN_FONT_SETUP"] = main_font_setup
        user_map = {f"{{{{{k}}}}}": v for k, v in user_context.items()}
        # Replace user-context tokens, but avoid replacing tokens that appear
        # inside LaTeX comment lines (lines that start with optional
        # whitespace followed by '%'). Replacing inside comments can produce
        # broken TeX (e.g. a comment that mentions {{MAIN_FONT_SETUP}} would
        # get replaced and leave an unmatched brace sequence). We therefore
        # scan the file line-by-line and only substitute tokens on non-comment
        # lines.
        if user_map:
            lines = tex_content.splitlines(True)
            for idx, line in enumerate(lines):
                # If the line is a pure LaTeX comment, skip replacements on it
                if re.match(r"^\s*%", line):
                    continue
                new_line = line
                for ph, val in user_map.items():
                    if ph in new_line:
                        new_line = new_line.replace(ph, val)
                lines[idx] = new_line
            tex_content = "".join(lines)

        # If the user profile supplies an explicit profile picture path, prefer
        # that image for any template references to common profile-picture
        # filenames. This avoids requiring template edits and lets the
        # selected user's picture appear in the generated .tex automatically.
        profile_pic = user.get("profile_pic") if isinstance(user, dict) else None
        if profile_pic:
            # Normalize to the form templates expect (parser already rewrites
            # ../figures/ -> figures/ later but handle common variants here).
            profile_pic = profile_pic.replace("../figures/", "figures/")
            # List of common filenames templates may reference; replace them
            # with the profile_pic provided by the user profile.
            common_names = [
                "figures/profile-pic.png",
                "figures/profile-pic.jpg",
                "figures/profile-pic.jpeg",
                "figures/profile_placeholder.png",
                "figures/profile_placeholder.jpg",
            ]
            for cn in common_names:
                tex_content = tex_content.replace(cn, profile_pic)
        # If user provides an explicit signature image, replace common
        # signature filenames in templates so the signature image is used.
        signature_img = user.get("signature_image") if isinstance(user, dict) else None
        if signature_img:
            signature_img = signature_img.replace("../figures/", "figures/")
            common_sig_names = [
                "figures/signature.png",
                "figures/signature.jpg",
                "figures/signature.jpeg",
                "figures/sign.png",
                "figures/sign.jpg",
            ]
            for cs in common_sig_names:
                tex_content = tex_content.replace(cs, signature_img)

    # Fill recipient/company placeholders from sections if available
    # Derive recipient name from SALUTATION if needed (strip 'Dear' and comma)
    sal = sections.get("SALUTATION", "")
    recipient = sections.get("RECIPIENT_NAME", "")
    if not recipient and sal:
        # Expect formats like 'Dear Name,' or 'Sehr geehrte Frau Name,'
        m = re.search(r"Dear\s+([^,]+),", sal)
        if not m:
            m = re.search(r"Sehr geehrte[rn]?\s+([^,]+),", sal)
        if m:
            recipient = m.group(1).strip()

    company = sections.get("COMPANY_NAME", "")

    # If COMPANY_NAME or RECIPIENT_NAME are empty, try to derive them
    # from the markdown filename (useful when the md is named like
    # YYYY-MM-DD_CompanyName_Job_Title.md). We will create two values:
    #   - derived_company: a compact company token
    #   - derived_job: the job title (underscores -> spaces)
    # Prefer an explicitly passed markdown basename (without extension).
    fname = md_basename or ""

    derived_company = ""
    derived_job = ""
    if fname:
        # remove leading date patterns like 2025-10-22_ or 2025_10_22-
        fname2 = re.sub(r"^[0-9]{4}[-_][0-9]{2}[-_][0-9]{2}[_-]?", "", fname)
        # split tokens on underscores
        tokens = [t for t in fname2.split("_") if t]
        if len(tokens) >= 2:
            # use the LAST token as company name, rest as job title
            derived_company = tokens[-1]
            derived_job = " ".join(tokens[:-1])
        else:
            # fallback: treat whole name as job title and company empty
            derived_job = re.sub(r"[^A-Za-z0-9]", " ", fname2).strip()
            derived_company = ""
        # cleanup: replace multiple spaces and trim
        derived_job = re.sub(r"\s+", " ", derived_job).strip()
        derived_company = re.sub(r"\s+", " ", derived_company).strip()

    # If sections don't provide COMPANY_NAME or RECIPIENT_NAME, inject derived
    # If the markdown didn't supply COMPANY_NAME but we derived values from
    # the filename, prefer writing a single combined recipient string
    # "Company - Job Title" and do NOT also populate COMPANY_NAME to avoid
    # duplicate lines in the generated letter.
    if derived_company and derived_job:
        recipient = f"{derived_company} - {derived_job}"
        # only keep COMPANY_NAME if it was explicitly provided in the md
        if not sections.get("COMPANY_NAME"):
            company = ""
    else:
        # fallback: if we have a derived_company but no derived_job, use it
        if not company and derived_company:
            company = derived_company

    # Build final values for JOB_TITLE and COMPANY_NAME placeholders.
    # Priority: explicit markdown sections -> derived filename values.
    job_title_val = ""
    company_val = ""
    if sections.get("JOB_TITLE"):
        job_title_val = latex_escape(sections.get("JOB_TITLE", ""))
    elif sections.get("POSITION_TITLE"):
        job_title_val = latex_escape(sections.get("POSITION_TITLE", ""))
    elif derived_job:
        job_title_val = latex_escape(derived_job)

    if sections.get("COMPANY_NAME"):
        company_val = latex_escape(sections.get("COMPANY_NAME", ""))
    elif derived_company:
        company_val = latex_escape(derived_company)

    explicit_company_provided = bool(sections.get("COMPANY_NAME"))

    # If recipient still empty, derive from company_val and job_title_val
    if not recipient and company_val and job_title_val:
        recipient = f"{company_val} - {job_title_val}"

    # Replace both triple-brace (keep braces for macro args) and double-brace variants
    for ph in ["RECIPIENT_NAME", "COMPANY_NAME"]:
        raw = ""
        if ph == "RECIPIENT_NAME":
            raw = latex_escape(recipient)
        else:
            raw = latex_escape(company)
        # triple-brace usually used inside a macro argument like \companyname{{{RECIPIENT_NAME}}}
        # replace with a braced value so macros get a proper argument: {Name}
        tex_content = tex_content.replace("{{{" + ph + "}}}", "{" + raw + "}")
        # double-brace may appear inline; replace with raw text
        tex_content = tex_content.replace("{{" + ph + "}}", raw)

    # Generic replacement: replace any remaining {{TOKEN}} or {{{TOKEN}}} from
    # the sections parsed from markdown or from the user profile when available.
    # This covers template variants that use slightly different placeholder names
    # (for example the Classic template) and prevents preflight failures.
    def try_replace_token(token_name):
        # priority: sections -> user profile fields
        if token_name in sections:
            return latex_escape(sections.get(token_name, ""))
        # map user fields without braces and uppercased keys
        if user_context and token_name in user_context:
            return user_context[token_name]
        return None

    # Replace triple- and double-brace tokens, but only on non-comment lines.
    # This prevents replacing tokens that appear in explanatory comment
    # lines (for example the template contains a commented mention of
    # {{MAIN_FONT_SETUP}}). Replacing inside comments can break TeX
    # when the replacement contains braces or percent signs.
    lines = tex_content.splitlines(True)
    for idx, line in enumerate(lines):
        # Skip pure comment lines
        if re.match(r"^\s*%", line):
            continue

        # triple-brace replacement (keeps braces around the value)
        def repl_triple(m):
            tn = m.group(1).strip()
            val = try_replace_token(tn)
            return ("{" + val + "}") if val is not None else m.group(0)

        line = re.sub(r"\{\{\{([^}]+)\}\}\}", repl_triple, line)

        # double-brace replacement
        def repl_double(m):
            tn = m.group(1).strip()
            val = try_replace_token(tn)
            return val if val is not None else m.group(0)

        line = re.sub(r"\{\{([^}]+)\}\}", repl_double, line)
        lines[idx] = line
    tex_content = "".join(lines)

    # If common company/address tokens remain and we don't have values for them,
    # blank them out to avoid leaving {{...}} placeholders that trip preflight.
    optional_company_tokens = [
        "COMPANY_ADDRESS",
        "COMPANY_CITY",
        "COMPANY_ZIP",
        "COMPANY_NAME",
    ]
    for tok in optional_company_tokens:
        tex_content = tex_content.replace("{{" + tok + "}}", "")
        tex_content = tex_content.replace("{{{" + tok + "}}}", "")

    # Remove some optional placeholders that may contain underscores and break LaTeX
    optional_placeholders = [
        "{{YOUR_TAGLINE_OR_EDUCATION}}",
        "{{YOUR_LINKEDIN}}",
        "{{YOUR_LINKEDIN_URL}}",
        "{{YOUR_PHONE_TEL}}",
    ]
    for ph in optional_placeholders:
        tex_content = tex_content.replace(ph, "")

    # Fix common image path mistakes: templates may reference ../figures/ but
    # compilation runs from project root, so use figures/
    tex_content = tex_content.replace("../figures/", "figures/")

    # Final normalization: ensure ampersands inadvertently produced as
    # "\textbackslash{}&" during escaping are reduced back to "\&". This
    # preserves tabular alignment characters (raw '&') while still fixing
    # artifacts coming from latex_escape transformations.
    tex_content = re.sub(r"\\textbackslash\{\}\\&", r"\\&", tex_content)
    tex_content = tex_content.replace(r"\textbackslash{}&", r"\&")
    tex_content = re.sub(r"\\\\&", r"\\&", tex_content)

    # Final safety: escape any raw underscores not already escaped. This
    # avoids LaTeX errors like "Missing $ inserted" when an underscore
    # sneaks into the output (for example after backslash/textbackslash
    # normalization). Use a negative lookbehind so we don't double-escape.
    tex_content = re.sub(r"(?<!\\)_", r"\\_", tex_content)

    # punctuation. When template macros include '\\' between fields and
    # some fields are blank, we can end up with sequences like '\\\\,'
    # Inject JOB_TITLE and COMPANY_NAME placeholders explicitly
    # COMPANY_NAME: only inject if explicitly provided or derived and not blank
    # helper to replace multiple token variants (escaped underscores, triple/double braces)
    def replace_variants(tex_content_local, token, value):
        # token example: 'JOB_TITLE' or 'COMPANY_NAME'
        plain_double = "{{" + token + "}}"
        plain_triple = "{{{" + token + "}}}"
        esc_token = token.replace("_", r"\_")
        esc_double = "{{" + esc_token + "}}"
        esc_triple = "{{{" + esc_token + "}}}"
        for variant in (plain_double, plain_triple, esc_double, esc_triple):
            if variant in tex_content_local:
                # triple-brace variants expect a braced replacement
                if variant.startswith("{{{"):
                    tex_content_local = tex_content_local.replace(
                        variant, "{" + value + "}"
                    )
                else:
                    tex_content_local = tex_content_local.replace(variant, value)
        return tex_content_local

    if explicit_company_provided:
        tex_content = replace_variants(tex_content, "JOB_TITLE", job_title_val)
        tex_content = replace_variants(tex_content, "COMPANY_NAME", company_val)
    else:
        tex_content = replace_variants(tex_content, "JOB_TITLE", job_title_val)
        tex_content = replace_variants(tex_content, "COMPANY_NAME", "")
    #    LaTeX linebreak in the template). This avoids accidental long runs.
    tex_content = re.sub(r"(?:\\){3,}", r"\\", tex_content)
    # 2) Remove occurrences of double-backslash followed immediately by a comma
    #    which happen when a comma in the template follows an empty field.
    tex_content = re.sub(r"\\\\,\s*", "", tex_content)
    # 3) Remove leading '\\' inside braces (e.g. address field) if present
    tex_content = re.sub(r"\{\\\\\s*", "{", tex_content)
    # 4) Remove stray '\\,' (backslash followed by comma) left over
    tex_content = tex_content.replace("\\,", "")
    # 5) Collapse any remaining runs of more than two backslashes to two
    tex_content = re.sub(r"(?:\\){3,}", r"\\", tex_content)

    # Write output: ensure parent directory exists before writing the .tex file
    out_dir = os.path.dirname(output_path)
    if out_dir:
        try:
            os.makedirs(out_dir, exist_ok=True)
        except Exception:
            # If directory creation fails for any reason, raise a clear error
            raise
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(tex_content)


def load_user_profiles(yaml_path="user_info.yml"):
    """Load user profiles from YAML. If PyYAML not installed, do a minimal parse."""
    p = Path(yaml_path)
    if not p.exists():
        # try searching upward up to 3 parent directories (works when running from 3_latex/)
        cwd = Path.cwd()
        found = None
        for parent in [cwd, cwd.parent, cwd.parent.parent, cwd.parent.parent.parent]:
            candidate = parent / yaml_path
            if candidate.exists():
                found = candidate
                break
        if found is None:
            return []
        p = found
    if YAML_AVAILABLE:
        with open(p, "r", encoding="utf-8") as f:
            data = yaml_mod.safe_load(f)
            return data if isinstance(data, list) else []
    # Minimal parser for simple YAML list of maps
    profiles = []
    curr = None
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip() or line.strip().startswith("#"):
                continue
            if line.lstrip().startswith("- "):
                if curr:
                    profiles.append(curr)
                curr = {}
                line = line[line.index("- ") + 2 :]
                if ":" in line:
                    k, v = line.split(":", 1)
                    curr[k.strip()] = v.strip()
            elif ":" in line and curr is not None:
                k, v = line.split(":", 1)
                curr[k.strip()] = v.strip()
        if curr:
            profiles.append(curr)
    return profiles


def latex_escape(s: str) -> str:
    """Escape common LaTeX special characters."""
    if s is None:
        return ""
    # Coerce to string if needed (YAML may parse phone numbers as int)
    if not isinstance(s, str):
        s = str(s)
    # Preserve any user-escaped ampersands (literal \&) so we don't
    # convert the leading backslash into a printed backslash glyph
    # (\textbackslash{}) later. Use an alphanumeric token to avoid
    # accidental escaping of underscores; restore it at the end.
    AMP_PRE_ESC = "AMPTOKEN42"
    s = s.replace("\\&", AMP_PRE_ESC)
    # Replace characters with their LaTeX-escaped equivalents.
    # Note: order matters. Do NOT replace backslash first — do it last to
    # avoid introducing extra backslashes before other escapes (which
    # could produce sequences like "\\\\&" or "\\&" that TeX
    # interprets as a linebreak followed by an alignment tab).
    repl_order = [
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
        # backslash last
        ("\\", r"\textbackslash{}"),
    ]
    for k, v in repl_order:
        s = s.replace(k, v)
    # Restore any preserved user-escaped ampersands as a single-escaped \&
    s = s.replace(AMP_PRE_ESC, r"\&")
    return s


# Font detection and host-side caching removed per user request.
# The parser now always emits an unconditional \setmainfont when a
# preferred font is supplied on the CLI or via the user profile.


def parse_front_matter(md_file):
    """Very small front-matter parser: returns a dict of top-level key: value pairs."""
    try:
        with open(md_file, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception:
        return {}
    fm = {}
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            block = parts[1]
            for line in block.splitlines():
                if not line.strip() or line.strip().startswith("#"):
                    continue
                if ":" in line:
                    k, v = line.split(":", 1)
                    fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm


def detect_language_from_frontmatter(frontmatter: dict, filename_stem: str = ""):
    """Detect language from frontmatter 'language' key or from filename suffix.
    Returns 'de' or 'en' or None."""
    if not frontmatter and not filename_stem:
        return None
    # 1) explicit language in frontmatter
    lang = frontmatter.get("language") if isinstance(frontmatter, dict) else None
    if lang:
        l = lang.strip().lower()
        if l.startswith("g") or "ger" in l or l in ("de", "deutsch", "german"):
            return "de"
        if l.startswith("e") or "eng" in l or l in ("en", "english"):
            return "en"
    # 2) check fileName in frontmatter
    fn = frontmatter.get("fileName") if isinstance(frontmatter, dict) else None
    if fn:
        fn = str(fn).strip()
        if (
            fn.upper().endswith("_DE.md")
            or fn.upper().endswith("_DE")
            or fn.upper().endswith("-DE.md")
            or fn.upper().endswith("-DE")
        ):
            return "de"
        if (
            fn.upper().endswith("_ENG.md")
            or fn.upper().endswith("_ENG")
            or fn.upper().endswith("-ENG.md")
            or fn.upper().endswith("-ENG")
        ):
            return "en"
    # 3) check filename stem
    if filename_stem:
        s = filename_stem.strip()
        if s.upper().endswith("_DE") or s.upper().endswith("-DE"):
            return "de"
        if s.upper().endswith("_ENG") or s.upper().endswith("-ENG"):
            return "en"
    return None


def format_date_for_lang(dt: datetime, lang: Optional[str] = None):
    """Return a formatted date string according to language.
    German months are produced from an internal map to avoid locale dependence."""
    if lang == "de":
        months_de = {
            1: "Januar",
            2: "Februar",
            3: "März",
            4: "April",
            5: "Mai",
            6: "Juni",
            7: "Juli",
            8: "August",
            9: "September",
            10: "Oktober",
            11: "November",
            12: "Dezember",
        }
        return f"{dt.day}. {months_de.get(dt.month, dt.strftime('%B'))} {dt.year}"
    # Default: English-style (day. Month Year) — months from system locale via strftime
    return dt.strftime("%d. %B %Y")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert n8n markdown to .tex files (batch or single)"
    )
    parser.add_argument(
        "file", nargs="?", help="Optional single markdown file to process"
    )
    parser.add_argument("--user", "-u", help="User profile id from user_info.yml")
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Automatically accept suggested filenames and overwrite",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without writing files",
    )
    # Available templates: 'modern' and optional 'engineering' if present.
    parser.add_argument(
        "--template",
        choices=["modern", "engineering"],
        help="Choose template non-interactively",
    )
    parser.add_argument(
        "--date",
        help='Override date to use in templates (e.g. "23. Oktober 2025"). If omitted, today\'s date is used',
    )
    parser.add_argument(
        "--font",
        help='Preferred main font name to use in templates (e.g. "Lato" or "Source Sans 3").',
    )
    args = parser.parse_args()
    # If environment variables are set (via Make), use them as defaults when flags omitted
    env_user = os.environ.get("USER") or os.environ.get("USER_PROFILE")
    env_template = os.environ.get("TEMPLATE")
    env_font = os.environ.get("FONT")
    env_yes = os.environ.get("YES")
    env_dry = os.environ.get("DRY_RUN")
    if not args.user and env_user:
        args.user = env_user
    if not args.template and env_template:
        args.template = env_template
    # Allow FONT to be supplied as an env var (Makefiles may set FONT=...)
    if not getattr(args, "font", None) and env_font:
        args.font = env_font
    if not args.yes and env_yes:
        # treat any non-empty env value as truthy
        args.yes = True
    if not args.dry_run and env_dry:
        args.dry_run = True
    # If running non-interactively (e.g. invoked from Make), default to yes to avoid prompts
    try:
        if not sys.stdout.isatty():
            args.yes = True
    except Exception:
        # If isatty check fails for any reason, don't crash - keep provided args
        pass
    # Allow either: single file passed as argument, or no args -> process all md in src/content/
    md_files = []
    if args.file:
        md_file = args.file
        if not os.path.exists(md_file):
            print(f"Error: File not found: {md_file}")
            sys.exit(1)
        md_files = [md_file]
    else:
        # Batch mode: look for all markdown files in src/content/
        content_dir = Path("src/content")
        if not content_dir.exists():
            print("Error: src/content/ directory not found")
            sys.exit(1)
        md_files = sorted([str(p) for p in content_dir.glob("*.md")])
        if not md_files:
            print("Error: No markdown files found in src/content/")
            sys.exit(1)

    print("╔══════════════════════════════════════════════╗")
    print("║  Application Letter from Markdown           ║")
    print("╚══════════════════════════════════════════════╝")

    # Choose template (CLI overrides interactive). Classic template support
    # has been removed; default to Modern when not provided.
    if args.template:
        if args.template == "modern":
            template = "src/templates/cover_letter_modern.tex"
            template_name = "Modern"
        elif args.template == "engineering":
            template = "src/templates/cover_letter_engineering.tex"
            template_name = "Engineering"
        else:
            print(
                f"Error: unsupported template '{args.template}'. Only 'modern' and 'engineering' are supported."
            )
            sys.exit(1)
    else:
        # Non-interactive default: Modern template
        template = "src/templates/cover_letter_modern.tex"
        template_name = "Modern"

    # Load user profiles and prompt selection
    profiles = load_user_profiles()
    selected_user = None
    if profiles:
        # If --user provided, try to find it
        if args.user:
            for p in profiles:
                if p.get("id") == args.user:
                    selected_user = p
                    break
            if not selected_user:
                print(
                    f"User profile '{args.user}' not found. Available: {[p.get('id') for p in profiles]}"
                )
                sys.exit(1)
            print(f"Selected user: {selected_user.get('full_name','')}")
        else:
            print("\nAvailable user profiles:")
            for i, p in enumerate(profiles, start=1):
                nid = p.get("id") or p.get("full_name") or f"user{i}"
                print(f"  {i}) {nid}")
            sel = input(
                "Select user profile by number (or press Enter to skip): "
            ).strip()
            if sel:
                try:
                    idx = int(sel) - 1
                    selected_user = profiles[idx]
                    print(f"Selected user: {selected_user.get('full_name','')}")
                except Exception:
                    print("Invalid selection, continuing without auto-fill")

    # (Per-file date handling moved into processing loop so we can detect
    # language per-markdown and format dates accordingly.)

    # Process each markdown file
    for md_file in md_files:
        print("\n-------------------------------------------------------")
        print(f"Processing: {md_file}")
        sections = parse_markdown(md_file)
        if not sections:
            print(f"Warning: No sections found in {md_file} - skipping")
            continue

        basename = Path(md_file).stem
        # Detect front-matter language or filename suffix (DE/ENG) and
        # compute a language-aware date string for this file. CLI --date
        # overrides formatting if provided.
        front = parse_front_matter(md_file)
        lang = detect_language_from_frontmatter(front, basename)
        if args.date:
            date_str = args.date
        else:
            date_str = format_date_for_lang(datetime.now(), lang)
        # Build per-file effective user context so templates always receive DATE
        if selected_user:
            selected_user_effective = dict(selected_user)
            selected_user_effective["date"] = date_str
        else:
            selected_user_effective = {"date": date_str}
        # Propagate font preference from CLI into the effective user context
        if hasattr(args, "font") and args.font:
            selected_user_effective["preferred_font"] = args.font
        suggested = f"{basename}.tex"
        print(f"Suggested filename: {suggested}")
        if args.dry_run:
            print(f"[dry-run] Would create: src/applications/{suggested}")
            continue
        if args.yes:
            custom = ""
            auto_overwrite = True
        else:
            custom = input(
                "Press Enter to use this name, or type a different name (or type SKIP to skip): "
            ).strip()

        if custom.lower() == "skip":
            print(f"Skipping {md_file}")
            continue

        if custom:
            filename = custom if custom.endswith(".tex") else f"{custom}.tex"
        else:
            filename = suggested

        output_path = f"src/applications/{filename}"

        # If exists, ask per-file
        if os.path.exists(output_path):
            if args.yes:
                overwrite = "y"
            else:
                overwrite = input(
                    f"Warning: File already exists: {output_path}\nOverwrite? (y/n): "
                )
            if overwrite.lower() != "y":
                print(f"Skipping {output_path}")
                continue

        create_tex_file(
            template,
            sections,
            output_path,
            user=selected_user_effective,
            md_basename=basename,
            language=lang,
        )
        print(f"✓ Created: {output_path}")
        print(f"  Template: {template_name}")
        print(f"  Source: {md_file}")

    print(
        "\nAll done. Review files in src/applications/ and run ./compile.sh or `make all` to build PDFs."
    )


if __name__ == "__main__":
    main()

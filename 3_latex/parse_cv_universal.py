#!/usr/bin/env python3
"""
Universal CV parser supporting multiple templates (hipster, luxsleek)
Usage: python parse_cv_universal.py <cv_markdown_file> --user <user_id> [--template hipster|luxsleek]
"""

import re
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Try to import PyYAML
yaml_mod = None
try:
    import yaml as yaml_mod
    YAML_AVAILABLE = True
except Exception:
    YAML_AVAILABLE = False

# Import the existing parser functions
# The original project kept common parsing helpers in `parse_cv.py`.
# To make this universal script self-contained so `parse_cv.py` can be removed,
# we bring the small set of helper functions here (copied/adapted from parse_cv.py).


def latex_escape(text):
    """Escape special LaTeX characters"""
    if not text:
        return ""
    # Order matters - do backslash first
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text


def parse_section(content, section_name):
    """Extract content of a section"""
    # Try the provided section name first, but also support common
    # translations (English <-> German) so the parser can handle
    # markdown files written in either language.
    # Build a list of candidate section headings to match.
    candidates = [section_name]
    # Common English->German mappings for CV headings
    SECTION_I18N = {
        "About Me": "Über mich",
        "Interests": "Interessen",
        "Specialization": "Spezialisierung",
        "Technical Skills": "Technische Fähigkeiten",
        "Experience": "Berufserfahrung",
        "Education": "Ausbildung",
        "Certifications": "Zertifikate",
        "Languages": "Sprachen",
        "Core strengths": "Kernkompetenzen",
        "One-line summary": "Kurzprofil",
    }

    # If section_name maps to a German equivalent, include it as candidate.
    if section_name in SECTION_I18N:
        candidates.append(SECTION_I18N[section_name])

    # Also include a lowercase / capitalized variant to be more flexible
    candidates.extend([s.capitalize() for s in list(dict.fromkeys(candidates))])

    # Build an alternation pattern for any of the candidates and match.
    alt = "|".join([re.escape(c) for c in candidates if c])
    pattern = rf"##\s+(?:{alt})\s*\n\n(.*?)(?=\n##|\Z)"
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def parse_specializations(content):
    """Parse specialization bullet points"""
    spec_text = parse_section(content, "Specialization")
    if not spec_text:
        return []

    specs = []
    for line in spec_text.split("\n"):
        line = line.strip()
        if line.startswith("- "):
            specs.append(line[2:].strip())
    return specs


def parse_skills(content):
    """Parse technical skills with proficiency levels"""
    skills_text = parse_section(content, "Technical Skills")
    if not skills_text:
        return []

    skills = []
    for line in skills_text.split("\n"):
        # Format: **Skill Name:** proficiency_level
        match = re.match(r"\*\*(.+?):\*\*\s*([\d.]+)", line)
        if match:
            skill_name = match.group(1).strip()
            proficiency = float(match.group(2).strip())
            skills.append({"name": skill_name, "level": proficiency})
        else:
            # Accept bold-only skill lines like: **Tooling & Frameworks**
            match2 = re.match(r"\*\*(.+?)\*\*\s*$", line)
            if match2:
                skill_name = match2.group(1).strip()
                skills.append({"name": skill_name, "level": None})
    return skills


def parse_entries(content, section_name):
    """Parse multi-entry sections (Experience, Education, etc.)"""
    section_text = parse_section(content, section_name)
    if not section_text:
        return []

    entries = []
    # Split by --- separator
    blocks = section_text.split("---")

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        entry = {}

        # Extract title and organization: **Title** | Organization
        title_match = re.search(r"\*\*(.+?)\*\*\s*\|\s*(.+?)$", block, re.MULTILINE)
        if title_match:
            entry["title"] = title_match.group(1).strip()
            entry["organization"] = title_match.group(2).strip()
        # Extract dates and location: *YYYY--YYYY | Location* (match whole line,
        # avoid matching inside bold '**' markers)
        date_match = re.search(r"^\*(.+?)\*$", block, re.MULTILINE)
        if date_match:
            date_info = date_match.group(1).strip()
            if "|" in date_info:
                parts = date_info.split("|")
                entry["dates"] = parts[0].strip()
                entry["location"] = parts[1].strip() if len(parts) > 1 else ""
            else:
                entry["dates"] = date_info
                entry["location"] = ""

        # Extract description (bullet points or paragraph)
        desc_lines = []
        for line in block.split("\n"):
            line = line.strip()
            if line.startswith("- "):
                desc_lines.append(line[2:])
            elif line and not line.startswith("**") and not line.startswith("*"):
                # It's a paragraph description
                desc_lines.append(line)

        entry["description"] = " ".join(desc_lines) if desc_lines else ""
        entry["bullets"] = desc_lines  # Keep individual bullets for formatting

        if entry:
            entries.append(entry)

    return entries


def parse_certifications(content):
    """Parse certifications"""
    cert_text = parse_section(content, "Certifications")
    if not cert_text:
        return []
    certs = []
    # Support multiple line formats. We iterate over actual lines to be
    # tolerant of entries without a year (common in some CVs), different
    # dash characters (hyphen, en-dash, em-dash) and optional leading bullets.
    for line in cert_text.splitlines():
        line = line.strip()
        if not line or line == "---":
            continue
        # Remove leading list markers
        if line.startswith("- ") or line.startswith("* "):
            line = line[2:].strip()

        # Try patterns in order of specificity
        # 1) **YYYY** - Name - Org
        m = re.search(r"\*\*(\d{4})\*\*\s*[-–—]\s*(.+?)\s*[-–—]\s*(.+)", line)
        if m:
            certs.append({"year": m.group(1), "name": m.group(2).strip(), "organization": m.group(3).strip()})
            continue

        # 2) **Name** — Org  (bold name, no year)
        m2 = re.search(r"\*\*(.+?)\*\*\s*[-–—]\s*(.+)", line)
        if m2:
            certs.append({"year": "", "name": m2.group(1).strip(), "organization": m2.group(2).strip()})
            continue

        # 3) Name — Org  (no bold)
        m3 = re.search(r"(.+?)\s*[-–—]\s*(.+)", line)
        if m3:
            certs.append({"year": "", "name": m3.group(1).strip(), "organization": m3.group(2).strip()})
            continue

        # 4) Fallback: whole line is the certification name
        certs.append({"year": "", "name": line.strip().strip('*').strip(), "organization": ""})

    return certs


def parse_languages(content):
    """Parse languages section"""
    lang_text = parse_section(content, "Languages")
    if not lang_text:
        return []

    languages = []
    for line in lang_text.split("\n"):
        # Flexible formats supported:
        #  - **Language:** Level (X/4)
        #  - **Language:** Level
        #  - **Language:** Level (C1-C2)  (kept as level string)
        match = re.search(r"\*\*(.+?):\*\*\s*(.+?)(?:\s*\((\d)/4\))?$", line)
        if match:
            name = match.group(1).strip()
            level = match.group(2).strip()
            circles = int(match.group(3)) if match.group(3) else 0
            languages.append({
                "name": name,
                "level": level,
                "circles": circles
            })
    return languages


def parse_publications(content):
    """Parse publications & research output section into a list of items.

    Each publication in the markdown is expected to be a block separated by
    '---' or a pair of lines: title then URL. This function returns a list of
    dicts: {title, url} where url may be empty.
    """
    pub_text = parse_section(content, "Publications")
    if not pub_text:
        # try alternative heading used in this repo
        pub_text = parse_section(content, "Publications & Research Output")
    if not pub_text:
        return []

    pubs = []
    # Split blocks by the horizontal rule or iterate lines for compact lists
    blocks = [b.strip() for b in re.split(r"\n---\n", pub_text) if b.strip()]
    for block in blocks:
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        if not lines:
            continue
        title = lines[0]
        url = ""
        if len(lines) > 1 and (lines[1].startswith("http://") or lines[1].startswith("https://")):
            url = lines[1]
        else:
            # Try to find a URL anywhere in the block
            m = re.search(r"(https?://\S+)", block)
            if m:
                url = m.group(1)

        pubs.append({"title": title, "url": url})

    return pubs


def fill_template(template_path, data, output_path):
    """Fill template with parsed data"""
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
    # Prepare replacements
    # Use a localized document title when the parser detected German input
    lang = data.get("lang", "en")
    if lang == "de":
        doc_title = f"Lebenslauf - {data.get('full_name', 'Lebenslauf')}"
    else:
        doc_title = f"CV - {data.get('full_name', 'Curriculum Vitae')}"

    replacements = {
        "{{DOCUMENT_TITLE}}": doc_title,
        "{{FULL_NAME}}": latex_escape(data.get("full_name", "")),
        "{{FIRST_NAME}}": latex_escape(data.get("first_name", "")),
        "{{LAST_NAME}}": latex_escape(data.get("last_name", "")),
        "{{JOB_TITLE}}": latex_escape(data.get("job_title", "")),
        "{{PROFILE_PICTURE}}": "profile.jpg",  # Default, can be customized
        "{{ABOUT_ME}}": latex_escape(data.get("about_me", "")),
        "{{PERSONAL_INFO}}": data.get("personal_info", ""),
        "{{SPECIALIZATIONS}}": data.get("specializations", ""),
        "{{INTERESTS}}": latex_escape(data.get("interests", "")),
        "{{TECHNICAL_SKILLS}}": data.get("technical_skills", ""),
        "{{PROGRAMMING_SKILLS}}": data.get("programming_skills", ""),
        "{{CONTACT_BUBBLES}}": data.get("contact_bubbles", ""),
        "{{SHORT_RESUME}}": data.get("short_resume", ""),
        "{{EXPERIENCE_ENTRIES}}": data.get("experience", ""),
        "{{EDUCATION_ENTRIES}}": data.get("education", ""),
        "{{CERTIFICATIONS}}": data.get("certifications", ""),
    # Languages: convert list -> LaTeX table lines when possible
    "{{LANGUAGES}}": generate_languages(data.get("languages", [])),
        "{{PUBLICATIONS_SECTION}}": data.get("publications", ""),
        "{{TALKS_SECTION}}": data.get("talks", ""),
        "{{FOOTER_INFO}}": data.get("footer", ""),
    }

    # Replace all placeholders
    for placeholder, value in replacements.items():
        template = template.replace(placeholder, value)

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(template)

    print(f"✓ Generated: {output_path}")


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


def generate_luxsleek_experience(entries):
    """Generate experience entries for LuxSleek template"""
    if not entries:
        return ""
    
    lines = []
    for entry in entries:
        title = latex_escape(entry.get("title", ""))
        org = latex_escape(entry.get("organization", ""))
        dates = latex_escape(entry.get("dates", ""))
        location = latex_escape(entry.get("location", ""))
        desc = entry.get("description", "")
        
        # Format: Title (bold)
        # Company/University + (Location) on next line in reduced-size text
        # Time period on the following line in reduced-size text
        
        # Line 1: Position title (bold)
        lines.append(f"\\textbf{{{title}}}")

        # Line 2: at Company (Location) in reduced size
        location_part = f", {location}" if location else ""
        lines.append(f"\\reducedtext{{at \\textit{{{org}}}{location_part}}}")

        # Line 3: Time period in reduced size
        lines.append(f"\\reducedtext{{{dates}}}")

        # Add description as bullet points (keep original bullets if present)
        if desc:
            lines.append("\\begin{itemize}[leftmargin=*,nosep]")
            bullets = entry.get("bullets", [])
            if bullets:
                for bullet in bullets:
                    lines.append(f"  \\item {latex_escape(bullet)}")
            else:
                lines.append(f"  \\item {latex_escape(desc)}")
            lines.append("\\end{itemize}")
        
        lines.append("\\vspace{1ex}")
        lines.append("")
    
    return "\n".join(lines)


def generate_luxsleek_education(entries):
    """Generate education entries for LuxSleek template"""
    if not entries:
        return ""
    
    lines = []
    for entry in entries:
        title = latex_escape(entry.get("title", ""))
        org = latex_escape(entry.get("organization", ""))
        dates = latex_escape(entry.get("dates", ""))
        location = latex_escape(entry.get("location", ""))
        desc = entry.get("description", "")
        
        # Line 1: Degree / Title (bold)
        lines.append(f"\\textbf{{{title}}}")

        # Line 2: University, Location in reduced size
        location_part = f", {location}" if location else ""
        lines.append(f"\\reducedtext{{\\textit{{{org}}}{location_part}}}")

        # Line 3: Dates in reduced size
        lines.append(f"\\reducedtext{{{dates}}}")

        if desc:
            lines.append(f"\\smaller{{{latex_escape(desc)}}}")

        lines.append("\\vspace{1ex}")
        lines.append("")
    
    return "\n".join(lines)


def generate_luxsleek_certifications(certs):
    """Generate certifications for LuxSleek template"""
    if not certs:
        return ""
    
    lines = []
    lines.append("\\begin{itemize}[leftmargin=*,nosep]")
    for cert in certs:
        year = cert.get("year", "")
        name = latex_escape(cert.get("name", ""))
        org = latex_escape(cert.get("organization", ""))

        if year:
            year = latex_escape(year)
            lines.append(f"  \\item \\textbf{{{year}}} - {name}{', \\textit{{' + org + '}}' if org else ''}")
        else:
            # No year: render name and optionally organization
            if org:
                lines.append(f"  \\item {name}, \\textit{{{org}}}")
            else:
                lines.append(f"  \\item {name}")
    
    lines.append("\\end{itemize}")
    return "\n".join(lines)


def generate_luxsleek_publications(pubs):
    """Generate LaTeX for publications for LuxSleek / templates.

    Returns a LaTeX itemize block with each publication as an item. If a URL
    is available, render as \href{url}{title} otherwise render the title.
    """
    if not pubs:
        return ""

    lines = []
    lines.append("\\begin{itemize}[leftmargin=*,nosep]")
    for p in pubs:
        # Remove common markdown bold/italic markers around titles
        raw_title = p.get("title", "")
        # strip surrounding ** or * if present
        title_text = re.sub(r"^\*{1,2}\s*(.+?)\s*\*{1,2}$", r"\1", raw_title)
        title = latex_escape(title_text)
        url = p.get("url", "")
        if url:
            # Use \href if hyperref is available in the template
            escaped_url = latex_escape(url)
            lines.append(f"  \\item \\href{{{escaped_url}}}{{{title}}}")
        else:
            lines.append(f"  \\item {title}")
    lines.append("\\end{itemize}")
    return "\n".join(lines)


def generate_luxsleek_languages(languages):
    """Generate languages list for LuxSleek template"""
    if not languages:
        return ""
    
    lang_parts = []
    for lang in languages:
        name = latex_escape(lang["name"])
        level = latex_escape(lang["level"])
        lang_parts.append(f"\\textbf{{{name}}} ({level})")
    
    return ", ".join(lang_parts)


def generate_luxsleek_skills(skills):
    """Generate skills list for LuxSleek template"""
    if not skills:
        return ""
    
    lines = []
    for skill in skills:
        name = latex_escape(skill["name"])
        lines.append(f"\\item {name}")
    
    return "\n".join(lines)


def generate_luxsleek_interests(interests_text):
    """Convert an interests text block into a LaTeX itemize list for the LuxSleek sidebar.

    Handles multiline markdown bullets, comma-separated lists, or single-line free text.
    """
    if not interests_text:
        return ""

    items = []
    # Prefer explicit lines if present
    if "\n" in interests_text:
        for ln in interests_text.splitlines():
            ln = ln.strip()
            if not ln:
                continue
            if ln.startswith("- ") or ln.startswith("* "):
                ln = ln[2:].strip()
            items.append(ln)
    else:
        # fallbacks: comma-separated or ' - ' separated or single item
        if "," in interests_text:
            parts = [p.strip() for p in interests_text.split(",") if p.strip()]
            items.extend(parts)
        elif " - " in interests_text:
            parts = [p.strip() for p in interests_text.split(" - ") if p.strip()]
            items.extend(parts)
        else:
            items.append(interests_text.strip())

    # Return item lines only — the template wraps the list in \begin{itemize}...
    lines = []
    for it in items:
        lines.append(f"\\item {latex_escape(it)}")

    return "\n".join(lines)


def generate_languages(languages):
    """Generate languages table with proficiency circles for hipster template"""
    if not languages:
        return ""

    lines = []
    for lang in languages:
        name = latex_escape(lang.get("name", ""))
        level = latex_escape(lang.get("level", ""))
        circles = lang.get("circles", 0) if isinstance(lang.get("circles", 0), int) else 0
        empty_circles = max(0, 4 - circles)

        lines.append(
            f"\\textbf{{{name}}} & {level} & \\pictofraction{{\\faCircle}}{{cvgreen}}{{{circles}}}{{black!30}}{{{empty_circles}}}{{\\tiny}} \\\\"
        )

    return "\n".join(lines)


def fill_luxsleek_template(template_path, data, output_path, user_profile, font_name=None):
    """Fill LuxSleek template with parsed data and user profile"""
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
    
    # Clean up markdown artifacts from text fields
    about_me = data.get("about_me", "").replace("---", "").strip()
    interests = data.get("interests", "").replace("---", "").strip()
    
    # Build font setup if font_name provided
    font_setup = ""
    if font_name:
        # Use fontspec but guard against missing fonts to avoid XeLaTeX aborts.
        # We prefer the requested main/sans font, and for monospaced try JetBrains Mono then Menlo.
        font_setup = (
            "% Custom font selection via fontspec\n"
            "\\usepackage{fontspec}\n"
            "% Try to set main/sans font if available, otherwise fall back to default sans.\n"
            "\\IfFontExistsTF{" + font_name + "}{%\n"
            "  \\setmainfont{" + font_name + "}%\n"
            "  \\setsansfont{" + font_name + "}%\n"
            "}{%\n"
            "  % Font not found: use default sans-serif family\n"
            "  \\renewcommand{\\familydefault}{\\sfdefault}%\n"
            "}%\n"
            "% For monospaced font: prefer JetBrains Mono, fall back to Menlo (macOS), otherwise leave default.\n"
            "\\IfFontExistsTF{JetBrains Mono}{%\n"
            "  \\setmonofont{JetBrains Mono}[Scale=0.9]%\n"
            "}{%\n"
            "  \\IfFontExistsTF{Menlo}{%\n"
            "    \\setmonofont{Menlo}[Scale=0.9]%\n"
            "  }{%\n"
            "    % leave monospaced default - do not call \\setmonofont to avoid errors\n"
            "  }%\n"
            "}%\n"
        )
    else:
        # Default fallback: use standard LaTeX sans-serif
        font_setup = (
            "% Use sans-serif font (available by default)\n"
            "\\renewcommand{\\familydefault}{\\sfdefault}"
        )
    
    # Prepare replacements using user profile for personal data
    replacements = {
        "{{MAIN_FONT_SETUP}}": font_setup,
        "{{FIRST_NAME}}": latex_escape(user_profile.get("first_name", "")),
        "{{LAST_NAME}}": latex_escape(user_profile.get("last_name", "")),
        "{{JOB_TITLE}}": latex_escape(user_profile.get("job_title", "")),
        "{{EMAIL}}": latex_escape(user_profile.get("email", "")),
        "{{PHONE}}": latex_escape(user_profile.get("phone", "")),
        "{{LOCATION}}": latex_escape(user_profile.get("location", "")),
        "{{NATIONALITY}}": latex_escape(user_profile.get("nationality", "")),
        "{{BIRTH_YEAR}}": latex_escape(user_profile.get("birth_year", "")),
    "{{ABOUT_ME}}": latex_escape(about_me),
    # Render interests as a vertical itemize list in the sidebar for LuxSleek
    "{{INTERESTS}}": generate_luxsleek_interests(interests),
        "{{PROFILE_PICTURE}}": user_profile.get("profile_pic", "profile.jpg"),
        "{{LANGUAGES_LIST}}": generate_luxsleek_languages(data.get("languages", [])),
        "{{SKILLS_LIST}}": generate_luxsleek_skills(data.get("technical_skills", [])),
        "{{EXPERIENCE_ENTRIES}}": generate_luxsleek_experience(data.get("experience", [])),
        "{{EDUCATION_ENTRIES}}": generate_luxsleek_education(data.get("education", [])),
        "{{CERTIFICATIONS}}": generate_luxsleek_certifications(data.get("certifications", [])),
        "{{PUBLICATIONS_SECTION}}": data.get("publications", ""),
    }
    
    # Replace all placeholders
    for placeholder, value in replacements.items():
        template = template.replace(placeholder, value)
    
    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(template)
    
    print(f"✓ Generated: {output_path}")


def fill_hipster_template(template_path, data, output_path, user_profile, font_name=None):
    """Fill hipster template - needs update to use user profile"""
    # For now, merge user profile into data
    data.update({
        "first_name": user_profile.get("first_name", ""),
        "last_name": user_profile.get("last_name", ""),
        "full_name": user_profile.get("full_name", ""),
        "email": user_profile.get("email", ""),
        "phone": user_profile.get("phone", ""),
        "location": user_profile.get("location", ""),
        "linkedin_url": user_profile.get("linkedin_url", ""),
        "linkedin_label": user_profile.get("linkedin_label", ""),
        "github": user_profile.get("github", ""),
        "website": user_profile.get("website", ""),
        "nationality": user_profile.get("nationality", ""),
        "birth_year": user_profile.get("birth_year", ""),
    })
    
    # Read template
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
    
    # Build font setup if font_name provided
    font_setup = ""
    if font_name:
        font_setup = (
            "% Custom font selection via fontspec\n"
            "\\usepackage{fontspec}\n"
            "\\IfFontExistsTF{" + font_name + "}{%\n"
            "  \\setmainfont{" + font_name + "}%\n"
            "  \\setsansfont{" + font_name + "}%\n"
            "}{%\n"
            "  \\renewcommand{\\familydefault}{\\sfdefault}%\n"
            "}%\n"
            "\\IfFontExistsTF{JetBrains Mono}{%\n"
            "  \\setmonofont{JetBrains Mono}[Scale=0.9]%\n"
            "}{%\n"
            "  \\IfFontExistsTF{Menlo}{%\n"
            "    \\setmonofont{Menlo}[Scale=0.9]%\n"
            "  }{%\n"
            "    % fallback: leave default monospace\n"
            "  }%\n"
            "}%\n"
        )
    else:
        # Leave empty - hipster template has its own defaults
        font_setup = "% Using document class default fonts"
    
    # Replace font placeholder first
    template = template.replace("{{MAIN_FONT_SETUP}}", font_setup)
    
    # Then use the local fill_template for the remaining placeholder substitutions.
    # Write the modified template to the output file first, then call fill_template
    # to perform the standard placeholder replacement and final write.
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(template)
    # Now invoke local fill_template (copied into this module) to finish filling
    fill_template(output_path, data, output_path)


def parse_and_generate(md_file, template_name="hipster", user_id=None, font_name=None):
    """Parse CV markdown and generate output for specified template"""
    
    # Load user profiles
    profiles = load_user_profiles()
    
    # Determine user_id from filename if not provided and detect language
    lang = "en"
    if not user_id:
        # Extract stem and detect language suffixes like _de, -de, _en, -en
        filename = Path(md_file).stem
        m = re.search(r'[_-](de|en)$', filename, re.IGNORECASE)
        if m:
            lang = m.group(1).lower()
        else:
            lang = "en"

        # Remove leading cv- or cv_ and trailing language suffix when deriving user id
        name_part = re.sub(r'^cv[-_]', '', filename, flags=re.IGNORECASE)
        name_part = re.sub(r'[-_]?(en|de)$', '', name_part, flags=re.IGNORECASE)
        # First token (split on - or _) is a reasonable user id guess
        first_name = re.split(r'[-_]', name_part)[0]
        for profile in profiles:
            if profile.get("id") == first_name:
                user_id = first_name
                break

    # Save detected language into a local variable for use later
    detected_lang = lang
    
    if not user_id:
        print("Error: Could not determine user ID. Please specify with --user flag.")
        print(f"Available users: {', '.join([p.get('id', '?') for p in profiles])}")
        sys.exit(1)
    
    # Find user profile
    user_profile = None
    for profile in profiles:
        if profile.get("id") == user_id:
            user_profile = profile
            break
    
    if not user_profile:
        print(f"Error: User '{user_id}' not found in user_info.yml")
        print(f"Available users: {', '.join([p.get('id', '?') for p in profiles])}")
        sys.exit(1)
    
    print(f"Using profile: {user_profile.get('full_name', user_id)}")
    
    # Parse the markdown file using base parser
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract basic data
    data = {}
    data["source_file"] = md_file
    # expose detected language to templates and downstream functions
    data["lang"] = detected_lang
    
    # Parse sections
    data["about_me"] = parse_section(content, "About Me")
    data["interests"] = parse_section(content, "Interests")

    # Fallbacks for Interests: if the explicit `## Interests` section is missing,
    # try to reuse other short-summary sections in a sensible order so the
    # template doesn't end up empty. Preference order:
    #  1) One-line summary
    #  2) Core strengths
    #  3) First one or two lines of About Me
    if not data.get("interests"):
        one_line = parse_section(content, "One-line summary")
        if one_line:
            data["interests"] = one_line.strip()

    if not data.get("interests"):
        core = parse_section(content, "Core strengths")
        if core:
            # Keep only the first few bullet lines if present
            lines = [l.strip() for l in core.splitlines() if l.strip()]
            data["interests"] = "\n".join(lines[:3]) if lines else core.strip()

    if not data.get("interests") and data.get("about_me"):
        # Use the first one or two lines of About Me as a last resort
        about_lines = [l.strip() for l in data["about_me"].splitlines() if l.strip()]
        if about_lines:
            data["interests"] = "\n".join(about_lines[:2])
    
    # Parse technical skills
    skills = parse_skills(content)
    data["technical_skills"] = skills
    
    # Parse experience and education
    data["experience"] = parse_entries(content, "Experience")
    data["education"] = parse_entries(content, "Education")
    
    # Parse certifications
    data["certifications"] = parse_certifications(content)
    # Parse publications and render to LaTeX block for templates
    pubs = parse_publications(content)
    data["publications"] = generate_luxsleek_publications(pubs)
    
    # Parse languages
    data["languages"] = parse_languages(content)
    
    # Determine template and output paths
    templates = {
        "hipster": Path("src/templates/cv_hipster_template.tex"),
        "luxsleek": Path("src/templates/cv_luxsleek_template.tex"),
    }
    
    if template_name not in templates:
        print(f"Error: Unknown template '{template_name}'. Available: {', '.join(templates.keys())}")
        sys.exit(1)
    
    template_path = templates[template_name]
    
    # Generate output filename using user_id
    output = Path(f"src/applications/CV_{user_id}_{template_name}.tex")
    
    # Fill template based on type
    if template_name == "hipster":
        fill_hipster_template(template_path, data, output, user_profile, font_name)
    elif template_name == "luxsleek":
        fill_luxsleek_template(template_path, data, output, user_profile, font_name)
    
    print(f"✓ Generated: {output}")
    print(f"\nDone! Compile with:")
    print(f"  make compile FILE={output}")
    
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse CV markdown and generate LaTeX")
    parser.add_argument("markdown_file", type=Path, help="Path to CV markdown file")
    parser.add_argument(
        "--user", "-u",
        help="User profile ID from user_info.yml (auto-detected from filename if not specified)"
    )
    parser.add_argument(
        "--template",
        choices=["hipster", "luxsleek"],
        default="hipster",
        help="CV template to use (default: hipster)"
    )
    parser.add_argument(
        "--font",
        help="Custom font name to use (requires fontspec and XeLaTeX). Example: 'Source Sans 3' or 'Inter'"
    )
    
    args = parser.parse_args()
    
    if not args.markdown_file.exists():
        print(f"Error: File not found: {args.markdown_file}")
        sys.exit(1)
    
    print(f"Parsing CV: {args.markdown_file}")
    print(f"Using template: {args.template}")
    if args.font:
        print(f"Using custom font: {args.font}")
    
    parse_and_generate(args.markdown_file, args.template, args.user, args.font)

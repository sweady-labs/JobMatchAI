#!/bin/bash
#########################################################
# LaTeX Compilation Script with Automatic Organization
# Usage: ./compile.sh <filename.tex> [engine]
# Example: ./compile.sh main.tex xelatex
#########################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SRC_DIR="src"
OUTPUT_DIR="output"
BUILD_DIR="build"
DEFAULT_ENGINE="xelatex"

# Parse arguments
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: No .tex file specified${NC}"
    echo "Usage: ./compile.sh <filename.tex> [engine]"
    echo "Example: ./compile.sh main.tex xelatex"
    echo "Available engines: pdflatex, xelatex, lualatex"
    exit 1
fi

INPUT_FILE="$1"
ENGINE="${2:-$DEFAULT_ENGINE}"

# Extract filename without extension
BASENAME=$(basename "$INPUT_FILE" .tex)

# Determine full path to source file
if [ -f "$INPUT_FILE" ]; then
    SOURCE_FILE="$INPUT_FILE"
elif [ -f "$SRC_DIR/$INPUT_FILE" ]; then
    SOURCE_FILE="$SRC_DIR/$INPUT_FILE"
elif [ -f "$SRC_DIR/$BASENAME.tex" ]; then
    SOURCE_FILE="$SRC_DIR/$BASENAME.tex"
elif [ -f "$SRC_DIR/applications/$INPUT_FILE" ]; then
    SOURCE_FILE="$SRC_DIR/applications/$INPUT_FILE"
elif [ -f "$SRC_DIR/applications/$BASENAME.tex" ]; then
    SOURCE_FILE="$SRC_DIR/applications/$BASENAME.tex"
else
    echo -e "${RED}Error: Cannot find $INPUT_FILE${NC}"
    echo "Looked in: ./, $SRC_DIR/, $SRC_DIR/applications/"
    exit 1
fi

echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}  LaTeX Compilation${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "Source:  ${YELLOW}$SOURCE_FILE${NC}"
echo -e "Engine:  ${YELLOW}$ENGINE${NC}"
echo -e "Build:   ${YELLOW}$BUILD_DIR/${NC}"
echo -e "Output:  ${YELLOW}$OUTPUT_DIR/${BASENAME}.pdf${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"

# Create directories if they don't exist
mkdir -p "$BUILD_DIR" "$OUTPUT_DIR"

# Function to collect build artifacts (logs, aux files) into build/logs
collect_build_artifacts() {
    # Don't fail the script if copying artifacts fails
    set +e
    TS=$(date +%Y%m%dT%H%M%S)
    LOG_DIR="$BUILD_DIR/logs"
    mkdir -p "$LOG_DIR"

    # Copy files produced inside build dir
    for ext in log fls fdb_latexmk aux out synctex.gz xdv; do
        for f in "$BUILD_DIR"/*."$ext"; do
            [ -e "$f" ] || continue
            cp -a "$f" "$LOG_DIR/$(basename "$f").$TS" 2>/dev/null || true
        done
    done

    # Also copy any auxiliary/log files created at repository root
    for ext in log fls fdb_latexmk aux out synctex.gz xdv; do
        for f in ./*."$ext"; do
            [ -e "$f" ] || continue
            cp -a "$f" "$LOG_DIR/$(basename "$f").ROOT.$TS" 2>/dev/null || true
        done
    done

    set -e
}

# Ensure we always try to collect logs on exit (success or failure)
trap 'collect_build_artifacts' EXIT

# Preflight checks: fail early if source .tex contains unsafe tokens
echo -e "\n${YELLOW}[0/3] Running preflight checks...${NC}"
# Read source and search for patterns that commonly break LaTeX or indicate placeholders
## Detect unescaped ampersands using Perl (works on macOS)
## Ignore lines that are comments (start with optional whitespace then %)
## Also ignore ampersands in tabular/array environments (between \begin{tabular} and \end{tabular})
RAW_AMP_COUNT=$(perl -nle 'next if /^[[:space:]]*%/; next if /\\begin\{tabular/ .. /\\end\{tabular/; next if /\\begin\{array/ .. /\\end\{array/; print "$.:$_" if /(?<!\\)\&/' "$SOURCE_FILE" 2>/dev/null || true)
## Find placeholder tokens but ignore those that are only in commented lines (lines starting with optional whitespace then %)
## Also ignore LaTeX command definitions like {\small$\diamond$\ #1}
PLACEHOLDERS=$(awk '/\{\{[^}]+\}\}/ { if ($0 !~ /^[[:space:]]*%/ && $0 !~ /\\newcommand/ && $0 !~ /\\small\$\\diamond\$/) print NR":"$0 }' "$SOURCE_FILE" || true)
TODO_MARKS=$(grep -n --line-buffered -i "TODO" "$SOURCE_FILE" || true)

ERR=0
if [ -n "$RAW_AMP_COUNT" ]; then
    echo -e "${RED}Preflight: Found unescaped ampersand(s) in source:${NC}"
    echo "$RAW_AMP_COUNT"
    ERR=1
fi
if [ -n "$PLACEHOLDERS" ]; then
    echo -e "${RED}Preflight: Found placeholder token(s) like {{...}} in source:${NC}"
    echo "$PLACEHOLDERS"
    ERR=1
fi
if [ -n "$TODO_MARKS" ]; then
    echo -e "${YELLOW}Preflight: Found TODO markers (case-insensitive):${NC}"
    echo "$TODO_MARKS"
    # Do not treat TODO as fatal by default; just warn
fi

if [ $ERR -ne 0 ]; then
    echo -e "${RED}Preflight failed. Please fix the above issues in the .tex source or the markdown -> parser output before compiling.${NC}"
    exit 2
fi

# Compile with engine
echo -e "\n${YELLOW}[1/3] Compiling with $ENGINE...${NC}"
# Add style directory to TEXINPUTS so LaTeX can find custom class files
export TEXINPUTS=".:./style:./src:./src/applications:$TEXINPUTS"
$ENGINE \
    -interaction=nonstopmode \
    -halt-on-error \
    -output-directory="$BUILD_DIR" \
    "$SOURCE_FILE"

# Check if PDF was created
if [ ! -f "$BUILD_DIR/$BASENAME.pdf" ]; then
    echo -e "${RED}Error: Compilation failed - no PDF generated${NC}"
    echo -e "Check $BUILD_DIR/$BASENAME.log for errors"
    exit 1
fi

# Move PDF to output directory
echo -e "${YELLOW}[2/3] Moving PDF to output directory...${NC}"
mv "$BUILD_DIR/$BASENAME.pdf" "$OUTPUT_DIR/$BASENAME.pdf"

# Detect which font was requested in the source and whether compilation logged any fallbacks
LOG_FILE="$BUILD_DIR/$BASENAME.log"
REQUESTED_FONT=""
# Try to extract an explicit \setmainfont or \setsansfont from the source (first occurrence)
REQUESTED_FONT=$(/usr/bin/grep -oE "\\\\(setmainfont|setsansfont)\{[^}]+\}" "$SOURCE_FILE" 2>/dev/null | head -n1 | sed -E "s/.*\{([^}]+)\}.*/\1/") || true
if [ -z "$REQUESTED_FONT" ]; then
    # Fallback: look for the first \IfFontExistsTF{FontName} pattern
    REQUESTED_FONT=$(/usr/bin/grep -oE "\\\\IfFontExistsTF\{[^}]+\}" "$SOURCE_FILE" 2>/dev/null | head -n1 | sed -E "s/.*\{([^}]+)\}.*/\1/" ) || true
fi
APPLIED_STATUS="(unknown)"
if [ -f "$LOG_FILE" ] && [ -n "$REQUESTED_FONT" ]; then
    # Look for notable log messages related to fonts
    NOTFOUND_MATCH=$(/usr/bin/grep -i -n "not found" "$LOG_FILE" 2>/dev/null | /usr/bin/grep -i "$REQUESTED_FONT" || true)
    SHAPE_MATCH=$(/usr/bin/grep -i -n "Font shape" "$LOG_FILE" 2>/dev/null | /usr/bin/grep -i "$REQUESTED_FONT" || true)

    # Capture explicit 'using `...` instead' substitution lines (may include internal spec like TU/Name(0)/m/n)
    # Use a safer pipeline that avoids shell-interpreting backticks.
    # Strip grep's line numbers first, then normalize the backtick to a pipe and extract the bit
    SUBSTITUTED_SPEC=$(/usr/bin/grep -n 'using `' "$LOG_FILE" 2>/dev/null | sed -E 's/^[0-9]+://' | sed 's/`/|/g' | sed "s/' instead//" | sed -E 's/ on input line [0-9]+\.?$//' | cut -d'|' -f2 | tr '\n' ',' | sed 's/,$//' || true)

    if [ -n "$NOTFOUND_MATCH" ] || [ -n "$SHAPE_MATCH" ] || [ -n "$SUBSTITUTED_SPEC" ]; then
        if [ -n "$SUBSTITUTED_SPEC" ]; then
            # Try to extract a readable font family from the substituted spec
            # e.g. TU/SourceSans3(0)/m/n -> SourceSans3
            CLEAN_SUB=$(echo "$SUBSTITUTED_SPEC" | tr ',' '\n' | sed -E 's#^.*/([^/()]+)\([0-9]+\)/.*#\1#; s#^.*/([^/()]+)$#\1#' | awk '{print $1}' | tr '\n' ',' | sed 's/,$//' )
            APPLIED_STATUS="requested font '$REQUESTED_FONT' (fallback → ${CLEAN_SUB} [raw: ${SUBSTITUTED_SPEC}])"
        else
            APPLIED_STATUS="requested font '$REQUESTED_FONT' (fallback/substitution detected — see log excerpt below)"
        fi

        # Print a short relevant excerpt from the log to aid debugging
    MATCH_LINE=$(/usr/bin/grep -n -E 'not found|Font shape|using `' "$LOG_FILE" 2>/dev/null | head -n1 | cut -d: -f1 || true)
        if [ -n "$MATCH_LINE" ]; then
            START=$((MATCH_LINE > 3 ? MATCH_LINE - 3 : 1))
            END=$((MATCH_LINE + 3))
            echo -e "${YELLOW}Relevant log excerpt (around line $MATCH_LINE):${NC}"
            sed -n "${START},${END}p" "$LOG_FILE" | sed -n '1,200p'
        fi
    else
        APPLIED_STATUS="requested font '$REQUESTED_FONT' (appears applied)"
    fi
elif [ -f "$LOG_FILE" ] && [ -z "$REQUESTED_FONT" ]; then
    # No explicit requested font found in source; try to show any font names mentioned in log
    LOG_FONTS=$(/usr/bin/grep -iE "font|Font" "$LOG_FILE" 2>/dev/null | sed -n '1,6p' | tr '\n' ' ')
    if [ -n "$LOG_FONTS" ]; then
        APPLIED_STATUS="Fonts mentioned in log: ${LOG_FONTS}"
    fi
fi

# If pdffonts is available, run it to show which fonts are embedded in the final PDF
EMBEDDED_FONTS=""
PDF_PATH="$OUTPUT_DIR/$BASENAME.pdf"
if command -v pdffonts >/dev/null 2>&1 && [ -f "$PDF_PATH" ]; then
    # pdffonts output has a two-line header; collect font names from first column
    EMBEDDED_FONTS=$(/usr/bin/pdffonts "$PDF_PATH" 2>/dev/null | awk 'NR>2 {print $1}' | tr '\n' ',' | sed 's/,$//' || true)
    if [ -n "$EMBEDDED_FONTS" ]; then
        # Try to find a match between requested font and embedded font names (case-insensitive substring)
        MATCHING_EMBED=$(echo "$EMBEDDED_FONTS" | tr ',' '\n' | /usr/bin/awk -v rq="$REQUESTED_FONT" 'BEGIN{IGNORECASE=1} index(tolower($0), tolower(rq)) { print $0; exit }') || true
        if [ -n "$MATCHING_EMBED" ]; then
            APPLIED_STATUS="$APPLIED_STATUS; embedded font: ${MATCHING_EMBED}"
        else
            APPLIED_STATUS="$APPLIED_STATUS; embedded fonts: ${EMBEDDED_FONTS}"
        fi
    fi
fi

echo -e "${YELLOW}[3/3] Cleaning up auxiliary files in build directory...${NC}"
# By default remove auxiliary files produced inside the build directory.
# Set KEEP_BUILD_LOGS=1 in the environment if you want to keep the .log files for debugging.
if [ "${KEEP_BUILD_LOGS}" = "1" ]; then
    echo -e "${YELLOW}Keeping build logs in ${BUILD_DIR}/${NC} (KEEP_BUILD_LOGS=1)"
    rm -f "$BUILD_DIR"/*.{aux,out,fls,fdb_latexmk,synctex.gz,xdv} 2>/dev/null || true
else
    rm -f "$BUILD_DIR"/*.{aux,log,out,fls,fdb_latexmk,synctex.gz,xdv} 2>/dev/null || true
fi

# Also remove any stray auxiliary files that may have been written to the repository root
rm -f ./*.aux ./*.log ./*.out ./*.fls ./*.fdb_latexmk ./*.synctex.gz ./*.xdv 2>/dev/null || true

echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Success!${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "PDF: ${YELLOW}$OUTPUT_DIR/$BASENAME.pdf${NC}"
if [ -n "$APPLIED_STATUS" ]; then
    echo -e "Font info: ${YELLOW}$APPLIED_STATUS${NC}"
fi
echo -e "Build files: ${YELLOW}$BUILD_DIR/${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"

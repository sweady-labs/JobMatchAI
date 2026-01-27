# Makefile for LaTeX projects
# Makes compilation simple and organized

# Configuration
SRC_DIR := src
OUTPUT_DIR := output
BUILD_DIR := build
ENGINE := xelatex

# Determine CV source file from MD (if provided) or USER mapping.
# This is evaluated by make using variables passed on the command line.
# Map USER id to CV markdown file. Add your own user mappings here.
# Example: $(if $(filter $(USER),alex),src/cv_content/cv-alex-mueller.md,)
CV_SRC_FILE := $(if $(MD),$(MD),)
MAKE_TEMPLATE := $(if $(TEMPLATE),$(TEMPLATE),hipster)
OUT_BASE := $(if $(MD),$(basename $(notdir $(MD))),CV_$(USER)_$(MAKE_TEMPLATE))

# Python interpreter selection:
# - Honor an externally provided PYTHON variable if set (e.g. `make PYTHON=/usr/local/bin/python3`)
# - Otherwise auto-detect a working python3 by checking common names in PATH
#   and verifying the interpreter runs and is Python 3.x. Falls back to /usr/bin/python3
#   or plain `python3` as a last resort.
PYTHON ?= $(shell for c in python3 python; do p=$$(command -v $$c 2>/dev/null); if [ -n "$$p" ]; then $$p -c "import sys; sys.exit(0 if sys.version_info[0]>=3 else 1)" >/dev/null 2>&1 && { echo "$$p"; exit 0; }; fi; done; if [ -x /usr/bin/python3 ]; then echo /usr/bin/python3; else echo python3; fi)

# Find all .tex files in src/ and src/applications/
TEX_FILES := $(wildcard $(SRC_DIR)/*.tex) $(wildcard $(SRC_DIR)/applications/*.tex)
PDF_FILES := $(patsubst $(SRC_DIR)/%.tex,$(OUTPUT_DIR)/%.pdf,$(wildcard $(SRC_DIR)/*.tex)) \
			$(patsubst $(SRC_DIR)/applications/%.tex,$(OUTPUT_DIR)/%.pdf,$(wildcard $(SRC_DIR)/applications/*.tex))

# Colors
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

.PHONY: all clean help compile watch

.PHONY: md2pdf md2pdf-single


# Parse a markdown and compile to PDF in one step
# Usage: make md2pdf MD=path/to/file.md USER=alex TEMPLATE=modern YES=1

# md2pdf: process all markdowns in src/content/
# Usage: make md2pdf [USER=id] [TEMPLATE=modern|engineering] [YES=1] [DRY_RUN=1]
# - If DRY_RUN is set (non-empty), parser runs with --dry-run and no PDFs are produced.
md2pdf:
	@echo "Processing all markdown files in $(SRC_DIR)/content -> src/applications -> output"
	@echo "Using Python interpreter: $(PYTHON)"
	@PY_OPTS=""; \
	if [ -n "$(USER)" ]; then PY_OPTS="$$PY_OPTS --user $(USER)"; fi; \
	if [ -n "$(TEMPLATE)" ]; then PY_OPTS="$$PY_OPTS --template $(TEMPLATE)"; fi; \
	if [ -n "$(YES)" ]; then PY_OPTS="$$PY_OPTS --yes"; fi; \
	if [ -n "$(DRY_RUN)" ]; then PY_OPTS="$$PY_OPTS --dry-run"; fi; \
	if [ -n "$(FONT)" ]; then PY_OPTS="$$PY_OPTS --font=$(FONT)"; fi; \

	mkdir -p $(BUILD_DIR); \
	SUCCESS_FILE="$(BUILD_DIR)/md2pdf_success.list"; \
	FAIL_FILE="$(BUILD_DIR)/md2pdf_fail.list"; \
	: > "$$SUCCESS_FILE"; : > "$$FAIL_FILE"; \
	for md in $(SRC_DIR)/content/*.md; do \
		if [ ! -f "$$md" ]; then continue; fi; \
		echo "\n---\nParsing: $$md"; \
		USER="$(USER)" TEMPLATE="$(TEMPLATE)" YES="$(YES)" DRY_RUN="$(DRY_RUN)" FONT="$(FONT)" $(PYTHON) ./parse_md_to_tex.py --yes $$PY_OPTS "$$md" || { echo "Parser failed for $$md"; echo "$$md" >> "$$FAIL_FILE"; continue; }; \
		if [ -n "$(DRY_RUN)" ]; then echo "[dry-run] skipped compile for $$md"; echo "$$(basename $$md .md).pdf" >> "$$SUCCESS_FILE"; continue; fi; \
		BASE=$$(basename "$$md" .md); \
		TEX=src/applications/$$BASE.tex; \
		if [ -f "$$TEX" ]; then \
			echo "Compiling $$TEX"; \
			if $(MAKE) compile FILE="$$TEX"; then \
				echo "$$BASE.pdf" >> "$$SUCCESS_FILE"; \
			else \
				echo "$$md" >> "$$FAIL_FILE"; \
			fi; \
		else \
			echo "Warning: expected $$TEX not found after parsing $$md"; echo "$$md" >> "$$FAIL_FILE"; \
		fi; \
	done; \
	# Print summary (read from build/ files) in a single, silent bash invocation
	@bash -c 'printf "\n===== md2pdf summary =====\n"; \
	if [ -s "$(BUILD_DIR)/md2pdf_success.list" ]; then printf "Succeeded:\n"; while IFS= read -r f; do printf "  %s\n" "$$f"; done < "$(BUILD_DIR)/md2pdf_success.list"; else printf "No successful PDFs produced.\n"; fi; \
	if [ -s "$(BUILD_DIR)/md2pdf_fail.list" ]; then printf "Failed:\n"; while IFS= read -r f; do printf "  %s\n" "$$f"; done < "$(BUILD_DIR)/md2pdf_fail.list"; fi; \
	printf "========================\n"; rm -f "$(BUILD_DIR)/md2pdf_success.list" "$(BUILD_DIR)/md2pdf_fail.list"'


# md2pdf-single: process a single markdown file passed via MD=
# Usage: make md2pdf-single MD=src/content/job.md USER=alex TEMPLATE=modern YES=1
md2pdf-single:
	@if [ -z "$(MD)" ]; then \
		echo "Usage: make md2pdf-single MD=path/to/file.md [USER=id] [TEMPLATE=modern] [YES=1] [DRY_RUN=1]"; \
		exit 1; \
	fi
	@echo "Processing single markdown: $(MD)";
	@echo "Using Python interpreter: $(PYTHON)";
	@PY_OPTS=""; \
	if [ -n "$(USER)" ]; then PY_OPTS="$$PY_OPTS --user $(USER)"; fi; \
	if [ -n "$(TEMPLATE)" ]; then PY_OPTS="$$PY_OPTS --template $(TEMPLATE)"; fi; \
	if [ -n "$(YES)" ]; then PY_OPTS="$$PY_OPTS --yes"; fi; \
	if [ -n "$(DRY_RUN)" ]; then PY_OPTS="$$PY_OPTS --dry-run"; fi; \
	if [ -n "$(FONT)" ]; then PY_OPTS="$$PY_OPTS --font=$(FONT)"; fi; \
	USER="$(USER)" TEMPLATE="$(TEMPLATE)" YES="$(YES)" DRY_RUN="$(DRY_RUN)" FONT="$(FONT)" $(PYTHON) ./parse_md_to_tex.py --yes $$PY_OPTS "$(MD)" || { echo "Parser failed for $(MD)"; exit 3; }; \
	if [ -n "$(DRY_RUN)" ]; then echo "[dry-run] skipped compile for $(MD)"; exit 0; fi; \
	BASE=$$(basename "$(MD)" .md); \
	TEX=src/applications/$$BASE.tex; \
	if [ -f "$$TEX" ]; then \
		echo "Compiling $$TEX"; \
		$(MAKE) compile FILE="$$TEX"; \
	else \
		echo "Warning: expected $$TEX not found after parsing $(MD)"; exit 4; \
	fi


# Default target - compile all .tex files
all: $(PDF_FILES)
	@echo "$(GREEN)✓ All documents compiled successfully$(NC)"

# Compile a single file
# Usage: make compile FILE=main.tex
compile:
	@if [ -z "$(FILE)" ]; then \
		echo "$(YELLOW)Usage: make compile FILE=yourfile.tex$(NC)"; \
		exit 1; \
	fi
	@bash ./compile.sh $(FILE) $(ENGINE)

# Pattern rule: compile any .tex file from src/ or src/applications/ to output/
$(OUTPUT_DIR)/%.pdf: $(SRC_DIR)/%.tex
	@bash ./compile.sh $< $(ENGINE)

$(OUTPUT_DIR)/%.pdf: $(SRC_DIR)/applications/%.tex
	@bash ./compile.sh $< $(ENGINE)

# Clean build directory
clean:
	@echo "$(YELLOW)Cleaning build files...$(NC)"
	@rm -rf $(BUILD_DIR)/*
	@rm -f *.aux *.log *.out *.fls *.fdb_latexmk *.synctex.gz *.xdv
	@echo "$(GREEN)✓ Build directory cleaned$(NC)"

# Deep clean - removes output PDFs too
distclean: clean
	@echo "$(YELLOW)Removing output PDFs...$(NC)"
	@rm -rf $(OUTPUT_DIR)/*
	@echo "$(GREEN)✓ Everything cleaned$(NC)"

# Watch and auto-compile (requires fswatch on macOS)
# Install: brew install fswatch
watch:
	@if [ -z "$(FILE)" ]; then \
		echo "$(YELLOW)Usage: make watch FILE=yourfile.tex$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Watching $(FILE) for changes... (Ctrl+C to stop)$(NC)"
	@fswatch -o $(SRC_DIR)/$(FILE) | xargs -n1 -I{} make compile FILE=$(FILE)

# Help message
help:
	@echo "$(GREEN)═══════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)  LaTeX Makefile - Available Commands$(NC)"
	@echo "$(GREEN)═══════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "  $(YELLOW)make$(NC)              - Compile all .tex files in src/"
	@echo "  $(YELLOW)make all$(NC)          - Same as above"
	@echo "  $(YELLOW)make compile FILE=x.tex$(NC) - Compile a specific file"
	@echo "  $(YELLOW)make clean$(NC)        - Remove build files"
	@echo "  $(YELLOW)make distclean$(NC)    - Remove build files AND PDFs"
	@echo "  $(YELLOW)make watch FILE=x.tex$(NC)   - Auto-compile on file change"
	@echo "  $(YELLOW)make md2pdf USER=alex TEMPLATE=modern [FONT=\"Inter\"]$(NC) - Parse markdown(s) and compile to PDF (optional FONT)"
	@echo "  $(YELLOW)make cv USER=alex [TEMPLATE=hipster|luxsleek] [FONT=\"Inter\"]$(NC) - Generate CV from markdown (optional FONT)"
	@echo "  $(YELLOW)make help$(NC)         - Show this help message"
	@echo ""
	@echo "$(GREEN)Examples:$(NC)"
	@echo "  make compile FILE=main.tex"
	@echo "  make compile FILE=cv_modern.tex ENGINE=pdflatex"
	@echo "  make watch FILE=main.tex"
	@echo "  make md2pdf MD=candidates/alex/0_inbox-jobs/2025-10-22/job.md USER=alex TEMPLATE=modern"
	@echo "  make md2pdf MD=src/content/example.md USER=alex TEMPLATE=modern FONT=\"Lato\"  # Parse and force font"
	@echo "  make cv USER=alex                  # Generate with default hipster template"
	@echo "  make cv USER=alex TEMPLATE=hipster # Generate with hipster template"
	@echo "  make cv USER=alex TEMPLATE=luxsleek # Generate with luxsleek template"
	@echo "  make cv USER=alex TEMPLATE=luxsleek FONT=\"Inter\" # Generate CV with luxsleek and custom font"
	@echo "  $(YELLOW)make cv MD=path/to/file.md USER=alex TEMPLATE=luxsleek FONT=\"Inter\"$(NC) - Generate CV from a specific markdown file using the USER profile"
	@echo ""
	@echo "$(GREEN)═══════════════════════════════════════════════$(NC)"

# Generate CV from profile markdown (hipster template)
# Usage: make cv USER=<your-user-id> [TEMPLATE=hipster|luxsleek] [FONT="Source Sans 3"]
.PHONY: cv
cv:
	@if [ -z "$(USER)" ]; then \
		echo "Usage: make cv USER=<your-user-id> [TEMPLATE=hipster|luxsleek] [FONT=\"Source Sans 3\"]"; \
		exit 1; \
	fi
	TEMPLATE_NAME="$${TEMPLATE:-hipster}"; \
	echo "$(GREEN)Generating CV for $(USER) with $$TEMPLATE_NAME template...$(NC)"; \
	# CV file chosen from make variable CV_SRC_FILE (computed from MD or USER).
	if [ ! -f "$(CV_SRC_FILE)" ]; then \
		echo "Error: CV file not found: $(CV_SRC_FILE)"; \
		exit 1; \
	fi; \
	echo "Using CV content: $(CV_SRC_FILE)"; \
	# Call the parser directly (avoid building/`eval`-ing a complex command string).
	if [ -n "$(FONT)" ]; then \
		echo "CMD: $(PYTHON) ./parse_cv_universal.py \"$(CV_SRC_FILE)\" --user $(USER) --template \"$(MAKE_TEMPLATE)\" --font \"$(FONT)\""; \
		$(PYTHON) ./parse_cv_universal.py "$(CV_SRC_FILE)" --user $(USER) --template "$(MAKE_TEMPLATE)" --font "$(FONT)" || { echo "Parser failed"; exit 1; }; \
		echo "Using custom font: $(FONT)"; \
	else \
		echo "CMD: $(PYTHON) ./parse_cv_universal.py \"$(CV_SRC_FILE)\" --user $(USER) --template \"$(MAKE_TEMPLATE)\""; \
		$(PYTHON) ./parse_cv_universal.py "$(CV_SRC_FILE)" --user $(USER) --template "$(MAKE_TEMPLATE)" || { echo "Parser failed"; exit 1; }; \
	fi; \
	TEX_FILE="src/applications/CV_$(USER)_$(MAKE_TEMPLATE).tex"; \
	# If MD was provided, rename the generated TeX to match the MD basename so PDF and tex share a name.
	GENERATED_TEX="src/applications/CV_$(USER)_$(MAKE_TEMPLATE).tex"; \
	TARGET_TEX="src/applications/$(OUT_BASE).tex"; \
	if [ -n "$(MD)" ]; then \
		if [ -f $$GENERATED_TEX ]; then mv -f $$GENERATED_TEX $$TARGET_TEX; else echo "Error: Expected generated TeX not found: $$GENERATED_TEX"; exit 1; fi; \
	else \
		TARGET_TEX=$$GENERATED_TEX; \
	fi; \
	if [ -f "$$TARGET_TEX" ]; then \
		echo "Compiling CV..."; \
		$(MAKE) compile FILE="$$TARGET_TEX"; \
		echo "$(GREEN)✓ CV generated successfully: output/$(OUT_BASE).pdf$(NC)"; \
	else \
		echo "Error: Expected TeX file not found: $$TARGET_TEX"; \
		exit 1; \
	fi

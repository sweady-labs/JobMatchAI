## Top-level Makefile proxy
# Delegates common LaTeX-related make targets to the 3_latex/Makefile so you
# can run `make ...` from the repository root.

.PHONY: all md2pdf md2pdf-single md2pdf-single compile clean distclean watch help cv

# Default: build everything in 3_latex
all:
	$(MAKE) -C 3_latex all

# Pass-through targets. Forward commonly used variables so you can call:
#   make md2pdf USER=alex TEMPLATE=modern
md2pdf:
	$(MAKE) -C 3_latex md2pdf USER=$(USER) TEMPLATE=$(TEMPLATE) YES=$(YES) DRY_RUN=$(DRY_RUN) FONT=$(FONT)

md2pdf-single:
	$(MAKE) -C 3_latex md2pdf-single MD=$(MD) USER=$(USER) TEMPLATE=$(TEMPLATE) YES=$(YES) DRY_RUN=$(DRY_RUN) FONT=$(FONT)

compile:
	$(MAKE) -C 3_latex compile FILE=$(FILE)

clean:
	$(MAKE) -C 3_latex clean

distclean:
	$(MAKE) -C 3_latex distclean

watch:
	$(MAKE) -C 3_latex watch FILE=$(FILE)

help:
	$(MAKE) -C 3_latex help

cv:
	$(MAKE) -C 3_latex cv USER=$(USER)

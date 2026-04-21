# =============================================================================
# static/questa/Makefile — Questa flow entry point
# =============================================================================
# Include chain:
#   static/questa/Makefile
#       -> $WORKAREA/toolbase/questa/tool.mk
#             defines: compile / elab / all targets via ace_shell
#
# Usage (from this directory, inside ace_shell --tool questa):
#   make compile  FILELIST=/path/to/filelist.json
#   make elab     FILELIST=/path/to/filelist.json
#   make all      FILELIST=/path/to/filelist.json
# =============================================================================

include ${WORKAREA}/toolbase/questa/tool.mk

.PHONY: help

help:
	@echo ""
	@echo "Questa flow targets (must supply FILELIST=<path>):"
	@echo ""
	@echo "  compile   — run vlog per IP (compile stage)"
	@echo "  elab      — run vopt elaboration"
	@echo "  all       — compile + elab in one shot"
	@echo ""
	@echo "Examples:"
	@echo "  make all     FILELIST=\$$WORKAREA/static/questa/filelist.json"
	@echo "  make compile FILELIST=\$$WORKAREA/static/questa/filelist.json"
	@echo ""
	@echo "Flow cfg: \$$WORKAREA/static/questa/flow.ace  (auto-used)"
	@echo ""

# =============================================================================
# static/vcs/Makefile — VCS flow entry point
# =============================================================================
# This Makefile is the entry point for VCS simulation flows in the
# static activity area.  It delegates all real work to the versioned
# tool rules in toolbase/vcs/tool.mk.
#
# The include chain:
#   static/vcs/Makefile
#       -> $WORKAREA/toolbase/vcs/tool.mk      (active workspace copy)
#             defines: compile / elab / all targets via ace_shell
#
# Usage (from this directory, inside ace_shell --tool vcs):
#   make compile FILELIST=/path/to/filelist.json
#   make elab    FILELIST=/path/to/filelist.json
#   make all     FILELIST=/path/to/filelist.json
#
# Optional overrides:
#   FLOW_CFG=/path/to/flow.ace   — use a custom flow config
#   WORKAREA=/path/to/workarea   — set if not already in environment
# =============================================================================

include ${WORKAREA}/toolbase/vcs/tool.mk

.PHONY: help

help:
	@echo ""
	@echo "VCS flow targets (must supply FILELIST=<path>):"
	@echo ""
	@echo "  compile   — run vlogan per IP"
	@echo "  elab      — run vcs elaboration"
	@echo "  all       — compile + elab in one shot"
	@echo ""
	@echo "Examples:"
	@echo "  make all     FILELIST=\$$WORKAREA/static/vcs/filelist.json"
	@echo "  make compile FILELIST=\$$WORKAREA/static/vcs/filelist.json"
	@echo ""
	@echo "Flow cfg is auto-discovered from:"
	@echo "  \$$WORKAREA/<activity>/vcs/flow.ace  (activity from tool.ace [params])"
	@echo ""
	@echo "Override flow cfg:"
	@echo "  make all FILELIST=... FLOW_CFG=\$$WORKAREA/static/vcs/flow.ace"
	@echo ""

# =============================================================================
# static/xcelium/Makefile — Xcelium simulation entry point
# =============================================================================
# Usage:
#   make compile  FILELIST=<path>   Compile all IPs (writes cds.lib)
#   make elab     FILELIST=<path>   Elaborate top module
#   make all      FILELIST=<path>   compile + elab
#
# DUT is auto-read from the FILELIST JSON — no need to supply it manually.
# XCELIUM_FLOW_CFG defaults to this directory's flow.ace.
#
# Must be run inside ace_shell --tool xcelium (tool.mk handles this).
# =============================================================================

WORKAREA ?= $(realpath $(dir $(abspath $(lastword $(MAKEFILE_LIST))))/../..)

include $(WORKAREA)/toolbase/xcelium/tool.mk

.PHONY: help

help:
	@echo "Xcelium simulation flow targets:"
	@echo "  compile  FILELIST=<path>  — compile all IPs (writes cds.lib)"
	@echo "  elab     FILELIST=<path>  — elaborate top module"
	@echo "  all      FILELIST=<path>  — compile + elab"
	@echo ""
	@echo "  DUT is auto-read from the FILELIST JSON."
	@echo "  XCELIUM_FLOW_CFG defaults to: $(WORKAREA)/static/xcelium/flow.ace"
	@echo ""
	@echo "Example (from demo_tasks.mk):"
	@echo "  make bypass_pnr_reg_fp__xcelium_all"

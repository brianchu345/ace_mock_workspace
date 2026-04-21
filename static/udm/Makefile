# =============================================================================
# static/udm/Makefile — UDM flow entry point
# =============================================================================
# Usage:
#   make udm_vcs_compile  FILELIST=<json>  FLAT_FILELIST=<sim.f>
#   make udm_vcs_elab     FILELIST=<json>  FLAT_FILELIST=<sim.f>
#   make udm_udm_compile  FILELIST=<json>  FLAT_FILELIST=<sim.f>
#   make all              FILELIST=<json>  FLAT_FILELIST=<sim.f>
#
# DUT is auto-read from the FILELIST JSON.
# FLAT_FILELIST defaults to $WORKAREA/input_filelist/$(DUT).sim.f
# UDM_VCS_FLOW_CFG defaults to this directory's flow.ace.
# =============================================================================

WORKAREA ?= $(realpath $(dir $(abspath $(lastword $(MAKEFILE_LIST))))/../..)

include $(WORKAREA)/toolbase/udm_rtl_reader/tool.mk

.PHONY: help

help:
	@echo "UDM flow targets:"
	@echo "  udm_vcs_compile  FILELIST=<json>  — VCS compile with UDM forced defines"
	@echo "  udm_vcs_elab     FILELIST=<json>  — VCS elab with UDM forced defines"
	@echo "  udm_udm_compile  FILELIST=<json>  — UDM RTL reader (unified_defines.f + udm_shell_cth)"
	@echo "  all              FILELIST=<json>  — all three stages in order"
	@echo ""
	@echo "  FLAT_FILELIST defaults to: \$$WORKAREA/input_filelist/\$$DUT.sim.f"
	@echo "  UDM_VCS_FLOW_CFG defaults to: $(WORKAREA)/static/udm/flow.ace"
	@echo ""
	@echo "Example (from demo_tasks.mk):"
	@echo "  make bypass_pnr_reg_fp__udm_all"

# =============================================================================
# Makefile — workspace entry point
# =============================================================================
# Assumes the user is already inside the ace environment (ace_shell entered).
#
# Usage:
#   make <dut>__vcs_compile
#   make <dut>__vcs_elab
#   make <dut>__vcs_all
# =============================================================================

WORKAREA ?= /nfs/site/disks/da_scratch_1/users/chubrian/chipstack_wkspace/ace_demo

include $(WORKAREA)/baseline_tools/flows/vcs/vcs.Makefile

.PHONY: help
help:
	@echo "Usage: make <dut>__vcs_compile | <dut>__vcs_elab | <dut>__vcs_all"
	@echo ""
	@echo "  DUT is extracted from the target name and exported so that"
	@echo "  vcs_flow.cfg resolves: [includes] ../../../cfg/\$$DUT.design.cfg"
	@echo ""
	@echo "  Flow cfg is auto-discovered:"
	@echo "    1. \$$WORKAREA/user_override/vcs/vcs_flow_override.cfg  (if exists)"
	@echo "    2. \$$WORKAREA/baseline_tools/flows/vcs/vcs_flow.cfg    (fallback)"
	@echo ""
	@echo "Examples:"
	@echo "  make bypass_pnr_reg_fp__vcs_compile"
	@echo "  make bypass_pnr_reg_fp__vcs_all"

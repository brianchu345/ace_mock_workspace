# =============================================================================
# static/simwrapper/Makefile — simwrapper (sf_sim_model_gen) flow entry point
# =============================================================================
# ACE equivalent of the cheetah pattern:
#   export FLOW_ROOT = ${WORKAREA}/baseline_tools/simwrapper
#   include ${FLOW_ROOT}/Makefile.simwrapper
#
# Here tool.mk replaces Makefile.simwrapper, substituting:
#   ARC_CMD          -> ace_shell --tool simwrapper -c
#   CTH_SIM_MODEL_GEN -> resolved sf_sim_model_gen.py via ace_query
#   reponame         -> REPO_NAME make variable (defaults to DUT)
#
# Usage (inside ace_setup):
#   make simwrapper_rtl_collect_check  DUT=<dut>  [FLAT_FILELIST=<path>]  [REPO_NAME=<name>]
#   make simwrapper_check              DUT=<dut>  [REPO_NAME=<name>]      [UDM_DB=<path>]
#   make simwrapper_sim                DUT=<dut>
#   make all                           DUT=<dut>  [FLAT_FILELIST=<path>]  [REPO_NAME=<name>]
# =============================================================================

WORKAREA ?= $(realpath $(dir $(abspath $(lastword $(MAKEFILE_LIST))))/../..)

include $(WORKAREA)/toolbase/simwrapper/tool.mk

.PHONY: help

help:
	@echo ""
	@echo "simwrapper (sf_sim_model_gen) flow targets:"
	@echo ""
	@echo "  simwrapper_rtl_collect_check  DUT=<dut>  — collect RTL and verify model"
	@echo "  simwrapper_check              DUT=<dut>  — check against UDM DB (needs swfrontcheck output)"
	@echo "  simwrapper_sim                DUT=<dut>  — run sim-only model generation"
	@echo "  all                           DUT=<dut>  — rtl_collect_check + sim"
	@echo ""
	@echo "Optional variables:"
	@echo "  REPO_NAME=<name>       — repository/IP name for --ip-name (defaults to DUT)"
	@echo "  FLAT_FILELIST=<path>   — flat .sim.f (defaults to output/<DUT>/flm/flat/<DUT>.sim.f)"
	@echo "  UDM_DB=<path>          — .udm file for simwrapper_check"
	@echo ""
	@echo "Example (from demo_tasks.mk):"
	@echo "  make bypass_pnr_reg_fp__simwrapper_rtl_collect_check"
	@echo "  make bypass_pnr_reg_fp__simwrapper_all"
	@echo ""

# =============================================================================
# Makefile — workspace entry point
# =============================================================================
# After sourcing ace_setup, run any target as:
#   make <dut>__<tool>_<step>
#
# The DUT name is extracted from the target and passed down to the flow.
# =============================================================================
include $(WORKAREA)/toolbase/design_fe.mk

.PHONY: help
help:
	@echo ""
	@echo "Usage: make <dut>__<tool>_<step>"
	@echo ""
	@echo "  VCS (compile + elaborate):"
	@echo "    make <dut>__vcs_compile"
	@echo "    make <dut>__vcs_elab"
	@echo "    make <dut>__vcs_all"
	@echo ""
	@echo "  Questa:"
	@echo "    make <dut>__questa_compile"
	@echo "    make <dut>__questa_elab"
	@echo "    make <dut>__questa_all"
	@echo ""
	@echo "  Xcelium:"
	@echo "    make <dut>__xcelium_compile"
	@echo "    make <dut>__xcelium_elab"
	@echo "    make <dut>__xcelium_all"
	@echo ""
	@echo "  UDM RTL Reader (VCS compile + elab + UDM compile):"
	@echo "    make <dut>__udm_vcs_compile"
	@echo "    make <dut>__udm_vcs_elab"
	@echo "    make <dut>__udm_udm_compile"
	@echo "    make <dut>__udm_all"
	@echo ""
	@echo "  VC Lint:"
	@echo "    make <dut>__vc_lint_compile"
	@echo "    make <dut>__vc_lint_run"
	@echo "    make <dut>__vc_lint_all"
	@echo ""
	@echo "  DI RDL-to-IPXACT:"
	@echo "    make <dut>__rdl2ipxact"
	@echo ""
	@echo "  All flows (vcs + questa + xcelium + udm + rdl2ipxact):"
	@echo "    make <dut>__all"
	@echo ""
	@echo "Examples:"
	@echo "  make bypass_pnr_reg_fp__vcs_all"
	@echo "  make bypass_pnr_reg_fp__rdl2ipxact"
	@echo "  make bypass_pnr_reg_fp__all"
	@echo ""

include $(WORKAREA)/demo_tasks.mk

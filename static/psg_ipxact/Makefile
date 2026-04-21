# =============================================================================
# static/psg_ipxact/Makefile — DI rdl2ipxact flow entry point
# =============================================================================
# Usage (from ace_mock_workspace root, after source ace_setup):
#   make -C static/psg_ipxact rdl2ipxact CELLS=bypass_pnr_reg_fp
#
# Or from the top-level Makefile via a generated target.
# =============================================================================

include ${WORKAREA}/toolbase/altera_design_intent/tool.mk

.PHONY: help

help:
	@echo ""
	@echo "DI rdl2ipxact targets (must supply CELLS=<cell_name>):"
	@echo ""
	@echo "  rdl2ipxact   — compile RDL and generate IPXACT XML"
	@echo "  all          — same as rdl2ipxact"
	@echo ""
	@echo "Examples:"
	@echo "  make rdl2ipxact CELLS=bypass_pnr_reg_fp"
	@echo ""

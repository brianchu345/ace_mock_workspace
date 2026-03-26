# =============================================================================
# vc_cdc.Makefile — VC-CDC run pattern rules
# =============================================================================
# Included by the workspace Makefile. Assumes WORKAREA is already defined.
#
# Usage (from workspace root):
#   make <dut>__vc_cdc_run
#
# Flow cfg is auto-discovered (no --flow-cfg needed):
#   1. $$WORKAREA/user_override/vc_cdc/vc_cdc_flow_override.cfg  (if exists)
#   2. $$WORKAREA/baseline_tools/flows/vc_cdc/vc_cdc_flow.cfg    (fallback)
#
# DUT and WORKAREA are exported so the wrapper and config parser see them.
# =============================================================================

PYTHON  ?= /usr/intel/pkgs/python3/3.12.3/bin/python3
WRAPPER := $(WORKAREA)/???/vc_cdc/vc_cdc_wrapper.py

FORCE:
.PHONY: FORCE

%__vc_cdc_run: FORCE
	export DUT=$* WORKAREA=$(WORKAREA) && \
	$(PYTHON) $(WRAPPER) \
	    --filelist $(WORKAREA)/output/$*_all_filelist.json \
	    --step run

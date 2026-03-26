# =============================================================================
# vcs.mk — VCS compile / elaborate pattern rules
# =============================================================================
# Included by the workspace Makefile. Assumes WORKAREA is already defined.
#
# Usage (from workspace root):
#   make <dut>__vcs_compile
#   make <dut>__vcs_elab
#   make <dut>__vcs_all
#
# Flow cfg is auto-discovered by the wrapper (no --flow-cfg needed):
#   1. $$WORKAREA/user_override/vcs/vcs_flow_override.cfg  (if exists)
#   2. $$WORKAREA/baseline_tools/flows/vcs/vcs_flow.cfg    (fallback)
#
# Override FILELIST_BASE if your output tree differs:
#   make bypass_pnr_reg_fp__vcs_compile FILELIST_BASE=/other/output
# =============================================================================

PYTHON        ?= /usr/intel/pkgs/python3/3.12.3/bin/python3
WRAPPER       := /nfs/site/disks/da_scratch_1/users/chubrian/chipstack_wkspace/playground/new_system/vcs_flow_scripts/vcs_wrapper.py
FILELIST_BASE := /nfs/site/disks/da_scratch_1/users/chubrian/chipstack_wkspace/ace_demo/input_filelist

# FORCE: prerequisite that is always out-of-date, making pattern rules
# always execute regardless of whether a matching file exists on disk.
# (.PHONY cannot be applied directly to pattern rules in GNU Make.)
FORCE:
.PHONY: FORCE

# ---------------------------------------------------------------------------
# Pattern rules — $* is the DUT stem (everything before __vcs_<step>)
# DUT and WORKAREA are exported so the wrapper and ConfigParser see them.
# ---------------------------------------------------------------------------
%__vcs_compile: FORCE
	export DUT=$* WORKAREA=$(WORKAREA) && \
	$(PYTHON) $(WRAPPER) \
	    --filelist $(FILELIST_BASE)/$*_sim_filelist.json \
	    --step compile

%__vcs_elab: FORCE
	export DUT=$* WORKAREA=$(WORKAREA) && \
	$(PYTHON) $(WRAPPER) \
	    --filelist $(FILELIST_BASE)/$*_sim_filelist.json \
	    --step elab

%__vcs_all: FORCE
	export DUT=$* WORKAREA=$(WORKAREA) && \
	$(PYTHON) $(WRAPPER) \
	    --filelist $(FILELIST_BASE)/$*_sim_filelist.json \
	    --step all

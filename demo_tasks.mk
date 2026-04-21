# =============================================================================
# demo_tasks.mk — DUT-target fanout to static flow Makefiles
# =============================================================================

_FILELIST = $(WORKAREA)/input_filelist/$*_sim_filelist.json

%__vcs_compile:
	$(MAKE) -C $(WORKAREA)/static/vcs compile DUT=$* FILELIST=$(_FILELIST)

%__vcs_elab:
	$(MAKE) -C $(WORKAREA)/static/vcs elab DUT=$* FILELIST=$(_FILELIST)

%__vcs_all:
	$(MAKE) -C $(WORKAREA)/static/vcs all DUT=$* FILELIST=$(_FILELIST)

%__questa_compile:
	$(MAKE) -C $(WORKAREA)/static/questa compile DUT=$* FILELIST=$(_FILELIST)

%__questa_elab:
	$(MAKE) -C $(WORKAREA)/static/questa elab DUT=$* FILELIST=$(_FILELIST)

%__questa_all:
	$(MAKE) -C $(WORKAREA)/static/questa all DUT=$* FILELIST=$(_FILELIST)

%__xcelium_compile:
	$(MAKE) -C $(WORKAREA)/static/xcelium compile DUT=$* FILELIST=$(_FILELIST)

%__xcelium_elab:
	$(MAKE) -C $(WORKAREA)/static/xcelium elab DUT=$* FILELIST=$(_FILELIST)

%__xcelium_all:
	$(MAKE) -C $(WORKAREA)/static/xcelium all DUT=$* FILELIST=$(_FILELIST)

%__udm_vcs_compile:
	$(MAKE) -C $(WORKAREA)/static/udm udm_vcs_compile DUT=$* FILELIST=$(_FILELIST)

%__udm_vcs_elab:
	$(MAKE) -C $(WORKAREA)/static/udm udm_vcs_elab DUT=$* FILELIST=$(_FILELIST)

%__udm_udm_compile:
	$(MAKE) -C $(WORKAREA)/static/udm udm_udm_compile DUT=$* FILELIST=$(_FILELIST)

%__udm_all:
	$(MAKE) -C $(WORKAREA)/static/udm all DUT=$* FILELIST=$(_FILELIST)

%__psg_ipxact_all:
	$(MAKE) -C $(WORKAREA)/static/psg_ipxact all CELLS=$*

# Backward-compatible alias used in help text.
%__rdl2ipxact: %__psg_ipxact_all

%__all:
	$(MAKE) -C $(WORKAREA)/static/vcs all DUT=$* FILELIST=$(_FILELIST)
	$(MAKE) -C $(WORKAREA)/static/questa all DUT=$* FILELIST=$(_FILELIST)
	$(MAKE) -C $(WORKAREA)/static/xcelium all DUT=$* FILELIST=$(_FILELIST)
	$(MAKE) -C $(WORKAREA)/static/udm all DUT=$* FILELIST=$(_FILELIST)
	$(MAKE) -C $(WORKAREA)/static/psg_ipxact all CELLS=$*

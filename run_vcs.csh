#!/bin/tcsh -f

set WORKAREA  = /nfs/site/disks/da_scratch_1/users/chubrian/chipstack_wkspace/ace_demo
set ACE_SHELL = /nfs/site/disks/da_scratch_1/users/chubrian/applications.design-automation.altera-cb-env.config/bin/ace_shell
set PYTHON    = /usr/intel/pkgs/python3/3.12.3/bin/python3
set WRAPPER   = /nfs/site/disks/da_scratch_1/users/chubrian/chipstack_wkspace/playground/new_system/vcs_flow_scripts/vcs_wrapper.py
set TOOL_CFG  = $WORKAREA/baseline_tools/tools/vcs/vcs_tool.cfg
set FLOW_CFG  = $WORKAREA/user_override/vcs/vcs_flow.cfg
set FILELIST  = /nfs/site/disks/da_scratch_1/users/chubrian/chipstack_wkspace/playground/demo_bypass_pnr_reg/output/bypass_pnr_reg_fp/genfilelist/json/bypass_pnr_reg_fp_sim_filelist.json

set CMD = "$PYTHON $WRAPPER --tool-cfg $TOOL_CFG --flow-cfg $FLOW_CFG --filelist $FILELIST --step all"

$ACE_SHELL --shell /bin/tcsh -f $WORKAREA/tool.cfg -c "$CMD"

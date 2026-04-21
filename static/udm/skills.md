# UDM Flow — Testing & Skills Reference

## Architecture

```
demo_tasks.mk
  %__udm_vcs_compile / %__udm_vcs_elab / %__udm_udm_compile / %__udm_all
    → cd static/udm; make <target> DUT=<dut> FILELIST=<json> FLAT_FILELIST=<sim.f>
      → static/udm/Makefile
        → includes ace_toolbase/udm_rtl_reader/tool.mk
          │
          ├─ udm_vcs_compile / udm_vcs_elab
          │    ace_shell --tool vcs -c 'python vcs_wrapper.py --flow-cfg udm_vcs_flow.cfg ...'
          │        VCS compile/elab with UDM forced defines
          │        Artifacts → static/vcs/output/udm_vcs_work/
          │
          └─ udm_udm_compile
               ace_shell --tool udm_rtl_reader -c 'python udm_wrapper.py ...'
                   1. Creates unified_defines.f (software_defines.sv + flat .sim.f)
                   2. udm_shell_cth udm_rtl_reader.py -t <top> -f unified_defines.f --print_hier
                   Artifacts → static/udm/output/udm_compile/<dut>/
```

**Key files:**

| File | Purpose |
|------|---------|
| `ace_toolbase/udm_rtl_reader/tool.cfg` | DEVDATA env (DEVDATA_TOOLS_ROOT, PATH, LD_LIBRARY_PATH) |
| `ace_toolbase/udm_rtl_reader/tool.mk` | Make targets: udm_vcs_compile/elab/udm_compile/all |
| `static/udm/udm_vcs_flow.cfg` | Inherits vcs_flow.cfg + prepends UDM forced defines |
| `udm_flow_scripts/udm_wrapper.py` | UDM compile driver (unified_defines.f + udm_shell_cth) |
| `udm_flow_scripts/udm_rtl_reader.py` | Verific-based UDM RTL reader (copied from /p/cth/cad/flm/) |
| `udm_flow_scripts/software_defines.sv` | UDM macro header (DA_ONLY_QUARTUS_UDM defines) |

**Forced UDM defines (from udm_genfilelist.py):**
```
+define+QUARTUS+QUARTUS_ARCS+SW_SYNTHESIZABLE_ONLY+ALTR_HPS_INTEL_MACROS_OFF
       +FUNCTIONAL+functional+SVA_OFF+INTEL_SVA_OFF+FC_IO96_COMPILE
       +TSMC_MEMORY_BEH+TSMC_PWR_AWARE
```

---

## Inputs

| Input | Description | Default |
|-------|-------------|---------|
| `FILELIST` | Hierarchical JSON filelist | from `demo_tasks.mk` |
| `FLAT_FILELIST` | Flat resolved `.sim.f` for UDM RTL reader | `$WORKAREA/input_filelist/$DUT.sim.f` |

---

## Setup — Fresh Shell

```bash
cd /nfs/site/disks/da_scratch_1/users/chubrian/ace_wkspace/ace_mock_workspace
/nfs/site/disks/da_scratch_1/users/chubrian/ace_wkspace/ace_config/0.1.0/bin/ace_setup

# Verify UDM tool env resolves
ace_query --tool udm_rtl_reader ENVS DEVDATA_TOOLS_ROOT --resolve
ace_query --tool udm_rtl_reader ENVS DEVDATA_BIN_ROOT   --resolve
```

---

## Running via demo_tasks.mk (recommended)

```bash
cd $WORKAREA

# VCS compile with UDM defines only
make bypass_pnr_reg_fp__udm_vcs_compile

# VCS compile + elab
make bypass_pnr_reg_fp__udm_vcs_elab

# UDM RTL reader compile only
make bypass_pnr_reg_fp__udm_udm_compile

# All three stages
make bypass_pnr_reg_fp__udm_all
```

---

## Running via Makefile directly

```bash
WORKAREA=/nfs/site/disks/da_scratch_1/users/chubrian/ace_wkspace/ace_mock_workspace
FILELIST=$WORKAREA/output/bypass_pnr_reg_fp/demo_genfilelist/json/bypass_pnr_reg_fp_sim_filelist.json
FLAT=$WORKAREA/input_filelist/bypass_pnr_reg_fp.sim.f

cd $WORKAREA/static/udm

make udm_vcs_compile    DUT=bypass_pnr_reg_fp FILELIST=$FILELIST FLAT_FILELIST=$FLAT
make udm_vcs_elab       DUT=bypass_pnr_reg_fp FILELIST=$FILELIST FLAT_FILELIST=$FLAT
make udm_udm_compile    DUT=bypass_pnr_reg_fp FILELIST=$FILELIST FLAT_FILELIST=$FLAT
```

---

## What udm_udm_compile does step by step

1. **Reads top module** from the JSON filelist (`top` field).
2. **Creates output dir**: `static/udm/output/udm_compile/<dut>/`
3. **Copies `software_defines.sv`** from `udm_flow_scripts/` to output dir.
4. **Creates `<dut>.unified_defines.f`**:
   - Line 1: `software_defines.sv` (sets `DA_ONLY_QUARTUS_UDM` context for macro guard)
   - Rest: contents of the flat `.sim.f` filelist verbatim
5. **Checks for exclude file**: `$WORKAREA/output/<dut>/flm/udm/<dut>.exclude`
6. **Runs** `udm_shell_cth udm_rtl_reader.py -t <top> -f <unified_defines.f> --print_hier [-e <exclude>]`
   - `udm_shell_cth` activates verific Python bindings from `$DEVDATA_BIN_ROOT`
   - Produces `<dut>.udm` database + `<dut>.filelist_rtl_hierarchy.json`

---

## Difference from regular VCS flow

| Aspect | Regular VCS | UDM VCS |
|--------|-------------|---------|
| Flow cfg | `vcs_flow.cfg` | `udm_vcs_flow.cfg` (inherits + adds defines) |
| Defines | IP-type macros only | + UDM Quartus forced defines |
| Work dir | `vcs_output/vcs_work` | `vcs_output/udm_vcs_work` |
| After elab | done | → udm_udm_compile stage |

---

## Bumping devdata version

Edit `ace_toolbase/udm_rtl_reader/tool.cfg`:
```ini
[params]
DEVDATA_REL = devdata_tools/py3/26.1.1/796   # change this
```
All downstream paths (DEVDATA_TOOLS_ROOT, DEVDATA_BIN_ROOT) resolve automatically.

---

## Common failures

| Error | Cause | Fix |
|-------|-------|-----|
| `udm_shell_cth: command not found` | Not inside `ace_shell --tool udm_rtl_reader` | Run `ace_setup` and use correct shell |
| `Flat filelist not found` | `FLAT_FILELIST` doesn't exist | Check `input_filelist/<dut>.sim.f` exists |
| `software_defines.sv not found` | udm_flow_scripts dir issue | Verify `udm_flow_scripts/software_defines.sv` exists |
| `udm_verific ImportError` | LD_LIBRARY_PATH not set | Ensure inside `ace_shell --tool udm_rtl_reader` |
| VCS compile fails with UDM defines | Design doesn't compile with Quartus guards | Check +define string in `udm_vcs_flow.cfg` |

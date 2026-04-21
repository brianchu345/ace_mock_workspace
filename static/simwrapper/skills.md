# simwrapper Flow — Testing & Usage Guide

## Architecture

Unlike vcs/questa/xcelium, simwrapper **does not use a Python wrapper**.
`sf_sim_model_gen` is already a self-contained wrapper tool; `tool.mk` calls it directly.

```
static/simwrapper/Makefile
    -> $WORKAREA/toolbase/simwrapper/tool.mk
           ace_shell --tool simwrapper -c 'python sf_sim_model_gen.py sim ...'
```

ACE equivalent of the cheetah pattern:
```makefile
# cheetah
$(ARC_CMD) $(CTH_SIM_MODEL_GEN) sim ...

# ACE
ace_shell --tool simwrapper -c 'python sf_sim_model_gen.py sim ...'
```

## Reference

- Cheetah baseline: `/nfs/site/disks/psg_cthtools_1/pu_tu/baseline_tools/psg/RC/simwrapper/`
- Example workspace: `/nfs/site/disks/da_scratch_1/users/chubrian/chipstack_wkspace/playground/demo_bypass_pnr_reg/static/simwrapper/`
- Tool version: `SF_SIM_MODEL_GEN_VERSION = 0.2.2` (in `ace_projbase/base_tool_bundle.cfg`)

## Setup

```bash
cd $WORKAREA
/nfs/site/disks/da_scratch_1/users/chubrian/ace_wkspace/ace_config/0.1.0/bin/ace_setup
```

## Verify Tool Config

```bash
ace_query --tool simwrapper params sf_sim_model_gen_py --resolve
ace_query --tool simwrapper ENVS SF_SIM_MODEL_GEN_BIN_PATH --resolve
ace_query --tool simwrapper ENVS DEVDATA_TOOLS_ROOT --resolve
```

## Targets

| Target | Description | Prerequisites |
|--------|-------------|---------------|
| `simwrapper_rtl_collect_check` | RTL collect + model check | Flat .sim.f filelist |
| `simwrapper_check` | Check against UDM DB | UDM DB from `run_udm_swfrontcheck` |
| `simwrapper_sim` | Sim-only model generation | `rtl_collect_check` complete |
| `all` | `rtl_collect_check` + `sim` | Flat .sim.f filelist |

Note: `simwrapper_check` depends on an external iflow step (`run_udm_swfrontcheck`) and
is not included in `all`. Run it separately once that output is available.

## Running Directly

```bash
cd $WORKAREA/static/simwrapper

# RTL collect check (needs flat .sim.f from iflow or input_filelist)
make simwrapper_rtl_collect_check \
  DUT=bypass_pnr_reg_fp \
  FLAT_FILELIST=$WORKAREA/input_filelist/bypass_pnr_reg_fp.sim.f

# Sim-only (after rtl_collect_check)
make simwrapper_sim DUT=bypass_pnr_reg_fp

# All (rtl_collect_check + sim)
make all DUT=bypass_pnr_reg_fp \
  FLAT_FILELIST=$WORKAREA/input_filelist/bypass_pnr_reg_fp.sim.f

# Check (needs swfrontcheck UDM DB — run separately)
make simwrapper_check DUT=bypass_pnr_reg_fp
```

## Running via demo_tasks.mk

```bash
cd $WORKAREA
make bypass_pnr_reg_fp__simwrapper_all
make bypass_pnr_reg_fp__simwrapper_rtl_collect_check
make bypass_pnr_reg_fp__simwrapper_check
```

## Key Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DUT` | (required) | Design top module name |
| `REPO_NAME` | `$(DUT)` | Repository/IP name for `--ip-name` |
| `FLAT_FILELIST` | `$WORKAREA/output/<DUT>/flm/flat/<DUT>.sim.f` | Flat filelist for rtl_collect_check |
| `UDM_DB` | `$WORKAREA/output/psg_swfrontcheck/.../<DUT>.udm` | UDM database for simwrapper_check |

## Common Failures

| Error | Cause | Fix |
|-------|-------|-----|
| `sf_sim_model_gen: not found` | Not in `ace_shell --tool simwrapper` env | Run inside `ace_setup`; `SF_SIM_MODEL_GEN_BIN_PATH` must be in PATH |
| `ModuleNotFoundError: click` | devdata python env not set up | Check `DEVDATA_TOOLS_ROOT` is resolved in tool.cfg |
| `No such file: *.sim.f` | FLAT_FILELIST path incorrect | Supply correct `FLAT_FILELIST=` on command line |
| `No such file: *.udm` | swfrontcheck not yet run | Run `run_udm_swfrontcheck` iflow step before `simwrapper_check` |

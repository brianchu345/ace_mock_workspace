# Questa Flow — Testing Procedure & Agent Skills

Consult this file before making changes or debugging the questa flow.

---

## 1. Environment Bootstrap (fresh shell)

```csh
/nfs/site/disks/da_scratch_1/users/chubrian/ace_wkspace/ace_config/0.1.0/bin/ace_setup
```

After this, `ace_shell`, `ace_query`, and `ace_cfg` are on `$PATH`.

---

## 2. Entering the Questa Tool Environment

```csh
# Interactive shell
ace_shell --tool questa

# Single-command execution (used by Makefile targets)
ace_shell --tool questa -c '<command>'
```

---

## 3. Verifying Configuration

```csh
ace_query --tool questa ENVS ACE_TOOL_QUESTA_HOME --resolve
# Expected: .../ace_wkspace/applications.design-automation.altera-cb-env.tool-questa

ace_query --tool questa PARAMS activity
# Expected: static

ace_query --tool questa ENVS QUESTA_HOME --resolve
```

---

## 4. Configuration File Locations

| Purpose           | File path |
|-------------------|-----------|
| Tool env/params   | `$WORKAREA/toolbase/questa/tool.cfg` |
| Flow configuration | `$WORKAREA/static/questa/questa_flow.cfg` |
| Tool make rules   | `$WORKAREA/toolbase/questa/tool.mk` |
| Activity Makefile | `$WORKAREA/static/questa/Makefile` |

---

## 5. Running the Flow via Makefile

```csh
cd $WORKAREA

# Full flow for a DUT
make bypass_pnr_reg_fp__questa_all

# Individual stages
make bypass_pnr_reg_fp__questa_compile
make bypass_pnr_reg_fp__questa_elab

# Direct from static/questa (supply FILELIST explicitly)
cd $WORKAREA/static/questa
make all FILELIST=$WORKAREA/static/questa/filelist.json
```

---

## 6. Running the Wrapper Directly

```csh
# Inside ace_shell --tool questa
QUESTA_PY=/usr/intel/pkgs/python3/3.12.3/bin/python3
WRAPPER=/nfs/site/disks/da_scratch_1/users/chubrian/ace_wkspace/vcs_flow_scripts/questa_wrapper.py

$QUESTA_PY $WRAPPER \
    --filelist $WORKAREA/static/questa/filelist.json \
    --flow-cfg $WORKAREA/static/questa/questa_flow.cfg \
    --step all \
    --verbose
```

---

## 7. Questa Compile/Elab Flow

```
CompileStage
  1. vlib <work_dir>/<work_lib>    — create Questa library directory
  2. per IP: vlog [opts] -work <lib_dir> -f filelist.f
  3. Write modelsim.ini            — library path map for vopt/vsim

ElabStage
  vopt <work_lib>.<top> [opts] -o <top>_opt
```

To simulate after elab:
```csh
vsim <top>_opt
```

---

## 8. Common Failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ace_cfg: command not found` | ace_setup not run | Run step 1 |
| `vlog: command not found` | Not inside ace_shell | Run `ace_shell --tool questa` |
| `ACE_TOOL_QUESTA_HOME` wrong path | tool.cfg has wrong value | Check `toolbase/questa/tool.cfg [envs]` |
| `No rule to make target 'compile'` | Wrong Makefile included | Ensure `static/questa/Makefile` includes `toolbase/questa/tool.mk` |
| `modelsim.ini` not found | Compile stage not run | Run compile before elab |

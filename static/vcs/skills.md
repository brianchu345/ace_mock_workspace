# VCS Flow — Testing Procedure & Agent Skills

This file is the primary reference for testing and running the VCS compile/elaborate
flow in the mock workspace.  Consult it before making changes or debugging.

---

## 1. Environment Bootstrap (fresh shell)

The ACE environment is **not** active in a plain login shell.  Always bootstrap first.

```csh
# Step 1 — bootstrap ACE from the local installation
/nfs/site/disks/da_scratch_1/users/chubrian/ace_wkspace/ace_config/0.1.0/bin/ace_setup
```

After this, `ace_shell`, `ace_query`, and `ace_cfg` are on `$PATH`.

---

## 2. Entering the VCS Tool Environment

All VCS flow commands must run inside `ace_shell --tool vcs` so that
`VCS_HOME`, `VERDI_HOME`, `PATH`, and license tokens are set.

```csh
# Interactive shell with VCS environment
ace_shell --tool vcs

# Single-command execution (used by Makefile targets)
ace_shell --tool vcs -c '<command>'
```

Inside `ace_shell`, `$WORKAREA` is automatically set to the current workspace root.

---

## 3. Verifying Configuration

```csh
# Confirm ACE_TOOL_VCS_HOME points to the local repo
ace_query --tool vcs ENVS ACE_TOOL_VCS_HOME --resolve
# Expected: /nfs/site/disks/da_scratch_1/users/chubrian/ace_wkspace/applications.design-automation.altera-cb-env.tool-vcs

# Check VCS_HOME resolution
ace_query --tool vcs ENVS VCS_HOME --resolve

# Check activity param (controls flow cfg path)
ace_query --tool vcs PARAMS activity
# Expected: static
```

---

## 4. Configuration File Locations

| Purpose              | File path |
|----------------------|-----------|
| Tool env/params      | `$WORKAREA/toolbase/vcs/tool.cfg` |
| Flow configuration   | `$WORKAREA/static/vcs/vcs_flow.cfg` |
| Tool make rules      | `$WORKAREA/toolbase/vcs/tool.mk` |
| Activity entry point | `$WORKAREA/static/vcs/Makefile` |

**Flow cfg auto-discovery path** (in `_find_flow_cfg`):
```
$WORKAREA/<activity>/<toolname>/<toolname>_flow.cfg
= $WORKAREA/static/vcs/vcs_flow.cfg
```
`activity` is read from `tool.cfg [params] activity = static`.

---

## 5. Running the Flow via Makefile

```csh
cd $WORKAREA/static/vcs

# Run full flow (analyze + elab)
make all FILELIST=$WORKAREA/static/vcs/filelist.json

# Run only compile/analyze stage
make analyze FILELIST=$WORKAREA/static/vcs/filelist.json

# Run only elaboration
make elab FILELIST=$WORKAREA/static/vcs/filelist.json

# Override flow cfg explicitly
make all FILELIST=... FLOW_CFG=$WORKAREA/static/vcs/vcs_flow.cfg
```

---

## 6. Running the Wrapper Directly

```csh
# Must be inside ace_shell --tool vcs
VCS_PY=/usr/intel/pkgs/python3/3.12.3/bin/python3
WRAPPER=/nfs/site/disks/da_scratch_1/users/chubrian/ace_wkspace/vcs_flow_scripts/vcs_wrapper.py

$VCS_PY $WRAPPER \
    --filelist $WORKAREA/static/vcs/filelist.json \
    --step all \
    --verbose

# Output directory is created automatically:
#   $WORKAREA/static/vcs/output/
```

---

## 7. Python Wrapper Architecture

```
vcs_wrapper.py
    VCSFlow(BaseFlow)
        ToolConfig   — ace_query(tool='vcs')     full ACE bootstrap
        FlowConfig   — ace_query(file=flow_cfg)  direct file parse
        output_dir   = $WORKAREA/static/vcs/output  (auto-mkdir)
        work_dir     = vcs_flow.cfg [vcs] work_dir  (or output_dir/vcs_work)
        |
        +-- AnalyzeStage  → vlogan per IP
        +-- ElabStage     → vcs elab

ace_flow_base.py  (imported by vcs_wrapper.py)
    _ACE_CONFIG_HOME  — from $ACE_CFG_ROOT or $ACE_CONFIG_HOME or local fallback
    ToolConfig        — uses ace_query(tool=...) for full project resolution
    FlowConfig        — uses ace_query(file=...) for isolated flow file parsing
    BaseFlow          — workarea, output_dir, stages, run()
    BaseStage         — lifecycle: get_inputs → setup_env → preprocess
                                   → generate_script → execute → postprocess
```

---

## 8. Configuration Separation

- **Tool config** (`ace_query(tool='vcs')`) — the full ACE include chain runs,
  resolving cross-file params like `VCS_HOME_PATH` and `VCS_VERSION` from projbase.
  Never mix tool env vars into the flow cfg.

- **Flow config** (`ace_query(file=vcs_flow.cfg)`) — parsed in isolation.
  All `section(key)` references must resolve within the same file.
  User-tunable knobs (debug switches, incremental flags) live here.

---

## 9. `@include` Line Rules

```
# WRONG — inline comments break the parser
@include <WORKAREA>/ace.cfg  # sets WORKAREA

# CORRECT — no inline comments on @include lines
@include <WORKAREA>/ace.cfg
```

---

## 10. Common Failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ace_cfg: command not found` | ace_setup not run | Run step 1 above |
| `Not inside ace_setup, Exiting` | Makefile run outside ace environment | Run `ace_setup` first |
| `ACE_TOOL_VCS_HOME` points to ericolso | `tool.cfg` has wrong path | Check `$WORKAREA/toolbase/vcs/tool.cfg [envs]` |
| `Params(ACE_TOOL_ORDER) missing` | Inline comment on `@include` line | Remove comment from the include line |
| Flow cfg not found | Activity mismatch or wrong workarea | Check `ace_query --tool vcs PARAMS activity` |
| Unresolved `params(...)` tokens in opts | `$DUT` not exported | Export `DUT` before running the wrapper |

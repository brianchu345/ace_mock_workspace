# Xcelium Flow — Testing & Skills Reference

## Architecture

```
demo_tasks.mk
  %__xcelium_compile / %__xcelium_elab / %__xcelium_all
    → cd static/xcelium; make compile/elab/all DUT=<dut> FILELIST=<path>
      → static/xcelium/Makefile
        → includes ace_toolbase/xcelium/tool.mk
          → ace_shell --tool xcelium -c 'python xcelium_wrapper.py ...'
            → XceliumFlow (ace_flow_base.BaseFlow)
              ├── CompileStage  writes cds.lib + xrun -compile per IP
              └── ElabStage     xrun -elabonly -top <lib>.<top>
```

**Key files:**

| File | Purpose |
|------|---------|
| `ace_toolbase/xcelium/tool.cfg` | XCM_HOME, PATH, arc license, xrun_exec |
| `ace_toolbase/xcelium/tool.mk` | Make targets (compile/elab/all) |
| `static/xcelium/xcelium_flow.cfg` | Compile/elab flag strings |
| `vcs_flow_scripts/xcelium_wrapper.py` | Python flow driver |

**Library mapping: `cds.lib`** (written to `work_dir` at compile time)

Xcelium uses `cds.lib` (not `modelsim.ini`) to map logical library names to physical directories.
The file header `INCLUDE ${XCM_HOME}/tools/inca/files/cds.lib` pulls in Cadence built-ins.
Every compiled IP library gets a `define <lib> <abs_path>` line.
Elaboration resolves all cross-library references through `cds.lib` automatically — no
explicit `-L lib` flags needed (unlike Questa).

---

## Setup — Fresh Shell

```bash
# 1. Enter the ACE mock workspace
cd /nfs/site/disks/da_scratch_1/users/chubrian/ace_wkspace/ace_mock_workspace

# 2. Bootstrap ACE
/nfs/site/disks/da_scratch_1/users/chubrian/ace_wkspace/ace_config/0.1.0/bin/ace_setup

# 3. Verify tool config resolves
ace_query --tool xcelium ENVS ACE_TOOL_XCELIUM_HOME --resolve
ace_query --tool xcelium PARAMS xrun_exec --resolve
```

---

## Running via demo_tasks.mk (recommended)

```bash
cd $WORKAREA
# Compile only
make bypass_pnr_reg_fp__xcelium_compile

# Elab only (requires compile first)
make bypass_pnr_reg_fp__xcelium_elab

# Both in sequence
make bypass_pnr_reg_fp__xcelium_all
```

`demo_tasks.mk` auto-computes FILELIST from `$OUTPUT_DIR/<dut>/demo_genfilelist/json/<dut>_sim_filelist.json`.

---

## Running via Makefile directly

```bash
# Must have ace_setup already run
WORKAREA=/nfs/site/disks/da_scratch_1/users/chubrian/ace_wkspace/ace_mock_workspace
FILELIST=$WORKAREA/output/bypass_pnr_reg_fp/demo_genfilelist/json/bypass_pnr_reg_fp_sim_filelist.json

cd $WORKAREA/static/xcelium

make compile DUT=bypass_pnr_reg_fp FILELIST=$FILELIST
make elab    DUT=bypass_pnr_reg_fp FILELIST=$FILELIST
```

---

## Running the wrapper directly (inside ace_shell)

```bash
ace_shell --tool xcelium -c "python3 \
    /nfs/site/disks/da_scratch_1/users/chubrian/ace_wkspace/vcs_flow_scripts/xcelium_wrapper.py \
    --filelist $FILELIST \
    --flow-cfg $WORKAREA/static/xcelium/xcelium_flow.cfg \
    --step compile"
```

---

## Key Xcelium commands used

| Stage | Command |
|-------|---------|
| Compile (per IP) | `xrun -compile <analyze_opts> -work <lib> -xmlibdirpath <work_dir>/<lib> -cdslib <cds.lib> -f <filelist>` |
| Elaborate | `xrun -elabonly <elab_opts> -top <top_lib>.<top> -cdslib <cds.lib>` |

**Differences from Questa:**
- No `vlib` step — Xcelium creates library dirs during compile
- `cds.lib` instead of `modelsim.ini`
- `-xmlibdirpath <dir>/<lib>` instead of `-work <libdir>`
- Elab resolves all libs via `cds.lib` header INCLUDE — no `-L <lib>` flags needed

---

## Output locations

```
static/xcelium/output/
  xcelium_work/           ← compiled libraries + cds.lib
    work/                 ← default work library
    <ip>_lib/             ← IPs with overrideLib
    cds.lib               ← library map for xrun
  <dut>/
    xcelium_compile/
      <dut>_xcelium_compile.log
    xcelium_elab/
      <dut>_xcelium_elab.log
```

---

## Bumping the Xcelium version

Edit only `ace_projbase/base_tool_bundle.cfg`:

```ini
[ToolVersion]
XCM_VERSION = 24.09.001   # change this
```

`XCM_HOME = Params(XCM_HOME_PATH)/Toolversion(XCM_VERSION)` resolves automatically.

---

## Common failures

| Error | Cause | Fix |
|-------|-------|-----|
| `xrun: command not found` | Not inside `ace_shell --tool xcelium` | Run `ace_setup` first |
| `Error parsing configuration: not enough values` | Content before first `[section]` in tool.cfg | Check tool.cfg starts with a `#` comment or `[section]` header |
| `SyntaxError: expected 'key = value'` | Backslash line continuation in .cfg | Flatten multi-line values onto one line (ACE parser doesn't support `\`) |
| `cds.lib: No such file or directory` | Elab run before compile | Run compile stage first |
| `ERROR: Top module not found` | Top lib not in `-top` arg | Check `overrideLib` in filelist JSON; `top_lib` is auto-resolved by ElabStage |

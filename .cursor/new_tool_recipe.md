# Recipe: Adding a New EDA Tool Flow

This document records the exact steps used to add the Questa flow.
Follow these steps to add the next tool (e.g. xcelium, dc, icc2).

---

## Checklist

```
[ ] 1.  toolbase/<tool>/tool.cfg
[ ] 2.  toolbase/<tool>/tool.mk
[ ] 3.  static/<tool>/Makefile
[ ] 4.  static/<tool>/<tool>_flow.cfg
[ ] 5.  static/<tool>/skills.md
[ ] 6.  vcs_flow_scripts/<tool>_wrapper.py
[ ] 7.  demo_tasks.mk — add <tool> pattern targets
[ ] 8.  ace_fe_tool_order.cfg — @include <TOOLNAME>/tool.cfg  (already done if generic)
```

---

## Step 1 — `toolbase/<tool>/tool.cfg`

Mirror `toolbase/questa/tool.cfg`:

```ini
[params]
activity = static        # activity directory name

[envs]
ACE_TOOL_<TOOL>_HOME = /path/to/your/local/ace_tool_<tool>
<TOOL>_HOME          = Params(<TOOL>_HOME_PATH)/Toolversion(<TOOL>_VERSION)
PATH                |= Envs(<TOOL>_HOME)/bin:

[params]
<exec>_exec = Envs(<TOOL>_HOME)/bin/<exec>
```

Rules:
- `activity` drives the flow cfg auto-discovery path.
- `ACE_TOOL_<TOOL>_HOME` must point to the local tool repo (not another user's).
- No inline comments on `@include` lines.  See `bug.md`.

---

## Step 2 — `toolbase/<tool>/tool.mk`

Copy `toolbase/questa/tool.mk`.  Change the three variables at the top:

```makefile
export TOOLNAME    = <tool>
<TOOL>_FLOW_CFG  ?= $(WORKAREA)/static/<tool>/<tool>_flow.cfg
<TOOL>_WRAPPER   := /path/to/vcs_flow_scripts/<tool>_wrapper.py
```

Targets: `compile`, `elab`, `all` — always pass `--flow-cfg $(<TOOL>_FLOW_CFG)`.
Each target must use `$(ACE_SHELL)` so the tool environment is active.

---

## Step 3 — `static/<tool>/Makefile`

One-liner:

```makefile
include ${WORKAREA}/toolbase/<tool>/tool.mk
```

Plus a `help:` target explaining the three targets and FILELIST.

---

## Step 4 — `static/<tool>/<tool>_flow.cfg`

Sections:

```ini
[params]
# Base flag strings — infra-owned
ALTR_<TOOL>_ANALYZE_SETTINGS = ...
ALTR_<TOOL>_ELAB_SETTINGS    = ...

[<tool>]
# User knobs
DEBUG_SWITCH     =
QUIET_MODE       =
VERILOG_ANALYZE_OPTS = params(ALTR_<TOOL>_ANALYZE_SETTINGS) <tool>(DEBUG_SWITCH)
ELAB_OPTS_SWITCH     = params(ALTR_<TOOL>_ELAB_SETTINGS)
work_dir  = ./<tool>_work
WORK_LIB  = work         # tool-specific: questa only
PASS      = gk
```

Key: The section name `[<tool>]` must match `flow_section` in the Python wrapper.

---

## Step 5 — `static/<tool>/skills.md`

Document:
- Bootstrap command (`ace_setup` path)
- `ace_shell --tool <tool>` entry
- Key `ace_query` verification commands
- File locations table
- Makefile usage
- Direct wrapper invocation
- Common failures table

---

## Step 6 — `vcs_flow_scripts/<tool>_wrapper.py`

Copy `questa_wrapper.py`.  Change the following:

| Item | questa | new tool |
|------|--------|----------|
| `_TOOL_NAME` | `'questa'` | `'<tool>'` |
| `flow_section` class attr | `'questa'` | `'<tool>'` |
| `CompileStage` | `vlog` per IP | `<analyze_cmd>` per IP |
| `ElabStage` | `vopt` | `<elab_cmd>` |
| `output_dir` | `static/questa/output` | `static/<tool>/output` |
| exec attrs | `vlib_exec`, `vlog_exec`, `vopt_exec` | tool-specific |
| `_write_map_file` | writes `modelsim.ini` | writes `<tool>`-specific map |
| Step choices in argparse | `compile/elab/all` | adjust if different |

Reuse without change:
- `_UNRESOLVED_TOKEN` regex
- `_find_flow_cfg()` function (auto-discovers from activity)
- `BaseFlow` / `BaseStage` inheritance
- `ace_query` usage pattern
- Log file path pattern

---

## Step 7 — `demo_tasks.mk`

Add three pattern rules:

```makefile
%__<tool>_compile: %__demo_gen_filelist
	cd $(WORKAREA)/static/<tool>; make compile DUT=$* FILELIST=$(_FILELIST)

%__<tool>_elab: %__<tool>_compile
	cd $(WORKAREA)/static/<tool>; make elab DUT=$* FILELIST=$(_FILELIST)

%__<tool>_all: %__demo_gen_filelist
	cd $(WORKAREA)/static/<tool>; make all DUT=$* FILELIST=$(_FILELIST)
```

Usage:
```
make bypass_pnr_reg_fp__<tool>_all
```

---

## Step 8 — Verify with ace_query

```csh
ace_setup   # or ace_shell --tool <tool>

ace_query --tool <tool> ENVS ACE_TOOL_<TOOL>_HOME --resolve
ace_query --tool <tool> PARAMS activity
ace_query --tool <tool> ENVS <TOOL>_HOME --resolve
```

---

## Xcelium Reference (next tool)

Xcelium compile/elab commands:
- Compile: `xmvlog` (SV), `xmvhdl` (VHDL)
- Elab: `xmelab`
- Sim: `xmsim`

Suggested file layout:
```
toolbase/xcelium/tool.cfg
toolbase/xcelium/tool.mk
static/xcelium/Makefile
static/xcelium/xcelium_flow.cfg
static/xcelium/skills.md
vcs_flow_scripts/xcelium_wrapper.py
```

`tool.cfg` [params]:
```ini
xmvlog_exec = Envs(XCELIUM_HOME)/tools/bin/xmvlog
xmelab_exec = Envs(XCELIUM_HOME)/tools/bin/xmelab
xmsim_exec  = Envs(XCELIUM_HOME)/tools/bin/xmsim
```

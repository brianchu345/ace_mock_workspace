# ACE Tool Integration Knowledge Base

This file is a Cursor agent reference for adding new EDA simulation tools to the
ACE mock workspace. It captures patterns learned from VCS, Questa, and Xcelium.

---

## Completed tools and their patterns

| Tool | Compile binary | Elab binary | Library map | Key flag |
|------|---------------|-------------|-------------|----------|
| VCS | `vlogan` | `vcs` | `synopsys_sim.setup` | `-f <filelist>` |
| Questa | `vlog` | `vopt` | `modelsim.ini` | `-work <lib>` |
| Xcelium | `xrun -compile` | `xrun -elabonly` | `cds.lib` | `-xmlibdirpath <dir>/<lib>` |

---

## Recipe: Adding a new EDA simulation tool (e.g. Xcelium → ToolX)

### Step 1 — `ace_toolbase/<tool>/tool.ace`

```ini
# Header comment — describe the tool
[params]
activity       = static
<TOOL>_HOME_PATH = /p/hdk/.../<tool>/         # Param not Env — doesn't pollute PATH

[arc]
<tool>-lic-token                              # ARC license feature token

[envs]
ACE_TOOL_<TOOL>_HOME = /path/to/ace/tool/repo # informational, shown by tool.mk
<TOOL>_HOME = Params(<TOOL>_HOME_PATH)/Toolversion(<TOOL>_VERSION)
PATH |= Envs(<TOOL>_HOME)/<bin_subdir>:

[params]
<exec>_exec = Envs(<TOOL>_HOME)/<bin_subdir>/<exec>
```

**Rules:**
- `<TOOL>_HOME_PATH` goes in `[params]` — keeps PATH clean (Slang pattern)
- `<TOOL>_HOME` goes in `[envs]` — composes path root + `Toolversion()`
- `Toolversion(<TOOL>_VERSION)` must have a matching entry in `ace_projbase/base_tool_bundle.ace [ToolVersion]`
- `[arc]` is a flat list of license tokens only — no paths or env vars
- Verdi / debug tool licenses can be added as separate tokens but are optional

### Step 2 — `ace_toolbase/<tool>/tool.mk`

```makefile
export TOOLNAME        = <tool>
export DUT

<TOOL>_FLOW_CFG   ?= $(WORKAREA)/static/<tool>/flow.ace

ACE_TOOL_<TOOL>_HOME = $(shell ace_query --tool <tool> ENVS ACE_TOOL_<TOOL>_HOME --resolve)
$(info INFO: <tool> tool directory: $(ACE_TOOL_<TOOL>_HOME))

ACE_SHELL          := ace_shell --tool $(TOOLNAME) -c
<TOOL>_PYTHON      ?= /usr/intel/pkgs/python3/3.12.3/bin/python3
<TOOL>_WRAPPER     := /path/to/<tool>_wrapper.py

.PHONY: compile elab all

compile:
	$(ACE_SHELL) '$(TOOL_PYTHON) $(<TOOL>_WRAPPER) \
	    --filelist $(FILELIST) \
	    --flow-cfg $(<TOOL>_FLOW_CFG) \
	    --step compile'
# elab and all follow the same pattern
```

### Step 3 — `ace_mock_workspace/static/<tool>/Makefile`

```makefile
WORKAREA ?= $(realpath $(dir $(abspath $(lastword $(MAKEFILE_LIST))))/../..)
include $(WORKAREA)/toolbase/<tool>/tool.mk
```

Add a `help:` target documenting FILELIST, DUT, and default FLOW_CFG.

### Step 4 — `ace_mock_workspace/static/<tool>/flow.ace`

```ini
[params]
ALTR_<TOOL>_ANALYZE_SETTINGS = <base analyze flags>
ALTR_<TOOL>_ELAB_SETTINGS    = <base elab flags>

[<tool>]
WORK_LIB             = work
VERILOG_ANALYZE_OPTS = Params(ALTR_<TOOL>_ANALYZE_SETTINGS)
ELAB_OPTS_SWITCH     = Params(ALTR_<TOOL>_ELAB_SETTINGS)
work_dir             = ./output/<tool>_work
PASS                 = gk
```

**Rules:**
- Section name `[<tool>]` must match `flow_section` in the wrapper class
- No `@include` of tool configs — strict tool/flow separation
- No backslash (`\`) line continuation — ACE parser does not support it; flatten onto one line
- No inline comments on `@include` lines

### Step 5 — `vcs_flow_scripts/<tool>_wrapper.py`

Inherit from `BaseFlow`. Key attributes to set in `flow_preprocess()`:

| Attribute | Source |
|-----------|--------|
| `self.<exec>_exec` | `tc.resolve('params', '<exec>_exec', ev)` |
| `self.analyze_opts` | `fc.resolve('VERILOG_ANALYZE_OPTS', ev)` |
| `self.elab_opts` | `fc.resolve('ELAB_OPTS_SWITCH', ev)` |
| `self.work_lib` | `fc.get('WORK_LIB', 'work')` |
| `self.work_dir` | `fc.resolve('work_dir', ev)` → anchor to `output_dir` if relative |

Set `flow_section = '<tool>'` on the class to match `[<tool>]` in the flow config.

**Library mapping approach by tool:**

| Tool | Map file | Written by | Used by |
|------|----------|------------|---------|
| Questa | `modelsim.ini` | CompileStage._write_modelsim_ini | vopt |
| Xcelium | `cds.lib` | CompileStage._write_cds_lib | xrun -elabonly |

For Questa, ElabStage must scan `work_dir` for all subdirs and add `-L <lib>` per library.
For Xcelium, cds.lib handles library resolution — no per-lib flags in the elab command.

**Top library resolution** (both tools):
```python
top_info     = ip_details.get(top, {})
top_lib      = top_info.get('overrideLib', '') or flow.work_lib
```
IPs with `overrideLib` in the filelist JSON are compiled into a named lib; the top module
may be in that lib rather than `work`. Always read `overrideLib` before constructing the
elab command.

### Step 6 — `ace_mock_workspace/demo_tasks.mk`

```makefile
%__<tool>_compile: %__demo_gen_filelist
	cd $(WORKAREA)/static/<tool>; make compile DUT=$* FILELIST=$(_FILELIST)

%__<tool>_elab: %__<tool>_compile
	cd $(WORKAREA)/static/<tool>; make elab DUT=$* FILELIST=$(_FILELIST)

%__<tool>_all: %__demo_gen_filelist
	cd $(WORKAREA)/static/<tool>; make all DUT=$* FILELIST=$(_FILELIST)
```

### Step 7 — `ace_mock_workspace/static/<tool>/skills.md`

Document: architecture diagram, setup steps, run commands (demo_tasks, Makefile, direct wrapper),
key command formats, output locations, version bump procedure, common failures.

### Step 8 — `ace_projbase/base_tool_bundle.ace`

Add the toolversion if missing:
```ini
[ToolVersion]
<TOOL>_VERSION = <version_string>
```

### Step 9 — Update docs

- `ace_mock_workspace/activity.md` — record what was done, decisions, files changed
- `ace_mock_workspace/new_tool_recipe.md` — update with tool-specific notes
- `ace_mock_workspace/.cursor/tools.md` — update this file

---

## Known parser constraints (ACE config)

| Constraint | Detail |
|-----------|--------|
| No inline `#` comments on `@include` lines | Comment becomes part of path — silently breaks the include |
| No backslash `\` line continuation | Multi-line values must be flattened to one line |
| No content before first `[section]` header | Causes `not enough values to unpack` parse error |
| `[arc]` is flat list only | Never put paths or env vars there |

---

## Environment variable resolution order

ACE config resolves values lazily across multiple passes:
1. `Params(KEY)` — look up in `[params]` sections of parsed files
2. `Envs(KEY)` — look up in `[envs]` sections of parsed files
3. `Toolversion(KEY)` — look up in `[ToolVersion]` sections (from projbase bundle)
4. `<FILE_DIR>`, `<WORKAREA>`, `<TOOLNAME>`, `<ACTIVITY>` — special builtins

`ace_query(tool='<tool>', section='envs', key='XCM_HOME', resolve=True)` fully resolves
all of the above in one call. Use this instead of direct ConfigParser access.

---

## Common make targets per DUT

```bash
make <dut>__vcs_compile          # VCS compile
make <dut>__vcs_elab             # VCS elab
make <dut>__questa_compile       # Questa compile
make <dut>__questa_elab          # Questa elab
make <dut>__xcelium_compile      # Xcelium compile
make <dut>__xcelium_elab         # Xcelium elab
```

---

## Troubleshooting checklist

1. `ace_cfg: Command not found` → `ace_setup` not run; run it first
2. `Error parsing configuration` → Check tool.ace starts with `#` comment or `[section]`
3. `No rule to make target 'compile'` → Makefile include path wrong; check `tool.mk` is found
4. `xrun/vcs/vlog: not found` → Not inside `ace_shell --tool <tool>` env
5. `Unresolved Toolversion()` → `<TOOL>_VERSION` missing from `base_tool_bundle.ace`
6. Top module not found at elab → Check `overrideLib` in filelist JSON; `top_lib` must match compile lib

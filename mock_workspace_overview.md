# ACE Mock Workspace — Overview

## What Is This Workspace?

`ace_mock_workspace` is the integration environment for ACE frontend flows. It wires together
the ACE configuration system, tool integrations, and project settings into a runnable workspace
for running frontend EDA flows. It is at /nfs/site/home/chubrian/da_scratch_1/ace_wkspace/ace_mock_workspace

> **Note on paths:** This demo uses local symlinks to `../ace_toolbase` and `../ace_projbase`
> for convenience. In a production environment, `toolbase/` symlinks to
> `/p/psg/flows/hw/common/ace/toolbase/<version>` and `projbase/` symlinks to
> `/p/psg/flows/hw/common/ace/projbase/<version>`, allowing multiple workspaces to share
> the same centrally-versioned configurations. And iflow is not implemented yet

---

## Quick Start

```bash
cd ace_mock_workspace
ace_setup                          # bootstraps the ACE environment (sets PATH, WORKAREA, etc.)
make <dut>__<tool>_<step>                 # e.g.  make bypass_pnr_reg_fp__vcs_all
make bypass_pnr_reg_fp__vcs_compile       # single stage
make bypass_pnr_reg_fp__vcs_elab          # single stage (requires compile to have run first)
```

Run `make help` for a full list of available targets.

---

## Directory Layout

```
ace_mock_workspace/
├── ace_setup                 # symlink → ../ace_config/bin/ace_setup
├── project.ace               # workspace stitch point (see below)
├── Makefile                  # entry point: make <dut>__<tool>_<step>
├── demo_tasks.mk             # DUT-target fanout rules to static/<tool>/Makefile
│
├── cfg/                      # [mocked / TBD] per-DUT design configs — not yet part of spec
├── input_filelist/           # [mocked / TBD] RTL filelists per DUT — format TBD
│
├── toolbase/                 # symlink → /p/psg/flows/hw/common/ace/toolbase/<version>  (tool redirectors)
│                              # demo: symlinked to ../ace_toolbase for local convenience
├── projbase/                 # symlink → /p/psg/flows/hw/common/ace/projbase/<version>  (project config)
│                              # demo: symlinked to ../ace_projbase for local convenience
│   ├── project.ace
│   ├── base_tool_bundle.ace / tool_bundle.ace
│   ├── ip_type_params/       # [temporary / TBD] IP-type macro sets — not yet part of spec
│   └── static/               # project-owned collaterals (vary per project, not per tool version)
│       ├── vcs/
│       │   ├── vcswarn2err.ace
│       │   └── w2e_configs/
│       └── udm_rtl_reader/
│           └── software_defines.sv
│
├── static/                   # per-flow configs and Makefiles (one subdir per EDA flow)
│   ├── vcs/
│   ├── questa/
│   ├── xcelium/
│   ├── udm/
│   ├── vc_lint/
│   ├── simwrapper/
│   └── psg_ipxact/
│
├── src/                      # DUT source artifacts (IPXACT, RDL)
└── output/                   # [mocked / TBD] flow run outputs — location TBD
```

---

## Bootstrap: `project.ace`

`project.ace` at the workspace root is the **workspace stitch point**. It is the first file
the ACE bootstrap chain reads after `config.ace`, and it pulls together the two foundational
config layers:

```ini
@include toolbase/config_fe.ace   # sets ACE_TOOL_ORDER → triggers tool config loading
@include projbase/project.ace     # sets project-wide env vars and tool versions
```

This is functionally the same as `$WORKAREA/tool.cth` in Cheetah. You do not normally 

---

## `toolbase/` — Tool Redirectors

`toolbase/` is a symlink to the ACE-managed directory of **thin redirectors** — one subdirectory
per tool. In production it points to `/p/psg/flows/hw/common/ace/toolbase/<version>`. In this
demo it is symlinked to the local `../ace_toolbase` for convenience.

Each tool subdirectory contains exactly two files:

| File | Purpose |
|---|---|
| `tool.ace` | Declares `ACE_TOOL_*_HOME` and includes the full tool config from the versioned repo |
| `tool.mk` | Makefile fragment that reads `ACE_TOOL_*_HOME` and delegates to the versioned `tool.mk` |

**Nothing flow-related belongs here.** No `flow.ace`, no scripts, no data files.

The key benefit of this layer is **independent tool development**: each tool repo is versioned
and released on its own schedule. To upgrade a tool, you change only the version number in
`toolbase/<tool>/tool.ace` — no other workspace files are touched.

### Toolbase bootstrap files

Two files at the top of `toolbase/` are not tool-specific:

| File | Purpose |
|---|---|
| `config_fe.ace` | Sets `ACE_TOOL_ORDER` to point at `ace_fe_tool_order.ace`; defines `ACE_CFG_BASE` and shared env vars |
| `ace_fe_tool_order.ace` | Defines the order in which tool configs are loaded during ACE bootstrap |
| `design_fe.mk` | Shared Makefile recipe: validates `ace_setup` is active, sets `WORKAREA` guard |
| `ace_flow_template/` | Optional shared Python base classes and utilities (see below) |

### `ace_flow_template/` — Optional Shared Flow Infrastructure

Python flow wrappers may inherit from the base classes here. This is recommended for flows
structured as multiple sequential stages, where each stage invokes a tool via `ace_shell --tool`.
The shared scaffolding reduces duplication for such flows. Flows not following this pattern
can implement their own wrappers independently.

Each `BaseStage` subclass implements three lifecycle hooks — all optional, called in order:

| Hook | Purpose |
|---|---|
| `preprocess_inputs()` | Validate inputs, resolve paths, build command arguments |
| `execute()` | Invoke the tool subprocess |
| `postprocess()` | Parse logs, check exit status, report metrics |

| File | Purpose |
|---|---|
| `ace_flow_base.py` | `BaseFlow` and `BaseStage` — defines the stage lifecycle above |
| `ace_flow_utilities.py` | `find_flow_cfg`, `read_flow_cfg`, `run_cmd`, `setup_logger` |
| `log_analyzer.py` | `parse_log_file()` — extracts errors/warnings from tool logs |

---

## `static/<tool>/` — Per-Flow Workspace Config

Each subdirectory under `static/` is the workspace's home for a flow. It contains
the flow configuration and the Makefile that drives it. Nothing here is about how the tool is
installed — that belongs in `toolbase/`.

| File | Purpose |
|---|---|
| `Makefile` | Includes `toolbase/<tool>/tool.mk` (thin redirector), which delegates to `tool-<name>/<version>/tool.mk` where the actual targets and `ace_shell` invocations are defined |
| `flow.ace` | Workspace-level flow config (extends the tool's base `flow.ace` from its versioned repo) |

### `flow.ace` pattern

The workspace `flow.ace` includes the tool's base config from its versioned repo,
then layers workspace-specific overrides on top:

```ini
@include $ACE_TOOL_VCS_HOME/flow.ace   # base flow from versioned tool repo

[vcs]
TOP_COMPILE_LIB =                      # workspace-specific overrides
ERROR_EXCLUDE   = [abc, def, ghi]
WARNING_EXCLUDE = [xyz, uvw, rst]
```

`$ACE_TOOL_VCS_HOME` is exported into the shell by `ace_shell --tool vcs` (via `tool.ace [envs]`).
The `flow.ace` is parsed by the Python flow wrapper at runtime, inside that shell context,
so the variable is always available. The wrapper reads all flow parameters from this config.

---

## `projbase/` — Project Configuration

`projbase/` is a symlink to the project-wide configuration directory. In production it points
to `/p/psg/flows/hw/common/ace/projbase/<version>`. In this demo it is symlinked to the local
`../ace_projbase` for convenience. It holds project-wide settings shared across all tools and
all DUTs in the project.

### `project.ace`

The main project config. Loaded by `project.ace` at the workspace root. Sets:

- **IP library paths** — `SOC_STD_MACRO_TAG`, `CTECH_TAG`, `ALTR_PKG_TAG`, etc.
- **Simulation library paths** — `DW_SIM` (DesignWare simulation models)
- **Design environment flags** — `WELL_BIAS_UPF`, etc.

Includes `tool_bundle.ace` for tool version pinning.

### `base_tool_bundle.ace` / `tool_bundle.ace`

Pin the version of every tool used in the project under `[ToolVersion]`, and define
install-path base variables under `[Params]`:

```ini
[ToolVersion]
VCS_VERSION    = W-2024.09-SP2-4
QUESTA_VERSION = w241129
XCM_VERSION    = 24.06.071
...

[Params]
VCS_HOME_PATH   = /p/psg/eda/synopsys/vcsmx
VERDI_HOME_PATH = /p/psg/eda/synopsys/verdi
```

Tool configs reference these to build install paths without hardcoding versions:

```ini
# tool-vcs/<version>/tool.ace
[envs]
VCS_HOME   = Params(VCS_HOME_PATH)/Toolversion(VCS_VERSION)
VERDI_HOME = Params(VERDI_HOME_PATH)/Toolversion(VERDI_VERSION)
```

To upgrade VCS, change `VCS_VERSION` in `tool_bundle.ace` — all tool paths update automatically.

### `ip_type_params/`

> **Status: temporary / TBD.** This directory exists for demo purposes and is not yet part of
> the finalized spec. Its location under `projbase/` may change.

Currently holds one `.ace` file per IP type (`asic`, `dv`, `cbb`, `softip`, `fc`, etc.).
Each file defines a `[params]` macro set for that IP family, selected at flow-config parse time
based on the DUT's `IP_TYPE` field.

### `static/<tool>/` — Project-Owned Collaterals

`projbase/static/` holds **project-specific data files** that vary from project to project and
do not belong in the tool repo, which is frozen at a version tag. The tool's `flow.ace`
references them via `$WORKAREA/projbase/static/`.

| Directory | Contents | Consumer |
|---|---|---|
| `static/vcs/vcswarn2err.ace` | Warn-to-error filter references — points into `w2e_configs/` | VCS `flow.ace` `@include` |
| `static/vcs/w2e_configs/` | `.f` files that promote VCS analysis/elab warnings to errors | `vcswarn2err.ace` |
| `static/udm_rtl_reader/software_defines.sv` | Project-specific SystemVerilog `` `ifdef `` define blocks for UDM | UDM flow wrapper (path sourced from `flow.ace`) |

---

## Versioned Tool Repos

Each tool lives in its own versioned directory, `tool-<name>/<version>/`, released and
developed independently of the workspace. In this demo, tool repos are located at
`../tools_demo/tool-<name>/<version>/`. In production, these would be centrally-versioned
at a location like `/p/psg/flows/hw/common/ace/tools/tool-<name>/<version>/`.

The thin redirector in `toolbase/<tool>/tool.ace` sets `ACE_TOOL_*_HOME` to point at the
active version, allowing workspaces to upgrade simply by changing the version reference.

Common files in every versioned tool repo:

| Item | Purpose |
|---|---|
| `tool.ace` | Tool installation config: `[arc]` resources, `[envs]` tool paths, `[params]` exec names |
| `tool.mk` | Full Makefile logic: targets, `ace_shell` invocations, Python wrapper calls |
| `flow.ace` | Base flow config — workspace `flow.ace` includes and overrides this |
| `bin/` | Executables — Python flow entry points |
| `modules/` | Main flow logic, modularized as stage classes or utility modules |

### `tool.ace` sections

| Section | Purpose |
|---|---|
| `[arc]` | ARC resource to acquire before launching the shell. ACE calls ARC to resolveand exports all resulting environment variables into the shell. Primarily used for license resources (e.g. `vcs-vcsmx-lic`), but can be used for any ARC resource to bring export ALL environment variables. |
| `[envs]` | Shell environment variables set directly by ACE — tool install paths, `PATH` prepends, etc. |
| `[params]` | Internal named strings consumed by ACE (not exported to shell) — exec names, activity flags. |

### Example: `tool-vcs/<version>/tool.ace`

```ini
[arc]
vcs-vcsmx-lic          # ARC license resource — exports LM_LICENSE_FILE and related vars
synopsys_verdi-lic

[envs]
VCS_HOME        = Params(VCS_HOME_PATH)/Toolversion(VCS_VERSION)
VERDI_HOME      = Params(VERDI_HOME_PATH)/Toolversion(VERDI_VERSION)
VCS_TARGET_ARCH = linux64
PATH            |= Envs(VCS_HOME)/bin:Envs(VERDI_HOME)/bin:
```

`VCS_HOME_PATH` and `VCS_VERSION` are resolved from `projbase/base_tool_bundle.ace`
via multi-pass lazy evaluation — no explicit ordering is required.

---

## Running a Flow

```
make bypass_pnr_reg_fp__vcs_compile
  │
  └─ demo_tasks.mk:  make -C static/vcs compile DUT=bypass_pnr_reg_fp FILELIST=...
       │
       └─ static/vcs/Makefile:
            include toolbase/vcs/tool.mk       ← thin redirector → tool-vcs/<version>/tool.mk
            compile target:
              ace_shell --tool vcs -c '...'     ← sets PATH, VCS_HOME, VERDI_HOME from tool.ace [envs]
                python3 tool-vcs/<version>/bin/vcs_flow.py
                  --filelist input_filelist/<dut>_sim_filelist.json
                  --flow-cfg static/vcs/flow.ace
                  --stage compile
```

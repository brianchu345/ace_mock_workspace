# ACE Mock Workspace — User Guide

The mock workspace at `/nfs/site/home/chubrian/da_scratch_1/ace_wkspace/ace_mock_workspace/`
is the integration environment for ACE flows. Users run flows here by invoking `make`.
Flow owners configure the underlying infrastructure (toolbase, projbase, flow configs) —
users inherit that configuration and can adjust it for their run.

---

## Workspace Layout

```
ace_mock_workspace/
├── ace_setup                    # Run once to enter the ACE environment
├── ace.cfg                      # Workspace stitch point (see below)
├── Makefile                     # Top-level entry point
│
├── cfg/
│   └── bypass_pnr_reg_fp.design.ace
│
├── input_filelist/
│   └── bypass_pnr_reg_fp_sim_filelist.json
│
├── static/                      # Per-tool flow configs — users adjust these
│   ├── vcs/
│   │   ├── flow.ace
│   │   └── Makefile
│   ├── questa/
│   │   ├── flow.ace
│   │   └── Makefile
│   ├── xcelium/
│   │   ├── flow.ace
│   │   └── Makefile
│   └── udm/
│       ├── flow.ace
│       └── Makefile
│
├── output/                      # Logs and artifacts (created at runtime)
│
├── toolbase/ ⟶ ../ace_toolbase/ # Tool installation configs (see below)
└── projbase/ ⟶ ../ace_projbase/ # Project baseline configs (see below)
```

**Key config files:**

- `design.ace` — Connects toolbase and projbase to the workspace. Users can add overrides here (e.g. env vars, tool version pins) on top of the project baseline.
- `cfg/<dut>.design.ace` — Per-DUT data: design name, top module, IP type, and any design-specific settings consumed by the flow.
- `input_filelist/` — Mock RTL filelists for demonstration purposes only.
- `static/<flow>/flow.ace` — User-facing flow configuration. The primary file users edit to change flow behavior.
- `static/<flow>/Makefile` — Delegates to `toolbase/<tool>/tool.mk`; exposes the flow steps available for that tool.

---

## `design.ace` — The Workspace Stitch Point

```ini
@include toolbase/config_fe.ace   # activates tool binary paths and license setup
@include projbase/project.ace     # brings in tool versions and project-wide env vars
```

The join point between toolbase and projbase. Users can append overrides — env vars,
tool version pins, or additional includes — after the baseline includes.

---

## `toolbase/` — Tool Installation Configs

`toolbase/` is a symlink to `/nfs/site/home/chubrian/da_scratch_1/ace_wkspace/ace_toolbase/`.

```
ace_toolbase/
├── config_fe.ace
├── vcs/
│   ├── tool.ace
│   └── tool.mk
├── questa/
├── xcelium/
├── udm_rtl_reader/
└── ace_flow_template/
```

- `config_fe.ace` — Sets the ACE tool search order and points to the ACE config package release.
- `<tool>/tool.ace` — Declares the ARC license tokens, tool home environment variables (e.g. `VCS_HOME`), and binary exec paths for a given tool. Read by `ace_shell`; not read by Python flows.
- `<tool>/tool.mk` — Defines the flow steps as make targets (e.g. `compile`, `elab`, `all`, or tool-specific stages), each wrapped in `ace_shell` to activate the correct tool environment before running.
- `ace_flow_template/` — Python base classes (`BaseFlow`, `BaseStage`) shared across all flows. See `flow_base_template.md`.

---

## `projbase/` — Project Baseline Configs

`projbase/` is a symlink to `/nfs/site/home/chubrian/da_scratch_1/ace_wkspace/ace_projbase/`.

```
ace_projbase/
├── project.ace
├── base_project.ace
├── tool_bundle.ace
├── base_tool_bundle.ace
└── ip_type_params/
    ├── ip_type.asic.ace
    ├── ip_type.dv.ace
    └── ...
```

- `base_tool_bundle.ace` — Org-wide canonical version pins for every tool (VCS, Questa, Xcelium, FC, SpyGlass, etc.).
- `tool_bundle.ace` — Branch-level overrides on top of the base bundle; pins specific tool versions for this branch.
- `base_project.ace` / `project.ace` — Project-wide environment variables: library tag paths, macro definitions, UPF settings.
- `ip_type_params/ip_type.<TYPE>.ace` — Simulator `+define` macros for each IP classification. Selected automatically at runtime based on the DUT's `IP_TYPE`.

---

## Running Flows

```bash
ace_setup
make <dut>__<flow>_<step>
```

| Part | Example values |
|---|---|
| `<dut>` | `bypass_pnr_reg_fp` — matches a file in `cfg/` |
| `<flow>` | `vcs`, `questa`, `xcelium`, `udm` |
| `<step>` | `compile`, `elab`, `all` |

```bash
make bypass_pnr_reg_fp__vcs_all
make bypass_pnr_reg_fp__questa_compile
make bypass_pnr_reg_fp__all      # runs every flow in sequence
```

Run `make help` for the full target list.

---

## Customizing a Flow

Each flow's behavior is controlled by its `flow.ace` under `static/`. These are
pre-configured by flow owners with safe defaults. Users edit them to adjust behavior for
their run.

```ini
[params]
# Reusable flag string chunks — composable building blocks.
# Set by flow owners as defaults; users can override values here too.
# Referenced inside [vcs] as params(KEY).
ALTR_VCS_ANALYZE_SETTINGS = -sverilog -timescale=1ns/1ps ...

[vcs]
# Feature switches for this flow. Set a value to enable; leave empty to disable.
# Keys here can compose params above — e.g.:
VERILOG_ANALYZE_OPTS = params(ALTR_VCS_ANALYZE_SETTINGS) vcs(DEBUG_SWITCH) vcs(MULTI_THREADING)

DEBUG_SWITCH =             # e.g. -kdb -lca -debug_access+all  (enable waveforms)
MULTI_THREADING =          # e.g. -jm 8  (parallel compilation jobs)
VCS_INCREMENTAL =          # e.g. -incr_vlogan  (skip unchanged files)
CTH_QUIET_MODE =           # e.g. -q  (suppress messages)
```

**Example** — to enable debug waveforms, set in `static/vcs/vcs_flow.cfg`:

```ini
DEBUG_SWITCH = -kdb -lca -debug_access+all
```

---

## ACE vs. Cheetah

- **Tool and flow configuration are strictly separate.** In Cheetah, `baseline_tools/<tool>/tool.cth` serves as a catch-all — it can contain tool installation settings, flow parameters, and environment setup all in one file, and other `tool.cth` files freely include it. This makes it difficult to understand what any given file is responsible for. In ACE, `tool.cfg` owns only tool installation (binary paths, licenses, env vars) and `flow.cfg` owns only flow behavior. Neither includes the other.

- **Each flow step runs in a reproducible, isolated tool shell.** In Cheetah, environment variables can be set or modified dynamically as the flow progresses, meaning the environment at execution time depends on execution order. In ACE, `ace_shell --tool <tool>` fully resolves and locks the tool environment before any flow code runs — the same make target always produces the same environment, regardless of what else is in the shell.

- **Infrastructure is versioned and external.** In Cheetah, `baseline_tools/` lives inside the design repo and must be maintained per-workspace. In ACE, `toolbase` and `projbase` are separate versioned repositories, symlinked into the workspace. Tool and project updates are a symlink bump — the workspace is not touched.

- **Flow configs live in a consistent location.** In Cheetah, `flow.cfg` location varies by tool and team — it may be under `verif/<tool>/`, `static/<tool>/`, or elsewhere depending on convention. In ACE, every flow config is always at `static/<flow>/<flow>_flow.cfg`, regardless of tool or project.

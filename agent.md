# ACE Demo — Agent Context

Read this file before making any changes in this directory.

## What Is ACE

ACE is the in-house frontend EDA flow infrastructure that replaced the legacy **Cheetah** system.
It provides a config-file-driven layer over EDA tools (VCS, VC-CDC, etc.) and manages tool
paths, license acquisition, and flow parameterization.

The workspace entry point is `ace_shell_setup`, which invokes `ace_shell` and loads the
top-level `tool.cfg` into the ACE environment.

---

## Environment Setup

```csh
# tcsh — enter the ace environment for this workspace
source ace_shell_setup
# or equivalently:
$ACE_SHELL --shell /bin/tcsh -f $WORKAREA/tool.cfg -c "<command>"
```

`WORKAREA` must be set to the ace_demo root before running any wrappers.
`DUT` must be set to the design-under-test name (e.g. `bypass_pnr_reg_fp`).

---

## Directory Layout

```
ace_demo/
├── ace_shell_setup              # sources the ace_shell binary; workspace entry point
├── tool.cfg                     # workspace-level ace config (loaded by ace_shell)
├── Makefile                     # invokes vcs_wrapper.py via make <dut>__vcs_<step>
│
├── baseline_tools/              # INFRA-OWNED — do not add per-design overrides here
│   ├── global_config/
│   │   ├── global_project.cfg   # project-wide [envs]: IP_MODELS, DW_SIM, tag paths, etc.
│   │   └── ip_type_params/      # ip_type.<type>.cfg — per-IP-type macro sets
│   ├── tools/
│   │   └── vcs/
│   │       └── vcs_tool.cfg     # VCS tool config: [arc] licenses, [envs] paths, [params] execs
│   └── flows/
│       └── vcs/
│           ├── vcs_flow.cfg     # VCS flow config: [params] flags, [vcs] switches
│           ├── vcswarn2err.cfg  # warn-to-error filter file paths
│           ├── vcs.Makefile     # pattern rules for compile/elab/all
│           └── w2e_configs/     # .f files listing promoted warning IDs
│
├── cfg/
│   └── <dut>.design.cfg         # per-DUT identity: TOP_IP_NAME, TOP_MODULE_NAME, IP_TYPE
│
├── user_override/
│   └── vcs/
│       └── vcs_flow_override.cfg  # user overrides; includes baseline flow cfg first
│
├── input_filelist/
│   └── <dut>_sim_filelist.json  # RTL filelist consumed by vcs_wrapper.py
│
└── output/                      # logs per DUT and per step
    └── <dut>/
        └── vcs_<step>/<dut>_vcs_<step>.log
```

---

## Config File Architecture

### The Two Pillars: Tool Config vs Flow Config

These are **strictly independent** — neither includes the other.

| File | Purpose | Sections used |
|------|---------|---------------|
| `baseline_tools/tools/<tool>/<tool>_tool.cfg` | Tool installation: license features, binary paths, versions | `[arc]`, `[envs]`, `[params]` |
| `baseline_tools/flows/<flow>/<flow>_flow.cfg` | Flow parameterization: compiler flags, switches, metadata | `[includes]`, `[params]`, `[vcs]` |

A flow wrapper (e.g. `vcs_wrapper.py`) reads **both files separately** and merges the
resolved namespaces itself. Never add a tool include inside a flow file or vice versa.

### User Override Files

`user_override/<flow>/<flow>_flow_override.cfg` includes the baseline flow config and then
adds or overrides specific keys:

```ini
[includes]
../../baseline_tools/flows/vcs/vcs_flow.cfg   # pull in baseline first

[vcs]
DEBUG_SWITCH = -kdb -lca -debug_access+all    # override a single key
work_dir     = $WORKAREA/work/bypass_pnr_reg_fp
```

The wrapper auto-discovers overrides: if `user_override/vcs/vcs_flow_override.cfg` exists it
takes precedence over the baseline flow cfg; otherwise the baseline is used directly.

---

## Config File Sections

### `[arc]`

Lists ARC license feature names. The ACE config parser resolves these automatically into the
correct license environment variables and appends them to the environment before running any
tool. You do not write env vars here — only the bare feature token.

```ini
[arc]
vcs-vcsmx-lic
synopsys_verdi-lic
```

### `[envs]`

Shell environment variables. Values can reference other sections using the resolution syntax.

```ini
[envs]
VCS_HOME = envs(VCS_HOME_PATH)/params(VCS_VERSION)/linux64/suse
```

### `[params]`

Named string parameters (not exported as shell env vars). Used to compose flag strings.

```ini
[params]
ALTR_VCS_ANALYZE_SETTINGS = -sverilog -timescale=1ns/1ps -y ${DW_SIM}
vlogan_exec = envs(VCS_HOME)/bin/vlogan
```

### `[vcs]` (or other tool namespace sections)

Feature-switch keys for a specific tool's flow. Overrideable by user_override files.
Wrappers read this section exclusively for composed command lines.

```ini
[vcs]
DEBUG_SWITCH =                        # empty = disabled
VERILOG_ANALYZE_OPTS = params(ALTR_VCS_ANALYZE_SETTINGS) vcs(W2E_ANALYZE) vcs(DEBUG_SWITCH)
```

### `[global_config]`

Per-DUT identity values set in `cfg/<dut>.design.cfg`. Referenced dynamically during
include resolution.

```ini
[global_config]
IP_TYPE = asic
```

### `[includes]`

Ordered list of other `.cfg` files to include. A leading `-` makes the include optional
(silently skipped if the file does not exist).

```ini
[includes]
vcswarn2err.cfg
-../../../cfg/$DUT.design.cfg
-../../global_config/ip_type_params/ip_type.global_config(IP_TYPE).cfg
```

---

## Value Resolution Syntax

The ACE config parser expands cross-section references at parse time:

| Syntax | Meaning |
|--------|---------|
| `envs(KEY)` | Value from `[envs]` section |
| `params(KEY)` | Value from `[params]` section |
| `vcs(KEY)` | Value from `[vcs]` section |
| `global_config(KEY)` | Value from `[global_config]` section |
| `resolve_value(expr)` | Expands expr before using it as a filename |
| `$VAR` / `${VAR}` | Shell environment variable (expanded at runtime) |

The include `ip_type.global_config(IP_TYPE).cfg` is a dynamic filename: the parser first
resolves `global_config(IP_TYPE)` (e.g. `asic`) and then looks up the file
`ip_type.asic.cfg`. This means `cfg/$DUT.design.cfg` **must** be included before this line.

---

## Running Flows

### Via Make (preferred)

```bash
export WORKAREA=<path-to-ace_demo>
export DUT=bypass_pnr_reg_fp
make bypass_pnr_reg_fp__vcs_compile
make bypass_pnr_reg_fp__vcs_elab
make bypass_pnr_reg_fp__vcs_all
```

### Via wrapper script directly (from inside ace_shell)

```bash
python3 vcs_wrapper.py \
  --tool-cfg $WORKAREA/baseline_tools/tools/vcs/vcs_tool.cfg \
  --flow-cfg $WORKAREA/user_override/vcs/vcs_flow_override.cfg \
  --filelist $WORKAREA/input_filelist/${DUT}_sim_filelist.json \
  --step all
```

### Via run script (wraps ace_shell invocation)

```csh
csh run_vcs.csh
```

---

## Adding a New Tool

1. Create `baseline_tools/tools/<tool>/<tool>_tool.cfg` with `[arc]`, `[envs]`, `[params]`.
2. Create `baseline_tools/flows/<tool>/<tool>_flow.cfg` with `[includes]`, `[params]`, `[vcs]`.
3. The two files must remain independent — no cross-includes.
4. Optionally create `user_override/<tool>/<tool>_flow_override.cfg` that includes the
   baseline flow cfg and overrides specific keys.
5. Add a Makefile include and pattern rules in `baseline_tools/flows/<tool>/<tool>.Makefile`.

## Adding a New DUT

1. Create `cfg/<dut>.design.cfg` with `[global_config]` keys (`TOP_IP_NAME`, `IP_TYPE`, etc.).
2. Place the filelist at `input_filelist/<dut>_sim_filelist.json`.
3. Run `make <dut>__vcs_all`.

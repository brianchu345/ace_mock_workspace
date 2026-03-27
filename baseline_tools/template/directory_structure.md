# ACE Demo — Directory Structure

## Visual Tree

```
ace_demo/                                  ← WORKAREA root
│
├── tool.cfg                               ← Workarea entry point; loaded by ACE shell on startup.
│                                            Includes global_project.cfg + whichever tool configs
│                                            the wrapper needs. Exports [envs] into the shell.
│
├── baseline_tools/                        ← Versioned, project-agnostic EDA configurations (in git).
│   │
│   ├── global_config/                     ← Shared config fragments included by tool/flow configs.
│   │   ├── tool_version.cfg               ← Base RTL/FE tool versions (all activities inherit this).
│   │   ├── static_tool_version.cfg        ← Static-analysis tool versions; @includes tool_version.cfg.
│   │   ├── dv_tool_version.cfg            ← DV tool versions; @includes tool_version.cfg.
│   │   └── proj_base/                     ← Project-level defaults (IP type macros, sim params).
│   │       ├── global_project.cfg         ← Project-wide [envs]: DW_SIM, IP_MODELS, SOC_* tags.
│   │       ├── ip_type_params/            ← Per-IP-type macro files (aip, asic, cbb, dv, ss …).
│   │       │   ├── ip_type.aip.cfg
│   │       │   ├── ip_type.asic.cfg
│   │       │   └── ...
│   │       └── sim_params/                ← Shared simulator analyze/elab flag sets.
│   │           ├── vcs_params.cfg
│   │           ├── xcelium_params.cfg
│   │           ├── questa_params.cfg
│   │           └── riviera_params.cfg
│   │
│   ├── tools/                             ← One subdirectory per EDA tool.
│   │   └── <tool_name>/
│   │       └── <tool_name>_tool.cfg       ← Tool configuration (see §Tool Config below).
│   │
│   ├── flows/                             ← One subdirectory per flow variant.
│   │   └── <flow_name>/
│   │       ├── <flow_name>_flow.cfg       ← Flow configuration (see §Flow Config below).
│   │       ├── cleanup.cfg                ← (optional) model-size reduction rules.
│   │       └── run_audit                  ← (optional) post-processing script.
│   │
│   ├── template/                          ← Reference templates and documentation (this file).
│   │   ├── TEMPLATE_tool.cfg
│   │   ├── TEMPLATE_flow.cfg
│   │   └── directory_structure.md
│   │
├── user_override/                         ← Per-user / per-workarea flow overrides (not in git).
│   └── <flow_name>/
│       └── <flow_name>_flow_override.cfg  ← Re-declares [<flow_name>] keys to override baseline.
│
├── cfg/                                   ← DUT-specific design configs, one per DUT.
│   └── $DUT.design.cfg                    ← Sets [global_config] IP_TYPE, MILESTONE, etc.
│
└── output/                                ← Run outputs (not in git).
    └── $DUT/
        └── <flow_name>/
```

---

## `<tool_name>_tool.cfg` — Tool Configuration

A tool config describes **how to locate and invoke a single EDA tool**. It is **standalone** — it never `@include`s a flow config.

```ini
# =============================================================================
# <tool>_tool.cfg
# =============================================================================
[params]
activity = static          # or: dv
                           # Selects which version file to pull in:
                           #   static → global_config/static_tool_version.cfg
                           #   dv     → global_config/dv_tool_version.cfg

@include ../../global_config/params(activity)_tool_version.cfg
                           # Brings in [toolversion] and [envs] from the correct
                           # version file. Resolved lazily by config_parser.py.

[envs]
TOOL_HOME = /p/path/to/tool/Toolversion(TOOL_VERSION)
                           # Toolversion(KEY) resolves from [toolversion] above.
                           # Envs(KEY) cross-references another [envs] value.

[arc]
vendor-lic/feature         # ARC license feature token.
                           # ACE config parser exports the license env var automatically.
                           # Only override queue/timeout in user_override if required.

[params]
tool_exec = Envs(TOOL_HOME)/bin/tool_binary
                           # Convenience param so flow wrappers avoid hard-coding paths.
```

**What belongs here:**
- Install path construction (`TOOL_HOME`, `TOOL_VERSION`)
- `[arc]` license feature tokens
- Exec-path convenience params (`tool_exec`)
- Tool-level environment variables required at invocation time

**What does NOT belong here:**
- Flow switches (`PASS`, `FILELIST`, `VERILOG_ANALYZE_OPTS`)
- Design-specific paths or DUT references
- Anything in `[<flow_name>]` sections

---

## `<flow_name>_flow.cfg` — Flow Configuration

A flow config describes **how to run a specific analysis pass** using one or more tools. It is **standalone** — it never `@include`s a tool config.

```ini
# =============================================================================
# <flow>_flow.cfg
# =============================================================================
# Include order:
#   1. Shared simulator/tool params (from proj_base/sim_params/)
#   2. DUT design config (sets IP_TYPE in [global_config])
#   3. IP-type macro file (lazy-evaluated)

@include ../../global_config/proj_base/sim_params/vcs_params.cfg
@include ../../../cfg/$DUT.design.cfg
@include ../../global_config/proj_base/ip_type_params/ip_type.global_config(IP_TYPE).cfg

[params]
# Override shared defaults for this specific flow only.
# ALTR_VCS_ELAB_SETTINGS = -error=DTIE

[<flow_name>]
PASS                  = <pass_name>    # Output dir tag and GK qualifier
POST_PROCESSING_FILE  = $WORKAREA/baseline_tools/flows/<flow_name>/run_audit
VERILOG_ANALYZE_OPTS  = Params(ALTR_VCS_ANALYZE_SETTINGS) Params(ALTR_MACROS_...)
ELAB_OPTS_SWITCH      = Params(ALTR_VCS_ELAB_SETTINGS)
FILELIST              = $WORKAREA/output/$DUT/genfile/json/${DUT}_all_filelist.json
```

**What belongs here:**
- Flow switches consumed by the wrapper (`PASS`, `FILELIST`, `VERILOG_ANALYZE_OPTS`, etc.)
- `@include` chains for shared params and IP-type macros
- Post-processing and cleanup hooks

**What does NOT belong here:**
- Tool install paths or version numbers
- `[arc]` license tokens
- `[envs]` blocks unless the env is flow specific and not tool specific

---

## Config Hierarchy and Load Order

The ACE wrapper loads tool and flow configs **independently**, then merges their sections:

```
                        ┌─────────────────────────────────┐
                        │  $WORKAREA/tool.cfg              │
                        │  (loaded at ace_shell startup)   │
                        └────────────┬────────────────────┘
                                     │ @include
                 ┌───────────────────┼───────────────────────────┐
                 ▼                   ▼                            ▼
    global_project.cfg       tool_version.cfg           <tool>_tool.cfg
    (DW_SIM, IP_MODELS …)    (base versions)            (TOOL_HOME, [arc], exec)
                                     │
                         ┌───────────┴──────────┐
                         ▼                       ▼
              static_tool_version.cfg    dv_tool_version.cfg
              (activity=static tools)   (activity=dv tools)

   ── Wrapper invocation ──────────────────────────────────────────────────────

   wrapper.py reads:
     1. <tool>_tool.cfg         → exports TOOL_HOME, license env, exec path
     2. <flow>_flow.cfg         → reads PASS, FILELIST, ANALYZE_OPTS, etc.
     3. user_override/<flow>/   → overrides flow-level keys only

   user_override re-declares [<flow_name>] keys — it does NOT touch tool config.
```

### Key Resolution Rules

| Syntax | Where It Resolves |
|---|---|
| `Toolversion(KEY)` | `[toolversion]` section (from version cfg) |
| `Envs(KEY)` | `[envs]` section (from same or included cfg) |
| `Params(KEY)` | `[params]` section (from same or included cfg) |
| `global_config(KEY)` | `[global_config]` section (set by `$DUT.design.cfg`) |
| `@include path` | Path resolved relative to the including file; lazy-evaluated |
| `params(activity)_tool_version.cfg` | `activity` resolved from `[params]` before path expansion |

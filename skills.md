# ACE Demo — Agent Skills

These are operating rules for any Cursor agent working inside `ace_demo/`.
Read `agent.md` first for full architecture context.

---

## Before You Start

- Read `agent.md` to understand the ACE config system, section semantics, and directory layout.
- Understand whether you are touching **infra** (`baseline_tools/`) or **user** (`user_override/`, `cfg/`) files — they have different change policies.

---

## Config Authoring Rules

### Tool vs Flow separation (hard rule)

`baseline_tools/tools/<tool>/<tool>_tool.cfg` and `baseline_tools/flows/<tool>/<tool>_flow.cfg`
**must never include each other**. A flow wrapper reads them separately; coupling breaks that contract.

- Tool config owns: `[arc]` license tokens, `[envs]` binary paths, `[params]` executable names.
- Flow config owns: `[params]` flag strings, `[vcs]` (or tool-namespace) feature switches, `[includes]` for flow-only helpers.

### User overrides go in `user_override/`, not `baseline_tools/`

If a user needs to change a flag, add it to `user_override/<flow>/<flow>_flow_override.cfg`.
Start the file with:
```ini
[includes]
../../baseline_tools/flows/<flow>/<flow>_flow.cfg
```
Then add only the keys that differ. Do not edit baseline files for per-design needs.

### Include ordering in flow files

When a flow includes `cfg/$DUT.design.cfg` and then a dynamic ip_type file, the design cfg
**must** come first so `global_config(IP_TYPE)` is resolved before the ip_type include.

### Optional includes use the `-` prefix

```ini
[includes]
-../../../cfg/$DUT.design.cfg   # silently skipped if file doesn't exist
```

### `[arc]` is license-only

Never put tool paths or env vars in `[arc]`. It is a flat list of ARC feature tokens; the
ACE parser resolves them to license env vars automatically.

### Empty values disable switches

```ini
[vcs]
DEBUG_SWITCH =        # disabled — produces no flags in the composed command line
```

Set to a non-empty string to enable:
```ini
DEBUG_SWITCH = -kdb -lca -debug_access+all
```

---

## Making Changes

### To bump a tool version

Edit only `baseline_tools/tools/<tool>/<tool>_tool.cfg`:
```ini
[params]
VCS_VERSION = X-2025.06-SP2   # change this line
```
The `[envs]` composed paths (`envs(VCS_HOME_PATH)/params(VCS_VERSION)/...`) resolve automatically.

### To enable a flow feature for a run

Add to `user_override/<flow>/<flow>_flow_override.cfg`:
```ini
[vcs]
DEBUG_SWITCH = -kdb -lca -debug_access+all
```

### To add a project-wide env var

Edit `baseline_tools/global_config/global_project.cfg` under `[envs]`. This file is included
by `tool.cfg` so its values are visible to all tools and flows.

### To add a new DUT

1. Create `cfg/<dut>.design.cfg`:
   ```ini
   [global_config]
   TOP_IP_NAME     = <dut>
   TOP_MODULE_NAME = <dut>
   IP_TYPE         = asic
   ```
2. Place filelist at `input_filelist/<dut>_sim_filelist.json`.
3. Run `make <dut>__vcs_all` (inside ace_shell or via `run_vcs.csh`).

---

## Running and Testing

Always run inside the ACE environment:
```bash
source ace_shell_setup   # or: $ACE_SHELL -f $WORKAREA/tool.cfg -c "<cmd>"
```

Check the output log to verify success:
```
output/<dut>/vcs_<step>/<dut>_vcs_<step>.log
```

---

## What Not To Do

- Do not add `+define+` macros directly to a flow cfg — use the ip_type param files under `baseline_tools/global_config/ip_type_params/`.
- Do not hardcode absolute paths in `baseline_tools/` files — use `$WORKAREA`, `envs()`, or `params()` references.
- Do not include a tool cfg from inside a flow cfg or vice versa.
- Do not edit `baseline_tools/` to work around a single-design issue; use `user_override/` instead.
- Do not add license tokens to `[envs]` or `[params]` — they belong exclusively in `[arc]`.

# ACE Mock Workspace — Agent Skills

These are operating rules for any Cursor agent working inside `ace_mock_workspace/`.
Read `agent.md` first for full architecture context.

---

## Before You Start

- Read `agent.md` to understand the ACE config system, section semantics, and directory layout.
- Understand whether you are touching **toolbase** (`toolbase/`, `projbase/`) or **flow/design** (`static/`, `cfg/`) files — they have different change policies.

---

## Config Authoring Rules

### Tool vs Flow separation (hard rule)

`toolbase/<tool>/tool.ace` and `static/<tool>/flow.ace`
**must never include each other**. A flow wrapper reads them separately; coupling breaks that contract.

- Tool config owns: `[arc]` license tokens, `[envs]` binary paths, `[params]` executable names.
- Flow config owns: `[params]` flag strings, `[<tool>]` (or tool-namespace) feature switches, `[includes]` for flow-only helpers.

### Flow overrides and customization

Flow configs in `static/<tool>/flow.ace` contain baseline settings. To customize for a specific run:

- Modify the flow config directly for persistent changes (if you own the flow).
- Or create an override config that includes the baseline and overrides specific keys.

Do not modify `toolbase/` or `projbase/` configs for flow-specific needs — those are tool infrastructure.

### Include ordering in flow files

When a flow includes `cfg/$DUT.design.cfg` and then a dynamic ip_type file, the design cfg
**must** come first so `global_config(IP_TYPE)` is resolved before the ip_type include.

### No inline comments on `@include` lines

The parser does **not** strip `# comments` from `@include` paths — the comment becomes
part of the file path and silently breaks the include.

```ini
# WRONG
@include <WORKAREA>/design.ace   # workspace overlay

# CORRECT — put comment on its own line
# workspace overlay
@include <WORKAREA>/design.ace
```

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

Edit only `toolbase/<tool>/tool.ace`:
```ini
[params]
VCS_VERSION = X-2025.06-SP2   # change this line
```
The `[envs]` composed paths (`envs(VCS_HOME_PATH)/params(VCS_VERSION)/...`) resolve automatically.

Also update `projbase/base_tool_bundle.ace` if the version needs to be tracked there:
```ini
[ToolVersion]
VCS_VERSION = X-2025.06-SP2
```

### To enable a flow feature for a run

Edit `static/<tool>/flow.ace`:
```ini
[<tool>]
DEBUG_SWITCH = -kdb -lca -debug_access+all
```

### To add a project-wide env var

Edit `projbase/project.ace` under `[envs]`. This file is included by `design.ace` so its values are visible to all tools and flows.

### To add a new DUT

1. Create `cfg/<dut>.design.ace`:
   ```ini
   [global_config]
   TOP_IP_NAME     = <dut>
   TOP_MODULE_NAME = <dut>
   IP_TYPE         = asic
   ```
2. Place filelist at `input_filelist/<dut>_sim_filelist.json`.
3. Run `make <dut>__<tool>_all` (e.g., `make <dut>__vcs_all`).

---

## Running and Testing

Always run inside the ACE environment:
```bash
source ace_setup
# or:
ace_shell --tool <tool> -c "<cmd>"
```

Check the output log to verify success:
```
output/<dut>/<tool>_<step>/<dut>_<tool>_<step>.log
```

---

## What Not To Do

- Do not add `+define+` macros directly to a flow cfg — use the ip_type param files under `projbase/ip_type_params/`.
- Do not hardcode absolute paths in `toolbase/` or `projbase/` files — use `$WORKAREA`, `envs()`, or `params()` references.
- Do not include a tool cfg from inside a flow cfg or vice versa.
- Do not edit `toolbase/` or `projbase/` to work around a single-design issue; use flow configs in `static/` or design configs in `cfg/` instead.
- Do not add license tokens to `[envs]` or `[params]` — they belong exclusively in `[arc]`.

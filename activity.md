# Activity Log

## 2026-03-26 (session 3)

### Cleaned up vc_cdc_tool.cfg; added reference and compatibility docs
- **`baseline_tools/tools/vc_cdc/vc_cdc_tool.cfg`**: removed `SNPSLMD_QUEUE`/`SNPS_MAX_WAITTIME` from `[envs]` with note that ARC handles these automatically; bumped `PSG_FE_CHECKER_UTILITIES_VERSION` from `1.9` to `1.27.2` (minimum version with `vccdc_methodology/` and all vc_cdc-specific scripts).
- **`psg_fe_checker_utilities_reference.md`**: documents all `bin/` scripts, methodology directories, and usage patterns (run_audit CSV, TCL source, Makefile targets, flow cfg path keys) across all ioss3 Cheetah flows.
- **`migration_compatibility.md`**: documents 8 compatibility issues ranging from DMX audit script dependency (high) to sdc2sgdc missing from Makefile (low), with impact ratings and required ACE actions.

## 2026-03-26 (session 2)

### Relocated activity.md and added flow decisions docs
- Moved `activity.md` from workspace root to `ace_demo/` (ace_demo is the project root).
- Created `baseline_tools/flows/vcs/decisions.md` — documents design rationale for VCS flow (W2E separation, DEBUG_SWITCH default, [vcs] vs [params] split, tool/flow independence, ip_type optional includes).

### Converted Cheetah vc_cdc baseline to ACE format
- **`baseline_tools/tools/vc_cdc/vc_cdc_tool.cfg`** — fully aggregated from three Cheetah layers (rtl_tools.cth base, pesg_fe.baseline_tools/vc_cdc/tool.cth paths, ioss3 project overrides). Cheetah `[License]` blocks → `[arc]`, `toolversion()` → `params()`. All ioss3 version and path overrides win.
- **`baseline_tools/flows/vc_cdc/vc_cdc_flow.cfg`** — converted from `ioss3_hsio/baseline_tools/vc_cdc/global_flow.cfg`, milestone locked to 1.0 (`CHECK = setup cdc`). Follows ACE tool/flow separation contract.
- **`baseline_tools/flows/vc_cdc/vc_cdc.Makefile`** — pattern rules for `%__vc_cdc_run`; no `CHEETAH_RTL_ROOT`, no `cth_query` calls.
- **`baseline_tools/flows/vc_cdc/stdcell_filelist/`** — copied directly from Cheetah (alynx, km, n3c variants).
- **`baseline_tools/flows/vc_cdc/run_audit`** — copied from Cheetah.
- **`baseline_tools/flows/vc_cdc/inputs/run_opts.tcl`** — copied from Cheetah.
- **`baseline_tools/flows/vc_cdc/decisions.md`** — documents Cheetah→ACE conversion decisions, milestone-as-branch rationale, stdcell co-location, removal of runtime `cth_query`.

## 2026-03-26

### Created ACE demo agent documentation
- **`ace_demo/agent.md`** — comprehensive architecture reference covering: ACE vs Cheetah history, environment setup (`ace_shell_setup`), full directory layout, all config section semantics (`[arc]`, `[envs]`, `[params]`, `[vcs]`, `[global_config]`, `[includes]`), value resolution syntax (`envs()`, `params()`, `vcs()`, `global_config()`), `[arc]` license auto-resolution, tool/flow separation contract, user override pattern, and how-to guides for adding tools and DUTs.
- **`ace_demo/skills.md`** — agent operating rules covering: config authoring rules (tool/flow separation, override policy, include ordering, arc-only license tokens), step-by-step change guides (version bump, feature enable, new DUT), run instructions, and an explicit "what not to do" list.

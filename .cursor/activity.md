# Activity Log

## 2026-03-31 (session 4)

### Added VC Lint (vc_static) flow; disabled simwrapper (IPR)

**simwrapper disabled:** sf_sim_model_gen is not ACE-compatible yet (IPR).
Targets in `demo_tasks.mk` commented out.

**vc_lint integration** following ACE standard practice:

**Reference material consulted:**
- `/nfs/site/disks/psg_cthtools_1/pu_tu/baseline_tools/psg/RC/vc_lint/` — baseline Makefile.inc, global_flow.cfg, inputs/, liberty_filelist/
- `/nfs/site/disks/crt_tools_059/baseline_tools/pesg_fe/1.22.11.p01/vc_lint/tool.cth` — env/license
- `/nfs/site/disks/da_scratch_1/users/chubrian/chipstack_wkspace/playground/demo_bypass_pnr_reg/static/vc_lint/flow.cfg` — project overrides
- `/nfs/site/disks/crt_tools_045/Cheetah-RTL/2024.12.p05/static_checks/vc_static/lib/Vc_static.py` — vc_static_shell call pattern: `$VC_STATIC_HOME/bin/vc_static_shell -f <tcl> -batch`

**Key design decisions:**
- ACE replaces `cth_vc_static -lint -compile/run` with `vc_lint_wrapper.py --step compile/run`.
- `[arc] synopsys_vc_static/X-2025.06-SP2` provides `VC_STATIC_HOME` and PATH — not overridden in tool.cfg (license feature name TBC).
- `vc_lint_wrapper.py` generates compile.tcl dynamically from the JSON filelist (one `analyze -format sverilog ... -work <lib> -f ...` per IP), mirrors Cheetah `Vc_static.py` localCompile() structure.
- `vc_lint_flow.cfg` is a single merged file (global_flow.cfg + project flow.cfg combined) — no include chain needed.
- `inputs/compile_settings.tcl` and `inputs/run_settings.tcl` copied from baseline; they source from `$PSG_FE_CHECKER_UTILITIES_HOME/vclint_methodology/`.
- `PSG_FE_CHECKER_UTILITIES_HOME` set to `/p/cth/cad/psg_fe_checker_utilities/1.27.2` via tool.cfg [envs] + `PSG_FE_CHECKER_UTILS_VERSION` in base_tool_bundle.cfg.
- Liberty filelist referenced directly from baseline path (not copied) in vc_lint_flow.cfg.

**Files created:**
- `toolbase/vc_lint/tool.cfg` — arc token, PSG_FE_CHECKER_UTILITIES_HOME, VC_FLAVOR, SNPS env
- `toolbase/vc_lint/tool.mk` — compile/run/all targets via ace_shell
- `static/vc_lint/Makefile` — entry point
- `static/vc_lint/vc_lint_flow.cfg` — merged global + project config
- `static/vc_lint/inputs/compile_settings.tcl` — copied from baseline
- `static/vc_lint/inputs/run_settings.tcl` — copied from baseline
- `static/vc_lint/skills.md` — testing guide
- `vcs_flow_scripts/vc_lint_wrapper.py` — Python wrapper (CompileStage + RunStage)

**Files modified:**
- `demo_tasks.mk` — added `%__vc_lint_compile`, `%__vc_lint_run`, `%__vc_lint_all`; commented out simwrapper targets
- `ace_projbase/base_tool_bundle.cfg` — added `PSG_FE_CHECKER_UTILS_VERSION = 1.27.2`

## 2026-03-31 (session 3)

### Added simwrapper (sf_sim_model_gen) flow

Added simwrapper as a fourth tool integration alongside VCS, Questa, and Xcelium.

**Key insight — no Python wrapper needed:**
Unlike vcs/questa/xcelium which needed a Python wrapper to orchestrate per-IP compile loops,
`sf_sim_model_gen` is itself a self-contained wrapper tool. `tool.mk` calls it directly via
`ace_shell --tool simwrapper`, replacing the cheetah `ARC_CMD` pattern:
```
# cheetah: $(ARC_CMD) $(CTH_SIM_MODEL_GEN) sim ...
# ACE:     ace_shell --tool simwrapper -c 'python sf_sim_model_gen.py sim ...'
```

**Reference material consulted:**
- `/nfs/site/disks/psg_cthtools_1/pu_tu/baseline_tools/psg/RC/simwrapper/tool.cth` — env/version reference
- `/nfs/site/disks/psg_cthtools_1/pu_tu/baseline_tools/psg/RC/simwrapper/Makefile.simwrapper` — target definitions
- `/nfs/site/disks/da_scratch_1/users/chubrian/chipstack_wkspace/playground/demo_bypass_pnr_reg/static/simwrapper/Makefile` — how cheetah integrates it

**Files created:**
- `toolbase/simwrapper/tool.cfg` — env setup: `SF_SIM_MODEL_GEN_HOME`, `SF_SIM_MODEL_GEN_BIN_PATH`, devdata python runtime (provides `click`), PATH
- `toolbase/simwrapper/tool.mk` — three targets (`simwrapper_rtl_collect_check`, `simwrapper_check`, `simwrapper_sim`, `all`) calling `ace_shell --tool simwrapper -c`
- `static/simwrapper/Makefile` — entry point; includes `toolbase/simwrapper/tool.mk`
- `static/simwrapper/simwrapper_flow.cfg` — placeholder for future flow-level overrides
- `static/simwrapper/skills.md` — testing/usage guide

**Files modified:**
- `demo_tasks.mk` — added `%__simwrapper_rtl_collect_check`, `%__simwrapper_check`, `%__simwrapper_sim`, `%__simwrapper_all` pattern rules
- `ace_projbase/base_tool_bundle.cfg` — added `SF_SIM_MODEL_GEN_VERSION = 0.2.2`

**Key decisions:**
- `SF_SIM_MODEL_GEN_HOME_PATH` in `[params]` — not polluting PATH until explicitly composed.
- `SF_SIM_MODEL_GEN_HOME = Params(SF_SIM_MODEL_GEN_HOME_PATH)/Toolversion(SF_SIM_MODEL_GEN_VERSION)` — versioned path following Slang/Xcelium pattern.
- devdata python env included in tool.cfg (provides `click` for `sf_sim_model_gen.py`).
- `sf_sim_model_gen.py` invoked directly with our Python interpreter to avoid the `python` vs `python3` issue in the bash wrapper script.
- `REPO_NAME` defaults to `DUT` if not set (cheetah gets this from `cth_query params REPO_cluster`).
- `FLAT_FILELIST` defaults to `$WORKAREA/output/<DUT>/flm/flat/<DUT>.sim.f` (cheetah iflow output location).
- `simwrapper_check` not included in `all` — depends on external `run_udm_swfrontcheck` iflow step.

## 2026-03-31 (session 2)

### Added Xcelium simulation flow

Added Xcelium as a third sim tool alongside VCS and Questa.

**Reference material consulted:**
- `applications.services.design-system.baseline-tools-psg.repo/xcelium/global_flow.cfg` — baseline flags
- `/nfs/site/disks/crt_tools_045/Cheetah-RTL/2024.12.p05/sim/lib/Xcelium.py` — command structure
- `/nfs/site/disks/crt_tools_059/baseline_tools/pesg_fe/1.22.11.p01/xcelium/tool.cth` — env/license reference

**Key decisions:**
- `XCM_HOME_PATH` lives in `[params]` (not `[envs]`) — matches Slang pattern so it does not
  pollute the shell until explicitly composed into `XCM_HOME`.
- `XCM_HOME = Params(XCM_HOME_PATH)/Toolversion(XCM_VERSION)` — versioned home path.
- `[arc] cadence_xcelium-lic` — matches `cadence/xcelium` feature from tool.cth.
- Verdi excluded from PATH — not needed for compile/elab.
- `DW_SIM` flags removed from `VERILOG_ANALYZE_OPTS` — HDK-internal path unavailable in demo.
- Library mapping uses `cds.lib` (Xcelium native), not `modelsim.ini`.
  Header `INCLUDE ${XCM_HOME}/tools/inca/files/cds.lib` is expanded by xrun at runtime.
- `xrun -compile` / `xrun -elabonly` — single binary for both stages (unlike Questa's vlib/vlog/vopt).
- Elab resolves all cross-library refs via cds.lib INCLUDE chain — no `-L <lib>` flags needed.

**Files created:**
- `ace_toolbase/xcelium/tool.cfg` — XCM_HOME, PATH, `cadence_xcelium-lic`, `xrun_exec`
- `ace_toolbase/xcelium/tool.mk` — compile/elab/all targets via `ace_shell --tool xcelium`
- `ace_mock_workspace/static/xcelium/Makefile` — entry point, includes tool.mk
- `ace_mock_workspace/static/xcelium/xcelium_flow.cfg` — analyze/elab flag strings
- `ace_mock_workspace/static/xcelium/skills.md` — testing guide
- `vcs_flow_scripts/xcelium_wrapper.py` — XceliumFlow + CompileStage + ElabStage
- `ace_mock_workspace/.cursor/tools.md` — agent knowledge base for adding new tools

**Files modified:**
- `ace_mock_workspace/demo_tasks.mk` — added `%__xcelium_compile/elab/all` pattern rules

**Run:**
```bash
make bypass_pnr_reg_fp__xcelium_compile
make bypass_pnr_reg_fp__xcelium_elab
make bypass_pnr_reg_fp__xcelium_all
```

---

## 2026-03-31

### Fixed ace_setup bootstrap chain — two root-cause config bugs

**Symptom**: Running `ace_setup` from the mock workspace failed with:
```
ValueError: Lazy evaluation for Params(ACE_TOOL_ORDER) resulted in missing value
```
Then after partial workarounds, `make help` failed with `ace_cfg: Command not found`.

**Root cause 1 — inline comments on `@include` lines in `ace_fe_tool_order.cfg`**

The file had:
```
@include <WORKAREA>/ace.cfg                        # repo setup/project setup
```
The config parser does not strip inline `#` comments from `@include` paths (by design — it
only strips them from key=value assignments). The comment text became part of the file path,
making the include silently fail. On the second parse pass (triggered because `config_fe.cfg`
redirects `ACE_TOOL_ORDER`), `ace.cfg` was never re-included, so `ACE_TOOL_ORDER` disappeared
from the parser's freshly-reset section dict, causing the ValueError.

**Fix**: Remove inline comments from `@include` lines in `toolbase/ace_fe_tool_order.cfg`.
The parser rule is: `@include` paths must be comment-free; put doc comments on a separate `#` line above.

**Root cause 2 — `ACE_CFG_BASE` in `config_fe.cfg` pointed to ericolso's NFS path**

`config_fe.cfg` had `ACE_CFG_BASE = /nfs/site/disks/psg_data_25/ericolso/...`. This caused
`ace_setup` to compute `ACE_CFG_ROOT = <ericolso_path>/0.1.0` and then re-exec into ericolso's
copy of `ace_setup`, which also failed (same parser issue + wrong paths).

**Fix**: Updated `config_fe.cfg` to point `ACE_CFG_BASE` at the workspace-local release copy:
`ACE_CFG_BASE = /nfs/site/disks/da_scratch_1/users/chubrian/ace_wkspace/ace_config`

The user created `ace_wkspace/ace_config/0.1.0/` as a local versioned release, so
`ACE_CFG_ROOT = ace_config/0.1.0` resolves correctly and `ace_setup` no longer re-execs.

**Files changed**:
- `toolbase/ace_fe_tool_order.cfg` — stripped inline comments from all three `@include` lines
- `toolbase/config_fe.cfg` — updated `ACE_CFG_BASE` to local `ace_wkspace/ace_config`

---

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

# Activity Log

## 2026-03-27 (session 9)

### Refactored include syntax; added vcs* tools and flows; added templates

**Include syntax fix:**
- `vc_lint_flow.cfg` and `vcs_flow.cfg`: replaced legacy `[includes]` section with `@include` directives (new format per `config_format.md`). The `-` prefix (`@include -path`) means optional — parser skips silently if file absent.

**Shared params extraction:**
- Created `global_config/vcs_params.cfg`: single source of truth for `ALTR_VCS_ANALYZE_SETTINGS`, `ALTR_VCS_ELAB_SETTINGS` (empty default), `W2E_ANALYZE`, `W2E_ELAB`. All vcs* flow configs include this file and override only what they need (e.g. vcssw sets `ALTR_VCS_ELAB_SETTINGS = -error=DTIE`).
- Updated `vcs_flow.cfg` to include `vcs_params.cfg` and remove inline duplicate params.

**Templates:**
- `baseline_tools/TEMPLATE_tool.cfg` — canonical guideline for tool configs: `[arc]` for license tokens, `[envs]` for path composition via `Toolversion()`, `[params]` for exec paths.
- `baseline_tools/TEMPLATE_flow.cfg` — canonical guideline for flow configs: standalone (no tool @include), `[params]` for base flag overrides, `[<flow>]` for all wrapper-readable settings.

**New tool configs:**
- `tools/vcssim/vcssim_tool.cfg` — DV VCS (`vcssim_vcs = V-2023.12-SP1-1`); uses `linux64/suse` subpath (V-* PSG mirror layout differs from W-* flat layout). Shared by vcssim, vcssimmpp, vcssimmppxprop, vcssimemu. **Note: vcssimmpp and vcssimmppxprop are the same tool — xprop is a flow-level flag, not a tool distinction.**
- `tools/vcssimzoix/vcssimzoix_tool.cfg` — vcssim + `ZOIXHOME` for fault-injection simulation.

**New flow configs (all use vcs_tool.cfg + vcs_params.cfg):**
- `flows/vcssw/vcssw_flow.cfg` — SW model compile, overrides elab to `-error=DTIE`, uses flat stubs filelist.
- `flows/vcsdv/vcsdv_flow.cfg` — DV testbench compile, UVM include, `ALTR_MACROS_SIM_DV`.
- `flows/vcsdvpp/vcsdvpp_flow.cfg` — DV post-processing, `ALTR_MACROS_SIM_DV_PP`, debug on by default.

**Key architectural notes captured:**
- `vcsdv`, `vcsdvpp`, `vcssw` all use RTL VCS (`VCS_VERSION = W-2024.09-SP2-4`), not DV VCS. The "dv" in vcsdv refers to the testbench type, not the simulator version.
- `vcssim` family uses DV VCS (`vcssim_vcs = V-2023.12-SP1-1`) with `linux64/suse` path.
- `vcssimmpp` and `vcssimmppxprop` are effectively the same tool.

## 2026-03-27 (session 8)

### Fixed VCS exec paths; migrated all vc_* tools to ACE

**Bug fix — VCS exec path:**
- Verified against live filesystem: `/p/psg/eda/synopsys/vcsmx/W-2024.09-SP2-4/bin/vlogan` is the correct path; `/linux64/suse` subdirectory does not exist in the PSG mirror.
- Removed `/linux64/suse` suffix from `VCS_HOME` and `VERDI_HOME` in `baseline_tools/tools/vcs/vcs_tool.cfg`.

**Bug fix — vc_static exec name:**
- Verified: PSG vc_static install only contains `vc_static_shell` binary (not `vc_cdc` or `vc_lint`). `VC_FLAVOR` env var controls analysis mode.
- Fixed `vc_cdc_exec` → `vc_static_exec = Envs(VC_STATIC_HOME)/bin/vc_static_shell` in `vc_cdc_tool.cfg`. Same pattern applied to all new vc_* tool configs.

**`static_versions.cfg` — extended:**
- Added `VCLINT_VERSION = V-2023.12-SP2-10`, `VCLINT_METHODOLOGY_VERSION = 2.02.22.25ww18`, `VC_VERSION = T-2022.06`.

**New tool configs (all in `baseline_tools/tools/`):**
- `vc_lint/vc_lint_tool.cfg` — lint family, PSG path, overrides `VCCOMMON_METHODOLOGY_VERSION = 2.04.08.25ww11` (differs from vc_cdc's `2.04.07.25ww07`)
- `vc_rdc/vc_rdc_tool.cfg` — RDC analysis, shares VCCDC_* versions with vc_cdc
- `vc_effm/vc_effm_tool.cfg` — EffM analysis, VCLINT_* versions, `VC_FLAVOR=EFFM`
- `vc_ol/vc_ol_tool.cfg` — OL analysis, `VC_FLAVOR=OL`
- `vc_sva/vc_sva_tool.cfg` — SVA analysis, `VC_FLAVOR=SVA`
- `vc_common/vc_common_tool.cfg` — common methodology only, uses `VCCOMMON_VERSION`
- `vcformal/vcformal_tool.cfg` — formal verification, `VC_VERSION=T-2022.06`, HDK path (no PSG mirror for this version)

**New flow config:**
- `flows/vc_lint/vc_lint_flow.cfg` — converted from `ioss3_hsio/baseline_tools/vc_lint/global_flow.cfg`. Has flow logic (`global_flow.cfg`, `Makefile.inc`, run scripts) → classified as a **flow**, same split as vc_cdc.

**Classification summary:**
- `vc_lint` → tool + flow (both `tools/` and `flows/`)
- `vc_rdc`, `vc_effm`, `vc_ol`, `vc_sva`, `vc_common`, `vcformal` → tool only (no `global_flow.cfg` in Cheetah)

## 2026-03-27 (session 7)

### Added global version config files + updated tool configs to new format

- **`baseline_tools/global_config/tool_version.cfg`** — new base version file, copied directly from `ioss3_hsio/baseline_tools/rtl_tools.cth`. Contains `[toolversion]` (VCS, Verdi, Xcelium, Questa, FC, Veloce, SpyGlass, etc.) and `[envs]` (PSG install-path roots: `VCS_HOME_PATH`, `VERDI_HOME_PATH`, `VELOCE_HOME_PATH`, `DFT_SPYGLASS_PATH`).
- **`baseline_tools/global_config/dv_versions.cfg`** — new DV version file. Uses `@include tool_version.cfg` then adds DV overrides copied from the three `dv_tools.cth` layers (`vcssim_vcs`, `questasim`, `xcelium`, `dvb`, `emu_vcs`, etc.). Adds workarea-local VIP env vars (`SAOLA_HOME`, `UVM_HOME`, `DESIGNWARE_HOME`).
- **`baseline_tools/global_config/static_versions.cfg`** — new static analysis version file. Uses `@include tool_version.cfg` then adds `VCCDC_VERSION`, `VCCOMMON_VERSION`, `VCCDC_METHODOLOGY_VERSION`, `CDCQA_VERSION`, `PSG_FE_CHECKER_UTILITIES_VERSION`.
- **`baseline_tools/tools/vcs/vcs_tool.cfg`** — rewritten. Replaces hardcoded `VCS_VERSION`/`VERDI_VERSION` in `[params]` with `@include ../../global_config/tool_version.cfg`. `VCS_HOME`/`VERDI_HOME` now use `Toolversion()` cross-section refs per new config format.
- **`baseline_tools/tools/vc_cdc/vc_cdc_tool.cfg`** — rewritten. Replaces inline version params with `@include ../../global_config/static_versions.cfg`. All `params(VERSION)` refs in `[envs]` converted to `Toolversion(VERSION)` per new format. `vc_cdc_exec` moved to `[params]`.
- **`playground/new_system/vcs_flow_scripts/vcs_wrapper.py`** — docstring updated to document the `@include` chain, `Toolversion()` resolution pattern, and `_build_env_vars` / `_resolve_tool` behavior. No functional changes required — `parse_file()` follows `@include` transparently.

## 2026-03-26 (session 6)

### Rewrote graph: cluster-based tool overlap, per-flow inclusion chains
- vis-network CDN blocked by corporate firewall → replaced with `plotly` + `networkx` (via `UsrIntel.R1`). plotly.js embedded inline, no external deps.
- **Inclusion Chain view** — dropdown to pick one flow, shows its A→B→C include tree auto-fitted/centered. No scrolling.
- **Tool Clusters view** — compares 94 `pesg_fe.baseline_tools` tool configs. **Key fix**: subtracts the 143-attribute common base (from `rtl_tools.cth`/`dv_tools.cth`) before comparing — previous version was 83% red because everything shared the same inherited base. Uses `greedy_modularity_communities` to detect 12 natural clusters (e.g. vc_static family, vcssim variants, runtools group, emulation tools). 46 singletons shown separately. Click any cluster → panel shows shared unique attrs + each member tool's full config.
- **`tools/config_graph/baseline_graph.html`** — 4.7 MB, 119 flows, 94 tools, 12 clusters.

## 2026-03-26 (session 5)

### Interactive baseline tools dependency graph (v2)
- **`tools/config_graph/config_graph.py`** — Reads all `tool.cth` files under `baseline_tools/` via `CTH.Config` (same API as `flm_utilities.read_config`). Requires `cth_psetup_fe` env. Two-view interactive HTML:
  - **View 1 — Inclusion Chains**: static hierarchical layout, all flows as top-level nodes, shared configs (`rtl_tools`, `dv_tools`, `pesg_fe:*`) as children. No physics/movement.
  - **View 2 — Attribute Overlap**: all flows as nodes, edges between flows colored green→red by similarity (shared envs, tool versions, licenses). Slider to filter by min overlap. Click edge to see exact/divergent attributes.
  - **Click-to-expand attributes**: licenses, envs, versions, params shown in collapsible side panel on node click (not always-visible child nodes).
  - All `baseline_tools/` children with `tool.cth` treated as flows (top-level). Excludes `iflow`, `iflow_mako`, `ifeed`.
  - Pluggable `BaseConfigReader` ABC; `ACEConfigReader` stub ready for drop-in.
- **`tools/config_graph/baseline_graph.html`** — 119 flows, 3157 overlap edges.

## 2026-03-26 (session 4)

### Cheetah baseline analysis documentation
- **`cheetah_baseline_analysis.md`** — documents the full Cheetah dependency chain in plain English (5-layer include cascade, CSS-like override rule, double-include mechanism, DV vs RTL version registry split, ioss3 pass-through vs override classification, ACE collapse implications). Explains why DV tools carry different versions than RTL tools and why `SAOLA_HOME`/`UVM_HOME`/`DESIGNWARE_HOME` from `dv_tools.cth` belong in `global_project.cfg` not tool cfgs.

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

## 2026-03-27 (session 4)

### Implemented parametric @include via params(activity) in all tool.cfgs

**Key finding from ACE config_parser.py source:**
- `resolve_value()` uses `r"(\w+)\((\w+)\)"` with case-insensitive section lookup — `params(activity)` works in `@include` paths.
- `parse_file()` runs fixed-point lazy evaluation (multiple passes until stable) — `[params]` can technically come before OR after `@include`, but convention is before for readability.
- `-` prefix for optional includes IS supported by the parser (strips leading `-`).

**New file:** `global_config/rtl_tool_version.cfg` — thin wrapper that `@include tool_version.cfg`. Needed because `tool_version.cfg` lacks the `rtl_` prefix required for the uniform parametric pattern.

**All 30 activity-tagged tool.cfgs rewritten (Python script):**
- `[params] activity = <X>` block moved BEFORE `@include` for clarity
- `@include ../../global_config/<X>_tool_version.cfg` → `@include ../../global_config/params(activity)_tool_version.cfg` (uniform for all 30 tools)
- Standalone tools unchanged (cfgip, wrap_gen, design_intent — own versions, no global base)

**TEMPLATE_tool.cfg updated** to show the correct pattern with `[params] activity` before the parametric `@include`.

## 2026-03-27 (session 3)

### Refactored global_config version file naming; added activity param to all tool.cfgs

**Renamed files:**
- `global_config/dv_versions.cfg` → `global_config/dv_tool_version.cfg`
- `global_config/static_versions.cfg` → `global_config/static_tool_version.cfg`
- `global_config/tool_version.cfg` unchanged (RTL/FE base)

**Bulk updates (sed across all *.cfg):**
- All `@include` paths and comment references updated to new filenames across `baseline_tools/tools/` and `baseline_tools/flows/`.

**Added `activity` param to 30 tool.cfgs (Python script):**
- `activity = static` — vc_cdc, vc_common, vc_effm, vc_lint, vc_ol, vc_rdc, vc_sva, vcformal (8 tools)
- `activity = dv`     — cc, certitude, cf_utils, cpp, crb, crflow, vcssim, vcssimzoix, veloce, visadv, vps, xceliumsim, zebu (13 tools)
- `activity = rtl`    — collage, collage_tb, coretools, ctf, defacto, vcs, verdi, visa, xcelium (9 tools)
- Standalone tools skipped (own `[toolversion]`, no global base): cfgip, wrap_gen, design_intent

**Updated:**
- `TEMPLATE_tool.cfg` — updated version source comments + added `activity = rtl` to [params] section
- `migration_status.md` — updated to new cfg filenames

## 2026-03-27 (session 2)

### Added arc_license.txt reference; migrated cc, certitude, cf_utils, cfgip, collage*, coretools, cpp, crb, crflow, ctf, defacto, design_intent, ctech

**Infrastructure:**
- Created `baseline_tools/migration_status.md` — tracks all Cheetah tools/flows with ✅/🔲/⚠️ status and 7 open questions (COLLAGE_VERSION, CORE_TOOLS_VERSION, SDG_INTERFACE_DEFS_VERSION, defacto/STAR license token, certitude license, cpp necessity, cth_wrap_di replacement).

**Global config updates:**
- `global_config/tool_version.cfg` — added `DEFACTO_VERSION`, `COLLAGE_VERSION` (placeholder 6.06), `COLLAGE_INTF_DEF_VERSION`, `INTGMSTR_VERSION`, `BUS_INTERFACE_DEF_VERSION`, `SDG_INTERFACE_DEFS_VERSION` (TBD), `CORE_TOOLS_VERSION` (TBD).
- `global_config/dv_versions.cfg` — added `cf_utils`, `onesource`, `socbuilder_client`.

**New tool configs:** cc, certitude, cf_utils, cfgip, collage, collage_tb, coretools, cpp, crb, crflow, ctf, defacto, design_intent.
**New flow configs:** design_intent (+ 5 Makefiles + di_checks.yaml), ctech (base + 6 process-variant cfgs).

## 2026-03-27

### Migrated veloce, verdi, visa, visadv, vps, wrap_gen, xcelium*, zebu tools and xcelium flow

**Infrastructure:**
- Introduced `global_config/sim_params/` directory for simulator-specific analyze/elab parameter files.
- Moved `global_config/vcs_params.cfg` → `global_config/sim_params/vcs_params.cfg`; updated `@include` paths in `flows/vcs/`, `flows/vcssw/`, `flows/vcsdv/`, `flows/vcsdvpp/`, and `TEMPLATE_flow.cfg`.
- Created `global_config/sim_params/xcelium_params.cfg` with `ALTR_XCELIUM_ANALYZE_SETTINGS`, `ALTR_XCELIUMSW_ANALYZE_SETTINGS`, and `ALTR_XCELIUM_ELAB_SETTINGS`.
- Extended `global_config/tool_version.cfg`: added `VISAROOT_VERSION = 5.3.3` and `VISAFLOW_ROOT_VERSION = 4.7` (from Cheetah-RTL base; no ioss3 override).
- Extended `global_config/dv_versions.cfg`: added emu/emulation versions (`zse`, `emu_designcompiler`, `emu_gcc`, `emu_tb_gcc`, `jem`, `simics`), VPS/FPGA versions (`vps`, `quartus`, `vivado`, `red_softmodel`, `visualizer`, `vps_questasim`, `fpga_gcc`, `fpga_tb_gcc`), DV VISA versions (`visa_root = 5.3`, `visaflow_root = 4.7`), and `XCM_BASE_PATH` in `[envs]`.

**New tool configs (tools only — no Cheetah global_flow.cfg existed):**
- `tools/veloce/veloce_tool.cfg` — Mentor Veloce emulation; DV versions; `arc: mentor/veloce`.
- `tools/verdi/verdi_tool.cfg` — Synopsys Verdi standalone waveform viewer; RTL versions; `arc: synopsys/verdi`.
- `tools/visa/visa_tool.cfg` — Intel VISA RTL variant (`VISAROOT_VERSION = 5.3.3`); no license.
- `tools/visadv/visadv_tool.cfg` — Intel VISA DV variant (`visa_root = 5.3`); no license.
- `tools/vps/vps_tool.cfg` — Mentor VPS FPGA emulation; DV versions; `arc: mentor/vps + xilinx/vivado`.
- `tools/wrap_gen/wrap_gen_tool.cfg` — PSG wrap_gen.py standalone; own `[toolversion]`; no license.
- `tools/xcelium/xcelium_tool.cfg` — Cadence Xcelium RTL (`XCM_VERSION = 24.06.071`); HDK path; `arc: cadence/xcelium + synopsys/verdi`.
- `tools/xceliumsim/xceliumsim_tool.cfg` — Cadence Xcelium DV (`xcelium = 24.09.071`); DV versions + Cadence AVS flags; `arc: cadence/xcelium`.
- `tools/zebu/zebu_tool.cfg` — Synopsys ZeBu emulation; DV versions; `arc: synopsys/zebu + xilinx/vivado`.

**New flow config:**
- `flows/xcelium/xcelium_flow.cfg` — Xcelium RTL compile+elab flow; includes `xcelium_params.cfg`, `$DUT.design.cfg`, and ip_type cfg; `[xcelium]` section with flow control knobs.
- `flows/xcelium/cleanup.cfg` and `run_audit` — copied from Cheetah.

## 2026-03-26

### Created ACE demo agent documentation
- **`ace_demo/agent.md`** — comprehensive architecture reference covering: ACE vs Cheetah history, environment setup (`ace_shell_setup`), full directory layout, all config section semantics (`[arc]`, `[envs]`, `[params]`, `[vcs]`, `[global_config]`, `[includes]`), value resolution syntax (`envs()`, `params()`, `vcs()`, `global_config()`), `[arc]` license auto-resolution, tool/flow separation contract, user override pattern, and how-to guides for adding tools and DUTs.
- **`ace_demo/skills.md`** — agent operating rules covering: config authoring rules (tool/flow separation, override policy, include ordering, arc-only license tokens), step-by-step change guides (version bump, feature enable, new DUT), run instructions, and an explicit "what not to do" list.

## 2026-03-27

### Removed `rtl` activity category — now only `dv` and `static`
- All tool.cfgs with `activity = rtl` updated to `activity = static` (9 files: collage, collage_tb, coretools, ctf, defacto, vcs, verdi, visa, xcelium).
- `global_config/rtl_tool_version.cfg` marked as deprecated; no longer included by any tool.

### Expanded `static_tool_version.cfg` with new tool versions
Added version variables for: JG_VERSION, LEC_VERSION, MINT_*, POWERARTIST_VERSION, PUNI_*, VISUALIZER_VERSION, RTLA_VERSION, PP_RTLA_VERSION, LC_VERSION, RIVIERA_VERSION, CDC_SPYGLASS_*, DFT_SPYGLASS_DC_VERSION, DFT_METHODOLOGY_VERSION, LINT_SPYGLASS_*, OL_SPYGLASS_*, CDCLINT_VERSION, SOCBUILDER_VERSION, UB_VERSION+deps, VCLP_*, ARC_BIN_VERSION, LIB_ANALYZER_VERSION, IPQC_*, PSG_LIFT_VERSION, REPOQC_VERSION, FEPACKAGER_VERSION.
- `LINT_SPYGLASS_VERSION`, `OL_SPYGLASS_VERSION`, `LINT_METHODOLOGY_VERSION`, `OL_METHODOLOGY_VERSION` — not found in any Cheetah config layer; set to TBD.

### Expanded `dv_tool_version.cfg` with new DV tool versions
Added: dvt, moab, stratus, utdb, socfusegen, gtkp, wxe_version, xlm_version (Palladium), hdlice_version, ixcom_version, lec_version (DV Palladium), pal_script_version, pal_dw_version, protocompiler, fpga_vcs, fpga_verdi, haps_dc_version.

### Added sim_params for QuestaSim and Riviera-PRO
- `global_config/sim_params/questa_params.cfg` — shared analyze/elab settings for questa/questasw flows.
- `global_config/sim_params/riviera_params.cfg` — shared analyze/elab settings for riviera/rivierasw flows.

### Migrated 26 static tool configs (activity=static)
New `tools/` directories: fc, jasper, lec, mint, powerartist, psg_lift, psg_roap, puni, repoqc, rtla, sglint, sgol, socbuilder, ub, ipqc, xceliumsw, fepackager, questa, riviera, fishtail, h2b, pprtl, upf_utils, vc_lp, sgcdc, sgdft.
- `xceliumsw_tool.cfg` and `riviera_tool.cfg` are thin wrappers re-including the parent tool.

### Migrated 15 DV tool configs (activity=dv)
New `tools/` directories: euclide, haps, dvt, fuseflow, jasperdv, moab, palladium, questasim, questasimmpp, specman, stratus, utdb, vcssimemu, vcssimmpp, vcssimmppxprop.
- questasimmpp, vcssimemu, vcssimmpp, vcssimmppxprop are thin wrappers re-including parent tool (all share same binary at tool level; differences are flow-level flags only).

### Migrated 13 flow configs
New `flows/` directories: questa, questasw, riviera, rivierasw, fishtail, h2b, pprtl, upf_utils, vc_lp, sgcdc, sgdft, udm_vcs, xceliumsw.
- udm_vcs_flow.cfg inherits vcs_flow.cfg via @include; overrides PASS, FILELIST, VERILOG_ANALYZE_OPTS.
- xceliumsw_flow.cfg uses xcelium_params.cfg from sim_params/.

### Documented Cheetah-specific and ambiguous tools in migration_status.md
Cheetah-specific (not migrated): cheetah-rtl, iflow, iflow_mako, ifeed, dv_env, runtools, simregress, lsti, lstp, trex, jestr, cth_hls, cth_mako_render, dmz, flm.
Ambiguous (awaiting user decision): effm_fpga/palladium/veloce/vps/zebu, avatar, fpga, magillem, designpackage, di2urm, rtl2lib, simwrapper, fepackagingflow, syn_caliber, syn_lec, gk-utils, identify_leafcells, intgmastr, ippwrmod, update_ship, fetimemod.

## 2026-03-27 (2)

### Updated [arc] sections in all tool configs to match arc_license.txt format
- Read `arc_license.txt` and cross-referenced all tool `[arc]` feature tokens against it.
- **Updated (remapped to arc_license.txt format):** `cadence/jasper` → `jasper_gold-lic/license` (jasper, jasperdv); `cadence/conformal` → `cadence_conformal-lic/license` (lec); all `fishtail/*` + `synopsys/TCM` consolidated to `fishtail_timeconstraint-lic/license`; `synopsys/spyglass` → `atrenta_spyglass-lic/advancedCDC` for CDC tools (sgcdc, vc_cdc, vc_rdc); `synopsys/spyglass` → `atrenta_spyglass-lic/baseLint_batch` for lint tools (sgdft, sglint, sgol, vc_lint, vc_effm, vc_ol, vc_sva, vc_common, vc_lp).
- **Not found — commented with `# NOT IN arc_license.txt — verify`:** synopsys/vc_static, synopsys/vcsmx, synopsys/fusioncompiler, synopsys/vcformal, synopsys/rtla, synopsys/primepower, synopsys/verdi*, synopsys/designcompiler, synopsys/lynx, synopsys/euclide, synopsys/protocompiler, synopsys/zebu, mentor/tessent, mentor/questasim, mentor/visualizer, mentor/veloce, mentor/vps, cadence/xcelium, cadence/palladium, cadence/specman, cadence/Stratus, ansys/powerartist, amiq/dvt, defacto/STAR, synopsys/coretools, xilinx/vivado.
- 46 tool.cfg files updated; all unresolved tokens logged in `migration_status.md` under "ARC License Features — Not Found in arc_license.txt".

## 2026-03-27 (3)

### Housekeeping: sim_params paths, migration_status cleanup, directory structure doc
- Fixed all `@include` references from `global_config/sim_params/` and `global_config/ip_type_params/` to the correct `global_config/proj_base/sim_params/` and `global_config/proj_base/ip_type_params/` across 15 flow configs and `template/TEMPLATE_flow.cfg`.
- Rewrote `migration_status.md`: concise tables of migrated tools (74), migrated flows (22), Cheetah-specific skipped tools, ambiguous/deferred tools, open issues, and ARC feature gap table.
- Created `template/directory_structure.md`: visual tree of `ace_demo/`, explanation of `tool.cfg` and `flow.cfg` structure, config hierarchy and load order, and key resolution syntax table.

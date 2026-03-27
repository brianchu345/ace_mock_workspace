# ACE Migration Status

**Key:** ✅ Done | ⚠️ Done with open issue | 🔲 Not migrated | ❌ Skipped (Cheetah-specific)

---

## Tools — Migrated (74)

| Tool | Activity | Notes |
|---|---|---|
| `cc` | static | GCC wrapper; no license |
| `certitude` | static | ARC: `synopsys/vcsmx` not in arc_license.txt |
| `cf_utils` | static | PSG utility scripts; no EDA license |
| `cfgip` | static | PSG cfgip.py; no license |
| `collage` | static | ⚠️ `COLLAGE_VERSION` TBD |
| `collage_tb` | static | ⚠️ `CORE_TOOLS_VERSION` TBD; ARC: `synopsys/coretools` not in arc_license.txt |
| `coretools` | static | ⚠️ `CORE_TOOLS_VERSION` TBD; ARC: `synopsys/coretools` not in arc_license.txt |
| `cpp` | static | g++ wrapper; no license |
| `crb` | static | DVB CRB; no EDA license |
| `crflow` | static | Cheetah dir is `crflow` (no underscore) |
| `ctf` | static | PSG CTF; no license |
| `defacto` | static | ⚠️ ARC: `defacto/STAR` not in arc_license.txt |
| `design_intent` | static | Uses `magillem-lic/license` (found in arc_license.txt) |
| `dvt` | dv | ⚠️ ARC: `amiq/dvt` not in arc_license.txt |
| `euclide` | dv | ⚠️ ARC: `synopsys/euclide` not in arc_license.txt |
| `fc` | static | ⚠️ ARC: `synopsys/fusioncompiler` not in arc_license.txt |
| `fepackager` | static | No license |
| `fishtail` | static | ARC updated to `fishtail_timeconstraint-lic/license` ✅ |
| `fuseflow` | dv | No EDA license |
| `h2b` | static | ⚠️ ARC: `synopsys/lynx` not in arc_license.txt |
| `haps` | dv | ⚠️ ARC: `synopsys/protocompiler`, `xilinx/vivado` not in arc_license.txt |
| `ipqc` | static | No license |
| `jasper` | static | ARC updated to `jasper_gold-lic/license` ✅ |
| `jasperdv` | dv | ARC updated to `jasper_gold-lic/license` ✅ |
| `lec` | static | ARC updated to `cadence_conformal-lic/license` ✅ |
| `mint` | static | ⚠️ ARC: `mentor/tessent`, `synopsys/vcsmx`, `synopsys/verdi3` not in arc_license.txt |
| `moab` | dv | Cadence job scheduler; no EDA license |
| `palladium` | dv | ⚠️ ARC: `cadence/palladium` not in arc_license.txt |
| `powerartist` | static | ⚠️ ARC: `ansys/powerartist`, `synopsys/designcompiler`, `synopsys/DesignWareLibrary` not in arc_license.txt |
| `pprtl` | static | ⚠️ ARC: `synopsys/primepower`, `synopsys/rtla` not in arc_license.txt |
| `psg_lift` | static | No license |
| `psg_roap` | static | ⚠️ Version not in any global config; confirm with PSG team |
| `puni` | static | No license |
| `questa` | static | ⚠️ ARC: `mentor/questasim`, `mentor/visualizer` not in arc_license.txt |
| `questasim` | dv | ⚠️ ARC: `mentor/questasim` not in arc_license.txt |
| `questasimmpp` | dv | Thin wrapper over `questasim_tool.cfg` |
| `repoqc` | static | No license |
| `riviera` | static | No ARC (Riviera license via env) |
| `rtla` | static | ⚠️ ARC: `synopsys/rtla`, `synopsys/dc` not in arc_license.txt |
| `sgcdc` | static | ARC updated to `atrenta_spyglass-lic/advancedCDC` ✅; `synopsys/designcompiler` not in arc_license.txt |
| `sgdft` | static | ARC updated to `atrenta_spyglass-lic/baseLint_batch` ✅; `synopsys/designcompiler` not in arc_license.txt |
| `sglint` | static | ⚠️ ARC updated; `LINT_SPYGLASS_VERSION` TBD in static_tool_version.cfg |
| `sgol` | static | ⚠️ ARC updated; `OL_SPYGLASS_VERSION` TBD in static_tool_version.cfg |
| `socbuilder` | static | No license |
| `specman` | dv | ⚠️ ARC: `cadence/specman` not in arc_license.txt |
| `stratus` | dv | ⚠️ ARC: `cadence/Stratus` not in arc_license.txt |
| `ub` | static | ⚠️ ARC: `mentor/tessent` not in arc_license.txt |
| `upf_utils` | static | ⚠️ ARC: `synopsys/vc_static` not in arc_license.txt |
| `utdb` | dv | No license |
| `vc_cdc` | static | ARC: `atrenta_spyglass-lic/advancedCDC` ✅; `synopsys/vc_static` not in arc_license.txt |
| `vc_common` | static | ARC: `atrenta_spyglass-lic/baseLint_batch` ✅; `synopsys/vc_static` not in arc_license.txt |
| `vc_effm` | static | ARC: `atrenta_spyglass-lic/baseLint_batch` ✅; `synopsys/vc_static` not in arc_license.txt |
| `vc_lint` | static | ARC: `atrenta_spyglass-lic/baseLint_batch` ✅; `synopsys/vc_static` not in arc_license.txt |
| `vc_lp` | static | ARC: `atrenta_spyglass-lic/baseLint_batch` ✅; `synopsys/vc_static`, `synopsys/verdi3` not in arc_license.txt |
| `vc_ol` | static | ARC: `atrenta_spyglass-lic/baseLint_batch` ✅; `synopsys/vc_static` not in arc_license.txt |
| `vc_rdc` | static | ARC: `atrenta_spyglass-lic/advancedCDC` ✅; `synopsys/vc_static` not in arc_license.txt |
| `vc_sva` | static | ARC: `atrenta_spyglass-lic/baseLint_batch` ✅; `synopsys/vc_static` not in arc_license.txt |
| `vcformal` | static | ⚠️ ARC: `synopsys/vcformal` not in arc_license.txt |
| `vcs` | static | ⚠️ ARC: `vcs-vcsmx-lic`, `synopsys_verdi-lic` — looks like ARC format but not in provided arc_license.txt; verify |
| `vcssim` | dv | ⚠️ ARC: `synopsys/vcsmx` not in arc_license.txt |
| `vcssimemu` | dv | Thin wrapper over `vcssim_tool.cfg` |
| `vcssimmpp` | dv | Thin wrapper over `vcssim_tool.cfg` |
| `vcssimmppxprop` | dv | Thin wrapper over `vcssim_tool.cfg` |
| `vcssimzoix` | dv | ⚠️ ARC: `synopsys/vcsmx` not in arc_license.txt |
| `veloce` | dv | ⚠️ ARC: `mentor/veloce` not in arc_license.txt |
| `verdi` | static | ⚠️ ARC: `synopsys/verdi` not in arc_license.txt |
| `visa` | static | RTL variant (5.3.3) |
| `visadv` | dv | DV variant |
| `vps` | dv | ⚠️ ARC: `mentor/vps`, `xilinx/vivado` not in arc_license.txt |
| `wrap_gen` | static | No license |
| `xcelium` | static | ⚠️ ARC: `cadence/xcelium`, `synopsys/verdi` not in arc_license.txt |
| `xceliumsim` | dv | ⚠️ ARC: `cadence/xcelium` not in arc_license.txt |
| `xceliumsw` | static | Thin wrapper over `xcelium_tool.cfg` |
| `zebu` | dv | ⚠️ ARC: `synopsys/zebu`, `xilinx/vivado` not in arc_license.txt |

---

## Flows — Migrated (22)

| Flow | Corresponding Tool | Notes |
|---|---|---|
| `ctech` | `ctech` (Cheetah-internal) | Flow only; no ACE tool config (Cheetah-specific runner) |
| `design_intent` | `design_intent` | Flow + tool both migrated |
| `fishtail` | `fishtail` | Flow + tool both migrated |
| `h2b` | `h2b` | Flow + tool both migrated |
| `pprtl` | `pprtl` | Flow + tool both migrated |
| `questa` | `questa` | Flow + tool; uses `proj_base/sim_params/questa_params.cfg` |
| `questasw` | `questa` | SW variant; reuses `questa_tool.cfg` |
| `riviera` | `riviera` | Flow + tool; uses `proj_base/sim_params/riviera_params.cfg` |
| `rivierasw` | `riviera` | SW variant; reuses `riviera_tool.cfg` |
| `sgcdc` | `sgcdc` | Flow + tool both migrated |
| `sgdft` | `sgdft` | Flow + tool both migrated |
| `udm_vcs` | `vcs` | Inherits from `vcs_flow.cfg` |
| `upf_utils` | `upf_utils` | Flow + tool both migrated |
| `vc_cdc` | `vc_cdc` | Flow + tool both migrated |
| `vc_lint` | `vc_lint` | Flow + tool both migrated |
| `vc_lp` | `vc_lp` | Flow + tool both migrated |
| `vcs` | `vcs` | Uses `proj_base/sim_params/vcs_params.cfg` |
| `vcsdv` | `vcssim` | DV variant; reuses `vcssim_tool.cfg` |
| `vcsdvpp` | `vcssim` | DV++ variant |
| `vcssw` | `vcs` | SW variant |
| `xcelium` | `xcelium` | Uses `proj_base/sim_params/xcelium_params.cfg` |
| `xceliumsw` | `xceliumsw` | SW variant; reuses `xcelium_tool.cfg` |

---

## Tools — Not Migrated (Cheetah-Specific)

These are Cheetah infrastructure components with no ACE equivalent needed.

| Tool | Reason |
|---|---|
| `iflow` | Cheetah internal flow runner |
| `iflow-mako` | Cheetah template engine |
| `ifeed` | Cheetah internal |
| `runtools` | Cheetah job dispatcher |
| `cth_hls` | Cheetah HLS wrapper |
| `cth_query` | Cheetah config query CLI |
| `cheetah_rtl_root` | Cheetah install root |
| `pesg_fe.baseline_tools` | Cheetah-side PSG baseline layer |
| `fpga` | References `CHEETAH_RTL_ROOT`; Cheetah-specific |
| `magillem` | Delegated to `pesg_fe.baseline_tools`; covered by `design_intent` |
| `sim` | Cheetah simulation dispatcher |

---

## Tools — Ambiguous / Deferred (Need Decision)

| Tool | Blocker |
|---|---|
| `effm_fpga` | Are these RTL-side emulation configs distinct from DV tools (`haps`, `palladium`, etc.)? Needs clarification. |
| `effm_palladium` | Same as above |
| `effm_veloce` | Same as above |
| `effm_vps` | Same as above |
| `effm_zebu` | Same as above |
| `avatar` | Hardcoded project path (`AVATAR_PROJECT = nadder_fcv`); genericize or skip? |
| `fetimemod` | Extremely complex (LibraryCompiler + PrimeTime + BCM + kite); prioritize? |
| `rtl2lib` | Uncommon; migrate or defer? |
| `simwrapper` | Uncommon; migrate or defer? |
| `di2urm` | Uncommon; migrate or defer? |
| `syn_caliber` | Uncommon; migrate or defer? |
| `syn_lec` | Uncommon; migrate or defer? |
| `designpackage` | Uncommon; migrate or defer? |

---

## Open Issues

| # | Issue | Status |
|---|---|---|
| 1 | `LINT_SPYGLASS_VERSION`, `LINT_METHODOLOGY_VERSION` — not found in any Cheetah config layer. Set TBD in `static_tool_version.cfg`. | Open |
| 2 | `OL_SPYGLASS_VERSION`, `OL_METHODOLOGY_VERSION` — same as above. | Open |
| 3 | `psg_roap` version not in any global config. Confirm with PSG team. | Open |
| 4 | `COLLAGE_VERSION`, `CORE_TOOLS_VERSION` — not resolvable without `cth_psetup_fe`. Confirm version strings. | Open |
| 5 | `effm_*` tools — determine if RTL-side emulation configs need separate ACE entries or collapse into DV tools. | Open |
| 6 | 28 ARC feature tokens not found in `arc_license.txt` (see table below). Verify correct resource names with ARC/licensing team. | Open |

---

## ARC Features Not in `arc_license.txt`

These are commented `# NOT IN arc_license.txt — verify` in each tool config.

| Feature Token | Used By |
|---|---|
| `synopsys/vc_static` | vc_cdc, vc_lint, vc_effm, vc_ol, vc_rdc, vc_sva, vc_common, vc_lp, upf_utils |
| `synopsys/vcsmx` | certitude, mint, vcssim, vcssimzoix |
| `synopsys/fusioncompiler` | fc |
| `synopsys/vcformal` | vcformal |
| `synopsys/rtla` | rtla, pprtl |
| `synopsys/primepower` | pprtl |
| `synopsys/verdi` / `synopsys/verdi3` | xcelium, vc_lp, mint |
| `synopsys/designcompiler` / `synopsys/dc` | sgcdc, sgdft, sglint, sgol, powerartist, rtla |
| `synopsys/lynx` | h2b |
| `synopsys/euclide` | euclide |
| `synopsys/protocompiler` | haps |
| `synopsys/zebu` | zebu |
| `synopsys/DesignWareLibrary` | powerartist |
| `mentor/tessent` | mint, ub |
| `mentor/questasim` | questa, questasim |
| `mentor/visualizer` | questa |
| `mentor/veloce` | veloce |
| `mentor/vps` | vps |
| `cadence/xcelium` | xcelium, xceliumsim |
| `cadence/palladium` | palladium |
| `cadence/specman` | specman |
| `cadence/Stratus` | stratus |
| `ansys/powerartist` | powerartist |
| `amiq/dvt` | dvt |
| `defacto/STAR` | defacto |
| `synopsys/coretools` | coretools, collage_tb |
| `xilinx/vivado` | haps, vps, zebu |
| `vcs-vcsmx-lic` / `synopsys_verdi-lic` | vcs (already ARC-style; confirm token is current) |

**Mapped and updated (old Cheetah → arc_license.txt):**

| Old Token | New Token |
|---|---|
| `cadence/jasper` | `jasper_gold-lic/license` |
| `cadence/conformal` | `cadence_conformal-lic/license` |
| `fishtail/confirm` + `/refocus` + `/focus` + `synopsys/TCM` | `fishtail_timeconstraint-lic/license` |
| `synopsys/spyglass` (CDC: sgcdc, vc_cdc, vc_rdc) | `atrenta_spyglass-lic/advancedCDC` |
| `synopsys/spyglass` (lint: sgdft, sglint, sgol, vc_lint, vc_effm, vc_ol, vc_sva, vc_common, vc_lp) | `atrenta_spyglass-lic/baseLint_batch` |

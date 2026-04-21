# PSG FE Checker Utilities — Reference Guide

`PSG_FE_CHECKER_UTILITIES_HOME` points to a versioned install of the `psg_fe_checker_utilities`
package at `/p/cth/cad/psg_fe_checker_utilities/<version>/`.

In Cheetah it was resolved dynamically via `toolversion(psg_fe_checker_utilities)` in
`psg_tools.cth`. In ACE it is a static `[params]` version in `vc_cdc_tool.cfg`
(currently `1.27.2` — the minimum version that includes the `vccdc_methodology/` subtree
and all vc_cdc-specific scripts).

---

## What it provides

### `bin/` — post-processing and audit scripts

All Python scripts import `from dmx.tnrlib.audit_check import AuditFile`. This is the
**DMX (Design Management eXchange)** library — Intel's Cheetah release/ICM infrastructure.
The audit scripts generate signed XML audit files consumed by the Cheetah GK (gatekeeper) system.

**DMX_LIB** must be set for these to run (resolved via `cth_query ENVS DMX_LIB -resolve`
in Cheetah). These scripts are effectively **Cheetah-GK-only** in their current form.

| Script | Used by flow | Purpose |
|--------|-------------|---------|
| `gen_vcs_audit.py` | `vcs`, `vcsdv`, `vcssw`, `vcsdvpp` | Generates DMX audit file from VCS compile/elab logs |
| `gen_xcelium_audit.py` | `xcelium`, `xceliumsw` | Generates DMX audit file from Xcelium run |
| `gen_questa_audit.py` | `questa`, `questasw` | Generates DMX audit file from Questa run |
| `gen_riviera_audit.py` | `riviera`, `rivierasw` | Generates DMX audit file from Riviera run |
| `gen_vccdc_audit.py` | `vc_cdc` (via `run_audit`) | Generates DMX audit file from VC-CDC run results |
| `gen_vclint_audit.py` | `vc_lint` (via `run_audit`) | Generates DMX audit file from VC-Lint run results |
| `gen_sgcdc_audit.py` | `sgcdc` | Generates DMX audit file from SpyGlass CDC run |
| `gen_sgdft_audit.py` | `sgdft` (via `run_audit`) | Generates DMX audit file from SpyGlass DFT run |
| `gen_sglint_audit.py` | `sglint` | Generates DMX audit file from SpyGlass Lint run |
| `gen_effm_veloce_audit.py` | `effm_veloce` | Generates DMX audit file from Veloce emulation run |
| `check_sip_cdc_abstract.py` | `sgcdc` | Checks that the CDC abstract (SIP) is up to date |
| `check_sip_vccdc_abstract.py` | `vc_cdc` (via `run_audit`) | Checks that the VC-CDC abstract is up to date; reads `$RUN_SETTINGS_FILE` |
| `altera_vc_cdc_check.py` | `vc_cdc` (`Makefile.inc`) | Post-run GK qualification check for VC-CDC; called manually as `make altera_vc_cdc_check` |
| `altera_vc_lint_check.py` | `vc_lint` (`Makefile.inc`) | Post-run GK qualification check for VC-Lint |
| `vc_cdc_synchronizer_audit.pl` | `vc_cdc` (via `run_audit`) | Parses the CDC detailed report, audits synchronizer usage against allowed cell list |
| `synchronizer_audit.pl` | `sgcdc` | Same as above but for SpyGlass CDC report format |
| `run_rtl_encryption.py` | `vcs`, `vcsdv`, `vcssw`, `vcsdvpp`, `questa`, `questasw`, `xcelium`, `xceliumsw`, `riviera`, `rivierasw` | Tests that RTL files are syntactically encryptable by the target simulator (run after compilation) |
| `extract_define.py` | `questasw`, `vcssw` (via `run_audit`) | Extracts `+define+` flags from compile log and writes a `.f` file for software-view re-runs |
| `setup_riviera_run.py` | `riviera` | Generates Riviera-specific run scripts from design configuration |
| `setup_sdc2sgdc_run.py` | `vc_cdc` (`sdc2sgdc` Makefile target) | Generates TCL + SDC constraint wrapper for sdc2sgdc CDC flow |

### `vccdc_methodology/` — VC-CDC Synopsys methodology

Referenced as `$PSG_FE_CHECKER_UTILITIES_HOME/vccdc_methodology/`.

| File / dir | Purpose |
|-----------|---------|
| `altera_vc_cdc_settings.tcl` | **Mandatory** VC-CDC run settings; sourced by `inputs/run_opts.tcl` in every vc_cdc run |
| `CDCRDCRulesOvs.tcl` | CDC/RDC rule overrides (suppressions, severity adjustments) |
| `CDC_post_opts.tcl` | Post-analysis processing options |
| `cdc_global_waiver.swl` | Global project-level CDC waivers applied to every run |
| `cdc_0.5_waivers.tcl` | Milestone 0.5 waiver set |
| `cdc_0.8_waivers.tcl` | Milestone 0.8 waiver set |
| `cdc_1.0_waivers.tcl` | Milestone 1.0 waiver set |
| `cdcqa_waivers.txt` | CDCQA waiver list (read by `CDCQA_WAIVERS` flow cfg key) |
| `valid_sync_cells.tcl` | Allowlist of recognized synchronizer cell names |
| `time_zero_waivers.tcl` | Waivers for time-zero / initialization violations |
| `master/` | Versioned methodology TCL tree (the contents of `VCCDC_METHODOLOGY_PATH`) |
| `cdcqa/<version>/bin/` | CDCQA binary for CDC quality analysis (resolved by `CDCQA_HOME`) |

### `vclint_methodology/` — VC-Lint Synopsys methodology

| File | Purpose |
|------|---------|
| `psg_vc_lint_settings.tcl` | Mandatory VC-Lint run settings; sourced by `vc_lint/inputs/run_settings.tcl` |
| `psg_vc_lint_compile_settings.tcl` | Compile-phase settings; sourced by `vc_lint/inputs/compile_settings.tcl` |
| `LintRulesOvs.tcl` | Lint rule overrides |
| `time_zero_waivers.tcl` | Time-zero waivers |
| `policies/` | Policy files for lint severity |

### `cdc_methodology/` — SpyGlass CDC methodology

| File | Purpose |
|------|---------|
| `psg_sgcdc_settings.tcl` | SpyGlass CDC run settings; sourced by `sgcdc/inputs/dft_run.tcl` |
| `cdc_global_waiver.swl` | Global waiver file for SpyGlass CDC |
| `block/` | Block-level CDC settings |

### `sgdft_methodology/` — SpyGlass DFT methodology

Sourced by `sgdft/inputs/dft_run.tcl` and `sgdft/inputs/analyze.tcl`. Provides Altera-specific
SpyGlass DFT settings and rule overrides.

### `sglint_methodology/` — SpyGlass Lint methodology

Referenced by `sglint` flow. Contains first-phase RTL lint policy files.

---

## How it is invoked across ioss3 flows

### Pattern 1 — Makefile post-processing target (mandatory GK step)
```makefile
# All simulators: vcs, questa, xcelium, riviera, vcssw, questasw, xceliumsw, rivierasw
${PSG_FE_CHECKER_UTILITIES_HOME}/bin/run_rtl_encryption --cells ${DUT} --vcs

# Static check flows: vc_cdc, vc_lint
${PSG_FE_CHECKER_UTILITIES_HOME}/bin/altera_vc_cdc_check.py ${TOP_IP_NAME} ${DUT} ...
```

### Pattern 2 — `run_audit` CSV (POST_PROCESSING_FILE, executed by flow wrapper)
```
$PSG_FE_CHECKER_UTILITIES_HOME/bin/check_sip_vccdc_abstract.py,$DUT,$RUN_SETTINGS_FILE
$PSG_FE_CHECKER_UTILITIES_HOME/bin/vc_cdc_synchronizer_audit.pl,<report_path>,...
$PSG_FE_CHECKER_UTILITIES_HOME/bin/gen_vccdc_audit.py,$TOP_IP_NAME,$DUT,$TOP_MODULE_NAME,$PASS
```

### Pattern 3 — TCL `source` inside tool run scripts
```tcl
# inputs/run_opts.tcl (vc_cdc)
source $::env(PSG_FE_CHECKER_UTILITIES_HOME)/vccdc_methodology/altera_vc_cdc_settings.tcl

# inputs/run_settings.tcl (vc_lint)
source $::env(PSG_FE_CHECKER_UTILITIES_HOME)/vclint_methodology/psg_vc_lint_settings.tcl
```

### Pattern 4 — flow cfg path references
```ini
# vc_cdc tool.cth / vc_cdc_tool.cfg
VCCDC_METHODOLOGY_PATH = envs(PSG_FE_CHECKER_UTILITIES_HOME)/vccdc_methodology/master
CDC_MILESTONE_GLOBAL_WAIVER_PATH = envs(PSG_FE_CHECKER_UTILITIES_HOME)/vccdc_methodology
CDCQA_HOME = envs(PSG_FE_CHECKER_UTILITIES_HOME)/vccdc_methodology/cdcqa/<version>/bin

# vc_lint tool.cth
LINT_MILESTONE_GLOBAL_WAIVER_PATH = envs(PSG_FE_CHECKER_UTILITIES_HOME)/vclint_methodology
```

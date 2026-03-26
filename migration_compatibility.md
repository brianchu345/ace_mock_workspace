# ACE Migration — Compatibility Notes

This document captures known incompatibilities and difficulties when migrating
Cheetah-based flows to ACE. It is a living document — update it as new issues surface.

---

## 1. DMX audit scripts cannot run without Cheetah/GK infrastructure (HIGH IMPACT)

**Affected scripts** (all in `$PSG_FE_CHECKER_UTILITIES_HOME/bin/`):

```
gen_vccdc_audit.py       gen_vcs_audit.py        gen_questa_audit.py
gen_vclint_audit.py      gen_sgcdc_audit.py       gen_sgdft_audit.py
gen_xcelium_audit.py     gen_riviera_audit.py     gen_effm_veloce_audit.py
check_sip_vccdc_abstract.py   check_sip_cdc_abstract.py
altera_vc_cdc_check.py   altera_vc_lint_check.py
```

All of these import:
```python
from dmx.tnrlib.audit_check import AuditFile
```

`dmx` is the Intel ICM/Cheetah release library. It requires `DMX_LIB` to be set
(previously resolved at runtime via `cth_query ENVS DMX_LIB -resolve`). Without it
these scripts will crash at import time.

**In ACE** the `run_audit` mechanism (`POST_PROCESSING_FILE`) calls these scripts as
post-processing steps. If the intention is to produce GK-compatible audit XML, the
ACE wrapper will need to either:
- Provide its own `DMX_LIB` resolution (if DMX is available outside Cheetah), or
- Replace the audit generation step with an ACE-native results check

Until resolved, comment out or remove the `run_audit` CSV entries that invoke DMX scripts.
The `vccdc_methodology` TCL files (Pattern 3 sourcing) are **not** DMX-dependent and are safe.

---

## 2. `PSG_FE_CHECKER_UTILITIES_VERSION` must be >= 1.27.x (MEDIUM IMPACT)

The Cheetah Makefile originally resolved the version dynamically via
`toolversion(psg_fe_checker_utilities)`. The ACE tool cfg pins it to a static
`[params]` value.

- Versions < 1.27.x do **not** include `vccdc_methodology/`, `altera_vc_cdc_settings.tcl`,
  `gen_vccdc_audit.py`, `vc_cdc_synchronizer_audit.pl`, `altera_vc_cdc_check.py`, or
  `check_sip_vccdc_abstract.py`.
- The `run_audit` file and `inputs/run_opts.tcl` will silently fail or error if pointed
  at an old version.

**Current pin**: `1.27.2`. Bump this in `vc_cdc_tool.cfg` when a newer release is qualified.
Track available versions at `/p/cth/cad/psg_fe_checker_utilities/`.

---

## 3. `cth_query` is gone — any script calling it at runtime will fail (HIGH IMPACT)

Cheetah Makefiles and some Python scripts call `cth_query` at runtime to resolve env vars:

```bash
export PSG_FE_CHECKER_UTILITIES_HOME=$(cth_query ENVS PSG_FE_CHECKER_UTILITIES_HOME -resolve)
export MILESTONE=$(cth_query Params REPO_milestone)
export TOP_IP_NAME=$(cth_query -file ${WORKAREA}/cfg/${DUT}.design.cfg global_config TOP_IP_NAME)
```

In ACE, the config parser resolves these before any tool runs. Flow wrappers should read
values directly from the resolved ACE config namespace. Existing scripts (`extract_vcs_command_full.py`,
`run_vcs_compile_elab.sh`, `gen_xcelium_chipstack_yaml.py`) that still call `cth_query`
at runtime need to be rewritten to accept these values as arguments or environment variables
injected by the ACE wrapper.

---

## 4. `run_rtl_encryption.py` — RTL encryptability check portability (LOW-MEDIUM IMPACT)

Used by all simulator flows (`vcs`, `questa`, `xcelium`, `riviera`, `*sw` variants) as a
post-compile step. It also imports `UsrIntel.R1` (Intel-internal Python module) and possibly
DMX. Whether it can run standalone outside Cheetah depends on those imports.

If ACE is used in an environment without `UsrIntel.R1`, this script will fail at import time.
The ACE wrapper should make this step conditional or replaceable.

---

## 5. `CHEETAH_RTL_ROOT` used in `riviera`/`rivierasw` flows (MEDIUM IMPACT)

The Cheetah `riviera` and `rivierasw` Makefiles derive:
```makefile
export CHEETAH_RTL_ROOT = ${PSG_FE_CHECKER_UTILITIES_HOME}/data/cheetah-rtl-root
```

This means those flows depend on a specific subdirectory inside `psg_fe_checker_utilities`
that acts as a Cheetah-RTL root proxy. In ACE, this path no longer exists in the same way.
Flow owners converting `riviera`/`rivierasw` must identify what `CHEETAH_RTL_ROOT` provides
(Makefile includes, flow scripts) and replicate those dependencies directly.

---

## 6. Milestone waiver selection previously done at runtime (LOW IMPACT)

In Cheetah, the `Makefile.inc` resolved `MILESTONE` via:
```makefile
export MILESTONE := $(shell cth_query Params REPO_milestone)
```
and then selected `${MILESTONE}_flow.cfg` at runtime.

In ACE, the milestone is the git branch — there is no runtime selection. The waiver TCL
files in `vccdc_methodology/` (`cdc_0.5_waivers.tcl`, `cdc_0.8_waivers.tcl`,
`cdc_1.0_waivers.tcl`) are still available and the correct one should be loaded by
`altera_vc_cdc_settings.tcl` based on the configured milestone. Confirm with the
methodology owner that `altera_vc_cdc_settings.tcl` does not rely on `cth_query` to
determine which waiver set to load.

---

## 7. `VCCOMMON_METHODOLOGY_PATH` points to HDK, not PSG utilities (LOW IMPACT)

Unlike `VCCDC_METHODOLOGY_PATH` (overridden by ioss3 to use `PSG_FE_CHECKER_UTILITIES_HOME`),
`VCCOMMON_METHODOLOGY_PATH` still points to:
```
/p/hdk/rtl/proj_tools/vc_methodology_common/master
```
This is a Synopsys-maintained HDK path, not a PSG utilities path. It requires access to
the HDK disk. If ACE is ever used in an environment without HDK access, this path will
need to be re-homed.

---

## 8. `sdc2sgdc` target requires `setup_sdc2sgdc_run.py` (LOW IMPACT)

The `sdc2sgdc` Makefile target in `vc_cdc/Makefile.inc` calls:
```makefile
make sgcdc_run PASS=sdc2sgdc ...
```

The `setup_sdc2sgdc_run.py` script reads YAML config files and generates run TCL. In ACE
this target is not yet reflected in the `vc_cdc.Makefile`. If sdc2sgdc is needed, a
dedicated `%__vc_cdc_sdc2sgdc` pattern rule must be added.

---

## Summary table

| Issue | Impact | ACE action needed |
|-------|--------|-------------------|
| DMX audit scripts require `dmx.tnrlib` | High | Replace or gate audit steps |
| `cth_query` called at runtime in scripts | High | Rewrite scripts to take ACE-resolved values |
| `PSG_FE_CHECKER_UTILITIES_VERSION` must be >= 1.27.x | Medium | Already fixed to 1.27.2 |
| `run_rtl_encryption.py` needs `UsrIntel.R1` | Medium | Make step conditional |
| `riviera`/`rivierasw` use `CHEETAH_RTL_ROOT` via psg_fe_checker_utilities | Medium | Identify and replicate dependencies |
| Milestone waiver selection via `cth_query` in methodology TCL | Low | Confirm with methodology owner |
| `VCCOMMON_METHODOLOGY_PATH` → HDK path | Low | Re-home if HDK is unavailable |
| `sdc2sgdc` target not in `vc_cdc.Makefile` | Low | Add pattern rule if needed |

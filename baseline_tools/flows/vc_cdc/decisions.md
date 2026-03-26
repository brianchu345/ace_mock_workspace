# VC-CDC Flow — Design Decisions

## Cheetah → ACE conversion summary

| Cheetah concept | ACE equivalent |
|----------------|----------------|
| `[INCLUDES] tool.cth` chains | Removed — wrapper reads tool and flow cfg independently |
| `[ToolVersion] / toolversion()` function | `[params]` version strings + `params()` resolution |
| `[License] feature = synopsys/vc_static` | `[arc]` token list in `vc_cdc_tool.cfg` |
| `cth_query -tool vc_cdc ENVS ...` in Makefile | Removed — ACE config parser replaces `cth_query` |
| `CHEETAH_RTL_ROOT` / `FLOW_ROOT` / `RTL_UTIL_ROOT` | Removed — no Cheetah runtime dependency |
| Per-milestone `*_flow.cfg` include switch | Single flow.cfg per branch; milestone is a git branch |

## Why there is only one `vc_cdc_flow.cfg` (not one per milestone)

In Cheetah the project workspace included `${MILESTONE}_flow.cfg` at runtime to select
the active milestone. In ACE, the baseline_tools repo is branched per milestone and project
(`<project>/<milestone>`). The branch itself IS the milestone selector — there is nothing to
switch at runtime. Only the contents of the checked-out branch matter.

This file is locked to milestone **1.0** (`CHECK = setup cdc`). To create a 0.5 baseline
(setup-only), branch this repo and change `CHECK = setup`.

## Why `stdcell_filelist/` lives in the flow directory

In Cheetah, the stdcell filelist lived under `baseline_tools/vc_cdc/stdcell_filelist/`.
ACE co-locates all flow-specific inputs alongside the flow config so the flow directory is
self-contained. The wrapper reads `CDC_STD_BMOD` from `[vc_cdc]` and does not need to know
the baseline_tools directory layout.

Three PDK variants are kept (`alynx`, `km`, `n3c`). The active variant is selected by the
`CDC_STD_BMOD` key in the flow cfg (default: `alynx` for N3 143H). User overrides can point
to a different variant without touching the flow cfg.

## Why `run_audit` and `inputs/run_opts.tcl` are in the flow directory

`run_audit` is a CSV-like list of post-processing scripts consumed by the flow wrapper after
vc_cdc completes. It references `$PSG_FE_CHECKER_UTILITIES_HOME` env vars that are already
resolved by the time the wrapper runs. It is flow-specific, not tool-specific.

`inputs/run_opts.tcl` sources the mandatory Altera CDC settings TCL from
`$PSG_FE_CHECKER_UTILITIES_HOME`. The "DO NOT EDIT" banner is preserved from the Cheetah
original — the file should remain a thin shim that sources the upstream TCL.

## Why the Makefile drops `cth_query` calls

All configuration that `Makefile.inc` previously resolved via `cth_query` (MILESTONE,
TOP_IP_NAME, PSG_FE_CHECKER_UTILITIES_HOME, etc.) is now resolved by the ACE config parser
at wrapper invocation time. The Makefile only needs to know the wrapper path and DUT name.

## Why `ALTR_VC_CDC_ANALYZE_SETTINGS` is in `[params]`, not `[vc_cdc]`

Base flag strings that should not be user-overridden go in `[params]`. Only composable
feature switches that are expected to vary between runs or users go in `[vc_cdc]`.
`-format sverilog -verbose` is a fixed baseline choice, not a per-run decision.

## Why `CREATE_OUTDIR_LINK = false`

Creating a `latest` symlink causes race conditions in parallel multi-DUT runs and is
unnecessary when the wrapper writes structured output to `output/<dut>/vc_cdc/<pass>/`.
Flow owners can enable it in `user_override/vc_cdc/vc_cdc_flow_override.cfg` if needed.

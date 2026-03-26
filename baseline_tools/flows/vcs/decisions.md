# VCS Flow — Design Decisions

## Why `[vcs]` is the user-overrideable namespace

All keys that a flow wrapper reads from the composed command line live in `[vcs]`, not `[params]`.
`[params]` values are immutable base strings (flag fragments); `[vcs]` values are composable
switches that user_override files can replace by repeating the same key in a `[vcs]` block.
The ACE config parser merges sections of the same name in order, with later definitions winning.
This gives a clean two-layer model: infra owns `[params]`, users own `[vcs]`.

## Why `DEBUG_SWITCH` defaults to empty

KDB + full signal access (`-kdb -lca -debug_access+all`) multiplies compile time and disk usage
significantly. The baseline leaves the switch empty so production and GK runs stay fast.
Users enable it in `user_override/vcs/vcs_flow_override.cfg` when debugging is needed.

## Why warn-to-error (W2E) lives in a separate `vcswarn2err.cfg`

W2E filter lists are maintained independently of the base flag strings — they get updated as
projects suppress or promote new warnings. Separating them lets the W2E lists evolve without
touching the flag composition logic. The flow cfg includes `vcswarn2err.cfg` first so W2E keys
(`W2E_ANALYZE`, `W2E_ELAB`) are available when `VERILOG_ANALYZE_OPTS` and `ELAB_OPTS_SWITCH`
are composed later in the file.

## Why ip_type includes are optional (`-` prefix)

Early in a design lifecycle, the DUT design cfg or the ip_type cfg may not exist yet.
Making them optional allows the parser to continue without error so that tool-level operations
(path resolution, license setup) can still run. The flow wrapper is expected to validate
required inputs before invoking analysis.

## Why `ALTR_VCS_ELAB_SETTINGS` uses `-full64` and not `-access +rwc`

`-access +rwc` was deprecated in VCS X-2025 and triggers `UNKWN_OPTVSIM`. Signal access for
debug is gated through `DEBUG_SWITCH = -debug_access+all` instead, keeping elab clean when
debug is not requested.

## Why `PASS = gk` is in the flow, not the tool

`PASS` is a flow-level concept (GK qualification stage), not a tool property. Different runs
of the same tool (GK vs sdc2sgdc vs other passes) would use different PASS values. Putting it
in the flow cfg lets user_override files change the pass without touching tool installation
config.

## Why the tool cfg and flow cfg never include each other

A flow wrapper reads both files independently and merges their namespaces. Coupling them via
includes would break that contract and prevent a wrapper from selectively applying one without
the other — e.g. running a tool path check without loading all flow flags.

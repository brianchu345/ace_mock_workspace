# Cheetah Baseline Tools — Findings & Dependency Analysis

This document explains how the Cheetah configuration layer works in
`ioss3_hsio/baseline_tools/`, why it is organized the way it is, and
what that means for the ACE conversion.

---

## How Cheetah resolves tool configuration (plain English)

When you run a Cheetah flow, the tool configuration is not in one file.
It is assembled by following a chain of `[INCLUDES]` — each file reads
other files first, then adds or overrides values on top.

Think of it like CSS: later rules override earlier ones. The file at the
bottom of the chain gets the final word on any value.

### The chain for a typical RTL tool

Here is the full chain for `vc_cdc` as an example, written out in the
order Cheetah processes it:

```
Step 1  /p/hdk/cad/Cheetah-RTL/2024.12.p05/rtl_tools.cth
        → Sets the ground-truth version strings for ~70 tools
          (VCS_VERSION, VERDI_VERSION, VCCDC_VERSION, etc.)
        → Sets CHEETAH_RTL_ROOT
        → Does NOT set any install paths or licenses

Step 2  ioss3_hsio/baseline_tools/pesg_fe.baseline_tools/rtl_tools.cth
        → One line: just includes Step 1
        → Adds nothing — pure redirect

Step 3  ioss3_hsio/baseline_tools/pesg_fe.baseline_tools/vc_cdc/tool.cth
        → Includes Step 2 (which chains to Step 1)
        → Composes the install path:
            VCCDC_HOME_PATH = /p/hdk/rtl/cad/...
            VC_STATIC_HOME  = VCCDC_HOME_PATH / VCCDC_VERSION
        → Adds license: synopsys/vc_static, synopsys/spyglass

Step 4  ioss3_hsio/baseline_tools/rtl_tools.cth          (project overrides)
        → Includes Step 2 again (Cheetah handles the duplicate silently)
        → Overrides ~10 version strings to project-approved values:
            VCCDC_VERSION    V-2023.12-SP2-3  →  V-2023.12-SP2-10
            VCS_VERSION      V-2023.12-SP2-3  →  W-2024.09-SP2-4
            etc.
        → Overrides some install paths from /p/hdk/ to /p/psg/eda/

Step 5  ioss3_hsio/baseline_tools/vc_cdc/tool.cth         (project tool layer)
        → Includes Step 3 (pesg_fe vc_cdc paths + license)
        → Includes Step 4 (ioss3 version overrides)
        → Adds its own version overrides on top
```

**The key rule**: if the same variable appears more than once across the chain,
the LAST definition wins. So the ioss3 project values (Steps 4 and 5)
always override the PSG and Cheetah-RTL base values.

### Why is Step 1 parsed twice?

Steps 3 and 4 each independently include `../rtl_tools.cth`, which both
chain back to the same Cheetah-RTL base file. Cheetah parses that base
file twice. This is not a bug — it is how the version override mechanism
works: Step 4 (ioss3 rtl_tools.cth) is included second so its overrides
land last and win. It is redundant processing, but intentional.

In ACE this is completely gone. One flat file, no chaining.

---

## The five layers and what each one actually does

| Layer | File | What it contributes |
|-------|------|---------------------|
| **Ground truth** | `Cheetah-RTL/.../rtl_tools.cth` | ~70 version strings only — no paths, no licenses |
| **PSG redirect** | `pesg_fe.baseline_tools/rtl_tools.cth` | Single `[INCLUDES]` line pointing at Cheetah-RTL — adds nothing |
| **PSG tool** | `pesg_fe.baseline_tools/<tool>/tool.cth` | Install path composition + `[License]` token — same pattern for every EDA tool |
| **Project versions** | `ioss3/baseline_tools/rtl_tools.cth` | ~10 version overrides + switches HDK paths to PSG mirrors (`/p/psg/eda/`) |
| **Project tool** | `ioss3/baseline_tools/<tool>/tool.cth` | For ~60 tools: zero local content (pure pass-through). For ~30 tools: a few additional version or path overrides |

The PSG redirect layer (Layer 2) exists only to decouple the ioss3 repo
from the exact Cheetah-RTL install path. If Intel ships a new
`Cheetah-RTL/2025.xx` release, only that one redirect file needs updating.

---

## How many ioss3 tool.cth files actually do anything?

Out of ~120 `ioss3/baseline_tools/<tool>/tool.cth` files:

- **~60 are pure pass-throughs** — they contain only `[INCLUDES]` lines
  with no version overrides, no envs, no licenses. They exist solely to
  chain the PSG and project layers together.
  Examples: `fc`, `questa`, `sgcdc`, `sgdft`, `sglint`, `verdi`, `visa`,
  `xceliumsw`, `vc_common`, `vc_effm`, `vc_ol`, `vc_rdc`, `vc_sva`.

- **~30 add version overrides** — they bump one or two version strings
  above the ioss3 `rtl_tools.cth` baseline.
  Examples: `vc_cdc` (VCCDC_VERSION), `vc_lint` (VCLINT_VERSION),
  `fishtail` (FISHTAIL_VERSION, VCS_VERSION).

- **~30 add local envs or paths** — tools with project-specific install
  paths or additional environment variables.
  Examples: `pprtl`, `rtla`, `magillem_assembler`, `vcs`, `flm`.

In ACE, all three categories collapse to a single `<tool>_tool.cfg`.

---

## DV tools vs RTL tools — why the versions differ

### The short answer

DV (Design Verification) tools and RTL tools are maintained by different
teams with different release schedules. They are allowed to run on
different simulator versions at the same time. The Cheetah config system
has two completely separate version registries to support this.

### The two registries

**RTL registry** — `Cheetah-RTL/2024.12.p05/rtl_tools.cth`
Managed by the RTL/synthesis infrastructure team. Covers tools used in
RTL sign-off flows: VCS (for compile/elab), Verdi, VC-CDC, VC-Lint,
SpyGlass, Fusion Compiler, etc.

**DV registry** — `/p/hdk/pu_tu/prd/baseline_tools/pesg_fe/2024.09.../dv_tools.cth`
Managed by the DV infrastructure team. Covers tools used in full-chip
verification runs: VCS sim runner (`vcssim_vcs`), Questa, Xcelium,
specman, JEM, veloce, HAPS, etc.

### They use the same tools but at different versions

For example, VCS appears in BOTH registries:

| Registry | Variable | Version | Used by |
|----------|----------|---------|---------|
| RTL | `VCS_VERSION` (ioss3 override) | W-2024.09-SP2-4 | `vcs`, `vcsdv`, `vcssw` flows — RTL compile/elab |
| DV | `vcssim_vcs` (ioss3 override) | V-2023.12-SP1-1 | `vcssim` flow — UVM testbench simulation |

The RTL team qualified and moved to W-2024.09 for their compile flow.
The DV team is still running V-2023.12-SP1-1 for simulation because their
regression infrastructure has not yet been re-validated on the newer
version.

Neither team blocks the other.

### Which tools belong to which registry

**RTL tools** (chain through `rtl_tools.cth`):
`vcs`, `vcsdv`, `vcsdvpp`, `vcssw`, `questa`, `questasw`, `xcelium`,
`xceliumsw`, `vc_cdc`, `vc_lint`, `vc_lp`, `vc_rdc`, `vc_sva`,
`vc_common`, `vc_effm`, `vc_ol`, `vcformal`, `sgcdc`, `sgdft`, `sglint`,
`sgol`, `fc`, `fishtail`, `pprtl`, `rtla`, `powerartist`, `defacto`,
`lec`, `jasper`, `upf_utils`, `mint`, `puni`, `visa`, `fepackager`,
`socbuilder`, `intgmastr`, `collage`, `flm`, `verdi`, and others.

**DV tools** (chain through `dv_tools.cth`):
`vcssim`, `vcssimmpp`, `vcssimemu`, `vcssimzoix`, `questasim`,
`questasimmpp`, `xceliumsim`, `certitude`, `cc`, `cpp`, `crb`, `crflow`,
`cth_hls`, `dvt`, `emu`, `emuvcs`, `euclide`, `fuseflow`, `haps`,
`jasperdv`, `jem`, `moab`, `palladium`, `specman`, `stratus`, `utdb`,
`veloce`, `visadv`, `vps`, `zebu`, and others.

**Spans both** (e.g. `fpga`, `effm_*`): includes both `rtl_tools.cth`
and `dv_tools.cth` because the flow uses both RTL synthesis tools and
DV simulation tools.

### What ioss3 dv_tools.cth adds beyond the DV registry

```
ioss3/baseline_tools/dv_tools.cth:

[ToolVersion]
  vcssim_vcs   = V-2023.12-SP1-1   ← project override of DV VCS version
  vcssim_verdi = V-2023.12-SP1-1   ← project override of DV Verdi version

[ENVS]
  SAOLA_HOME      = ${WORKAREA}/subip/vip/saola       ← local workspace path
  UVM_HOME        = ${WORKAREA}/subip/vip/uvm         ← local workspace path
  DESIGNWARE_HOME = ${WORKAREA}/subip/vip/designware  ← local workspace path
```

The first block is a version override (belongs in tool config).
The second block is workspace-local VIP paths (belongs in project config,
not tool config). In ACE these would be split: version overrides go in
the tool cfg `[params]`, and workspace paths go in `global_project.cfg`.

---

## What this means for ACE conversion

### The 4-layer chain collapses to 1 file

Every `<tool>_tool.cfg` in ACE is self-contained:

```ini
[arc]              ← replaces [License] feature = ... mode = append
synopsys/vc_static

[params]           ← replaces [toolversion] from all layers combined
VCCDC_VERSION = V-2023.12-SP2-10   ← ioss3 final value, no chaining needed

[envs]             ← replaces path composition from pesg_fe.baseline_tools
VCCDC_HOME_PATH = /p/psg/eda/synopsys/vc_static   ← ioss3 PSG mirror
VC_STATIC_HOME  = envs(VCCDC_HOME_PATH)/params(VCCDC_VERSION)
```

No includes. No version cascades. The final resolved value is written
directly. To understand what version a tool is running, you read one file.

### DV tools in ACE

The DV/RTL split is preserved: DV tool cfgs carry the DV-registry version
and the DV install path. An `xceliumsim_tool.cfg` will have a different
`XCM_VERSION` than the `xcelium_tool.cfg` used by the RTL compile flow,
because those are different qualified baselines from different teams.

### The one file that is NOT a tool.cfg

`dv_tools.cth` also sets `SAOLA_HOME`, `UVM_HOME`, `DESIGNWARE_HOME` —
workspace-local VIP paths. These do not belong in any tool cfg; they
belong in `baseline_tools/global_config/global_project.cfg` alongside
`DW_SIM` and the other project-wide paths that are already there.

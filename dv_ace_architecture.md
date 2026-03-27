# DV Tool Configuration Architecture for ACE

This document answers three tightly coupled questions:
1. Is the Cheetah include chain understanding correct?
2. What is tool-specific vs flow-specific in DV configs?
3. Should there be a centralized version file, and should DV variants live in the same tool directory?

---

## 1. Correcting the include chain understanding

Your understanding is **mostly correct, with one important nuance.**

Every ioss3 DV tool's `tool.cth` follows this pattern (using `vcssim` as the example):

```
ioss3/vcssim/tool.cth
  INCLUDE 1 → pesg_fe.baseline_tools/vcssim/tool.cth
                 INCLUDE → pesg_fe.baseline_tools/dv_tools.cth (snapshot of 2024.09 release)
                              sets vcssim_vcs = V-2023.12-SP2-3, etc.
                 [LICENSE] synopsys/vcsmx
                 [ENVS] VCS_HOME, VERDI_HOME, PATH, etc.
  INCLUDE 2 → ioss3/dv_tools.cth
                 INCLUDE → pesg_fe.baseline_tools/dv_tools.cth  ← PARSED AGAIN (redundant)
                 INCLUDE → /p/hdk/.../2024.09.eng.fe.240913/dv_tools.cth  ← live release copy (also sets SP2-3)
                 [ToolVersion] vcssim_vcs = V-2023.12-SP1-1  ← project override (wins)
                 [ENVS] SAOLA_HOME, UVM_HOME, DESIGNWARE_HOME  ← workspace paths (wrong place)
```

**What this means:**
- `dv_tools.cth` IS parsed 3 times per DV tool invocation (snapshot via pesg_fe tool, snapshot via ioss3 override, live release copy).
- YES — every DV tool ends up with all 40 DV version strings and all 40 install paths from `dv_tools.cth`, whether it uses them or not. `vcssim` silently knows the FPGA Vivado path and the Palladium Veloce path.
- The most authoritative source for version defaults is the PSG FE release `dv_tools.cth`, but the final word belongs to the ioss3 `[ToolVersion]` override block.
- The `SAOLA_HOME`/`UVM_HOME`/`DESIGNWARE_HOME` in `ioss3/dv_tools.cth` are workspace-relative VIP paths. They are **not DV tool settings** — they ended up here for convenience but the comment in the file itself says "ToDo: develop methodology to control these at a proj level."

---

## 2. Tool-specific vs flow-specific in DV configs

From reading all the `pesg_fe.baseline_tools/<tool>/tool.cth` files:

### Tool-specific (belongs in `tool.cfg`)

| What | Example | Why it's tool-specific |
|------|---------|----------------------|
| License feature | `synopsys/vcsmx`, `cadence/jasper`, `mentor/questasim` | Identifies the binary you need licensed |
| Tool install path | `VCS_HOME = params(vcssim_vcs_path)` | Where the binary lives |
| Binary PATH addition | `params(vcssim_vcs_path)/bin:params(gcc_path)/bin` | How the shell finds the executable |
| Architecture flags | `VCS_TARGET_ARCH = suse64`, `VCS_LIC_EXPIRE_WARNING = 0` | Static invocation settings for this tool |
| Tool version string | `vcssim_vcs = V-2023.12-SP1-1` | Which binary to load |
| Tool-linked library | `VCS_LIB`, `CER_VCS_PLI = .../libcertess_pli_vcs.so` | PLI/VPI shims that are version-matched to the binary |
| Companion tool paths | `VERDI_HOME`, `RUNTOOLS_PATH` (for certitude), `SPECMAN_PATH` | Tools that are always co-invoked |

### Flow-specific (belongs in `flow.cfg`)

| What | Example | Why it's flow-specific |
|------|---------|----------------------|
| Compile/sim flags | `VERILOG_ANALYZE_OPTS`, `SIM_OPTS`, `ELAB_OPTS` | Change per milestone/IP type |
| Enabled sub-flows | `USER_FLOWS = vcssimemu vcssimfpga` | Which variants to run |
| Pass criteria | `PASS = gk` | Depends on milestone |
| DVB flow pointer | `DVB_ROOT` (resolved at runtime) | The DV flow framework install |
| Post-processing | report filters, waivers | Flow-level decisions |

### Project/workspace config (belongs in `project_config/workspace.cfg`)

| What | Example | Why it's project-specific |
|------|---------|--------------------------|
| VIP checkout paths | `SAOLA_HOME = ${WORKAREA}/subip/vip/saola` | Workspace directory layout, not a tool install |
| UVM root | `UVM_HOME = ${WORKAREA}/subip/vip/uvm` | Same — this is a repo checkout, not an EDA install |
| DesignWare | `DESIGNWARE_HOME = ${WORKAREA}/subip/vip/designware` | Same |

These three are currently misplaced in `dv_tools.cth`. In ACE, they belong in a project-level global config that the workspace `tool.cfg` includes, not in any tool's cfg.

---

## 3. Architecture analysis: centralized version file + DV variants

### Your proposed architecture

```
global_config/
  dv_tool_versions.cfg       ← all DV version params
  rtl_tool_versions.cfg      ← all RTL version params

tools/vcs/
  vcs_tool.cfg               ← RTL VCS: [includes] rtl_tool_versions.cfg
  vcs_dv_tool.cfg            ← DV VCS: [includes] dv_tool_versions.cfg

project_config/
  workspace.cfg              ← SAOLA_HOME, UVM_HOME, DESIGNWARE_HOME
```

### Critical problem: `VCS_HOME` collision

Both `vcs_tool.cfg` and `vcs_dv_tool.cfg` would need to export `VCS_HOME`.
A flow wrapper that loads both in one session (which is common for mixed RTL+DV flows)
would have one overwrite the other. There is no namespace isolation.

This is exactly why Cheetah already separates `vcs` and `vcssim` into
**completely distinct tool namespaces with distinct env variable sets**:

| Setting | `vcs` (RTL) | `vcssim` (DV sim) |
|---------|------------|-------------------|
| License | `synopsys/vcs` | `synopsys/vcsmx` |
| `VCS_HOME` | RTL install path (W-2024.09-SP2-4) | DV install path (V-2023.12-SP1-1) |
| `VERDI_HOME` | RTL Verdi | DV Verdi (different version) |
| `VCS_LIB` | — | set (DV PLI library) |
| `VCS_TARGET_ARCH` | — | `suse64` |
| `SPECMAN` | — | set (DV-only) |

These are not "the same tool at a different version" — they have different licenses,
different env var sets, and are used by mutually exclusive flow types.

**Conclusion: keep `tools/vcs/` and `tools/vcssim/` as separate directories.**
The DV variant concept (`vcs_dv_tool.cfg` in `tools/vcs/`) creates an env collision
problem without providing any benefit over a separate directory.

---

## 4. Centralized version file: yes, but how?

### The PSG FE 2025.03 signal

The latest PSG FE release (`2025.03.eng.fe.250319`) introduced `toolversions.cth` —
a **single file containing all version strings** for both DV and RTL tools, with no
DV/RTL split. The file lists them in alphabetical order with no section headers.
This validates the centralized version table approach.

Note: it does NOT contain `[PARAMS]` (no path composition). Just version strings.
Paths are still composed in individual tool configs from those version params.

### Recommended ACE approach

```
baseline_tools/
  global_config/
    tool_versions.cfg         ← ONE file, ALL version strings (no DV/RTL split)
                                 mirrors PSG FE toolversions.cth structure
    workspace.cfg             ← SAOLA_HOME, UVM_HOME, DESIGNWARE_HOME

  tools/
    vcs/
      vcs_tool.cfg            ← [includes] ../../global_config/tool_versions.cfg
                                 [arc] synopsys/vcs
                                 [envs] VCS_HOME = .../params(VCS_RTL_VERSION)

    vcssim/
      vcssim_tool.cfg         ← [includes] ../../global_config/tool_versions.cfg
                                 [arc] synopsys/vcsmx
                                 [envs] VCS_HOME = .../params(VCSSIM_VCS_VERSION)
                                         VERDI_HOME = .../params(VCSSIM_VERDI_VERSION)
```

The `tool_versions.cfg` uses different key names for tools that exist at two versions:

```ini
# tools/global_config/tool_versions.cfg

# RTL tool versions
VCS_RTL_VERSION       = W-2024.09-SP2-4
VERDI_RTL_VERSION     = W-2024.09-SP2-4
VCCDC_VERSION         = W-2024.09-SP2-4

# DV sim tool versions (separate qualified versions)
VCSSIM_VCS_VERSION    = V-2023.12-SP1-1
VCSSIM_VERDI_VERSION  = V-2023.12-SP1-1
QUESTASIM_VERSION     = w240726
XCELIUM_DV_VERSION    = 24.09.071

# Tools with no RTL/DV split
JASPER_VERSION        = 2024.03
CERTITUDE_VERSION     = V-2023.12-SP2-2
```

### Pros and cons

| | Centralized `tool_versions.cfg` | Per-tool self-contained |
|---|---|---|
| Version snapshot visibility | Single file — instant project-wide audit | Must grep across all tool cfgs |
| Version bump PR size | One file, one PR | One file per tool affected |
| Blast radius of a bad version bump | All tools in one PR review; easy to revert | Isolated to one tool |
| Tool cfg portability | Needs `[includes]` to version file to be useful | Fully self-contained |
| Aligns with PSG FE direction | YES — mirrors `toolversions.cth` pattern | No |
| Risk of key name collision | Low if naming is disciplined | None |

**The centralized approach wins on visibility and aligns with where PSG FE is going.
The include of `tool_versions.cfg` at the top of each `tool.cfg` keeps each tool cfg
independently correct without relying on external load order.**

### What NOT to do: split into `dv_tool_versions.cfg` + `rtl_tool_versions.cfg`

If each tool.cfg only includes its "own" version file, you still need to know
which one to include. This re-introduces a DV/RTL routing problem.
One unified `tool_versions.cfg` with distinct key names is simpler and has
no downside. Any given tool only reads the keys it uses.

---

## 5. Final recommended directory layout

```
baseline_tools/
  global_config/
    tool_versions.cfg         ← all version strings: RTL + DV, indexed by unique key names
    workspace.cfg             ← SAOLA_HOME, UVM_HOME, DESIGNWARE_HOME (project layout only)

  tools/
    # RTL tools
    vcs/vcs_tool.cfg
    verdi/verdi_tool.cfg
    vc_cdc/vc_cdc_tool.cfg
    vc_lint/vc_lint_tool.cfg
    jasper/jasper_tool.cfg       ← RTL formal (jasperfe in Cheetah)
    ...

    # DV tools — separate directories, NOT variants inside RTL tool dirs
    vcssim/vcssim_tool.cfg       ← DV VCS sim (different version + license than vcs/)
    questasim/questasim_tool.cfg
    xceliumsim/xceliumsim_tool.cfg
    certitude/certitude_tool.cfg
    jasperdv/jasperdv_tool.cfg   ← DV formal (different from jasper/)
    emu/emu_tool.cfg
    ...

  flows/
    vcssim/vcssim_flow.cfg       ← DVB_ROOT, USER_FLOWS, sim opts
    vc_cdc/vc_cdc_flow.cfg
    ...
```

Key rules:
1. Every `tool.cfg` starts with `[includes] ../../global_config/tool_versions.cfg`
2. No tool.cfg sets `SAOLA_HOME`, `UVM_HOME`, or `DESIGNWARE_HOME`
3. No `dv_vcs_tool.cfg` inside `tools/vcs/` — DV VCS lives in `tools/vcssim/`
4. `global_config/workspace.cfg` is project-specific; it is NOT included in tool.cfg
   files (only in flow wrappers or project-level includes)

# ACE Demo — for Engineers Familiar with Cheetah-RTL

**Audience**: Engineers who have used Cheetah-RTL (CTH) and want to understand how ACE
differs and why.

**Time**: ~20–30 minutes.

**Format**: Walk through this script live in a terminal. The audience watches and asks questions
at each section break.

---

## Part 1 — The Problem ACE Solves (3 min)

*Talk track (no commands yet):*

> In Cheetah, to run VCS compile you source `cth_sim`, set `DUT=`, set `ACTIVITY=`, and then
> call `make vcs_compile`. The tool path, license, and flow flags are spread across
> `flow.cfg`, `tool.cth`, and a dozen shell variables. If VCS upgrades, you grep for the
> version string in multiple places.
>
> ACE separates these into four distinct layers — tool installation, project versions, flow
> parameters, and DUT identity — and has a config parser that resolves references across them
> automatically. You change the version in one file, and every path that depends on it updates.
>
> Let me show you what that looks like.

---

## Part 2 — Workspace Bootstrap (3 min)

```bash
# Enter the mock workspace (mirrors a real ACE project area)
cd ace_mock_workspace

# This is equivalent to "source cth_setup" in Cheetah
source ace_setup
```

> `ace_setup` does what CTH's `cth_setup` does — sets `PATH`, `WORKAREA`, and other env vars —
> but it reads from structured `.ace` config files instead of a bash script.

```bash
# Verify the environment is active
echo $WORKAREA
echo $PATH | tr ':' '\n' | grep synopsys   # VCS_HOME/bin should be in PATH
```

---

## Part 3 — Four Config Layers (5 min)

> ACE has four types of config file. This is the most important concept to absorb.
> Each type is **strictly independent** — they never include each other.

```
┌──────────────────────────────────────────────────────────────────┐
│  Layer          File                          What it controls    │
├──────────────────────────────────────────────────────────────────┤
│  tool install   tools_demo/tool-vcs/          Paths, licenses,   │
│                   0.1.0/tool.ace              tool version refs   │
│                                                                    │
│  project        projbase/base_tool_bundle.ace VCS_VERSION,        │
│                                               install path bases  │
│                                                                    │
│  flow           tools_demo/tool-vcs/          Compile flags,      │
│                   0.1.0/flow.ace              switches, patterns  │
│                 static/vcs/flow.ace           Workspace overrides │
│                                                                    │
│  DUT            cfg/<dut>.design.ace          Top module, IP type │
└──────────────────────────────────────────────────────────────────┘
```

**Show the tool config — notice NO hardcoded version:**

```bash
cat ../tools_demo/tool-vcs/0.1.0/tool.ace
```

> The paths say `Params(VCS_HOME_PATH)/Toolversion(VCS_VERSION)` — they reference the project
> layer at resolve time. In CTH, the tool path was hardcoded in `tool.cth`.

**Show where the version lives:**

```bash
cat projbase/tool_bundle.ace
cat projbase/base_tool_bundle.ace | grep -A5 "VCS_VERSION\|VCS_HOME_PATH"
```

> Change `VCS_VERSION` here, and all tool paths update automatically.
> ACE resolves these references in multiple passes — `tool.ace` is parsed before
> `tool_bundle.ace` in the include order, but resolution happens after all files are loaded,
> so the reference always finds its value.

**Show the flow config — this is the CTH `flow.cfg` equivalent:**

```bash
cat ../tools_demo/tool-vcs/0.1.0/flow.ace
```

> Notice `VERILOG_ANALYZE_OPTS` is composed from smaller named pieces:
> `params(ALTR_VCS_ANALYZE_SETTINGS)`, `vcs(DEBUG_SWITCH)`, etc.
> In CTH these were bash variables concatenated in a Makefile.
> Here the config parser assembles the final string — the Python script just reads the
> resolved value.

---

## Part 4 — DUT Identity (2 min)

```bash
# Show a DUT config — this is the CTH "design" context
cat cfg/bypass_pnr_reg_fp.design.ace
```

> `TOP_MODULE_NAME` and `IP_TYPE` here are what you'd set as shell variables or in a
> CTH project.cfg. In ACE they're in a dedicated file per DUT, so you can `diff` them,
> version-control them cleanly, and add a new DUT without touching Python.

---

## Part 5 — Running the Flow (7 min)

> This is the moment everything comes together.

**Step 1 — Compile (vlogan)**

```bash
make bypass_pnr_reg_fp__vcs_compile
```

> Watch the output. You'll see ACE set up the environment, then call:
>   `ace_shell --tool vcs -c "python3 vcs_flow.py --stage compile ..."`
>
> That single `ace_shell` invocation reads `tool.ace`, sets `VCS_HOME`, sets `PATH`, acquires
> ARC licenses — then hands off to the Python wrapper.

```bash
# Show what was produced
ls output/bypass_pnr_reg_fp/vcs_compile/
cat output/bypass_pnr_reg_fp/vcs_compile/synopsys_sim.setup
```

> `synopsys_sim.setup` is the library map file — equivalent to what CTH's `genCompileFilesAndMapFiles()`
> wrote. ACE's `CompileStage.execute()` does the same thing: one `vlogan -work <lib>` call per
> IP, with `SYNOPSYS_SIM_SETUP` pointing at this file.

**Step 2 — Elaborate (vcs)**

```bash
make bypass_pnr_reg_fp__vcs_elab
```

```bash
# Show the elab log
cat output/bypass_pnr_reg_fp/vcs_elab/bypass_pnr_reg_fp_vcs_elab.log | tail -20
```

> Elab reads `SYNOPSYS_SIM_SETUP` from `vcs_compile/` automatically — no manual path
> wiring needed. This mirrors exactly what CTH's `genElabFiles()` did with
> `setenv SYNOPSYS_SIM_SETUP <compileDir>/map_files/synopsys_sim.setup`.

**Step 3 — Both in one shot**

```bash
make bypass_pnr_reg_fp__vcs_all
```

**Step 4 — Single stage re-run (elab only)**

```bash
# In CTH you'd re-run just vcs_elab. In ACE:
make bypass_pnr_reg_fp__vcs_elab
```

> Because compile artifacts are in their own stable directory (`vcs_compile/`), elab can
> always be re-run independently without re-compiling.

---

## Part 6 — Config Resolution Live (3 min)

> ACE ships a query tool — `ace_query`. This is something CTH never had.

```bash
# What does VCS_HOME actually resolve to?
ace_query --tool vcs ENVS VCS_HOME --resolve

# Where did that value come from?
ace_query --tool vcs ENVS VCS_HOME --trace

# What are all the flags that will be passed to vlogan?
ace_query --tool vcs VCS VERILOG_ANALYZE_OPTS --resolve
```

> `--resolve` gives you the final value. `--trace` tells you which file and line number
> defined it. In CTH, if a flag was wrong you'd add `echo` statements to Makefiles.
> Here you just run `ace_query --trace`.

---

## Part 7 — Adding a New DUT (2 min)

> In CTH, adding a new DUT meant editing project.cfg, maybe a Makefile, and hoping you
> didn't miss a variable. In ACE:

```bash
# 1. Drop a new design config
cat > cfg/my_new_block.design.ace << 'EOF'
[global_config]
TOP_IP_NAME     = my_new_block
TOP_MODULE_NAME = my_new_block
IP_TYPE         = asic
EOF

# 2. Drop a filelist
# cp input_filelist/bypass_pnr_reg_fp_sim_filelist.json \
#    input_filelist/my_new_block_sim_filelist.json
# (edit to point at your RTL)

# 3. Run — zero Python changes, zero Makefile changes
# make my_new_block__vcs_all
```

> The Python wrapper reads `DUT` from the environment and `TOP_MODULE_NAME` from the design
> config. Nothing else needs to change.

---

## Part 8 — CTH → ACE Concept Map (reference)

| CTH concept | ACE equivalent |
|---|---|
| `tool.cth` — tool install paths | `tools_demo/<tool>/tool.ace` `[envs]` |
| `flow.cfg` — compile/elab flags | `tools_demo/<tool>/flow.ace` `[<tool>]` |
| `project.cfg` — IP lib paths | `projbase/project.ace` `[envs]` |
| `base_tool_bundle.cth` — versions | `projbase/base_tool_bundle.ace` `[ToolVersion]` |
| `cth_setup` | `ace_setup` |
| `cth_sim --tool vcs` | `ace_shell --tool vcs` |
| `make vcs_compile` | `make <dut>__vcs_compile` |
| `Simulation.genCompileFilesAndMapFiles()` | `CompileStage.execute()` in `compile_stage.py` |
| `Simulation.genElabFiles()` | `ElabStage.execute()` in `elab_stage.py` |
| `Vcs.getElabCmd()` | `ElabStage.execute()` — `-liblist_work [lib.]top` |
| Hardcoded version in `tool.cth` | `Toolversion(VCS_VERSION)` in `tool.ace` |
| Per-IP run_csh / compile CSH scripts | Direct subprocess in `run_cmd()` — no intermediate scripts |

---

## Questions to Expect

**"Why not just keep Cheetah?"**
> ACE is config-driven and Python-native. CTH runs through a chain of CSH scripts generated
> at runtime — debugging means reading generated `.csh` files. In ACE, the flow is a Python
> class you can read, step through with a debugger, and unit-test.

**"What happens when `ace_shell` is not sourced?"**
> The Python wrapper calls bare `vlogan`, which fails with "command not found" since
> `VCS_HOME/bin` is not on PATH. `ace_shell` is the contract — it sets up the tool environment
> before handing off to Python.

**"Can I override a flag without editing the base flow.ace?"**
> Yes. Add the key to `static/vcs/flow.ace` under `[vcs]`. The workspace config layer always
> wins over the base tool config.

**"How do I debug a wrong flag value?"**
> `ace_query --tool vcs VCS VERILOG_ANALYZE_OPTS --trace` — it prints the resolved value and
> the exact file:line where it was defined or last overridden.

# ACE Flow Resolution — Three Trees

A flow works because three independent chains come together at runtime.

---

## Tree 1 — Tool Config Resolution
> **Entry**: `ace_shell --tool vcs`
> **Output**: shell environment — `VCS_HOME`, `PATH`, ARC licenses

```
ace_shell --tool vcs
│
│  reads ACE_TOOL_ORDER → toolbase/ace_fe_tool_order.ace  (multi-pass)
│
├── toolbase/<tool>/tool.ace                    [thin redirector]
│   ├── [params] ACE_TOOL_VCS_HOME = /path/to/tool-vcs/0.1.0
│   └── @include <ACE_TOOL_VCS_HOME>/tool.ace
│         └── tools_demo/tool-vcs/0.1.0/tool.ace  [versioned tool config]
│               ├── [arc]  vcs-vcsmx-lic
│               └── [envs] VCS_HOME = Params(VCS_HOME_PATH)/Toolversion(VCS_VERSION)
│                          PATH    |= Envs(VCS_HOME)/bin:
│
└── project.ace → projbase/project.ace → tool_bundle.ace → base_tool_bundle.ace
      ├── [ToolVersion] VCS_VERSION    = W-2024.09-SP2-4
      └── [Params]      VCS_HOME_PATH  = /p/psg/eda/synopsys/vcsmx

      (ACE re-parses until all cross-references resolve — no explicit @include needed
       between tool.ace and tool_bundle.ace; multi-pass handles it)

RESULT → VCS_HOME=/p/psg/eda/synopsys/vcsmx/W-2024.09-SP2-4  in shell env
         'vlogan', 'vcs' callable by name via PATH
```

---

## Tree 2 — Flow Config Resolution
> **Entry**: `vcs_flow.py --flow-cfg static/vcs/flow.ace`
> **Output**: `flow_cfg_data` dict — all keys resolved, ready for the Python wrapper

```
static/vcs/flow.ace                              [workspace override layer]
│   @include $ACE_TOOL_VCS_HOME/flow.ace
│
└── tools_demo/tool-vcs/0.1.0/flow.ace           [base flow config]
    ├── @include $WORKAREA/projbase/static/vcs/vcswarn2err.ace
    │         └── projbase/static/vcs/vcswarn2err.ace
    │               ├── [vcs] W2E_ANALYZE = -f $WORKAREA/projbase/static/vcs/w2e_configs/w2e_vlog_ip-soc_l5.f
    │               └── [vcs] W2E_ELAB    = -file $WORKAREA/projbase/static/vcs/w2e_configs/w2e_elab_ip-soc_l5.f
    ├── @include $WORKAREA/cfg/$DUT.design.ace    → [global_config] TOP_MODULE_NAME, IP_TYPE
    ├── @include $WORKAREA/projbase/ip_type_params/ip_type.global_config(IP_TYPE).ace
    │                                             → [params] ALTR_MACROS_SIMPWR_RTL = +define+...
    │
    ├── [params] ALTR_VCS_ANALYZE_SETTINGS = -sverilog -timescale=1ns/1ps ...
    │
    └── [vcs]  VERILOG_ANALYZE_OPTS = params(ALTR_VCS_ANALYZE_SETTINGS)
                                      params(ALTR_MACROS_SIMPWR_RTL)
                                      vcs(W2E_ANALYZE) ...
               ENABLE_MAP_FILE      = true
               ...

    [vcs] workspace overrides in static/vcs/flow.ace win over base:
               TOP_COMPILE_LIB = 
               ERROR_EXCLUDE   = [abc, def]

RESULT → flow_cfg_data['vcs']['VERILOG_ANALYZE_OPTS'] = "-sverilog ... +define+... -error=..."
         Python wrapper reads these directly — no shell variables involved
```

### Tree 2b — UDM Flow Config Resolution
> **Entry**: `udm_flow.py --flow-cfg static/udm/flow.ace` (under `ace_shell --tool udm_rtl_reader`)
> **Output**: `flow_cfg_data['udm_rtl_reader']['SOFTWARE_DEFINES']` — path to `software_defines.sv`

```
static/udm/flow.ace                                        [workspace override layer]
│
├── @include $ACE_TOOL_VCS_HOME/flow.ace                   ← $ACE_TOOL_VCS_HOME not set in udm shell
│         (silently skipped — VCS keys not needed here)
│
└── @include -$ACE_TOOL_UDM_RTL_READER_HOME/flow.ace       ← set by ace_shell --tool udm_rtl_reader
          └── tools_demo/tool-udm_rtl_reader/0.1.0/flow.ace
                └── [udm_rtl_reader]
                      SOFTWARE_DEFINES = $WORKAREA/projbase/static/udm_rtl_reader/software_defines.sv

RESULT → flow_cfg_data['udm_rtl_reader']['SOFTWARE_DEFINES']
                        = "$WORKAREA/projbase/static/udm_rtl_reader/software_defines.sv"
         udm_compile_stage.py copies this file into the stage output dir
```

> **Same `static/udm/flow.ace` serves two shells:**
> - Under `ace_shell --tool vcs` (udm_vcs_compile / elab): VCS include resolves, UDM include skips → `[vcs]` keys used
> - Under `ace_shell --tool udm_rtl_reader` (udm_udm_compile): VCS include skips, UDM include resolves → `[udm_rtl_reader]` keys used

---

## Tree 3 — Makefile Chain
> **Entry**: `make <dut>__vcs_compile`
> **Output**: subprocess call to `vlogan`

```
make bypass_pnr_reg_fp__vcs_compile
│
└── Makefile → demo_tasks.mk
      └── %__vcs_compile:
            $(MAKE) -C static/vcs compile DUT=$* FILELIST=input_filelist/$*_sim_filelist.json
            │
            └── static/vcs/Makefile
                  └── include toolbase/vcs/tool.mk          [thin Makefile redirector]
                        ACE_TOOL_VCS_HOME = $(ace_query ... ACE_TOOL_VCS_HOME --resolve)
                        include $(ACE_TOOL_VCS_HOME)/tool.mk
                        │
                        └── tools_demo/tool-vcs/0.1.0/tool.mk  [versioned targets]
                              compile:
                                ace_shell --tool vcs -c '
                                  python3 vcs_flow.py
                                    --filelist  <filelist>
                                    --flow-cfg  static/vcs/flow.ace
                                    --stage     compile
                                '

RESULT → vlogan called with resolved flags inside ace_shell subprocess
         output/<dut>/vcs_compile/  created
```

---

## How the Three Trees Connect

```
make <dut>__<flow>_<step>
        │
        │  Tree 3 — Makefile
        │  workspace → static → toolbase → versioned tool.mk
        │
        ▼
ace_shell --tool <tool> -c 'python3 <tool>_flow.py --flow-cfg ...'
        │                           │
        │ Tree 1                    │ Tree 2
        │ tool.ace resolution       │ flow.ace resolution
        │ → PATH, VCS_HOME,         │ → VERILOG_ANALYZE_OPTS,
        │   licenses in env         │   ENABLE_* switches,
        │                           │   TOP_MODULE_NAME
        └───────────┬───────────────┘
                    │
             <tool>_flow.py
             BaseFlow.run()
               ├── CompileStage  →  vlogan  (found via Tree 1 PATH)
               │                    flags   (from Tree 2 flow_cfg_data)
               └── ElabStage     →  vcs     (found via Tree 1 PATH)
                                    flags   (from Tree 2 flow_cfg_data)
```

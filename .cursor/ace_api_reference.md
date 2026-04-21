# ACE Python API Reference

This document covers the Python API for programmatic access to ACE configuration data.

---

## ace_query API

The `ace_query` function in `src/api.py` provides a programmatic interface to the same configuration data that the `ace_query` command-line tool prints. Import it once and call it with keyword arguments — no subprocess, no temporary files.

### Import

```python
from src.api import ace_query, ConfigValue
```

---

## Function Signature

```python
def ace_query(
    file: str | None = None,
    tool: str | None = None,
    section: str | None = None,
    key: str | None = None,
    key_filter: str | None = None,
    resolve: bool = False,
    params: dict | None = None,
    env: dict | None = None,
    cth: bool = False,
) -> ConfigParser | dict[str, ConfigValue] | list[dict[str, ConfigValue]] | str
```

---

## Parameters

### file

**Type**: `str | None`  
**Default**: `None`

Path to the config file to parse. When given the file is parsed directly — bootstrap and `ACE_TOOL_ORDER` are bypassed entirely.

When omitted the standard bootstrap is used:

1. Built-in `[Params] ACE_TOOL_ORDER` is set to the repo's `config.ace`.
2. `config.ace` optionally includes `$WORKAREA/design.ace` (or `$WARD/design.ace`).
3. If `design.ace` overrides `ACE_TOOL_ORDER`, multi-pass lazy evaluation re-bootstraps from the new path.

To engage CTH mode instead, set `cth=True` (see below).

### tool

**Type**: `str | None`  
**Default**: `None`

Tool name for `<TOOLNAME>` expansion inside `@include` paths. Setting this automatically sets `TOOLNAME=<tool>` in the parser's param table. The matching `ACTIVITY` is also resolved from `$WORKAREA/baseline_tools/activity_dir.map` and set as `ACTIVITY=<value>` if found.

### section

**Type**: `str | None`  
**Default**: `None`

Name of the section to return (case-insensitive). When omitted the full `ConfigParser` object is returned instead.

### key

**Type**: `str | None`  
**Default**: `None`

Name of a specific key inside `section` to return (case-insensitive). Requires `section`. Returns a plain `str`.

### key_filter

**Type**: `str | None`  
**Default**: `None`

"key:value" filter string for list sections (`[[section]]`). Only instances where `key` equals `value` are included in the returned list. Requires `section`; ignored for normal sections.

### resolve

**Type**: `bool`  
**Default**: `False`

When `True`, environment variables and `section(key)` cross-references in the returned value are expanded before the string is returned. Only meaningful when `key` is specified.

### params

**Type**: `dict | None`  
**Default**: `None`

Additional `{PARAM: value}` substitutions for `<PARAM>` token expansion in `@include` paths. `TOOLNAME` and `ACTIVITY` (derived from `tool`) are already set automatically; entries supplied here take precedence over those automatic values.

### env

**Type**: `dict | None`  
**Default**: `None`

Extra environment variables applied as a temporary overlay on `os.environ` for the duration of the call. The caller's environment is left unchanged after the call — pre-existing keys are restored, newly-added keys are removed. Use this to supply `WORKAREA`, `WARD`, `CENTRAL_TOOL_ORDER`, or any `$VAR` referenced inside config values or include paths without side-effects.

### cth

**Type**: `bool`  
**Default**: `False`

When `True`, engage CTH (Central Tool Hub) mode: `$CENTRAL_TOOL_ORDER` is read from the environment and used as the `ACE_TOOL_ORDER` bootstrap path instead of the built-in default. Raises `ValueError` if `$CENTRAL_TOOL_ORDER` is not set. Ignored when `file` is given (explicit file always bypasses the bootstrap).

```python
# Parse via $CENTRAL_TOOL_ORDER (must be set in env)
parser = ace_query(cth=True, tool="vcs")

# Or supply it explicitly without mutating os.environ
parser = ace_query(
    cth=True,
    env={"CENTRAL_TOOL_ORDER": "/central/tools/order.ace"},
    tool="vcs",
)
```

---

## Return Values

The return type depends on which parameters are supplied:

| section | key | Returns |
|---------|-----|---------|
| not given | — | `ConfigParser` — fully loaded parser |
| given (normal section) | not given | `dict[str, ConfigValue]` |
| given (list section) | not given | `list[dict[str, ConfigValue]]` |
| given | given | `str` — the value (optionally resolved) |

---

## ConfigValue

Each value in the returned dicts is a `ConfigValue` object (re-exported from `src.api`):

```python
from src.api import ConfigValue

cv: ConfigValue = section_dict["MY_KEY"]
cv.value        # the current value (str, int, float, …)
cv.file_path    # file where the value was last assigned
cv.line_number  # line number of that assignment
cv.history      # list of (old_value, file, line) prior assignments
cv.deduplicated_history()  # history with consecutive duplicates removed
```

---

## ConfigParser

When no `section` is given the full parser is returned and all its methods are available:

```python
parser = ace_query(file="design.ace", tool="vcs")

parser.get_all_sections()            # list of section names (lowercase)
parser.get_section("envs")           # dict[str, ConfigValue]
parser.get_sections("tools")         # generator of list-section instances
parser.get_sections("tools", filter="Name:my_tool")
parser.get_section_text("envs", trace=True, resolve=True)
parser.resolve_value("$WORKAREA/foo")
```

---

## Exceptions

| Exception | When raised |
|-----------|-------------|
| `FileNotFoundError` | `file=` given but the path does not exist |
| `ValueError` | `cth=True` but `$CENTRAL_TOOL_ORDER` is not set; `key=` given without `section=`; invalid `key_filter` format; `key=` used on a list section |
| `KeyError` | Requested section or key not present in the config |

---

## Examples

### Load the full parser

```python
from src.api import ace_query

parser = ace_query(file="/path/to/design.ace", tool="vcs")
for section in parser.get_all_sections():
    print(section)
```

### Read a single value

```python
version = ace_query(
    file="/path/to/design.ace",
    tool="vcs",
    section="TOOLVERSION",
    key="VCS_VERSION",
)
print(version)   # e.g. "2023.12"
```

### Read a single value with variable resolution

```python
root = ace_query(
    file="/path/to/design.ace",
    section="PARAMS",
    key="design_root",
    resolve=True,
    env={"WORKAREA": "/my/workarea"},
)
print(root)   # $WORKAREA expanded to /my/workarea
```

### Read an entire normal section

```python
envs: dict = ace_query(file="/path/to/design.ace", section="ENVS")
for key, cv in envs.items():
    print(f"{key} = {cv.value}  # {cv.file_path}:{cv.line_number}")
```

### Read a list section

```python
tools: list = ace_query(file="/path/to/design.ace", section="TOOLS")
for inst in tools:
    name = inst.get("Name") or inst.get("name")
    print(name.value if name else "<unnamed>")
```

### Filter a list section

```python
matches = ace_query(
    file="/path/to/design.ace",
    section="TOOLS",
    key_filter="Name:my_tool",
)
# matches is a list with 0 or 1 entries
```

### Supply environment variables cleanly

```python
# WORKAREA is set only for this call; os.environ is unchanged afterwards
value = ace_query(
    env={"WORKAREA": "/project/my_wa", "CENTRAL_TOOL_ORDER": ""},
    tool="rtla",
    section="ENVS",
    key="PATH",
)
```

### Use params= for extra <PARAM> tokens

```python
# Config contains: @include <DESIGNROOT>/tool_overlay.ace
parser = ace_query(
    file="/path/to/design.ace",
    params={"DESIGNROOT": "/proj/my_design"},
)
```

---

## Relationship to the CLI

| CLI invocation | API equivalent |
|----------------|---------------|
| `ace_query -f cfg.ace` | `ace_query(file="cfg.ace")` |
| `ace_query --tool vcs ENVS` | `ace_query(file=…, tool="vcs", section="ENVS")` |
| `ace_query --tool vcs ENVS PATH` | `ace_query(…, tool="vcs", section="ENVS", key="PATH")` |
| `ace_query --resolve ENVS PATH` | `ace_query(…, section="ENVS", key="PATH", resolve=True)` |
| `ace_query TOOLS Name:my_tool` | `ace_query(…, section="TOOLS", key_filter="Name:my_tool")` |
| `DUT=abc ace_query …` | `ace_query(…, env={"DUT": "abc"})` |

---

## Typical Usage Patterns

### In Flow Wrappers

Flow wrappers typically use `ace_query()` to load tool and flow configs:

```python
from src.api import ace_query

class VCSFlow(BaseFlow):
    def flow_preprocess(self):
        # Load tool config
        tc = ace_query(tool="vcs")
        
        # Resolve executable paths
        ev = dict(os.environ)
        self.vlogan_exec = tc.resolve('params', 'vlogan_exec', ev)
        self.vcs_exec = tc.resolve('params', 'vcs_exec', ev)
        
        # Load flow config
        fc = ace_query(file=self.flow_cfg_path)
        
        # Resolve flow parameters
        self.work_lib = fc.get('WORK_LIB', 'work')
        self.analyze_opts = fc.resolve('VERILOG_ANALYZE_OPTS', ev)
```

### In Configuration Tools

Configuration management scripts can use `ace_query()` for validation and comparison:

```python
from src.api import ace_query

def validate_tool_config(tool_name: str):
    """Validate that required tool config keys are present."""
    parser = ace_query(tool=tool_name)
    
    # Check required sections
    required_sections = ['envs', 'params', 'arc']
    for section in required_sections:
        if section not in parser.get_all_sections():
            raise ValueError(f"Missing required section [{section}] in {tool_name} config")
    
    # Check required environment variables
    envs = parser.get_section('envs')
    if f'{tool_name.upper()}_HOME' not in envs:
        raise ValueError(f"Missing {tool_name.upper()}_HOME in [envs]")
```

### In Test Scripts

Test scripts can use `ace_query()` to verify config values:

```python
from src.api import ace_query
import pytest

def test_vcs_version():
    """Verify VCS version is set correctly."""
    version = ace_query(
        tool="vcs",
        section="PARAMS",
        key="VCS_VERSION",
    )
    
    # Check version format (e.g., "X-2025.06-SP2")
    assert version.startswith("X-"), f"Unexpected VCS version format: {version}"
    assert "2025" in version, f"VCS version should be 2025.x: {version}"
```

---

## Related

- `ace_utilities_reference.md` — CLI utility command reference
- `agent.md` — ACE config architecture and bootstrap chain
- `compatibility_analysis.md` — Spec compatibility analysis

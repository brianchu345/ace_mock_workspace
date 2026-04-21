# ACE Utility Commands Reference

This document covers the CLI utilities provided by ACE for configuration management,
environment setup, and shell integration.

---

## ace_query

Print configuration data with optional filtering, tracing, and value resolution.

### Usage

```bash
# Print all sections
ace_query --file config.ace

# Print one section
ace_query --file config.ace SECTION

# Print one key value
ace_query --file config.ace SECTION KEY

# Filter list sections by key:value
ace_query --file config.ace SECTION Name:prod

# Resolve variables and section(key) references
ace_query --file config.ace SECTION KEY --resolve

# Override WORKAREA for this invocation only
ace_query --workarea /path/to/wa PARAMS design

# KEY=VAL positional assignments are supported (gmake-style)
ace_query WORKAREA=/tmp/wa SECTION KEY
```

### Options

| Option | Description |
|--------|-------------|
| `--file`, `-f` | Configuration file to parse. When omitted, the parser bootstraps via `Params(ACE_TOOL_ORDER)` (see Bootstrap Behavior below). |
| `--tool` | Sets TOOLNAME for `<TOOLNAME>` expansion in includes. ACTIVITY is auto-resolved when available. |
| `--trace` | Show value source (file:line) plus override history. |
| `--resolve` | Resolve environment variables and `Section(key)` references in output. |
| `--workarea`, `-w` | Temporarily override `$WORKAREA` for config lookup and include resolution. |
| `--verbose`, `-v` | Enable verbose logging. |

### Bootstrap Behavior

When `--file` is not specified, all tools use the same bootstrap sequence:

1. The parser is seeded with a built-in `[Params] ACE_TOOL_ORDER` pointing at the repo's `config.ace`.
2. `config.ace` includes `$WORKAREA/design.ace` (or `$WARD/design.ace`) as an optional overlay.
3. If `design.ace` overrides `[Params] ACE_TOOL_ORDER`, multi-pass lazy evaluation re-bootstraps from the new path automatically.

**CTH mode**: When `$CENTRAL_TOOL_ORDER` is set in the environment, all tools automatically override `ACE_TOOL_ORDER` to that path before bootstrapping. This is the legacy integration path for Central Tool Hub environments.

When `--file` is given, the file is parsed directly — bootstrap and `ACE_TOOL_ORDER` are bypassed entirely.

---

## ace_cfg

Configuration status and comparison utility.

### Usage

```bash
ace_cfg status [--file FILE]
ace_cfg update
ace_cfg diff [OPTIONS] LEFT RIGHT
```

### Subcommands

#### status

Checks config parsing and prints shell stack state when running inside an `ace_shell` session.

```bash
ace_cfg status
ace_cfg status --file /path/to/design.ace
```

`--file` bypasses bootstrap and parses the given file directly.

#### update

Placeholder command:

```bash
ace_cfg update
```

#### diff

Compares two config sources (file path or directory/workarea), grouped by tool scope.

```bash
ace_cfg diff LEFT RIGHT
ace_cfg diff --tool rtla LEFT RIGHT
ace_cfg diff --sections ENVS --sections PARAMS LEFT RIGHT
ace_cfg diff --trace LEFT RIGHT
ace_cfg diff --resolve LEFT RIGHT
ace_cfg diff --yaml diff.yaml LEFT RIGHT
```

**Diff block semantics**:

- `TOOL=` — Diff appears only in no-tool parse.
- `TOOL=<name>` — Diff appears in exactly one tool.
- `TOOL=*` — Diff shared by two or more tools.

---

## ace_setup

Bootstraps the ACE environment by resolving `ACE_CFG_ROOT` via `parse_default()`, then re-executes from the correct release and hands off to `ace_shell`.

### Usage

```bash
ace_setup [--verbose] [--debug] [-c COMMAND] [--label LABEL]
```

`ace_setup` follows the same bootstrap path as all other tools — no separate `--file` argument is needed or accepted.

Re-execution is suppressed if `ACE_CFG_ROOT` is already set in the environment.

### Options

| Option | Description |
|--------|-------------|
| `--verbose` | Enable verbose logging during bootstrap. |
| `--debug` | Enable debug logging. |
| `-c COMMAND` | Execute command string and exit (forwarded to `ace_shell`). |
| `--label LABEL` | Set session label (shown in `ACE_SHELL_PROMPT`). |

### Bootstrap Chain

```
ace_setup (run by user)
  └─ ConfigParser.parse_default()
       └─ @include Params(ACE_TOOL_ORDER)             ← pass 1: uses default = config.ace
            ├─ config.ace                             ← sets ACE_CFG_ROOT, PATH
            │    └─ @include -<WORKAREA>/design.ace   ← optional workspace overlay
            │         └─ design.ace
            │              ├─ @include toolbase/config_fe.ace   ← OVERRIDES ACE_TOOL_ORDER
            │              └─ @include projbase/project.ace
            └─ [ACE_TOOL_ORDER changed → triggers pass 2]
  └─ ConfigParser.parse_default() [pass 2]
       └─ @include Params(ACE_TOOL_ORDER)             ← now = ace_fe_tool_order.ace
            └─ ace_fe_tool_order.ace
                 ├─ @include <TOOLNAME>/tool.ace      ← skipped if TOOLNAME unset
                 ├─ @include <WORKAREA>/design.ace    ← re-includes workspace overlay
                 └─ @include <WORKAREA>/<ACTIVITY>/<TOOLNAME>/tool.ace
```

### CTH Mode

When `$CENTRAL_TOOL_ORDER` is set in the environment, ACE automatically overrides `ACE_TOOL_ORDER` to that path before bootstrapping.

---

## ace_shell

Launch a shell with config-defined environment, or run a command with that environment.

### Usage

```bash
# Interactive shell
ace_shell [--file FILE] [--tool TOOL] [--shell SHELL]

# Execute command and exit
ace_shell [--file FILE] [--tool TOOL] [--shell SHELL] -c "command"

# Dispatch mode — positional command name looks up <cmd>_exec in [PARAMS]
ace_shell synth [--file FILE]

# Dispatch with extra args forwarded to <cmd>_exec
ace_shell synth --drc --effort high [--file FILE]

# Via plain symlink — looks up mytool_exec in [PARAMS]
mytool [--file FILE] [--shell SHELL]

# Via plain symlink with extra args forwarded to mytool_exec
mytool --opt arg [--file FILE]

# Via ace_shell_<tool> symlink — interactive shell with TOOLNAME=<tool>, no dispatch
ace_shell_vcs [--file FILE]
```

### Symlink Mode

The invocation name determines the mode:

| Invocation | Behaviour |
|------------|-----------|
| `ace_shell_<tool>` (no positional arg) | Interactive shell with `TOOLNAME=<tool>` |
| `<cmd>` plain symlink (no positional arg) | Dispatch: run `<cmd>_exec` from `[PARAMS]` |
| `ace_shell <cmd> [args...]` | Dispatch: run `<cmd>_exec`, forward extra args |
| `<cmd> [args...]` plain symlink | Dispatch: run `<cmd>_exec`, forward extra args |

Extra args — any positional words after the command name are appended to the exec'd command:

```bash
ace_shell synth --effort high    # runs: <synth_exec> --effort high
./abc --drc                      # runs: <abc_exec> --drc
```

**Chained symlinks for tool inference** — an intermediate `ace_shell_<tool>` link infers the tool:

```bash
ln -s ace_shell ace_shell_ab
ln -s ace_shell_ab abc

# Behaves like: ace_shell --tool ab abc
./abc --file design.ace
```

The invoked name (`abc`) maps to `abc_exec`; `--tool ab` is inferred from the chain.

### Options

| Option | Description |
|--------|-------------|
| `--file`, `-f` | Config file to load directly (bypasses bootstrap). When omitted, configuration is loaded via `Params(ACE_TOOL_ORDER)` bootstrap. |
| `--tool` | Sets TOOLNAME for include expansion. ACTIVITY is auto-resolved from tool mapping when available. |
| `--shell` | Shell executable to launch. Default is `$SHELL`, fallback `/bin/tcsh`. |
| `-c` | Execute command string and exit. |
| `--verbose`, `-v` | Enable verbose logging. |

### Shell Prompt — ACE_SHELL_PROMPT

Every `ace_shell` (and `ace_setup`) session sets `ACE_SHELL_PROMPT` in the environment. Its value is built from the last word of each stacked session label, oldest to newest, prefixed with `>`:

| Scenario | ACE_SHELL_PROMPT |
|----------|------------------|
| `ace_setup` | `>ace` |
| + `ace_shell --tool vcs` | `>ace>vcs` |
| + `ace_shell --tool synth` | `>ace>vcs>synth` |

Add the following snippet to your shell rc file to use it:

**tcsh** (`~/.tcshrc`):

```tcsh
if ($?ACE_SHELL_PROMPT) then
    set prompt="[%m %c] ${ACE_SHELL_PROMPT}> "
else
    set prompt="[%n@%m %c]> "
endif
```

**bash** (`~/.bashrc`):

```bash
if [[ -n "$ACE_SHELL_PROMPT" ]]; then
    PS1='[\u@\h \W]'"${ACE_SHELL_PROMPT}"'> '
else
    PS1='[\u@\h \W]> '
fi
```

The `>` characters show nesting depth at a glance; the label words identify which tool environments are active.

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `WORKAREA` | Primary workspace; seeded as `<WORKAREA>` param and `Params(WORKAREA)` in every parse. |
| `WARD` | Fallback workspace when `WORKAREA` is unset; treated identically once resolved. |
| `CENTRAL_TOOL_ORDER` | When set, overrides `ACE_TOOL_ORDER` (CTH mode). |
| `SHELL` | Default shell used by `ace_shell`. |
| `ACE_SHELL_PROMPT` | Shell prompt indicator showing nested ACE shell sessions. |
| `ACE_CFG_ROOT` | Resolved ACE config root directory (set after bootstrap). |

---

## Python Environment

ACE requires Python 3.12.3 from the Intel environment:

```bash
/usr/intel/pkgs/python3/3.12.3/bin/python3
```

Python scripts should import:

```python
import UsrIntel.R1
```

---

## See Also

- `ace_api_reference.md` — Python API for `ace_query()`
- `agent.md` — ACE bootstrap chain and config architecture
- `compatibility_analysis.md` — Spec compatibility analysis

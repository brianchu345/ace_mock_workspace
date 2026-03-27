Hey, a few things I want to align on before we start the ACE conversion:

**1. VCS variants — one dir per tool or group them?**
In Cheetah we have vcs, vcssim, emuvcs as separate dirs. They have different license feature, different binary path and ENV variables. In ACE, do we keep them as separate tool dirs (tools/vcs/, tools/vcssim/, tools/emuvcs/) or group them under one dir with multiple cfgs (tools/vcs/vcs.cfg, tools/vcs/vcssim.cfg)?

**2. Family-wide version files?**
In Cheetah, dv_tools.cth, rtl_tools.cth, and psg_tools.cth cth act as "family-wide" version registries and most tools include either one of them to resolve versions and paths. In ACE do we want the same pattern — a global_projconfig/dv_tool_versions.cfg and global_projconfig/default_tool_versions.cfg that each tool.cfg can include? And do we want an extra layer of tool/dv/ and tool/default_rtl/ tool/internal directories to distinguish them for readability? 

# FunnelAgent

A Claude plugin skeleton for funnel-related skills.

## Installation

```bash
# Add the marketplace
/plugin marketplace add <your-github-username>/FunnelAgent

# Install the plugin
/plugin install FunnelAgent@funnel-agent-marketplace
```

## Structure

```
FunnelAgent/
├── .claude-plugin/
│   ├── plugin.json          # Plugin metadata
│   └── marketplace.json     # Marketplace definition
├── skills/
│   └── funnel-agent/
│       └── SKILL.md         # Skill instructions for Claude
└── README.md
```

## Adding More Skills

Create a new folder under `skills/` with a `SKILL.md` file inside it. Then update `plugin.json` if needed.

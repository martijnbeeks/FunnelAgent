# FunnelAgent

A Claude Code plugin that generates direct-response advertorials from deep market research through a guided multi-step pipeline.

## What It Does

FunnelAgent automates a 4-step copywriting workflow:

1. **Deep Research** — Uses ChatGPT's API with web search to conduct exhaustive market research (Reddit, YouTube, Amazon reviews, forums, competitor ads)
2. **Synthesis Phase 1** — Analyzes research to identify 3-4 avatar/angle combinations with novelty gap scoring
3. **Synthesis Phase 2** — Creates a complete 14-part strategic intelligence brief for all angles
4. **Write Advertorial** — Generates a full advertorial as a ready-to-use HTML page (CONFIG + template)

## Quick Start

### 1. Setup

```bash
# Install Python dependencies
pip install -r scripts/requirements.txt

# Set your OpenAI API key
cp .env.example .env
# Edit .env and add your key
```

### 2. Run the Pipeline

```
/funnel-orchestrator
```

The orchestrator will guide you through:
- Collecting product info (name, market, problem, ingredients)
- Running deep research via ChatGPT API
- Presenting avatar/angle options for your selection
- Generating the full strategic brief
- Writing the advertorial and assembling the HTML

### 3. Output

Open `output/advertorial.html` in a browser to preview your advertorial.

## Skills

| Skill | Command | Purpose |
|-------|---------|---------|
| Orchestrator | `/funnel-orchestrator` | Guides the full pipeline |
| Deep Research | `/deep-research` | Step 1: Market research via ChatGPT API |
| Synthesis P1 | `/synthesis-phase1` | Step 2.1: Avatar/angle identification |
| Synthesis P2 | `/synthesis-phase2` | Step 2.2: Full strategic brief |
| Write Advertorial | `/write-advertorial` | Step 3: Write advertorial CONFIG + HTML |

Each skill can be run independently if you want to re-do a specific step.

## Project Structure

```
FunnelAgent/
├── skills/                     # Skill definitions
│   ├── funnel-orchestrator/    # Main pipeline conductor
│   ├── deep-research/          # ChatGPT API research
│   ├── synthesis-phase1/       # Avatar/angle selection
│   ├── synthesis-phase2/       # Full strategic synthesis
│   └── write-advertorial/      # Advertorial copy + HTML
├── scripts/
│   ├── deep_research.py        # Python script for OpenAI API
│   └── requirements.txt        # Python dependencies
├── skill_content/              # SOP reference documents
├── templates/
│   └── POV.html                # HTML advertorial template
├── output/                     # Generated files (gitignored)
├── .env.example                # API key template
└── .claude-plugin/             # Plugin metadata
```

## Requirements

- Claude Code
- Python 3.8+
- OpenAI API key (for deep research step)

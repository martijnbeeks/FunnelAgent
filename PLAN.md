# FunnelAgent Skills Architecture Plan

## Overview

Build a complete skill-based workflow for generating direct-response advertorials from deep market research. The pipeline has 4 steps, with user interaction points between steps.

---

## Workflow Steps & User Interaction Points

```
[User Input] --> Step 1: Deep Research (ChatGPT API)
                    |
                    v
              [Market Research Doc saved to output/]
                    |
                    v
             Step 2.1: Synthesis Phase 1 (Claude)
                    |
                    v
              [Present 3-4 Avatar/Angle options]
                    |
         >>> USER SELECTS primary avatar/angle <<<
                    |
                    v
             Step 2.2: Synthesis Phase 2 (Claude)
                    |
                    v
              [Full Strategic Brief saved to output/]
                    |
         >>> USER CONFIRMS target language <<<
                    |
                    v
             Step 3.1: Write Advertorial (Claude)
                    |
                    v
              [CONFIG output + POV.html populated]
```

---

## Files to Create

### 1. Infrastructure

| File | Purpose |
|------|---------|
| `.env.example` | Template for API key setup |
| `scripts/deep_research.py` | Python script calling OpenAI API with web search for deep research |
| `scripts/requirements.txt` | Python dependencies (`openai`) |
| `output/.gitkeep` | Output directory for generated docs |

**Update `.gitignore`:** Add `.env`, `output/*.md`, `output/*.json`, `node_modules/`

### 2. Skills (6 files)

| Skill | File | Purpose |
|-------|------|---------|
| Orchestrator | `skills/funnel-orchestrator/SKILL.md` | Main workflow conductor |
| Deep Research | `skills/deep-research/SKILL.md` | Step 1: ChatGPT API deep research |
| Synthesis P1 | `skills/synthesis-phase1/SKILL.md` | Step 2.1: Avatar/angle identification |
| Synthesis P2 | `skills/synthesis-phase2/SKILL.md` | Step 2.2: Full strategic synthesis |
| Write Advertorial | `skills/write-advertorial/SKILL.md` | Step 3.1: Write CONFIG for HTML template |

**Remove:** `skills/funnel-agent/SKILL.md` (skeleton placeholder)

### 3. Relocate Template

Move `skill_content/POV.html` to `templates/POV.html` for cleaner separation (SOP docs stay in `skill_content/` as reference, template goes in `templates/`).

---

## Skill Design Details

### Skill 1: `funnel-orchestrator` (User invokes: `/funnel-orchestrator`)

**Role:** Guides the user through the complete pipeline. Asks for inputs, calls sub-skills in order, handles user decision points.

**Flow:**
1. Ask user for: Product Name, Product Description, Target Market, Problem, Key Ingredients, Optional URLs, Target Language
2. Ask user for their OpenAI API key (or check `.env`)
3. Invoke `/deep-research` with the collected inputs
4. Save research output to `output/01_market_research.md`
5. Invoke `/synthesis-phase1` with research output
6. **Present avatar/angle options to user, ask them to select**
7. Invoke `/synthesis-phase2` with research + Phase 1 output + user selection
8. Save synthesis to `output/02_synthesis_strategy.md`
9. **Confirm target language with user**
10. Invoke `/write-advertorial` with all documents
11. Save CONFIG to `output/03_advertorial_config.js`
12. Copy `templates/POV.html` to `output/advertorial.html` and inject the CONFIG

### Skill 2: `deep-research` (Sub-skill, called by orchestrator)

**Role:** Execute deep market research via OpenAI API.

**Implementation:**
- The SKILL.md instructs Claude to:
  1. Read the SOP from `skill_content/PROMPT 1_ ChatGPT Market Research.pdf`
  2. Construct the full research prompt by injecting user's product info into the SOP template
  3. Run `scripts/deep_research.py` which:
     - Accepts the prompt via stdin or temp file
     - Calls OpenAI API (model: `o3` with `web_search_preview` tool, or `gpt-4o` with web search)
     - Streams/saves the response
  4. Save output to `output/01_market_research.md`

**The Python script (`scripts/deep_research.py`):**
- Reads `OPENAI_API_KEY` from env
- Takes prompt from `--prompt-file` argument
- Calls OpenAI Responses API with web_search tool enabled
- Writes output to specified file
- Handles errors gracefully

### Skill 3: `synthesis-phase1`

**Role:** Analyze research output and present avatar/angle options.

**Implementation:**
- SKILL.md contains the full Phase 1 prompt template from PROMPT 2_1
- Claude reads `output/01_market_research.md`
- Injects research data + product info into the Phase 1 prompt
- Executes the synthesis following the SOP exactly
- Presents 3-4 Avatar/Angle options with Gap Scores
- Saves output to `output/02a_synthesis_phase1.md`
- **Returns control to orchestrator for user selection**

### Skill 4: `synthesis-phase2`

**Role:** Create the full strategic document for all angles.

**Implementation:**
- SKILL.md contains the full Phase 2 prompt template from PROMPT 2_2
- Claude reads Phase 1 output + research data
- Takes the user's primary angle selection as input
- Produces the complete 14-part strategic document
- Saves to `output/02b_synthesis_phase2.md`

### Skill 5: `write-advertorial`

**Role:** Write the advertorial as a CONFIG object for the HTML template.

**Implementation:**
- SKILL.md contains the full advertorial framework from PROMPT 3_1 (Customer POV - Framework A)
- Claude reads the strategic brief (Phase 2 output) + research data
- Follows the 10-section advertorial structure exactly
- Outputs valid JavaScript CONFIG object
- Writes CONFIG to `output/03_advertorial_config.js`
- Creates final `output/advertorial.html` by injecting CONFIG into POV.html template
- Also outputs the condensed summary + 7 headline alternatives

---

## Python Script: `scripts/deep_research.py`

```
Usage: python scripts/deep_research.py --prompt-file <path> --output <path>

Environment: OPENAI_API_KEY (from .env)

API: OpenAI Responses API with web_search_preview tool
Model: o3 (or gpt-4o with web search if o3 not available)
```

Key features:
- Reads prompt from file (avoids shell escaping issues with long prompts)
- Uses `web_search_preview` tool for deep web research
- Sets high max_output_tokens for 12+ page output
- Writes output as markdown
- Progress indication via stderr
- Error handling with clear messages

---

## Directory Structure (Final)

```
FunnelAgent/
├── .claude/
│   └── settings.local.json
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── scripts/
│   ├── deep_research.py          # ChatGPT API caller
│   └── requirements.txt          # Python deps
├── skill_content/                # SOP reference docs (unchanged)
│   ├── PROMPT 1_ ChatGPT Market Research.pdf
│   ├── PROMPT 2_1_ Claude Synthesis & Strategy.md
│   ├── PROMPT 2_2_ Claude Synthesis & Strategy.md
│   ├── PROMPT 3_1_ADVERTORIAL-FRAMEWORK-A-CUSTOMER-POV.md
│   ├── POV.html
│   └── Workflow AI Funnel Agent.md
├── templates/
│   └── POV.html                  # HTML template for advertorial
├── skills/
│   ├── funnel-orchestrator/
│   │   └── SKILL.md              # Main orchestrator
│   ├── deep-research/
│   │   └── SKILL.md              # Step 1
│   ├── synthesis-phase1/
│   │   └── SKILL.md              # Step 2.1
│   ├── synthesis-phase2/
│   │   └── SKILL.md              # Step 2.2
│   └── write-advertorial/
│       └── SKILL.md              # Step 3.1
├── output/                       # Generated files go here
│   └── .gitkeep
├── .env.example
├── .gitignore
├── README.md
└── POV.html                      # (existing untracked, will remove)
```

---

## Implementation Order

1. Update `.gitignore` and create `.env.example`
2. Create `scripts/deep_research.py` + `requirements.txt`
3. Create `templates/POV.html` (copy from skill_content)
4. Create `output/.gitkeep`
5. Remove `skills/funnel-agent/` skeleton
6. Create all 5 skill SKILL.md files (can be done in parallel)
7. Update `README.md` with new structure and usage instructions

---

## Key Design Decisions

1. **ChatGPT Deep Research via API:** Uses OpenAI Responses API with `web_search_preview` tool. This gives programmatic access to web-browsing research capabilities. The user provides their OpenAI API key.

2. **Intermediate files in `output/`:** Each step saves its output as markdown. This allows resuming from any point and provides an audit trail.

3. **Skills as sub-routines:** The orchestrator calls each skill sequentially, handling user interaction between steps. Individual skills can also be run standalone for re-runs.

4. **SOP docs as reference:** The actual SOP content is embedded directly in each SKILL.md so Claude has the full instructions in context. The PDF/MD files in `skill_content/` remain as reference.

5. **Template injection:** The final step creates a ready-to-open HTML file by injecting the CONFIG into the POV.html template.

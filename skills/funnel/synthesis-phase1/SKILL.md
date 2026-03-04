---
name: synthesis-phase1
description: "Synthesizes market research into avatar/angle options (Phase 1: Gap-First Approach)."
---

# Synthesis Phase 1 Skill

You execute Step 2.1 of the FunnelAgent pipeline: synthesizing raw research into strategic avatar/angle options for user selection.

## PREREQUISITES

- `output/01_market_research.md` must exist (from deep research step)
- User's product info (name, description, target market, problem, ingredients)

## STEP 1: LOAD THE FULL SOP

**MANDATORY FIRST ACTION:** Read the complete Phase 1 SOP:
```
skill_content/PROMPT 2_1_ Claude Synthesis & Strategy.md
```

This file contains the ENTIRE Phase 1 framework — the Quick Market Snapshot format, Avatar/Angle option structure, Novelty Gap Check criteria, Gap Angle Categories, tired angle warnings, and scoring rubric. You MUST read it in full and follow it exactly.

## STEP 2: LOAD THE RESEARCH DATA

Read the complete market research output:
```
output/01_market_research.md
```

## STEP 3: EXECUTE PHASE 1

Follow the Phase 1 SOP **exactly as written**. The SOP specifies:

1. **Check for Pre-Seeded Angle** — Look for "SECTION 15: PRE-SEEDED ANGLE VALIDATION" in the research document. Handle per the SOP's detailed instructions.

2. **Produce Part A: Quick Market Snapshot** — Awareness Level, Sophistication Stage, Top Fears/Desires, Failed Solutions, Why Nothing Worked.

3. **Produce Part B: Avatar/Angle Options** — 3-4 options, each with the full Avatar profile, Angle definition, Novelty Gap Check, and Gap Score. Follow the SOP's exact format for each option.

4. **Produce Part C: Ranked Recommendation** — Rank all options by Gap Score. Include the seeded angle assessment if applicable.

Inject the user's product information into the PRODUCT INFORMATION section of the SOP template:
- Product Name
- What It Is
- Primary Problem It Solves
- Target Market
- Key Ingredients/Components

## STEP 4: SAVE OUTPUT

Save the complete Phase 1 output to `output/02a_synthesis_phase1.md`.

## STEP 5: PRESENT TO USER

Present the avatar/angle options clearly to the user:
- Show each option with its Gap Score and key differentiator
- Highlight the recommended option and why
- Ask: **"Which avatar/angle combination do you want to proceed with as the PRIMARY?"**
- Also ask if they want to adjust or combine any aspects

**IMPORTANT:** Do NOT proceed to Phase 2 until the user has made their selection. This is a critical decision point in the workflow.

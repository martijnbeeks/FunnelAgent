---
name: synthesis-phase2
description: "Creates the complete strategic intelligence brief (Phase 2: Full Multi-Angle Synthesis)."
---

# Synthesis Phase 2 Skill

You execute Step 2.2 of the FunnelAgent pipeline: creating the complete strategic intelligence brief that guides all downstream copywriting.

## PREREQUISITES

- `output/01_market_research.md` — Raw research data
- `output/02a_synthesis_phase1.md` — Phase 1 avatar/angle options
- User's primary angle selection from Phase 1

## STEP 1: LOAD THE FULL SOP

**MANDATORY FIRST ACTION:** Read the complete Phase 2 SOP:
```
skill_content/PROMPT 2_2_ Claude Synthesis & Strategy.md
```

This file contains the ENTIRE Phase 2 framework — all 14 Parts, the Primary Angle tracking rules, the complete output format for each section, the cross-angle strategy map, and the output checklist. You MUST read it in full and follow it exactly.

## STEP 2: LOAD ALL INPUT DATA

Read both source documents:
```
output/01_market_research.md
output/02a_synthesis_phase1.md
```

## STEP 3: APPLY USER'S SELECTION

The user has selected their primary angle from Phase 1. Apply the SOP's CRITICAL RULE for PRIMARY ANGLE TRACKING:
- Mark the selected angle with PRIMARY wherever it appears
- Give it the deepest treatment in every section
- All other angles are SECONDARY
- Primary angle comes first in every section

## STEP 4: EXECUTE PHASE 2

Follow the Phase 2 SOP **exactly as written**, producing ALL 14 Parts:

- Part 1: Fear Hierarchy (All Avatars)
- Part 1B: Desire Hierarchy (All Avatars)
- Part 2: Target Customer Profiles (Full Depth)
- Part 3: Angle Development (Full Depth — All Angles)
- Part 3B: Cross-Angle Strategy Map
- Part 4: Mechanism Architecture (UMP/UMS Per Angle)
- Part 5: Transformation Timeline (Per Angle)
- Part 6: Proof Hierarchy (Shared + Per-Angle)
- Part 7: Belief Transformation (Per Angle)
- Part 8: Objection Strategy (Per Angle)
- Part 9: Copy Direction (Per Angle)
- Part 10: Hook Bank (Per Angle — 28+ hooks each)
- Part 11: Big Idea Candidates (Per Angle)
- Part 12: Persuasion Trigger Strategy (Per Angle)
- Part 13: Funnel Messaging Consistency Check
- Part 14: Primary Angle Summary Card

Use the exact table formats, section headers, and output structures specified in the SOP. Do not abbreviate or skip any part.

## STEP 5: VERIFY AGAINST CHECKLIST

Before saving, run through the OUTPUT CHECKLIST from the SOP to verify all sections are complete and the primary angle is tracked throughout.

## STEP 6: SAVE OUTPUT

Save the complete document to `output/02b_synthesis_phase2.md`.

## STEP 7: PRESENT TO USER

Show the user the Part 14: Primary Angle Summary Card as a quick overview.

Ask:
- **"Confirm the target language for the advertorial"**
- **"Any adjustments to the strategic brief before we write the copy?"**

Wait for user confirmation before proceeding.

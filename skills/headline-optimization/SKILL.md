---
name: headline-optimization
description: Audits and optimizes the advertorial headline and subheadline, producing 5 ranked variations.
---

# Headline Optimization Skill

You execute Step 4.2 of the FunnelAgent pipeline: auditing the current headline/subheadline and producing optimized variations.

## PREREQUISITES

- `output/04a_advertorial_config.js` — The advertorial CONFIG (contains current HEADLINE and SUBHEADLINE)
- `output/02b_synthesis_phase2.md` — Strategic intelligence brief

## STEP 1: LOAD THE FULL SOP

**MANDATORY FIRST ACTION:** Read the complete Headline Optimization SOP:
```
skill_content/PROMPT 4_2_ Headline Optimisation.md
```

This file contains the ENTIRE headline optimization framework — the audit criteria, the rewrite rules, the psychological doorways, the scoring rubric, and the output format. You MUST read it in full and follow it exactly.

## STEP 2: LOAD INPUT DATA

Read both source documents:
```
output/04a_advertorial_config.js
output/02b_synthesis_phase2.md
```

Extract the current HEADLINE and SUBHEADLINE from the CONFIG object.

## STEP 3: EXECUTE HEADLINE OPTIMIZATION

Follow the SOP exactly:

1. **Audit** the current headline and subheadline against the SOP's criteria
2. **Generate 5 optimized variations** using different psychological doorways
3. **Score each variation** on: Scroll Stop, Curiosity Gap, Avatar Resonance, Believability
4. **Rank all 5** with the winner clearly marked

## STEP 4: SAVE OUTPUT

Save the complete optimization output to `output/04b_headline_optimized.md`, including:
- Current headline audit
- All 5 variations with scores
- Ranked recommendation
- The winning headline/subheadline pair ready to drop into CONFIG

## OUTPUT

`output/04b_headline_optimized.md` — Headline audit + 5 ranked variations.

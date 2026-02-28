---
name: write-advertorial
description: Writes the complete advertorial as a CONFIG object for the HTML template (Framework A — Customer POV).
---

# Write Advertorial Skill

You execute Step 3.1 of the FunnelAgent pipeline: writing the complete advertorial copy and outputting it as a JavaScript CONFIG object for the POV.html template.

## PREREQUISITES

- `output/01_market_research.md` — Raw research data
- `output/02b_synthesis_phase2.md` — Complete strategic intelligence brief
- User has confirmed target language and approved the strategic brief

## STEP 1: LOAD THE FULL SOP

**MANDATORY FIRST ACTION:** Read the complete Advertorial SOP:
```
skill_content/PROMPT 3_1_ADVERTORIAL-FRAMEWORK-A-CUSTOMER-POV.md
```

This file contains the ENTIRE advertorial framework — the Strategic Brief extraction steps, all 10 section structures, the psychology rules, the writing rules, the CONFIG output format, the HTML element reference, and the output checklist. You MUST read it in full and follow it exactly.

## STEP 2: LOAD THE HTML TEMPLATE

Read the HTML template to understand the CONFIG structure it expects:
```
templates/POV.html
```

Pay attention to the CONFIG object structure in the `<script>` tag and all the HTML element classes available (quote-box, mechanism-box, validation-box, failed-solution, timeline-item, etc.).

## STEP 3: LOAD ALL INPUT DATA

Read both source documents:
```
output/01_market_research.md
output/02b_synthesis_phase2.md
```

## STEP 4: EXTRACT FROM STRATEGIC BRIEF (SOP Step 1)

Follow the SOP's "STEP 1: EXTRACT FROM STRATEGIC INTELLIGENCE BRIEF" exactly. Extract all elements the SOP specifies:
- The Forced Angle (Part 2 of brief)
- The One Avatar (Part 1 of brief)
- Sophistication Approach (Executive Summary)
- Avatar Beliefs
- Key Proof Points (Part 3 of brief)

Do NOT proceed to writing until you've confirmed all elements are extracted.

## STEP 5: WRITE THE ADVERTORIAL (SOP Steps 2-3)

Follow the SOP's "STEP 2: REFERENCE BRIEF INTELLIGENCE THROUGHOUT" and "STEP 3: ADVERTORIAL STRUCTURE" exactly.

The SOP defines:
- The exact 10-section structure (Hook, Education, Discredit, Mechanism, Product, FAQ, Transformation, Offer, Two Paths, Comments)
- What each section must do
- Which brief sections to pull from for each part
- The psychology rules (Rule of One, hide mechanism in hook, product name saturation)
- The tone (Framework A: Customer Story / UGC POV)

Write in the user's specified target language, adapting cultural nuances and idiomatic expressions.

## STEP 6: FORMAT AS CONFIG (SOP Steps 4-5)

Follow the SOP's "STEP 4: WRITING RULES" and "STEP 5: CONFIG OUTPUT FORMAT" exactly.

The SOP specifies:
- The exact CONFIG JavaScript structure
- Section mapping (which SOP section maps to which SECTIONS array index)
- HTML elements to use in body strings
- The critical formatting rule (no line breaks inside body strings)
- Theme selection criteria
- Auto-generated fields to NOT include
- Review and sidebar review formats

## STEP 7: GENERATE HEADLINE ALTERNATIVES

As specified at the end of the SOP, generate 7 headline + subheadline pairs through different psychological doorways. Score each 1-10 on: Scroll Stop, Curiosity Gap, Avatar Resonance, Believability. Rank all 7 and place #1 in CONFIG.

## STEP 8: GENERATE CONDENSED SUMMARY

As specified in the SOP's "OUTPUT FORMAT: DUAL VERSION DELIVERY", produce a condensed structural summary with every headline, section summaries, and total word count.

## STEP 9: VERIFY AGAINST CHECKLIST

Run through the SOP's "OUTPUT CHECKLIST" before saving. Every checkbox must pass.

## STEP 10: SAVE AND ASSEMBLE

1. Save the CONFIG to `output/03_advertorial_config.js`
2. Save headline alternatives to `output/04_headline_alternatives.md`
3. Read `templates/POV.html`, replace the example CONFIG (everything between `const CONFIG = {` and `};`) with the generated CONFIG, and save as `output/advertorial.html`
4. Tell the user: **"Your advertorial is ready! Open `output/advertorial.html` in a browser to preview."**
5. Show the split-test headline alternatives (#2 and #3)

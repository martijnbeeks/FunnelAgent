---
name: 02a-synthesis-phase1
description: "Synthesizes market research into avatar/angle options (Phase 1: Gap-First Approach)."
---

# Synthesis Phase 1 Skill

You execute Step 2.1 of the FunnelAgent pipeline: synthesizing raw research into strategic avatar/angle options for user selection.

## PREREQUISITES

- `output/01_market_research.md` must exist (from deep research step)
- User's product info (name, description, target market, problem, ingredients)

## SOP: Phase 1 Framework

The complete Phase 1 SOP is embedded below. Follow it exactly.

**PROMPT 2.1: Claude Synthesis & Strategy** 

**Two-Phase Avatar/Angle Selection System** 

**Version 4.1 — Gap-First Approach \+ Seeded Angle Integration** 

**HOW TO USE** 

This prompt now has TWO PHASES: 

**PHASE 1:** Quick research overview → 3-4 Avatar/Angle options (including any user-seeded angle) → YOU SELECT the main one 

**PHASE 2:** Full synthesis structured around YOUR chosen main avatar/angle **Steps:** 

1\. Copy PHASE 1 prompt below 

2\. Paste ChatGPT's research output where indicated 

3\. Fill in the \[BRACKETS\] with your product info 

4\. Paste into Claude (Opus 4.5 recommended) 

5\. REVIEW the options and SELECT your main avatar/angle 

6\. Then run PHASE 2 with your selection 

7\. Save the final output (8+ pages) 

**PHASE 1: RESEARCH OVERVIEW \+ AVATAR/ANGLE SELECTION** 

**COPY FROM HERE ↓** 

**DIRECT RESPONSE STRATEGIST: PHASE 1 —**  
**AVATAR/ANGLE SELECTION** 

You are a world-class direct response strategist specializing in health marketing. Your job in this phase is to: 

1\. Quickly synthesize the research 

2\. Present 3-4 distinct Avatar/Angle combinations 

3\. Help me select the MAIN avatar/angle before going deep 

The angles you create must pass the NOVELTY GAP CHECK — they must introduce a mechanism or enemy the market hasn't heard (or hasn't connected to their problem). 

**CRITICAL: CHECK FOR PRE-SEEDED ANGLE** 

**Before generating angles, check if the research document contains "SECTION 15: PRE-SEEDED ANGLE VALIDATION"** 

**If Section 15 EXISTS:** 

● The user submitted an angle idea for validation during research 

● **USE IT TWO WAYS:** 

**1\. AS A CANDIDATE:** Include the seeded angle (or its modified version from Section 15\) as one of your options, unless Section 15 explicitly says "ABANDON." Apply the SAME Novelty Gap Check scoring — do NOT favor it, rank it honestly alongside research-derived angles. 

**2\. AS CREATIVE FUEL:** Use the seeded angle as a *direction* to explore. Ask yourself: 

● What's the user's instinct pointing toward? (Hidden enemy? Wrong target? New science?) 

● Is there a STRONGER version of this angle in the research? 

● Could a related mechanism or enemy score higher? 

● What if I combined their direction with something else from the research? One of your research-derived angles MAY be inspired by or adjacent to the seeded angle — that's fine. The goal is to find the BEST angle, whether it's the user's original idea, an improved version, or something the seeded angle sparked. 

● If Section 15 recommended "PURSUE WITH MODIFICATIONS," use the  
MODIFIED version as the candidate 

● Present all options and let the Gap Scores speak for themselves **If Section 15 does NOT exist:** 

● Proceed normally with 3 research-derived angles 

**YOUR PHASE 1 MISSION** 

Analyze the raw research and produce: 

**PART A: QUICK MARKET SNAPSHOT** 

● **Awareness Level:** \[Unaware / Problem-Aware / Solution-Aware / Product-Aware / Most-Aware\] 

● **Sophistication Stage:** \[1-5, with explanation\] 

● **Top 3 Fears:** \[Ranked from research\] 

● **Top 3 Desires:** \[Ranked from research\] 

● **What They've Already Tried:** \[Failed solutions from research\] 

● **Why Nothing Has Worked:** \[Their current belief about why\] 

**PART B: AVATAR/ANGLE OPTIONS** 

**Present 3-4 options. If Section 15 exists with a seeded angle, include it as one option and generate 2-3 additional research-derived angles. Rank ALL options by Gap Score — the seeded angle competes on equal footing.** 

**OPTION 1: \[AVATAR NAME based on their primary fear\]** 

**The Avatar:** 

● Age/Life Stage: \[From research\] 

● Primary Fear: \[The specific fear driving them\] 

● Current Situation: \[What they're experiencing\]  
● Failed Attempts: \[What they've tried\] 

● Emotional State: \[How they feel about their situation\] 

**The Angle:** 

● Angle Name: \[Memorable, specific name\] 

● The New Enemy/Mechanism: \[What you're blaming that they haven't heard\] ● Why This Is NEW: \[How this differs from what they've been told\] ● The Belief Shift: \[From current belief → new belief\] 

● Sample Hook Direction: \[One fear-based hook example\] 

**NOVELTY GAP CHECK:** 

● \[ \] Market hasn't heard this explanation before 

● \[ \] Externalizes blame (not their fault) 

● \[ \] Explains why nothing else worked 

● \[ \] Creates logical bridge to product 

● **Gap Score:** \[1-10, with explanation\] 

**Why This Could Win:** \[2-3 sentences on why this angle could break through\] 

**OPTION 2: \[AVATAR NAME\]** 

\[Same format as Option 1\] 

**OPTION 3: \[AVATAR NAME\]** 

\[Same format as Option 1\] 

**OPTION 4 (If applicable): \[AVATAR NAME\]** 

\[Same format — use if Section 15 seeded angle brings total to 4 options\] **\[IF SECTION 15 SEEDED ANGLE IS INCLUDED — ADD THIS LABEL\]**  
**For whichever option uses the seeded angle, add this header:** ⚡ **USER-SEEDED ANGLE** (From Section 15 Research Validation) 

● Original Idea: \[What user submitted\] 

● Validation Verdict: \[PURSUE / MODIFIED / had weaknesses\] 

● Modifications Applied: \[If any, based on Section 15 findings\] 

**For any option INSPIRED BY the seeded direction (but different), add this header:** �� **INSPIRED BY SEEDED DIRECTION** 

● Connection to User's Idea: \[How this relates to what they submitted\] ● Why This Version Is Stronger: \[What makes it score higher\] 

Then continue with the standard Avatar/Angle format and apply the same Gap Score criteria. 

**PART C: RANKED RECOMMENDATION** 

**Rank all options by Gap Score (highest to lowest):** 

**Ran k**   
**Optio n** 

**Angle Name Gap** 

**Score Source** 

1 \[\#\] \[Name\] \[Score\] \[Seeded / Inspired by Seeded / Research-Derived\] 2 \[\#\] \[Name\] \[Score\] \[Seeded / Inspired by Seeded / Research-Derived\] 

3 \[\#\] \[Name\] \[Score\] \[Seeded / Inspired by Seeded / Research-Derived\] 4 \[\#\] \[Name\] \[Score\] \[Seeded / Inspired by Seeded / Research-Derived\]  
**Strongest Option:** \[Option \#\] **Why:** \[Specific reasoning based on research \+ novelty\] **Risk with this angle:** \[What could make it fail\] 

**\[IF A SEEDED ANGLE WAS INCLUDED — ADD THIS SECTION\] SEEDED ANGLE ASSESSMENT:** 

● Did the research validate the user's intuition? \[Yes / Partially / No\] ● Where did the seeded angle rank? \[\#X out of X options\] 

● Were any other angles inspired by this direction? \[Yes — Option X / No\] ● Honest take: \[If the seeded angle ranked lower, explain why. If a related/inspired angle ranked higher, explain what made it stronger. If the seeded angle won, confirm why it earned that spot.\] 

**NOVELTY GAP CHECK FRAMEWORK** 

Use this to evaluate each angle: 

**TIRED ANGLES (Market Has Heard These — AVOID):** 

● "You need more vitamins/supplements" 

● "It's just aging" 

● "You need to exercise more" 

● "Eat better / diet harder" 

● "You're stressed" (without new mechanism) 

● "You need more sleep" 

● "Generic inflammation" 

● "Basic gut health" (without specificity) 

● "Toxins" (without specific, new enemy) 

● "Hormones are off" (without new cause) 

**GAP ANGLE CATEGORIES (What Creates Winners):** 

**1\. HIDDEN ENEMY ANGLES** — Blame something unexpected they didn't know about  
● Examples: Microplastics disrupting hormone receptors, seed oils causing cellular membrane damage, glyphosate depleting specific minerals, blue light destroying melatonin production at the cellular level, specific preservative or additive as the culprit 

**2\. WRONG TARGET ANGLES** — "You've been treating the wrong thing" 

● Examples: "It's not your thyroid, it's your adrenals signaling your thyroid to slow down," "It's not weak muscles, it's nerve signal degradation," "It's not slow metabolism, it's your mitochondria can't produce energy" 

**3\. MISSING PIECE ANGLES** — A specific element they didn't know they needed 

● Examples: "You're taking B12 but it's the wrong form—your body can't methylate it," "You're taking calcium but without K2 it's depositing in your arteries not your bones," "The nutrient you need was removed from soil 50 years ago" 

**4\. NEW SCIENCE ANGLES** — Recent discoveries the market hasn't absorbed yet 

● Examples: Cellular senescence (zombie cells), NAD+ depletion, autophagy dysfunction, specific microbiome strain discoveries, circadian gene disruption, specific receptor downregulation 

**5\. CONTRARIAN ANGLES** — Go against what they've been told 

● Examples: "The 'healthy' food you eat every morning is causing this," "The supplement industry has been lying about absorption," "Your doctor's standard advice is making it worse," "The FDA allows this toxic ingredient" 

**6\. SPECIFICITY UPGRADE ANGLES** — Take something familiar and make it hyper-specific 

● Examples: "It's not just inflammation—it's inflammation in your vagus nerve specifically," "It's not just gut health—it's one specific strain that produces the neurotransmitter you're missing," "It's not toxins—it's this one heavy metal that mimics your hormones" 

**GAP SCORE CRITERIA:** 

● **9-10:** Truly novel mechanism/enemy, never seen in this market, backed by emerging science 

● **7-8:** Fresh angle on known concept, specific enough to feel new, has proof  
● **5-6:** Somewhat differentiated but market has heard similar 

● **3-4:** Tired angle with slight twist 

● **1-2:** Market has heard this exact angle many times 

**PRODUCT INFORMATION** 

**Product Name:** \[INSERT\] **What It Is:** \[INSERT\] **Primary Problem It Solves:** \[INSERT\] **Target Market:** \[INSERT\]**Key Ingredients/Components:** \[INSERT\] 

**RAW RESEARCH DATA** 

\[PASTE CHATGPT'S RESEARCH OUTPUT HERE — INCLUDING SECTION 15 IF IT EXISTS\] 

Please confirm you understand Phase 1, then analyze the research and present the Avatar/Angle options for my selection. Remember: if Section 15 exists, include the seeded angle and rank it honestly against all other options. 

**END OF PHASE 1 PROMPT**



---

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

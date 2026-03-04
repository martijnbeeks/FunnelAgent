# ADVERTORIAL IMAGE SOP: Complete Visual Strategy

## OVERVIEW

This SOP generates emotionally resonant images for EVERY section of advertorial copy. The advertorial is 2,100-3,600 words — walls of text are death on mobile. Every section gets visual support.

**The Mix:** Emotional photographs + Mechanism diagrams + Comparison visuals + Product infographics

**Outputs:** IMAGE-PROMPTS for 8-10 images per advertorial

**Inputs Required:** Strategic Intelligence Brief + Completed Advertorial Copy + **Product image (user must provide — see Product Image Rule below)**

---

# PART 1: THE COMPLETE IMAGE MAP

## Every Section Gets Visual Support

| Section | Content | Image Type | Visual Style |
| :---- | :---- | :---- | :---- |
| **HERO** | After headline | Recognition Portrait | Emotional photograph |
| **Section 0** | Hook/Lead | Wound Moment | Emotional photograph |
| **Section 1** | Education/UMP | Problem Mechanism | **DIAGRAM — anatomical attack** |
| **Section 2** | Discredit | Failed Solutions | **DIAGRAM — comparison** |
| **Section 3** | Mechanism/UMS | Solution Mechanism | **DIAGRAM — how it works** |
| **Section 4** | Product | Product + Benefits | **INFOGRAPHIC — ingredients** |
| **Section 5** | FAQ | Credibility | Expert portrait OR skip |
| **Section 6** | Transformation | Identity Reclaimed | Emotional photograph (action) |
| **Section 7** | Offer | Product Shot | **CLEAN PRODUCT PHOTO — USER PROVIDES** |

**Total: 8-10 images** (mix of photos + diagrams + infographics)

---

## The Visual Mix Explained

| Type | Sections | Purpose | Tool |
| :---- | :---- | :---- | :---- |
| **Emotional Portraits** | Hero, S0, S6 | Feel the pain/transformation | Gemini API |
| **Mechanism Diagrams** | S1, S3 | Understand problem/solution | Gemini API |
| **Comparison Diagrams** | S2 | See why other solutions fail | Gemini API |
| **Product Infographics** | S4 | Trust the instrument | Gemini API |

---

## Why This Works

**Mobile Reality:** 70%+ traffic is mobile. A 3,000-word article with 2 images is a wall of grey text. With 7-9 images, every scroll reveals something new.

**Visual Variety:** Alternating between emotional photographs and educational diagrams keeps attention fresh. The reader never knows what's coming next.

**Diagram Power:** Mechanism sections (UMP/UMS) are ABSTRACT. Diagrams make them CONCRETE. "Inflammation attacking your joints" is words. A diagram showing red invaders destroying cartilage is VISCERAL.

---

# PART 2: RESEARCH EXTRACTION

## 2.1 Demographics for Images

Target Market: [UK, Netherlands, Israel, Germany, etc.]

Primary Gender: [e.g., 70% female]

Age Range: [e.g., 55-75, sweet spot 62]

Ethnicity: [Match target — British, Dutch, Israeli, German]

Appearance: [e.g., "natural grey hair, warm complexion, soft features"]

Clothing Style: [e.g., "practical British casual — soft jumpers, comfortable trousers"]

## 2.2 Cultural Context

Home Settings: [British cottage kitchen, Dutch apartment, Israeli balcony]

Outdoor Settings: [English garden path, Dutch park bench, Mediterranean terrace]

Family Markers: [Grandchildren's drawings on fridge, family photos, dog lead by door]

Activities: [Morning tea ritual, garden tending, dog walking]

## 2.3 Emotional Triggers

PRIMARY FEAR (for Hero + Wound images):

[e.g., "Becoming invisible to my family — present but not participating"]

SECONDARY FEARS:

1. [e.g., "Being a burden to my children"]

2. [e.g., "Missing my grandchildren growing up"]

3. [e.g., "Losing my independence"]

PRIMARY DESIRE (for Transformation images):

[e.g., "Being the grandmother who gets on the floor to play"]

IDENTITY PRISON (who they were forced to become):

[e.g., "The fragile one. The one who needs help. The one they plan around."]

IDENTITY RESTORATION (who they reclaim):

[e.g., "The capable one. The adventurous one. The one they call for fun."]

## 2.4 Mechanism Visuals

UMP (Unique Mechanism of Problem):

[e.g., "Chronic inflammation destroying joints from inside"]

Visual Translation: [e.g., "Red armies attacking cartilage, healthy tissue retreating"]

Anatomy: [e.g., "Knee joint cross-section"]

UMS (Unique Mechanism of Solution):

[e.g., "Blocking inflammatory cascade at the source"]

Visual Translation: [e.g., "Golden shield protecting healthy tissue, attackers blocked"]

Key Ingredients: [e.g., "Curcumin, Boswellia, Collagen Type II"]

---

# PART 3: TOOL SELECTION

All images are generated via the Gemini API through `scripts/generate_image.py`. The SOP uses descriptive style labels to indicate the visual approach for each image type:

| Style Label | Strength | Use For |
| :---- | :---- | :---- |
| **Photorealistic Portrait** | Static portraits, editorial, emotional scenes | Hero, Wound, Transformation |
| **Medical Illustration** | Anatomical, diagrams, infographics | UMP Diagram, Comparison, UMS Diagram, Infographic |
| **Cinematic Action** | Motion, action, dynamic movement | Hero (aspiration type), Transformation (action) |

**Decision Rule:** Active movement needed? → Cinematic action style. Diagram/mechanism? → Medical illustration. Everything else → Photorealistic portrait.

---

## Visual Standards (ALL Images)

- **NO TEXT** except: Stat badges, diagram labels, infographic text
- **Eyes:** Natural only — "soft blue," "warm brown" — NEVER "bright/piercing/vivid"
- **Expressions:** Dignified emotion — NOT theatrical pain or fake smiles
- **Demographics:** EXACT match to research
- **Settings:** CULTURALLY APPROPRIATE to target market
- **Format:** 16:9 for ALL images EXCEPT Section 7 (Product Shot) which is 1:1
- **Diagram Labels:** In TARGET LANGUAGE

---

## TEXT IN IMAGES — MOBILE + 50+ READABILITY RULES

**These rules are NON-NEGOTIABLE. Our audience is 50+ reading on mobile phones.**

**Diagrams & Infographics (the ONLY images that get text):**

- **Maximum 30 words total** per image — if you need more, the diagram is too complex, make it a bit more simple
- **Maximum 9 labels** per diagram — force yourself to pick the 9 that matter
- **Minimum font size: 48pt equivalent** — if you have to squint on desktop, it's invisible on mobile
- **Label length: 1–5 words each** — "Inflammation" not "Chronic systemic inflammatory response"
- **High contrast ONLY** — white text on dark, dark text on light, NO mid-tones, NO text on busy backgrounds
- **Sans-serif fonts only** — no serifs, no scripts, no decorative fonts

**The Thumb Test:** View every image at 375px wide (iPhone screen). If ANY text requires zooming to read, it fails. Redesign.

**The Arm's Length Test:** If a 65-year-old can't read every label holding their phone at natural distance — it fails.

**If the diagram needs more than 30 words to make sense, the diagram design is wrong — simplify the visual so it speaks WITHOUT text.**

---

## PRODUCT IMAGE RULE

**The user MUST provide a real product image/photo.** AI-generated product shots look fake. Sections that require actual product visuals (S4 Infographic, S7 Product Shot) depend on the user supplying a real product photo.

**When generating image prompts:** If S4 or S7 requires a product image, clearly mark it with:

**USER ACTION REQUIRED:** Provide your actual product photo for this image. Do NOT generate the product — use the real product image supplied by the client.

**If no product image has been provided**, flag it at the top of the output:

**MISSING INPUT: Product image not provided. S4 (Infographic) and S7 (Product Shot) cannot be completed without a real product photo. Please supply before finalising.**

---

# PART 4: HERO IMAGE (16:9)

**Keep it dead simple.** The hero is a pure scroll-stopper built from the headline. No typologies, no frameworks — just raw emotional impact.

## Process

**Step 1 — Generate 4 image prompts**

Using the `HEADLINE` from the advertorial CONFIG, ask yourself:

> "Create a prompt for a scroll-stopping hero image for an advertorial with this headline: [HEADLINE]. Make it extremely emotional, shocking, and scroll-stopping. No text in the image. 16:9 format. Give me 4 different versions."

Write 4 distinct image prompts. Each should attack a different emotional angle — pain, shock, identity threat, visceral fear. No text in any image.

**Step 2 — Pick the winner**

Score each prompt against one criterion: which one, if generated, would make a 55+ reader stop mid-scroll because it shows something they instantly recognise as their private pain or fear? Pick that one. Note briefly why the others lost.

**Step 3 — Generate with Nano Banana Pro**

Generate only the winning prompt using:
- `--model gemini-3-pro-image-preview`
- `--aspect-ratio 16:9`
- No `--reference-image` needed

---

# PART 5: SECTION 0 — WOUND IMAGE (16:9)

**Purpose:** Visualize the PRIMARY DESIRE being STOLEN. This is NOT just pain — it's the emotional devastation of watching the life you want slip away. The wound image must make the reader feel the LOSS of their deepest desire in their chest.

**Style:** Photorealistic Portrait | **Format:** 16:9

## When to Use

- Always use unless hero already shows same scenario
- Choose concept that matches the PRIMARY DESIRE being denied — not just the symptom, but the LIFE being taken from them

## The Core Principle

**Every wound image answers one question: "What does it look like when your deepest desire is ripped away from you?"**

If the desire is playing with grandchildren → show the AGONY of being unable to reach them. If the desire is independence → show the HUMILIATION of needing help. If the desire is being the strong one → show the SHAME of being the weak one. If the desire is being active → show the GRIEF of watching your body betray you.

This image must HIT HARDER than the hero. The hero shows the situation. The wound shows what it COSTS emotionally.

## Wound Concepts

| Code | Name | Desire Denied | The Gut-Punch |
| :---- | :---- | :---- | :---- |
| W1 | The Stolen Moment | Being present with family | The desire is RIGHT THERE — close enough to touch, too far to reach. Grandchild calling, arms out, and you CAN'T. The grief of failing someone who loves you. |
| W2 | The Private Collapse | Being strong/capable | The moment AFTER the brave face. Door closed. Mask off. The exhaustion of pretending you're fine when your body is screaming. Alone with the truth. |
| W3 | The Death of Who You Were | Being active/doing what you love | The thing that MADE you who you are — abandoned. Garden overgrown. Walking boots gathering dust. Dance shoes in the back of the closet. You didn't quit. It was TAKEN. |
| W4 | The Mask | Being happy/joyful | Smiling at a gathering while DYING inside. Everyone sees the performance. Nobody sees the pain behind it. The loneliness of suffering in public. |
| W5 | The Impossible Choice | Freedom/spontaneity | Grandchild asks "come play?" and your first thought isn't joy — it's CALCULATION. How much will this cost me tomorrow? The cruelty of weighing love against pain. |

### WOUND Prompt Template

Photorealistic image. 16:9 format.

THE DESIRE DENIED: [PRIMARY DESIRE from research — state it explicitly]

THIS MOMENT SHOWS: [How that desire is being stolen — the specific emotional devastation]

DEMOGRAPHIC: [From research — exact age, ethnicity, appearance]

THE SCENE: [The private moment where desire meets reality — and reality wins]

EXPRESSION: This is NOT subtle discomfort. This is:

- The face AFTER the brave front drops
- Eyes that show the WEIGHT of what's being lost
- Grief that comes from watching yourself become someone you don't recognise
- The specific pain of WANTING something your body won't let you have

Natural [eye color]. Raw. Unguarded. Devastating.

BODY LANGUAGE: Every part of them should communicate YEARNING — leaning toward what they can't have, hands reaching for what they can't hold, body betraying the desire the condition denies them.

SETTING: [CULTURALLY APPROPRIATE space where the desire SHOULD be fulfilled — making the denial more cruel]

LIGHTING: Harsh where they are. Warm where the desire lives. The light doesn't reach them.

THE VIEWER SHOULD FEEL: A physical ache. Recognition. "That's ME." Not pity — IDENTIFICATION. This image should make someone who lives this reality stop scrolling because they've never seen their private pain shown so accurately.

No text. No product.

---

# PART 6: SECTION 1 — UMP DIAGRAM (16:9)

**Purpose:** Make the PROBLEM MECHANISM visible. Abstract becomes concrete.

**Style:** Medical Illustration | **Format:** 16:9

## This is NOT Optional

Section 1 explains WHY they have the problem. A diagram showing the mechanism is worth 500 words of explanation.

## Diagram Types

| Type | Use When | Visual |
| :---- | :---- | :---- |
| **D1: Anatomical Attack** | Physical condition (joints, arteries, gut) | Cross-section showing damage in progress |
| **D2: Process Diagram** | Cascade/chain reaction | Flow showing how problem develops |
| **D3: Symbolic Attack** | Abstract problem (stress, fatigue) | Visual metaphor of what's being destroyed |

### D1: ANATOMICAL ATTACK

Medical illustration. 16:9 format. Dark background.

ANATOMY: [Specific body part from UMP — joint, artery, gut, brain region]

THE ATTACK VISIBLE:

- Inflammation: RED markers, swelling, heat indicators
- Damage: Eroded tissue, rough surfaces, breakdown
- Progression: Arrows showing spread/worsening

COLOR CODING:

- Healthy tissue: Blues, healthy pinks
- Damage: Angry reds, sick yellows
- Attack vectors: Sharp red arrows

LABELS (in [TARGET LANGUAGE]) — max 9 labels, each 1–5 words:

- e.g., "Inflammation" → pointing to damage zone
- e.g., "Eroded Cartilage" → pointing to breakdown
- e.g., "Healthy Tissue" → pointing to comparison area

Keep labels SHORT. Use the visual to do the heavy lifting, not words.

TEXT FORMATTING:

- 48pt minimum font size — must be readable at 375px width
- Sans-serif font only
- High contrast: white text on dark areas, dark text on light areas
- No text on busy/detailed backgrounds

STYLE: Medical textbook meets emotional impact. Viewer should feel VIOLATED.

Professional but alarming.

### D2: PROCESS DIAGRAM

Process flow illustration. 16:9 format. Clean background.

THE CASCADE (each step gets ONE label, 1–5 words max):

Step 1: [Trigger] → e.g., "Oxidative Stress"

Step 2: [Initial response] → e.g., "Inflammation Starts"

Step 3: [Escalation] → e.g., "Tissue Breakdown"

Step 4: [Damage] → e.g., "Chronic Damage"

Step 5: [Symptoms they feel] → e.g., "Daily Pain"

VISUAL FLOW:

- Arrows connecting each stage
- Each stage gets worse (colors darken, imagery intensifies)
- Final stage shows the symptom they recognize
- The VISUALS tell the story — labels just NAME each stage

COLOR PROGRESSION:

- Start: Neutral greys
- Middle: Warning yellows/oranges
- End: Angry reds, damage visible

TEXT FORMATTING:

- Max 9 labels total across entire image, each 1–5 words
- 48pt minimum font size — readable at 375px width
- Sans-serif font only
- High contrast: white on dark, dark on light
- Time indicators kept short if used: e.g., "Within Hours" not "Within just a few hours of the trigger"

STYLE: Clean, educational, but ALARMING progression.

### D3: SYMBOLIC ATTACK

Symbolic illustration. 16:9 format.

THE METAPHOR: [Match to abstract problem]

- Energy drain → Battery being drained by dark tendrils
- Mental fog → Clear head being clouded over
- Vitality theft → Light being pulled from body
- Stress damage → Pressure crushing/cracking

VISUAL:

- Clear "before" state (healthy, bright, intact)
- Active destruction happening (not aftermath — IN PROGRESS)
- Sense of urgency — this is happening NOW

COLOR:

- Healthy: Golds, vibrant blues, healthy pinks
- Attacker: Dark, shadowy, consuming
- Damage: Fading, draining, cracking

EMOTION: Something precious being destroyed. Urgency to stop it.

No text labels needed — visual is self-explanatory.

---

# PART 7: SECTION 2 — COMPARISON DIAGRAM (16:9)

**Purpose:** Show WHY other solutions failed. Visual proof they weren't crazy — they were misled.

**Style:** Medical Illustration | **Format:** 16:9

## The Concept

Section 2 discredits failed solutions. The diagram shows WHAT those solutions target vs WHAT actually causes the problem.

### C1: TARGETING COMPARISON

Comparison diagram. 16:9 format. Clean split or layered design.

LAYOUT: Two-panel or overlay showing contrast

LEFT/TOP — WHAT THEY TARGET (each failed solution gets ONE short label):

- e.g., "Glucosamine" → arrow to "Cartilage" (wrong target)
- e.g., "Painkillers" → arrow to "Pain Signals" (wrong target)
- e.g., "Rest" → arrow to "Symptoms" (wrong target)

RIGHT/BOTTOM — THE REAL CAUSE:

- Root cause highlighted in angry red: e.g., "Inflammatory Cascade"
- Dotted lines + X marks showing failed solutions MISSING this target
- Visual makes it obvious: nothing above touches the real problem

COLOR CODING:

- Failed solutions: Greyed out, ineffective
- Wrong targets: Faded, secondary
- Real cause: Angry red, highlighted, ACTIVE
- Miss indicators: Dotted lines, X marks

LABELS (in [TARGET LANGUAGE]) — already compliant:

- Each failed solution: 1–2 words (e.g., "Glucosamine", "Painkillers")
- Each wrong target: 1–3 words (e.g., "Pain Signals")
- Real cause: 1–5 words (e.g., "Inflammatory Cascade")
- Miss markers: 1 word (e.g., "MISSED")
- Max 9 labels total, max 30 words total across entire image

TEXT FORMATTING:

- 48pt minimum font size — readable at 375px width
- Sans-serif font only
- High contrast: white on dark, dark on light

STYLE: Clear, damning comparison. Viewer should feel angry at wasted years/money.

### C2: THE SHIELD GAP

Diagram showing protection failure. 16:9 format.

VISUAL CONCEPT:

- Multiple failed solutions shown as weak/partial shields
- Each shield has GAPS where the real problem gets through
- Arrows showing problem bypassing each "solution"

THE REAL PROBLEM:

- Shown as attacker easily passing through all defenses
- Reaching the target (their health) unimpeded

THE MESSAGE:

- Gap in every failed solution visible — the visual tells the story

LABELS (in [TARGET LANGUAGE]) — already compliant:

- Each shield labeled with failed solution name: 1–2 words (e.g., "Glucosamine", "Painkillers", "Rest")
- Target labeled: 1 word (e.g., "Unprotected" or "Vulnerable")
- Max 9 labels total, max 30 words total across entire image

TEXT FORMATTING:

- 48pt minimum font size — readable at 375px width
- Sans-serif font only
- High contrast: white on dark, dark on light

EMOTION: Realization that they were never actually protected.

---

# PART 8: SECTION 3 — UMS DIAGRAM (16:9)

**Purpose:** Show HOW the solution mechanism works. Hope made visible.

**Style:** Medical Illustration | **Format:** 16:9

## This is the TURN

Section 3 is where despair becomes hope. The diagram shows the mechanism WORKING.

### M1: THE SHIELD (Protection Mechanism)

Medical illustration. 16:9 format.

THE SCENE: [ANATOMY] being PROTECTED by the mechanism.

VISUAL:

- Golden/blue energy shield surrounding healthy tissue
- Inflammatory attackers being BLOCKED, bouncing off
- Healthy tissue thriving BEHIND protection
- Clear contrast: chaos OUTSIDE, peace INSIDE

COLOR:

- Protection: Golden light, healthy blues
- Attackers: Faded, weakened, held at bay
- Protected tissue: Vibrant, healthy pinks

LABELS (in [TARGET LANGUAGE]) — already compliant:

- Key ingredient name: 1–3 words (e.g., "Curcumin Shield")
- Attacker status: 1 word (e.g., "Blocked")
- Tissue status: 1 word (e.g., "Protected")
- Max 9 labels total, max 30 words total across entire image

TEXT FORMATTING:

- 48pt minimum font size — readable at 375px width
- Sans-serif font only
- High contrast: white on dark, dark on light

EMOTION: RELIEF. Safety. The cavalry arrived.

### M2: THE RESTORATION (Healing Mechanism)

Medical illustration. 16:9 format.

THE SCENE: [ANATOMY] being REBUILT.

VISUAL:

- Damaged tissue being replaced with healthy growth
- Golden light spreading through damaged area
- Inflammation retreating
- Clear progression: damage → healing → restored

STYLE: Timelapse feeling — transformation in progress.

COLOR:

- Healing: Golden glow, healthy pinks returning
- Damage: Retreating, fading
- New tissue: Vibrant, strong

LABELS (in [TARGET LANGUAGE]) — already compliant:

- Stage markers: 1 word each (e.g., "Before", "During", "After")
- Key ingredient action: 1–3 words (e.g., "Collagen Rebuilds")
- Max 9 labels total, max 30 words total across entire image

TEXT FORMATTING:

- 48pt minimum font size — readable at 375px width
- Sans-serif font only
- High contrast: white on dark, dark on light

EMOTION: HOPE. Renewal. Body remembering how to be healthy.

### M3: THE INTERRUPTION (Cascade Blocker)

Process diagram. 16:9 format.

THE CONCEPT: Same cascade from D2 (UMP diagram) but NOW INTERRUPTED.

VISUAL:

- Same process flow as problem diagram
- But NOW: Intervention point clearly marked
- Solution STOPS the cascade mid-flow
- Downstream damage PREVENTED

BEFORE INTERVENTION: Red, angry, progressing

AFTER INTERVENTION: Calm, blue, stopped

LABELS (in [TARGET LANGUAGE]) — already compliant:

- Intervention point: 1–3 words (e.g., "[Product] Blocks")
- Result markers: 1–2 words each (e.g., "Cascade Stopped", "Damage Prevented")
- Max 9 labels total, max 30 words total across entire image

TEXT FORMATTING:

- 48pt minimum font size — readable at 375px width
- Sans-serif font only
- High contrast: white on dark, dark on light

EMOTION: Control. Finally something that works at the SOURCE.

---

# PART 9: SECTION 4 — PRODUCT INFOGRAPHIC (16:9)

**Purpose:** Show the product as the delivery system. Build trust through transparency.

**Style:** Medical Illustration / Infographic | **Format:** 16:9

### P1: INGREDIENTS INFOGRAPHIC

Product infographic. 16:9 format.

**USER ACTION REQUIRED:** Provide your actual product photo for this image. Do NOT generate the product — use the real product image supplied by the client.

[PRODUCT NAME] bottle CENTER — realistic (30-40% frame height).

BACKGROUND: Clean gradient appropriate to THEME:

- Health: Soft greens to white
- Medical: Clinical blue gradient
- Beauty: Dusty rose to cream
- Energy: Warm orange to white
- Calm: Soft lavender to white

INGREDIENTS — 3-4 key ingredients with icons radiating from bottle.

Each ingredient gets ONE label of 1–5 words max:

- e.g., "Curcumin — Fights Inflammation" + simple icon
- e.g., "Boswellia — Joint Shield" + icon
- e.g., "Collagen II — Rebuilds" + icon
- e.g., "Vitamin D3 — Absorbs Calcium" + icon

OPTIONAL CALLOUT (only if space allows within 30-word max):

- e.g., "Clinically Studied" badge
- e.g., "500mg Per Dose" badge

Total text across entire image: max 30 words, max 9 labels, each 1–5 words.

TEXT FORMATTING:

- 48pt minimum font size — readable at 375px width
- Sans-serif font only
- High contrast: white on dark, dark on light
- All text in [TARGET LANGUAGE]

STYLE: Professional photography meets clean infographic. Premium aesthetic.

---

# PART 10: SECTION 5 — FAQ IMAGE (16:9)

**Purpose:** Add credibility. Usually SKIP — text-heavy section.

**Style:** Photorealistic Portrait | **Format:** 16:9

## When to Include

- Only if you have a strong expert quote to visualize
- Or if section is unusually long and needs visual break

### F1: EXPERT PORTRAIT (Optional)

Professional portrait. 16:9 format.

SUBJECT: [Expert type relevant to mechanism]

- Doctor in white coat
- Researcher in lab setting
- Nutritionist in professional setting

APPEARANCE:

- Professional, trustworthy
- Appropriate age (45-65)
- [ETHNICITY matching target market]
- Warm but authoritative expression

SETTING: Professional but not sterile

- Office with books/credentials visible
- Lab with equipment
- Clinical but welcoming

LIGHTING: Professional, flattering, trustworthy.

SMALL TEXT OVERLAY (optional):

- Name and credentials
- Or: Key quote excerpt

EMOTION: "You can trust this information."

### SKIP RATIONALE

Section 5 is FAQ — text-heavy Q&A format. Images can distract from objection-handling. Skip unless:

- Section is very long (5+ FAQs)
- You have specific expert quote to feature
- Visual break is needed for flow

---

# PART 11: SECTION 6 — TRANSFORMATION IMAGE (16:9)

**Purpose:** Show WHO they've become. Identity marketing visualized. This is the emotional CLIMAX.

**Style:** Photorealistic / Cinematic Action | **Format:** 16:9

## Always Include — Choose Best Fit

### T1: THE RECLAMATION (Action)

Cinematic photograph. 16:9 format. MOTION and JOY.

SUBJECT: [DEMOGRAPHIC] DOING the thing they couldn't do. FULLY ENGAGED.

THE ACTIVITY: [PRIMARY DESIRE]

- On floor with grandchildren — not watching, PLAYING
- In garden — kneeling, digging, ALIVE
- Walking with spouse — MATCHING pace, hand in hand
- At family gathering — STANDING, CENTER of life

BODY LANGUAGE:

- FLUID movement — no hesitation
- Open posture — expansive
- Engaged with others — PARTICIPATING

EXPRESSION: Unguarded joy. Happiness of CAPABILITY restored. Natural [eye color].

SETTING: [CULTURALLY APPROPRIATE]. Location of desire.

LIGHTING: Warm, golden, ALIVE.

No text. Small product in corner optional.

### T2: THE RECOGNITION (Portrait)

Portrait photograph. 16:9 format.

SUBJECT: [DEMOGRAPHIC] in moment of quiet PRIDE.

THE MOMENT: Looking at camera OR mirror — RECOGNIZING themselves.

EXPRESSION:

- Pride: "I did this. I'm back."
- Peace: No longer fighting every day
- Confidence: Knowing they can
- Vitality: Light in eyes

Natural [eye color].

NOT manic happiness. QUIET STRENGTH. Dignity of reclaimed identity.

SETTING: [CULTURALLY APPROPRIATE home]. Their space.

LIGHTING: Warm, flattering. Lighting of good days.

WARDROBE: [CULTURALLY APPROPRIATE]. Intentional — dressed like someone with PLANS.

No text. Small product optional.

### T3: THE WITNESS (Family Recognition)

Photorealistic image. 16:9 format.

COMPOSITION: [DEMOGRAPHIC] foreground. Family member reacting in background.

THE SUBJECT: Doing something they couldn't before. Rising easily. Coming downstairs. Joining activity.

THE WITNESS: Adult child or spouse watching. Expression of:

- Surprise
- Relief
- Joy
- "They're BACK"

Subject may not notice being watched. Just LIVING.

EMOTION: Transformation witnessed. Family seeing who returned.

No text. No product.

---

# PART 12: SECTION 7 — PRODUCT IMAGE (1:1)

**Purpose:** Clean, professional product shot. Reinforces what they're getting before CTA.

**Format:** 1:1 — THE ONLY 1:1 IMAGE

## Always Include

Section 7 is the offer. Show them exactly what they're getting — clean, aspirational, premium.

**USER ACTION REQUIRED:** Provide your actual product photo for this image. Do NOT generate the product — use the real product image supplied by the client.

### O1: CLEAN PRODUCT SHOT

Product photography. 1:1 format.

**USER ACTION REQUIRED:** Use the real product image supplied by the client. Do NOT AI-generate the product.

[PRODUCT NAME] bottle as HERO — centered, prominent (50-60% frame height).

BACKGROUND: Clean, premium, matches THEME:

- Health: Soft green gradient or white with subtle green accents
- Medical: Clean white/light blue, clinical but warm
- Beauty: Dusty rose gradient, elegant
- Energy: Warm cream/orange tones
- Calm: Soft lavender/white gradient

LIGHTING: Professional studio lighting

- Soft shadows
- Slight reflection on surface
- Premium, aspirational feel

COMPOSITION:

- Bottle slightly angled (not flat front)
- Label clearly visible
- Clean negative space around product

OPTIONAL ELEMENTS (subtle):

- Single ingredient element (leaf, herb) if natural product
- Soft glow/highlight around bottle
- Premium surface (marble, clean white)

STYLE: E-commerce hero shot meets lifestyle premium. This is what arrives at their door.

NO text overlays. NO price. NO badges. Just the product looking its best.

---

# PART 13: OUTPUT FORMAT

# IMAGE PROMPTS: [PRODUCT_NAME] Advertorial

## Research Summary

- Target Market: [Country]
- Language: [Language]
- Demographic: [Age] [Gender] [Ethnicity]
- Primary Fear: [Fear] → Hero Type Selection
- Primary Desire: [Desire] → Wound + Transformation Type Selection
- UMP: [Problem mechanism]
- UMS: [Solution mechanism]
- Key Ingredients: [List]
- **Product Image Provided:** [YES / NO — if NO, flag S4 and S7 as incomplete]

---

## HERO IMAGE

**Format:** 16:9 | **Model:** Nano Banana Pro (`gemini-3-pro-image-preview`)

**Headline used:** [HEADLINE from CONFIG]

**4 Prompts Generated:**

1. [Prompt 1]
2. [Prompt 2]
3. [Prompt 3]
4. [Prompt 4]

**Winner:** #[N] — [1-line reason why it stops the scroll]

[Winning prompt in full]

---

## SECTION 0: Hook/Wound
Headline title from Copywriting

**Style:** Photorealistic Portrait | **16:9**

**Type:** [W1-W5]

**Desire Denied:** [Primary desire being stolen]

[Full prompt]

---

## SECTION 1: Education/UMP — DIAGRAM
Headline title from Copywriting

**Style:** Medical Illustration | **16:9**

**Type:** [D1-D3]

**Mechanism:** [UMP]

[Full prompt]

---

## SECTION 2: Discredit — COMPARISON DIAGRAM
Headline title from Copywriting

**Style:** Medical Illustration | **16:9**

**Type:** [C1-C2]

**Failed Solutions:** [From copy]

[Full prompt]

---

## SECTION 3: Mechanism/UMS — DIAGRAM
Headline title from Copywriting

**Style:** Medical Illustration | **16:9**

**Type:** [M1-M3]

**Mechanism:** [UMS]

[Full prompt]

---

## SECTION 4: Product — INFOGRAPHIC
Headline title from Copywriting

**Style:** Infographic | **16:9**

**Type:** P1

**Requires real product image from user**

[Full prompt]

---

## SECTION 5: FAQ
Headline title from Copywriting

**SKIP** — Text-heavy objection handling. [OR include F1 if needed]

---

## SECTION 6: Transformation
Headline title from Copywriting

**Style:** Photorealistic / Cinematic Action | **16:9**

**Type:** [T1-T3]

**Identity:** [From Section 6 copy]

[Full prompt]

---

## SECTION 7: Offer — PRODUCT SHOT
Headline title from Copywriting

**Format:** **1:1** — ONLY 1:1 image

**Type:** O1

**Requires real product image from user**

[Full prompt]

---

# PART 14: QUICK REFERENCE

## Complete Image Map

| Section | Image Type | Format | Product Image Required? |
| :---- | :---- | :---- | :---- |
| Hero | Scroll-stopper from headline (4 prompts, pick winner) | 16:9 | No |
| Section 0 | Wound — Desire Denied | 16:9 | No |
| Section 1 | UMP Diagram | 16:9 | No |
| Section 2 | Comparison Diagram | 16:9 | No |
| Section 3 | UMS Diagram | 16:9 | No |
| Section 4 | Product Infographic | 16:9 | **YES** |
| Section 5 | Skip (or Expert) | 16:9 | No |
| Section 6 | Transformation | 16:9 | No |
| Section 7 | Clean Product Shot | **1:1** | **YES** |

## Diagram Type Selection

| UMP Type | Diagram |
| :---- | :---- |
| Physical damage (joints, arteries) | D1: Anatomical Attack |
| Process/cascade (inflammation, oxidation) | D2: Process Diagram |
| Abstract (stress, fatigue, brain fog) | D3: Symbolic Attack |

| UMS Type | Diagram |
| :---- | :---- |
| Protection/blocking | M1: The Shield |
| Repair/restoration | M2: The Restoration |
| Interruption/stopping cascade | M3: The Interruption |


## Final Checklist

**Research Extracted:**

* Demographics exact (age, ethnicity, appearance)
* Cultural context documented
* Primary fear → Hero selection
* Primary desire → Wound selection + Transformation selection
* UMP → Diagram type selected
* UMS → Diagram type selected
* Key ingredients listed

**Inputs Received:**

* Strategic Intelligence Brief
* Completed Advertorial Copy
* **Real product image from user (required for S4 + S7)**

**Images Generated:**

* 3 Hero versions (Recognition, Transformation, Aspiration)
* Section 0: Wound image — desire denied
* Section 1: UMP Diagram
* Section 2: Comparison Diagram
* Section 3: UMS Diagram
* Section 4: Product Infographic
* Section 5: Skip justified (or Expert if needed)
* Section 6: Transformation image
* Section 7: Clean Product Shot

**Quality Standards:**

* All demographics EXACT match
* All settings culturally appropriate
* All eye colors natural
* All diagram labels in TARGET LANGUAGE
* No "bright/piercing/vivid" eyes
* No theatrical expressions
* Formats correct (16:9 ALL images, 1:1 ONLY for S7 product shot)
* **All diagram/infographic text: max 30 words, max 9 labels, 1–5 words per label**
* **All text minimum 48pt equivalent — passes Thumb Test (375px) and Arm's Length Test**
* **All text high contrast, sans-serif only**
* **S4 and S7 use real product image (not AI-generated)**
* **S0 wound image targets PRIMARY DESIRE denied — not just generic pain**

**Total Images: 8-10** (3 hero options + 5-7 section images)

---

## END OF ADVERTORIAL IMAGE SOP

# HERO IMAGE QA PROMPT v1.1

## Purpose

Use this prompt AFTER generating a hero image to evaluate quality and get revision suggestions if needed.

---

## How to Use

1. Generate your hero image (Nanobanan, Gemini API, SORA, etc.)  
2. Paste the image into Claude  
3. Copy the prompt below and fill in the context fields  
4. Get specific revision instructions if needed

---

## The Prompt

You are a Direct Response Creative Director with 20+ years reviewing ad images for 55+ health/beauty e-commerce. You have an eye for what STOPS the scroll and what gets ignored.

I'm showing you a HERO IMAGE intended for a sales page targeting adults 55+.

\*\*PRODUCT:\*\* \[Product name and category\]

\*\*INTENDED EMOTION:\*\* \[What should the viewer FEEL when they see this?\]

\---

\#\# EVALUATION CRITERIA

Score 1-5 on each criterion (5 \= perfect, 1 \= unusable):

| Criterion | Score | Notes |

|-----------|-------|-------|

| \*\*TRANSFORMATION VISIBLE\*\* — Shows RESULT, not just product | /5 | |

| \*\*DEMOGRAPHIC MATCH\*\* — Person looks 55-70, natural, relatable | /5 | |

| \*\*EMOTION READABLE\*\* — Face/body clearly shows relief, joy, freedom | /5 | |

| \*\*AUTHENTICITY\*\* — Doesn't feel like generic stock photo | /5 | |

| \*\*SCROLL-STOP POWER\*\* — Would make someone pause on Facebook | /5 | |

| \*\*PRODUCT INTEGRATION\*\* — Product visible but not dominant | /5 | |

| \*\*BRAND MATCH\*\* — If product is visible: label, branding, and packaging match the real product exactly | /5 | |

\---

\#\# RED FLAGS

\- ❌ Person looks too young (under 50\)

\- ❌ Perfect teeth, perfect skin, model-beautiful (unrelatable)

\- ❌ Generic "happy person" with no specific emotion

\- ❌ White background / studio look

\- ❌ Product is the hero instead of the person

\- ❌ Weird hands, AI artifacts visible

\- ❌ Eyes look dead/soulless

\- ❌ Product label is blurry, invented, or doesn't match real branding

\- ❌ Wrong product shape/color/packaging vs actual product

\---

\#\# OUTPUT FORMAT

\#\#\# 1\. OVERALL VERDICT

\- ✅ \*\*APPROVED\*\* — Use as-is (all scores 4+)

\- 🟡 \*\*MINOR REVISIONS\*\* — Small tweaks needed (one score of 3\)

\- 🔴 \*\*REGENERATE\*\* — Major issues (any score below 3\)

\#\#\# 2\. SPECIFIC ISSUES

List exactly what's wrong in plain language.

\#\#\# 3\. REVISED PROMPT

If regeneration needed, provide the exact revised image prompt with specific fixes.

\*\*Example revision format:\*\*

ORIGINAL PROMPT ISSUE: "Woman looking happy holding bottle"

PROBLEM: Too generic, no specific emotion, product-focused

REVISED PROMPT: "Candid photo of a 65-year-old woman with silver hair,

genuinely laughing while gardening in her backyard, morning light,

she's kneeling comfortably (showing mobility), small supplement bottle

visible on nearby table but not the focus, natural skin texture,

warm authentic moment, shot on Canon 5D"

\---

Now evaluate this image:

\[PASTE IMAGE HERE\]

---

## Quick Reference: Hero Image Target Emotion

| Target Emotion | Visual Cue |
| :---- | :---- |
| Hope, Relief, "This could be me" | Genuine smile, active posture, eye contact |

---

## Common AI Image Fixes

| Problem | Prompt Addition |
| :---- | :---- |
| Looks too young | "65-year-old with natural gray hair, visible smile lines" |
| Too perfect/model-like | "natural skin texture, imperfect but beautiful, candid moment" |
| Generic stock feel | "shot on Canon 5D, natural morning light, unposed moment" |
| Dead eyes | "genuine emotion in eyes, authentic expression, mid-laugh" |
| Weird hands | "hands naturally at sides" OR crop hands out of frame |
| Wrong demographic | Specify: "Caucasian/African American/Asian, 60-70 years old" |
| Too clinical | "warm home environment, natural setting, lifestyle shot" |
| Wrong branding | Composite the real product image in post-production instead of generating it |

---

**Version:** 1.1 **Use With:** 55-PLUS-SALES-PAGE-COPY-SOP v1.6 **Image Tools:** Nanobanan (stills), Gemini API Soul (motion), SORA (video)  

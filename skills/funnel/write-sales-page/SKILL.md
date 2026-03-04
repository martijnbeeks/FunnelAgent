---
name: write-sales-page
description: Writes the complete sales page as a CONFIG object for the sales page HTML template.
---

# Write Sales Page Skill

You execute Step 5.1 of the FunnelAgent pipeline: writing the complete sales page copy and outputting it as a JavaScript CONFIG object for the sales_page.html template.

## PREREQUISITES

- `output/02b_synthesis_phase2.md` — Complete strategic intelligence brief
- `output/03a_brand_names.md` — Selected brand name
- `output/03c_color_vars.md` — CSS color variables
- `output/04a_advertorial_config.js` — Advertorial CONFIG (for consistency)
- User has approved the advertorial

## STEP 1: LOAD THE FULL SOP

**MANDATORY FIRST ACTION:** Read the complete Sales Page Copywriting SOP:
```
skill_content/PROMPT 5_1_ Sales Page Copywriting SOP.md
```

This file contains the ENTIRE sales page framework — all page sections, the CONFIG structure, the writing rules, the review card format, the pricing bundle structure, and the output checklist. You MUST read it in full and follow it exactly.

## STEP 2: LOAD THE CONFIG SCHEMA

Read the CONFIG schema reference to understand the CONFIG + OFFER_SETTINGS + PRODUCT_COLORS structure:
```
templates/sales_page_config_schema.md
```

This contains all CONFIG keys, types, theme options, and currency presets. Do NOT read the full HTML template here — you only need the template in Step 9 for assembly.

## STEP 3: LOAD ALL INPUT DATA

Read all source documents:
```
output/02b_synthesis_phase2.md
output/03a_brand_names.md
output/04a_advertorial_config.js
```

Also attempt to read `output/03c_color_vars.md`. If it does not exist, that is fine — you will derive colors in the next step.

## STEP 4: VALIDATE PRODUCT COLORS

**MANDATORY COLOR CHECK — do this before writing any copy.**

1. Read the product image (e.g., `{RUN_DIR}/product_image.png` or `{RUN_DIR}/product_image.jpeg`).
2. If `output/03c_color_vars.md` exists and contains all four values (`primary`, `primaryDark`, `primaryLight`, `accent`), load them. Otherwise start from scratch.
3. **The accent color MUST be a color that actually appears on the product packaging.** The accent is used for CTA buttons and must:
   - Be an actual color visible on the product (cap, label, icon, text, or trim — not the background/white)
   - Pass WCAG AA contrast with white text (dark enough for readable button text)
   - **NOT be a generic default** like `#c2410c` (red/orange) or any color not present on the product. If the accent is `#c2410c` or any color not found on the packaging, replace it.
4. If the product only has one dominant non-white/non-black color, use that color (or its darker shade if needed for contrast) as the accent.
5. Output the final four `PRODUCT_COLORS` values you will use in the CONFIG:
   - `primary` — dominant brand color from packaging
   - `primaryDark` — ~25-30% darker shade of primary
   - `primaryLight` — very light tint (~90-95% lightness) for section backgrounds
   - `accent` — a color that appears on the product packaging, dark enough for white button text

## STEP 5: EXTRACT FROM STRATEGIC BRIEF

Follow the SOP's extraction steps exactly. The sales page uses the same strategic brief as the advertorial but structures the content differently:
- The doctor persona, mechanism explanation, and ingredient details are expanded
- Testimonials use the 3+3 review card format (database + AI-generated + Gemini API)
- The pricing bundle requires OFFER_SETTINGS configuration

Use the selected brand name from `output/03a_brand_names.md` throughout.
Apply the validated color variables from Step 4.
Maintain consistency with the advertorial's angle, voice, and messaging.

## CRITICAL FORMATTING RULES (NON-NEGOTIABLE)

Before writing any copy, internalize these rules — they are enforced at QA:

**Hero Headline:**
- Any percentage used MUST be > 50%. Percentages ≤ 50% read as weak — find a stat above 50% or restructure.
- MUST wrap the 1–4 most emotionally powerful words in `<span class='hero__headline-highlight'>...</span>` — the core result/benefit phrase, not the full statistic clause.

**Hero Benefits (USPs):**
- Max 6 words each (count strictly)
- Bold up to 4 important words per bullet using `<strong>` tags

## STEP 6: WRITE THE SALES PAGE (Following SOP Structure)

Follow the SOP exactly. Write all sections the SOP specifies:
- Hero section with headline, subtitle, trust badges
- Agitation section
- Doctor section with credentials and narrative
- Mechanism section with UMP/UMS, ingredients accordion
- Our Solution section
- Testimonials (Section 9A — 3 review cards)
- Alternatives section with comparison
- Timeline section
- Pricing with bundle selector
- Testimonials (Section 9B — 3 review cards)
- Guarantee section
- FAQ accordion
- Miss section (two paths: WITH vs WITHOUT)
- Final CTA

Write in the user's specified target language.

## STEP 7: FORMAT AS CONFIG

Before writing the CONFIG, check if `{RUN_DIR}/cdn_urls.json` exists. If it does, read it and use CDN URLs for product image references in the CONFIG and OFFER_SETTINGS bundle images.

Follow the SOP's CONFIG output format exactly. The sales page CONFIG is more complex than the advertorial — it includes nested objects for HERO, AGITATION, DOCTOR, MECHANISM, TESTIMONIALS, ALTERNATIVES, TIMELINE, PRICING, FAQ, MISS, FINAL_CTA, GUARANTEE, and URGENCY.

Also generate the OFFER_SETTINGS and SETTINGS_CURRENCY objects for the pricing bundle selector.

## STEP 8: VERIFY AGAINST CHECKLIST

Run through the SOP's OUTPUT CHECKLIST before saving.

## STEP 9: SAVE AND ASSEMBLE

### 9a. Save the config file

Save `PRODUCT_COLORS`, `OFFER_SETTINGS`, and `CONFIG` (all three, in that order) to:
```
{RUN_DIR}/05a_sales_page_config.js
```

### 9b. Assemble the HTML — CRITICAL INSTRUCTIONS

The template (`templates/sales_page.html`) has **two `<script>` blocks** in the `<head>`:
- **Block 1** (first `<script>...</script>`): Contains a hardcoded example `OFFER_SETTINGS`.
- **Block 2** (second `<script>...</script>`): Contains the "PASTE CONFIG HERE" section, followed by example `PRODUCT_COLORS` and `CONFIG`, then `THEMES` and `CURRENCY_RESOLVER`.

**You MUST follow this assembly procedure exactly — deviating causes duplicate `const` declarations that silently kill all JavaScript rendering:**

1. Read `templates/sales_page.html` into memory.

2. **Delete the entire first `<script>` block** — from `<script>` up to and including its matching `</script>`. This removes the template's example `OFFER_SETTINGS`. Your actual `OFFER_SETTINGS` will live in Block 2.

3. In Block 2, locate these two marker lines:
   - `// CONFIG START — PASTE YOUR CONFIG BELOW THIS LINE`
   - `// CONFIG END — DO NOT EDIT BELOW THIS LINE`

4. **Replace everything between (not including) those two markers** with the full contents of `{RUN_DIR}/05a_sales_page_config.js`. This inserts `PRODUCT_COLORS`, `OFFER_SETTINGS`, and `CONFIG` as a single block.

5. Do **not** modify anything outside those markers. `THEMES`, `CURRENCY_RESOLVER`, and the rendering JavaScript that follows `// CONFIG END` must remain intact.

6. Save the result to `{RUN_DIR}/sales_page.html`.

**Validation — verify before saving:**
- `<script>` appears exactly **2 times** in the file (config block + rendering block)
- `const CONFIG` appears exactly **1 time** (the comment in the HTML `<!-- ... -->` does not count)
- `const PRODUCT_COLORS` appears exactly **1 time**
- `const OFFER_SETTINGS` appears exactly **1 time**
- `const THEMES` appears exactly **1 time**
- `BRAND_NAME` in the file matches the selected brand name

7. Tell the user: **"Your sales page is ready! Open `{RUN_DIR}/sales_page.html` in a browser to preview."**

## OUTPUT

| File | Content |
|------|---------|
| `{RUN_DIR}/05a_sales_page_config.js` | `PRODUCT_COLORS` + `OFFER_SETTINGS` + `CONFIG` JavaScript objects |
| `{RUN_DIR}/sales_page.html` | Final assembled HTML (single config `<script>` block + rendering `<script>` block) |

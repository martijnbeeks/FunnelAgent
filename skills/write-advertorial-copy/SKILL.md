---
name: write-advertorial-copy
description: Writes the complete advertorial as a CONFIG object for the HTML template (Framework A — Customer POV).
---

# Write Advertorial Copy Skill

You execute Step 4.1 of the FunnelAgent pipeline: writing the complete advertorial copy and outputting it as a JavaScript CONFIG object for the advertorial_POV.html template.

## PREREQUISITES

- `output/01_market_research.md` — Raw research data
- `output/02b_synthesis_phase2.md` — Complete strategic intelligence brief
- `output/03a_brand_names.md` — Selected brand name
- `output/03c_color_vars.md` — CSS color variables
- User has confirmed target language and approved the strategic brief

## STEP 1: LOAD THE FULL SOP

**MANDATORY FIRST ACTION:** Read the complete Advertorial SOP:
```
skill_content/PROMPT 4_1_ Advertorial Framework A Customer POV.md
```

This file contains the ENTIRE advertorial framework — the Strategic Brief extraction steps, all section structures, the psychology rules, the writing rules, the CONFIG output format, the HTML element reference, and the output checklist. You MUST read it in full and follow it exactly.

## STEP 2: LOAD THE HTML TEMPLATE

Read the HTML template to understand the CONFIG structure it expects:
```
templates/advertorial_POV.html
```

Pay attention to the CONFIG object structure in the `<script>` tag and all the HTML element classes available (quote-box, mechanism-box, validation-box, failed-solution, timeline-item, etc.).

## STEP 3: LOAD ALL INPUT DATA

Read all source documents:
```
output/01_market_research.md
output/02b_synthesis_phase2.md
output/03a_brand_names.md
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

## STEP 5: EXTRACT FROM STRATEGIC BRIEF (SOP Step 1)

Follow the SOP's extraction step exactly. Extract all elements the SOP specifies:
- The Forced Angle (from brief)
- The One Avatar (from brief)
- Sophistication Approach
- Avatar Beliefs
- Key Proof Points

Use the selected brand name from `output/03a_brand_names.md` as the product/brand name throughout.
Apply the validated color variables from Step 4 to the CONFIG THEME section.

Do NOT proceed to writing until you've confirmed all elements are extracted.

## STEP 6: WRITE THE ADVERTORIAL (SOP Steps 2-3)

Follow the SOP's advertorial structure exactly. The SOP defines:
- The section structure (Hook, Education, Discredit, Mechanism, Product, FAQ, Transformation, Offer, Two Paths, Comments)
- What each section must do
- Which brief sections to pull from
- The psychology rules (Rule of One, hide mechanism in hook, product name saturation)
- The tone (Framework A: Customer Story / UGC POV)

Write in the user's specified target language, adapting cultural nuances and idiomatic expressions.

## STEP 7: FORMAT AS CONFIG (SOP Steps 4-5)

Before writing the CONFIG, check if `{RUN_DIR}/cdn_urls.json` exists. If it does, read it and use the CDN URL for `product_image.png` as the value for `CONFIG.PRODUCT_IMAGE` (instead of leaving it empty or using a local path).

Follow the SOP's CONFIG output format exactly. The SOP specifies:
- The exact CONFIG JavaScript structure
- Section mapping
- HTML elements to use in body strings
- The critical formatting rule (no line breaks inside body strings)
- Theme selection criteria
- Review and sidebar review formats

## STEP 8: VERIFY AGAINST CHECKLIST

Run through the SOP's OUTPUT CHECKLIST before saving. Every checkbox must pass.

## STEP 9: SAVE AND ASSEMBLE

1. Save the CONFIG to `output/04a_advertorial_config.js`
2. Read `templates/advertorial_POV.html`, replace the example CONFIG (everything between `const CONFIG = {` and `};`) with the generated CONFIG, and save as `output/advertorial.html`
3. Tell the user: **"Your advertorial is ready! Open `output/advertorial.html` in a browser to preview."**

## OUTPUT

| File | Content |
|------|---------|
| `output/04a_advertorial_config.js` | CONFIG JavaScript object |
| `output/advertorial.html` | Final assembled HTML |

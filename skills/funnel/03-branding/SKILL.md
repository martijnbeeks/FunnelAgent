---
name: 03-branding
description: "Generates brand name options, logo prompt + color palette, and product image prompt (Steps 3.1–3.3)."
---

# Branding Skill

You execute Step 3 of the FunnelAgent pipeline: creating the brand identity — brand name, logo, color palette, and product image.

## PREREQUISITES

- `output/00_product_info.md` — Product information
- `output/02b_synthesis_phase2.md` — Complete strategic intelligence brief
- `GEMINI_API_KEY` must be set in `.env` or environment
- Python 3.8+ with `google-genai` and `python-dotenv` packages installed

## STEP 1: BRAND NAME GENERATION (Step 3.1)

### Brand Name SOP

# BRAND NAME GENERATION SOP v1.0

## Purpose

Generate 10 compelling brand name options for a direct-response health/beauty product based on market research and strategic brief data.

## Input Required

- Product information (`output/00_product_info.md`)
- Market research (`output/01_market_research.md`)
- Strategic brief (`output/02b_synthesis_phase2.md`)

## Instructions

Generate 10 brand names for the product based on the research docs. The names should:

1. **Coin or modify words** — hint at the benefit without spelling it out literally (e.g., "Reliva" suggests relief, "Rem" suggests REM sleep)
2. **Combine a polished coined word with a functional anchor** — Flow, Max, Labs, Pro, Rem, Vive
3. **Feel ownable and trademarkable** — not generic descriptors
4. **Be 2–3 syllables per part**, easy to say
5. **Strike a balance** — more direct than luxury Latin names, but more refined than "StrengthFuel"
6. **4 of the 10 should be one single fluent word** (e.g., "Reliva", "Fungia")

## Output Format

For each name:

```
### [Number]. [Brand Name]™

**Wordplay/hint:** [Explain the subtle wordplay or benefit hint]
**Syllables:** [Count]
**Category:** [Single word / Compound]
**Why it works:** [1 sentence on positioning fit]
```

After all 10, provide:

```
## RECOMMENDED WINNER

**[Best Name]™**

**Rationale:** [Why this name best fits the product, market, and angle from the strategic brief]
```

## Rules

- Names must be appropriate for the target demographic identified in the research
- Names must align with the PRIMARY angle from the strategic brief
- Avoid names that are already well-known supplement brands
- Each name must work with a ™ symbol
- Consider the target language/market when evaluating pronunciation


---

### 1b. Load Input Data

Read:
```
output/00_product_info.md
output/02b_synthesis_phase2.md
```

### 1c. Execute Brand Name Generation

Follow the SOP exactly. Generate 10 brand name options with wordplay explanations, then recommend a winner.

### 1d. Save Output

Save the complete brand name options to `output/03a_brand_names.md`.

### 1e. Present to User

Show all 10 options with the recommended winner. Ask:
> **"Which brand name do you want to proceed with? Or suggest your own."**

Wait for user selection before proceeding.

---

## STEP 2: LOGO CREATION + COLOR PICKER (Step 3.2)

### Logo Creation + Color Picker SOP

First, analyze the provided product packaging image and identify the exact dominant colors, accent tones, and visual mood. Then, based on that analysis, **create a prompt to feed to Gemini API** for an ultra-professional, minimalist vector logo for the brand: **\[INSERT YOUR BRAND NAME HERE™\]**. The generated prompt must instruct Gemini API to color-match the logo exclusively to the packaging palette identified in the analysis. The prompt must also include the following instructions: Clean, balanced, and modern design inspired by premium health & beauty brands like Lumēvia™, Fungia™, or Sciatico™. A small, elegant icon or symbol to the left of the text representing calmness, breathing, or airflow — such as a soft wave, leaf, or gentle swirl — colored to match the packaging. A refined serif or semi-serif font (not sans-serif) conveying trust, calmness, and sophistication. A ™ symbol at the end of the brand name. The logo must fill the entire 432×98 px frame horizontally with no excess transparent padding. 100% transparent background — no white, grey, shadow, or gradient. Flat, high-quality vector graphic appearance, cropped exactly to the logo's edges, rendered as if for Shopify header or product packaging. Output dimensions exactly 432×98 pixels. 

When done, continue with the following assignment: 

**Look at the product image. Extract the dominant brand color from the packaging/label (ignore white, black, small highlighted color and background colors). Then give me updated values for these four theme variables:** 

1\. **`primary`** — The dominant brand color as-is (hex) 

2\. **`primaryDark`** — A darker shade of that color, suitable for headers and buttons (roughly 25-30% darker) 

3\. **`primaryLight`** — A very light tint of that color, suitable for section backgrounds (roughly 90-95% lightness) 

4\. **`accent`** — A color that actually appears on the product packaging (cap, label, icon, text, or trim — not the background/white). Must pass WCAG AA contrast with white text. If the product only has one non-white/non-black color, use that color or its darker shade. **Never use a color not found on the product.**

**Output format — just this, nothing else:** 

primary: "\#\_\_\_\_\_\_", 

primaryDark: "\#\_\_\_\_\_\_", 

primaryLight: "\#\_\_\_\_\_\_", 

accent: "\#\_\_\_\_\_\_", 

**Rules:** 

● Base `primary`, `primaryDark`, and `primaryLight` on the SAME hue from the product packaging 

● `primaryDark` must pass WCAG AA contrast on white text  
● `primaryLight` must be subtle enough to use as a full-section background without overwhelming body text 

● `accent` is for CTA buttons — it MUST be dark enough for white text to be clearly readable. Never use a light or medium color here.
● `accent` MUST be a color that actually exists on the product packaging — never invent a color not on the product. If the dominant color is too light, use a darker shade of that same color.
● If the packaging has multiple colors, choose the one that carries the most brand identity (usually the largest non-white, non-black color on the label)

---

### 2b. Execute Logo Prompt Generation

Follow the SOP exactly. The SOP requires:
1. Analyzing the product packaging image to identify dominant colors
2. Creating a prompt for an ultra-professional minimalist vector logo
3. Extracting the dominant brand color for CSS theme variables

Insert the selected brand name from Step 1 into `[INSERT YOUR BRAND NAME HERE™]`.

### 2c. Save Logo Prompt

Save the generated logo prompt to `output/03b_logo_prompt.md`.

### 2d. Generate Logo via Gemini API

Run the image generation script:
```bash
python scripts/generate_image.py \
  --prompt-file output/03b_logo_prompt.md \
  --output output/logo.png \
  --aspect-ratio 1:1
```

### 2e. Upload Logo to CDN

If R2 CDN credentials are configured (check for `R2_ACCESS_KEY_ID` in environment), upload the logo:

```bash
python scripts/upload_to_cdn.py \
  --file output/logo.png \
  --key {run_name}/logo.png
```

Capture the CDN URL printed to stdout. If the upload fails or R2 credentials are not set, log a warning and continue — CDN is optional.

### 2f. Extract and Save Color Variables

From the SOP's color picker output, save the CSS color variables to `output/03c_color_vars.md` in this format:

```
--theme-primary: #XXXXXX;
--theme-primary-dark: #XXXXXX;
--theme-primary-light: #XXXXXX;
--theme-accent: #XXXXXX;
```

---

## STEP 3: PRODUCT IMAGE (Step 3.3)

### Product Image SOP

﻿I've uploaded two images:  
1\. A product image  
2\. My brand name/logo  
Please:  
1\. REPLACE the existing brand name/logo on the product with my uploaded brand name  
2\. Keep the exact same product shape, size, and style  
3\. Integrate my brand name naturally — it should look like the original product photography, not edited  
4\. Remove any objects, props, powder, ingredients, accessories, or decorative elements that overlap, obstruct, or sit in front of the product. The full product must be completely visible and unobstructed from every edge — nothing in front of, leaning against, or partially covering it.  
5\. Place the rebranded product in a premium studio setting:  
   \* White marble surface with subtle grey veining  
   \* Clean gradient or white background behind  
   \* Professional studio lighting  
   \* Soft natural shadow beneath product  
   \* Slight angle (15-20°) for dimension  
6\. Make it look like a high-end e-commerce hero shot  
CRITICAL:  
\* The product must stand completely alone — no props, scattered ingredients, or objects touching or overlapping it  
\* My brand name must be sharp, clear, and readable  
\* Label should look professionally printed, not photoshopped on  
\* No AI artifacts, warped text, or distortions  
\* Final image should look like original product photography from a premium brand  
Format: 1:1 (square) Quality: Photorealistic, commercial product photography standard

---

### 3b. Execute Product Image Prompt Generation

Follow the SOP exactly. Generate a prompt for a professional product image.

### 3c. Save Product Image Prompt

Save the generated prompt to `output/03d_product_image_prompt.md`.

### 3d. Generate Product Image via Gemini API

Run the image generation script:
```bash
python scripts/generate_image.py \
  --prompt-file output/03d_product_image_prompt.md \
  --output output/product_image.png \
  --aspect-ratio 1:1
```

### 3e. Upload Product Image to CDN

If R2 CDN credentials are configured, upload the product image:

```bash
python scripts/upload_to_cdn.py \
  --file output/product_image.png \
  --key {run_name}/product_image.png
```

Capture the CDN URL printed to stdout. If the upload fails or R2 credentials are not set, log a warning and continue.

---

## STEP 4: SAVE CDN URL MANIFEST

If either the logo or product image was successfully uploaded to CDN, write the CDN URLs to `output/cdn_urls.json`:

```json
{
  "logo.png": "https://cdn.example.com/run-name/logo.png",
  "product_image.png": "https://cdn.example.com/run-name/product_image.png"
}
```

Only include entries for images that were actually uploaded. If no uploads succeeded (or R2 credentials were not set), do NOT create this file.

---

## OUTPUT

| File | Content |
|------|---------|
| `output/03a_brand_names.md` | 10 brand name options + winner |
| `output/03b_logo_prompt.md` | Logo generation prompt |
| `output/03c_color_vars.md` | CSS color variables |
| `output/03d_product_image_prompt.md` | Product image prompt |
| `output/logo.png` | Generated logo image |
| `output/product_image.png` | Generated product image |
| `output/cdn_urls.json` | CDN URL manifest (if R2 configured) |

---
name: branding
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

### 1a. Load the Brand Name SOP

**MANDATORY FIRST ACTION:** Read the complete Brand Name Generation SOP:
```
skill_content/PROMPT 3_0_ Brand Name Generation.md
```

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

### 2a. Load the Logo SOP

Read the complete Logo Creation + Color Picker SOP:
```
skill_content/PROMPT 3_1_ Logo Creation + Color Picker.md
```

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

### 3a. Load the Product Image SOP

Read the complete Product Image Prompt SOP:
```
skill_content/PROMPT 3_2_ Product Image Prompt.md
```

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

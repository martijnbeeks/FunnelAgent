---
name: advertorial-images
description: "Generates image prompts for the advertorial and runs iterative hero image QA (Steps 4.3–4.4)."
---

# Advertorial Images Skill

You execute Steps 4.3 and 4.4 of the FunnelAgent pipeline: generating image prompts for the advertorial and performing hero image QA.

## PREREQUISITES

- `{RUN_DIR}/04a_advertorial_config.js` — The advertorial CONFIG
- `{RUN_DIR}/02b_synthesis_phase2.md` — Strategic intelligence brief
- **Product image** — The product photo (e.g., `{RUN_DIR}/product_image.png` or user-provided path). Required for Section 4 (Product Infographic) and Section 7 (Product Shot).
- `GEMINI_API_KEY` must be set in `.env` or environment
- Python 3.8+ with `google-genai`, `python-dotenv`, and `Pillow` packages installed

## STEP 1: IMAGE PROMPT GENERATION (Step 4.3)

### 1a. Load the Image Generation SOP

**MANDATORY FIRST ACTION:** Read the complete Image Generation SOP:
```
skill_content/PROMPT 4_3_ Image Generation Advertorial.md
```

This file contains the ENTIRE image prompt framework — research extraction, hero image types (6 Recognition, 3 Transformation, 1 Aspiration), wound concepts, diagram types (UMP, Comparison, UMS), product infographic, transformation images, and the exact output format. You MUST read it in full and follow it exactly.

### 1b. Load Input Data

Read:
```
{RUN_DIR}/04a_advertorial_config.js
{RUN_DIR}/02b_synthesis_phase2.md
```

### 1c. Execute Research Extraction (SOP Part 2)

Before generating any image prompts, extract from the Strategic Intelligence Brief:
1. **Demographics** — age, gender, ethnicity, appearance, clothing style
2. **Cultural context** — home settings, outdoor settings, family markers
3. **Emotional triggers** — primary fear, secondary fears, primary desire, identity prison, identity restoration
4. **Mechanism visuals** — UMP visual translation, UMS visual translation, key ingredients

These drive ALL image prompt decisions.

### 1d. Execute Image Prompt Generation (SOP Parts 4–12)

Follow the SOP exactly. The SOP produces prompts for:

| Image | SOP Part | Type | Format |
|-------|----------|------|--------|
| **Hero V1** — Recognition | Part 4 | Select from 1A–1F based on PRIMARY FEAR | 16:9 |
| **Hero V2** — Transformation | Part 4 | Select from 2A–2C based on UMP | 16:9 |
| **Hero V3** — Aspiration | Part 4 | 3A: Living the Desire | 16:9 |
| **Section 0** — Wound | Part 5 | Select from W1–W5 based on PRIMARY DESIRE | 16:9 |
| **Section 1** — UMP Diagram | Part 6 | Select from D1–D3 based on UMP type | 16:9 |
| **Section 2** — Comparison Diagram | Part 7 | Select from C1–C2 | 16:9 |
| **Section 3** — UMS Diagram | Part 8 | Select from M1–M3 based on UMS type | 16:9 |
| **Section 4** — Product Infographic | Part 9 | P1 (requires product image) | 16:9 |
| **Section 5** — FAQ | Part 10 | SKIP unless needed (F1 Expert Portrait) | 16:9 |
| **Section 6** — Transformation | Part 11 | Select from T1–T3 | 16:9 |
| **Section 7** — Product Shot | Part 12 | O1 (requires product image) | **1:1** |

**Total: 8-10 images** (3 hero options + 5-7 section images)

### 1e. Save Image Prompts

Save all generated image prompts to `{RUN_DIR}/04c_image_prompts_advertorial.md` using the output format from SOP Part 13.

### 1f. Generate Images via Gemini API

**Generate all images in parallel.** For each image prompt:
1. Save the prompt text to a temporary file (e.g., `{RUN_DIR}/advertorial_images/_prompt_<image_name>.txt`)
2. Determine if this section requires the product image (see table below)
3. Prepare the corresponding `generate_image.py` command

**Product image requirement per section:**

| Image | Product? | Use `--reference-image`? | Aspect Ratio |
|-------|----------|--------------------------|--------------|
| Hero V1 (Recognition) | NO | No | 16:9 |
| Hero V2 (Transformation) | NO | No | 16:9 |
| Hero V3 (Aspiration) | NO | No | 16:9 |
| Section 0: Wound | NO | No | 16:9 |
| Section 1: UMP Diagram | NO | No | 16:9 |
| Section 2: Comparison Diagram | NO | No | 16:9 |
| Section 3: UMS Diagram | NO | No | 16:9 |
| Section 4: Product Infographic | **YES** | **Yes** | 16:9 |
| Section 5: FAQ/Expert | NO | No | 16:9 |
| Section 6: Transformation | NO | No | 16:9 |
| Section 7: Product Shot | **YES** | **Yes** | **1:1** |

Then launch **all** generation commands simultaneously using parallel Bash tool calls (one per image):

**For sections WITHOUT product:**
```bash
python scripts/generate_image.py \
  --prompt-file {RUN_DIR}/advertorial_images/_prompt_<image_name>.txt \
  --output {RUN_DIR}/advertorial_images/<image_name>.png \
  --aspect-ratio <ratio>
```

**For sections WITH product (S4, S7) — include `--reference-image`:**
```bash
python scripts/generate_image.py \
  --prompt-file {RUN_DIR}/advertorial_images/_prompt_<image_name>.txt \
  --output {RUN_DIR}/advertorial_images/<image_name>.png \
  --aspect-ratio <ratio> \
  --reference-image {RUN_DIR}/product_image.png
```

The `--reference-image` flag sends the product photo to Gemini's multimodal API alongside the text prompt, so the model can composite the actual product into the scene. **Never describe the product's appearance in the text prompt** — only the Gemini API sees the uploaded photo.

**IMPORTANT:** Do NOT generate images one at a time. Issue all Bash calls in a single response so they run concurrently. Wait for all to complete, then verify each output file exists.

### 1g. Upload All Advertorial Images to CDN

If R2 CDN credentials are configured (check for `R2_ACCESS_KEY_ID` in environment), upload all generated images:

```bash
python scripts/upload_to_cdn.py \
  --directory {RUN_DIR}/advertorial_images/ \
  --prefix {run_name}/advertorial_images/
```

Capture the JSON output mapping filenames to CDN URLs. Merge these into `{RUN_DIR}/cdn_urls.json` (create if it doesn't exist, merge if it does). If the upload fails or R2 credentials are not set, log a warning and skip CDN URL injection.

### 1h. Update Advertorial CONFIG with CDN URLs

If CDN URLs were captured in step 1g:
1. Read `{RUN_DIR}/04a_advertorial_config.js`
2. Read `{RUN_DIR}/cdn_urls.json`
3. Replace `HERO_IMAGE` value with the CDN URL for the hero image
4. Replace each `SECTIONS[n].image` value with the corresponding section image CDN URL
5. If `PRODUCT_IMAGE` is present in the manifest, use its CDN URL
6. Write updated CONFIG back to `{RUN_DIR}/04a_advertorial_config.js`

### 1i. Reassemble Advertorial HTML

Read `templates/advertorial_POV.html`, replace the example CONFIG block with the updated CONFIG from step 1h, and save as `{RUN_DIR}/advertorial.html`.

---

## STEP 2: HERO IMAGE QA (Step 4.4)

**NOTE:** If hero QA triggers regeneration, the regenerated hero image must also be uploaded to CDN (re-run step 1g for just that file using `--file`), and the CONFIG/HTML must be updated again (re-run steps 1h-1i).

### 2a. Load the Hero Image QA SOP

Read the complete Hero Image Improver SOP:
```
skill_content/PROMPT 4_4_ Hero Image Improver.md
```

### 2b. Execute Hero Image QA

Follow the SOP exactly:
1. Evaluate the generated hero image against the SOP's quality criteria
2. Score on: Relevance, Emotional Impact, Realism, Brand Fit, Composition
3. If score is below threshold, generate a revised prompt and re-generate
4. Iterate until the image passes QA or the user approves

### 2c. Save QA Results

Save the hero image review to `{RUN_DIR}/04d_hero_review.md`, including:
- Quality scores for each criterion
- Pass/fail verdict
- Revision prompts if applicable
- Final approved image path

---

## OUTPUT

| File | Content |
|------|---------|
| `{RUN_DIR}/04c_image_prompts_advertorial.md` | All image prompts (3 heroes + section images) |
| `{RUN_DIR}/04d_hero_review.md` | Hero image QA results |
| `{RUN_DIR}/advertorial_images/*.png` | Generated images (8-10 total) |

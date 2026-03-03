---
name: advertorial-images
description: "Generates image prompts for the advertorial and runs iterative hero image QA (Steps 4.3–4.4)."
---

# Advertorial Images Skill

You execute Steps 4.3 and 4.4 of the FunnelAgent pipeline: generating image prompts for the advertorial and performing hero image QA.

## PREREQUISITES

- `output/04a_advertorial_config.js` — The advertorial CONFIG
- `output/02b_synthesis_phase2.md` — Strategic intelligence brief
- `output/advertorial.html` — The assembled advertorial
- **Product image** — The product photo (e.g., `{RUN_DIR}/product_image.png` or user-provided path). Required for sections that need the product overlay.
- `GEMINI_API_KEY` must be set in `.env` or environment
- Python 3.8+ with `google-genai`, `python-dotenv`, and `Pillow` packages installed

## STEP 1: IMAGE PROMPT GENERATION (Step 4.3)

### 1a. Load the Image Generation SOP

**MANDATORY FIRST ACTION:** Read the complete Image Generation SOP:
```
skill_content/PROMPT 4_3_ Image Generation Advertorial.md
```

This file contains the ENTIRE image prompt framework — avatar identification analysis, image style requirements, section-by-section image specifications, and the exact prompt format for each image. You MUST read it in full and follow it exactly.

### 1b. Load Input Data

Read:
```
output/04a_advertorial_config.js
output/02b_synthesis_phase2.md
```

### 1c. Execute Image Prompt Generation

Follow the SOP exactly. Generate image prompts for each section of the advertorial as specified by the SOP. Each prompt should match the avatar demographics, product context, and emotional tone from the strategic brief.

### 1d. Save Image Prompts

Save all generated image prompts to `output/04c_image_prompts_advertorial.md`.

### 1e. Generate Images via Gemini API

**Generate all images in parallel.** For each image prompt:
1. Save the prompt text to a temporary file (e.g., `output/advertorial_images/_prompt_<image_name>.txt`)
2. Determine if this section requires the product image (see table below)
3. Prepare the corresponding `generate_image.py` command

**Product image requirement per section (from SOP):**

| Section | Product? | Use `--reference-image`? |
|---------|----------|--------------------------|
| 1. Hook | NO | No |
| 2. Education | NO (diagram) | No |
| 3. Discredit | NO | No |
| 4. Mechanism | NO | No |
| 5. Split Transformation | NO | No |
| 6. FAQ | **YES** — overlay | **Yes** |
| 7. Your Transformation | **YES** — overlay | **Yes** |
| 8. The Offer | **YES** — overlay | **Yes** |
| 9. Two Paths | **YES** — overlay | **Yes** |
| Profile photos | NO | No |

Then launch **all** generation commands simultaneously using parallel Bash tool calls (one per image):

**For sections WITHOUT product (1-5, profiles):**
```bash
python scripts/generate_image.py \
  --prompt-file output/advertorial_images/_prompt_<image_name>.txt \
  --output output/advertorial_images/<image_name>.png \
  --aspect-ratio <ratio_from_sop>
```

**For sections WITH product (6-9) — include `--reference-image`:**
```bash
python scripts/generate_image.py \
  --prompt-file output/advertorial_images/_prompt_<image_name>.txt \
  --output output/advertorial_images/<image_name>.png \
  --aspect-ratio <ratio_from_sop> \
  --reference-image {RUN_DIR}/product_image.png
```

The `--reference-image` flag sends the product photo to Gemini's multimodal API alongside the text prompt, so the model can composite the actual product into the scene. **Never describe the product's appearance in the text prompt** — only the Gemini API sees the uploaded photo.

**IMPORTANT:** Do NOT generate images one at a time. Issue all Bash calls in a single response so they run concurrently. Wait for all to complete, then verify each output file exists.

### 1f. Upload All Advertorial Images to CDN

If R2 CDN credentials are configured (check for `R2_ACCESS_KEY_ID` in environment), upload all generated images:

```bash
python scripts/upload_to_cdn.py \
  --directory output/advertorial_images/ \
  --prefix {run_name}/advertorial_images/
```

Capture the JSON output mapping filenames to CDN URLs. Merge these into `{RUN_DIR}/cdn_urls.json` (create if it doesn't exist, merge if it does). If the upload fails or R2 credentials are not set, log a warning and skip CDN URL injection.

### 1g. Update Advertorial CONFIG with CDN URLs

If CDN URLs were captured in step 1f:
1. Read `{RUN_DIR}/04a_advertorial_config.js`
2. Read `{RUN_DIR}/cdn_urls.json`
3. Replace `HERO_IMAGE` value with the CDN URL for the hero image
4. Replace each `SECTIONS[n].image` value with the corresponding section image CDN URL
5. If `PRODUCT_IMAGE` is present in the manifest, use its CDN URL
6. Write updated CONFIG back to `{RUN_DIR}/04a_advertorial_config.js`

### 1h. Reassemble Advertorial HTML

Read `templates/advertorial_POV.html`, replace the example CONFIG block with the updated CONFIG from step 1g, and save as `{RUN_DIR}/advertorial.html`.

---

## STEP 2: HERO IMAGE QA (Step 4.4)

**NOTE:** If hero QA triggers regeneration, the regenerated hero image must also be uploaded to CDN (re-run step 1f for just that file using `--file`), and the CONFIG/HTML must be updated again (re-run steps 1g-1h).

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

Save the hero image review to `output/04d_hero_review.md`, including:
- Quality scores for each criterion
- Pass/fail verdict
- Revision prompts if applicable
- Final approved image path

---

## OUTPUT

| File | Content |
|------|---------|
| `output/04c_image_prompts_advertorial.md` | All image prompts |
| `output/04d_hero_review.md` | Hero image QA results |
| `output/advertorial_images/*.png` | Generated images |

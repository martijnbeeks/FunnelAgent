---
name: sales-page-images
description: "Generates image prompts for the sales page and runs iterative hero image QA (Steps 5.2–5.3)."
---

# Sales Page Images Skill

You execute Steps 5.2 and 5.3 of the FunnelAgent pipeline: generating image prompts for the sales page and performing hero image QA.

## PREREQUISITES

- `output/05a_sales_page_config.js` — The sales page CONFIG
- `output/02b_synthesis_phase2.md` — Strategic intelligence brief
- **Product image** — The product photo (e.g., `{RUN_DIR}/product_image.png` or user-provided path). Required for Hero A, Hero B, Hero C, mechanism diagram, alternatives diagram, and review product-in-use images.
- `GEMINI_API_KEY` must be set in `.env` or environment
- Python 3.8+ with `google-genai`, `python-dotenv`, and `Pillow` packages installed

## STEP 1: IMAGE PROMPT GENERATION (Step 5.2)

### 1a. Load the Sales Page Image SOP

**MANDATORY FIRST ACTION:** Read the complete Sales Page Image SOP:
```
skill_content/PROMPT 5_2_ Sales Page Image SOP.md
```

This file contains the ENTIRE sales page image framework — hero image requirements, section-by-section image specs, review card image distribution (database + AI + Gemini API), mechanism diagram specs, before/after comparison specs, and the prompt format. You MUST read it in full and follow it exactly.

### 1b. Load Input Data

Read:
```
output/05a_sales_page_config.js
output/02b_synthesis_phase2.md
```

### 1c. Execute Image Prompt Generation

Follow the SOP exactly. The sales page requires **11 images** (generate 2 variations of every image and pick the best):

- **3 Hero images** (for A/B testing):
  - Hero A: The First Morning (product on counter)
  - Hero B: Split Before/After (product as small overlay)
  - Hero C: Person + Guarantee Badge (product held in hand)
- Agitation image (pain recognition moment)
- Doctor portrait (authority figure)
- Mechanism diagram (UMP→UMS, 16:9)
- Alternatives diagram (comparison/discredit, 16:9)
- Two Paths: WITHOUT image (pain state)
- Two Paths: WITH image (transformation)
- 2 Review AI images (1 product-in-use + 1 outcome)

Generate prompts for each AI-generated image as specified by the SOP.

### 1d. Save Image Prompts

Save all generated image prompts to `output/05b_image_prompts_sales_page.md`.

### 1e. Generate Images via Gemini API

**Generate all images in parallel.** For each image prompt:
1. Save the prompt text to a temporary file (e.g., `output/sales_page_images/_prompt_<image_name>.txt`)
2. Determine if this image requires the product reference image (see table below)
3. Prepare the corresponding `generate_image.py` command

**Product image requirement per image (from SOP):**

| Image | Product? | Use `--reference-image`? |
|-------|----------|--------------------------|
| Hero A: First Morning | **YES** (natural placement) | **Yes** |
| Hero B: Split Before/After | **YES** (overlay) | **Yes** |
| Hero C: Person + Guarantee Badge | **YES** (in hand, 25-35%) | **Yes** |
| Agitation | NO | No |
| Doctor | NO | No |
| Mechanism diagram | **YES** (name/icon) | **Yes** |
| Alternatives diagram | **YES** (name) | **Yes** |
| Two Paths — Without | NO | No |
| Two Paths — With | OPTIONAL | Only if product included |
| Review: Product In Use | **YES** (30-50%) | **Yes** |
| Review: Outcome | NO | No |

Then launch **all** generation commands simultaneously using parallel Bash tool calls (one per image):

**For images WITHOUT product (Agitation, Doctor, Without, Review Outcome):**
```bash
python scripts/generate_image.py \
  --prompt-file output/sales_page_images/_prompt_<image_name>.txt \
  --output output/sales_page_images/<image_name>.png \
  --aspect-ratio <ratio_from_sop>
```

**For images WITH product (Hero A, Hero B, Hero C, Mechanism, Alternatives, Review Product-In-Use) — include `--reference-image`:**
```bash
python scripts/generate_image.py \
  --prompt-file output/sales_page_images/_prompt_<image_name>.txt \
  --output output/sales_page_images/<image_name>.png \
  --aspect-ratio <ratio_from_sop> \
  --reference-image {RUN_DIR}/product_image.png
```

The `--reference-image` flag sends the product photo to Gemini's multimodal API alongside the text prompt, so the model can render the actual product in the scene. **Never describe the product's appearance in the text prompt** — only the Gemini API sees the uploaded photo.

**IMPORTANT:** Do NOT generate images one at a time. Issue all Bash calls in a single response so they run concurrently. Wait for all to complete, then verify each output file exists.

### 1f. Upload All Sales Page Images to CDN

If R2 CDN credentials are configured (check for `R2_ACCESS_KEY_ID` in environment), upload all generated images:

```bash
python scripts/upload_to_cdn.py \
  --directory output/sales_page_images/ \
  --prefix {run_name}/sales_page_images/
```

Capture the JSON output mapping filenames to CDN URLs. Merge these into `{RUN_DIR}/cdn_urls.json` (create if it doesn't exist, merge if it does). If the upload fails or R2 credentials are not set, log a warning and skip CDN URL injection.

### 1g. Update Sales Page CONFIG with CDN URLs

If CDN URLs were captured in step 1f:
1. Read `{RUN_DIR}/05a_sales_page_config.js`
2. Read `{RUN_DIR}/cdn_urls.json`
3. Replace image values with their CDN URLs:
   - `HERO.IMAGE` — hero image A
   - `HERO.IMAGE_B` — hero image B (split before/after)
   - `HERO.IMAGE_C` — hero image C (person + guarantee badge)
   - `AGITATION.IMAGE` — agitation section image
   - `DOCTOR.IMAGE` — doctor portrait
   - `MECHANISM.DIAGRAM_IMAGE` — mechanism diagram
   - `ALTERNATIVES.DIAGRAM_IMAGE` — alternatives comparison diagram
   - `MISS.WITHOUT_IMAGE` — "without" comparison image
   - `MISS.WITH_IMAGE` — "with" comparison image
   - Testimonial `IMAGE` fields where the value is a generated filename (not `"gemini"`, `"database"`, or empty)
4. If `PRODUCT_IMAGE` or `product_image.png` is in the manifest, use its CDN URL for product image references
5. Write updated CONFIG back to `{RUN_DIR}/05a_sales_page_config.js`

### 1h. Reassemble Sales Page HTML

Read `templates/sales_page.html`, replace the example CONFIG block with the updated CONFIG from step 1g, and save as `{RUN_DIR}/sales_page.html`.

---

## STEP 2: HERO IMAGE QA (Step 5.3)

**NOTE:** If hero QA triggers regeneration, the regenerated hero image must also be uploaded to CDN (re-run step 1f for just that file using `--file`), and the CONFIG/HTML must be updated again (re-run steps 1g-1h).

### 2a. Load the Hero Image QA SOP

Read the complete Hero Checking Prompt SOP:
```
skill_content/PROMPT 5_3_ Hero Checking Prompt.md
```

### 2b. Execute Hero Image QA

Follow the SOP exactly:
1. Evaluate the generated hero image against the SOP's quality criteria
2. Score on all dimensions specified in the SOP
3. If below threshold, generate a revised prompt and re-generate via Gemini API
4. Iterate until the image passes QA or the user approves

### 2c. Save QA Results

Save the hero image review to `output/05c_sp_hero_review.md`, including:
- Quality scores for each criterion
- Pass/fail verdict
- Revision prompts if applicable
- Final approved image path

---

## OUTPUT

| File | Content |
|------|---------|
| `output/05b_image_prompts_sales_page.md` | All image prompts |
| `output/05c_sp_hero_review.md` | Hero image QA results |
| `output/sales_page_images/*.png` | Generated images |

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

### 1c. Native Ad Image Selection for Review Slots

The 4 review slots that previously required a funnelbuilder (R1: `REVIEWS_A[0]`, R2: `REVIEWS_A[1]`, R5: `REVIEWS_B[1]`, R6: `REVIEWS_B[2]`) are filled from the native ad image library — realistic selfie photos matched to the target avatar.

**Read the native ad library:**
```
20 native ads/descriptions.json
```

**Determine gender targeting** from the product info and synthesis brief:
- Gender-specific product (e.g., men's prostate, women's hormones): use all 4 images from that gender
- Unisex product: use 2 images per gender

**Select 4 images using these criteria (in priority order):**
1. **Gender match** — hard filter if product is gender-specific
2. **Age proximity** — closest to the target sweet spot age from the synthesis brief
3. **Setting variety** — prefer different backgrounds across all 4 (e.g., indoor/outdoor mix)
4. **Ethnicity diversity** — prioritize the dominant target market ethnicity; include 1 realistic minority image for UK/US/AU markets

**No duplicates — each of the 4 files must be different.**

**Copy selected images to the run directory:**
```bash
cp "20 native ads/<selected1>.png" "{RUN_DIR}/sales_page_images/review_native_1.png"
cp "20 native ads/<selected2>.png" "{RUN_DIR}/sales_page_images/review_native_2.png"
cp "20 native ads/<selected3>.png" "{RUN_DIR}/sales_page_images/review_native_3.png"
cp "20 native ads/<selected4>.png" "{RUN_DIR}/sales_page_images/review_native_4.png"
```

**Update the CONFIG** — replace the 4 review slots with the selected filenames:
- `REVIEWS_A[0].IMAGE`: `"review_native_1.png"` (was `""`)
- `REVIEWS_A[1].IMAGE`: `"review_native_2.png"` (was `"gemini"`)
- `REVIEWS_B[1].IMAGE`: `"review_native_3.png"` (was `""`)
- `REVIEWS_B[2].IMAGE`: `"review_native_4.png"` (was `"gemini"`)

These filenames will be resolved to full CDN URLs in step 1h when CDN upload runs.

### 1d. Execute Image Prompt Generation

Follow the SOP exactly. The sales page requires **14 images** total:

**11 sales page section images** (generate 2 variations of every image and pick the best):
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

**3 Bundle product images** (for the pricing section — 1 image each, no variations needed):
- Bundle 1-Month: 1 product unit on transparent background
- Bundle 2-Month: 2 product units arranged side-by-side on transparent background
- Bundle 3-Month: 3 product units arranged in a row on transparent background

Generate prompts for each AI-generated image as specified by the SOP.

### 1e. Save Image Prompts

Save all generated image prompts to `output/05b_image_prompts_sales_page.md`.

### 1f. Generate Images via Gemini API

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
| Bundle: 1-Month Supply | **YES** (1 unit) | **Yes** |
| Bundle: 2-Month Supply | **YES** (2 units) | **Yes** |
| Bundle: 3-Month Supply | **YES** (3 units) | **Yes** |

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

**Bundle product images** (include `--reference-image` — same product photo as section images):
```bash
python scripts/generate_image.py \
  --prompt-file output/sales_page_images/_prompt_bundle_1month.txt \
  --output output/sales_page_images/bundle_1month.png \
  --aspect-ratio 1:1 \
  --reference-image {RUN_DIR}/product_image.png

python scripts/generate_image.py \
  --prompt-file output/sales_page_images/_prompt_bundle_2month.txt \
  --output output/sales_page_images/bundle_2month.png \
  --aspect-ratio 1:1 \
  --reference-image {RUN_DIR}/product_image.png

python scripts/generate_image.py \
  --prompt-file output/sales_page_images/_prompt_bundle_3month.txt \
  --output output/sales_page_images/bundle_3month.png \
  --aspect-ratio 1:1 \
  --reference-image {RUN_DIR}/product_image.png
```

**IMPORTANT:** Do NOT generate images one at a time. Issue all Bash calls in a single response so they run concurrently. Wait for all to complete, then verify each output file exists.

### 1g. Upload All Sales Page Images to CDN

If R2 CDN credentials are configured (check for `R2_ACCESS_KEY_ID` in environment), upload all generated images:

```bash
python scripts/upload_to_cdn.py \
  --directory output/sales_page_images/ \
  --prefix {run_name}/sales_page_images/
```

Capture the JSON output mapping filenames to CDN URLs. Merge these into `{RUN_DIR}/cdn_urls.json` (create if it doesn't exist, merge if it does). If the upload fails or R2 credentials are not set, log a warning and skip CDN URL injection.

### 1h. Update Sales Page CONFIG with CDN URLs

If CDN URLs were captured in step 1f:
1. Read `{RUN_DIR}/05a_sales_page_config.js`
2. Read `{RUN_DIR}/cdn_urls.json`
3. Replace image values with their CDN URLs:
   - **Hero images** — Hero C (Person + Guarantee Badge) is always the recommended default. Assign Hero C's CDN URL to `HERO.IMAGE` (the image shown on the sales page), Hero A's URL to `HERO.IMAGE_B`, and Hero B's URL to `HERO.IMAGE_C` for A/B testing reference.
   - `AGITATION.IMAGE` — agitation section image
   - `DOCTOR.IMAGE` — doctor portrait
   - `MECHANISM.DIAGRAM_IMAGE` — mechanism diagram
   - `ALTERNATIVES.DIAGRAM_IMAGE` — alternatives comparison diagram
   - `MISS.WITHOUT_IMAGE` — "without" comparison image
   - `MISS.WITH_IMAGE` — "with" comparison image
   - Testimonial `IMAGE` fields where the value is a filename (not `"gemini"`, `"database"`, or empty) — this includes both AI-generated review images and native ad images (`review_native_1.png` through `review_native_4.png`)
4. Bundle image CDN URLs are stored for use in step 1h (injected directly into the template's OFFER_SETTINGS — **not** written into the config file):
   - bundle_1month.png CDN URL → template's bundles[0].image
   - bundle_2month.png CDN URL → template's bundles[1].image
   - bundle_3month.png CDN URL → template's bundles[2].image
5. Write updated CONFIG back to `{RUN_DIR}/05a_sales_page_config.js`

### 1i. Reassemble Sales Page HTML

**CRITICAL — Follow this exact procedure:**

The template's first `<script>` block (containing `const OFFER_SETTINGS`) is the **user-controlled zone** for bundle pricing, gift names, and gift images. It must **never be deleted or replaced**. Only the bundle `image` fields are updated with generated CDN URLs.

1. Read `templates/sales_page.html` into memory.
2. **Update bundle image fields in the first `<script>` block** — load `{RUN_DIR}/cdn_urls.json` and look up `bundle_1month.png`, `bundle_2month.png`, `bundle_3month.png` by key, then replace the first 3 occurrences of `image: ""` in order:
   ```python
   import re, json
   with open(f'{RUN_DIR}/cdn_urls.json') as f:
       cdn_urls = json.load(f)
   for key in ['bundle_1month.png', 'bundle_2month.png', 'bundle_3month.png']:
       url = cdn_urls.get(key, '')
       if url:
           html = re.sub(r'image:\s*""', f'image: "{url}"', html, count=1)
   ```
3. In the second `<script>` block, locate the two marker lines:
   - `// CONFIG START — PASTE YOUR CONFIG BELOW THIS LINE`
   - `// CONFIG END — DO NOT EDIT BELOW THIS LINE`
4. Extract only `PRODUCT_COLORS` and `CONFIG` from `{RUN_DIR}/05a_sales_page_config.js` — skip `OFFER_SETTINGS` (it lives in the template). Extract each block separately:
   ```python
   # PRODUCT_COLORS block: from 'const PRODUCT_COLORS' up to 'const OFFER_SETTINGS'
   pc_start = config.find('const PRODUCT_COLORS')
   pc_end = config.find('const OFFER_SETTINGS')
   product_colors_block = config[pc_start:pc_end].strip()
   # CONFIG block: from 'const CONFIG' to end
   cfg_start = config.find('const CONFIG')
   config_block = config[cfg_start:].strip()
   config_to_inject = product_colors_block + "\n\n" + config_block
   ```
5. Replace everything **between** (not including) those markers with `config_to_inject`.
6. Do not modify anything outside those markers.
7. Save the result to `{RUN_DIR}/sales_page.html`.

**Validate before saving:** `const CONFIG` must appear exactly twice (once in an HTML comment, once in JS), `const PRODUCT_COLORS` exactly once, `const OFFER_SETTINGS` exactly once (from the template's first `<script>`), `const THEMES` exactly once.

---

## STEP 2: HERO IMAGE QA (Step 5.3)

**NOTE:** If hero QA triggers regeneration, the regenerated hero image must also be uploaded to CDN (re-run step 1g for just that file using `--file`), and the CONFIG/HTML must be updated again (re-run steps 1h-1i).

### 2a. Load the Hero Image QA SOP

Read the complete Hero Checking Prompt SOP:
```
skill_content/PROMPT 5_3_ Hero Checking Prompt.md
```

### 2b. Execute Hero Image QA

Follow the SOP exactly:
1. Evaluate the generated hero image against the SOP's quality criteria
2. Score on all dimensions specified in the SOP
3. **Hero C specific check — MANDATORY BADGE VALIDATION:** Visually confirm the guarantee badge is present, large (≥20% image width), and clearly readable. If the badge is missing, too small, or unreadable, automatically regenerate with a strengthened prompt before proceeding with other QA steps.
4. If below threshold on any dimension, generate a revised prompt and re-generate via Gemini API
5. Iterate until the image passes QA or the user approves

### 2c. Save QA Results

Save the hero image review to `output/05c_sp_hero_review.md`, including:
- **All three hero images** shown for comparison (file paths to Hero A, Hero B, Hero C)
- Quality scores for each hero on all QA criteria
- Pass/fail verdict for each
- Which hero was selected as best-suited (per Hero Selection Guide) and why
- Revised prompt if QA triggered regeneration
- Path to the revised/final approved image (if different from the original)

---

## OUTPUT

| File | Content |
|------|---------|
| `output/05b_image_prompts_sales_page.md` | All image prompts (11 section + 3 bundle) |
| `output/05c_sp_hero_review.md` | Hero QA results — all 3 heroes + selected winner + revised image (if any) |
| `output/sales_page_images/*.png` | Generated images (section images + bundle_1month.png, bundle_2month.png, bundle_3month.png) |

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

FunnelAgent is a Claude Code plugin (v2.0.0) that orchestrates a 5-step direct-response sales funnel pipeline. Entry point: `/funnel-orchestrator`.

## Setup

```bash
pip install -r scripts/requirements.txt
cp .env.example .env   # then add OPENAI_API_KEY and GEMINI_API_KEY
```

## Architecture

**Orchestrator delegates, never executes.** The orchestrator (`skills/funnel-orchestrator/SKILL.md`) coordinates the pipeline by spawning sub-agents via the Task tool with `subagent_type: "general-purpose"` and `mode: "bypassPermissions"`. It passes `RUN_DIR=output/{product_name}/` to every sub-agent.

**Each SKILL.md is self-contained.** SOPs are embedded directly inside the respective `SKILL.md` file under a `## SOP: ...` section. To update a framework or rubric, edit the skill file directly — no separate `skill_content/` file to keep in sync. The `skill_content/` directory is kept as a historical archive only.

**CONFIG-based HTML assembly.** Advertorial and sales page skills produce JavaScript CONFIG objects (`04a_advertorial_config.js`, `05a_sales_page_config.js`) that get injected into the HTML templates (`templates/advertorial_POV.html`, `templates/sales_page.html`) to produce final HTML output.

## Pipeline Steps

| Step | Skill | External API | Key Output |
|------|-------|-------------|------------|
| 0 | `00-extract-product-info` | WebFetch | `00_product_info.md` |
| 1 | `01-deep-research` | OpenAI (o3/gpt-4o) | `01_market_research.md` |
| 2.1 | `02a-synthesis-phase1` | — | `02a_synthesis_phase1.md` |
| 2.2 | `02b-synthesis-phase2` | — | `02b_synthesis_phase2.md` |
| 3 | `03-branding` | Gemini | `03a-d` files + `logo.png` + `product_image.png` |
| 4.1 | `04a-write-advertorial-copy` | — | `04a_advertorial_config.js` + `advertorial.html` |
| 4.2 | `04b-headline-optimization` | — | `04b_headline_optimized.md` |
| 4.3-4.4 | `04c-advertorial-images` | Gemini | `advertorial_images/*.png` + `04d_hero_review.md` |
| 5.1 | `05a-write-sales-page` | — | `05a_sales_page_config.js` + `sales_page.html` |
| 5.2-5.3 | `05b-sales-page-images` | Gemini | `sales_page_images/*.png` + `05c_sp_hero_review.md` |

## Scripts

```bash
# Deep research (background API call, may take several minutes)
python scripts/deep_research.py --prompt-file <path> --output <path> [--model o3-deep-research]

# Image generation (Nano Banana 2 — gemini-3.1-flash-image-preview)
python scripts/generate_image.py --prompt-file <path> --output <path> [--aspect-ratio 1:1]

# Image generation with product reference (multimodal, same model)
python scripts/generate_image.py --prompt-file <path> --output <path> --reference-image <product-photo> [--aspect-ratio 1:1]

# Use a different model (e.g., Nano Banana Pro)
python scripts/generate_image.py --prompt-file <path> --output <path> [--model gemini-3-pro-image-preview]

# CDN upload (optional, requires R2 credentials in .env)
python scripts/upload_to_cdn.py --file <path> --key <r2-key>
python scripts/upload_to_cdn.py --directory <path> --prefix <r2-prefix>
```

All scripts load API keys from `.env` in the project root. `deep_research.py` uses the OpenAI Deep Research API with background polling, web search, and code interpreter enabled. `upload_to_cdn.py` uses boto3 for S3-compatible R2 uploads.

## Key Conventions

- **Resume capability**: Before each step, the orchestrator checks if output files already exist and offers to skip or redo.
- **User decision gates**: The pipeline pauses for user approval after steps 1, 2.1, 2.2, 3, 4.1-4.2, 4.4, 5.1, and 5.3.
- **Sub-agents read their own SKILL.md first** — the SOP is embedded directly in the file, no external load needed.
- **Only summaries flow back** to the orchestrator — never load full output files into the orchestrator context.
- **All writing supports the user's target language** — language is confirmed during step 2.2 and carried through all downstream skills.
- **Hero image QA is iterative** — steps 4.4 and 5.3 score hero images on 5 dimensions and regenerate if below threshold.

## CDN Image Hosting (Optional)

Images can be automatically uploaded to **Cloudflare R2** so the HTML pages work when hosted anywhere (not just from local disk). CDN is optional — if R2 credentials are not set, everything works as before with local paths.

**R2 environment variables** (add to `.env`):
```
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
R2_BUCKET_NAME=...
R2_PUBLIC_URL=https://your-cdn-domain.com
```

**Upload script** (`scripts/upload_to_cdn.py`):
```bash
# Single file — prints CDN URL to stdout
python scripts/upload_to_cdn.py --file <path> --key <r2-key>

# Directory — prints JSON {filename: cdn_url} to stdout
python scripts/upload_to_cdn.py --directory <path> --prefix <r2-prefix>
```

**CDN URL manifest** (`{RUN_DIR}/cdn_urls.json`):
- Created by the branding skill after uploading logo + product image
- Merged into by advertorial-images and sales-page-images skills after uploading section images
- Format: `{"filename.png": "https://cdn.../path/filename.png"}`
- Read by copy skills (write-advertorial-copy, write-sales-page) to inject CDN URLs into CONFIG objects
- Read by image skills to update CONFIG files post-generation

**Flow:** Branding uploads shared assets → copy skills use CDN URLs in CONFIG → image skills upload section images and update CONFIG/HTML with CDN URLs.

## File Naming

Output files follow a numbered prefix scheme matching their pipeline step:
`00_` through `05_` with letter suffixes for sub-steps (e.g., `03a_`, `03b_`).

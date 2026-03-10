# FunnelAgent

A Claude Code plugin that generates complete direct-response sales funnels — from deep market research through branding, advertorial, and sales page — via a guided multi-step pipeline.

## What It Does

FunnelAgent automates a 5-step copywriting workflow:

1. **Deep Research** — Uses the OpenAI Deep Research API with web search and code interpreter to conduct exhaustive market research (Reddit, YouTube, Amazon reviews, forums, competitor ads)
2. **Synthesis** — Identifies avatar/angle combinations with novelty gap scoring (Phase 1), then creates a 14-part strategic intelligence brief (Phase 2)
3. **Branding** — Generates brand name options, logo, color palette, and product image via Gemini API
4. **Advertorial** — Writes a full advertorial as a ready-to-use HTML page, optimizes headlines, and generates all images via Gemini API with iterative hero image QA
5. **Sales Page** — Writes a complete sales page with pricing bundles, testimonials, FAQ, and generates all images with hero image QA

## Quick Start

### 1. Setup

```bash
# Install Python dependencies
pip install -r scripts/requirements.txt

# Set your API keys
cp .env.example .env
# Edit .env and add your OpenAI + Gemini keys
```

### 2. Run the Pipeline

```
/funnel-orchestrator
```

The orchestrator will guide you through:
- Collecting product info (name, market, problem, ingredients, product image)
- Running deep research via the OpenAI Deep Research API
- Presenting avatar/angle options for your selection
- Generating the full strategic brief
- Creating brand identity (name, logo, colors)
- Writing the advertorial with headline optimization
- Generating advertorial images + hero image QA
- Writing the sales page
- Generating sales page images + hero image QA

### Amazon Session Scraper

If you want to use the first-party Amazon scraper path instead of the Apify wrapper:

```bash
python scripts/amazon_login.py
```

That command opens a headed browser, lets you log in manually, and saves reusable session state locally for later scraping commands.

### 3. Output

Each run creates its own subfolder based on the product name:

```
output/jointease/          ← first product
output/sleepwell-pro/      ← second product
```

Open `output/{product}/advertorial.html` and `output/{product}/sales_page.html` in a browser to preview. Re-running for the same product reuses the folder (with resume capability).

## Skills

| Skill | Command | Step |
|-------|---------|------|
| Orchestrator | `/funnel-orchestrator` | Guides the full pipeline |
| Extract Product Info | `/extract-product-info` | Step 0: Parse product URL |
| Deep Research | `/deep-research` | Step 1: Market research via OpenAI Deep Research API |
| Synthesis P1 | `/synthesis-phase1` | Step 2.1: Avatar/angle identification |
| Synthesis P2 | `/synthesis-phase2` | Step 2.2: Full strategic brief |
| Branding | `/branding` | Step 3: Brand name + logo + colors + product image |
| Write Advertorial | `/write-advertorial-copy` | Step 4.1: Advertorial CONFIG + HTML |
| Headline Optimization | `/headline-optimization` | Step 4.2: Headline audit + 5 variations |
| Advertorial Images | `/advertorial-images` | Steps 4.3-4.4: Image prompts + hero QA |
| Write Sales Page | `/write-sales-page` | Step 5.1: Sales page CONFIG + HTML |
| Sales Page Images | `/sales-page-images` | Steps 5.2-5.3: Image prompts + hero QA |

Each skill can be run independently if you want to re-do a specific step.

## Project Structure

```
FunnelAgent/
├── skills/                        # Skill definitions (11 skills)
│   ├── funnel-orchestrator/       # Main pipeline conductor
│   ├── extract-product-info/      # URL product extraction
│   ├── deep-research/             # ChatGPT API research
│   ├── synthesis-phase1/          # Avatar/angle selection
│   ├── synthesis-phase2/          # Full strategic synthesis
│   ├── branding/                  # Brand name + logo + colors
│   ├── write-advertorial-copy/    # Advertorial copy + HTML
│   ├── headline-optimization/     # Headline audit + variations
│   ├── advertorial-images/        # Advertorial images + hero QA
│   ├── write-sales-page/          # Sales page copy + HTML
│   └── sales-page-images/         # Sales page images + hero QA
├── scripts/
│   ├── deep_research.py           # OpenAI Deep Research API caller
│   ├── generate_image.py          # Gemini API image generator
│   └── requirements.txt           # Python dependencies
├── skill_content/                 # SOP reference documents (14 files)
├── templates/
│   ├── advertorial_POV.html       # Advertorial HTML template
│   └── sales_page.html            # Sales page HTML template
├── output/                        # Generated files (gitignored)
│   ├── jointease/                 # One subfolder per product run
│   ├── sleepwell-pro/             # Another product run
│   └── ...
├── .env.example                   # API key template
└── .claude-plugin/                # Plugin metadata
```

## Output Files

Each run folder (`output/{product}/`) contains:

| File | Step |
|------|------|
| `00_product_info.md` | Product info |
| `01_market_research.md` | Deep research |
| `02a_synthesis_phase1.md` | Avatar/angle options |
| `02b_synthesis_phase2.md` | Strategic brief |
| `03a_brand_names.md` | Brand name options |
| `03b_logo_prompt.md` | Logo generation prompt |
| `03c_color_vars.md` | CSS color variables |
| `03d_product_image_prompt.md` | Product image prompt |
| `04a_advertorial_config.js` | Advertorial CONFIG |
| `04b_headline_optimized.md` | Headline variations |
| `04c_image_prompts_advertorial.md` | Advertorial image prompts |
| `04d_hero_review.md` | Advertorial hero QA |
| `advertorial.html` | Final advertorial |
| `05a_sales_page_config.js` | Sales page CONFIG |
| `05b_image_prompts_sales_page.md` | Sales page image prompts |
| `05c_sp_hero_review.md` | Sales page hero QA |
| `sales_page.html` | Final sales page |
| `logo.png` | Generated logo |
| `product_image.png` | Generated product image |
| `advertorial_images/` | Advertorial section images |
| `sales_page_images/` | Sales page section images |

## Requirements

- Claude Code
- Python 3.8+
- OpenAI API key (for deep research step)
- Gemini API key (for image generation)

---
name: deep-research
description: Conducts exhaustive market research via the ChatGPT Deep Research API for direct response copywriting.
---

# Deep Research Skill

You execute Step 1 of the FunnelAgent pipeline: deep market research via the OpenAI API.

## PREREQUISITES

- `OPENAI_API_KEY` must be set in `.env` or environment
- Python 3.8+ with `openai` and `python-dotenv` packages installed
- The user must have provided: Product Name, Product Description, Target Market, Problem, Key Ingredients
- **OR** a sales page URL (product info will be extracted first)

## STEP 0 (OPTIONAL): EXTRACT PRODUCT INFO FROM URL

If you received a **sales page URL** instead of manual product info, extract the product details before proceeding:

1. Use the **WebFetch** tool to fetch the sales page:
   ```
   WebFetch:
     url: {sales_page_url}
     prompt: "Extract all product information from this sales page. Return:
       1. Product Name
       2. Product Description (format, features, benefits)
       3. Target Market (demographics, life situation)
       4. Problem (main pain point/desire)
       5. Key Ingredients/Components (with dosages if listed)
       Be thorough and extract exact details."
   ```
2. Use the extracted info to fill in the product fields for Step 2 below.
3. Also pass the URL to the research prompt as **OPTION B (Upload Input)** so ChatGPT can deep-dive the page itself during research.

If `output/00_product_info.md` already exists (created by the extract-product-info skill), read it and use that data instead of re-fetching.

## STEP 1: LOAD THE FULL SOP

**MANDATORY FIRST ACTION:** Read the complete Deep Research SOP:
```
skill_content/PROMPT 1_ ChatGPT Market Research.md
```

This file contains the ENTIRE research framework that ChatGPT must follow — all 15 sections, all phases, all output requirements. You MUST read it in full before constructing the prompt.

## STEP 2: BUILD THE RESEARCH PROMPT

Construct the prompt to send to ChatGPT by combining:

1. **The complete SOP content** — Copy the ENTIRE SOP verbatim, starting from "DEEP RESEARCH SOP FOR DIRECT RESPONSE COPYWRITING" through "END OF RESEARCH SOP". Do NOT summarize or abbreviate.

2. **The user's product info** — Inject into the INPUT METHOD section:
   - If manual input: Fill in Basic Product Info, Basic Problem/Market, Key Ingredients
   - If URL provided: Use OPTION B (Upload Input) format

3. **Pre-seeded angle** (if provided by user) — Append as Section 15 input:
   ```
   SECTION 15: PRE-SEEDED ANGLE VALIDATION
   Angle to test: [USER'S ANGLE IDEA]
   Please validate this angle against your research findings.
   ```

Save the complete constructed prompt to `output/00_research_prompt.md`.

## STEP 3: EXECUTE THE RESEARCH

Run the Python script:

```bash
python scripts/deep_research.py \
  --prompt-file output/00_research_prompt.md \
  --output output/01_market_research.md
```

Expected runtime: 2-10 minutes. The script calls OpenAI's API with `web_search_preview` tool enabled.

## STEP 4: VALIDATE OUTPUT

After the script completes, read `output/01_market_research.md` and verify it contains the sections specified in the SOP's OUTPUT CHECKLIST:

- Step 0: Input Definition (Product, Target Market, Core Problem, Ingredients)
- Phase 1: Foundation Setting (4 definitions)
- Phase 2: Source Identification (5 categories of sources)
- Phase 3: Deep Data Mining (Sections 1-15 with all required quote minimums)
- 12+ pages total, no narrative paragraphs, all quotes sourced

If output is insufficient (< 3000 words or missing major sections), report to the user and suggest re-running with `--model gpt-4o` or providing more specific product info.

## TROUBLESHOOTING

| Issue | Solution |
|-------|----------|
| `OPENAI_API_KEY not set` | Create `.env` file with the key |
| `openai package not installed` | Run `pip install -r scripts/requirements.txt` |
| `Model not available` | Try `--model gpt-4o` as fallback |
| Output too short | Re-run or provide more context |
| API rate limit | Wait and retry |

## OUTPUT

Research document saved to `output/01_market_research.md` — used by synthesis skills in the next steps.

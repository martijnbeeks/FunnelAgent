---
name: extract-product-info
description: Extracts structured product information from a sales page URL using WebFetch.
---

# Extract Product Info Skill

You extract structured product information from a sales/product page URL. This is a utility skill used by the orchestrator to auto-populate product details instead of requiring manual input.

## INPUT

- A sales page URL provided by the user

## STEP 1: FETCH THE PAGE

Use the **WebFetch** tool to retrieve the sales page content:

```
WebFetch:
  url: {sales_page_url}
  prompt: "Extract all product information from this sales page. Return the following structured data:
    1. Product Name — the exact product name
    2. Product Description — what it is, format (pill/cream/powder/device/service), key features and benefits
    3. Target Market — who is this for: age, gender, life situation, health conditions
    4. Problem — the main pain point, frustration, or desire being addressed
    5. Key Ingredients/Components — all active compounds, ingredients, or key components listed
    6. Price points — any pricing info visible
    7. Claims — key marketing claims or promises made on the page

    Be thorough. Extract exact ingredient names and dosages if listed. Capture the language and framing used on the page."
```

## STEP 2: STRUCTURE THE OUTPUT

From the WebFetch results, compile a clean structured document with these sections:

```markdown
# Product Info — {Product Name}

## Product Name
{exact name}

## Product Description
{what it is, format, key features}

## Target Market
{who it's for — demographics, life situation, conditions}

## Problem
{main pain point or desire addressed}

## Key Ingredients/Components
{list all active ingredients/components with dosages if available}

## Additional Context
- **Price:** {if found}
- **Key Claims:** {major marketing claims}
- **Source URL:** {the original URL}
```

## STEP 3: SAVE OUTPUT

Save the structured product info to `output/00_product_info.md`.

## STEP 4: PRESENT FOR REVIEW

Display the extracted info to the user and ask:

> **"Here's what I extracted from the sales page. Please review and correct anything that's wrong or missing before we proceed."**

Wait for user confirmation or corrections. If the user provides corrections, update the output file accordingly.

## OUTPUT

`output/00_product_info.md` — structured product info ready for use by downstream pipeline steps.

# Sales Page CONFIG Schema Reference

This file documents the CONFIG, PRODUCT_COLORS, and OFFER_SETTINGS structures expected by `templates/sales_page.html`. Use this to build your CONFIG — only read the full HTML template when assembling the final page (Step 9).

## PRODUCT_COLORS Object

```javascript
const PRODUCT_COLORS = {
    primary: "#XXXXXX",       // String — dominant brand color from product packaging
    primaryDark: "#XXXXXX",   // String — ~25-30% darker shade of primary
    primaryLight: "#XXXXXX",  // String — very light tint (~90-95% lightness) for section backgrounds
    accent: "#XXXXXX"         // String — a color from the product packaging, dark enough for white button text
};
```

If any value is empty/falsy, the theme default is used.

## OFFER_SETTINGS Object

```javascript
const OFFER_SETTINGS = {
    currency: "USD",           // String — "USD" | "GBP" | "EUR" | "ILS" | "CUSTOM"
    customCurrency: {          // Object — only used when currency is "CUSTOM"
        symbol: "$",
        position: "before",    // "before" | "after"
        decimal: "."
    },
    bundles: [                 // Array (3 items) — product bundle options
        {
            name: "",          // String — display name (e.g. "1 Month Supply")
            description: "",   // String — subtitle/badge (e.g. "Most Popular", "" for none)
            originalPrice: 79, // Number — full price before discount
            salePrice: 39,     // Number — discounted price
            perUnitPrice: "",  // String — per-unit text (e.g. "$39.00/unit")
            image: "",         // String — product bundle image URL
            checkoutUrl: ""    // String — checkout link for this bundle
        }
    ],
    gifts: [                   // Array — free gifts unlocked by bundle tier
        {
            name: "",          // String — gift display name
            value: 0,          // Number — gift value
            image: "",         // String — gift image URL
            unlocksAtBundle: 1 // Number — 1 = all bundles, 2 = bundle 2+, 3 = bundle 3 only
        }
    ],
    countdown: {
        mode: "midnight",      // String — "midnight" | "fixed"
        fixedMinutes: 30       // Number — only used when mode is "fixed"
    }
};
```

## CONFIG Object

```javascript
const CONFIG = {
    BRAND_NAME: "",            // String — brand name used throughout the page
    THEME: "health",           // String — "health" | "beauty" | "other"

    URGENCY: {
        HERO_INGREDIENT: "",   // String — key ingredient name for urgency banner
        BOTTLE_COUNT: "",      // String — bottles remaining count
        DISCOUNT_PERCENT: ""   // String — discount percentage
    },

    HERO: {
        HEADLINE: "",          // String — may include <span class='hero__headline-highlight'>
        BADGE: "",             // String — trust badge text (e.g. "Doctor Formulated")
        SUBHEADLINE: "",       // String — subtitle below headline
        BENEFITS: [],          // Array of Strings — 3 bullet benefits
        IMAGE: ""              // String — hero image URL
    },

    TRUST_BAR: {
        RATING: "4.8",         // String — star rating
        REVIEW_COUNT: ""       // String — formatted count (e.g. "17,432")
    },

    DEMOGRAPHIC: {
        LINE_1: "",            // String — may include inline HTML for underline
        LINE_2: ""             // String — empathy line
    },

    AGITATION: {
        TITLE: "",             // String — section title
        UMP_TEXT: "",          // String — HTML explaining the root cause (<strong> allowed)
        FAILED_ATTEMPTS: "",   // String — HTML explaining why other things fail
        IMAGE: ""              // String — agitation image URL
    },

    DOCTOR: {
        NAME: "",              // String — doctor name
        TITLE: "",             // String — credentials (e.g. "Board-Certified Urologist")
        YEARS: "",             // String — years of experience
        QUOTE: "",             // String — doctor quote (use [BRAND] placeholder)
        IMAGE: ""              // String — doctor portrait URL
    },

    MECHANISM: {
        TITLE: "",             // String — section title
        DIAGRAM_IMAGE: "",     // String — mechanism diagram URL
        UMP: {
            LABEL: "",         // String — "why it happens" label
            TEXT: ""           // String — HTML explanation (<strong> allowed)
        },
        UMS: {
            LABEL: "",         // String — "how we fix it" label
            TEXT: ""           // String — HTML explanation (use [BRAND] placeholder, <strong> allowed)
        },
        INGREDIENTS: [         // Array — ingredient accordion items
            {
                NAME: "",      // String — ingredient name with form
                BENEFIT: "",   // String — one-line benefit
                DESCRIPTION: "",// String — detailed description
                STAT: ""       // String — research/stat backing
            }
        ],
        TRANSITION: "",        // String — paragraph after ingredients
        NO_CLAIMS: []          // Array of Strings — "NO X" badges (e.g. "NO GMOs")
    },

    TESTIMONIALS: {
        TITLE: "",             // String — may include **bold** markdown
        SUBTITLE: "",          // String
        TITLE_B: "",           // String — second testimonial section title
        REVIEWS_A: [           // Array (3 items) — first testimonial block
            {
                NAME: "",      // String — reviewer name
                TEXT: "",      // String — review text
                IMAGE: ""      // String — "" (AI-generated), "gemini" (Gemini API), or URL
            }
        ],
        REVIEWS_B: [           // Array (3 items) — second testimonial block
            {
                NAME: "",
                TEXT: "",
                IMAGE: ""
            }
        ]
    },

    ALTERNATIVES: {
        TITLE: "",             // String
        SUBTITLE: "",          // String
        DIAGRAM_IMAGE: "",     // String — comparison diagram URL
        ITEMS: [               // Array — competitor alternatives
            {
                NAME: "",      // String — alternative name
                TEXT: ""       // String — HTML why it fails (<strong> allowed)
            }
        ],
        SOLUTION_TEXT: ""      // String — HTML why this product is better (<strong> allowed)
    },

    TIMELINE: {
        TITLE: "",             // String — use [BRAND] placeholder
        PHASES: [              // Array (4 items) — progress phases
            {
                PERIOD: "",    // String — time period (e.g. "Week 1-2")
                NAME: "",      // String — phase name
                TEXT: ""       // String — description
            }
        ]
    },

    PRICING: {
        TITLE: "",             // String
        OPTIONS: [             // Array (3 items) — pricing display cards
            {
                SUPPLY: "",    // String — supply duration
                BOTTLES: "",   // String — bottle count
                ORIGINAL: "",  // String — original price with currency symbol
                PRICE: "",     // String — sale price with currency symbol
                SAVINGS: "",   // String — savings text
                SHIPPING: "",  // String — shipping info
                POPULAR: false // Boolean — highlight as popular
            }
        ],
        ORDER_URL: "#order"    // String
    },

    GUARANTEE: {
        NAME: ""               // String — guarantee name (e.g. "Sleep Better")
    },

    FAQ: {
        TITLE: "",             // String
        ITEMS: [               // Array — accordion Q&A items
            {
                Q: "",         // String — question
                A: ""          // String — HTML answer (<strong> allowed, use [BRAND] placeholder)
            }
        ]
    },

    MISS: {
        TITLE: "",             // String
        WITHOUT: [],           // Array of Strings — "without product" consequences
        WITH: [],              // Array of Strings — "with product" benefits
        WITHOUT_IMAGE: "",     // String — comparison image URL
        WITH_IMAGE: "",        // String — comparison image URL
        CLOSING: ""            // String — closing urgency line
    },

    FINAL_CTA: {
        TITLE: "",             // String
        SUBTITLE: "",          // String
        TRUST_LINE: ""         // String — trust badges text
    }
};
```

## Theme Options

| Theme | Primary | Accent | "As Seen In" Logos |
|-------|---------|--------|-------------------|
| `health` | Green `#1a5f4a` | Orange `#c2410c` | WebMD, Healthline, Men's Health, Prevention, AARP |
| `beauty` | Dusty rose `#b4838d` | Orange `#c2410c` | Allure, Vogue, Harper's Bazaar, Elle, Women's Health |
| `other` | Blue `#1e40af` | Orange `#c2410c` | Forbes, TechCrunch, Wired, Fast Company, Inc. |

Note: When PRODUCT_COLORS are set, they override theme defaults for primary, primaryDark, primaryLight, and accent.

## Currency Presets

| Code | Symbol | Position | Decimal |
|------|--------|----------|---------|
| `USD` | $ | before | . |
| `GBP` | £ | before | . |
| `EUR` | € | after | , |
| `ILS` | ₪ | before | . |

## Critical Rules

- **[BRAND] placeholder**: Use `[BRAND]` in doctor quotes, mechanism text, FAQ answers, and timeline title — the template replaces it with `CONFIG.BRAND_NAME`
- **No line breaks** inside string values — must be continuous
- HTML elements (`<strong>`, `<span>`) are allowed in most text fields
- `TESTIMONIALS.REVIEWS_A/B[].IMAGE` accepts `""` (AI-generated), `"gemini"` (Gemini API generates), or a URL
- `PRICING.OPTIONS` is display-only — actual checkout uses `OFFER_SETTINGS.bundles[].checkoutUrl`

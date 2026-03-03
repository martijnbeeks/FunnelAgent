# Advertorial CONFIG Schema Reference

This file documents the CONFIG object structure expected by `templates/advertorial_POV.html`. Use this to build your CONFIG — only read the full HTML template when assembling the final page (Step 9).

## CONFIG Object

```javascript
const CONFIG = {
    THEME: "health",           // String — "health" | "medical" | "beauty" | "energy" | "calm"
    SITE_NAME: "",             // String — overrides theme default site name (optional)
    CATEGORY: "",              // String — tag above headline (e.g. "Personal Experience")
    HEADLINE: "",              // String — main article headline
    SUBHEADLINE: "",           // String — italic sub-headline below hero image
    AUTHOR_NAME: "",           // String — byline (e.g. "Margaret T.")
    HERO_IMAGE: "",            // String — URL for hero image

    SECTIONS: [                // Array of section objects
        {
            headline: "",      // String — section H2
            image: "",         // String — section image URL (empty = no image)
            body: ``           // String (template literal) — HTML content (see elements below)
        }
    ],

    PRODUCT_NAME: "",          // String — product display name
    PRODUCT_IMAGE: "",         // String — product image URL
    PRODUCT_DESCRIPTION: "",   // String — one-line product description
    PRODUCT_BENEFITS: [],      // Array of Strings — bullet benefits (shown with checkmarks)
    ORDER_URL: "#order",       // String — CTA destination URL

    SIGN_OFF_TEXT: "",         // String — closing message
    SIGN_OFF_NAME: "",         // String — author sign-off (e.g. "—Margaret, Age 64")

    SIDEBAR_REVIEWS: [         // Array (3 items) — sidebar review cards
        {
            stars: "★★★★★",   // String — star display
            text: "",          // String — review text
            name: "",          // String — reviewer name
            age: "",           // String — reviewer age
            initial: ""        // String — single letter for avatar circle
        }
    ],

    REVIEWS_SCORE: "4.9",      // String — aggregate score
    REVIEWS_COUNT: "18,472",   // String — total review count (formatted)
    REVIEWS: [                 // Array (5 items) — bottom review cards
        {
            name: "",          // String — reviewer name
            age: "",           // String — reviewer age
            initial: "",       // String — single letter for avatar circle
            stars: "★★★★★",   // String — star display
            title: "",         // String — review title
            text: ""           // String — review body (may include HTML highlight spans)
        }
    ]
};
```

## Theme Options

| Theme | Primary | Site Name Default | Logo Icon |
|-------|---------|-------------------|-----------|
| `health` | Green `#1a5f4a` | Daily Wellness Journal | ✦ |
| `medical` | Blue `#1e40af` | Health Monitor Weekly | ✚ |
| `beauty` | Dusty rose `#b4838d` | Beauty & Glow Magazine | ✿ |
| `energy` | Orange `#c2410c` | Vitality Today | ⚡ |
| `calm` | Lavender `#8b93b8` | Restful Living | ☾ |

## Allowed HTML Elements in Section `body`

| Element | Purpose |
|---------|---------|
| `<p>Regular paragraph</p>` | Standard paragraph |
| `<p class="short">Short paragraph</p>` | Reduced bottom margin |
| `<strong>bold</strong>` | Bold emphasis |
| `<span class="highlight">text</span>` | Yellow highlight underline |
| `<div class="quote-box"><p>Peer quote</p></div>` | Styled quote block |
| `<div class="mechanism-box"><p>UMP explanation</p></div>` | Warning-style mechanism box |
| `<div class="validation-box"><p>You're not broken</p></div>` | Green validation box |
| `<p class="failed-solution"><strong>X</strong> — why</p>` | Failed solution (red bold) |
| `<p class="timeline-item"><strong>Time:</strong> Event</p>` | Timeline entry (green bold) |

## Critical Rules

- **No line breaks** inside `body` template literal strings — must be a single continuous line
- Empty sections (no headline + no body) are automatically skipped
- Sidebar is hidden on screens < 1100px
- Sticky CTA appears after Section 5 (index 4)

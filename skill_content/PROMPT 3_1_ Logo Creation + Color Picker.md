First, analyze the provided product packaging image and identify the exact dominant colors, accent tones, and visual mood. Then, based on that analysis, **create a prompt to feed to Gemini API** for an ultra-professional, minimalist vector logo for the brand: **\[INSERT YOUR BRAND NAME HERE™\]**. The generated prompt must instruct Gemini API to color-match the logo exclusively to the packaging palette identified in the analysis. The prompt must also include the following instructions: Clean, balanced, and modern design inspired by premium health & beauty brands like Lumēvia™, Fungia™, or Sciatico™. A small, elegant icon or symbol to the left of the text representing calmness, breathing, or airflow — such as a soft wave, leaf, or gentle swirl — colored to match the packaging. A refined serif or semi-serif font (not sans-serif) conveying trust, calmness, and sophistication. A ™ symbol at the end of the brand name. The logo must fill the entire 432×98 px frame horizontally with no excess transparent padding. 100% transparent background — no white, grey, shadow, or gradient. Flat, high-quality vector graphic appearance, cropped exactly to the logo's edges, rendered as if for Shopify header or product packaging. Output dimensions exactly 432×98 pixels. 

When done, continue with the following assignment: 

**Look at the product image. Extract the dominant brand color from the packaging/label (ignore white, black, small highlighted color and background colors). Then give me updated values for these four theme variables:** 

1\. **`primary`** — The dominant brand color as-is (hex) 

2\. **`primaryDark`** — A darker shade of that color, suitable for headers and buttons (roughly 25-30% darker) 

3\. **`primaryLight`** — A very light tint of that color, suitable for section backgrounds (roughly 90-95% lightness) 

4\. **`accent`** — A color that actually appears on the product packaging (cap, label, icon, text, or trim — not the background/white). Must pass WCAG AA contrast with white text. If the product only has one non-white/non-black color, use that color or its darker shade. **Never use a color not found on the product.**

**Output format — just this, nothing else:** 

primary: "\#\_\_\_\_\_\_", 

primaryDark: "\#\_\_\_\_\_\_", 

primaryLight: "\#\_\_\_\_\_\_", 

accent: "\#\_\_\_\_\_\_", 

**Rules:** 

● Base `primary`, `primaryDark`, and `primaryLight` on the SAME hue from the product packaging 

● `primaryDark` must pass WCAG AA contrast on white text  
● `primaryLight` must be subtle enough to use as a full-section background without overwhelming body text 

● `accent` is for CTA buttons — it MUST be dark enough for white text to be clearly readable. Never use a light or medium color here.
● `accent` MUST be a color that actually exists on the product packaging — never invent a color not on the product. If the dominant color is too light, use a darker shade of that same color.
● If the packaging has multiple colors, choose the one that carries the most brand identity (usually the largest non-white, non-black color on the label)
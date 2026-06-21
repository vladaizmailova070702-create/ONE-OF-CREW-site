# Frontend Website Rules

These rules apply when building or changing websites, landing pages, marketing pages,
frontend components, visual UI, and responsive web layouts.

## Project Brief

Before writing any code, read the project-specific brief if one exists:

- Look for `docs/` directory and read any `*_SITE_PROMPT.md` or `*_PROJECT.md` files first.
- The project brief overrides generic defaults below when they conflict.
- If no project brief exists, apply these rules as the full specification.

## Always Do First

- If a `frontend-design` skill or equivalent design instruction file is available, load it before writing frontend code in every session.
- Inspect the existing project structure before choosing an implementation style.
- Check `brand_assets/` first, then `assets/`, then existing public/static folders. Use real brand assets before placeholders.
- Identify the target stack from the repository. For existing apps, follow the app's framework, routing, styling, and component patterns.
- For a brand-new static prototype, default to a single `index.html` with self-contained styles unless the user asks for a framework.

## Design Intent

- Build the actual usable page or interface first, not a marketing explanation of what the page could be.
- Treat the target audience and domain as design constraints. Operational tools should be dense, calm, and scannable; editorial or campaign sites can be more expressive.
- Make the primary subject visible in the first viewport: product, person, venue, brand, object, dashboard, tool, or gameplay state.
- Prefer precise, restrained composition over generic "AI landing page" patterns.

## Reference Images

- If a reference image is provided, match layout, spacing, typography, color, border radius, shadows, and image treatment as closely as possible.
- Do not add sections, features, decorative elements, or content that are not present in the reference unless the user asks.
- Do not "improve" a reference design. Recreate it faithfully.
- Screenshot the implementation, compare it against the reference, fix visible mismatches, and screenshot again.
- Run at least two comparison rounds unless the first pass is already visually indistinguishable or the user explicitly stops the process.
- When comparing, be concrete: note actual mismatches such as "heading is 32px but reference is about 24px" or "card gap is 16px but should be 24px".

## Local Server And Verification

- Always verify through `localhost` or the project's dev server URL. Do not rely on `file:///` screenshots for final visual QA.
- If the project has a dev command, use it. Examples: `npm run dev`, `pnpm dev`, `yarn dev`, `bun dev`, `astro dev`, `next dev`, or the repo's documented command.
- If the project includes a local static server script such as `serve.mjs`, use it rather than inventing another server.
- Before starting a server, check whether one is already running on the expected port.
- Keep one server instance per port.
- Capture screenshots from the served URL and inspect the actual image before declaring the work done.
- Verify at minimum one desktop viewport and one mobile viewport for layout, overflow, and text fitting.

## Project Workflow

- Treat `CLAUDE.md` as the primary instruction file. `AGENTS.md` exists only to point agents back here.
- After every meaningful change, create an intentional git commit and push it to `main`.
- If push fails because network or authentication is unavailable, leave the local commit on `main`, report the exact error, and do not pretend it was pushed.

## Asset Layout

- Production files that can be served publicly live in the repository root, `brand_assets/`, and `assets/`.
- Optimized web media belongs in an explicit production subfolder under `assets/`, such as `assets/web/` or `assets/webp/`.
- Heavy originals and source-only material belong in `source_assets/originals/`. Keep them as an archive and do not reference them directly from `index.html`.
- Do not delete heavy originals unless the user explicitly asks. Move them out of production paths instead, then document where they went.
- Hosting ignore files such as `.vercelignore` and `.netlifyignore` must exclude source archives and local QA material from deployment.

## Screenshot Workspace

- Keep `temporary screenshots/` in the project as the shared local visual QA workspace for humans and AI agents.
- Store before/after screenshots, section crops, contact sheets, and comparison artifacts there while working.
- The folder contents are gitignored, except `temporary screenshots/README.md`, so local visual artifacts do not get published accidentally.
- Do not delete the folder just because its contents are temporary.

## Screenshot Checklist

Check all of the following before finalizing:

- Spacing, padding, alignment, and grid rhythm.
- Font family, size, weight, line height, and letter spacing.
- Exact or intentionally derived colors, including hover and focus states.
- Border radius, borders, dividers, shadows, and depth.
- Image crop, aspect ratio, focal point, overlays, and loading behavior.
- Mobile stacking, tap targets, wrapping, and horizontal overflow.
- Header, navigation, sticky elements, modals, and menus across breakpoints.
- Empty, loading, error, and disabled states when the UI includes dynamic behavior.

## Output Defaults

- For new static pages, prefer one `index.html` with inline CSS or a minimal local CSS file.
- Tailwind CDN is acceptable for quick prototypes only: `<script src="https://cdn.tailwindcss.com"></script>`.
- For production or existing projects, use the project's installed styling system instead of adding Tailwind by default.
- Placeholder images may use `https://placehold.co/WIDTHxHEIGHT`, but only when no suitable real asset exists.
- Use mobile-first responsive CSS.
- Use semantic HTML first. Reach for JavaScript only when interaction or state requires it.
- Do not introduce new dependencies unless they materially improve the result and fit the project.

## Brand Assets

- Always inspect `brand_assets/` before designing.
- If a logo exists, use it.
- If a color palette, typography sample, style tile, or screenshot exists, derive the design from it.
- If assets exist in `assets/`, prefer them over remote placeholder media.
- Do not replace real assets with placeholders.
- If only a raster palette image is provided, sample colors from it and use explicit hex values.

## Visual Craft Guardrails

- Do not use default Tailwind blue/indigo/purple as the primary palette unless it is part of the brand.
- Avoid one-note palettes where the whole page is only one hue family.
- Pair typography intentionally. Do not use the exact same generic font treatment for headings and body unless the brand demands it.
- Use consistent spacing tokens. Do not scatter random one-off spacing values.
- Create a clear depth system: base, raised, overlay, and focus states.
- Avoid generic `shadow-md` styling. Use shadows that match the surface, background, and light model.
- Do not decorate pages with disconnected gradient orbs, bokeh blobs, or arbitrary abstract shapes.
- Gradients should support content or image treatment, not hide weak layout.
- Animate only `transform` and `opacity` by default.
- Do not use `transition-all`.
- Every clickable element needs hover, active, disabled where relevant, and keyboard-visible focus states.
- Text must fit inside its container at mobile and desktop widths. Do not let labels, buttons, nav items, or cards overlap.
- Do not put cards inside cards unless the nested card is a true repeated data item or modal content.
- Keep card radius at 8px or less unless the existing design system uses a different radius.

## Layout And Responsiveness

- Use explicit layout constraints: max widths, grid tracks, aspect ratios, min/max sizes, and stable component dimensions.
- Do not scale font sizes directly with viewport width.
- Keep letter spacing at `0` unless a specific type style requires otherwise.
- Hero sections must leave a hint of the next section visible on normal mobile and desktop viewports.
- Do not use split hero layouts with text on one side and a decorative mockup card on the other unless the reference requires it.
- For landing heroes, make the H1 the brand, product, person, place, or literal offer. Put value proposition details in supporting copy.

## Content Rules

- Use the user's supplied copy exactly when provided.
- If copy is missing, write concise, domain-appropriate placeholder copy that can survive visual QA.
- Do not invent claims, prices, metrics, testimonials, awards, legal statements, or integrations.
- Avoid visible instructional text explaining the UI, its styling, or how to use obvious controls.
- Prefer concrete labels over vague labels such as "Learn more" when the destination is known.

## Accessibility And UX

- Use semantic landmarks: `header`, `nav`, `main`, `section`, `footer`, and meaningful headings.
- Maintain a logical heading order.
- Provide alt text for meaningful images. Use empty alt text for purely decorative images.
- Ensure color contrast is readable for body text, controls, and critical UI.
- Use real buttons for actions and real links for navigation.
- Ensure forms have labels, clear errors, and visible focus states.
- Respect reduced-motion preferences for nonessential animations.

## Performance

- Use appropriately sized images and preserve aspect ratios to avoid layout shift.
- Lazy-load non-critical images.
- Avoid heavy animation, large libraries, and unnecessary client-side JavaScript.
- Keep critical above-the-fold content fast and stable.
- Do not block rendering with unused fonts, icon packs, or scripts.

## Hard Rules

- Do not stop after one screenshot pass when visual matching or high-polish design is required.
- Do not use `transition-all`.
- Do not use default Tailwind blue/indigo/purple as the primary color unless it is a brand color.
- Do not ignore `brand_assets/` or `assets/`.
- Do not claim a screenshot or browser check was performed unless it was actually performed.
- Do not ship a layout with horizontal overflow, overlapping text, invisible focus, or broken mobile navigation.
- Do not rewrite unrelated project architecture to complete a visual task.

## Mandatory Self-Verification Workflow (do this, do not skip)

Verify visually **after every section and every change round** — not once at the end. The pattern is: build/edit a section → screenshot it on desktop and mobile → actually open and read the image → fix what you see → screenshot again. Most regressions (clipping, tiny logos, overflow, distorted images) are only caught by looking. If you skip this, you ship bugs.

Rules:
- Verify **each section the page actually has** (hero, gallery/portfolio, about, services, process, contact, footer, etc.), plus the global header/nav and footer, at **one desktop and one mobile width**.
- **Crop each section to its native resolution and look at the actual content — never judge a section from a downscaled full-page slice.** A whole-page screenshot scaled to ~360px hides sizing bugs (thumbnails squeezed into a grid cell, fixed-px elements that don't scale). Crop the real pixels and check element sizes, e.g. that gallery thumbnails are large and fill their row.
- **Also check at a large viewport (≈2560px wide).** Bugs from fixed-size or wrongly-nested grids only show on big screens. If an element looks "tiny and static" on 2K, find what constrains its size (a parent grid track, a `max-width`, a fixed `px`).
- If a section has interactive state (tabs, flip cards, lightbox, accordions), switch into that state before capturing — drive it with query params if the page supports them, or with Playwright. Don't assume the default state represents the whole section.
- Inspect **brand assets at the pixel level before using them** (dimensions, transparent padding, aspect ratio). A square PNG with large transparent margins will render tiny — trim it first. Never trust an asset's apparent size; measure it.
- After any text change, re-read the rendered section image to confirm no clipping/overflow and that wording is correct.
- Re-screenshot after each fix. Two passes minimum on anything visual.

### Local capture recipe on this machine (Windows)

Serve the static site from the repository root with any local HTTP server, then capture screenshots.

**Use Playwright for anything that depends on viewport height (`vh`/`svh`/`dvh`) — the hero, sticky/pinned elements, full-screen sections.** The headless Chrome `--screenshot` CLI resolves viewport-height units to the WRONG value (smaller than the screenshot surface), so a `100svh`/`100dvh` section looks broken (content mid-page, clipped buttons) even when the CSS is correct. Playwright sets a real layout viewport via CDP, so the units resolve exactly like a real browser. It can drive the already-installed Chrome with `channel="chrome"` (no extra browser download):

```
pip install playwright
python -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(channel='chrome')
    pg=b.new_page(viewport={'width':1440,'height':900})   # real viewport: svh/dvh == 900
    pg.goto('http://127.0.0.1:8123/', wait_until='load'); pg.wait_for_timeout(2500)
    pg.screenshot(path=r'%TEMP%/shots/desk.png')           # viewport-only by default
    # measure instead of guessing pixels:
    print(pg.evaluate('()=>({innerH:innerHeight, heroBottom:document.querySelector(\".hero\").getBoundingClientRect().bottom})'))
    b.close()
"
```
Drive interactive state with Playwright too (`pg.locator('#some-section').scroll_into_view_if_needed()`, click tabs, `pg.evaluate(...)` to read computed rects). Reading `getBoundingClientRect()` / `getComputedStyle` is more reliable than eyeballing crops.

The raw headless Chrome CLI (below) is fine for sections that DON'T depend on viewport height.

Environment gotchas (these have actually broken captures here):
- **Screenshot output path must contain NO spaces.** Chrome reads a space as a second "target" and fails with `Multiple targets are not supported`. Write raw headless output to a space-free dir (e.g. `%TEMP%\shots`), then copy reviewed/cropped artifacts into `temporary screenshots/` when they are useful for comparison.
- A `100svh`/`100dvh` section captured with the raw headless CLI in a tall window just stretches to fill the window. Verify those with Playwright (above), or with a static QA mode if the page provides one.
- Headless screenshots fire at load, before `IntersectionObserver` reveals run and before lazy images decode, so below-fold content looks blank. Wait for load + a short delay, or use a static QA mode if the page provides one.

**Optional: a static QA mode.** Consider building a query flag (e.g. `?qa=1`) into the page that renders the final, non-animated state, force-eager-loads all images, and disables scroll-triggered reveals — it makes headless full-page captures reliable. If the page exposes such a flag, use it for below-fold captures; do not rely on it for sections whose height depends on the viewport.

Working raw-CLI command (for non-viewport-height sections):
```
$out = "$env:TEMP\shots\name.png"   # space-free path
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new --no-first-run `
  --disable-gpu --no-sandbox --hide-scrollbars --user-data-dir="$env:TEMP\crp" `
  --window-size=1440,12000 --screenshot="$out" "http://localhost:8123/"
```
Then crop regions with `System.Drawing.Bitmap` and open each crop to inspect. Verify mobile by repeating with `--window-size=430,...`.

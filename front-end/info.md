# Tech Stack Research — The Edwardian Chronicle

## Research Date: 2026-05-22

---

## 1. Page-Flip Effect (Definitive: react-pageflip)

**Winner: `react-pageflip` v2.0.3** (React wrapper around StPageFlip)

| Library | npm package | Size | React Support | Status | Physics |
|---------|-------------|------|---------------|--------|---------|
| **react-pageflip** | `react-pageflip` | ~12 KB gzipped | Native | Stable (66K+ weekly DL) | Best |
| StPageFlip (core) | `page-flip` | ~10 KB gzipped | Via wrapper | Feature-complete | Best |
| @vuvandinh203/react-flipbook | `@vuvandinh203/react-flipbook` | ~15 KB | Native + Hooks | Active (7mo ago) | Good |
| Turn.js | `turn.js` | 200+ KB | No | ABANDONED | Good |
| CSS 3D Custom | N/A | 0 KB | Yes | N/A | Poor |
| Flipbook Viewer | `flipbook-viewer` | ~18 KB | Via wrapper | Active | Basic |

**Why react-pageflip:**
- Most realistic page-turning physics (page actually bends/curls like real paper)
- Only renders visible + adjacent pages (DOM-virtualized) — perfect for 50 pages
- Full HTML content support — can style pages with aged-paper CSS, serif fonts, multi-column layouts
- Hard/soft page density — cover pages rigid (`data-density="hard"`), inner pages bend naturally
- Touch/swipe on mobile
- Zero dependencies (no jQuery)

**Install:** `npm install react-pageflip`

---

## 2. Newspaper Layout Engine (Definitive: CSS Grid + CSS Columns)

**Architecture: CSS Grid for page structure + CSS Columns for article text flow.**
No JavaScript layout engine needed.

```
Page Layout (CSS Grid)          Article Text (CSS Columns)
+-------------------------+     +--------------------+
|      MASTHEAD (full)    |     |  Headline (span)   |
+--------+--------+-------+     +--------------------+
| Article| Article|Article|     | Text | Text | Text |
| Card 1 | Card 2 |Card 3 |     | col1 | col2 | col3 |
| (2col) | (body) |(body) |     |      |      |      |
+--------+----------------+     +--------------------+
|  Feature Article | Side  |
|  (span 3)        | bar   |
+--------------------------+
```

**Key CSS:**
```css
.newspaper-page {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 1.5rem;
}
.article-card {
  break-inside: avoid; /* NEVER split across columns */
}
.article-body {
  columns: 2 8em;
  text-align: justify;
  hyphens: auto;
}
.drop-cap::first-letter {
  float: left;
  font-size: 3.2em;
  line-height: 0.8;
  margin-right: 0.05em;
}
```

**Responsive Breakpoints:**
- Desktop (1200px+): 5 columns, 3-column article text
- Tablet (768px-1199px): 3 columns, 2-column article text
- Mobile (<768px): 1 column, single article text

---

## 3. Typography — Victorian/Edwardian Fonts

| Role | Font | Weights | Google Font |
|------|------|---------|-------------|
| **Masthead** | `Playfair Display` | 700, 900 | Yes |
| **Masthead Alt** | `UnifrakturMaguntia` | 400 (Gothic) | Yes |
| **Headlines** | `Playfair Display` | 700, 900 | Yes |
| **Sub-headlines** | `Playfair Display` | 400, 400i | Yes |
| **Body text** | `EB Garamond` | 400, 400i, 500 | Yes |
| **Body alt** | `Crimson Text` | 400, 400i | Yes |
| **Captions** | `EB Garamond` italic | 400i | Yes |
| **Date/header** | `IM Fell English` | 400 | Yes |

**Font pairing recommendation:**
- Masthead: Playfair Display 900 (uppercase, letter-spacing)
- Headlines: Playfair Display 700
- Body: EB Garamond 400
- Captions: EB Garamond 400 italic

---

## 4. Paper Texture & Aging Effects

**Subtle is key — avoid overdone "old paper" look.**

```css
/* Aged paper background */
--paper-bg: #f5f0e1;
--paper-dark: #e8e0cc;
--ink-black: #2c2416;
--ink-faded: #6b5d4f;

/* Page background */
.newspaper-page {
  background-color: var(--paper-bg);
  box-shadow: 
    inset 0 0 60px rgba(139, 119, 85, 0.12),
    0 4px 20px rgba(0, 0, 0, 0.15);
}

/* Subtle SVG paper grain overlay (CSS-only, no image asset needed) */
body::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 9999;
  opacity: 0.035;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
}

/* Sepia image filter for AIGC images */
.article-image {
  filter: grayscale(100%) contrast(1.1) sepia(30%);
}
```

---

## 5. Complete Tech Stack

### Core Stack (from scaffold):
- **React 19** + TypeScript
- **Vite 7.2.4** (build tool)
- **Tailwind CSS 3.4.19** (utility CSS)
- **Node.js 20**

### Additional Dependencies:
```bash
# Page flip effect
npm install react-pageflip

# Routing (lightweight)
npm install wouter

# State management (lightweight)
npm install zustand

# Animation
npm install gsap

# View Transitions API polyfill/support
npm install view-transitions-polyfill

# Typography plugin
npm install -D @tailwindcss/typography
```

### Image/Video Handling:
- CSS filters to make AIGC images look like 1900s engravings:
  `filter: grayscale(100%) contrast(1.2) sepia(25%) brightness(0.95);`
- Lazy loading with `loading="lazy"` and Intersection Observer
- React.lazy() for code-splitting page components

### Performance Strategy:
- **Code splitting**: Each newspaper page loaded on-demand via React.lazy()
- **Image lazy loading**: Only load images when page becomes visible
- **Page-flip virtualization**: Only renders visible + adjacent pages
- **Bundle estimate**: ~150KB gzipped (within 200KB Google recommendation)
- **50 articles**: Split across ~12-15 newspaper pages, each page has 3-5 articles

### State Management:
- Zustand for: current page, article data, category filter, navigation history
- React Context NOT needed — Zustand is simpler and lighter

### Routing:
- Wouter for: direct URL access to specific pages/sections
- HashRouter mode for static deployment compatibility

---

## 6. 2025-2026 Trending CSS Features to Use

- **`text-wrap: pretty`** — Better headline line breaks (Chrome 117+, Firefox 132+)
- **CSS `@container` queries** — Component-level responsive design
- **CSS nesting** (native, no preprocessor needed)
- **`@starting-style` + `transition-behavior: allow-discrete`** — Entry animations
- **View Transitions API** — Native smooth page transitions
- **`initial-letter`** — Proper drop cap support (drop-cap effect)

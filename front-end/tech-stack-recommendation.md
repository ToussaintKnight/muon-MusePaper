# Definitive Tech Stack: 1900s British Digital Newspaper (2026)

## Executive Summary: The Verdict

> **Stick with React 19. Upgrade Vite to v8. Upgrade Tailwind to v4.1. Use GSAP + Motion for animations. Use Wouter for routing. Use Zustand for state. Use react-pageflip for the page-turn effect.**

The user asked about Preact — we evaluated it thoroughly and decided **against** it. React 19 is the correct choice for this project.

---

## 1. FRAMEWORK: React 19 (NOT Preact)

### The Preact Question

| Factor | Preact 10.27.2 | React 19 |
|--------|---------------|----------|
| Bundle Size | 4.7KB gzipped | ~42KB gzipped |
| React 19 Compatibility | ~99% via `preact/compat` | Native |
| Ecosystem | Uses React libs via compat | Full native ecosystem |
| Vite Plugin | `@preact/preset-vite` | `@vitejs/plugin-react` |
| page-flip compat | Works (react-pageflip uses React refs) | Native |

### Why NOT Preact

1. **Bundle size savings are negligible**: The page-flip library alone is ~50KB. GSAP is ~30KB. Saving 37KB by switching to Preact is meaningless when your animation libraries dwarf that.

2. **Compat layer complexity**: Preact requires aliasing `react` → `preact/compat` via npm or bundler config. This adds friction and subtle edge cases, especially with React 19 features.

3. **The user wants "trendy 2026 tech"**: React 19 IS the trendy 2026 standard. Preact is a niche optimization choice for ultra-lightweight apps. A digital newspaper with page-flip animations and scroll effects is not an ultra-lightweight app.

4. **page-flip library uses React refs**: `react-pageflip` relies on `forwardRef` and React-specific patterns. While Preact/compat supports refs, any deviation creates hard-to-debug issues.

### npm install
```bash
npm install react@^19.0.0 react-dom@^19.0.0
npm install -D @types/react@^19.0.0 @types/react-dom@^19.0.0
```

### Recommended Vite Plugin Update
```bash
npm install -D @vitejs/plugin-react@^4.4.0
```

---

## 2. BUILD TOOL: Vite 8.0.14 (Major Upgrade)

### Status: CRITICAL UPGRADE NEEDED

The scaffold uses Vite v7.2.4. Vite 8 shipped March 2026 and is a game-changer:

| Feature | Vite 7.2.4 (Scaffold) | Vite 8.0.14 (Latest) |
|---------|----------------------|----------------------|
| Production Bundler | Rollup (JS) | **Rolldown (Rust)** |
| Build Speed | Baseline | **3-10x faster** |
| HMR Speed | Fast | **24x faster than Webpack** |
| Dev Server | esbuild | **Oxc (Rust)** |
| Vite DevTools | No | **Yes** |

### Why Upgrade
- Rolldown 1.0 (Rust-based Rollup replacement) = dramatically faster production builds
- Oxc transformer replaces esbuild for JS transforms
- Vite DevTools for performance debugging
- 115M+ weekly npm downloads — the undisputed 2026 build tool king

### npm install
```bash
npm install -D vite@^8.0.14
```

### vite.config.ts (Updated)
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tsconfigPaths from 'vite-tsconfig-paths';

export default defineConfig({
  plugins: [react(), tsconfigPaths()],
  build: {
    target: 'esnext',
    rollupOptions: {
      output: {
        manualChunks: {
          'page-flip': ['react-pageflip'],
          'gsap': ['gsap'],
          'motion': ['motion'],
        },
      },
    },
  },
});
```

---

## 3. CSS FRAMEWORK: Tailwind CSS v4.1 (Major Upgrade)

### Status: CRITICAL UPGRADE NEEDED

The scaffold uses Tailwind v3.4.19. Tailwind v4.0 released January 2025, v4.1 released April 2025. This is the biggest Tailwind update ever:

| Feature | Tailwind v3.4.19 (Scaffold) | Tailwind v4.1 (Latest) |
|---------|---------------------------|----------------------|
| Engine | JavaScript (PostCSS) | **Rust (Oxide/Lightning CSS)** |
| Build Speed | ~500ms | **~50ms (10x faster)** |
| Configuration | `tailwind.config.js` | **CSS-first (`@theme`)** |
| Container Queries | Plugin required | **Built-in** |
| `@starting-style` | Not supported | **Built-in** |
| Setup | 3 files, multiple deps | **`@import "tailwindcss"`** |

### Setup (No config file needed!)
```css
/* src/index.css — ONE LINE */
@import "tailwindcss";

/* Your newspaper theme */
@theme {
  --color-parchment: #f5f0e1;
  --color-ink: #2c1810;
  --color-newsprint: #e8dcc8;
  --font-headline: "Playfair Display", serif;
  --font-body: "EB Garamond", serif;
}
```

### Plugins to Add
```bash
npm install -D @tailwindcss/typography@^0.5.16
```

### npm install
```bash
npm install -D tailwindcss@^4.1.0 @tailwindcss/vite@^4.1.0
```

### Why Tailwind Typography Plugin
The `@tailwindcss/typography` plugin gives you `prose` classes for beautiful article typography — essential for a newspaper:
```html
<article class="prose prose-lg font-body text-ink">
  <!-- Beautifully styled article content -->
</article>
```

---

## 4. ANIMATION: GSAP + Motion v12 (Framer Motion)

### The 2026 Animation Stack

| Library | Role | Bundle Size | npm Package |
|---------|------|-------------|-------------|
| **GSAP** (with ScrollTrigger) | Scroll-driven reveals, timeline sequences, text animations | ~30KB (core + ScrollTrigger) | `gsap` |
| **Motion v12** (ex-Framer Motion) | UI animations, layout transitions, entrance effects | ~18KB (tree-shaken) | `motion` |
| **View Transitions API** | Native page transitions | 0KB (browser API) | Native |
| **CSS `@starting-style`** | Entry animations without JS | 0KB | Native CSS |

### Why This Combo

**GSAP** = the undisputed king of scroll-driven and complex animations. Its ScrollTrigger plugin is the gold standard for scroll-linked reveals — perfect for newspaper sections appearing as you scroll. All plugins are free since v3.12. Used by Disney, Google, Apple.

**Motion v12** (renamed from Framer Motion in 2025) = the best React-native animation library for UI interactions. Declarative API, `AnimatePresence` for exit animations, `whileInView` for viewport-triggered effects. Hardware-accelerated. React 19 compatible.

**View Transitions API** = the hottest 2025-2026 browser feature. Native page transitions with zero library overhead. Supported in Chrome, Edge, and Safari. Cross-document support landed in 2025.

### npm install
```bash
npm install gsap@^3.12.7
npm install motion@^12.0.0
```

### Architecture
```
Scroll-triggered section reveals  → GSAP + ScrollTrigger
Page entrance animations           → Motion (whileInView)
Page-to-page transitions           → View Transitions API
Hover/click micro-interactions     → Motion (whileHover, whileTap)
Text headline animations           → GSAP SplitText (free)
```

---

## 5. STATE MANAGEMENT: Zustand

### Why Zustand (2026's #1 Choice)

| Metric | Zustand | React Context | Redux Toolkit |
|--------|---------|--------------|---------------|
| Weekly Downloads | 72.9M (2026) | Built-in | 37.1M |
| Bundle Size | ~1KB | 0KB | ~15KB |
| Boilerplate | None | Medium | High |
| Provider needed | No | Yes | Yes |
| DevTools | Redux DevTools | React DevTools | Redux DevTools |
| TypeScript | Excellent | Good | Good |

For 50 articles with category filtering and page navigation: **Zustand**.

React Context would work for this scale, but Zustand gives you:
- Cleaner component code (no Provider wrappers)
- Better performance (no context re-render cascade)
- Redux DevTools integration for debugging
- Future-proof if state grows beyond 50 articles

### npm install
```bash
npm install zustand@^5.0.0
```

### Store Pattern
```typescript
import { create } from 'zustand';

interface Article {
  id: string;
  title: string;
  category: string;
  content: string;
  image: string;
  date: string;
  pageNumber: number;
}

interface NewspaperStore {
  articles: Article[];
  currentPage: number;
  selectedCategory: string | null;
  setCurrentPage: (page: number) => void;
  setCategory: (category: string | null) => void;
  getArticlesByCategory: () => Article[];
}

export const useNewspaperStore = create<NewspaperStore>((set, get) => ({
  articles: [], // loaded from JSON
  currentPage: 0,
  selectedCategory: null,
  setCurrentPage: (page) => set({ currentPage: page }),
  setCategory: (category) => set({ selectedCategory: category, currentPage: 0 }),
  getArticlesByCategory: () => {
    const { articles, selectedCategory } = get();
    return selectedCategory
      ? articles.filter((a) => a.category === selectedCategory)
      : articles;
  },
}));
```

---

## 6. ROUTING: Wouter v3.7

### Why Wouter

| Router | Bundle Size | Type-safe | Complexity |
|--------|------------|-----------|------------|
| React Router v7 | ~18KB | Partial | High |
| **Wouter v3.7** | **~2.1KB** | **Yes** | **Minimal** |
| TanStack Router | ~12KB | 100% | Medium |

For a newspaper site with ~5-10 routes (front page, article, category, about):
**Wouter** is the perfect fit. It's tiny, hooks-based, and has zero boilerplate.

TanStack Router is excellent but overkill for this project. React Router v7 is heavy and framework-oriented.

### npm install
```bash
npm install wouter@^3.7.0
```

### Usage
```typescript
import { Route, Switch, Link } from 'wouter';

function App() {
  return (
    <Switch>
      <Route path="/" component={FrontPage} />
      <Route path="/article/:id" component={ArticlePage} />
      <Route path="/category/:name" component={CategoryPage} />
      <Route path="/flipbook" component={FlipBookView} />
      <Route>404: Page Not Found</Route>
    </Switch>
  );
}
```

---

## 7. PAGE-FLIP LIBRARY: react-pageflip v2.0.3

### Why react-pageflip

`react-pageflip` is the React wrapper for **StPageFlip** — the best page-turning library in 2026:

| Feature | react-pageflip |
|---------|---------------|
| Underlying engine | StPageFlip |
| Bundle Size | ~50KB (StPageFlip core) |
| Dependencies | Zero |
| Mobile Touch | Yes (swipe gestures) |
| HTML Content | Yes (not just images) |
| Hard/Soft pages | Both |
| Portrait Mode | Yes |
| React Wrapper | Yes (`react-pageflip`) |

### npm install
```bash
npm install react-pageflip@^2.0.3
```

### Code-Splitting (IMPORTANT)
The page-flip library is heavy (~50KB). Code-split it:
```typescript
import { lazy, Suspense } from 'react';

const HTMLFlipBook = lazy(() => import('react-pageflip'));

// Use with Suspense
<Suspense fallback={<NewspaperSkeleton />}>
  <HTMLFlipBook width={550} height={733}>
    {pages.map((page) => (
      <NewspaperPage key={page.number} data={page} />
    ))}
  </HTMLFlipBook>
</Suspense>
```

---

## 8. IMAGES & PERFORMANCE

### Lazy Loading (Native — No Library Needed)
```html
<!-- Native lazy loading — works in all modern browsers -->
<img src="/article-image.jpg" loading="lazy" alt="..." />

<!-- With 1900s newspaper CSS filter effect -->
<img 
  src="/article-image.jpg" 
  loading="lazy"
  class="sepia-[0.3] contrast-125 grayscale-[0.2]"
  alt="Historical photograph"
/>
```

### CSS Filters for 1900s Photo Effect
```css
.newspaper-image {
  filter: sepia(0.4) contrast(1.2) grayscale(0.3) brightness(0.95);
  /* Makes modern photos look like 1900s engravings */
}
```

### Performance Strategy
| Concern | Decision | Rationale |
|---------|----------|-----------|
| 50 articles — virtualization? | **Not needed** | 50 DOM nodes is trivial |
| Code splitting? | **Yes** | Split page-flip library, article pages |
| Image lazy loading? | **Native `loading="lazy"`** | Built into browsers |
| Image optimization? | **Build-time** | Let Vite handle asset optimization |
| Bundle size target? | **<200KB initial** | Well within budget |

### Code Splitting Setup
```typescript
// Routes are lazy-loaded
const FrontPage = lazy(() => import('./pages/FrontPage'));
const ArticlePage = lazy(() => import('./pages/ArticlePage'));
const FlipBookView = lazy(() => import('./pages/FlipBookView'));
```

---

## 9. TYPOGRAPHY & FONTS

### 1900s British Newspaper Font Stack
```bash
# No npm install needed — Google Fonts via CDN
```

```css
/* In your CSS / Tailwind theme */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=EB+Garamond:ital,wght@0,400;0,500;0,700;1,400&family=IM+Fell+English:ital@0;1&display=swap');

@theme {
  --font-headline: "Playfair Display", serif;      /* Bold headlines */
  --font-body: "EB Garamond", serif;                /* Article body text */
  --font-decorative: "IM Fell English", serif;      /* Old-style accents */
}
```

### Tailwind Typography Plugin Classes
```html
<article class="prose prose-lg prose-stone font-body">
  <h1 class="font-headline text-4xl font-black tracking-tight">
    {{ Headline }}
  </h1>
  <p class="lead">{{ Lead paragraph }}</p>
  <p>{{ Body text }}</p>
</article>
```

---

## 10. COMPLETE NPM INSTALL COMMAND

### All Dependencies (One Command)
```bash
# CORE FRAMEWORK
npm install react@^19.0.0 react-dom@^19.0.0

# STATE MANAGEMENT
npm install zustand@^5.0.0

# ROUTING
npm install wouter@^3.7.0

# ANIMATION
npm install gsap@^3.12.7 motion@^12.0.0

# PAGE FLIP
npm install react-pageflip@^2.0.3

# DEV DEPENDENCIES
npm install -D vite@^8.0.14 @vitejs/plugin-react@^4.4.0
npm install -D tailwindcss@^4.1.0 @tailwindcss/vite@^4.1.0
npm install -D @tailwindcss/typography@^0.5.16
npm install -D typescript@^5.7.0 @types/react@^19.0.0 @types/react-dom@^19.0.0
npm install -D vite-tsconfig-paths@^5.0.0
```

---

## 11. PROJECT ARCHITECTURE

```
newspaper-project/
├── public/
│   ├── articles/              # Article content JSON
│   │   ├── issue-001.json
│   │   └── issue-002.json
│   └── images/                # Historical images
│       ├── engravings/
│       └── photographs/
│
├── src/
│   ├── main.tsx               # Entry point
│   ├── App.tsx                # Root with routing
│   ├── index.css              # Tailwind v4 import + theme
│   │
│   ├── pages/                 # Route-level pages (lazy-loaded)
│   │   ├── FrontPage.tsx
│   │   ├── ArticlePage.tsx
│   │   ├── FlipBookView.tsx   # Page-flip mode
│   │   └── CategoryPage.tsx
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Masthead.tsx       # Newspaper header
│   │   │   ├── Navigation.tsx
│   │   │   ├── Footer.tsx
│   │   │   └── PageLayout.tsx
│   │   ├── article/
│   │   │   ├── ArticleCard.tsx
│   │   │   ├── ArticleBody.tsx    # Uses prose typography
│   │   │   └── Headline.tsx
│   │   ├── flipbook/
│   │   │   ├── NewspaperPage.tsx  # Single page content
│   │   │   └── PageFlipWrapper.tsx # react-pageflip container
│   │   └── ui/
│   │       ├── Separator.tsx      # Decorative dividers
│   │       ├── DropCap.tsx        # First-letter styling
│   │       └── DateLine.tsx
│   │
│   ├── hooks/
│   │   ├── useScrollReveal.ts     # GSAP ScrollTrigger hook
│   │   ├── useViewTransition.ts   # View Transitions API hook
│   │   └── useNewspaperData.ts    # Data loading hook
│   │
│   ├── store/
│   │   └── useNewspaperStore.ts   # Zustand store
│   │
│   ├── types/
│   │   └── article.ts
│   │
│   └── lib/
│       ├── gsap.ts                # GSAP plugin registration
│       └── utils.ts
│
├── vite.config.ts             # Vite 8 + Rolldown config
├── tsconfig.json
├── tsconfig.app.json
├── package.json
└── index.html
```

---

## 12. ARCHITECTURE DIAGRAM (Data Flow)

```
┌─────────────────────────────────────────────────────────────┐
│                        BROWSER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  FrontPage   │  │  FlipBookView│  │   ArticlePage    │  │
│  │  (List view) │  │ (Page-flip)  │  │  (Single article)│  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
│         │                  │                    │            │
│  ┌──────▼──────────────────▼────────────────────▼─────────┐  │
│  │              Wouter Router (~2KB)                       │  │
│  └──────┬──────────────────┬────────────────────┬─────────┘  │
│         │                  │                    │            │
│  ┌──────▼──────┐  ┌────────▼────────┐  ┌───────▼────────┐  │
│  │  View Trans │  │  react-pageflip │  │    Motion      │  │
│  │  API (page) │  │  (page-turn FX) │  │ (UI animations)│  │
│  └──────┬──────┘  └────────┬────────┘  └───────┬────────┘  │
│         │                  │                    │            │
│  ┌──────▼──────────────────▼────────────────────▼─────────┐  │
│  │              React 19 + TypeScript                      │  │
│  └──────┬──────────────────┬────────────────────┬─────────┘  │
│         │                  │                    │            │
│  ┌──────▼──────┐  ┌────────▼────────┐  ┌───────▼────────┐  │
│  │   Zustand   │  │  GSAP + Scroll  │  │ Tailwind v4.1  │  │
│  │  (articles, │  │   (scroll FX)   │  │ (newspaper CSS)│  │
│  │   UI state) │  │                 │  │                │  │
│  └─────────────┘  └─────────────────┘  └────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Vite 8 + Rolldown (Rust)                │    │
│  │     (3-10x faster builds, code-splitting, HMR)       │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 13. KEY DECISIONS WITH PROS/CONS

### Decision 1: React 19 over Preact
| Pros | Cons |
|------|------|
| Full ecosystem compatibility | ~37KB larger bundle |
| Zero compat-layer friction | |
| React 19 features (Server Components ready) | |
| Better debugging experience | |
| **Industry standard 2026** | |

**Verdict**: The 37KB difference is meaningless with page-flip (~50KB) + GSAP (~30KB) in the bundle. React 19 wins.

---

### Decision 2: Vite 8 over Vite 7 (Scaffold)
| Pros | Cons |
|------|------|
| Rolldown: 3-10x faster production builds | Migration effort (minor) |
| Vite DevTools built-in | Node 20+ required |
| Latest ecosystem support | |
| Oxc transformer: faster than esbuild | |

**Verdict**: Upgrade is straightforward and high-impact. Do it.

---

### Decision 3: Tailwind v4.1 over v3.4.19 (Scaffold)
| Pros | Cons |
|------|------|
| 10x faster CSS builds (Rust engine) | v4 has different config patterns |
| Zero config needed | Some plugins may need updates |
| Built-in container queries | |
| CSS-first `@theme` approach | |
| `@starting-style` for entry animations | |

**Verdict**: The v4 upgrade is transformative. The CSS-first approach actually simplifies configuration.

---

### Decision 4: GSAP + Motion (dual library)
| Pros | Cons |
|------|------|
| Best tool for each job | Two animation libraries (~48KB combined) |
| GSAP: unmatched scroll animations | |
| Motion: unmatched React UI animations | |
| View Transitions API for free | |

**Verdict**: GSAP handles the heavy scroll-lifting. Motion handles React UI polish. The combination covers all animation needs.

---

### Decision 5: Wouter over React Router v7
| Pros | Cons |
|------|------|
| 2.1KB vs 18KB | Smaller ecosystem |
| Zero configuration | No nested route layouts (not needed here) |
| Hooks-based, modern API | |
| Perfect for 5-10 routes | |

**Verdict**: Wouter is the ideal lightweight router for a focused newspaper site. No need for React Router's complexity.

---

### Decision 6: Zustand over React Context
| Pros | Cons |
|------|------|
| No Provider wrapper needed | Another dependency (1KB) |
| No re-render cascade | |
| Redux DevTools integration | |
| Future-proof for state growth | |
| Cleaner component code | |

**Verdict**: For 50 articles, Context would work. Zustand's DX and future-proofing justify the 1KB.

---

## 14. 2025-2026 TRENDING FEATURES TO USE

### CSS `@starting-style` (Tailwind v4.1)
```css
/* Native entry animations without JS */
.newspaper-section {
  @starting-style {
    opacity: 0;
    transform: translateY(20px);
  }
  transition: opacity 0.5s, transform 0.5s;
}
```

### CSS `text-wrap: pretty`
```css
/* Prevents typographic orphans in headlines */
.headline {
  text-wrap: pretty;
}
```

### CSS `text-wrap: balance`
```css
/* Balanced multi-line headlines */
.subheadline {
  text-wrap: balance;
}
```

### CSS Container Queries (Tailwind v4.1 built-in)
```html
<!-- Responsive to CONTAINER size, not viewport -->
<div class="@container">
  <article class="flex flex-col @md:flex-row @lg:grid @lg:grid-cols-3">
    <!-- Responsive article layout -->
  </article>
</div>
```

### View Transitions API
```typescript
// Wrap route changes in startViewTransition
const navigateWithTransition = (callback: () => void) => {
  if (!document.startViewTransition) {
    callback();
    return;
  }
  document.startViewTransition(() => callback());
};
```

---

## 15. LIGHTHOUSE OPTIMIZATION TARGETS

| Metric | Target | Strategy |
|--------|--------|----------|
| **Performance** | 90+ | Code-split page-flip, lazy-load images, Vite 8 optimizations |
| **Accessibility** | 95+ | Semantic HTML, `text-wrap: pretty`, `prefers-reduced-motion` |
| **Best Practices** | 100 | HTTPS, modern browser APIs, no deprecated features |
| **SEO** | 100 | Semantic headings, meta tags, static JSON-LD |

### Critical Optimizations
```typescript
// 1. Lazy-load the heavy page-flip library
const FlipBookView = lazy(() => import('./pages/FlipBookView'));

// 2. Lazy-load images with native loading
<img src="..." loading="lazy" alt="..." />

// 3. Code-split routes
const FrontPage = lazy(() => import('./pages/FrontPage'));

// 4. Bundle splitting in vite.config.ts
manualChunks: {
  'page-flip': ['react-pageflip'],
  'gsap': ['gsap'],
  'motion': ['motion'],
}

// 5. Respect prefers-reduced-motion
const prefersReducedMotion = window.matchMedia(
  '(prefers-reduced-motion: reduce)'
).matches;
```

---

## 16. FINAL PACKAGE.JSON (Recommended)

```json
{
  "name": "1900s-digital-newspaper",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0"
  },
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "gsap": "^3.12.7",
    "motion": "^12.0.0",
    "react-pageflip": "^2.0.3",
    "wouter": "^3.7.0",
    "zustand": "^5.0.0"
  },
  "devDependencies": {
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "@vitejs/plugin-react": "^4.4.0",
    "@tailwindcss/vite": "^4.1.0",
    "@tailwindcss/typography": "^0.5.16",
    "tailwindcss": "^4.1.0",
    "typescript": "^5.7.0",
    "vite": "^8.0.14",
    "vite-tsconfig-paths": "^5.0.0"
  }
}
```

---

## Summary: The Definitive Stack

| Layer | Technology | Version | Bundle Size |
|-------|-----------|---------|-------------|
| **Framework** | React | v19.0.0 | ~42KB |
| **Build Tool** | Vite | v8.0.14 | Dev only |
| **CSS** | Tailwind CSS | v4.1.0 | ~0KB (purge) |
| **Typography** | @tailwindcss/typography | v0.5.16 | ~10KB |
| **Animations (Scroll)** | GSAP + ScrollTrigger | v3.12.7 | ~30KB |
| **Animations (UI)** | Motion (ex-Framer Motion) | v12.0.0 | ~18KB |
| **State** | Zustand | v5.0.0 | ~1KB |
| **Routing** | Wouter | v3.7.0 | ~2KB |
| **Page Flip** | react-pageflip | v2.0.3 | ~50KB |
| **Fonts** | Playfair Display + EB Garamond | Google Fonts | Variable |
| **Total JS (gzipped)** | | | **~153KB** |

**Well under the 200KB recommended budget.** The page-flip library is the largest single dependency, but it's the core feature — and it's code-split.

---

*Recommendation compiled June 2026. All versions are latest stable as of this date.*

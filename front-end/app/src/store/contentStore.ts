import { create } from 'zustand';

const API_BASE = 'http://localhost:8000';

export interface NewspaperArticle {
  id: string;
  headline: string;
  subheadline: string;
  byline: string;
  dateline: string;
  abstract: string;
  url: string;
  column_span: number;
  abstract_budget: number;
  image_theme: string;
  imageUrl?: string;
  section: string;
  score?: number;
}

export interface NewspaperPageData {
  page_number: number;
  layout_template: string;
  sections: { section: string; articles: NewspaperArticle[] }[];
}

export interface NewspaperIssue {
  issue_date: string;
  issue_number: number;
  pages: NewspaperPageData[];
  session_id: string;
}

interface NewspaperState {
  issue: NewspaperIssue | null;
  composedPages: NewspaperPageData[] | null;
  isLoading: boolean;
  isComposing: boolean;
  error: string | null;
  sessionId: string | null;
  clicks: Set<string>;
  tools: Set<string>;
  hasUnsavedChanges: boolean;

  fetchIssue: () => Promise<void>;
  clearError: () => void;
  setComposedPages: (pages: NewspaperPageData[]) => void;
  clickArticle: (itemId: string) => void;
  markTool: (itemId: string) => void;
  saveSession: () => Promise<{ success: boolean; message?: string }>;
}

async function fetchJSON(path: string, opts?: RequestInit) {
  const res = await fetch(API_BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export const useContentStore = create<NewspaperState>((set, get) => ({
  issue: null,
  composedPages: null,
  isLoading: false,
  isComposing: false,
  error: null,
  sessionId: null,
  clicks: new Set(),
  tools: new Set(),
  hasUnsavedChanges: false,

  async fetchIssue() {
    set({ isLoading: true, error: null });
    try {
      const issue: NewspaperIssue = await fetchJSON('/api/newspaper/issue');
      set({ issue, sessionId: issue.session_id, isLoading: false, error: null, clicks: new Set(), tools: new Set(), hasUnsavedChanges: false });
    } catch (e) {
      console.error('Failed to fetch newspaper issue:', e);
      set({ isLoading: false, error: String(e) });
    }
  },

  clearError() {
    set({ error: null });
  },

  setComposedPages(pages) {
    set({ composedPages: pages, isComposing: false });
  },

  clickArticle(itemId: string) {
    const { clicks, sessionId } = get();
    if (clicks.has(itemId)) return;
    clicks.add(itemId);
    // Also notify backend
    if (sessionId) {
      fetchJSON('/api/newspaper/click', {
        method: 'POST',
        body: JSON.stringify({ session_id: sessionId, item_id: itemId }),
      }).catch(() => {});
    }
    set({ clicks: new Set(clicks), hasUnsavedChanges: true });
  },

  markTool(itemId: string) {
    const { tools } = get();
    tools.add(itemId);
    set({ tools: new Set(tools), hasUnsavedChanges: true });
  },

  async saveSession() {
    const { sessionId, clicks, tools } = get();
    if (!sessionId) return { success: false, message: 'No active session' };

    try {
      const result = await fetchJSON('/api/session/save', {
        method: 'POST',
        body: JSON.stringify({
          session_id: sessionId,
          clicks: Array.from(clicks),
          ignores: [],
          tools: Array.from(tools),
        }),
      });
      set({ hasUnsavedChanges: false, clicks: new Set(), tools: new Set() });
      return { success: true, ...result };
    } catch (e) {
      return { success: false, message: String(e) };
    }
  },
}));

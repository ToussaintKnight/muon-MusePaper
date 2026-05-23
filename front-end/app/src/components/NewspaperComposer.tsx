import { useEffect, useState } from 'react';
import { useContentStore, type NewspaperIssue, type NewspaperPageData } from '@/store/contentStore';
import { measureSlots } from '@/lib/pretextLayout';
import { auditPages, refineLayout, type ComposedPage } from '@/agents/auditAgent';
import { placeImages } from '@/agents/imageAgent';
import NewspaperRenderer from './NewspaperRenderer';
import FinishOverlay from './FinishOverlay';

function transformToComposedPages(issue: NewspaperIssue): ComposedPage[] {
  return issue.pages.map((page) => ({
    pageNumber: page.page_number,
    layoutTemplate: page.layout_template,
    sections: page.sections.map((sec) => ({
      section: sec.section,
      articles: sec.articles.map((article) => ({
        id: article.id,
        headline: article.headline,
        subheadline: article.subheadline,
        byline: article.byline,
        dateline: article.dateline,
        abstract: article.abstract,
        url: article.url,
        columnSpan: article.column_span,
        measuredHeight: 0,
        lineCount: 0,
        imageTheme: article.image_theme,
        section: article.section,
        score: article.score,
      })),
    })),
  }));
}

function extractTextSlots(pages: ComposedPage[]): { id: string; text: string; font: string; columnWidth: number; lineHeight: number; budgetHeight: number }[] {
  const slots: { id: string; text: string; font: string; columnWidth: number; lineHeight: number; budgetHeight: number }[] = [];
  pages.forEach((page) => {
    page.sections.forEach((sec) => {
      sec.articles.forEach((article) => {
        const colWidth = article.columnSpan >= 3 ? 1200 : article.columnSpan === 2 ? 700 : 320;
        const lineHeight = 24;
        const budgetHeight = article.abstract.split(' ').length * (lineHeight * 0.6);
        slots.push({
          id: article.id,
          text: article.abstract,
          font: "16px 'EB Garamond', serif",
          columnWidth: colWidth,
          lineHeight,
          budgetHeight: Math.max(budgetHeight, 100),
        });
      });
    });
  });
  return slots;
}

export default function NewspaperComposer() {
  const { issue, composedPages, setComposedPages, isLoading, error, fetchIssue, clearError } = useContentStore();
  const [showFinish, setShowFinish] = useState(false);

  useEffect(() => {
    if (!issue && !isLoading && !error) {
      fetchIssue();
    }
  }, [issue, isLoading, error, fetchIssue]);

  useEffect(() => {
    if (!issue || composedPages) return;

    async function compose() {
      if (!issue) return;
      // 1. Create initial composed pages
      let pages = transformToComposedPages(issue);

      // 2. Pretext measurement (run once, refinement is lightweight)
      const slots = extractTextSlots(pages);
      const measured = measureSlots(slots);
      const measuredMap = new Map(measured.map((m) => [m.id, m]));

      // Apply measured heights
      pages = pages.map((page) => ({
        ...page,
        sections: page.sections.map((sec) => ({
          ...sec,
          articles: sec.articles.map((article) => {
            const m = measuredMap.get(article.id);
            return {
              ...article,
              measuredHeight: m?.measuredHeight ?? 0,
              lineCount: m?.lineCount ?? 0,
            };
          }),
        })),
      }));

      // 3. Audit + refine (max 2 passes)
      for (let pass = 0; pass < 2; pass++) {
        const audits = auditPages(pages);
        if (audits.every((a) => a.coverageRatio >= 0.5 && a.coverageRatio <= 0.75)) {
          break;
        }
        pages = refineLayout(pages, audits);
      }

      // 4. Image placement
      pages = pages.map((page) => ({
        ...page,
        sections: page.sections.map((sec) => ({
          ...sec,
          articles: placeImages(sec.articles),
        })),
      }));

      // 5. Flatten back to NewspaperPageData format
      const finalPages: NewspaperPageData[] = pages.map((page) => ({
        page_number: page.pageNumber,
        layout_template: page.layoutTemplate,
        sections: page.sections.map((sec) => ({
          section: sec.section,
          articles: sec.articles.map((a) => ({
            id: a.id,
            headline: a.headline,
            subheadline: a.subheadline,
            byline: a.byline,
            dateline: a.dateline,
            abstract: a.abstract,
            url: a.url,
            column_span: a.columnSpan,
            abstract_budget: 0,
            image_theme: a.imageTheme,
            imageUrl: a.imageUrl,
            section: a.section,
            score: a.score,
          })),
        })),
      }));

      setComposedPages(finalPages);
    }

    compose();
  }, [issue, composedPages, setComposedPages]);

  if (error) {
    return (
      <div className="min-h-[100dvh] bg-paper flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="font-headline text-ink text-2xl mb-4">The Presses Have Stopped</div>
          <div className="font-caption text-ink-faded italic mb-6">{error}</div>
          <button
            onClick={() => { clearError(); fetchIssue(); }}
            className="font-body text-xs small-caps tracking-[0.15em] border border-ink px-6 py-3 hover:bg-ink hover:text-paper transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="min-h-[100dvh] bg-paper flex items-center justify-center">
        <div className="text-center">
          <div className="font-headline text-ink text-2xl mb-4">Preparing Today's Edition</div>
          <div className="font-caption text-ink-faded italic">The presses are running...</div>
        </div>
      </div>
    );
  }

  if (!composedPages) {
    return (
      <div className="min-h-[100dvh] bg-paper flex items-center justify-center">
        <div className="text-center">
          <div className="font-headline text-ink text-2xl mb-4">Composing Pages</div>
          <div className="font-caption text-ink-faded italic">Measuring type and placing engravings...</div>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Fixed "Done for Today" button */}
      <div className="fixed bottom-6 right-6 z-50">
        <button
          onClick={() => setShowFinish(true)}
          className="font-headline text-xs small-caps tracking-[0.2em] bg-ink text-paper px-6 py-3 border border-ink shadow-lg hover:bg-paper hover:text-ink transition-colors"
        >
          Done for Today
        </button>
      </div>

      <NewspaperRenderer pages={composedPages} issueDate={issue?.issue_date} issueNumber={issue?.issue_number} />

      {showFinish && <FinishOverlay onClose={() => setShowFinish(false)} />}
    </>
  );
}

export interface PageAudit {
  pageNumber: number;
  textArea: number;
  imageArea: number;
  totalArea: number;
  coverageRatio: number;
}

export interface ComposedArticle {
  id: string;
  headline: string;
  subheadline: string;
  byline: string;
  dateline: string;
  abstract: string;
  url: string;
  columnSpan: number;
  measuredHeight: number;
  lineCount: number;
  imageTheme: string;
  imageUrl?: string;
  section: string;
  score?: number;
}

export interface ComposedPage {
  pageNumber: number;
  layoutTemplate: string;
  sections: { section: string; articles: ComposedArticle[] }[];
}

export function auditPages(pages: ComposedPage[]): PageAudit[] {
  return pages.map((page) => {
    const allArticles = page.sections.flatMap((s) => s.articles);
    const textArea = allArticles.reduce(
      (sum, a) => sum + a.measuredHeight * (a.columnSpan * 200),
      0
    );
    const imageArea = allArticles.filter((a) => a.imageUrl).length * 150 * 200;
    const totalArea = Math.max(1, textArea + imageArea);
    return {
      pageNumber: page.pageNumber,
      textArea,
      imageArea,
      totalArea,
      coverageRatio: textArea / totalArea,
    };
  });
}

export function refineLayout(
  pages: ComposedPage[],
  audits: PageAudit[],
  targetMin: number = 0.55,
  targetMax: number = 0.65
): ComposedPage[] {
  return pages.map((page, idx) => {
    const audit = audits[idx];
    if (!audit) return page;

    const needsMoreText = audit.coverageRatio < targetMin;
    const needsLessText = audit.coverageRatio > targetMax;

    if (!needsMoreText && !needsLessText) return page;

    const refinedSections = page.sections.map((sec) => ({
      ...sec,
      articles: sec.articles.map((article) => {
        if (needsMoreText && article.columnSpan === 1) {
          // Expand compact articles
          const extraWords = Math.floor(article.abstract.split(' ').length * 0.3);
          return {
            ...article,
            abstract: article.abstract + ' '.repeat(extraWords), // placeholder expansion
          };
        }
        if (needsLessText && article.columnSpan === 3) {
          // Shrink lead articles
          const words = article.abstract.split(' ');
          const targetWords = Math.floor(words.length * 0.8);
          return {
            ...article,
            abstract: words.slice(0, targetWords).join(' ') + '.',
          };
        }
        return article;
      }),
    }));

    return { ...page, sections: refinedSections };
  });
}

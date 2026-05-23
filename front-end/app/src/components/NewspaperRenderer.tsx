import type { NewspaperPageData } from '@/store/contentStore';
import ArticleCard from './ArticleCard';
import Masthead from './Masthead';

interface NewspaperRendererProps {
  pages: NewspaperPageData[];
  issueDate?: string;
  issueNumber?: number;
}

function PageLayout({ page }: { page: NewspaperPageData }) {
  const isFront = page.layout_template === 'front_page';
  const allArticles = page.sections.flatMap((s) => s.articles);

  if (isFront) {
    const lead = allArticles[0];
    const secondary = allArticles.slice(1, Math.min(5, allArticles.length));
    const bottom = allArticles.slice(5);

    return (
      <div className="newspaper-page">
        <Masthead />

        {/* Latest Intelligence bar */}
        <div className="my-6">
          <div className="border-t-2 border-ink" />
          <div className="border-b border-ink py-2 flex items-center justify-center">
            <span className="font-headline text-ink text-xs md:text-sm small-caps tracking-[0.15em] font-bold">
              Latest Intelligence
            </span>
          </div>
        </div>

        {/* Secondary headlines row */}
        {secondary.length > 0 && (
          <section className="mb-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-x-gutter gap-y-4">
              {secondary.map((article) => (
                <div key={article.id} className="lg:border-r border-rule lg:pr-gutter last:border-r-0">
                  <ArticleCard article={article} />
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Decorative rule */}
        <div className="my-6">
          <div className="border-t-2 border-ink mb-0.5" />
          <div className="border-t border-rule" />
        </div>

        {/* Lead article */}
        {lead && (
          <section className="mb-8">
            <ArticleCard article={lead} />
          </section>
        )}

        {/* Bottom row */}
        {bottom.length > 0 && (
          <section className="mb-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-x-gutter gap-y-4">
              {bottom.map((article) => (
                <div key={article.id} className="md:border-r border-rule md:pr-gutter last:border-r-0">
                  <ArticleCard article={article} />
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    );
  }

  // Section spread layout
  return (
    <div className="newspaper-page">
      {page.sections.map((sec) => (
        <div key={sec.section} className="mb-12">
          {/* Section header */}
          <div className="mb-6">
            <div className="border-t-2 border-ink mb-2" />
            <h2 className="font-headline text-ink text-2xl md:text-3xl font-black uppercase text-center tracking-tight">
              {sec.section === 'science' && 'Science & Industry'}
              {sec.section === 'commerce' && 'Commerce & Trade'}
              {sec.section === 'arts' && 'Arts & Letters'}
              {sec.section === 'society' && 'Society & Fashion'}
              {sec.section === 'foreign' && 'Foreign Affairs'}
              {sec.section === 'classifieds' && 'Notices & Advertisements'}
              {sec.section === 'front' && 'Front Page'}
              {!['science', 'commerce', 'arts', 'society', 'foreign', 'classifieds', 'front'].includes(sec.section) && sec.section}
            </h2>
            <div className="border-b border-ink mt-2" />
          </div>

          {/* Articles grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-x-gutter gap-y-6">
            {sec.articles.map((article) => (
              <div
                key={article.id}
                className={`
                  ${article.column_span >= 3 ? 'md:col-span-3' : ''}
                  ${article.column_span === 2 ? 'md:col-span-2' : ''}
                  ${article.column_span === 1 ? 'md:col-span-1' : ''}
                  ${article.column_span >= 2 ? 'md:border-r border-rule md:pr-gutter last:border-r-0' : ''}
                `}
              >
                <ArticleCard article={article} />
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

export default function NewspaperRenderer({ pages, issueDate }: NewspaperRendererProps) {
  return (
    <div className="bg-paper paper-grain min-h-[100dvh]">
      <div className="max-w-[1400px] mx-auto px-4 md:px-page-margin pb-12">
        {pages.map((page) => (
          <div
            key={page.page_number}
            className="mb-16 pb-16 border-b-2 border-ink last:border-b-0"
          >
            {/* Page number */}
            <div className="flex justify-between items-center mb-4 text-[10px] font-caption text-ink-faded tracking-widest uppercase">
              <span>Page {page.page_number}</span>
              <span>{issueDate ? new Date(issueDate).toLocaleDateString('en-GB', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) : ''}</span>
            </div>

            <PageLayout page={page} />
          </div>
        ))}
      </div>
    </div>
  );
}

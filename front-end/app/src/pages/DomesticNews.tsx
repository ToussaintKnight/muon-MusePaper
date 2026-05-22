import Masthead from '@/components/Masthead';
import SectionHeader from '@/components/SectionHeader';
import NewspaperPage from '@/components/NewspaperPage';
import EngravingImage from '@/components/EngravingImage';
import { useContentStore } from '@/store/contentStore';

const sidebarHeadlines = [
  'Suffragette Demonstration at Hyde Park',
  'New Workmen\'s Compensation Act Takes Effect',
  'Liverpool Dock Strike Ends &mdash; Wages Restored',
  'Scottish Universities Expansion Fund Launched',
  'Birmingham Electrical Tramway Opens',
  'Wales Coal Output Reaches Record High',
];

const leaderText =
  'British industry stands at a crossroads. The twentieth century dawns with promise, yet the signs of challenge are everywhere apparent. American manufacturing grows apace, German chemical and electrical industries threaten our long-held supremacy, and even the workshops of the Empire\'s dominions begin to compete with the mother country.\n\nThe Government must seize this moment to invest in technical education, to modernise our factories, and to ensure that British goods remain the standard of excellence the world over. The Manchester Ship Canal and the Central London Railway demonstrate what British engineering can achieve when vision and capital are united.\n\nWe call upon the Board of Trade, the Chambers of Commerce, and the manufacturing interests of the nation to form a concerted plan of industrial development. The alternative is gradual decline, as other nations surpass us in the very fields we pioneered.\n\nThe time for decisive action is upon us, and the Chronicle pledges its full support to any measure that shall advance the cause of British manufacture.';

export default function DomesticNews() {
  const { getArticlesByCategory } = useContentStore();
  const articles = getArticlesByCategory('domestic');

  const parliament = articles[0];
  const article2 = articles[1];
  const article3 = articles[2];
  const article4 = articles[3];
  const article5 = articles[4];

  const renderArticleBody = (
    body: string,
    colClass: string,
    size: 'base' | 'sm' = 'base'
  ) => (
    <div
      className={`column-rule font-body text-ink leading-relaxed body-text ${colClass} ${size === 'sm' ? 'text-sm' : 'text-base'}`}
    >
      {body.split('\n\n').map((paragraph, idx) => (
        <p key={idx} className={idx === 0 ? 'drop-cap mb-3' : 'mb-3'}>
          {paragraph}
        </p>
      ))}
    </div>
  );

  return (
    <NewspaperPage>
      <Masthead />
      <SectionHeader
        title="DOMESTIC INTELLIGENCE"
        subtitle="PARLIAMENTARY PROCEEDINGS &middot; SOCIAL MOVEMENTS &middot; INDUSTRIAL AFFAIRS &middot; THE PROVINCES"
      />

      {/* ──────── TOP ROW: Parliament (3) + Article 2 (1) + Sidebar (1) ──────── */}
      <section className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-x-6 gap-y-8">
        {/* Parliamentary Report — 3 columns */}
        <article className="lg:col-span-3 md:col-span-2 break-inside-avoid">
          <h2 className="font-headline text-ink text-xl md:text-2xl lg:text-[28px] font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
            {parliament.headline}
          </h2>
          {parliament.subheadline && (
            <p className="font-headline text-ink-light text-base md:text-lg italic leading-snug mb-2">
              {parliament.subheadline}
            </p>
          )}
          <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mb-3">
            {parliament.dateline}
          </p>
          {parliament.image && (
            <EngravingImage
              src={`/${parliament.image}`}
              alt={parliament.headline}
              caption={parliament.caption}
            />
          )}
          {renderArticleBody(parliament.body, 'columns-2 lg:columns-3 gap-4')}
          <p className="font-body text-ink-light text-xs small-caps tracking-[0.1em] text-right mt-3">
            {parliament.byline}
          </p>
        </article>

        {/* Article 2 — single column */}
        <article className="lg:col-span-1 md:col-span-1 break-inside-avoid border-t lg:border-t-0 md:border-t-0 border-rule pt-4 lg:pt-0">
          <h3 className="font-headline text-ink text-lg md:text-xl font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
            {article2.headline}
          </h3>
          <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mb-2">
            {article2.dateline}
          </p>
          {renderArticleBody(article2.body, 'columns-1', 'sm')}
          <p className="font-body text-ink-light text-[10px] small-caps tracking-[0.1em] text-right mt-2">
            {article2.byline}
          </p>
        </article>

        {/* Sidebar — "Other Domestic Intelligence" */}
        <aside className="lg:col-span-1 md:col-span-3 break-inside-avoid bg-paper-dark/50 border border-rule p-4">
          <h4 className="font-headline text-ink-faded text-sm small-caps tracking-[0.15em] font-bold text-center mb-3 border-b border-rule pb-2">
            OTHER DOMESTIC INTELLIGENCE
          </h4>
          <ul className="space-y-0">
            {sidebarHeadlines.map((item, idx) => (
              <li
                key={idx}
                className="py-2 border-b border-dotted border-rule last:border-b-0"
              >
                <p className="font-body text-ink-light text-[13px] leading-snug italic">
                  {item}
                </p>
              </li>
            ))}
          </ul>
        </aside>
      </section>

      {/* Decorative horizontal rule */}
      <div className="my-8 flex items-center gap-4">
        <div className="flex-1 border-t border-rule" />
        <img
          src="/section-fleuron.svg"
          alt=""
          className="w-3 h-3 opacity-40"
        />
        <div className="flex-1 border-t border-rule" />
      </div>

      {/* ──────── BOTTOM ROW: Article 3 (1) + Article 4 (2) + Article 5 (2) ──────── */}
      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-x-6 gap-y-8">
        {/* Article 3 */}
        <article className="lg:col-span-1 break-inside-avoid">
          <h3 className="font-headline text-ink text-lg md:text-xl font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
            {article3.headline}
          </h3>
          <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mb-2">
            {article3.dateline}
          </p>
          {renderArticleBody(article3.body, 'columns-1', 'sm')}
          <p className="font-body text-ink-light text-[10px] small-caps tracking-[0.1em] text-right mt-2">
            {article3.byline}
          </p>
        </article>

        {/* Article 4 — with engraving */}
        <article className="lg:col-span-2 break-inside-avoid border-t lg:border-t-0 border-rule pt-4 lg:pt-0">
          <h3 className="font-headline text-ink text-lg md:text-[22px] font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
            {article4.headline}
          </h3>
          {article4.subheadline && (
            <p className="font-headline text-ink-light text-sm italic leading-snug mb-2">
              {article4.subheadline}
            </p>
          )}
          <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mb-2">
            {article4.dateline}
          </p>
          {article4.image && (
            <EngravingImage
              src={`/${article4.image}`}
              alt={article4.headline}
              caption={article4.caption}
              className="my-3"
            />
          )}
          {renderArticleBody(article4.body, 'columns-1 md:columns-2 gap-4', 'sm')}
          <p className="font-body text-ink-light text-[10px] small-caps tracking-[0.1em] text-right mt-2">
            {article4.byline}
          </p>
        </article>

        {/* Article 5 */}
        <article className="lg:col-span-2 break-inside-avoid border-t md:border-t-0 border-rule pt-4 md:pt-0">
          <h3 className="font-headline text-ink text-lg md:text-[22px] font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
            {article5.headline}
          </h3>
          {article5.subheadline && (
            <p className="font-headline text-ink-light text-sm italic leading-snug mb-2">
              {article5.subheadline}
            </p>
          )}
          <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mb-2">
            {article5.dateline}
          </p>
          {renderArticleBody(article5.body, 'columns-1 md:columns-2 gap-4', 'sm')}
          <p className="font-body text-ink-light text-[10px] small-caps tracking-[0.1em] text-right mt-2">
            {article5.byline}
          </p>
        </article>
      </section>

      {/* ──────── LEADER COLUMN ──────── */}
      <div className="my-8">
        <div className="border-t-2 border-ink mb-0.5" />
        <div className="border-t border-rule mb-4" />

        <p className="text-center font-body text-ink-faded text-xs small-caps tracking-[0.2em] mb-3">
          LEADER
        </p>
        <h3 className="font-headline text-ink text-xl md:text-2xl font-bold text-center leading-tight mb-4">
          The Future of British Industry &mdash; A Call to Action
        </h3>

        <div className="columns-1 md:columns-2 lg:columns-3 gap-6 column-rule font-body text-ink text-base leading-relaxed body-text">
          {leaderText.split('\n\n').map((paragraph, idx) => (
            <p key={idx} className={idx === 0 ? 'drop-cap mb-3' : 'mb-3'}>
              {paragraph}
            </p>
          ))}
        </div>

        <p className="font-body text-ink-light text-xs small-caps tracking-[0.1em] text-right mt-4">
          THE EDITOR
        </p>

        <div className="border-t border-rule mt-4 mb-0.5" />
        <div className="border-t-2 border-ink" />
      </div>

      {/* Page footer line */}
      <div className="mt-6 pt-4 border-t border-rule flex items-center justify-center gap-3">
        <div className="w-12 border-t border-rule" />
        <span className="font-body text-ink-faded text-[10px] small-caps tracking-[0.2em]">
          THE LONDON MORNING CHRONICLE &mdash; SATURDAY, JUNE 15, 1901
        </span>
        <div className="w-12 border-t border-rule" />
      </div>
    </NewspaperPage>
  );
}

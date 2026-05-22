import Masthead from '@/components/Masthead';
import SectionHeader from '@/components/SectionHeader';
import NewspaperPage from '@/components/NewspaperPage';
import EngravingImage from '@/components/EngravingImage';
import { useContentStore } from '@/store/contentStore';

export default function ForeignAffairs() {
  const { getArticlesByCategory } = useContentStore();
  const articles = getArticlesByCategory('foreign');

  const lead = articles[0];
  const rightCol1 = articles[1];
  const rightCol2 = articles[2];
  const bottom1 = articles[3];
  const bottom2 = articles[4];

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
        title="FOREIGN AFFAIRS"
        subtitle="INTELLIGENCE FROM THE CONTINENT &middot; THE ORIENT &middot; THE AMERICAS"
      />

      {/* ──────── TOP ROW: Lead (3 cols) + 2 single columns ──────── */}
      <section className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-x-6 gap-y-8">
        {/* Lead Article — spans 3 columns */}
        <article className="lg:col-span-3 md:col-span-2 break-inside-avoid">
          <h2 className="font-headline text-ink text-2xl md:text-[28px] lg:text-[32px] font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
            {lead.headline}
          </h2>
          {lead.subheadline && (
            <p className="font-headline text-ink-light text-base md:text-lg italic leading-snug mb-2">
              {lead.subheadline}
            </p>
          )}
          <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mb-3">
            {lead.dateline}
          </p>
          {lead.image && (
            <EngravingImage
              src={`/${lead.image}`}
              alt={lead.headline}
              caption={lead.caption}
            />
          )}
          {renderArticleBody(lead.body, 'columns-2 lg:columns-3 gap-4')}
          <p className="font-body text-ink-light text-xs small-caps tracking-[0.1em] text-right mt-3">
            {lead.byline}
          </p>
        </article>

        {/* Right Column Article 1 */}
        <article className="lg:col-span-1 md:col-span-1 break-inside-avoid border-t lg:border-t-0 md:border-t-0 border-rule pt-4 lg:pt-0">
          <h3 className="font-headline text-ink text-lg md:text-xl font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
            {rightCol1.headline}
          </h3>
          <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mb-2">
            {rightCol1.dateline}
          </p>
          {renderArticleBody(rightCol1.body, 'columns-1', 'sm')}
          <p className="font-body text-ink-light text-[10px] small-caps tracking-[0.1em] text-right mt-2">
            {rightCol1.byline}
          </p>
        </article>

        {/* Right Column Article 2 */}
        <article className="lg:col-span-1 md:col-span-1 break-inside-avoid border-t md:border-t-0 border-rule pt-4 md:pt-0">
          <h3 className="font-headline text-ink text-lg md:text-xl font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
            {rightCol2.headline}
          </h3>
          <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mb-2">
            {rightCol2.dateline}
          </p>
          {renderArticleBody(rightCol2.body, 'columns-1', 'sm')}
          <p className="font-body text-ink-light text-[10px] small-caps tracking-[0.1em] text-right mt-2">
            {rightCol2.byline}
          </p>
        </article>
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

      {/* ──────── BOTTOM ROW: 2 articles spanning remaining columns ──────── */}
      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-x-6 gap-y-8">
        {/* Bottom Article 1 — with engraving */}
        <article className="lg:col-span-2 break-inside-avoid">
          <h3 className="font-headline text-ink text-lg md:text-[22px] font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
            {bottom1.headline}
          </h3>
          {bottom1.subheadline && (
            <p className="font-headline text-ink-light text-sm italic leading-snug mb-2">
              {bottom1.subheadline}
            </p>
          )}
          <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mb-2">
            {bottom1.dateline}
          </p>
          {bottom1.image && (
            <EngravingImage
              src={`/${bottom1.image}`}
              alt={bottom1.headline}
              caption={bottom1.caption}
              className="my-3"
            />
          )}
          {renderArticleBody(bottom1.body, 'columns-1 md:columns-2 gap-4', 'sm')}
          <p className="font-body text-ink-light text-[10px] small-caps tracking-[0.1em] text-right mt-2">
            {bottom1.byline}
          </p>
        </article>

        {/* Bottom Article 2 */}
        <article className="lg:col-span-3 break-inside-avoid border-t md:border-t-0 lg:border-t-0 border-rule pt-4 md:pt-0">
          <h3 className="font-headline text-ink text-lg md:text-[22px] font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
            {bottom2.headline}
          </h3>
          {bottom2.subheadline && (
            <p className="font-headline text-ink-light text-sm italic leading-snug mb-2">
              {bottom2.subheadline}
            </p>
          )}
          <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mb-2">
            {bottom2.dateline}
          </p>
          {renderArticleBody(bottom2.body, 'columns-1 md:columns-2 lg:columns-3 gap-4', 'sm')}
          <p className="font-body text-ink-light text-[10px] small-caps tracking-[0.1em] text-right mt-2">
            {bottom2.byline}
          </p>
        </article>
      </section>

      {/* Continued-from reference */}
      <div className="mt-10 pt-3 border-t border-rule">
        <p className="font-caption text-ink-faded text-[11px] italic">
          Continued from Page 1
        </p>
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

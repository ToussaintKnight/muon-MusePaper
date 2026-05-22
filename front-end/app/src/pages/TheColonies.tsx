import Masthead from '@/components/Masthead';
import SectionHeader from '@/components/SectionHeader';
import NewspaperPage from '@/components/NewspaperPage';
import EngravingImage from '@/components/EngravingImage';
import { useContentStore } from '@/store/contentStore';

const empireGazetteItems = [
  { location: 'CAPE TOWN', text: 'New railway to Kimberley diamond fields opened' },
  { location: 'CALCUTTA', text: 'Monsoon rains expected within the fortnight' },
  { location: 'MONTREAL', text: 'Canadian Pacific announces new Atlantic service' },
  { location: 'KINGSTON', text: 'Sugar harvest exceeds expectations' },
  { location: 'MELBOURNE', text: 'Parliament debates immigration restriction bill' },
  { location: 'LAGOS', text: 'British expedition returns from interior exploration' },
];

const patentsRegister = [
  'Improvements in Steam Engines — J. Watt & Co., Glasgow',
  'New Process for Rubber Vulcanisation — Mr. T. Hancock, London',
  'Electric Telegraph Apparatus — The Telegraph Construction Co.',
];

export default function TheColonies() {
  const { getArticlesByCategory } = useContentStore();
  const articles = getArticlesByCategory('colonies');

  const leadIndia = articles[0];
  const leadAustralia = articles[1];
  const bottomCanada = articles[2];
  const bottomSAfrica = articles[3];
  const bottomNewZealand = articles[4];

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
        title="THE COLONIES"
        subtitle="INDIA &middot; AFRICA &middot; AUSTRALASIA &middot; CANADA &middot; THE WEST INDIES"
      />

      {/* ──────── TOP ROW: India (2) + Australia (2) + Empire Gazette (1) ──────── */}
      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-x-6 gap-y-8">
        {/* Lead Article 1 — India */}
        <article className="lg:col-span-2 break-inside-avoid">
          <h2 className="font-headline text-ink text-xl md:text-2xl lg:text-[26px] font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
            {leadIndia.headline}
          </h2>
          {leadIndia.subheadline && (
            <p className="font-headline text-ink-light text-base italic leading-snug mb-2">
              {leadIndia.subheadline}
            </p>
          )}
          <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mb-3">
            {leadIndia.dateline}
          </p>
          {leadIndia.image && (
            <EngravingImage
              src={`/${leadIndia.image}`}
              alt={leadIndia.headline}
              caption={leadIndia.caption}
            />
          )}
          {renderArticleBody(leadIndia.body, 'columns-1 md:columns-2 gap-4')}
          <p className="font-body text-ink-light text-xs small-caps tracking-[0.1em] text-right mt-3">
            {leadIndia.byline}
          </p>
        </article>

        {/* Lead Article 2 — Australia */}
        <article className="lg:col-span-2 break-inside-avoid border-t lg:border-t-0 border-rule pt-4 lg:pt-0">
          <h2 className="font-headline text-ink text-xl md:text-2xl lg:text-[26px] font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
            {leadAustralia.headline}
          </h2>
          {leadAustralia.subheadline && (
            <p className="font-headline text-ink-light text-base italic leading-snug mb-2">
              {leadAustralia.subheadline}
            </p>
          )}
          <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mb-3">
            {leadAustralia.dateline}
          </p>
          {renderArticleBody(leadAustralia.body, 'columns-1 md:columns-2 gap-4')}
          <p className="font-body text-ink-light text-xs small-caps tracking-[0.1em] text-right mt-3">
            {leadAustralia.byline}
          </p>
        </article>

        {/* Empire Gazette Sidebar */}
        <aside className="lg:col-span-1 break-inside-avoid bg-paper-dark/50 border border-rule p-4">
          <h4 className="font-headline text-ink-faded text-sm small-caps tracking-[0.15em] font-bold text-center mb-3 border-b border-rule pb-2">
            THE EMPIRE GAZETTE
          </h4>
          <ul className="space-y-0">
            {empireGazetteItems.map((item, idx) => (
              <li
                key={idx}
                className="py-2 border-b border-dotted border-rule last:border-b-0"
              >
                <p className="font-body text-ink text-[12px] small-caps tracking-[0.05em] font-semibold leading-tight">
                  {item.location}
                </p>
                <p className="font-body text-ink-light text-[12px] leading-snug italic">
                  {item.text}
                </p>
              </li>
            ))}
          </ul>

          {/* Patents Register */}
          <div className="mt-4 pt-3 border-t border-rule">
            <h4 className="font-headline text-ink-faded text-[11px] small-caps tracking-[0.15em] font-bold text-center mb-2">
              PATENTS REGISTER
            </h4>
            <ul className="space-y-0">
              {patentsRegister.map((item, idx) => (
                <li
                  key={idx}
                  className="py-1.5 border-b border-dotted border-rule/60 last:border-b-0"
                >
                  <p className="font-body text-ink-light text-[11px] leading-snug">
                    {item}
                  </p>
                </li>
              ))}
            </ul>
          </div>
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

      {/* ──────── BOTTOM ROW: Canada (1) + SA (1) + NZ (1) + Map (2) ──────── */}
      <section className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-x-6 gap-y-8">
        {/* Canada — with engraving */}
        <article className="lg:col-span-1 break-inside-avoid">
          <h3 className="font-headline text-ink text-lg md:text-[22px] font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
            {bottomCanada.headline}
          </h3>
          {bottomCanada.subheadline && (
            <p className="font-headline text-ink-light text-sm italic leading-snug mb-2">
              {bottomCanada.subheadline}
            </p>
          )}
          <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mb-2">
            {bottomCanada.dateline}
          </p>
          {bottomCanada.image && (
            <EngravingImage
              src={`/${bottomCanada.image}`}
              alt={bottomCanada.headline}
              caption={bottomCanada.caption}
              className="my-3"
            />
          )}
          {renderArticleBody(bottomCanada.body, 'columns-1', 'sm')}
          <p className="font-body text-ink-light text-[10px] small-caps tracking-[0.1em] text-right mt-2">
            {bottomCanada.byline}
          </p>
        </article>

        {/* South Africa */}
        <article className="lg:col-span-1 break-inside-avoid border-t lg:border-t-0 border-rule pt-4 lg:pt-0">
          <h3 className="font-headline text-ink text-lg md:text-[22px] font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
            {bottomSAfrica.headline}
          </h3>
          {bottomSAfrica.subheadline && (
            <p className="font-headline text-ink-light text-sm italic leading-snug mb-2">
              {bottomSAfrica.subheadline}
            </p>
          )}
          <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mb-2">
            {bottomSAfrica.dateline}
          </p>
          {renderArticleBody(bottomSAfrica.body, 'columns-1', 'sm')}
          <p className="font-body text-ink-light text-[10px] small-caps tracking-[0.1em] text-right mt-2">
            {bottomSAfrica.byline}
          </p>
        </article>

        {/* New Zealand */}
        <article className="lg:col-span-1 break-inside-avoid border-t md:border-t-0 border-rule pt-4 md:pt-0">
          <h3 className="font-headline text-ink text-lg md:text-[22px] font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
            {bottomNewZealand.headline}
          </h3>
          {bottomNewZealand.subheadline && (
            <p className="font-headline text-ink-light text-sm italic leading-snug mb-2">
              {bottomNewZealand.subheadline}
            </p>
          )}
          <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mb-2">
            {bottomNewZealand.dateline}
          </p>
          {renderArticleBody(bottomNewZealand.body, 'columns-1', 'sm')}
          <p className="font-body text-ink-light text-[10px] small-caps tracking-[0.1em] text-right mt-2">
            {bottomNewZealand.byline}
          </p>
        </article>

        {/* Empire Map Reference */}
        <div className="lg:col-span-2 break-inside-avoid bg-paper-dark/30 border border-rule p-4 flex flex-col">
          <h4 className="font-headline text-ink-faded text-sm small-caps tracking-[0.15em] font-bold text-center mb-3">
            THE BRITISH EMPIRE IN 1901
          </h4>

          {/* Stylised map placeholder */}
          <div className="flex-1 min-h-[180px] bg-rule/20 border border-rule relative overflow-hidden">
            {/* Decorative grid lines */}
            <div className="absolute inset-0 grid grid-cols-6 grid-rows-4">
              {Array.from({ length: 24 }).map((_, i) => (
                <div
                  key={i}
                  className="border border-rule/30"
                />
              ))}
            </div>
            {/* Compass rose */}
            <div className="absolute top-3 right-3 w-12 h-12 flex items-center justify-center">
              <div className="absolute w-0.5 h-full bg-accent/40" />
              <div className="absolute h-0.5 w-full bg-accent/40" />
              <span className="font-body text-accent text-[10px] small-caps font-bold relative z-10">
                N
              </span>
            </div>
            {/* Place names */}
            <div className="absolute inset-0 p-3 flex flex-col justify-between">
              <div className="flex justify-between">
                <span className="font-body text-[9px] small-caps text-ink-light tracking-wide">
                  Canada
                </span>
                <span className="font-body text-[9px] small-caps text-accent tracking-wide">
                  United Kingdom
                </span>
              </div>
              <div className="flex justify-between">
                <span className="font-body text-[9px] small-caps text-ink-light tracking-wide">
                  West Africa
                </span>
                <span className="font-body text-[9px] small-caps text-accent tracking-wide">
                  India
                </span>
              </div>
              <div className="flex justify-between">
                <span className="font-body text-[9px] small-caps text-ink-light tracking-wide">
                  South Africa
                </span>
                <span className="font-body text-[9px] small-caps text-accent tracking-wide">
                  Australia
                </span>
              </div>
            </div>
          </div>

          <p className="font-caption text-ink-faded text-xs italic text-center mt-3 leading-tight">
            The extent of Imperial possessions, embracing one-fifth of the
            world&apos;s land surface
          </p>
          <p className="font-body text-ink-faded text-[10px] small-caps tracking-[0.1em] text-center mt-2">
            Approximate Area: 11,000,000 sq. miles &middot; Population:
            400,000,000
          </p>
        </div>
      </section>

      {/* Page footer line */}
      <div className="mt-10 pt-4 border-t border-rule flex items-center justify-center gap-3">
        <div className="w-12 border-t border-rule" />
        <span className="font-body text-ink-faded text-[10px] small-caps tracking-[0.2em]">
          THE LONDON MORNING CHRONICLE &mdash; SATURDAY, JUNE 15, 1901
        </span>
        <div className="w-12 border-t border-rule" />
      </div>
    </NewspaperPage>
  );
}

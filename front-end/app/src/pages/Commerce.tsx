import { useContentStore } from '@/store/contentStore';
import NewspaperPage from '@/components/NewspaperPage';
import Masthead from '@/components/Masthead';
import SectionHeader from '@/components/SectionHeader';
import ArticleBlock from '@/components/ArticleBlock';
import EngravingImage from '@/components/EngravingImage';

/* ------------------------------------------------------------------ */
/*  Market data                                                        */
/* ------------------------------------------------------------------ */

interface MarketRow {
  item: string;
  value: string;
  change: string;
  direction: 'up' | 'down' | 'flat';
}

const marketData: MarketRow[] = [
  { item: 'Bank Rate', value: '3%', change: '\u2014', direction: 'flat' },
  { item: 'Consols', value: '94\u00BD', change: '\u2212\u00BC', direction: 'down' },
  { item: 'India Stock', value: '106', change: '+\u215B', direction: 'up' },
  { item: 'Spanish Fours', value: '32', change: '\u2212\u00BD', direction: 'down' },
  { item: 'Grand Trunk', value: '12\u00BE', change: '+\u215B', direction: 'up' },
  { item: 'London & NW', value: '165', change: '\u2014', direction: 'flat' },
  { item: 'Midland', value: '118\u00BD', change: '+\u00BC', direction: 'up' },
  { item: 'Pennsylvania', value: '68', change: '+\u00BD', direction: 'up' },
];

interface CommodityRow {
  item: string;
  price: string;
  change: string;
  direction: 'up' | 'down' | 'flat';
}

const commodityData: CommodityRow[] = [
  { item: 'Wheat (qr)', price: '42s 6d', change: '+6d', direction: 'up' },
  { item: 'Cotton (lb)', price: '4.15d', change: '+\u00BCd', direction: 'up' },
  { item: 'Tea (lb)', price: '1s 2d', change: '\u22121d', direction: 'down' },
  { item: 'Sugar (cwt)', price: '16s 4d', change: '\u2014', direction: 'flat' },
  { item: 'Wool (lb)', price: '10d', change: '+\u00BDd', direction: 'up' },
  { item: 'Copper (ton)', price: '\u00A372 10s', change: '\u2212\u00A31', direction: 'down' },
];

interface ShippingEntry {
  vessel: string;
  status: string;
  details: string;
}

const shippingEntries: ShippingEntry[] = [
  {
    vessel: 'S.S. Majestic',
    status: 'ARRIVED',
    details: 'From New York \u2014 1,200 passengers, general cargo',
  },
  {
    vessel: 'S.S. Persia',
    status: 'SAILED',
    details: 'P&O liner for Bombay \u2014 mails and passengers',
  },
  {
    vessel: 'Barque Sea Witch',
    status: 'CLEARED',
    details: 'For Melbourne \u2014 wool and tallow',
  },
  {
    vessel: 'Thames Docks',
    status: 'DOCKS',
    details: '47 vessels today, 12 loading, 8 unloading',
  },
  {
    vessel: "Lloyd's",
    status: 'REPORT',
    details: 'No casualties reported in home waters',
  },
];

interface CompanyNotice {
  company: string;
  text: string;
}

const companyNotices: CompanyNotice[] = [
  {
    company: 'Anglo-Persian Oil Co.',
    text: 'Announces preliminary drilling results favourable.',
  },
  {
    company: 'Harrods Ltd.',
    text: 'Reports turnover increase of 15% over previous year.',
  },
  {
    company: 'The Gramophone Co.',
    text: 'To open new factory in Hayes.',
  },
  {
    company: 'Imperial Tobacco',
    text: 'Declares interim dividend of 4s. per share.',
  },
];

/* ------------------------------------------------------------------ */
/*  Helper: change colour                                               */
/* ------------------------------------------------------------------ */

function changeColor(dir: 'up' | 'down' | 'flat'): string {
  if (dir === 'up') return 'text-ink';
  if (dir === 'down') return 'text-accent';
  return 'text-ink-faded';
}

/* ------------------------------------------------------------------ */
/*  Commerce Page                                                       */
/* ------------------------------------------------------------------ */

export default function Commerce() {
  const { getArticlesByCategory } = useContentStore();
  const articles = getArticlesByCategory('commerce');

  const leadArticle = articles[0]; // cm-1: Bank Rate
  const shippingArticle = articles[1]; // cm-2: Shipping
  // cm-3: Telephone article available as articles[2] if needed
  const cottonArticle = articles[3]; // cm-4: Cotton
  const canalArticle = articles[4]; // cm-5: Ship Canal

  return (
    <NewspaperPage>
      <Masthead />

      {/* Section header */}
      <SectionHeader
        title="\u2766 Commerce & Trade \u2766"
        subtitle="Money Market \u00b7 The Produce Markets \u00b7 Shipping Intelligence \u00b7 Share Report"
      />

      {/* ============================================================ */}
      {/* TOP ROW: Market Table | Shipping | Lead Article               */}
      {/* Desktop: 5 columns; Tablet: 3; Mobile: 1                     */}
      {/* ============================================================ */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4 lg:gap-6 mb-8">

        {/* --- Column 1: Money Market Table --- */}
        <div className="lg:col-span-1">
          <h3 className="font-headline text-ink text-sm small-caps tracking-[0.15em] font-bold mb-3 text-center">
            The Money Market
          </h3>
          <table className="w-full font-body text-[13px] border-collapse">
            <thead>
              <tr className="border-b border-rule">
                <th className="text-left font-semibold text-ink-light small-caps tracking-[0.1em] pb-1 pr-1">
                  Item
                </th>
                <th className="text-right font-semibold text-ink-light small-caps tracking-[0.1em] pb-1 px-1">
                  Price
                </th>
                <th className="text-right font-semibold text-ink-light small-caps tracking-[0.1em] pb-1 pl-1">
                  Chg.
                </th>
              </tr>
            </thead>
            <tbody>
              {marketData.map((row) => (
                <tr
                  key={row.item}
                  className="border-b border-rule/60 hover:bg-paper-dark/50 transition-colors"
                >
                  <td className="py-[3px] pr-1 text-ink-light">{row.item}</td>
                  <td className="py-[3px] px-1 text-right font-mono text-ink">
                    {row.value}
                  </td>
                  <td
                    className={`py-[3px] pl-1 text-right font-mono ${changeColor(
                      row.direction
                    )}`}
                  >
                    {row.change}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="font-caption text-ink-faded text-xs italic text-center mt-2 leading-tight">
            The market was steady throughout the week.
          </p>
        </div>

        {/* --- Column 2: Shipping Intelligence --- */}
        <div className="lg:col-span-1 border-t md:border-t-0 lg:border-l border-rule pt-4 md:pt-0 lg:pl-6">
          <h3 className="font-headline text-ink text-sm small-caps tracking-[0.15em] font-bold mb-3 text-center">
            Shipping Intelligence
          </h3>
          <div className="space-y-3">
            {shippingEntries.map((entry) => (
              <div key={entry.vessel} className="border-b border-rule/40 pb-2">
                <p className="font-caption text-ink-faded text-[11px] italic tracking-[0.03em]">
                  {entry.status} —{' '}
                  <span className="text-ink-light font-semibold">
                    {entry.vessel}
                  </span>
                </p>
                <p className="font-body text-ink text-[13px] leading-snug mt-0.5">
                  {entry.details}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* --- Columns 3-5: Lead Article (2 col on desktop) --- */}
        <div className="md:col-span-3 lg:col-span-3 lg:pl-6 lg:border-l border-rule">
          {leadArticle && (
            <article>
              <h2 className="font-headline text-ink text-[22px] md:text-[26px] font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
                {leadArticle.headline}
              </h2>
              {leadArticle.subheadline && (
                <p className="font-headline text-ink-light text-base italic leading-snug mb-3">
                  {leadArticle.subheadline}
                </p>
              )}
              <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mb-3">
                {leadArticle.dateline}
              </p>
              {leadArticle.image && (
                <EngravingImage
                  src={`/${leadArticle.image}`}
                  alt={leadArticle.headline}
                  caption={leadArticle.caption}
                  className="my-4"
                />
              )}
              <div className="font-body text-ink text-base leading-relaxed body-text columns-1 md:columns-2 gap-6">
                {leadArticle.body.split('\n\n').map((paragraph, idx) => (
                  <p key={idx} className={idx === 0 ? 'drop-cap mb-4' : 'mb-4'}>
                    {paragraph}
                  </p>
                ))}
              </div>
              <p className="font-body text-ink-light text-xs small-caps tracking-[0.1em] text-right mt-3">
                {leadArticle.byline}
              </p>
            </article>
          )}
        </div>
      </div>

      {/* Divider */}
      <div className="border-t-2 border-ink mb-0.5" />
      <div className="border-t border-rule mb-8" />

      {/* ============================================================ */}
      {/* BOTTOM ROW: 5 columns                                            */}
      {/* Railway | Cotton+img | Commodity Table | Company Notices       */}
      {/* ============================================================ */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4 lg:gap-6">

        {/* --- Article 4: Railway Wars (from canal article data) --- */}
        <div className="lg:col-span-1">
          {canalArticle && (
            <ArticleBlock article={canalArticle} variant="compact" />
          )}
        </div>

        {/* --- Article 5: Cotton + image --- */}
        <div className="lg:col-span-1 lg:border-l border-rule lg:pl-6">
          {cottonArticle && (
            <>
              <h3 className="font-headline text-ink text-lg font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
                {cottonArticle.headline}
              </h3>
              <p className="font-headline text-ink-light text-sm italic leading-snug mb-2">
                {cottonArticle.subheadline}
              </p>
              <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mb-2">
                {cottonArticle.dateline}
              </p>
              <EngravingImage
                src="/engraving-commerce-02.jpg"
                alt="Shipping port scene"
                caption="The busy docks at Liverpool — cotton imports arriving daily"
                className="my-3"
              />
              <p className="font-body text-ink text-sm leading-relaxed body-text">
                {cottonArticle.body.split('\n\n')[0]}
              </p>
              <p className="font-body text-ink-light text-xs small-caps tracking-[0.1em] text-right mt-2">
                {cottonArticle.byline}
              </p>
            </>
          )}
        </div>

        {/* --- Commodity Prices Table --- */}
        <div className="lg:col-span-1 lg:border-l border-rule lg:pl-6">
          <h3 className="font-headline text-ink text-sm small-caps tracking-[0.15em] font-bold mb-3 text-center">
            The Produce Markets
          </h3>
          <table className="w-full font-body text-[13px] border-collapse">
            <thead>
              <tr className="border-b border-rule">
                <th className="text-left font-semibold text-ink-light small-caps tracking-[0.1em] pb-1 pr-1">
                  Commodity
                </th>
                <th className="text-right font-semibold text-ink-light small-caps tracking-[0.1em] pb-1 px-1">
                  Price
                </th>
                <th className="text-right font-semibold text-ink-light small-caps tracking-[0.1em] pb-1 pl-1">
                  Wk.
                </th>
              </tr>
            </thead>
            <tbody>
              {commodityData.map((row) => (
                <tr
                  key={row.item}
                  className="border-b border-rule/60 hover:bg-paper-dark/50 transition-colors"
                >
                  <td className="py-[3px] pr-1 text-ink-light">{row.item}</td>
                  <td className="py-[3px] px-1 text-right font-mono text-ink">
                    {row.price}
                  </td>
                  <td
                    className={`py-[3px] pl-1 text-right font-mono ${changeColor(
                      row.direction
                    )}`}
                  >
                    {row.change}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* --- Company Notices --- */}
        <div className="lg:col-span-2 lg:border-l border-rule lg:pl-6">
          <h3 className="font-headline text-ink text-sm small-caps tracking-[0.15em] font-bold mb-3 text-center">
            Public Company Notices
          </h3>
          <div className="space-y-3">
            {companyNotices.map((notice) => (
              <div
                key={notice.company}
                className="border-b border-dotted border-rule/60 pb-2"
              >
                <p className="font-body text-ink text-[13px] leading-snug">
                  <span className="font-semibold">{notice.company}</span> —{' '}
                  {notice.text}
                </p>
              </div>
            ))}
          </div>

          {/* Shipping article teaser */}
          {shippingArticle && (
            <div className="mt-6 pt-4 border-t border-rule">
              <h4 className="font-headline text-ink text-base font-bold leading-tight mb-1 hover:text-accent transition-colors duration-200 cursor-pointer">
                {shippingArticle.headline}
              </h4>
              <p className="font-headline text-ink-light text-sm italic leading-snug mb-2">
                {shippingArticle.subheadline}
              </p>
              <p className="font-body text-ink text-[13px] leading-relaxed body-text">
                {shippingArticle.body.split('\n\n')[0].slice(0, 180)}...
              </p>
              <p className="font-body text-ink-light text-xs small-caps tracking-[0.1em] text-right mt-2">
                {shippingArticle.byline}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Page Footer */}
      <div className="mt-12 pt-6 border-t-2 border-ink">
        <div className="flex items-center justify-center gap-4 mb-4">
          <img
            src="/section-fleuron.svg"
            alt=""
            className="w-3 h-3 opacity-50"
          />
          <span className="font-body text-ink-light text-sm small-caps tracking-[0.15em]">
            — 9 —
          </span>
          <img
            src="/section-fleuron.svg"
            alt=""
            className="w-3 h-3 opacity-50"
          />
        </div>
      </div>
    </NewspaperPage>
  );
}

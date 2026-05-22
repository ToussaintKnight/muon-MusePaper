import { useContentStore } from '@/store/contentStore';
import NewspaperPage from '@/components/NewspaperPage';
import Masthead from '@/components/Masthead';
import SectionHeader from '@/components/SectionHeader';
import ArticleBlock from '@/components/ArticleBlock';
import EngravingImage from '@/components/EngravingImage';

/* ------------------------------------------------------------------ */
/*  Patents data                                                       */
/* ------------------------------------------------------------------ */

interface PatentEntry {
  id: number;
  title: string;
  inventor: string;
  location: string;
}

const patents: PatentEntry[] = [
  {
    id: 1,
    title: 'Improvements in Electric Accumulators',
    inventor: 'W. H. Smith & Co.',
    location: 'Birmingham',
  },
  {
    id: 2,
    title: 'A New Type of Internal Combustion Engine',
    inventor: 'Mr. Herbert Austin',
    location: 'Wolseley',
  },
  {
    id: 3,
    title: 'Self-Propelled Road Vehicle Steering Apparatus',
    inventor: 'Daimler Motor Company',
    location: 'Coventry',
  },
  {
    id: 4,
    title: 'Process for the Artificial Production of Silk',
    inventor: 'Courtaulds Ltd.',
    location: 'Coventry',
  },
  {
    id: 5,
    title: 'Improved Method of Water Purification',
    inventor: 'Mr. John Armstrong',
    location: 'Glasgow',
  },
  {
    id: 6,
    title: 'Calculating Machine for Commercial Use',
    inventor: 'The Burroughs Adding Machine Co.',
    location: 'London',
  },
];

/* ------------------------------------------------------------------ */
/*  Science & Industry Page                                            */
/* ------------------------------------------------------------------ */

export default function ScienceIndustry() {
  const { getArticlesByCategory } = useContentStore();
  const articles = getArticlesByCategory('science');

  const leadArticle = articles[0]; // si-1: Röntgen Rays
  const wirelessArticle = articles[1]; // si-2: Wireless
  const exhibitionArticle = articles[2]; // si-3: Glasgow Exhibition
  const surveyArticle = articles[3]; // si-4: Ordnance Survey
  const turbineArticle = articles[4]; // si-5: Steam Turbine

  return (
    <NewspaperPage>
      <Masthead />

      {/* Section header */}
      <SectionHeader
        title="\u2766 Science & Industry \u2766"
        subtitle="Inventions \u00b7 Engineering \u00b7 Chemistry \u00b7 Electricity \u00b7 Aeronautics"
      />

      {/* ============================================================ */}
      {/* TOP ROW: Lead Article (3 cols) | Patents Register (2 cols)    */}
      {/* ============================================================ */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4 lg:gap-6 mb-8">

        {/* --- Lead Article: 3 columns --- */}
        <div className="lg:col-span-3">
          {leadArticle && (
            <article>
              <h2 className="font-headline text-ink text-[24px] md:text-[28px] font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
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

              {/* Large engraving */}
              <EngravingImage
                src="/engraving-science-01.jpg"
                alt="Scientific apparatus demonstration"
                caption="Professor Thompson demonstrating the remarkable Röntgen rays at Burlington House before assembled Fellows"
                className="my-4"
              />

              {/* 3-column body text on desktop */}
              <div className="font-body text-ink text-base leading-relaxed body-text columns-1 md:columns-2 lg:columns-3 gap-5">
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

        {/* --- Patents Register: 2 columns --- */}
        <div className="lg:col-span-2 lg:border-l border-rule lg:pl-6 pt-6 lg:pt-0">
          <h3 className="font-headline text-ink text-sm small-caps tracking-[0.15em] font-bold mb-4 text-center">
            Patents Registered This Week
          </h3>

          <div className="space-y-0">
            {patents.map((patent, idx) => (
              <div
                key={patent.id}
                className={`py-3 ${
                  idx < patents.length - 1
                    ? 'border-b border-dotted border-rule/60'
                    : ''
                }`}
              >
                <p className="font-headline text-ink text-[13px] font-bold leading-snug mb-0.5">
                  {patent.id}. {patent.title}
                </p>
                <p className="font-caption text-ink-light text-xs italic tracking-[0.03em]">
                  {patent.inventor}, {patent.location}
                </p>
              </div>
            ))}
          </div>

          {/* Supplementary patent note */}
          <div className="mt-6 p-4 bg-paper-dark/40 border border-rule/60">
            <h4 className="font-headline text-ink text-sm font-bold small-caps tracking-[0.1em] mb-2">
              Patent Office Notice
            </h4>
            <p className="font-body text-ink-light text-[13px] leading-relaxed">
              Applications for patents should be filed at the Patent Office,
              25 Southampton Buildings, Chancery Lane, London. Fees: Provisional
              specification 5s.; Complete specification 10s. All enquiries to be
              addressed to the Comptroller-General.
            </p>
          </div>

          {/* Wireless article teaser below patents */}
          {wirelessArticle && (
            <div className="mt-6 pt-4 border-t border-rule">
              <h4 className="font-headline text-ink text-base font-bold leading-tight mb-1 hover:text-accent transition-colors duration-200 cursor-pointer">
                {wirelessArticle.headline}
              </h4>
              <p className="font-headline text-ink-light text-sm italic leading-snug mb-2">
                {wirelessArticle.subheadline}
              </p>
              <p className="font-body text-ink text-[13px] leading-relaxed body-text">
                {wirelessArticle.body.split('\n\n')[0].slice(0, 200)}...
              </p>
              <p className="font-body text-ink-light text-xs small-caps tracking-[0.1em] text-right mt-2">
                {wirelessArticle.byline}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Divider */}
      <div className="border-t-2 border-ink mb-0.5" />
      <div className="border-t border-rule mb-8" />

      {/* ============================================================ */}
      {/* BOTTOM ROW: 4 articles (1 col each)                              */}
      {/* Exhibition | Wireless (text) | Survey | Turbine                  */}
      {/* ============================================================ */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">

        {/* --- Article 1: Glasgow Exhibition (with image) --- */}
        <div className="lg:col-span-1">
          {exhibitionArticle && (
            <article className="h-full flex flex-col">
              <h3 className="font-headline text-ink text-lg font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
                {exhibitionArticle.headline}
              </h3>
              <p className="font-headline text-ink-light text-sm italic leading-snug mb-2">
                {exhibitionArticle.subheadline}
              </p>
              <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mb-2">
                {exhibitionArticle.dateline}
              </p>
              <EngravingImage
                src="/engraving-science-02.jpg"
                alt="Exhibition hall with industrial machinery"
                caption="The Palace of Industries at the Glasgow Exhibition"
                className="my-2"
              />
              <p className="font-body text-ink text-sm leading-relaxed body-text flex-grow">
                {exhibitionArticle.body.split('\n\n')[0]}
              </p>
              <p className="font-body text-ink-light text-xs small-caps tracking-[0.1em] text-right mt-2">
                {exhibitionArticle.byline}
              </p>
            </article>
          )}
        </div>

        {/* --- Article 2: Wireless (text only) --- */}
        <div className="lg:col-span-1 lg:border-l border-rule lg:pl-6">
          {wirelessArticle && (
            <article className="h-full flex flex-col">
              <h3 className="font-headline text-ink text-lg font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
                {wirelessArticle.headline}
              </h3>
              <p className="font-headline text-ink-light text-sm italic leading-snug mb-2">
                {wirelessArticle.subheadline}
              </p>
              <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mb-2">
                {wirelessArticle.dateline}
              </p>
              {/* Technical diagram placeholder - ornamental rule */}
              <div className="my-3 py-4 px-3 bg-paper-dark/30 border border-rule/60 text-center">
                <div className="font-body text-ink-faded text-[11px] small-caps tracking-[0.15em] mb-2">
                  Wireless Telegraphy Diagram
                </div>
                <div className="flex items-center justify-center gap-2">
                  <div className="w-12 h-12 border border-rule rounded-full flex items-center justify-center">
                    <span className="font-body text-[10px] text-ink-light">
                      TX
                    </span>
                  </div>
                  <div className="w-16 border-t border-dashed border-ink-faded relative">
                    <span className="absolute -top-3 left-1/2 -translate-x-1/2 font-caption text-[9px] italic text-ink-faded">
                      waves
                    </span>
                  </div>
                  <div className="w-12 h-12 border border-rule rounded-full flex items-center justify-center">
                    <span className="font-body text-[10px] text-ink-light">
                      RX
                    </span>
                  </div>
                </div>
              </div>
              <p className="font-body text-ink text-sm leading-relaxed body-text flex-grow">
                {wirelessArticle.body.split('\n\n')[0]}
              </p>
              <p className="font-body text-ink-light text-xs small-caps tracking-[0.1em] text-right mt-2">
                {wirelessArticle.byline}
              </p>
            </article>
          )}
        </div>

        {/* --- Article 3: Ordnance Survey --- */}
        <div className="lg:col-span-1 lg:border-l border-rule lg:pl-6">
          {surveyArticle && (
            <ArticleBlock article={surveyArticle} variant="compact" />
          )}
        </div>

        {/* --- Article 4: Steam Turbine --- */}
        <div className="lg:col-span-1 lg:border-l border-rule lg:pl-6">
          {turbineArticle && (
            <ArticleBlock article={turbineArticle} variant="compact" />
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
            — 13 —
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

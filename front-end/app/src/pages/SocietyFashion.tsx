import { useContentStore } from '@/store/contentStore';
import Masthead from '@/components/Masthead';
import SectionHeader from '@/components/SectionHeader';
import EngravingImage from '@/components/EngravingImage';
import NewspaperPage from '@/components/NewspaperPage';

/* ─── hard-coded section data ─── */

interface FashionPlate {
  title: string;
  description: string;
}

const fashionPlates: FashionPlate[] = [
  {
    title: 'The New Sleeve',
    description:
      'The fashionable sleeve of the moment is the leg-of-mutton, reaching its most exaggerated proportions this Season. Ladies are advised that moderation in all things produces the most elegant effect.',
  },
  {
    title: 'Walking Dresses',
    description:
      'For the Park, the tailor-made costume in light tweed continues to hold favour. The jacket is worn shorter than last year, with a pronounced waist.',
  },
  {
    title: 'Evening Gowns',
    description:
      'For Court presentations, white satin remains de rigueur, with trains of not less than three yards. Lace insertions and seed pearls are the favoured ornamentation.',
  },
];

interface CalendarEvent {
  date: string;
  description: string;
}

const seasonCalendar: CalendarEvent[] = [
  { date: 'June 18', description: 'Court Drawing Room, Buckingham Palace' },
  { date: 'June 20', description: "Lady Salisbury's Reception at Hatfield House" },
  { date: 'June 22', description: 'Royal Ascot (Gold Cup Day)' },
  { date: 'June 24', description: "The Duchess of Marlborough's Ball at Blenheim" },
  { date: 'June 26', description: 'Garden Party at Marlborough House (by Royal command)' },
  { date: 'June 28', description: "Eton v. Harrow at Lord's" },
  { date: 'June 30', description: 'Promenade Concert, Queen\'s Hall' },
  { date: 'July 3', description: "Wimbledon Lawn Tennis (Gentlemen's Final)" },
];

interface Obituary {
  name: string;
  body: string;
}

const obituaries: Obituary[] = [
  {
    name: 'The Right Honourable The Earl of Selborne, G.C.M.G.',
    body: 'Died at his seat in Hampshire, aged 68. Formerly First Lord of the Admiralty and High Commissioner for South Africa. A statesman of distinguished ability and unimpeachable integrity.',
  },
  {
    name: 'Sir William Thomson, Lord Kelvin, O.M.',
    body: 'The eminent physicist and mathematician died in Glasgow, aged 83. His contributions to thermodynamics and the science of electricity are known throughout the civilised world.',
  },
];

interface PersonalNotice {
  type: string;
  content: string;
}

const personalNotices: PersonalNotice[] = [
  {
    type: 'Engagement',
    content:
      'The engagement is announced between Captain Arthur Wellesley, Grenadier Guards, youngest son of the Duke of Wellington, and Miss Violet Manners, daughter of Lord Manners.',
  },
  {
    type: 'Thanks',
    content:
      'The Countess of Westmorland desires to express her sincere thanks to the many friends who sent kind messages of sympathy on the occasion of her recent bereavement.',
  },
  {
    type: 'Invitation',
    content:
      'The Duchess of Portland will be at home on Wednesday, the 19th instant, from three to six o\'clock. Cards of invitation have been issued.',
  },];

/* ─── page component ─── */
export default function SocietyFashion() {
  const articles = useContentStore((state) => state.articles);
  const societyArticles = articles.filter((a) => a.category === 'society');

  /* sf-1 = Court Circular / lead, sf-2 = wedding, sf-3 = Ascot, sf-4 = Cowes, sf-5 = Fashions */
  const courtArticle = societyArticles[0];
  const weddingArticle = societyArticles[1];
  const ascotArticle = societyArticles[2];
  const cowesArticle = societyArticles[3];
  const fashionArticle = societyArticles[4];

  const courtParagraphs = courtArticle?.body.split('\n\n') ?? [];
  const weddingParagraphs = weddingArticle?.body.split('\n\n') ?? [];

  return (
    <NewspaperPage>
      <Masthead />

      <SectionHeader
        title="Society & Fashion"
        subtitle="The Court · The Season · Fashionable Gatherings · Marriages"
      />

      {/* ════════════════════ COURT CIRCULAR — full width ════════════════════ */}
      {courtArticle && (
        <section className="mb-10">
          <div className="border-t-2 border-ink mb-0.5" />
          <div className="border-t border-rule mb-4" />

          <p className="font-body text-ink text-sm small-caps tracking-[0.2em] text-center mb-3">
            Court Circular
          </p>

          <h2 className="font-headline text-ink text-xl md:text-2xl font-bold leading-tight mb-4 text-center max-w-4xl mx-auto">
            {courtArticle.headline}
          </h2>
          {courtArticle.subheadline && (
            <p className="font-headline text-ink-light text-sm md:text-base italic text-center leading-snug mb-4 max-w-3xl mx-auto">
              {courtArticle.subheadline}
            </p>
          )}

          {/* 3-column body, indented opening */}
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-x-gutter gap-y-4 max-w-5xl mx-auto">
            <div className="hidden lg:block" /> {/* spacer */}
            <div className="lg:border-r border-rule lg:pr-gutter">
              {courtParagraphs[0] && (
                <p
                  className="font-body text-ink text-base leading-relaxed body-text"
                  style={{ textIndent: '2em' }}
                >
                  {courtParagraphs[0]}
                </p>
              )}
            </div>
            <div className="lg:border-r border-rule lg:pr-gutter">
              {courtParagraphs[1] && (
                <p className="font-body text-ink text-base leading-relaxed body-text">
                  {courtParagraphs[1]}
                </p>
              )}
            </div>
            <div>
              {courtParagraphs[2] && (
                <p className="font-body text-ink text-base leading-relaxed body-text">
                  {courtParagraphs[2]}
                </p>
              )}
            </div>
            <div className="hidden lg:block" /> {/* spacer */}
          </div>

          <p className="font-body text-ink-light text-xs small-caps tracking-[0.1em] text-center mt-4">
            {courtArticle.byline}
          </p>

          <div className="border-t border-rule mt-4 mb-0.5" />
          <div className="border-t-2 border-ink" />
        </section>
      )}

      {/* ════════════════════ GARDEN PARTY + FASHION + CALENDAR ════════════════════ */}
      <section className="mb-10">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-x-gutter gap-y-8">
          {/* ── Garden Party / Ascot article (2 cols, large image) ── */}
          <div className="lg:col-span-2">
            {ascotArticle && (
              <article>
                <h3 className="font-headline text-ink text-lg md:text-[22px] font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
                  {ascotArticle.headline}
                </h3>
                {ascotArticle.subheadline && (
                  <p className="font-headline text-ink-light text-sm italic leading-snug mb-2">
                    {ascotArticle.subheadline}
                  </p>
                )}
                <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mb-3">
                  {ascotArticle.dateline}
                </p>

                {ascotArticle.image && (
                  <EngravingImage
                    src={`/${ascotArticle.image}`}
                    alt={ascotArticle.headline}
                    caption={ascotArticle.caption}
                    className="my-3"
                  />
                )}

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-x-gutter gap-y-4">
                  <div className="lg:border-r border-rule lg:pr-gutter">
                    <div className="drop-cap font-body text-ink text-[15px] leading-relaxed body-text">
                      {ascotArticle.body.split('\n\n')[0]}
                    </div>
                  </div>
                  <div>
                    <p className="font-body text-ink text-[15px] leading-relaxed body-text">
                      {ascotArticle.body.split('\n\n')[1]}
                    </p>
                  </div>
                </div>

                <p className="font-body text-ink-light text-[11px] small-caps tracking-[0.1em] text-right mt-2">
                  {ascotArticle.byline}
                </p>
              </article>
            )}
          </div>

          {/* ── Fashion Plates (1 col) ── */}
          <div className="lg:border-l border-rule lg:pl-gutter md:border-r border-rule md:pr-gutter">
            <h3 className="font-headline text-ink text-sm small-caps tracking-[0.15em] font-bold text-center mb-4">
              The Latest Modes
            </h3>
            <div className="border-t-2 border-ink mb-0.5" />
            <div className="border-t border-rule mb-4" />

            <div className="space-y-4">
              {fashionPlates.map((plate, idx) => (
                <article key={idx} className="py-2">
                  <h4 className="font-headline text-ink text-[13px] font-bold leading-tight mb-1">
                    {plate.title}
                  </h4>
                  <p className="font-body text-ink-light text-[13px] leading-relaxed italic">
                    &ldquo;{plate.description}&rdquo;
                  </p>
                  {idx < fashionPlates.length - 1 && (
                    <div className="border-t border-dotted border-rule mt-3" />
                  )}
                </article>
              ))}
            </div>

            {/* Royal motif */}
            <div className="mt-6 text-center">
              <p
                className="text-accent/40 text-xl"
                style={{ fontFamily: 'Georgia, serif' }}
              >
                &#10020;
              </p>
            </div>
          </div>

          {/* ── Season's Calendar (2 cols) ── */}
          <div className="lg:col-span-2 lg:border-l border-rule lg:pl-gutter">
            <h3 className="font-headline text-ink text-sm small-caps tracking-[0.15em] font-bold text-center mb-4">
              The Season&apos;s Social Calendar
            </h3>
            <div className="border-t-2 border-ink mb-0.5" />
            <div className="border-t border-rule mb-4" />

            <div className="space-y-0">
              {seasonCalendar.map((event, idx) => (
                <div
                  key={idx}
                  className={`py-2.5 px-3 ${
                    idx % 2 === 0 ? 'bg-paper-dark/40' : 'bg-transparent'
                  }`}
                >
                  <p className="font-body text-ink text-xs font-semibold mb-0.5">
                    {event.date}
                  </p>
                  <p className="font-body text-ink-light text-xs leading-relaxed">
                    {event.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Decorative rule */}
      <div className="my-8">
        <div className="border-t-2 border-ink mb-0.5" />
        <div className="border-t border-rule" />
      </div>

      {/* ════════════════════ WEDDING + OBITUARIES ROW ════════════════════ */}
      <section className="mb-10">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-x-gutter gap-y-8">
          {/* ── Wedding Notice (3 cols) ── */}
          <div className="lg:col-span-3">
            {weddingArticle && (
              <article>
                <div className="flex items-center justify-center gap-2 mb-3">
                  <img
                    src="/section-fleuron.svg"
                    alt=""
                    className="w-3 h-3 opacity-50"
                  />
                  <span className="font-headline text-ink text-sm small-caps tracking-[0.15em] font-bold">
                    Marriages
                  </span>
                  <img
                    src="/section-fleuron.svg"
                    alt=""
                    className="w-3 h-3 opacity-50"
                  />
                </div>

                <h3 className="font-headline text-ink text-lg md:text-xl font-bold leading-tight mb-3 text-center">
                  {weddingArticle.headline}
                </h3>
                {weddingArticle.subheadline && (
                  <p className="font-headline text-ink-light text-sm italic text-center leading-snug mb-4">
                    {weddingArticle.subheadline}
                  </p>
                )}

                <div className="border-t-2 border-ink mb-0.5" />
                <div className="border-t border-rule mb-4" />

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-x-gutter gap-y-4">
                  <div className="lg:border-r border-rule lg:pr-gutter">
                    <div className="drop-cap font-body text-ink text-[15px] leading-relaxed body-text">
                      {weddingParagraphs[0]}
                    </div>
                  </div>
                  <div className="lg:border-r border-rule lg:pr-gutter">
                    <p className="font-body text-ink text-[15px] leading-relaxed body-text">
                      {weddingParagraphs[1]}
                    </p>
                  </div>
                  <div>
                    <p className="font-body text-ink text-[15px] leading-relaxed body-text">
                      {weddingParagraphs[2] ??
                        'The happy couple departed for the Continent immediately after the reception, where they will spend a honeymoon of some weeks before taking up residence at the family seat in Scotland.'}
                    </p>
                  </div>
                </div>

                <p className="font-caption text-ink-faded text-xs italic text-center mt-4 tracking-[0.03em]">
                  {weddingArticle.dateline}
                </p>
              </article>
            )}

            {/* ── Cowes Regatta article below the wedding ── */}
            {cowesArticle && (
              <div className="mt-8 pt-6 border-t border-rule">
                <h3 className="font-headline text-ink text-lg md:text-[20px] font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
                  {cowesArticle.headline}
                </h3>
                {cowesArticle.subheadline && (
                  <p className="font-headline text-ink-light text-sm italic leading-snug mb-2">
                    {cowesArticle.subheadline}
                  </p>
                )}
                <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mb-2">
                  {cowesArticle.dateline}
                </p>
                <p className="font-body text-ink text-[15px] leading-relaxed body-text">
                  {cowesArticle.body.split('\n\n')[0]}
                </p>
                <p className="font-body text-ink-light text-[11px] small-caps tracking-[0.1em] text-right mt-2">
                  {cowesArticle.byline}
                </p>
              </div>
            )}
          </div>

          {/* ── Obituaries + Personal Notices (2 cols) ── */}
          <div className="lg:col-span-2 lg:border-l border-rule lg:pl-gutter">
            {/* Obituaries */}
            <div
              className="border-2 border-ink p-4 mb-6"
              style={{ borderColor: 'var(--ink)' }}
            >
              <h3 className="font-headline text-ink-faded text-sm small-caps tracking-[0.15em] font-bold text-center mb-4">
                Deaths
              </h3>
              <div className="border-t border-ink mb-4" />

              <div className="space-y-4">
                {obituaries.map((ob, idx) => (
                  <article key={idx}>
                    <h4 className="font-headline text-ink text-sm font-bold leading-tight mb-1">
                      {ob.name}
                    </h4>
                    <p className="font-body text-ink-light text-[13px] leading-relaxed">
                      {ob.body}
                    </p>
                    {idx < obituaries.length - 1 && (
                      <div className="border-t border-rule/60 mt-3" />
                    )}
                  </article>
                ))}
              </div>
            </div>

            {/* Personal Notices */}
            <div className="mt-6">
              <h3 className="font-headline text-ink text-sm small-caps tracking-[0.15em] font-bold text-center mb-4">
                Personal Notices
              </h3>
              <div className="border-t-2 border-ink mb-0.5" />
              <div className="border-t border-rule mb-4" />

              <div className="space-y-0">
                {personalNotices.map((notice, idx) => (
                  <div key={idx}>
                    <div className="py-3">
                      <p className="font-body text-ink text-xs font-semibold small-caps tracking-[0.15em] mb-1">
                        {notice.type}
                      </p>
                      <p className="font-body text-ink-light text-[13px] leading-relaxed">
                        {notice.content}
                      </p>
                    </div>
                    {idx < personalNotices.length - 1 && (
                      <div className="border-t border-dotted border-rule" />
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Fashions article snippet */}
            {fashionArticle && (
              <div className="mt-6 pt-4 border-t border-rule">
                <h4 className="font-headline text-ink text-sm font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
                  {fashionArticle.headline}
                </h4>
                <p className="font-body text-ink-light text-[13px] leading-relaxed body-text">
                  {fashionArticle.body.split('\n\n')[0].slice(0, 180)}...
                </p>
                <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mt-1">
                  {fashionArticle.dateline}
                </p>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* ════════════════════ PAGE FOOTER ════════════════════ */}
      <div className="mt-12 pt-6 border-t border-rule">
        <div className="flex items-center justify-center gap-3">
          <img src="/section-fleuron.svg" alt="" className="w-3 h-3 opacity-50" />
          <span className="font-body text-ink-light text-sm small-caps tracking-[0.15em]">
            — 15 —
          </span>
          <img src="/section-fleuron.svg" alt="" className="w-3 h-3 opacity-50" />
        </div>
      </div>
    </NewspaperPage>
  );
}

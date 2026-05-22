import { useContentStore } from '@/store/contentStore';
import Masthead from '@/components/Masthead';
import SectionHeader from '@/components/SectionHeader';
import EngravingImage from '@/components/EngravingImage';
import NewspaperPage from '@/components/NewspaperPage';

/* ─── hard-coded section data ─── */

interface BookNotice {
  title: string;
  author: string;
  publisher: string;
  review: string;
}

const bookNotices: BookNotice[] = [
  {
    title: 'The Hound of the Baskervilles',
    author: 'A. Conan Doyle',
    publisher: 'George Newnes, 6s.',
    review:
      'A new Sherlock Holmes mystery of the most gripping kind. The Dartmoor setting is evoked with masterly skill.',
  },
  {
    title: 'Kim',
    author: 'Rudyard Kipling',
    publisher: 'Macmillan, 6s.',
    review:
      "Kipling's Indian tale is a work of singular charm and insight. The road-colours of India have never been so vividly rendered.",
  },
  {
    title: 'The Wings of the Dove',
    author: 'Henry James',
    publisher: 'Constable, 7s. 6d.',
    review:
      "Mr. James's latest novel demands patient attention, but rewards the diligent reader with profound psychological observation.",
  },
  {
    title: 'The First Men in the Moon',
    author: 'H.G. Wells',
    publisher: 'George Newnes, 6s.',
    review:
      "Mr. Wells's scientific romance takes the reader on a fantastic journey of the most imaginative sort.",
  },
];

interface ComingEvent {
  date: string;
  description: string;
}

const comingEvents: ComingEvent[] = [
  { date: 'June 18', description: "Mr. Tree in The Merry Wives of Windsor at His Majesty's" },
  { date: 'June 20', description: 'Sarasate violin recital, St. James\'s Hall' },
  { date: 'June 22', description: 'Private view: Whistler retrospective, Goupil Gallery' },
  { date: 'June 25', description: "Premiere: Elgar's new orchestral work, Covent Garden" },
];

/* ─── star rating ─── */
function StarRating({ count = 5 }: { count?: number }) {
  return (
    <div className="flex items-center justify-center gap-1 my-3">
      {Array.from({ length: count }).map((_, i) => (
        <span
          key={i}
          className="text-accent text-lg"
          style={{ fontFamily: 'Georgia, serif' }}
        >
          &#10022;
        </span>
      ))}
      <span className="font-caption text-ink-faded text-xs italic ml-2 tracking-[0.03em]">
        A Performance Without Parallel
      </span>
    </div>
  );
}

/* ─── page component ─── */
export default function ArtsLetters() {
  const articles = useContentStore((state) => state.articles);
  const artsArticles = articles.filter((a) => a.category === 'arts');

  /* lead + four remaining articles */
  const lead = artsArticles[0];
  const remainder = artsArticles.slice(1);

  /* split body paragraphs for the lead article */
  const leadParagraphs = lead?.body.split('\n\n') ?? [];

  return (
    <NewspaperPage>
      <Masthead />

      <SectionHeader
        title="The Arts & Letters"
        subtitle="The Theatre · Literature · Music · The Fine Arts"
      />

      {/* ════════════════════ LEAD ROW: Theatre Review + Book Notices ════════════════════ */}
      <section className="mb-10">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-x-gutter gap-y-8">
          {/* ── Lead Theatre Review (3 cols) ── */}
          <div className="lg:col-span-3">
            {/* Headline */}
            <h2 className="font-headline text-ink text-xl md:text-[28px] font-bold leading-tight mb-2">
              {lead?.headline}
            </h2>
            {lead?.subheadline && (
              <p className="font-headline text-ink-light text-sm md:text-base italic leading-snug mb-2">
                {lead.subheadline}
              </p>
            )}

            <StarRating count={5} />

            <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mb-4">
              {lead?.dateline}
            </p>

            {/* Theatre engraving */}
            {lead?.image && (
              <EngravingImage
                src={`/${lead.image}`}
                alt={lead?.headline ?? ''}
                caption={lead?.caption}
                className="my-4"
              />
            )}

            {/* Body — 3 columns desktop */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-x-gutter gap-y-4">
              <div className="lg:border-r border-rule lg:pr-gutter">
                {leadParagraphs[0] && (
                  <div className="drop-cap font-body text-ink text-base leading-relaxed body-text">
                    {leadParagraphs[0]}
                  </div>
                )}
              </div>
              <div className="lg:border-r border-rule lg:pr-gutter">
                {leadParagraphs[1] && (
                  <p className="font-body text-ink text-base leading-relaxed body-text">
                    {leadParagraphs[1]}
                  </p>
                )}
              </div>
              <div>
                {leadParagraphs[2] && (
                  <p className="font-body text-ink text-base leading-relaxed body-text">
                    {leadParagraphs[2]}
                  </p>
                )}
              </div>
            </div>

            <p className="font-body text-ink-light text-xs small-caps tracking-[0.1em] text-right mt-3">
              {lead?.byline}
            </p>
          </div>

          {/* ── Book Notices (2 cols) ── */}
          <div className="lg:col-span-2 lg:border-l border-rule lg:pl-gutter">
            <h3 className="font-headline text-ink text-sm small-caps tracking-[0.15em] font-bold text-center mb-4">
              Books Received and Noticed
            </h3>
            <div className="border-t-2 border-ink mb-0.5" />
            <div className="border-t border-rule mb-4" />

            <div className="space-y-0">
              {bookNotices.map((book, idx) => (
                <div key={idx}>
                  <div className="py-3">
                    <h4 className="font-headline text-ink text-sm md:text-base font-bold italic leading-snug mb-1">
                      &ldquo;{book.title}&rdquo;
                    </h4>
                    <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mb-2">
                      By {book.author}. {book.publisher}
                    </p>
                    <p className="font-body text-ink-light text-[13px] leading-relaxed">
                      {book.review}
                    </p>
                  </div>
                  {idx < bookNotices.length - 1 && (
                    <div className="border-t border-dotted border-rule" />
                  )}
                </div>
              ))}
            </div>

            {/* Literary quote */}
            <div className="mt-6 pl-3 border-l-2 border-accent/30">
              <blockquote className="font-body text-ink-light text-sm italic leading-relaxed">
                &ldquo;The theatre is the finest vehicle for the transmission of human emotion
                ever devised by civilised man.&rdquo;
              </blockquote>
              <cite className="font-caption text-ink-faded text-xs italic tracking-[0.03em] not-italic block mt-1">
                — The Dramatic Review, 1898
              </cite>
            </div>
          </div>
        </div>
      </section>

      {/* Decorative rule */}
      <div className="my-8">
        <div className="border-t-2 border-ink mb-0.5" />
        <div className="border-t border-rule" />
      </div>

      {/* ════════════════════ BOTTOM ROW: 4 columns ════════════════════ */}
      <section className="mb-10">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-x-gutter gap-y-8">
          {/* ── Article 2: Literary (1 col) ── */}
          <div className="md:border-r border-rule md:pr-gutter">
            {remainder[0] && (
              <article>
                <h3 className="font-headline text-ink text-lg md:text-[18px] font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
                  {remainder[0].headline}
                </h3>
                {remainder[0].subheadline && (
                  <p className="font-headline text-ink-light text-sm italic leading-snug mb-2">
                    {remainder[0].subheadline}
                  </p>
                )}
                <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mb-2">
                  {remainder[0].dateline}
                </p>

                {remainder[0].image && (
                  <EngravingImage
                    src={`/${remainder[0].image}`}
                    alt={remainder[0].headline}
                    caption={remainder[0].caption}
                    className="my-3"
                  />
                )}

                <div className="drop-cap font-body text-ink text-[15px] leading-relaxed body-text">
                  {remainder[0].body.split('\n\n')[0]}
                </div>
                <p className="font-body text-ink-light text-[11px] small-caps tracking-[0.1em] text-right mt-2">
                  {remainder[0].byline}
                </p>
              </article>
            )}
          </div>

          {/* ── Article 3: Art Exhibition (1 col) ── */}
          <div className="lg:border-r border-rule lg:pr-gutter">
            {remainder[1] && (
              <article>
                <h3 className="font-headline text-ink text-lg md:text-[18px] font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
                  {remainder[1].headline}
                </h3>
                {remainder[1].subheadline && (
                  <p className="font-headline text-ink-light text-sm italic leading-snug mb-2">
                    {remainder[1].subheadline}
                  </p>
                )}
                <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mb-2">
                  {remainder[1].dateline}
                </p>
                <div className="drop-cap font-body text-ink text-[15px] leading-relaxed body-text">
                  {remainder[1].body.split('\n\n')[0]}
                </div>
                <p className="font-body text-ink-light text-[11px] small-caps tracking-[0.1em] text-right mt-2">
                  {remainder[1].byline}
                </p>
              </article>
            )}

            {/* Second literary quote */}
            <div className="mt-6 pl-3 border-l-2 border-accent/30">
              <blockquote className="font-body text-ink-light text-sm italic leading-relaxed">
                &ldquo;A good book has no ending.&rdquo;
              </blockquote>
              <cite className="font-caption text-ink-faded text-xs italic tracking-[0.03em] not-italic block mt-1">
                — R.L. Stevenson
              </cite>
            </div>
          </div>

          {/* ── Article 4: Music Review (1 col) ── */}
          <div className="md:border-r border-rule md:pr-gutter">
            {remainder[2] && (
              <article>
                <h3 className="font-headline text-ink text-lg md:text-[18px] font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
                  {remainder[2].headline}
                </h3>
                {remainder[2].subheadline && (
                  <p className="font-headline text-ink-light text-sm italic leading-snug mb-2">
                    {remainder[2].subheadline}
                  </p>
                )}
                <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mb-2">
                  {remainder[2].dateline}
                </p>
                <div className="drop-cap font-body text-ink text-[15px] leading-relaxed body-text">
                  {remainder[2].body.split('\n\n')[0]}
                </div>
                <p className="font-body text-ink-light text-[11px] small-caps tracking-[0.1em] text-right mt-2">
                  {remainder[2].byline}
                </p>
              </article>
            )}
          </div>

          {/* ── Coming Events sidebar (1 col) ── */}
          <div>
            <h3 className="font-headline text-ink text-sm small-caps tracking-[0.15em] font-bold text-center mb-4">
              Coming Attractions
            </h3>
            <div className="border-t-2 border-ink mb-0.5" />
            <div className="border-t border-rule mb-4" />

            <div className="space-y-3">
              {comingEvents.map((event, idx) => (
                <div
                  key={idx}
                  className={`py-2 px-3 ${
                    idx % 2 === 0 ? 'bg-paper-dark/40' : 'bg-transparent'
                  }`}
                >
                  <p className="font-body text-ink text-xs font-semibold mb-0.5">
                    {event.date}
                  </p>
                  <p className="font-body text-ink-light text-xs leading-relaxed italic">
                    {event.description}
                  </p>
                </div>
              ))}
            </div>

            {/* Mini music note */}
            <div className="mt-6 text-center">
              <p
                className="text-accent/40 text-2xl"
                style={{ fontFamily: 'Georgia, serif' }}
              >
                &#9836; &#9836; &#9836;
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ════════════════════ ARTICLE 5: Full width essay ════════════════════ */}
      {remainder[3] && (
        <section className="mb-10">
          <div className="border-t border-rule mb-6" />
          <article className="max-w-4xl mx-auto">
            <h3 className="font-headline text-ink text-xl md:text-[22px] font-bold leading-tight mb-2 text-center hover:text-accent transition-colors duration-200 cursor-pointer">
              {remainder[3].headline}
            </h3>
            {remainder[3].subheadline && (
              <p className="font-headline text-ink-light text-base italic leading-snug mb-3 text-center">
                {remainder[3].subheadline}
              </p>
            )}
            <p className="font-caption text-ink-faded text-xs italic text-center tracking-[0.03em] mb-6">
              {remainder[3].dateline}
            </p>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-x-gutter gap-y-4 max-w-3xl mx-auto">
              <div className="lg:border-r border-rule lg:pr-gutter">
                <div className="drop-cap font-body text-ink text-base leading-relaxed body-text">
                  {remainder[3].body.split('\n\n')[0]}
                </div>
              </div>
              <div>
                <p className="font-body text-ink text-base leading-relaxed body-text">
                  {remainder[3].body.split('\n\n')[1]}
                </p>
              </div>
            </div>

            <p className="font-body text-ink-light text-xs small-caps tracking-[0.1em] text-right mt-4 max-w-3xl mx-auto">
              {remainder[3].byline}
            </p>
          </article>
        </section>
      )}

      {/* ════════════════════ PAGE FOOTER ════════════════════ */}
      <div className="mt-12 pt-6 border-t border-rule">
        <div className="flex items-center justify-center gap-3">
          <img src="/section-fleuron.svg" alt="" className="w-3 h-3 opacity-50" />
          <span className="font-body text-ink-light text-sm small-caps tracking-[0.15em]">
            — 11 —
          </span>
          <img src="/section-fleuron.svg" alt="" className="w-3 h-3 opacity-50" />
        </div>
      </div>
    </NewspaperPage>
  );
}

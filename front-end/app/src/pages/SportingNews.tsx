import { useContentStore } from '@/store/contentStore';
import Masthead from '@/components/Masthead';
import SectionHeader from '@/components/SectionHeader';
import EngravingImage from '@/components/EngravingImage';
import NewspaperPage from '@/components/NewspaperPage';
import DropCap from '@/components/DropCap';

/* ── racing tips data ──────────────────────────────────────── */
const racingTips = [
  { race: 'Gold Cup', horse: 'DORILAS', odds: '3-1', note: 'favourite, well worth the price' },
  { race: "St. James's Palace Stakes", horse: 'THUNDERBOLT', odds: '6-1', note: 'each way' },
  { race: 'Wokingham Stakes', horse: 'FAIR MAID', odds: '10-1', note: 'good value' },
];

/* ── fixtures table data ───────────────────────────────────── */
const fixtures = [
  { date: 'July 15', event: 'Varsity Cricket Match', location: "Lord's Ground" },
  { date: 'July 18-19', event: 'County Championship', location: 'The Oval' },
  { date: 'July 22', event: 'Royal Ascot Gold Cup', location: 'Ascot Racecourse' },
  { date: 'July 25', event: "St. James's Palace Stakes", location: 'Ascot Racecourse' },
  { date: 'July 29', event: 'Wimbledon Lawn Tennis Final', location: 'All England Club' },
];

/* ── cricket score data ────────────────────────────────────── */
const cricketScores = [
  { team: 'AUSTRALIA', innings: 'First Innings', runs: '194 all out', topBat: 'Trumble 62, Noble 34', bowling: 'Hirst 4-52, Richardson 3-48' },
  { team: 'ENGLAND', innings: 'First Innings', runs: '267 for 5', topBat: 'Foster 121*, MacLaren 48', bowling: 'Trumble 3-71' },
];

/* ── county results data ───────────────────────────────────── */
const countyResults = [
  'Yorkshire 312 & 156 beat Surrey 198 & 145 by 125 runs',
  'Lancashire 289 & 201 beat Kent 245 & 156 by 89 runs',
  'Sussex 198 & 176 drew with Nottinghamshire 267 & 107-5',
];

export default function SportingNews() {
  const { getArticlesByCategory } = useContentStore();
  const sportsArticles = getArticlesByCategory('sports');

  const leadArticle = sportsArticles[0];    // Gentlemen v. Players at Lord's
  const racingArticle = sportsArticles[1];  // Derby Day
  // Additional sports articles: rowing (2), tennis (3), rugby (4)

  return (
    <NewspaperPage>
      <Masthead />

      <SectionHeader
        title="\u2766 SPORTING INTELLIGENCE \u2766"
        subtitle="CRICKET \u00b7 THE TURF \u00b7 ROWING \u00b7 ATHLETICS \u00b7 YACHTING"
      />

      {/* ════════════════ TOP ROW: Cricket + Racing + Fixtures ════════════════ */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-[var(--gutter)] mb-8">

        {/* ── Cricket Lead (2 cols) ── */}
        <div className="lg:col-span-2">
          {leadArticle && (
            <article>
              <h2 className="font-headline text-ink text-xl md:text-2xl font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
                Australia All Out for 194 — England Take Command at Lord's
              </h2>
              <p className="font-headline text-ink-light text-sm md:text-base italic leading-snug mb-2">
                Trumble's bowling wreaks havoc but Foster's 121 steadies the English innings
              </p>
              <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mb-3">
                {"Lord's Cricket Ground, June 13"}
              </p>

              {/* Cricket engraving */}
              <EngravingImage
                src="/engraving-sports-01.jpg"
                alt="Cricket match at Lord's"
                caption={"A moment from today's play at Lord's — Mr. Foster drives to the boundary"}
                className="my-3"
              />

              {/* Score box */}
              <ScoreBox />

              {/* Body with drop cap */}
              <p className="font-body text-ink text-[15px] leading-relaxed body-text mt-4">
                <DropCap>A</DropCap>
                magnificent contest unfolded at the headquarters of cricket yesterday, as England and Australia battled for supremacy in the opening match of the Test series. The Australian eleven, winning the toss, elected to bat upon a wicket that promised pace and carry, though the humid atmosphere suggested some movement for the seam bowlers in the early hour.
              </p>
              <p className="font-body text-ink text-[15px] leading-relaxed body-text mt-3">
                The visitors' innings began disastrously, with both openers dismissed without scoring by the excellent bowling of Mr. Hirst and Mr. Richardson. A brief recovery was effected by Mr. Trumble, who struck a defiant 62, and Mr. Noble, whose 34 provided some respectability to the total. Nevertheless, the Australian side was dismissed for the modest score of 194, a total that seemed scarcely adequate on so true a pitch.
              </p>
              <p className="font-body text-ink text-[15px] leading-relaxed body-text mt-3">
                England's reply commenced under the lengthening shadows of the afternoon, and soon found itself in difficulties at 87 for four. It was then that Mr. Foster, the Surrey amateur, played one of the great Test innings, finishing the day unbeaten on 121. His batting combined classical defence with daring attack, and the crowd rose to him repeatedly as he dispatched the Australian bowling to all parts of the ground.
              </p>

              <p className="font-body text-ink-light text-[12px] small-caps tracking-[0.15em] mt-3 font-semibold text-right">
                OLD CRICKETER
              </p>
            </article>
          )}
        </div>

        {/* ── Racing (2 cols) ── */}
        <div className="lg:col-span-2 border-t lg:border-t-0 lg:border-l border-rule pt-6 lg:pt-0 lg:pl-[var(--gutter)]">
          {racingArticle && (
            <article>
              <h2 className="font-headline text-ink text-xl md:text-2xl font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
                Royal Ascot Opens Monday — The Finest Fields in Memory
              </h2>
              <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mb-3">
                {"Ascot, June 14"}
              </p>

              {/* Racing engraving */}
              <EngravingImage
                src="/engraving-sports-02.jpg"
                alt="Horse race at Ascot"
                caption="The Gold Cup field rounding Tattenham Corner in last year's thrilling renewal"
                className="my-3"
              />

              <p className="font-body text-ink text-[15px] leading-relaxed body-text">
                <DropCap>T</DropCap>
                he Royal Meeting at Ascot commences on Monday next under the most favourable auspices. The entries for the principal events are of exceptionally high quality, and the Turf world anticipates a week of racing that will long be remembered. His Majesty the King has signified his intention to be present throughout the meeting, and the Royal party will include many distinguished foreign guests.
              </p>
              <p className="font-body text-ink text-[15px] leading-relaxed body-text mt-3">
                The Gold Cup, the blue riband of the meeting, has attracted a field of eleven, headed by the favourite Dorilas, owned by Mr. Leopold de Rothschild. The three-year-old colt has been in the most impressive form this season, winning the Lingfield Derby Trial by four lengths, and his backers are confident that he will justify his position at the head of the market.
              </p>

              {/* Racing tip box */}
              <div
                className="mt-5 p-4 border-[2px] bg-paper-dark"
                style={{ borderStyle: 'double', borderColor: 'var(--rule)' }}
              >
                <p className="font-headline text-ink text-sm font-bold small-caps tracking-[0.15em] text-center mb-3">
                  THE TIPSTER'S SELECTIONS
                </p>
                <p className="font-caption text-ink-faded text-[11px] italic text-center mb-3">
                  By Turf Commissioner
                </p>
                <div className="border-t border-rule mb-3" />
                {racingTips.map((tip) => (
                  <div key={tip.horse} className="mb-2 last:mb-0">
                    <p className="font-body text-[13px] leading-snug">
                      <span className="text-ink font-semibold">{tip.race}:</span>{' '}
                      <span className="font-bold" style={{ color: 'var(--accent)' }}>{tip.horse}</span>{' '}
                      <span className="text-ink-light">({tip.odds}{tip.note ? `, ${tip.note}` : ''})</span>
                    </p>
                  </div>
                ))}
              </div>

              <p className="font-body text-ink-light text-[12px] small-caps tracking-[0.15em] mt-3 font-semibold text-right">
                TURF CORRESPONDENT
              </p>
            </article>
          )}
        </div>

        {/* ── Fixtures Sidebar (1 col) ── */}
        <div className="lg:col-span-1 border-t lg:border-t-0 lg:border-l border-rule pt-6 lg:pt-0 lg:pl-[var(--gutter)]">
          <FixturesSidebar />
        </div>
      </div>

      {/* ════════════════ BOTTOM ROW: 4 articles ════════════════ */}
      <div className="border-t-2 border-ink mb-0.5 mt-4" />
      <div className="border-t border-rule mb-6" />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-[var(--gutter)]">
        {/* Rowing */}
        <article className="lg:border-r lg:border-rule lg:pr-[var(--gutter)]">
          <h3 className="font-headline text-ink text-lg font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
            Oxford Crew in Fine Fettle for Boat Race
          </h3>
          <p className="font-caption text-ink-faded text-[11px] italic tracking-[0.03em] mb-2">
            {"Putney, June 12"}
          </p>
          <div className="my-2 overflow-hidden">
            <img
              src="/engraving-sports-02.jpg"
              alt="Rowing crews training at Putney"
              className="w-full h-auto object-cover"
              loading="lazy"
              style={{ maxHeight: '120px', objectPosition: 'center 30%' }}
            />
          </div>
          <p className="font-body text-ink text-[13px] leading-relaxed">
            The Oxford University Boat Club has completed its final week of training on the Thames at Putney, and the Dark Blue crew is reported to be in excellent condition for the annual contest against Cambridge. Stroke Mr. R. C. Bourne has had his men rowing with remarkable precision, and the times recorded in practice rows suggest a formidable performance on race day.
          </p>
        </article>

        {/* Athletics */}
        <article className="lg:border-r lg:border-rule lg:pr-[var(--gutter)]">
          <h3 className="font-headline text-ink text-lg font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
            AAA Championships — Record Entries Received
          </h3>
          <p className="font-caption text-ink-faded text-[11px] italic tracking-[0.03em] mb-2">
            {"Stamford Bridge, June 11"}
          </p>
          <p className="font-body text-ink text-[13px] leading-relaxed">
            The Amateur Athletic Association announces that entries for the forthcoming championships at Stamford Bridge have exceeded all previous records. Some four hundred athletes will compete across twenty events, including the marquee contests of the 100 yards, one mile, and hammer throw. Mr. Reggie Walker, the South African sprinter, is entered for the furlong, and the public eagerly anticipates his clash with Mr. J. P. Stark of Edinburgh University.
          </p>
          <p className="font-body text-ink text-[13px] leading-relaxed mt-2">
            The steeplechase, a recent addition to the championship programme, has attracted a field of twenty, and the spectators are promised a thrilling contest over the water jumps.
          </p>
        </article>

        {/* Yachting */}
        <article className="lg:border-r lg:border-rule lg:pr-[var(--gutter)]">
          <h3 className="font-headline text-ink text-lg font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
            Cowes Week Programme Announced
          </h3>
          <p className="font-caption text-ink-faded text-[11px] italic tracking-[0.03em] mb-2">
            {"Cowes, June 10"}
          </p>
          <div className="my-2 overflow-hidden">
            <img
              src="/engraving-sports-01.jpg"
              alt="Yachts racing at Cowes"
              className="w-full h-auto object-cover"
              loading="lazy"
              style={{ maxHeight: '120px', objectPosition: 'center 60%' }}
            />
          </div>
          <p className="font-body text-ink text-[13px] leading-relaxed">
            The Royal Yacht Squadron has published the sailing programme for the annual Cowes Week regatta, which commences on the first of August. The entries include His Majesty the King's yacht Britannia, the Prince of Wales's cutter, and a host of distinguished vessels from the principal yacht clubs of Europe.
          </p>
        </article>

        {/* Sporting Cartoon */}
        <article>
          <div
            className="border-[2px] p-3 bg-paper-dark"
            style={{ borderStyle: 'solid', borderColor: 'var(--rule)' }}
          >
            <div className="overflow-hidden mb-2">
              <img
                src="/engraving-sports-02.jpg"
                alt="Sporting cartoon"
                className="w-full h-auto object-cover"
                loading="lazy"
                style={{ maxHeight: '200px', objectPosition: 'center 70%', filter: 'grayscale(100%) contrast(1.1) sepia(15%)' }}
              />
            </div>
            <p className="font-caption text-ink-light text-[12px] italic text-center leading-tight">
              {"The Anxious Racegoer: 'I say, cabby \u2014 can you get me to Ascot in time for the Gold Cup?'"}
            </p>
          </div>
        </article>
      </div>

      {/* Page footer */}
      <div className="mt-12 pt-6 border-t border-rule">
        <div className="flex items-center justify-center gap-4">
          <div className="border-t border-rule flex-1 max-w-[100px]" />
          <span className="font-body text-ink-faded text-sm small-caps tracking-[0.15em]">— 19 —</span>
          <img src="/section-fleuron.svg" alt="" className="w-3 h-3 opacity-40" />
          <span className="font-body text-ink-faded text-sm small-caps tracking-[0.15em]">— 20 —</span>
          <div className="border-t border-rule flex-1 max-w-[100px]" />
        </div>
      </div>
    </NewspaperPage>
  );
}

/* ── Score Box ─────────────────────────────────────────────── */
function ScoreBox() {
  return (
    <div
      className="mt-4 p-3 border bg-paper-dark"
      style={{ borderColor: 'var(--rule)', borderWidth: '2px', borderStyle: 'double' }}
    >
      <p className="font-headline text-ink text-[12px] font-bold small-caps tracking-[0.15em] text-center mb-2">
        SCOREBOARD
      </p>
      <div className="border-t border-rule mb-2" />
      {cricketScores.map((score) => (
        <div key={score.team} className="mb-2 last:mb-0">
          <div className="flex items-baseline justify-between flex-wrap gap-x-2">
            <span className="font-body text-ink text-[13px] font-bold small-caps tracking-[0.1em]">
              {score.team}
            </span>
            <span className="font-body text-ink text-[13px] font-semibold">
              {score.runs}
            </span>
          </div>
          <p className="font-body text-ink-light text-[11px] leading-snug mt-0.5">
            ({score.topBat}; {score.bowling})
          </p>
        </div>
      ))}
    </div>
  );
}

/* ── Fixtures Sidebar ──────────────────────────────────────── */
function FixturesSidebar() {
  return (
    <div className="bg-paper-dark p-3 border border-rule">
      <p className="font-headline text-ink text-sm font-bold small-caps tracking-[0.15em] text-center mb-3">
        FIXTURES & RESULTS
      </p>

      {/* Fixtures table */}
      <div className="border border-rule mb-3">
        <table className="w-full border-collapse">
          <thead>
            <tr className="border-b border-rule bg-paper">
              <th className="font-body text-[11px] font-bold small-caps tracking-[0.1em] text-left p-1.5 border-r border-rule">
                Date
              </th>
              <th className="font-body text-[11px] font-bold small-caps tracking-[0.1em] text-left p-1.5">
                Event
              </th>
            </tr>
          </thead>
          <tbody>
            {fixtures.map((f, i) => (
              <tr key={i} className="border-b border-rule/60 last:border-b-0">
                <td className="font-body text-ink text-[11px] font-semibold p-1.5 border-r border-rule whitespace-nowrap">
                  {f.date}
                </td>
                <td className="font-body text-ink-light text-[11px] p-1.5 leading-tight">
                  {f.event}
                  <br />
                  <span className="text-ink-faded italic">{f.location}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* County results */}
      <div className="border-t border-rule pt-2">
        <p className="font-body text-ink text-[11px] font-bold small-caps tracking-[0.1em] mb-1.5">
          County Championship
        </p>
        {countyResults.map((result, i) => (
          <p key={i} className="font-body text-ink-light text-[11px] leading-snug mb-1 last:mb-0">
            {result}
          </p>
        ))}
      </div>

      {/* Upcoming */}
      <div className="border-t border-rule pt-2 mt-2">
        <p className="font-body text-ink text-[11px] font-bold small-caps tracking-[0.1em] mb-1.5">
          Coming Fixtures
        </p>
        <p className="font-body text-ink text-[11px] leading-snug">
          June 17 — England v. Australia (2nd Day), Lord's
        </p>
        <p className="font-body text-ink text-[11px] leading-snug mt-1">
          June 18 — Oxford v. Cambridge Boat Race, Putney
        </p>
        <p className="font-body text-ink text-[11px] leading-snug mt-1">
          June 19 — Royal Ascot (Day 2), Gold Cup
        </p>
        <p className="font-body text-ink text-[11px] leading-snug mt-1">
          June 20 — Wimbledon Championships begin
        </p>
      </div>
    </div>
  );
}

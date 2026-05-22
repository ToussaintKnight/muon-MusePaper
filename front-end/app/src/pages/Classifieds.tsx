import { useContentStore } from '@/store/contentStore';
import Masthead from '@/components/Masthead';
import SectionHeader from '@/components/SectionHeader';
import NewspaperPage from '@/components/NewspaperPage';

/* ── period ad data (images + copy) ────────────────────────── */
const adsWithImages = [
  {
    id: 'bovril',
    image: '/ad-bovril.jpg',
    name: 'BOVRIL',
    tagline: 'The Great Strength Giver — Gives Vigour and Vitality',
    price: 'Sixpence per jar — All Chemists and Grocers',
  },
  {
    id: 'pears',
    image: '/ad-pears-soap.jpg',
    name: "PEARS' SOAP",
    tagline: 'For the Complexion — The Perfection of Purity',
    price: 'Recommended by the Medical Profession — 6d. per tablet',
  },
  {
    id: 'railway',
    image: '/ad-railway.jpg',
    name: 'GREAT WESTERN RAILWAY',
    tagline: 'Visit the West Country — Express trains to Exeter, Plymouth, and Penzance',
    price: 'Fares from 10s. 6d. return',
  },
  {
    id: 'corsets',
    image: '/ad-corsets.jpg',
    name: 'THE PERFECT FORM',
    tagline: "Madame Celeste's Patent Corsets combine elegance with comfort. Scientifically designed to give the fashionable silhouette without constriction. Every lady of taste should inspect our new Summer range.",
    price: '14, Regent Street, London, W.',
  },
  {
    id: 'tonic',
    image: '/ad-tonic.jpg',
    name: "DR. PERCIVAL'S VEGETABLE LIFE TONIC",
    tagline: 'Restores Vitality, Renews the Blood — A Positive Remedy for Nervous Debility',
    price: 'Beware of Imitations — Insist on the Genuine',
  },
  {
    id: 'haberdashery',
    image: '/ad-haberdashery.jpg',
    name: 'SCOTT & CO., GENTLEMEN\'S HABERDASHERS',
    tagline: 'Hats, Gloves, Cravats, and Neckwear of the First Quality',
    price: '22, Jermyn Street, St. James\'s',
  },
];

/* ── personal notices ──────────────────────────────────────── */
const notices = [
  {
    label: 'WANTED',
    heading: 'A Governess',
    body: 'For three children aged 6, 8, and 10. Must be proficient in French, Music, and the usual accomplishments. Apply with references to Mrs. A., care of this office.',
  },
  {
    label: 'FOR SALE',
    heading: 'A Piano-Forte',
    body: "A Broadwood grand piano in rosewood case, four years old, excellent condition. Owner departing for India. \u00a345. Enquire at 17, Cadogan Square, S.W.",
  },
  {
    label: 'LOST',
    heading: 'A Gold Watch',
    body: 'On Tuesday last, between Hyde Park Corner and Piccadilly, a gentleman\'s gold hunter watch, engraved with initials "J.R.E." on the case. A reward of two guineas will be paid for its return to the porter\'s lodge at the Athenaeum Club.',
  },
  {
    label: 'PERSONAL',
    heading: 'With Thanks',
    body: 'Mrs. Eleanor Hartley desires to express her sincere gratitude to the many friends and well-wishers who sent messages of condolence following the passing of her late husband, Mr. Reginald Hartley.',
  },
];

export default function Classifieds() {
  const { getArticlesByCategory } = useContentStore();
  const classifiedArticles = getArticlesByCategory('classifieds');

  return (
    <NewspaperPage>
      <Masthead />

      <SectionHeader
        title="\u2766 ADVERTISEMENTS \u2766"
        subtitle="ADVERTISERS ARE INVITED TO INSPECT OUR RATES \u2014 APPLY AT THE OFFICE"
      />

      {/* ── Ad Grid: 2 columns \u00d7 3 rows on desktop ── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-[var(--gutter)] mb-12">
        {adsWithImages.map((ad) => (
          <AdBox key={ad.id}>
            <AdImage src={ad.image} alt={ad.name} />
            <p className="font-headline text-ink text-base md:text-lg font-bold text-center mt-3 leading-tight">
              {ad.name}
            </p>
            <p className="font-body text-ink-light text-[12px] italic text-center mt-2 leading-snug">
              {ad.tagline}
            </p>
            <p className="font-body text-ink-faded text-[11px] text-center mt-2 small-caps tracking-[0.1em]">
              {ad.price}
            </p>
          </AdBox>
        ))}
      </div>

      {/* ── Personal Notices Section ── */}
      <div className="mt-10 mb-6">
        <div className="w-full my-6">
          <div className="border-t-2 border-ink mb-0.5" />
          <div className="border-t border-rule mb-3" />
          <div className="flex items-center justify-center gap-3">
            <img src="/section-fleuron.svg" alt="" className="w-4 h-4 opacity-60" />
            <h2 className="font-headline text-ink text-sm md:text-lg font-bold small-caps tracking-[0.15em] text-center">
              {"\u2766 PERSONAL NOTICES & TRADE ANNOUNCEMENTS \u2766"}
            </h2>
            <img src="/section-fleuron.svg" alt="" className="w-4 h-4 opacity-60" />
          </div>
          <p className="text-center font-body text-[10px] md:text-xs small-caps text-ink-faded mt-2 tracking-[0.2em]">
            (One Shilling and Sixpence for Six Words)
          </p>
          <div className="border-t border-rule mt-3 mb-0.5" />
          <div className="border-t-2 border-ink" />
        </div>
      </div>

      {/* Notices grid: 1 col mobile, 2 col tablet, 4 col desktop */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-[var(--gutter)]">
        {notices.map((notice) => (
          <div
            key={notice.label}
            className="border-2 border-rule p-4 bg-paper-dark"
          >
            <p className="font-headline text-ink text-[13px] font-bold small-caps tracking-[0.15em] mb-2">
              {notice.label} — {notice.heading}
            </p>
            <p className="font-body text-ink-light text-[13px] leading-relaxed">
              {notice.body}
            </p>
          </div>
        ))}
      </div>

      {/* ── Also display any classifieds from content store ── */}
      {classifiedArticles.length > 0 && (
        <div className="mt-12">
          <div className="border-t border-rule/60 my-6" />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-[var(--gutter)]">
            {classifiedArticles.map((article) => (
              <div
                key={article.id}
                className="border-2 border-rule p-4 bg-paper"
              >
                <p className="font-headline text-ink text-base font-bold text-center">
                  {article.headline}
                </p>
                {article.subheadline && (
                  <p className="font-body text-ink-light text-[12px] italic text-center mt-1">
                    {article.subheadline}
                  </p>
                )}
                {article.image && (
                  <div className="my-3">
                    <img
                      src={`/${article.image}`}
                      alt={article.headline}
                      className="w-full h-auto object-cover"
                      loading="lazy"
                    />
                  </div>
                )}
                <p className="font-body text-ink-light text-[13px] leading-relaxed mt-2">
                  {article.body}
                </p>
                {article.caption && (
                  <p className="font-caption text-ink-faded text-[11px] italic text-center mt-2">
                    {article.caption}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </NewspaperPage>
  );
}

/* ── sub-components ────────────────────────────────────────── */

function AdBox({ children }: { children: React.ReactNode }) {
  return (
    <div
      className="
        relative border-[2px] p-4 bg-paper
        transition-all duration-300 hover:scale-[1.01]
      "
      style={{ borderStyle: 'double', borderColor: 'var(--rule)' }}
    >
      {/* Decorative corner flourishes */}
      <CornerFlourish position="tl" />
      <CornerFlourish position="tr" />
      <CornerFlourish position="bl" />
      <CornerFlourish position="br" />
      {children}
    </div>
  );
}

function CornerFlourish({ position }: { position: 'tl' | 'tr' | 'bl' | 'br' }) {
  const posClass =
    position === 'tl'
      ? '-top-1 -left-1'
      : position === 'tr'
        ? '-top-1 -right-1 scale-x-[-1]'
        : position === 'bl'
          ? '-bottom-1 -left-1 scale-y-[-1]'
          : '-bottom-1 -right-1 scale-x-[-1] scale-y-[-1]';

  return (
    <div className={`absolute ${posClass} w-3 h-3 pointer-events-none`}>
      <svg viewBox="0 0 12 12" fill="none" className="w-full h-full">
        <path
          d="M0 12V0C0 0 2 2 4 2C6 2 8 0 10 0C10 0 10 4 8 6C6 8 0 12 0 12Z"
          fill="var(--ink-faded)"
          opacity="0.35"
        />
      </svg>
    </div>
  );
}

function AdImage({ src, alt }: { src: string; alt: string }) {
  return (
    <div className="overflow-hidden">
      <img
        src={src}
        alt={alt}
        className="w-full h-auto object-cover transition-transform duration-300 hover:scale-[1.02]"
        loading="lazy"
      />
    </div>
  );
}

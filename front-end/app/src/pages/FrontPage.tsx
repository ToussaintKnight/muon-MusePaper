import { useContentStore } from '@/store/contentStore';
import Masthead from '@/components/Masthead';
import SectionHeader from '@/components/SectionHeader';
import ArticleBlock from '@/components/ArticleBlock';
import EngravingImage from '@/components/EngravingImage';
import NewspaperPage from '@/components/NewspaperPage';

export default function FrontPage() {
  const articles = useContentStore((state) => state.articles);

  const frontArticles = articles.filter((a) => a.category === 'front');
  const leadArticle = frontArticles[0];
  const secondaryHeadlines = frontArticles.slice(1);

  return (
    <NewspaperPage>
      {/* Masthead Band */}
      <Masthead />

      {/* Latest Intelligence bar */}
      <div className="my-6">
        <div className="border-t-2 border-ink" />
        <div className="border-b border-ink py-2 flex items-center justify-center">
          <div className="flex items-center gap-2">
            <img src="/section-fleuron.svg" alt="" className="w-3 h-3 opacity-60" />
            <span className="font-headline text-ink text-xs md:text-sm small-caps tracking-[0.15em] font-bold">
              Latest Intelligence
            </span>
            <img src="/section-fleuron.svg" alt="" className="w-3 h-3 opacity-60" />
          </div>
        </div>
        <div className="flex flex-wrap items-center justify-center gap-x-3 md:gap-x-6 py-2 border-b border-ink">
          {['Europe', 'The Orient', 'The Americas', 'The Empire', 'At Home'].map((region) => (
            <span
              key={region}
              className="font-body text-[9px] md:text-[11px] small-caps text-ink-faded tracking-[0.2em]"
            >
              {region}
            </span>
          ))}
        </div>
      </div>

      {/* Four-Column Secondary Headlines */}
      <section className="mb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-x-gutter gap-y-4">
          {secondaryHeadlines.map((article, idx) => (
            <div
              key={article.id}
              className={idx < secondaryHeadlines.length - 1 ? 'lg:border-r border-rule pr-gutter' : ''}
            >
              <ArticleBlock article={article} variant="teaser" />
            </div>
          ))}
        </div>
      </section>

      {/* Decorative rule */}
      <div className="my-6">
        <div className="border-t-2 border-ink mb-0.5" />
        <div className="border-t border-rule" />
      </div>

      {/* Hero Engraving */}
      <section className="mb-8">
        <EngravingImage
          src="/hero-engraving-front.jpg"
          alt="Houses of Parliament"
          caption="The Houses of Parliament at the close of the evening session — a scene familiar to every Londoner"
        />
      </section>

      {/* Decorative rule */}
      <div className="my-6">
        <div className="border-t-2 border-ink mb-0.5" />
        <div className="border-t border-rule" />
      </div>

      {/* Lead Article */}
      {leadArticle && (
        <section className="mb-8">
          {/* Lead headline */}
          <h2 className="font-headline text-ink text-3xl md:text-4xl lg:text-[48px] font-black uppercase text-center leading-tight tracking-[-0.01em] mb-3">
            {leadArticle.headline}
          </h2>
          {leadArticle.subheadline && (
            <p className="font-headline text-ink-light text-base md:text-lg lg:text-xl italic text-center leading-snug mb-3 max-w-3xl mx-auto">
              {leadArticle.subheadline}
            </p>
          )}
          <p className="font-caption text-ink-faded text-xs italic text-center tracking-[0.03em] mb-6">
            {leadArticle.dateline}
          </p>

          {/* Lead article body - 3 columns on desktop */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-x-gutter">
            {/* Column 1 */}
            <div className="lg:border-r border-rule lg:pr-gutter">
              <div className="drop-cap font-body text-ink text-base leading-relaxed body-text">
                {leadArticle.body.split('\n\n')[0]}
              </div>
            </div>
            {/* Column 2 */}
            <div className="lg:border-r border-rule lg:pr-gutter hidden lg:block">
              <p className="font-body text-ink text-base leading-relaxed body-text">
                {leadArticle.body.split('\n\n')[1]}
              </p>
            </div>
            {/* Column 3 */}
            <div className="hidden lg:block">
              <p className="font-body text-ink text-base leading-relaxed body-text">
                {leadArticle.body.split('\n\n')[2]}
              </p>
            </div>
          </div>

          {/* Mobile: full body text */}
          <div className="lg:hidden mt-4">
            <div className="font-body text-ink text-base leading-relaxed body-text space-y-4">
              {leadArticle.body.split('\n\n').map((paragraph, idx) => (
                <p key={idx} className={idx === 0 ? 'drop-cap' : ''}>
                  {paragraph}
                </p>
              ))}
            </div>
          </div>

          {/* Byline */}
          <p className="font-body text-ink-light text-xs small-caps tracking-[0.1em] text-right mt-4">
            {leadArticle.byline}
          </p>
        </section>
      )}

      {/* Decorative rule */}
      <div className="my-6">
        <div className="border-t-2 border-ink mb-0.5" />
        <div className="border-t border-rule" />
      </div>

      {/* Bottom secondary articles */}
      <section className="mb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-x-gutter gap-y-4">
          {/* Article 5: 1 col */}
          <div className="lg:col-span-1 lg:border-r border-rule lg:pr-gutter">
            <ArticleBlock
              article={{
                id: 'bottom-1',
                headline: 'Irish Home Rule Debate Resumes',
                subheadline: 'Mr. Redmond demands immediate action from the Government',
                dateline: 'From our Parliamentary Reporter, Westminster, June 14',
                byline: 'By Our Parliamentary Reporter',
                body: 'Mr. John Redmond yesterday moved the adjournment of the House to discuss the continued refusal of the Government to introduce a Home Rule Bill for Ireland. In a speech of great passion, he warned that the patience of the Irish people was nearing exhaustion.',
                category: 'front',
                columnSpan: 1,
              }}
              variant="compact"
            />
          </div>

          {/* Article 6: 2 cols with image */}
          <div className="lg:col-span-3 lg:border-r border-rule lg:pr-gutter">
            <ArticleBlock
              article={{
                id: 'bottom-2',
                headline: 'German Emperor Arrives in London',
                subheadline: 'His Majesty Kaiser Wilhelm II received at Buckingham Palace',
                dateline: 'From our Court Correspondent, Buckingham Palace, June 13',
                byline: 'By Our Court Reporter',
                body: 'His Imperial and Royal Majesty Kaiser Wilhelm II, German Emperor and King of Prussia, arrived at Victoria Station yesterday afternoon on his long-anticipated visit to the British court. His Majesty was received by the Prince of Wales and an escort of the Household Cavalry.',
                image: 'engraving-domestic-01.jpg',
                caption: 'The Kaiser\'s arrival at Victoria Station',
                category: 'front',
                columnSpan: 2,
              }}
              variant="compact"
            />
          </div>

          {/* Article 7: 1 col */}
          <div className="lg:col-span-1">
            <ArticleBlock
              article={{
                id: 'bottom-3',
                headline: 'Bank Rate Held at Three Per Cent',
                subheadline: 'City expresses satisfaction at continued monetary ease',
                dateline: 'From our City Correspondent, Threadneedle Street, June 13',
                byline: 'By Our City Editor',
                body: 'The Bank of England has maintained the minimum rate of discount at three per cent for the third consecutive week, a decision that has been received with satisfaction in the City. The money market continues easy, with no unusual demands upon the resources of the banking system.',
                category: 'front',
                columnSpan: 1,
              }}
              variant="compact"
            />
          </div>
        </div>
      </section>

      {/* Section: Classifieds Preview */}
      <SectionHeader title="Notices &amp; Advertisements" />
      <section className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        {[
          { src: '/ad-bovril.jpg', alt: 'Bovril' },
          { src: '/ad-pears-soap.jpg', alt: 'Pears Soap' },
          { src: '/ad-railway.jpg', alt: 'Great Western Railway' },
          { src: '/ad-corsets.jpg', alt: 'The Perfect Form Corset' },
          { src: '/ad-tonic.jpg', alt: 'Dr. Percival\'s Tonic' },
          { src: '/ad-haberdashery.jpg', alt: 'Regent Street Haberdashery' },
        ].map((ad) => (
          <div key={ad.src} className="overflow-hidden">
            <img
              src={ad.src}
              alt={ad.alt}
              className="w-full h-auto object-cover transition-transform duration-300 hover:scale-[1.02] hover:shadow-md"
              loading="lazy"
            />
          </div>
        ))}
      </section>
    </NewspaperPage>
  );
}

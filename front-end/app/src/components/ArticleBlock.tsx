import type { Article } from '@/store/contentStore';

interface ArticleBlockProps {
  article: Article;
  variant?: 'full' | 'compact' | 'teaser';
}

export default function ArticleBlock({ article, variant = 'full' }: ArticleBlockProps) {
  if (variant === 'teaser') {
    return (
      <article className="py-3">
        <h3 className="font-headline text-ink text-base md:text-lg font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
          {article.headline}
        </h3>
        {article.subheadline && (
          <p className="font-body text-ink-light text-sm italic leading-snug mb-2">
            {article.subheadline}
          </p>
        )}
        <div className="border-t border-rule/60 mt-2" />
      </article>
    );
  }

  if (variant === 'compact') {
    return (
      <article className="py-4">
        <h3 className="font-headline text-ink text-lg md:text-xl font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
          {article.headline}
        </h3>
        {article.subheadline && (
          <p className="font-headline text-ink-light text-sm md:text-base italic leading-snug mb-2">
            {article.subheadline}
          </p>
        )}
        <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mb-2">
          {article.dateline}
        </p>
        <p className="font-body text-ink text-sm leading-relaxed body-text">
          {getPreviewText(article.body)}
        </p>
      </article>
    );
  }

  // full variant
  return (
    <article className="py-4">
      <h3 className="font-headline text-ink text-xl md:text-[22px] font-bold leading-tight mb-2 hover:text-accent transition-colors duration-200 cursor-pointer">
        {article.headline}
      </h3>
      {article.subheadline && (
        <p className="font-headline text-ink-light text-base md:text-lg italic leading-snug mb-3">
          {article.subheadline}
        </p>
      )}
      <p className="font-caption text-ink-faded text-xs italic tracking-[0.03em] mb-1">
        {article.dateline}
      </p>
      {article.image && (
        <div className="my-4">
          <img
            src={`/${article.image}`}
            alt={article.headline}
            className="w-full h-auto object-cover"
            loading="lazy"
          />
          {article.caption && (
            <p className="font-caption text-ink-faded text-xs italic text-center mt-2 leading-tight">
              {article.caption}
            </p>
          )}
        </div>
      )}
      <div className="drop-cap font-body text-ink text-base leading-relaxed body-text">
        {article.body.split('\n\n').map((paragraph, idx) => (
          <p key={idx} className={idx === 0 ? 'drop-cap' : ''}>
            {paragraph}
          </p>
        ))}
      </div>
      <p className="font-body text-ink-light text-xs small-caps tracking-[0.1em] text-right mt-3">
        {article.byline}
      </p>
    </article>
  );
}

function getPreviewText(body: string): string {
  const firstParagraph = body.split('\n\n')[0];
  if (firstParagraph.length > 200) {
    return firstParagraph.slice(0, 200) + '...';
  }
  return firstParagraph;
}

import { useState } from 'react';
import { useContentStore } from '@/store/contentStore';

interface ArticleCardProps {
  article: {
    id: string;
    headline: string;
    subheadline: string;
    byline: string;
    dateline: string;
    abstract: string;
    url: string;
    column_span: number;
    imageUrl?: string;
    section: string;
    score?: number;
  };
}

export default function ArticleCard({ article }: ArticleCardProps) {
  const [expanded, setExpanded] = useState(false);
  const clickArticle = useContentStore((s) => s.clickArticle);
  const clicks = useContentStore((s) => s.clicks);
  const isClicked = clicks.has(article.id);

  const handleClick = () => {
    if (!isClicked) {
      clickArticle(article.id);
    }
    setExpanded(!expanded);
  };

  return (
    <article
      className={`
        relative break-inside-avoid
        ${isClicked ? 'article-clicked' : ''}
        ${expanded ? 'article-expanded' : ''}
      `}
      data-section={article.section}
    >
      {/* Ink dot indicator for clicked articles */}
      {isClicked && (
        <div className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-ink opacity-60" />
      )}

      {/* Image */}
      {article.imageUrl && (
        <div className="mb-4 overflow-hidden">
          <img
            src={article.imageUrl}
            alt={article.headline}
            className="w-full h-auto object-cover sepia-[0.25] contrast-125 grayscale-[0.2] brightness-95"
            loading="lazy"
          />
        </div>
      )}

      {/* Headline */}
      <h2 className="font-headline text-ink font-bold leading-tight mb-1 cursor-pointer hover:opacity-80 transition-opacity"
        onClick={handleClick}
        style={{
          fontSize: article.column_span >= 3 ? '2rem' : article.column_span === 2 ? '1.5rem' : '1.1rem',
        }}
      >
        {article.headline}
      </h2>

      {/* Subheadline */}
      {article.subheadline && (
        <p className="font-headline text-ink-light italic text-sm mb-2 leading-snug">
          {article.subheadline}
        </p>
      )}

      {/* Byline & Dateline */}
      <div className="flex items-center gap-2 mb-3 text-[10px] text-ink-faded tracking-wider uppercase">
        <span className="font-body">{article.byline}</span>
        <span className="opacity-40">|</span>
        <span className="font-caption italic">{article.dateline}</span>
      </div>

      {/* Abstract */}
      <div className="font-body text-ink text-[13px] leading-relaxed body-text">
        {article.column_span >= 3 && !expanded ? (
          <div className="drop-cap">{article.abstract}</div>
        ) : (
          <p>{article.abstract}</p>
        )}
      </div>

      {/* Read More / Expand */}
      {!expanded && (
        <button
          onClick={handleClick}
          className="mt-3 text-[11px] font-caption italic text-ink-faded hover:text-ink transition-colors tracking-widest uppercase"
        >
          {isClicked ? 'Read More →' : 'Continue Reading →'}
        </button>
      )}

      {/* Expanded content */}
      {expanded && (
        <div className="mt-4 pt-4 border-t border-rule">
          <p className="font-body text-ink-light text-sm mb-3">
            Full article available at the original source.
          </p>
          <a
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block text-xs font-body small-caps tracking-[0.15em] text-ink border border-ink px-4 py-2 hover:bg-ink hover:text-paper transition-colors"
          >
            Read Original →
          </a>
        </div>
      )}
    </article>
  );
}

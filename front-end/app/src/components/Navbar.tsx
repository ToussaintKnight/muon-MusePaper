import { useState } from 'react';
import { Link, useLocation } from 'wouter';

const sections = [
  { path: '/', label: 'Home' },
  { path: '/foreign', label: 'Foreign' },
  { path: '/domestic', label: 'Domestic' },
  { path: '/colonies', label: 'Colonies' },
  { path: '/commerce', label: 'Commerce' },
  { path: '/arts', label: 'Arts' },
  { path: '/science', label: 'Science' },
  { path: '/society', label: 'Society' },
  { path: '/classifieds', label: 'Classifieds' },
  { path: '/sports', label: 'Sports' },
];

export default function Navbar() {
  const [location] = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <nav className="sticky top-0 z-[100] bg-paper-dark border-b border-rule">
      {/* Desktop nav */}
      <div className="hidden md:flex items-center justify-between max-w-[1400px] mx-auto px-page-margin h-10">
        <span className="font-body text-ink text-xs small-caps tracking-[0.15em] font-semibold">
          The London Morning Chronicle
        </span>
        <div className="flex items-center gap-1">
          {sections.map((section) => (
            <Link
              key={section.path}
              href={section.path}
              className={`font-body text-[11px] lg:text-xs small-caps tracking-[0.15em] px-2 py-1 nav-link-underline transition-colors duration-200 ${
                location === section.path
                  ? 'text-accent font-semibold'
                  : 'text-ink-light hover:text-ink'
              }`}
            >
              {section.label}
            </Link>
          ))}
        </div>
      </div>

      {/* Mobile nav bar */}
      <div className="md:hidden flex items-center justify-between px-4 h-10">
        <span className="font-body text-ink text-[10px] small-caps tracking-[0.15em] font-semibold truncate">
          The London Morning Chronicle
        </span>
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="p-1 text-ink"
          aria-label="Toggle menu"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            {mobileOpen ? (
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M6 18L18 6M6 6l12 12"
              />
            ) : (
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M4 6h16M4 12h16M4 18h16"
              />
            )}
          </svg>
        </button>
      </div>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div className="md:hidden bg-paper-dark border-t border-rule px-4 py-3">
          <div className="flex flex-col gap-1">
            {sections.map((section) => (
              <Link
                key={section.path}
                href={section.path}
                onClick={() => setMobileOpen(false)}
                className={`font-body text-sm small-caps tracking-[0.15em] py-2 px-2 transition-colors duration-200 ${
                  location === section.path
                    ? 'text-accent font-semibold bg-paper/50'
                    : 'text-ink-light hover:text-ink hover:bg-paper/30'
                }`}
              >
                {section.label}
              </Link>
            ))}
          </div>
        </div>
      )}
    </nav>
  );
}

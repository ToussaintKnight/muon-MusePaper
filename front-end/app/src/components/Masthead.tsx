import { Link } from 'wouter';

export default function Masthead() {
  return (
    <header className="bg-masthead-bg text-paper w-full">
      <div className="max-w-[1400px] mx-auto px-4 md:px-page-margin py-6">
        {/* Top ornamental rule */}
        <div className="flex justify-center mb-4">
          <img
            src="/masthead-ornament.svg"
            alt=""
            className="h-[30px] md:h-[45px] opacity-70"
            style={{ filter: 'brightness(0.8)' }}
          />
        </div>

        {/* Newspaper name */}
        <Link href="/" className="block text-center no-underline">
          <h1
            className="font-masthead text-paper text-[32px] md:text-[48px] lg:text-[64px] leading-none tracking-[0.05em] m-0"
            style={{ textShadow: '0 2px 8px rgba(245,240,225,0.1)' }}
          >
            The London Morning Chronicle
          </h1>
        </Link>

        {/* Bottom ornamental rule */}
        <div className="flex justify-center mt-4">
          <img
            src="/masthead-ornament.svg"
            alt=""
            className="h-[30px] md:h-[45px] opacity-70 rotate-180"
            style={{ filter: 'brightness(0.8)' }}
          />
        </div>

        {/* Date line */}
        <div className="text-center mt-4 font-body text-[10px] md:text-xs small-caps text-paper/80">
          <span className="tracking-[0.15em]">
            Saturday, 15th June, 1901 — Vol. CXXIV — No. 18,492 — Price One Penny
          </span>
        </div>
      </div>
    </header>
  );
}

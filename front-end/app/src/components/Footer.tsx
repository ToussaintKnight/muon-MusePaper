export default function Footer() {
  return (
    <footer className="w-full py-8 mt-8 border-t border-rule">
      <div className="max-w-[1400px] mx-auto px-4 md:px-page-margin flex flex-col items-center">
        {/* Decorative double rule */}
        <div className="w-full max-w-md">
          <div className="border-t-2 border-ink mb-0.5" />
          <div className="border-t border-rule mb-6" />
        </div>

        {/* Fleurons and page number */}
        <div className="flex items-center gap-3 mb-3">
          <img src="/section-fleuron.svg" alt="" className="w-3 h-3 opacity-50" />
          <span className="font-body text-ink-light text-sm small-caps tracking-[0.15em]">
            — 1 —
          </span>
          <img src="/section-fleuron.svg" alt="" className="w-3 h-3 opacity-50" />
        </div>

        {/* Copyright */}
        <p className="font-body text-ink-faded text-[11px] small-caps tracking-[0.1em] text-center">
          The London Morning Chronicle — Established 1821
        </p>

        {/* Continued note */}
        <p className="font-caption text-ink-faded/70 text-[10px] italic mt-2">
          [Continued on Page 4]
        </p>
      </div>
    </footer>
  );
}

interface SectionHeaderProps {
  title: string;
  subtitle?: string;
}

export default function SectionHeader({ title, subtitle }: SectionHeaderProps) {
  return (
    <div className="w-full my-6">
      {/* Double rule top */}
      <div className="border-t-2 border-ink mb-0.5" />
      <div className="border-t border-rule mb-3" />

      {/* Title with fleurons */}
      <div className="flex items-center justify-center gap-3">
        <img
          src="/section-fleuron.svg"
          alt=""
          className="w-4 h-4 md:w-5 md:h-5 opacity-60"
        />
        <h2 className="font-headline text-ink text-sm md:text-lg lg:text-2xl font-bold small-caps tracking-[0.15em] text-center">
          {title}
        </h2>
        <img
          src="/section-fleuron.svg"
          alt=""
          className="w-4 h-4 md:w-5 md:h-5 opacity-60"
        />
      </div>

      {/* Subtitle */}
      {subtitle && (
        <p className="text-center font-body text-[10px] md:text-xs small-caps text-ink-faded mt-2 tracking-[0.2em]">
          {subtitle}
        </p>
      )}

      {/* Double rule bottom */}
      <div className="border-t border-rule mt-3 mb-0.5" />
      <div className="border-t-2 border-ink" />
    </div>
  );
}

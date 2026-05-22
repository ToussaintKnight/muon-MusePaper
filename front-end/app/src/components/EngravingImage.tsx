interface EngravingImageProps {
  src: string;
  alt: string;
  caption?: string;
  className?: string;
}

export default function EngravingImage({ src, alt, caption, className = '' }: EngravingImageProps) {
  return (
    <figure className={`my-4 ${className}`}>
      <div className="overflow-hidden">
        <img
          src={src}
          alt={alt}
          className="w-full h-auto object-cover transition-transform duration-300 hover:scale-[1.02] hover:shadow-lg"
          loading="lazy"
        />
      </div>
      {caption && (
        <figcaption className="font-caption text-ink-faded text-xs md:text-[13px] italic text-center mt-2 leading-tight tracking-[0.02em]">
          {caption}
        </figcaption>
      )}
    </figure>
  );
}

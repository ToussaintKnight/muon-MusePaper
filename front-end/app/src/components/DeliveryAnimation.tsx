import { useEffect, useRef, useState } from 'react';
import gsap from 'gsap';

interface DeliveryAnimationProps {
  onComplete: () => void;
  onSkip: () => void;
}

export default function DeliveryAnimation({ onComplete, onSkip }: DeliveryAnimationProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const bikeRef = useRef<HTMLDivElement>(null);
  const paperRef = useRef<HTMLDivElement>(null);
  const [canSkip, setCanSkip] = useState(false);

  useEffect(() => {
    const tl = gsap.timeline({
      onComplete: () => {
        onComplete();
      },
    });

    // 1. Bike enters from left
    tl.fromTo(
      bikeRef.current,
      { x: '-100%', opacity: 0 },
      { x: '30vw', opacity: 1, duration: 2, ease: 'power2.out' }
    );

    // 2. Pause, then throw
    tl.to(bikeRef.current, { x: '35vw', duration: 0.3, ease: 'power1.inOut' });

    // 3. Paper flies from bike to center
    tl.fromTo(
      paperRef.current,
      { x: '35vw', y: '60vh', scale: 0.3, rotation: -15, opacity: 0 },
      { x: '50vw', y: '50vh', scale: 0.6, rotation: 5, opacity: 1, duration: 1, ease: 'back.out(1.2)' },
      '-=0.1'
    );

    // 4. Bike exits
    tl.to(bikeRef.current, { x: '120vw', duration: 1.5, ease: 'power2.in' }, '-=0.8');

    // 5. Paper lands and grows
    tl.to(paperRef.current, {
      x: '50vw',
      y: '50vh',
      scale: 1.2,
      rotation: 0,
      duration: 1,
      ease: 'power2.out',
    });

    // 6. Fade out paper, reveal newspaper
    tl.to(paperRef.current, { opacity: 0, scale: 2, duration: 0.8, ease: 'power2.in' });
    tl.to(containerRef.current, { opacity: 0, duration: 0.5, ease: 'power2.in' });

    // Allow skip after 2 seconds
    const skipTimer = setTimeout(() => setCanSkip(true), 2000);

    return () => {
      tl.kill();
      clearTimeout(skipTimer);
    };
  }, [onComplete]);

  return (
    <div
      ref={containerRef}
      className="fixed inset-0 z-[300] bg-paper overflow-hidden"
      style={{ background: 'linear-gradient(to bottom, #e8e0cc 0%, #f5f0e1 100%)' }}
    >
      {/* Sky */}
      <div className="absolute inset-0 opacity-20" style={{
        backgroundImage: 'url("data:image/svg+xml,%3Csvg width=\'60\' height=\'60\' viewBox=\'0 0 60 60\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'none\' fill-rule=\'evenodd\'%3E%3Cg fill=\'%239C92AC\' fill-opacity=\'0.15\'%3E%3Cpath d=\'M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z\'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")',
      }} />

      {/* Skip button */}
      {canSkip && (
        <button
          onClick={onSkip}
          className="absolute top-4 right-4 z-[301] font-body text-xs small-caps tracking-widest text-ink-faded hover:text-ink transition-colors"
        >
          Skip →
        </button>
      )}

      {/* Bicycle + Newsboy */}
      <div
        ref={bikeRef}
        className="absolute top-1/2 -translate-y-1/2"
        style={{ left: '-200px' }}
      >
        <div className="relative">
          {/* Simple SVG bike */}
          <svg width="120" height="80" viewBox="0 0 120 80" fill="none" className="opacity-80">
            {/* Wheels */}
            <circle cx="20" cy="60" r="18" stroke="#1A1410" strokeWidth="2" fill="none" />
            <circle cx="90" cy="60" r="18" stroke="#1A1410" strokeWidth="2" fill="none" />
            {/* Frame */}
            <path d="M20 60 L45 30 L75 30 L90 60" stroke="#1A1410" strokeWidth="2" fill="none" />
            <path d="M45 30 L35 60" stroke="#1A1410" strokeWidth="2" />
            <path d="M75 30 L70 20" stroke="#1A1410" strokeWidth="2" />
            {/* Handlebars */}
            <path d="M65 20 L80 15" stroke="#1A1410" strokeWidth="2" />
            {/* Seat */}
            <path d="M40 30 L35 25" stroke="#1A1410" strokeWidth="2" />
            {/* Rider body */}
            <circle cx="55" cy="18" r="6" fill="#1A1410" />
            <path d="M55 24 L50 35 L60 35 Z" fill="#1A1410" />
            <path d="M50 35 L45 45" stroke="#1A1410" strokeWidth="3" />
            <path d="M60 35 L65 42" stroke="#1A1410" strokeWidth="3" />
            {/* Cap */}
            <path d="M50 14 L58 12 L60 16" fill="#1A1410" />
          </svg>
        </div>
      </div>

      {/* Flying newspaper */}
      <div
        ref={paperRef}
        className="absolute w-[200px] h-[280px] bg-paper border border-ink shadow-xl"
        style={{
          left: '-100px',
          top: '-100px',
          transformOrigin: 'center center',
          backgroundImage: 'url("/paper-texture.jpg")',
          backgroundSize: 'cover',
        }}
      >
        {/* Mini masthead on flying paper */}
        <div className="p-4">
          <div className="border-b-2 border-ink pb-2 mb-2">
            <div className="font-masthead text-ink text-lg text-center leading-tight">
              The Daily Muse
            </div>
          </div>
          <div className="space-y-2">
            <div className="h-2 bg-ink/10 rounded" />
            <div className="h-2 bg-ink/10 rounded w-4/5" />
            <div className="h-2 bg-ink/10 rounded w-3/5" />
            <div className="h-2 bg-ink/10 rounded w-4/5" />
          </div>
        </div>
      </div>

      {/* Ground line */}
      <div className="absolute bottom-[20vh] left-0 right-0 h-px bg-ink/10" />
    </div>
  );
}

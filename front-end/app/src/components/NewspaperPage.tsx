import type { ReactNode } from 'react';

interface NewspaperPageProps {
  children: ReactNode;
  className?: string;
}

export default function NewspaperPage({ children, className = '' }: NewspaperPageProps) {
  return (
    <div className={`min-h-[100dvh] bg-paper paper-grain ${className}`}>
      <div className="max-w-[1400px] mx-auto px-4 md:px-page-margin pb-12">
        {children}
      </div>
    </div>
  );
}

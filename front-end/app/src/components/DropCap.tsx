import type { ReactNode } from 'react';

interface DropCapProps {
  children: ReactNode;
  className?: string;
}

export default function DropCap({ children, className = '' }: DropCapProps) {
  return (
    <span className={`drop-cap ${className}`}>
      {children}
    </span>
  );
}

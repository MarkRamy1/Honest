import React from 'react';
import { usePreferences } from '../preferences';

export type SkeletonVariant = 'product' | 'review' | 'matrix';

export interface SkeletonGridProps {
  readonly variant: SkeletonVariant;
  readonly count?: number;
}

/**
 * Explicit-variant layout-matching skeleton grid (speed-engineer Area 5 + vercel-composition-patterns).
 */
export function SkeletonGrid({ variant, count = 4 }: Readonly<SkeletonGridProps>) {
  const { t } = usePreferences();
  const items = Array.from({ length: count }, (_, i) => i + 1);

  if (variant === 'review') {
    return (
      <div className="review-grid" role="status" aria-live="polite" aria-label={t('Loading community reviews…')}>
        {items.map((n) => (
          <div
            key={n}
            className="panel review-card skeleton-card"
            style={{ height: 185 }}
            aria-hidden="true"
          />
        ))}
      </div>
    );
  }

  if (variant === 'matrix') {
    return (
      <div className="pricing-matrix-grid" role="status" aria-live="polite" aria-label={t('Loading 3-Tier Pricing Matrix…')}>
        {items.map((n) => (
          <div
            key={n}
            className="matrix-card skeleton-card"
            style={{ height: 340 }}
            aria-hidden="true"
          />
        ))}
      </div>
    );
  }

  return (
    <div className="product-grid" role="status" aria-live="polite" aria-label={t('Loading product')}>
      {items.map((n) => (
        <div className="skeleton-card" key={n} aria-hidden="true" />
      ))}
    </div>
  );
}

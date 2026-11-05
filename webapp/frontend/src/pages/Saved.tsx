import React, { useState } from 'react';
import { usePreferences } from '../preferences';
import type { Product } from '../types';
import { ProductCard } from '../components/ProductCard';
import { Icon } from '../components/Icon';

export interface SavedProps {
  readonly saved: Product[];
  readonly onToggleSave: (product: Product) => void;
  readonly onSelectProduct: (product: Product) => void;
  readonly onNavigateToDashboard: () => void;
}

export function Saved({
  saved,
  onToggleSave,
  onSelectProduct,
  onNavigateToDashboard
}: Readonly<SavedProps>) {
  const { t } = usePreferences();
  const [query, setQuery] = useState('');

  const filteredProducts = saved.filter((p) =>
    p.name.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <div className="eyebrow">{t('THE ONES WORTH COMING BACK TO')}</div>
          <h1>
            {t('Your shortlist')}
            <span className="heading-dot">.</span>
          </h1>
          <p>
            {saved.length} {t('saved')} {saved.length === 1 ? 'product' : 'products'} {t('· Stored on this device')}
          </p>
        </div>
        <button className="button primary" onClick={onNavigateToDashboard}>
          <Icon name="plus" size={18} /> {t('Discover more')}
        </button>
      </div>

      <div className="input-icon saved-search">
        <Icon name="search" />
        <input
          placeholder={t('Search saved products…')}
          aria-label={t('Search saved products')}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>

      {filteredProducts.length ? (
        <div className="product-grid">
          {filteredProducts.map((p) => (
            <ProductCard
              key={p.name}
              product={p}
              saved={true}
              onSave={onToggleSave}
              onSelect={onSelectProduct}
            />
          ))}
        </div>
      ) : (
        <div className="empty-state spacious">
          <div className="large-icon">
            <Icon name="bookmark" size={36} />
          </div>
          <h2>
            {query
              ? t('No matching products')
              : t('Good finds deserve a second look.')}
          </h2>
          <p>
            {query
              ? t('Try another search.')
              : t(
                  'Save a product from the catalog or an analysis to build your personal shortlist.'
                )}
          </p>
          <button className="button primary" onClick={onNavigateToDashboard}>
            {t('Explore products')} <Icon name="arrow" size={17} />
          </button>
        </div>
      )}
    </div>
  );
}

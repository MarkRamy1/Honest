import React from 'react';
import { usePreferences } from '../preferences';
import type { Product } from '../types';
import { Icon } from './Icon';
import { productPhotos } from '../data/mockData';

export interface ProductCardProps {
  readonly product: Product;
  readonly saved: boolean;
  readonly onSave: (product: Product) => void;
  readonly onSelect: (product: Product) => void;
}

function resolveImageUrl(img?: string, category?: string): string | undefined {
  if (!img) {
    const fallback = productPhotos[category || ''];
    return fallback ? fallback.replace('/app/images/', '/images/') : undefined;
  }
  if (img.startsWith('/app/images/')) {
    return img.replace('/app/images/', '/images/');
  }
  return img;
}

export function ProductCard({ product, saved, onSave, onSelect }: Readonly<ProductCardProps>) {
  const { t } = usePreferences();
  const image = resolveImageUrl(product.image, product.category);

  return (
    <article className="product-card">
      <div className="product-visual">
        <button
          className="product-image-button"
          onClick={() => onSelect(product)}
          aria-label={`Analyze ${product.name}`}
        >
          {image ? (
            <img
              src={image}
              alt={product.name}
              width={400}
              height={300}
              loading="lazy"
              decoding="async"
              onError={(e) => {
                e.currentTarget.hidden = true;
              }}
            />
          ) : (
            <Icon name="bag" size={64} />
          )}
        </button>
        <span className="product-tag">{product.category || t('Product')}</span>
        <button
          className={`icon-button save-button ${saved ? 'is-saved' : ''}`}
          aria-label={`${saved ? 'Unsave' : 'Save'} ${product.name}`}
          aria-pressed={saved}
          onClick={(e) => {
            e.stopPropagation();
            onSave(product);
          }}
        >
          <Icon name="bookmark" size={18} />
        </button>
        {((!product.image && image) || product.illustrative) && (
          <span className="image-note">
            {product.illustrative ? t('Design example · reference price') : t('Illustrative photo')}
          </span>
        )}
      </div>
      <div className="product-body">
        <small>{product.brand || t('YOUR NEXT FIND')}</small>
        <button className="product-title" onClick={() => onSelect(product)}>
          {product.name}
        </button>
        <div className="product-bottom">
          <span>
            {product.original_msrp ? (
              <>
                <strong>
                  ${Number(product.original_msrp).toLocaleString('en-US', { minimumFractionDigits: 2 })}
                </strong>
                <small>{t('Reference MSRP')}</small>
              </>
            ) : (
              <small>{t('Ready for a closer look')}</small>
            )}
          </span>
          <button className="circle-link" onClick={() => onSelect(product)} aria-label={`View ${product.name}`}>
            <Icon name="diagonal" />
          </button>
        </div>
      </div>
    </article>
  );
}

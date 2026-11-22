import React, { useState, useEffect } from 'react';
import { usePreferences } from '../preferences';
import type { Page, Product, AnalysisRecord } from '../types';
import { Icon } from '../components/Icon';
import { ProductCard } from '../components/ProductCard';
import { Feedback } from '../components/Feedback';
import { api } from '../services/api';
import { categories, featuredProducts, features, popularScans } from '../data/mockData';

export interface DashboardProps {
  readonly onSelectProduct: (product: Product) => void;
  readonly onNavigate: (page: Page) => void;
  readonly saved: Product[];
  readonly onToggleSave: (product: Product) => void;
  readonly history: AnalysisRecord[];
  readonly onSelectRecord: (record: AnalysisRecord) => void;
}

export function Dashboard({
  onSelectProduct,
  onNavigate,
  saved,
  onToggleSave,
  history,
  onSelectRecord
}: Readonly<DashboardProps>) {
  const { t, language } = usePreferences();
  const isAr = language === 'ar';
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState('All products');
  const [search, setSearch] = useState('');
  const [catalogVisible, setCatalogVisible] = useState(false);
  const [catalogProducts, setCatalogProducts] = useState<Product[]>([]);
  const [loadingCatalog, setLoadingCatalog] = useState(false);
  const [catalogError, setCatalogError] = useState('');

  // Fetch catalog products from API when catalog is visible or search/filter changes
  useEffect(() => {
    if (!catalogVisible) return;
    let isSubscribed = true;
    setLoadingCatalog(true);
    setCatalogError('');

    const searchTerm = search || (filter === 'All products' ? '' : filter);
    api.searchCatalog(searchTerm)
      .then((res) => {
        if (!isSubscribed) return;
        if (res.products) {
          setCatalogProducts(res.products);
        } else {
          setCatalogProducts([]);
        }
      })
      .catch((err) => {
        if (!isSubscribed) return;
        setCatalogError(err.message || 'Failed to load catalog');
      })
      .finally(() => {
        if (isSubscribed) setLoadingCatalog(false);
      });

    return () => {
      isSubscribed = false;
    };
  }, [catalogVisible, filter, search]);

  const handleHeroSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    onSelectProduct({ name: query.trim() });
  };

  const handleCatalogSearchSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const data = new FormData(e.currentTarget);
    setSearch(String(data.get('search') || ''));
  };

  return (
    <div className="page dashboard">
      {/* Hero Section */}
      <section className="dashboard-hero">
        <span className="pill">
          <Icon name="shield" size={13} /> {t('INDEPENDENT SHOPPING INTELLIGENCE · v4.0')}
        </span>
        <h1>{t('Shop Smarter with Honest AI')}</h1>
        <p>{t('Unbiased AI analysis, authentic quality scores, and real-world clarity before you buy.')}</p>

        <form className="hero-search" onSubmit={handleHeroSubmit}>
          <Icon name="search" size={23} />
          <input
            aria-label={t('Product to analyze')}
            placeholder={t('Paste any product link or search item (e.g. Sony WH-1000XM5)…')}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            required
            maxLength={255}
          />
          <button className="button primary" type="submit">
            {t('Analyze Link')} <Icon name="sparkles" size={17} />
          </button>
        </form>

        <div className="popular-scans">
          <span>{t('Popular scans:')}</span>
          {popularScans.map((s) => (
            <button key={s.label} onClick={() => onSelectProduct({ name: s.query })}>
              {t(s.label)}
            </button>
          ))}
        </div>

        {/* Signature Forensic Telemetry Strip (frontend-design: non-templated focal point) */}
        <div className="forensic-telemetry-strip" aria-label={isAr ? 'مؤشرات الفحص الجنائي' : 'Forensic telemetry indicators'}>
          <div className="forensic-telemetry-item">
            <span className="telemetry-code">01 / PRICE_PULSE</span>
            <strong>{isAr ? 'مخطط الأسعار لـ 90 يوماً' : '90-Day Stepped Price Ledger'}</strong>
            <span className="telemetry-metric positive">↓ 14.2% {isAr ? 'كشف الخصم الوهمي' : 'Fake-MSRP Detection'}</span>
          </div>
          <div className="forensic-telemetry-item">
            <span className="telemetry-code">02 / MATERIAL_VLM</span>
            <strong>{isAr ? 'مصفوفة الحقيقة (3 مستويات)' : '3-Tier Material Truth Matrix'}</strong>
            <span className="telemetry-metric">{isAr ? 'أصلي · هاي كوبي · بديل اقتصادي' : 'Original · High-Copy · Budget Dupe'}</span>
          </div>
          <div className="forensic-telemetry-item">
            <span className="telemetry-code">03 / MENA_LOGISTICS</span>
            <strong>{isAr ? 'توافق متاجر مصر والشرق الأوسط' : 'Egypt & MENA Store Telemetry'}</strong>
            <span className="telemetry-metric">{isAr ? 'دفع عند الاستلام · تقسيط 0% · شحن سريع' : 'COD · 0% Installments · 1–3d Express'}</span>
          </div>
        </div>
      </section>

      {/* Feature Quick-Action Cards */}
      <section className="feature-grid" aria-label={t('Shopping tools')}>
        {features.map((f) => (
          <article className="feature-card" key={f.title}>
            <div>
              <span className="feature-icon">
                <Icon name={f.icon} size={25} />
              </span>
              <span className="pill">{f.badge}</span>
            </div>
            <h2>{t(f.title)}</h2>
            <p>{t(f.description)}</p>
            <button className="text-button" onClick={() => onNavigate(f.page as Page)}>
              {t(f.action)} <Icon name="arrow" size={15} />
            </button>
          </article>
        ))}
      </section>

      {/* Recent Research / Catalog */}
      <div className="section-heading">
        <div>
          <h2>{t('Recent Research')}</h2>
          <p>{t('Explore the design collection, or analyze a product of your own.')}</p>
        </div>
        <button className="text-button" onClick={() => setCatalogVisible(!catalogVisible)}>
          {catalogVisible ? t('Design collection') : t('Browse catalog')} <Icon name="arrow" size={15} />
        </button>
      </div>

      {catalogVisible ? (
        <>
          <div className="catalog-toolbar">
            <div className="filter-tabs" aria-label={t('Product categories')}>
              {categories.map((c) => (
                <button
                  key={c}
                  className={filter === c ? 'selected' : ''}
                  onClick={() => {
                    setFilter(c);
                    setSearch('');
                  }}
                >
                  {c === 'tech' ? t('Electronics') : c}
                </button>
              ))}
            </div>

            <form className="catalog-search" onSubmit={handleCatalogSearchSubmit}>
              <Icon name="search" size={17} />
              <input aria-label={t('Search catalog')} name="search" placeholder={t('Search catalog…')} />
              <button className="icon-button" aria-label={t('Search catalog products')}>
                <Icon name="arrow" size={16} />
              </button>
            </form>
          </div>

          {loadingCatalog ? (
            <div className="product-grid">
              {[1, 2, 3, 4].map((n) => (
                <div className="skeleton-card" key={n} aria-label={t('Loading product')} />
              ))}
            </div>
          ) : catalogError ? (
            <Feedback message={catalogError} onRetry={() => setSearch(search)} />
          ) : catalogProducts.length ? (
            <div className="product-grid">
              {catalogProducts.map((p, idx) => (
                <ProductCard
                  key={p.id || idx}
                  product={p}
                  saved={saved.some((s) => s.name === p.name)}
                  onSave={onToggleSave}
                  onSelect={onSelectProduct}
                />
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <Icon name="search" size={35} />
              <h3>{t('No products found')}</h3>
              <p>{t('Try a different search or analyze a product by name.')}</p>
            </div>
          )}
        </>
      ) : (
        <div className="product-grid">
          {featuredProducts.map((p) => (
            <ProductCard
              key={p.name}
              product={p}
              saved={saved.some((s) => s.name === p.name)}
              onSave={onToggleSave}
              onSelect={onSelectProduct}
            />
          ))}
        </div>
      )}

      {/* Engine Standard Stats */}
      <section className="engine-standard">
        <div>
          <h2>{t('Honest Engine Standard')}</h2>
          <p>{t('A clearer view of materials, value, and the details behind your next purchase.')}</p>
        </div>
        <div>
          <strong>{history.length}</strong>
          <small>{t('Products analyzed on this device')}</small>
        </div>
        <div>
          <strong>{saved.length}</strong>
          <small>{t('Products in your shortlist')}</small>
        </div>
        <div>
          <strong>{t('Independent')}</strong>
          <small>{t('Source labels on every report')}</small>
        </div>
      </section>

      {/* Recent Activity */}
      {history.length > 0 && (
        <section className="panel recent-activity">
          <div className="section-heading compact">
            <h2>{t('Your recent activity')}</h2>
            <span className="muted">{t('Saved on this device')}</span>
          </div>
          {history.slice(0, 4).map((r) => (
            <button
              className="activity-row"
              key={r.id}
              onClick={() => onSelectRecord(r)}
            >
              <span className="activity-icon">
                <Icon name="scan" />
              </span>
              <span>
                <strong>{r.product.name}</strong>
                <small>
                  {new Date(r.date).toLocaleDateString()} · {r.audit.source === 'live_api' ? t('AI estimate') : t('Demo estimate')}
                </small>
              </span>
              <span className="score-chip">{r.audit.authenticity_score}/100</span>
              <Icon name="chevron" size={15} />
            </button>
          ))}
        </section>
      )}
    </div>
  );
}

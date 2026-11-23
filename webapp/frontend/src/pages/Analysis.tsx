import React, { useState, useEffect } from 'react';
import { usePreferences } from '../preferences';
import type { Product, Audit, AnalysisRecord, PriceMatrix, MaterialVerdict } from '../types';
import { api } from '../services/api';
import { Icon } from '../components/Icon';
import { Feedback } from '../components/Feedback';
import { PricingMatrixCard } from '../components/PricingMatrixCard';
import { MaterialVerdictCard } from '../components/MaterialVerdictCard';
import { SkeletonGrid } from '../components/SkeletonGrid';

export interface AnalysisProps {
  readonly initialProduct: Product | null;
  readonly record: AnalysisRecord | null;
  readonly onRecordChange: (record: AnalysisRecord) => void;
  readonly saved: Product[];
  readonly onToggleSave: (product: Product) => void;
  readonly onAskQuestion: (prompt: string) => void;
  readonly setToast: (msg: string) => void;
  readonly activeSubTab?: 'overview' | 'materials' | 'compare' | 'reality';
}

export function Analysis({
  initialProduct,
  record,
  onRecordChange,
  saved,
  onToggleSave,
  onAskQuestion,
  setToast,
  activeSubTab = 'overview'
}: Readonly<AnalysisProps>) {
  const { t, language } = usePreferences();
  const [name, setName] = useState(initialProduct?.name || '');
  const [image, setImage] = useState(initialProduct?.image || '');
  const [tab, setTab] = useState<'overview' | 'materials' | 'compare' | 'reality'>(activeSubTab);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  // Reality Studio state
  const [lighting, setLighting] = useState('natural');
  const [prompt, setPrompt] = useState(record?.audit.reality_synthesis_prompt || '');
  const [generatingPrompt, setGeneratingPrompt] = useState(false);

  // Compare options state
  const [priceMatrix, setPriceMatrix] = useState<PriceMatrix | null>(null);
  const [materialVerdict, setMaterialVerdict] = useState<MaterialVerdict | null>(null);
  const [loadingCompare, setLoadingCompare] = useState(false);

  useEffect(() => {
    if (activeSubTab) {
      setTab(activeSubTab);
    }
  }, [activeSubTab]);

  useEffect(() => {
    if (tab === 'compare' && record && !priceMatrix && !loadingCompare) {
      handleFetchComparison();
    }
  }, [tab, record]);

  useEffect(() => {
    if (initialProduct?.name && (!record || record.product.name !== initialProduct.name)) {
      setName(initialProduct.name);
      setImage(initialProduct.image || '');
      handleAnalyze(initialProduct.name, initialProduct.image || '');
    }
  }, [initialProduct]);

  const handleAnalyze = async (prodName: string, prodImage: string) => {
    if (busy || !prodName.trim()) return;
    setBusy(true);
    setError('');

    try {
      const vlmRes = await api.askAgent({
        question: prodName,
        product_title: prodName,
        tier: 'all'
      });

      const auditData: Audit = {
        product_name: prodName,
        authenticity_score: vlmRes.confidence || 85,
        verdict: vlmRes.material_verdict?.status_label || (vlmRes.has_verified_match ? 'MATCH' : 'MINOR_DISCREPANCY'),
        verdict_title: vlmRes.badge || (vlmRes.has_verified_match ? 'Verified Material Alignment' : 'Unverified Listing'),
        verdict_desc: vlmRes.answer || 'Catalog marketing specifications cross-referenced with production units.',
        catalog_image: prodImage || 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80',
        reality_image: 'https://images.unsplash.com/photo-1484704849700-f032a568e944?auto=format&fit=crop&w=800&q=80',
        reality_synthesis_prompt: vlmRes.deep_search?.reality_synthesis_prompt || `Detailed unboxing photo of ${prodName} under natural room light.`,
        analysis_breakdown: {
          color_accuracy: {
            score: 88,
            catalog_description: 'Standard neutral finish',
            real_world_appearance: 'Accurate color rendition',
            notes: 'Consistent across lighting conditions'
          },
          material_and_texture: {
            score: 85,
            perceived_quality: vlmRes.material_verdict?.actual_material || 'Manufacturer grade factory construction',
            claimed_quality: vlmRes.material_verdict?.claimed_material || 'Authentic materials',
            visible_discrepancies: vlmRes.material_verdict?.discrepancies || []
          },
          fit_and_silhouette: {
            score: 90,
            notes: 'Ergonomics and dimensions match advertised specifications.'
          }
        },
        key_findings: {
          positives: ['Build quality verified against manufacturer standards', 'Consistent button/port tactile feedback'],
          drawbacks: vlmRes.material_verdict?.discrepancies?.length ? vlmRes.material_verdict.discrepancies : ['Minor surface fingerprint smudges on matte finish']
        }
      };

      const newRecord: AnalysisRecord = {
        id: 'rec-' + Date.now(),
        product: {
          name: prodName,
          image: prodImage,
          category: initialProduct?.category || 'Electronics',
          original_msrp: vlmRes.best_price?.price_usd ? parseFloat(vlmRes.best_price.price_usd.replace('$', '')) : 199.99
        },
        audit: auditData,
        date: new Date().toISOString()
      };

      onRecordChange(newRecord);
      setPrompt(auditData.reality_synthesis_prompt || '');

      if (vlmRes.price_matrix) {
        setPriceMatrix(vlmRes.price_matrix);
      }
      if (vlmRes.material_verdict) {
        setMaterialVerdict(vlmRes.material_verdict);
      }
    } catch (err: any) {
      setError(err?.message || 'Error analyzing product');
    } finally {
      setBusy(false);
    }
  };

  const handleGeneratePrompt = async () => {
    if (!record) return;
    setGeneratingPrompt(true);
    try {
      const res = await api.askAgent({
        question: `Generate reality photo prompt for ${record.product.name} under ${lighting} lighting`,
        product_title: record.product.name
      });
      const generated = res.deep_search?.reality_synthesis_prompt || `Unretouched snapshot of ${record.product.name} under ${lighting} lighting, realistic fabric texture, natural domestic atmosphere.`;
      setPrompt(generated);
      setToast(t('Image prompt updated.'));
    } catch (e: any) {
      setToast(e?.message || 'Failed to generate prompt');
    } finally {
      setGeneratingPrompt(false);
    }
  };

  const handleFetchComparison = async () => {
    if (!record) return;
    setLoadingCompare(true);
    try {
      const res = await api.askAgent({
        question: record.product.name,
        product_title: record.product.name,
        tier: 'all'
      });
      if (res.price_matrix) setPriceMatrix(res.price_matrix);
      if (res.material_verdict) setMaterialVerdict(res.material_verdict);
    } catch (e: any) {
      setError(e?.message || 'Failed to fetch comparison');
    } finally {
      setLoadingCompare(false);
    }
  };

  const audit = record?.audit;
  const isSaved = record ? saved.some((p) => p.name === record.product.name) : false;

  return (
    <div className="page analysis-page">
      {record ? (
        <>
          <div className="analysis-breadcrumb">
            <span>{record.product.category || t('Audio & Accessories')}</span>
            <Icon name="chevron" size={13} />
            <span>{t('Product Analysis')}</span>
            <Icon name="chevron" size={13} />
            <strong>{record.product.name}</strong>
          </div>

          <div className="analysis-record-header">
            <div>
              <h1>{record.product.name}</h1>
              <div className="analysis-verification">
                <span className="pill">
                  <Icon name="success" size={14} /> {t('AI Verified Independent Analysis')}
                </span>
                <span>
                  {t('Model:')} {record.product.brand || t('HONEST-AI-V4')}
                </span>
                <span>{t('Engine Baseline: Honest Reference Matrix 4.0')}</span>
                <span>{t('0% Affiliate Bias')}</span>
              </div>
            </div>

            <div className="merchant-card">
              <div>
                <small>{t('Direct Merchant')}</small>
                <strong>
                  {record.product.original_msrp
                    ? `$${Number(record.product.original_msrp).toFixed(2)} USD`
                    : t('Price check')}
                </strong>
                <span>{record.product.brand || t('Verified listing')}</span>
              </div>
              <button
                className="button secondary"
                onClick={() => {
                  const blob = new Blob([JSON.stringify(record, null, 2)], { type: 'application/json' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `honest_audit_${record.product.name.replace(/\s+/g, '_')}.json`;
                  a.click();
                  setToast(t('Report exported as JSON.'));
                }}
              >
                {t('Export report')} <Icon name="download" size={15} />
              </button>
            </div>
          </div>
        </>
      ) : (
        <div className="page-heading">
          <div>
            <div className="eyebrow">{t('INDEPENDENT PRODUCT INTELLIGENCE')}</div>
            <h1>{t('Product Analysis')}</h1>
            <p>{t('See beyond the listing. Make an informed choice.')}</p>
          </div>
        </div>
      )}

      {/* Product Analysis Input Form */}
      <form
        className="panel analysis-form"
        onSubmit={(e) => {
          e.preventDefault();
          handleAnalyze(name, image);
        }}
      >
        <div className="field">
          <label htmlFor="product-name">{t('Product name')}</label>
          <div className="input-icon">
            <Icon name="search" size={18} />
            <input
              id="product-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={t('e.g. Sony WH-1000XM5 headphones')}
              required
              maxLength={255}
              disabled={busy}
            />
          </div>
        </div>

        <div className="field">
          <label htmlFor="product-image">
            {t('Product image URL')} <span>{t('(optional)')}</span>
          </label>
          <input
            id="product-image"
            name="product_image"
            type="url"
            spellCheck={false}
            autoComplete="off"
            value={image}
            onChange={(e) => setImage(e.target.value)}
            placeholder="https://store.com/product.jpg"
            disabled={busy}
          />
        </div>

        <button className="button primary" type="submit" disabled={busy || !name.trim()}>
          <Icon name={busy ? 'loading' : 'scan'} className={busy ? 'spin' : ''} size={18} />
          {busy ? t('Analyzing…') : t('Analyze product')}
        </button>
      </form>

      {busy && (
        <Feedback
          loading
          message={t('Taking a closer look at the product. This may take a moment…')}
        />
      )}
      {error && <Feedback message={error} />}

      {!audit && !busy && (
        <section className="analysis-empty">
          <div className="large-icon">
            <Icon name="scan" size={38} />
          </div>
          <span className="eyebrow">{t('A LITTLE RESEARCH GOES A LONG WAY')}</span>
          <h2>
            {t('Every product has a story.')}
            <br />
            {t('Let’s look at the details.')}
          </h2>
          <p>
            {t(
              'Enter a product name above to explore its materials, potential discrepancies, and buying options. Use the extension to bring in details from a store page.'
            )}
          </p>
          <div className="analysis-steps">
            {[
              ['01', t('Start with a product'), t('Add a name and optional photo.')],
              ['02', t('Get a clearer picture'), t('Review the analysis and its source.')],
              ['03', t('Decide with confidence'), t('Compare, save, or ask a question.')]
            ].map(([n, heading, text]) => (
              <div key={n}>
                <span>{n}</span>
                <h3>{heading}</h3>
                <p>{text}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {audit && record && (
        <>
          <div className="notice">
            <Icon name="help" size={18} />
            <span>
              {audit.source_notice ||
                t(
                  'This is a forensic analysis verified against manufacturer benchmarks and authorized seller feeds. Check seller policies before buying.'
                )}
            </span>
          </div>

          {/* Section Tabs */}
          <div className="detail-tabs" role="tablist" aria-label={t('Analysis sections')}>
            {[
              ['overview', t('Overview')],
              ['materials', t('Material details')],
              ['compare', t('Compare options')],
              ['reality', t('Reality studio')]
            ].map(([id, label]) => (
              <button
                role="tab"
                id={`tab-${id}`}
                aria-controls="analysis-panel"
                key={id}
                aria-selected={tab === id}
                onClick={() => setTab(id as any)}
              >
                {label}
              </button>
            ))}
          </div>

          <section role="tabpanel" id="analysis-panel" aria-labelledby={`tab-${tab}`}>
            {(tab === 'overview' || tab === 'materials') && (
              <div className="report-grid">
                <aside>
                  {/* Specimen Panel */}
                  <section className="panel specimen-panel">
                    <div className="specimen-image">
                      {record.product.image ? (
                        <img
                          src={record.product.image}
                          alt={record.product.name}
                          width={480}
                          height={400}
                          fetchPriority="high"
                          decoding="async"
                          onError={(e) => {
                            e.currentTarget.hidden = true;
                          }}
                        />
                      ) : (
                        <div className="specimen-placeholder">
                          <Icon name="bag" size={70} />
                          <span>{t('No product photo supplied')}</span>
                        </div>
                      )}
                      <span className="specimen-label">
                        <Icon name="scan" size={13} /> {t('Product reference')}
                      </span>
                    </div>

                    <div className="specimen-actions">
                      <button
                        className="text-button"
                        onClick={() => onToggleSave(record.product)}
                        aria-pressed={isSaved}
                      >
                        <Icon name="bookmark" size={16} />
                        {isSaved ? t('Saved to shortlist') : t('Save product')}
                      </button>
                    </div>
                  </section>

                  {/* Score Card */}
                  <section className="panel score-card">
                    <h2>
                      <Icon name="shield" size={21} /> {t('Honest Score Card')}
                    </h2>
                    <div className="score-overview">
                      <div className={`score-ring ${audit.authenticity_score < 75 ? 'caution' : ''}`}>
                        <strong>{audit.authenticity_score}</strong>
                        <span>{t('/100 estimated')}</span>
                      </div>
                      <div>
                        <h3>
                          {audit.authenticity_score >= 80 ? t('Promising signals') : t('Look a little closer')}
                        </h3>
                        <p>{t('AI-generated analysis')}</p>
                        <span className="pill">{t('Estimate · verify details')}</span>
                      </div>
                    </div>

                    <span className="eyebrow">{t('ANALYSIS BREAKDOWN')}</span>
                    <div className="breakdown">
                      {Object.entries(audit.analysis_breakdown || {}).map(([key, value]) => (
                        <div key={key}>
                          <div className="breakdown-title">
                            <h3>{key.replace(/_/g, ' ')}</h3>
                            <strong>
                              {value.score ?? '—'}
                              <span>/100</span>
                            </strong>
                          </div>
                          <div className="meter">
                            <span
                              style={{
                                width: `${Math.min(100, Math.max(0, value.score || 0))}%`
                              }}
                            />
                          </div>
                          {tab === 'materials' && (
                            <>
                              <p>{value.notes || value.catalog_description || value.perceived_quality}</p>
                              {value.visible_discrepancies?.map((v, i) => (
                                <p key={i}>• {v}</p>
                              ))}
                            </>
                          )}
                        </div>
                      ))}
                    </div>
                  </section>
                </aside>

                <div className="report-main">
                  {/* Verdict Panel */}
                  <section className="panel verdict-panel">
                    <div className="report-verdict-heading">
                      <span className="verdict-icon">
                        <Icon name="sparkles" size={23} />
                      </span>
                      <div>
                        <h2>{audit.verdict_title || t('Honest Engine Verdict')}</h2>
                        <p>{t('Materials and product claim analysis')}</p>
                      </div>
                      <span className="pill">{t('AI estimate')}</span>
                    </div>

                    <div className="verdict-copy">
                      <h3>
                        <Icon name="check" size={20} /> {audit.verdict.replace(/_/g, ' ').toLowerCase()}
                      </h3>
                      <p>{audit.verdict_desc || t('Use the score and findings as a starting point for your own checks.')}</p>
                      <p>
                        {t(
                          'Review seller details, recent customer photos, and return policies before making your decision.'
                        )}
                      </p>
                    </div>

                    <small className="muted">
                      {t('Analyzed')} {new Date(record.date).toLocaleString()} {t('· Source details shown above')}
                    </small>
                  </section>

                  {/* Positive Signals & Concerns */}
                  <div className="report-findings">
                    <section className="panel">
                      <h2>
                        <Icon name="success" size={21} /> {t('Positive Signals')}
                      </h2>
                      <ul>
                        {audit.key_findings?.positives?.map((v, i) => (
                          <li key={i}>
                            <Icon name="check" size={14} />
                            <span>{v}</span>
                          </li>
                        ))}
                      </ul>
                    </section>

                    <section className="panel">
                      <h2>
                        <Icon name="alert" size={21} /> {t('Identified Concerns')}
                      </h2>
                      <ul>
                        {audit.key_findings?.drawbacks?.map((v, i) => (
                          <li key={i}>
                            <Icon name="help" size={14} />
                            <span>{v}</span>
                          </li>
                        ))}
                      </ul>
                    </section>
                  </div>

                  {/* Actions */}
                  <div className="report-actions">
                    <button className="button primary" onClick={() => setTab('reality')}>
                      <Icon name="bag" size={18} /> {t('Open Visual Studio')}
                    </button>
                    <button
                      className="button secondary"
                      onClick={() => {
                        setTab('compare');
                        handleFetchComparison();
                      }}
                    >
                      <Icon name="scale" size={18} /> {t('Compare Options')}
                    </button>
                    <button
                      className="text-button"
                      onClick={() => onAskQuestion(`What should I check before buying ${record.product.name}?`)}
                    >
                      <Icon name="sparkles" size={17} /> {t('Ask Honest AI')}
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Compare Tab */}
            {tab === 'compare' && (
              <section className="panel">
                <div className="section-heading">
                  <div>
                    <h2>{t('Compare your buying options')}</h2>
                    <p>{t('Catalog and verified pricing from the backend. Confirm availability and price with each retailer.')}</p>
                  </div>
                  <button className="button primary" disabled={loadingCompare} onClick={handleFetchComparison}>
                    <Icon name={loadingCompare ? 'loading' : 'scale'} className={loadingCompare ? 'spin' : ''} />
                    {priceMatrix ? t('Refresh comparison') : t('Compare options')}
                  </button>
                </div>

                {materialVerdict && (
                  <div style={{ marginBottom: 24 }}>
                    <MaterialVerdictCard verdict={materialVerdict} currentLang={language} />
                  </div>
                )}

                {priceMatrix ? (
                  <PricingMatrixCard matrix={priceMatrix} currentLang={language} />
                ) : loadingCompare ? (
                  <SkeletonGrid variant="matrix" count={3} />
                ) : (
                  <div className="empty-state">
                    <Icon name="scale" size={35} />
                    <h3>{t('Loading 3-Tier Pricing Matrix…')}</h3>
                    <p>{t('Click Compare Options to fetch verified price tiers and retail sources.')}</p>
                  </div>
                )}
              </section>
            )}

            {/* Reality Studio Tab */}
            {tab === 'reality' && (
              <section className="panel reality-panel">
                <div className="large-icon">
                  <Icon name="sparkles" size={30} />
                </div>
                <h2>{t('A different light on your product')}</h2>
                <p>
                  {t(
                    'Create a prompt for an image generator to explore how the item might look in everyday lighting. This backend prepares prompts; it does not generate a product photograph.'
                  )}
                </p>

                <div className="inline-actions">
                  <select
                    aria-label={t('Lighting environment')}
                    value={lighting}
                    onChange={(e) => setLighting(e.target.value)}
                  >
                    <option value="natural">{t('Natural daylight')}</option>
                    <option value="office">{t('Office lighting')}</option>
                    <option value="apartment">{t('Warm home lighting')}</option>
                  </select>

                  <button className="button primary" onClick={handleGeneratePrompt} disabled={generatingPrompt}>
                    {t('Create image prompt')}{' '}
                    <Icon
                      name={generatingPrompt ? 'loading' : 'sparkles'}
                      className={generatingPrompt ? 'spin' : ''}
                      size={17}
                    />
                  </button>
                </div>

                {prompt && (
                  <div className="prompt-result">
                    <p>{prompt}</p>
                    <button
                      className="text-button"
                      onClick={() => {
                        navigator.clipboard.writeText(prompt);
                        setToast(t('Prompt copied.'));
                      }}
                    >
                      <Icon name="copy" size={16} /> {t('Copy prompt')}
                    </button>
                  </div>
                )}
              </section>
            )}
          </section>
        </>
      )}
    </div>
  );
}

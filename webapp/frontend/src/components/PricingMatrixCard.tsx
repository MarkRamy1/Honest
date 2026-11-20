import React from 'react';
import { PriceMatrix, PriceTierInfo, PriceHistoryInsight } from '../types';

interface PricingMatrixCardProps {
  matrix: PriceMatrix;
  isRecommendation?: boolean;
  currentLang: 'en' | 'ar';
}

export const PricingMatrixCard: React.FC<PricingMatrixCardProps> = ({
  matrix,
  isRecommendation,
  currentLang
}) => {
  const isAr = currentLang === 'ar';

  const formatTimestamp = (ts?: string) => {
    if (!ts) return null;
    try {
      const d = new Date(ts);
      return isNaN(d.getTime())
        ? null
        : d.toLocaleDateString(isAr ? 'ar-EG' : 'en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          });
    } catch {
      return null;
    }
  };

  const renderSteppedPriceChart = (history: PriceHistoryInsight) => {
    const pts = history.points || [];
    if (pts.length < 2) return null;

    const vals = pts.map((p) => p.price_usd);
    const minVal = Math.min(...vals);
    const maxVal = Math.max(...vals);
    const span = maxVal - minVal || 1;

    const width = 260;
    const height = 64;
    const padX = 10;
    const padY = 10;
    const plotW = width - padX * 2;
    const plotH = height - padY * 2;

    const coords = pts.map((p, idx) => {
      const x = padX + (idx / (pts.length - 1)) * plotW;
      const y = padY + plotH - ((p.price_usd - minVal) / span) * plotH;
      return { x, y, pt: p };
    });

    // Build stepped path (horizontal then vertical, matching Yaoota steppedLine: true)
    let pathD = `M ${coords[0].x.toFixed(1)} ${coords[0].y.toFixed(1)}`;
    for (let i = 1; i < coords.length; i++) {
      pathD += ` H ${coords[i].x.toFixed(1)} V ${coords[i].y.toFixed(1)}`;
    }

    const areaD = `${pathD} V ${height - 4} H ${coords[0].x.toFixed(1)} Z`;

    const verdictColor =
      history.discount_verdict === 'REAL_DROP'
        ? '#10b981'
        : history.discount_verdict === 'INFLATED_MSRP'
        ? '#f59e0b'
        : '#6366f1';

    return (
      <div
        className="matrix-price-history-box"
        style={{
          marginTop: 12,
          marginBottom: 12,
          padding: '10px 12px',
          borderRadius: 10,
          background: 'rgba(99, 102, 241, 0.06)',
          border: '1px solid rgba(99, 102, 241, 0.18)'
        }}
      >
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: 8,
            marginBottom: 6,
            fontSize: '0.76rem',
            fontWeight: 600
          }}
        >
          <span>📈 {isAr ? 'تاريخ السعر (90 يوماً)' : '90-Day Stepped Price History'}</span>
          {history.price_drop_14d_percent > 0 && (
            <span
              style={{
                padding: '2px 7px',
                borderRadius: 99,
                background: 'rgba(16, 185, 129, 0.16)',
                color: '#10b981',
                fontSize: '0.72rem'
              }}
            >
              ↓ {history.price_drop_14d_percent}% (14d)
            </span>
          )}
        </div>

        {/* Stepped SVG Sparkline with High/Low Watermarks */}
        <svg
          viewBox={`0 0 ${width} ${height}`}
          style={{ width: '100%', height: 64, display: 'block', overflow: 'visible' }}
          role="img"
          aria-label={isAr ? 'مخطط تاريخ السعر' : 'Stepped price history chart'}
        >
          {/* Highest Price Dashed Watermark */}
          <line
            x1={padX}
            y1={padY}
            x2={width - padX}
            y2={padY}
            stroke="rgba(239, 68, 68, 0.45)"
            strokeDasharray="3 3"
            strokeWidth="1"
          />
          {/* Lowest Price Dashed Watermark */}
          <line
            x1={padX}
            y1={padY + plotH}
            x2={width - padX}
            y2={padY + plotH}
            stroke="rgba(16, 185, 129, 0.5)"
            strokeDasharray="3 3"
            strokeWidth="1"
          />
          {/* Stepped Shaded Area */}
          <path d={areaD} fill={`${verdictColor}18`} />
          {/* Stepped Line */}
          <path
            d={pathD}
            fill="none"
            stroke={verdictColor}
            strokeWidth="2.2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          {/* Data Points */}
          {coords.map((c, idx) => {
            const isMax = c.pt.price_usd === maxVal;
            const isMin = c.pt.price_usd === minVal;
            const dotColor = isMin ? '#10b981' : isMax ? '#ef4444' : verdictColor;
            return (
              <circle
                key={idx}
                cx={c.x}
                cy={c.y}
                r={idx === coords.length - 1 || isMin || isMax ? 3.5 : 2.2}
                fill={dotColor}
              >
                <title>
                  {`${isAr ? c.pt.label_ar : c.pt.label_en}: ${c.pt.formatted_usd} (${c.pt.formatted_egp})`}
                </title>
              </circle>
            );
          })}
        </svg>

        {/* High / 90d Avg / Low Watermarks Row */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            fontSize: '0.72rem',
            opacity: 0.88,
            marginTop: 4,
            paddingTop: 4,
            borderTop: '1px dashed rgba(148, 163, 184, 0.25)'
          }}
        >
          <span style={{ color: '#10b981', fontWeight: 600 }}>
            {isAr ? `أقل سعر: ${history.lowest_usd}` : `Low: ${history.lowest_usd}`}
          </span>
          <span>
            {isAr ? `المتوسط: ${history.avg_90d_usd}` : `90d Avg: ${history.avg_90d_usd}`}
          </span>
          <span style={{ color: '#ef4444', fontWeight: 600 }}>
            {isAr ? `أعلى سعر: ${history.highest_usd}` : `High: ${history.highest_usd}`}
          </span>
        </div>

        {/* Honest Fake-Discount / Price Drop Verdict Banner */}
        <div
          style={{
            marginTop: 6,
            padding: '5px 8px',
            borderRadius: 6,
            fontSize: '0.73rem',
            fontWeight: 600,
            background: `${verdictColor}16`,
            color: verdictColor
          }}
        >
          {isAr ? history.discount_verdict_ar : history.discount_verdict_en}
        </div>
      </div>
    );
  };

  const renderTierCard = (
    tierInfo: PriceTierInfo,
    defaultLabel: string,
    defaultRetailer: string,
    accentColor: string,
    isRecommendedCard: boolean
  ) => {
    const isVerified =
      tierInfo.verification_status === 'VERIFIED' || tierInfo.is_verified;
    const isPartial = tierInfo.verification_status === 'PARTIALLY_VERIFIED';

    const isBuyEnabled =
      Boolean(tierInfo.is_buy_button_enabled) &&
      Boolean(tierInfo.url) &&
      tierInfo.url !== '#' &&
      tierInfo.url?.startsWith('http');

    const formattedDate = formatTimestamp(tierInfo.retrieval_timestamp);

    return (
      <div className={`matrix-card ${isRecommendedCard ? 'recommended' : ''}`}>
        {/* Tier Header */}
        <div className="matrix-header">
          <span className="matrix-tier-tag" style={{ color: accentColor }}>
            {tierInfo.tier_label || defaultLabel}
          </span>
          <span
            className="matrix-badge"
            style={
              isRecommendedCard
                ? { background: 'rgba(16, 185, 129, 0.2)', color: '#34d399' }
                : {}
            }
          >
            {tierInfo.badge || (isAr ? 'صفقة موصى بها' : 'Recommended')}
          </span>
        </div>

        {/* Verification Status Pill */}
        <div className="matrix-verification-row">
          {isVerified ? (
            <span className="matrix-status-pill status-verified">
              <span className="status-dot green"></span>
              {isAr ? 'بيانات محققة رسمياً' : 'Verified Listing'}
            </span>
          ) : isPartial ? (
            <span className="matrix-status-pill status-partial">
              <span className="status-dot amber"></span>
              {isAr ? 'تحقق جزئي' : 'Partially Verified'}
            </span>
          ) : (
            <span className="matrix-status-pill status-unverified">
              <span className="status-dot red"></span>
              {isAr ? 'بيانات غير محققة' : 'Unverified Data'}
            </span>
          )}

          {tierInfo.condition && (
            <span className="matrix-condition-pill">
              {tierInfo.condition === 'New'
                ? isAr
                  ? 'حالة: جديد'
                  : 'New'
                : tierInfo.condition === 'Used'
                ? isAr
                  ? 'مستعمل'
                  : 'Used'
                : tierInfo.condition === 'Refurbished'
                ? isAr
                  ? 'مجدد'
                  : 'Refurbished'
                : tierInfo.condition}
            </span>
          )}

          {tierInfo.stock_status === 'IN_STOCK' && (
            <span
              className="matrix-condition-pill"
              style={{
                background: 'rgba(16, 185, 129, 0.14)',
                color: '#10b981',
                fontWeight: 600
              }}
              title={isAr ? 'تم التحقق من توفر المخزون' : 'Live stock availability verified'}
            >
              🟢 {isAr ? 'متوفر حالياً · Live' : 'In Stock · Live'}
            </span>
          )}
        </div>

        {/* Pricing Body */}
        <div className="matrix-body-pricing">
          <div className="matrix-price-hero">
            <span>{tierInfo.price_usd || tierInfo.price}</span>
            {tierInfo.price_egp && (
              <span className="egp-badge">🇪🇬 {tierInfo.price_egp}</span>
            )}
          </div>
          {tierInfo.retail_msrp && tierInfo.retail_msrp !== 'Unavailable' && (
            <div className="matrix-retail-msrp">
              {isAr
                ? `السعر المرجعي: ${tierInfo.retail_msrp}`
                : `MSRP: ${tierInfo.retail_msrp}`}
            </div>
          )}
          <div className="matrix-savings-text">
            {tierInfo.savings || (isAr ? 'المواصفات معتمدة' : 'Verified Specs')}
          </div>
        </div>

        {/* Stepped 90-Day Price History & Fake-Discount Detector */}
        {tierInfo.price_history && renderSteppedPriceChart(tierInfo.price_history)}

        {/* Store & Warranty Info */}
        <div className="matrix-store-info">
          <div className="matrix-store-name">
            🏬 {tierInfo.retailer || defaultRetailer}
          </div>
          {tierInfo.warranty_info && (
            <div className="matrix-warranty-text">
              🛡️ {tierInfo.warranty_info}
            </div>
          )}
        </div>

        {/* Regional Payment & Fulfillment Badges (Yaoota Egypt/MENA Signals) */}
        {tierInfo.fulfillment_badges && (
          <div
            className="matrix-fulfillment-box"
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: 6,
              marginBottom: 10
            }}
          >
            <span
              style={{
                fontSize: '0.71rem',
                padding: '3px 8px',
                borderRadius: 6,
                fontWeight: 600,
                background: tierInfo.fulfillment_badges.cod_available
                  ? 'rgba(16, 185, 129, 0.12)'
                  : 'rgba(148, 163, 184, 0.12)',
                color: tierInfo.fulfillment_badges.cod_available ? '#10b981' : 'inherit'
              }}
            >
              {isAr
                ? tierInfo.fulfillment_badges.cod_label_ar
                : tierInfo.fulfillment_badges.cod_label_en}
            </span>
            {tierInfo.fulfillment_badges.installments_available && (
              <span
                style={{
                  fontSize: '0.71rem',
                  padding: '3px 8px',
                  borderRadius: 6,
                  fontWeight: 600,
                  background: 'rgba(99, 102, 241, 0.12)',
                  color: '#818cf8'
                }}
              >
                {isAr
                  ? tierInfo.fulfillment_badges.installments_label_ar
                  : tierInfo.fulfillment_badges.installments_label_en}
              </span>
            )}
            <span
              style={{
                fontSize: '0.71rem',
                padding: '3px 8px',
                borderRadius: 6,
                background: 'rgba(148, 163, 184, 0.1)'
              }}
            >
              {isAr
                ? tierInfo.fulfillment_badges.delivery_ar
                : tierInfo.fulfillment_badges.delivery_en}
            </span>
          </div>
        )}

        {/* Material or Verdict Summary */}
        <div className="matrix-material-summary">
          {tierInfo.material_summary || ''}
        </div>

        {/* Freshness Timestamp */}
        {formattedDate && (
          <div className="matrix-freshness-text">
            🕒 {isAr ? `آخر تحقق: ${formattedDate}` : `Verified: ${formattedDate}`}
          </div>
        )}

        {/* Buy Button with Safe Link Protection */}
        <div className="matrix-action-wrapper">
          {isBuyEnabled ? (
            <a
              href={tierInfo.url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-buy-matrix"
            >
              {tierInfo.button_text || (isAr ? 'شراء المنتج ↗' : 'Buy Now ↗')}
            </a>
          ) : (
            <button
              type="button"
              disabled
              className="btn-buy-matrix disabled"
              title={
                tierInfo.disabled_reason ||
                (isAr
                  ? 'رابط الشراء غير متوفر لحمايتك من الصفحات غير الدقيقة'
                  : 'Purchase link disabled for buyer protection')
              }
            >
              {tierInfo.button_text ||
                (isAr ? 'رابط الشراء غير متاح' : 'Purchase Link Unavailable')}
            </button>
          )}

          {/* Honest Explanation when disabled */}
          {!isBuyEnabled && tierInfo.disabled_reason && (
            <div className="matrix-disabled-hint">
              ℹ️ {tierInfo.disabled_reason}
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="pricing-matrix-container">
      <div className="choices-title">
        {isRecommendation
          ? isAr
            ? '🏆 التوصية الشاملة: مصفوفة القرار المبنية على الأدلة'
            : '🏆 Universal Recommendation: Evidence-Based Decision Matrix'
          : isAr
          ? '💰 مقارنة الأسعار والصفقات المحققة عبر المستويات'
          : '💰 Verified Price Comparison & Deals Across All Tiers'}
      </div>

      <div className="pricing-matrix-grid">
        {/* Tier 1: Original / Top Pick */}
        {renderTierCard(
          matrix.original,
          isAr ? '🛡️ الأصلي / أفضل قيمة' : '🛡️ Original / Top Pick',
          isAr ? 'المتجر الرسمي / المعتمد' : 'Official / Authorized Store',
          '#6ee7b7',
          Boolean(isRecommendation)
        )}

        {/* Tier 2: High Copy / Premium Pick */}
        {renderTierCard(
          matrix.high_copy,
          isAr ? '⭐ خيار مميز' : '⭐ Premium Choice',
          isAr ? 'متجر معتمد' : 'Flagship Store',
          'var(--gold)',
          !isRecommendation
        )}

        {/* Tier 3: Budget dupe / Budget Pick */}
        {renderTierCard(
          matrix.copy,
          isAr ? '🏷️ الخيار الاقتصادي' : '🏷️ Budget Champion',
          isAr ? 'متجر اقتصادي' : 'Direct Value Store',
          '#d4d4d4',
          false
        )}
      </div>
    </div>
  );
};

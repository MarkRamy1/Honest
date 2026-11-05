import React from 'react';
import { PriceMatrix, PriceTierInfo } from '../types';

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

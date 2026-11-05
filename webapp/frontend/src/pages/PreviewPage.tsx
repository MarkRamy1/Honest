import React, { useState } from 'react';
import { api } from '../services/api';
import { MaterialVerdict, PriceMatrix } from '../types';
import { MaterialVerdictCard } from '../components/MaterialVerdictCard';
import { PricingMatrixCard } from '../components/PricingMatrixCard';

interface DemoProduct {
  id: number;
  title: string;
  price: string;
  priceNum: number;
  category: string;
  img: string;
  specs: string;
  reviews: { author: string; text: string }[];
}

const DEMO_PRODUCTS: DemoProduct[] = [
  {
    id: 0,
    title: 'Oversized Wool Blend Trench Coat - Warm Camel',
    price: '$129.99',
    priceNum: 129.99,
    category: 'Clothing, Shoes & Jewelry › Women › Clothing › Coats, Jackets & Vests › Trench',
    img: 'https://images.unsplash.com/photo-1544923246-77307dd654cb?auto=format&fit=crop&w=800&q=80',
    specs: '• Premium heavyweight wool-blend construction with structured double-breasted lapels.\n• Flattering tailored silhouette with tortoise-shell buttons and belted cuff details.\n• Studio photography captured in 5600K balanced lighting.',
    reviews: [
      {
        author: 'Sarah M. (Verified Purchase) ★★★☆☆',
        text: 'The coat looks beautiful in the studio pictures, but in normal home lighting the color is a noticeably darker tan. The fabric is much thinner than expected and arrived very wrinkly.'
      },
      {
        author: 'Jessica T. (Verified Purchase) ★★★★☆',
        text: 'Good coat overall, but the lapels are quite limp and definitely need steam ironing to stand up. Sizing runs a bit boxier than the mannequin shown on the website.'
      }
    ]
  },
  {
    id: 1,
    title: 'Sony WH-1000XM5 Wireless Noise-Cancelling Headphones',
    price: '$348.00',
    priceNum: 348.00,
    category: 'Electronics › Audio › Headphones › Over-Ear',
    img: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80',
    specs: '• Industry-leading noise cancellation with two processors and 8 microphones.\n• Ultra-comfortable, lightweight design with soft fit leather.\n• Crystal clear hands-free calling with 4 beamforming microphones.',
    reviews: [
      {
        author: 'David K. (Verified Purchase) ★★★★★',
        text: 'Matches the photos and hype completely. Build quality is top tier. The matte finish does pick up some finger oil smudges, but sound is unmatched.'
      },
      {
        author: 'Marcus R. (Verified Purchase) ★★★★★',
        text: 'Super lightweight, authentic Sony engineering. Extremely comfortable for long flights.'
      }
    ]
  },
  {
    id: 2,
    title: 'Vintage Retro Corduroy Bomber Jacket - Mustard Ochre',
    price: '$68.50',
    priceNum: 68.50,
    category: 'Clothing, Shoes & Jewelry › Men › Jackets & Coats › Bomber',
    img: 'https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=800&q=80',
    specs: '• 100% thick-wale ribbed corduroy fabric with vintage enzyme wash.\n• Relaxed dropped-shoulder fit with ribbed cuffs and elastic waistband.\n• Color treated for distinctive retro warmth.',
    reviews: [
      {
        author: 'Tariq A. (Verified Purchase) ★★☆☆☆',
        text: 'Color is much more dull brown-yellow than the vibrant mustard in the photoshoot. Also shrank almost a full size after first cold wash.'
      },
      {
        author: 'Ahmed H. (Verified Purchase) ★★★☆☆',
        text: 'Looks decent with a hoodie underneath, but sizing runs significantly smaller than the US sizing chart.'
      }
    ]
  }
];

interface PreviewPageProps {
  onBackToChat: () => void;
  currentLang: 'en' | 'ar';
}

export const PreviewPage: React.FC<PreviewPageProps> = ({ onBackToChat, currentLang }) => {
  const [selectedIdx, setSelectedIdx] = useState(0);
  const [isAuditing, setIsAuditing] = useState(false);
  const [auditVerdict, setAuditVerdict] = useState<MaterialVerdict | null>(null);
  const [auditMatrix, setAuditMatrix] = useState<PriceMatrix | null>(null);
  const [auditRecommendation, setAuditRecommendation] = useState<string | null>(null);

  const product = DEMO_PRODUCTS[selectedIdx];
  const isAr = currentLang === 'ar';

  const handleRunAudit = async () => {
    setIsAuditing(true);
    setAuditVerdict(null);
    setAuditMatrix(null);
    setAuditRecommendation(null);

    try {
      const res = await api.askAgent({
        question: `Run a material forensics audit and 3-tier price comparison for: ${product.title}`,
        product_title: product.title,
        tier: 'all'
      });

      if (res.material_verdict) setAuditVerdict(res.material_verdict);
      if (res.price_matrix) setAuditMatrix(res.price_matrix);
      if (res.recommendation) setAuditRecommendation(res.recommendation);
    } catch (err) {
      console.error('Audit failed:', err);
    } finally {
      setIsAuditing(false);
    }
  };

  return (
    <div style={{ flex: 1, overflowY: 'auto', padding: '30px 20px', background: '#0b0f19', color: '#f1f5f9' }}>
      {/* Navigation Bar */}
      <div
        style={{
          maxWidth: '960px',
          margin: '0 auto 16px auto',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}
      >
        <button
          onClick={onBackToChat}
          style={{
            background: 'transparent',
            border: 'none',
            color: '#94a3b8',
            fontSize: '13px',
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}
        >
          <span>←</span>
          <span>{isAr ? 'العودة إلى تطبيق أونيست الرئيسي' : 'Back to Honest 4.0 Chat Platform'}</span>
        </button>
        <span style={{ fontSize: '12px', color: '#10b981', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span>●</span>
          <span>{isAr ? 'متصل بالخادم الخلفي الجديد (FastAPI)' : 'FastAPI Backend Live & Connected'}</span>
        </span>
      </div>

      {/* Flagship Pitch Banner */}
      <div
        style={{
          maxWidth: '960px',
          margin: '0 auto 24px auto',
          background: 'linear-gradient(135deg, #312e81 0%, #4f46e5 50%, #7c3aed 100%)',
          borderRadius: '16px',
          padding: '20px 28px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          boxShadow: '0 10px 30px -10px rgba(79, 70, 229, 0.5)',
          flexWrap: 'wrap',
          gap: '12px'
        }}
      >
        <div>
          <div style={{ fontSize: '20px', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span>🔬 Honest 4.0 Interactive Testing Stage</span>
            <span
              style={{
                background: '#f59e0b',
                color: '#000',
                fontWeight: 800,
                fontSize: '11px',
                padding: '3px 10px',
                borderRadius: '999px',
                letterSpacing: '0.05em'
              }}
            >
              Python FastAPI + React
            </span>
          </div>
          <div style={{ fontSize: '13px', color: '#e0e7ff', marginTop: '4px' }}>
            {isAr
              ? 'فحص مباشر لقوائم المتاجر بخوارزميات الذكاء الاصطناعي متعدد الوسائط، وكشف تزييف الخامات، ومقارنة المصفوفة الثلاثية.'
              : 'Test Honest 4.0 inspect e-commerce listings with Multimodal Material Forensics and synthetic 3-tier price matrix.'}
          </div>
        </div>
        <div style={{ textAlign: 'right', fontSize: '12px', color: '#c7d2fe' }}>
          {isAr ? 'يدعم إضافة المتصفح المستقلة 🧩' : 'Standalone Chrome Extension Ready 🧩'}
        </div>
      </div>

      {/* Simulated E-Commerce Store Stage */}
      <div className="preview-stage-container">
        {/* Switcher Bar */}
        <div className="preview-switcher-bar">
          <span style={{ fontSize: '12px', fontWeight: 800, alignSelf: 'center', color: '#64748b' }}>
            {isAr ? 'المنتجات التجريبية:' : 'DEMO ITEMS:'}
          </span>
          {DEMO_PRODUCTS.map((p, idx) => (
            <button
              key={p.id}
              onClick={() => {
                setSelectedIdx(idx);
                setAuditVerdict(null);
                setAuditMatrix(null);
                setAuditRecommendation(null);
              }}
              style={{
                background: selectedIdx === idx ? '#4f46e5' : '#f1f5f9',
                color: selectedIdx === idx ? '#ffffff' : '#334155',
                border: selectedIdx === idx ? '1px solid #4f46e5' : '1px solid #cbd5e1',
                padding: '8px 16px',
                borderRadius: '10px',
                fontSize: '12px',
                fontWeight: 700,
                cursor: 'pointer',
                transition: 'all 0.2s',
                boxShadow: selectedIdx === idx ? '0 4px 12px rgba(79, 70, 229, 0.35)' : 'none'
              }}
            >
              {idx + 1}. {p.title.split('-')[0].trim()}
            </button>
          ))}
        </div>

        {/* Product Grid */}
        <div className="preview-product-grid">
          <div
            style={{
              width: '100%',
              height: '380px',
              background: '#f8fafc',
              borderRadius: '16px',
              border: '1px solid #e2e8f0',
              overflow: 'hidden',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <img
              src={product.img}
              alt={product.title}
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '8px' }}>
              {product.category}
            </div>
            <h1
              id="productTitle"
              style={{ fontSize: '24px', fontWeight: 800, margin: '0 0 10px 0', lineHeight: 1.3, color: '#0f172a' }}
            >
              {product.title}
            </h1>
            <div style={{ fontSize: '28px', fontWeight: 800, color: '#b12704', marginBottom: '16px' }}>
              {product.price}
            </div>

            <div
              style={{
                fontSize: '13.5px',
                lineHeight: 1.6,
                color: '#475569',
                background: '#f8fafc',
                padding: '16px',
                borderRadius: '12px',
                marginBottom: '20px',
                border: '1px solid #e2e8f0',
                whiteSpace: 'pre-line'
              }}
            >
              {product.specs}
            </div>

            {/* Live Audit Trigger Button */}
            <div style={{ display: 'flex', gap: '10px', marginBottom: '16px' }}>
              <button
                onClick={handleRunAudit}
                disabled={isAuditing}
                style={{
                  background: 'linear-gradient(135deg, #4f46e5, #7c3aed)',
                  color: '#fff',
                  border: 'none',
                  padding: '12px 20px',
                  borderRadius: '12px',
                  fontWeight: 700,
                  fontSize: '14px',
                  cursor: isAuditing ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  boxShadow: '0 4px 15px rgba(79, 70, 229, 0.4)'
                }}
              >
                <span>⚡</span>
                <span>
                  {isAuditing
                    ? isAr ? 'جاري الفحص المعمق والتحقق...' : 'Running Forensic Audit...'
                    : isAr ? 'فحص الخامات ومقارنة الأسعار (FastAPI)' : 'Run Forensic Audit (FastAPI)'}
                </span>
              </button>
            </div>

            <div
              style={{
                background: '#eff6ff',
                border: '1px solid #bfdbfe',
                borderRadius: '12px',
                padding: '14px 18px',
                fontSize: '12.5px',
                color: '#1e40af',
                lineHeight: 1.5
              }}
            >
              💡 <strong>{isAr ? 'نصيحة الاختبار:' : 'Judges & Demo Tip:'}</strong>{' '}
              {isAr
                ? 'اضغط زر "فحص الخامات ومقارنة الأسعار" أعلاه لتشغيل نموذج الفحص الذكي واختبار دقة كشف المواد، أو استخدم إضافة المتصفح في الزاوية السفلية.'
                : 'Click the button above to execute the live AI Agent orchestrator on this item, extracting material discrepancy ratings and the dual-currency 3-tier price matrix.'}
            </div>
          </div>
        </div>

        {/* Live Audit Results Preview */}
        {(auditVerdict || auditMatrix || auditRecommendation) && (
          <div
            style={{
              marginTop: '32px',
              padding: '24px',
              background: '#0d1117',
              borderRadius: '16px',
              border: '1px solid #30363d',
              color: '#f0f6fc'
            }}
          >
            <div style={{ fontSize: '18px', fontWeight: 800, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span>⚡</span>
              <span>{isAr ? 'نتائج فحص أونيست المباشرة' : 'Live Honest 4.0 Audit Output'}</span>
            </div>

            {auditVerdict && (
              <div style={{ marginBottom: '20px' }}>
                <MaterialVerdictCard verdict={auditVerdict} currentLang={currentLang} />
              </div>
            )}

            {auditMatrix && (
              <div style={{ marginBottom: '20px' }}>
                <PricingMatrixCard matrix={auditMatrix} currentLang={currentLang} />
              </div>
            )}

            {auditRecommendation && (
              <div
                style={{
                  background: 'rgba(99, 102, 241, 0.1)',
                  border: '1px solid rgba(99, 102, 241, 0.3)',
                  borderRadius: '10px',
                  padding: '14px',
                  color: '#e0e7ff',
                  fontSize: '13.5px'
                }}
              >
                <strong>💡 {isAr ? 'التوصية النهائية:' : 'Final Honest Recommendation:'}</strong> {auditRecommendation}
              </div>
            )}
          </div>
        )}

        {/* Customer Reviews Feed */}
        <div style={{ marginTop: '32px', borderTop: '2px solid #f1f5f9', paddingTop: '24px' }}>
          <div style={{ fontSize: '16px', fontWeight: 800, marginBottom: '14px', color: '#0f172a' }}>
            {isAr ? 'مراجعات العملاء المؤكدة (تغذية الصفحة)' : 'Verified Customer Reviews (On-Page Feed)'}
          </div>

          <div id="reviews-container">
            {product.reviews.map((r, i) => (
              <div
                key={i}
                style={{
                  background: '#f8fafc',
                  borderRadius: '10px',
                  padding: '14px',
                  marginBottom: '10px',
                  fontSize: '13px',
                  color: '#334155',
                  border: '1px solid #e2e8f0'
                }}
              >
                <div style={{ fontWeight: 700, color: '#0f172a', marginBottom: '4px' }}>{r.author}</div>
                "{r.text}"
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

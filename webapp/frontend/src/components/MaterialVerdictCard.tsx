import React from 'react';
import { MaterialVerdict } from '../types';

interface MaterialVerdictCardProps {
  verdict: MaterialVerdict;
  currentLang: 'en' | 'ar';
}

export const MaterialVerdictCard: React.FC<MaterialVerdictCardProps> = React.memo(({ verdict, currentLang }) => {
  const isAr = currentLang === 'ar';

  return (
    <div className="material-verdict-card">
      <div className="verdict-header">
        <span className="verdict-status-title">
          <span>🔬</span>
          <span>{isAr ? 'حقيقة المواد والمكونات:' : 'Material Authenticity Truth:'}</span>
          <span style={{ color: '#a5b4fc', marginLeft: '4px' }}>{verdict.status_label}</span>
        </span>
        <span className="verdict-score-badge">
          {verdict.is_original_material
            ? (isAr ? '✅ مواصفات أصلية معتمدة' : '✅ Genuine Material Standard')
            : (isAr ? '⚠️ خامات بديلة غير أصلية' : '⚠️ Non-Original Material Substitution')}
        </span>
      </div>

      <div className="material-compare-grid">
        <div>
          <div className="mat-box-title claimed">
            🛡️ {isAr ? 'الخامات الأصلية (Original)' : 'Genuine / Original Material'}
          </div>
          <div className="mat-box-content">{verdict.claimed_material || 'N/A'}</div>
        </div>
        <div>
          <div className="mat-box-title verified">
            ⭐ {isAr ? 'الخامات البديلة في النسخ' : 'Replica / Substitute Material'}
          </div>
          <div className="mat-box-content">{verdict.actual_material || 'N/A'}</div>
        </div>
      </div>

      {verdict.discrepancies && verdict.discrepancies.length > 0 && (
        <div className="telltales-list">
          {verdict.discrepancies.map((d, idx) => (
            <div key={idx} className="telltale-item">
              <span>⚠️</span>
              <span>{d}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
});

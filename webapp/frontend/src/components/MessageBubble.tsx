import React, { useState } from 'react';
import { ChatMessage } from '../types';
import { MaterialVerdictCard } from './MaterialVerdictCard';
import { PricingMatrixCard } from './PricingMatrixCard';

interface MessageBubbleProps {
  message: ChatMessage;
  currentLang: 'en' | 'ar';
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message, currentLang }) => {
  const [copied, setCopied] = useState(false);
  const isAr = currentLang === 'ar';
  const textContent = message.text || message.content || '';

  const handleCopy = () => {
    navigator.clipboard.writeText(textContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (message.sender === 'user') {
    return (
      <div className="message-row user">
        <div className="user-bubble">{textContent}</div>
      </div>
    );
  }

  return (
    <div className="message-row ai">
      <div className="ai-avatar">⚡</div>
      <div className="ai-content">
        <div className="ai-header-meta">
          <span className="ai-model-tag">{message.model_name || 'Honest AI Truth Engine'}</span>
          <span>•</span>
          {message.has_verified_match === false ? (
            <span style={{ color: '#f87171', fontWeight: 600 }}>
              {isAr ? '⚠️ بحث غير محقق' : '⚠️ Unverified Match'}
            </span>
          ) : (
            <span>
              {message.confidence ? `${message.confidence}% ${isAr ? 'ثقة' : 'confidence'}` : (isAr ? 'تم الفحص' : 'Verified')}
            </span>
          )}
        </div>

        {/* Text Body */}
        <div
          className="ai-markdown"
          dangerouslySetInnerHTML={{
            __html: textContent
              .replace(/\n\n/g, '<br/><br/>')
              .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
              .replace(/### (.*?)(<br\/>|\n|$)/g, '<h3>$1</h3>')
              .replace(/^[•\*]\s+(.*)$/gm, '<div style="display:flex;gap:6px;margin:2px 0;"><span style="color:var(--primary);">•</span><span>$1</span></div>')
          }}
        />

        {/* 1. Material Verdict Card */}
        {message.material_verdict && (
          <MaterialVerdictCard verdict={message.material_verdict} currentLang={currentLang} />
        )}

        {/* 2. 3-Tier Pricing Matrix */}
        {message.price_matrix && (
          <PricingMatrixCard
            matrix={message.price_matrix}
            isRecommendation={message.is_recommendation}
            currentLang={currentLang}
          />
        )}

        {/* 3. Recommendation Highlight */}
        {message.recommendation && (
          <div
            style={{
              background: 'rgba(99, 102, 241, 0.08)',
              border: '1px solid rgba(99, 102, 241, 0.25)',
              borderRadius: '10px',
              padding: '12px 14px',
              display: 'flex',
              gap: '10px',
              alignItems: 'flex-start'
            }}
          >
            <span style={{ fontSize: '18px' }}>💡</span>
            <div>
              <strong style={{ fontSize: '13px', color: '#818cf8' }}>
                {isAr ? 'نصيحة أونيست الذكية للمشتري:' : 'Honest Buyer Recommendation:'}
              </strong>
              <div style={{ fontSize: '13.5px', color: '#e5e7eb', marginTop: '3px' }}>
                {message.recommendation}
              </div>
            </div>
          </div>
        )}

        {/* Actions Row */}
        <div style={{ display: 'flex', gap: '8px', marginTop: '4px' }}>
          <button className="icon-btn" onClick={handleCopy} style={{ fontSize: '11px', padding: '4px 8px' }}>
            <span>{copied ? '✓' : '📋'}</span>
            <span>{copied ? (isAr ? 'تم النسخ' : 'Copied') : (isAr ? 'نسخ' : 'Copy')}</span>
          </button>
        </div>
      </div>
    </div>
  );
};

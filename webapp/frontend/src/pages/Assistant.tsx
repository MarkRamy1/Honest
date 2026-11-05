import React, { useEffect, useRef, useState } from 'react';
import { usePreferences } from '../preferences';
import type { ChatMessage, ChatThread, Product } from '../types';
import { api } from '../services/api';
import { Icon } from '../components/Icon';
import { PricingMatrixCard } from '../components/PricingMatrixCard';
import { MaterialVerdictCard } from '../components/MaterialVerdictCard';
import { suggestions } from '../data/mockData';

export interface AssistantProps {
  readonly threads: ChatThread[];
  readonly activeThreadId: string | null;
  readonly onSelectThread: (id: string) => void;
  readonly onNewThread: () => void;
  readonly onDeleteThread: (id: string) => void;
  readonly onSendMessage: (text: string, mode?: 'detailed' | 'quick', model?: string) => Promise<void>;
  readonly isLoading: boolean;
  readonly productContext: Product | null;
  readonly setToast: (msg: string) => void;
  readonly initialPrompt?: string;
  readonly onClearPrompt?: () => void;
}

interface PersonaPreset {
  id: string;
  icon: string;
  labelEn: string;
  labelAr: string;
  query: string;
}

const PERSONA_PRESETS: PersonaPreset[] = [
  {
    id: 'teen-niece',
    icon: '🎁',
    labelEn: '15yo Niece Birthday Gift',
    labelAr: 'هدية عيد ميلاد فتاة 15 سنة',
    query: 'I am shopping on Amazon Egypt for a birthday gift for my 15-year-old niece. My budget is 2,000 to 4,000 EGP. Compare trendy items like the Fujifilm Instax Mini 12 camera, wireless headphones, and oversized hoodies. What are the pros, cons, and hidden costs?'
  },
  {
    id: 'camera-vs-audio',
    icon: '📸',
    labelEn: 'Instax vs Headphones',
    labelAr: 'كاميرا إنستاكس ضد السماعات',
    query: 'Compare the Fujifilm Instax Mini 12 Instant Camera vs Wireless Noise-Cancelling Headphones as a gift for a teenage girl. Are film cartridges included, and is color accurate to photos?'
  },
  {
    id: 'streetwear-fashion',
    icon: '👗',
    labelEn: 'Oversized Hoodie Check',
    labelAr: 'فحص خامة هودي أوفرسايز',
    query: 'How can I verify if an oversized fleece hoodie on Amazon Egypt is real heavyweight cotton or cheap thin polyester? Give me verification telltales.'
  },
  {
    id: 'egypt-market',
    icon: '🇪🇬',
    labelEn: 'Egypt Market Deal & Warranty',
    labelAr: 'أسعار السوق المصري والضمان',
    query: 'On Amazon Egypt (amazon.eg), what is the difference in local warranty and authenticity between items Fulfilled by Amazon vs third-party sellers?'
  }
];

export function Assistant({
  threads,
  activeThreadId,
  onSelectThread,
  onNewThread,
  onDeleteThread,
  onSendMessage,
  isLoading,
  productContext,
  setToast,
  initialPrompt,
  onClearPrompt
}: Readonly<AssistantProps>) {
  const { t, language } = usePreferences();
  const [historyOpen, setHistoryOpen] = useState(false);
  const [mode, setMode] = useState<'detailed' | 'quick'>('detailed');
  const [draft, setDraft] = useState('');
  const [selectedModel, setSelectedModel] = useState('gemini-2.5-flash');
  const bottomRef = useRef<HTMLDivElement>(null);

  const activeThread = threads.find((t) => t.id === activeThreadId) || threads[0];

  useEffect(() => {
    if (initialPrompt) {
      setDraft(initialPrompt);
      if (onClearPrompt) onClearPrompt();
    }
  }, [initialPrompt]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [activeThread?.messages, isLoading]);

  const handleSend = () => {
    if (!draft.trim() || isLoading) return;
    const msg = draft.trim();
    setDraft('');
    onSendMessage(msg, mode, selectedModel);
  };

  const handleCopy = (text: string) => {
    navigator.clipboard
      .writeText(text)
      .then(() => setToast(t('Response copied.')))
      .catch(() => setToast(t('Could not copy to clipboard.')));
  };

  return (
    <div className="chat-page">
      {/* Conversation History Drawer */}
      <aside className={`chat-history ${historyOpen ? 'is-open' : ''}`}>
        <div className="chat-history-title">
          <h2>{t('Your conversations')}</h2>
          <span>{threads.length}</span>
        </div>

        <button
          className="button primary"
          onClick={() => {
            onNewThread();
            setHistoryOpen(false);
          }}
        >
          <Icon name="plus" size={18} /> {t('New conversation')}
        </button>

        <span className="eyebrow history-label">{t('RECENT')}</span>

        {threads.length ? (
          threads.map((c) => (
            <div
              className={`conversation-row ${activeThread?.id === c.id ? 'selected' : ''}`}
              key={c.id}
            >
              <button
                onClick={() => {
                  onSelectThread(c.id);
                  setHistoryOpen(false);
                }}
              >
                <Icon name="chat" size={17} />
                <span>{c.title}</span>
              </button>
              <button
                className="icon-button"
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteThread(c.id);
                }}
                aria-label={`Delete conversation ${c.title}`}
              >
                <Icon name="trash" size={14} />
              </button>
            </div>
          ))
        ) : (
          <p className="muted history-empty">
            {t('A good question is the start of a better purchase.')}
          </p>
        )}

        <div className="privacy-note">
          <Icon name="shield" size={19} />
          <p>
            {t('Your conversations stay on this device.')}
            <small>{t('Questions are sent to the backend to generate answers.')}</small>
          </p>
        </div>
      </aside>

      {/* Main Chat Area */}
      <section className="chat-main">
        <header className="chat-header">
          <div>
            <span className="chat-logo">
              <Icon name="sparkles" />
            </span>
            <div>
              <h1>{t('AI shopping assistant')}</h1>
              <p>{t('Your independent shopping advisor · Honest Engine v4.0')}</p>
            </div>
          </div>

          <div className="chat-header-actions">
            <div className="mode-toggle">
              <button
                aria-pressed={mode === 'detailed'}
                onClick={() => setMode('detailed')}
              >
                {t('Detailed Analysis')}
              </button>
              <button
                aria-pressed={mode === 'quick'}
                onClick={() => setMode('quick')}
              >
                {t('Quick Summary')}
              </button>
            </div>

            <button
              className="text-button"
              onClick={() => {
                if (activeThread) onDeleteThread(activeThread.id);
              }}
            >
              <Icon name="trash" size={15} /> {t('Clear Chat')}
            </button>

            <button
              className="icon-button"
              aria-label={t('Start new conversation')}
              onClick={onNewThread}
            >
              <Icon name="plus" size={17} />
            </button>

            <button
              className="icon-button chat-history-toggle"
              aria-label={t('Conversation history')}
              aria-expanded={historyOpen}
              onClick={() => setHistoryOpen(!historyOpen)}
            >
              <Icon name="clock" size={17} />
            </button>
          </div>
        </header>

        {/* Messages Scroll Area */}
        <div className="chat-scroll" aria-live="polite">
          {!activeThread?.messages.length ? (
            <div className="chat-welcome">
              <div className="welcome-orb">
                <Icon name="sparkles" size={35} />
              </div>
              <span className="eyebrow">{t('A BETTER BUY STARTS WITH A CONVERSATION')}</span>
              <h2>{t('What’s on your wishlist?')}</h2>
              <p>
                {t('A second opinion. A smarter comparison. A little help finding the one.')}
                <br />
                {t('Whatever you’re shopping for, let’s figure it out together.')}
              </p>

              <div className="suggestion-grid">
                {suggestions.map((s) => (
                  <button
                    key={s.title}
                    onClick={() => {
                      setDraft(s.text);
                    }}
                  >
                    <Icon name={s.icon} size={23} />
                    <strong>{t(s.title)}</strong>
                    <span>{t(s.text)}</span>
                    <Icon name="diagonal" size={17} />
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="messages">
              {activeThread.messages.map((m) => {
                const isUser = m.sender === 'user' || m.role === 'user';
                const messageText = m.text || m.content || '';

                return (
                  <div key={m.id} className={`message ${isUser ? 'user' : ''}`}>
                    <div className="message-avatar">
                      <Icon name={isUser ? 'users' : 'shield'} size={18} />
                    </div>

                    <div className="message-body">
                      <div className="message-author">
                        <span>{isUser ? t('You') : m.model_name || t('Honest Truth Engine 4.0')}</span>
                        {m.timestamp && <small>{m.timestamp}</small>}
                      </div>

                      <div className="message-text">
                        <p>{messageText}</p>
                      </div>

                      {/* Forensic Cards Embedded in AI Responses */}
                      {!isUser && m.material_verdict && (
                        <div style={{ marginTop: 16 }}>
                          <MaterialVerdictCard verdict={m.material_verdict} currentLang={language} />
                        </div>
                      )}

                      {!isUser && m.price_matrix && (
                        <div style={{ marginTop: 16 }}>
                          <PricingMatrixCard matrix={m.price_matrix} currentLang={language} />
                        </div>
                      )}

                      {!isUser && (
                        <button
                          className="text-button copy-message"
                          onClick={() => handleCopy(messageText)}
                        >
                          <Icon name="copy" size={14} /> {t('Copy response')}
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}

              {isLoading && (
                <div className="thinking" role="status">
                  <Icon name="sparkles" size={19} />
                  <span>{t('Looking into it')}</span>
                  <span />
                  <span />
                  <span />
                </div>
              )}

              <div ref={bottomRef} />
            </div>
          )}
        </div>

        {/* Composer Area */}
        <div className="composer-area">
          {productContext && (
            <span className="context-pill">
              <Icon name="bag" size={14} /> {t('In context:')} {productContext.name}
            </span>
          )}

          {/* Quick Persona & Gift Advisor Chips */}
          <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '6px', marginBottom: '8px', scrollbarWidth: 'none' }}>
            {PERSONA_PRESETS.map((p) => (
              <button
                key={p.id}
                type="button"
                onClick={() => {
                  setDraft(p.query);
                }}
                style={{
                  background: 'rgba(99, 102, 241, 0.08)',
                  border: '1px solid rgba(99, 102, 241, 0.25)',
                  color: '#4f46e5',
                  padding: '5px 12px',
                  borderRadius: '999px',
                  fontSize: '11px',
                  fontWeight: 700,
                  cursor: 'pointer',
                  whiteSpace: 'nowrap',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px',
                  transition: 'all 0.2s'
                }}
              >
                <span>{p.icon}</span>
                <span>{language === 'ar' ? p.labelAr : p.labelEn}</span>
              </button>
            ))}
          </div>

          <form
            className="composer"
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
          >
            <textarea
              aria-label={t('Message your shopping assistant')}
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              placeholder={t('Ask anything about specs, hidden flaws, or comparisons…')}
              maxLength={4000}
              rows={2}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
            />

            <div className="composer-bottom">
              <div className="composer-options">
                <Icon name="sparkles" size={15} />
                <select
                  aria-label={t('AI model')}
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                >
                  <option value="gemini-2.5-flash">Gemini 2.5 Flash (Grounded)</option>
                  <option value="gemini-1.5-pro">Gemini 1.5 Pro (Deep Reasoning)</option>
                  <option value="gpt-4o">GPT-4o (OpenAI)</option>
                  <option value="mock">Offline Mock Engine</option>
                </select>
              </div>

              <button
                type="submit"
                className="send-button"
                disabled={!draft.trim() || isLoading}
                aria-label={t('Send message')}
              >
                <Icon name="up" size={21} />
              </button>
            </div>
          </form>

          <p className="composer-note">
            {t('AI can make mistakes. Check important details with the retailer.')}{' '}
            <span>{t('Enter to send · Shift + Enter for a new line')}</span>
          </p>
        </div>
      </section>
    </div>
  );
}

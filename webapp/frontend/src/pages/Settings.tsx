import React, { useState } from 'react';
import { usePreferences } from '../preferences';
import type { User } from '../types';
import { Icon } from '../components/Icon';

export interface SettingsProps {
  readonly user: User | null;
  readonly onOpenAccount: () => void;
  readonly onClearAllData: () => void;
  readonly setToast: (msg: string) => void;
}

export function Settings({
  user,
  onOpenAccount,
  onClearAllData,
  setToast
}: Readonly<SettingsProps>) {
  const { t } = usePreferences();
  const [confirmClear, setConfirmClear] = useState(false);

  const handleClear = () => {
    onClearAllData();
    setConfirmClear(false);
    setToast(t('Your local shopping data has been cleared.'));
  };

  return (
    <div className="page settings-page">
      <div className="page-heading">
        <div>
          <div className="eyebrow">{t('MAKE YOURSELF AT HOME')}</div>
          <h1>
            {t('Settings & help')}
            <span className="heading-dot">.</span>
          </h1>
          <p>{t('Your account, your data, and Honest on the go.')}</p>
        </div>
      </div>

      {/* Account Section */}
      <section className="panel settings-row">
        <div>
          <h2>{t('Your account')}</h2>
          <p>
            {user
              ? `Signed in as ${user.email}`
              : t('Sign in or create an account to join the community.')}
          </p>
        </div>
        <button className="button secondary" onClick={onOpenAccount}>
          {user ? t('Manage account') : t('Sign in')}
        </button>
      </section>

      {/* Browser Extension Section */}
      <section className="panel">
        <div className="section-heading">
          <div>
            <h2>{t('Honest, right in your browser')}</h2>
            <p>{t('Analyze a product without leaving its store page.')}</p>
          </div>
          <div className="inline-actions">
            <span className="pill">Manifest V3 Extension</span>
            <a
              className="button secondary"
              href="http://127.0.0.1:8000/extension/download"
              download="honest4-extension.zip"
            >
              {t('Download extension')}
            </a>
          </div>
        </div>

        <ol className="install-steps">
          <li>
            <span>1</span>
            <div>
              <strong>{t('Open Chrome’s extensions page')}</strong>
              <p>
                {t('Visit')} <code>{t('chrome://extensions')}</code> {t('and enable Developer mode.')}
              </p>
            </div>
          </li>
          <li>
            <span>2</span>
            <div>
              <strong>{t('Load unpacked')}</strong>
              <p>
                {t('Click Load unpacked in the top left and select:')} <code>D:\Honest\extension</code>
              </p>
            </div>
          </li>
          <li>
            <span>3</span>
            <div>
              <strong>{t('Give your next find a closer look')}</strong>
              <p>
                {t('Open any Amazon, Noon, or AliExpress page, or test the Demo Testing Stage.')}
              </p>
            </div>
          </li>
        </ol>
      </section>

      {/* Local Storage Privacy */}
      <section className="panel">
        <h2>{t('Your data stays yours')}</h2>
        <p>
          {t(
            'Saved products, analysis history, and conversations are stored in this browser. Accounts and community reviews are stored by the backend. Questions and product details are sent to the API when you request an analysis or answer.'
          )}
        </p>

        <div className="settings-row">
          <div>
            <h3>{t('Clear local shopping data')}</h3>
            <p>
              {t(
                'This removes saved products, analysis history, chat history, and local helpful-review marks.'
              )}
            </p>
          </div>

          {confirmClear ? (
            <div className="inline-actions">
              <button className="button secondary" onClick={() => setConfirmClear(false)}>
                {t('Cancel')}
              </button>
              <button className="button danger" onClick={handleClear}>
                {t('Clear data')}
              </button>
            </div>
          ) : (
            <button className="button secondary" onClick={() => setConfirmClear(true)}>
              <Icon name="trash" size={17} /> {t('Clear local data')}
            </button>
          )}
        </div>
      </section>

      {/* FAQs */}
      <section className="panel">
        <h2>{t('Understanding your results')}</h2>
        <details>
          <summary>{t('Are the scores verified?')}</summary>
          <p>
            {t(
              'No. AI responses are estimates; when the AI provider is unavailable the backend uses category-based demo heuristics. Each report shows which source it used.'
            )}
          </p>
        </details>
        <details>
          <summary>{t('Are prices current?')}</summary>
          <p>
            {t(
              'The backend includes a reference catalog and heuristic prices. Check the retailer’s page for current prices, stock, shipping, and returns.'
            )}
          </p>
        </details>
        <details>
          <summary>{t('Does the Reality Studio create images?')}</summary>
          <p>
            {t(
              'The current API creates an image-generation prompt for a lighting environment. You can copy it into an image generator. It does not produce or verify a photograph.'
            )}
          </p>
        </details>
      </section>
    </div>
  );
}

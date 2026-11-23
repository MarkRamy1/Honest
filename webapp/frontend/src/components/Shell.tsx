import React, { useState, type ReactNode } from 'react';
import { usePreferences } from '../preferences';
import { navigation } from '../data/mockData';
import { Icon } from './Icon';
import type { Page, User } from '../types';

export interface ShellProps {
  readonly page: Page;
  readonly onNavigate: (page: Page) => void;
  readonly user: User | null;
  readonly savedCount: number;
  readonly isOnline: boolean;
  readonly toast: string;
  readonly setToast: (msg: string) => void;
  readonly onOpenAccount: () => void;
  readonly children: ReactNode;
}

export function Shell({
  page,
  onNavigate,
  user,
  savedCount,
  isOnline,
  toast,
  setToast,
  onOpenAccount,
  children
}: Readonly<ShellProps>) {
  const { t, language, setLanguage, theme, toggleTheme } = usePreferences();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleNavClick = (targetPage: Page) => {
    onNavigate(targetPage);
    setMobileMenuOpen(false);
  };

  const handleNotify = () => {
    setToast(t('Independent Metric Verification: All engine scores calibrated and updated.'));
  };

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">
        {t('Skip to main content')}
      </a>
      {mobileMenuOpen && (
        <button
          className="sidebar-backdrop"
          aria-label={t('Close navigation')}
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Stitch Sidebar */}
      <aside className={`sidebar ${mobileMenuOpen ? 'open' : ''}`}>
        <a className="brand" href="#dashboard" onClick={() => handleNavClick('dashboard')}>
          <span className="brand-symbol">
            <Icon name="shield" size={27} />
          </span>
          <span className="brand-copy" translate="no">
            {t('Honest AI')}
            <small>{t('v4.0 Assistant')}</small>
          </span>
        </a>

        <nav aria-label={t('Main navigation')}>
          {navigation
            .filter((n) => !['saved', 'reviews', 'settings'].includes(n.id))
            .map((n) => {
              const isActive =
                page === n.id ||
                (n.id === 'analysis' && ['studio', 'compare'].includes(page));
              return (
                <a
                  key={n.id}
                  href={`#${n.id}`}
                  onClick={(e) => {
                    e.preventDefault();
                    handleNavClick(n.id as Page);
                  }}
                  className={isActive ? 'active' : ''}
                  aria-current={isActive ? 'page' : undefined}
                >
                  <Icon name={n.icon} />
                  <span>{t(n.label)}</span>
                </a>
              );
            })}
        </nav>

        <div className="sidebar-bottom">
          <div className="secondary-nav">
            <a
              href="#saved"
              className={page === 'saved' ? 'active' : ''}
              onClick={(e) => {
                e.preventDefault();
                handleNavClick('saved');
              }}
            >
              <Icon name="bookmark" size={18} />
              <span>{t('Saved products')}</span>
              {savedCount > 0 && <span className="nav-count">{savedCount}</span>}
            </a>

            <a
              href="#reviews"
              className={page === 'reviews' ? 'active' : ''}
              onClick={(e) => {
                e.preventDefault();
                handleNavClick('reviews');
              }}
            >
              <Icon name="users" size={18} />
              <span>{t('Community')}</span>
            </a>

            <a
              href="#settings"
              className={page === 'settings' || page === 'extension' ? 'active' : ''}
              onClick={(e) => {
                e.preventDefault();
                handleNavClick('settings');
              }}
            >
              <Icon name="settings" size={18} />
              <span>{t('Settings & help')}</span>
            </a>
          </div>

          <div className="engine-status">
            <i />
            <span>{t('AI Engine Active')}</span>
            <strong>{isOnline ? '99.8%' : t('Offline')}</strong>
          </div>

          <div className="engine-version">
            <span>{t('Honest Engine Core')}</span>
            <span translate="no">{t('v4.0.2')}</span>
          </div>
        </div>
      </aside>

      {/* Main Shell */}
      <div className="main-shell" dir={language === 'ar' ? 'rtl' : 'ltr'}>
        <header className="topbar">
          <div className="verification">
            <button
              className="icon-button mobile-menu"
              aria-label={t('Open navigation')}
              aria-expanded={mobileMenuOpen}
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              <Icon name="menu" />
            </button>
            <Icon name="shield" size={16} />
            <span>{t('Independent Metric Verification')}</span>
          </div>

          <div className="topbar-right">
            <div className="language-toggle" aria-label={t('Language')}>
              <button
                className={language === 'en' ? 'active' : ''}
                onClick={() => setLanguage('en')}
              >
                {t('EN')}
              </button>
              <button
                className={language === 'ar' ? 'active' : ''}
                onClick={() => setLanguage('ar')}
              >
                العربية
              </button>
            </div>

            <button
              type="button"
              className="theme-toggle-btn"
              onClick={toggleTheme}
              aria-label={theme === 'dark' ? t('Switch to light mode') : t('Switch to dark mode')}
              title={theme === 'dark' ? t('Switch to light mode') : t('Switch to dark mode')}
            >
              <Icon name={theme === 'dark' ? 'sun' : 'moon'} size={15} />
              <span className="theme-toggle-label">{theme === 'dark' ? t('Light') : t('Dark')}</span>
            </button>

            <button
              className="notification-button"
              aria-label={t('Notifications')}
              onClick={handleNotify}
            >
              <Icon name="alert" size={19} />
              <i />
            </button>

            <span
              className={`connection ${!isOnline ? 'offline' : ''}`}
              title={isOnline ? 'Backend connected' : 'Backend offline'}
            >
              <i />
            </span>

            <button className="topbar-account" onClick={onOpenAccount} aria-label={t('Your account')}>
              <span className="top-avatar">
                {user?.name.slice(0, 1).toUpperCase() || 'H'}
              </span>
              <span className="account-label">
                <strong>{user?.name || t('Analyst Session')}</strong>
                <span>{user ? t('Your account') : t('Personal Pro')}</span>
              </span>
            </button>
          </div>
        </header>

        <main id="main-content">{children}</main>

        <footer className="footer">
          <span>
            <Icon name="shield" size={14} /> {t('Independent shopping intelligence.')}
          </span>
          <span>{t('Honest Engine v4.0.2')}</span>
        </footer>
      </div>

      {toast && (
        <div className="toast" role="status" aria-live="polite">
          <Icon name="success" size={20} />
          {toast}
        </div>
      )}
    </div>
  );
}

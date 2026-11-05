import React, { useEffect, useRef, useState } from 'react';
import { usePreferences } from '../preferences';
import { api } from '../services/api';
import type { User } from '../types';
import { Feedback } from './Feedback';
import { Icon } from './Icon';

export interface AccountDialogProps {
  readonly user: User | null;
  readonly onUserChange: (user: User | null) => void;
  readonly setToast: (msg: string) => void;
  readonly onClose: () => void;
}

export function AccountDialog({ user, onUserChange, setToast, onClose }: Readonly<AccountDialogProps>) {
  const { t } = usePreferences();
  const dialog = useRef<HTMLDialogElement>(null);
  const [register, setRegister] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    dialog.current?.showModal();
  }, []);

  async function submit(form: HTMLFormElement) {
    setBusy(true);
    setError('');
    const data = Object.fromEntries(new FormData(form));

    try {
      if (register) {
        const res = await api.register(String(data.name || ''), String(data.email || ''), String(data.password || ''));
        if (res.user) {
          onUserChange(res.user);
          localStorage.setItem('honest_auth_user', JSON.stringify(res.user));
          setToast(`Welcome, ${res.user.name}.`);
          onClose();
        } else {
          setError(res.message || 'Registration failed.');
        }
      } else {
        const res = await api.login(String(data.email || ''), String(data.password || ''));
        if (res.user) {
          onUserChange(res.user);
          localStorage.setItem('honest_auth_user', JSON.stringify(res.user));
          setToast(`Welcome back, ${res.user.name}.`);
          onClose();
        } else {
          setError(res.message || 'Invalid credentials.');
        }
      }
    } catch (e: any) {
      setError(e?.message || 'Authentication error. Please check your credentials.');
    } finally {
      setBusy(false);
    }
  }

  const handleLogout = async () => {
    await api.logout();
    onUserChange(null);
    setToast('Signed out successfully.');
    onClose();
  };

  return (
    <dialog
      ref={dialog}
      className="account-dialog"
      onCancel={onClose}
      onClick={(e) => {
        if (e.target === dialog.current) onClose();
      }}
      aria-labelledby="account-title"
    >
      <div className="dialog-body">
        <button className="icon-button dialog-close" aria-label={t('Close account dialog')} onClick={onClose}>
          <Icon name="close" />
        </button>
        <div className="large-icon">
          <Icon name="shield" size={30} />
        </div>
        {user ? (
          <>
            <h2 id="account-title">
              {t('Hello,')} {user.name}
            </h2>
            <p>{user.email}</p>
            <p>{t('Your account is connected. Saved items and conversations remain on this device.')}</p>
            <button className="button secondary" onClick={handleLogout}>
              <Icon name="logout" size={17} /> {t('Sign out')}
            </button>
          </>
        ) : (
          <>
            <h2 id="account-title">{register ? t('A smarter way to shop.') : t('Welcome back.')}</h2>
            <p>{register ? t('Create your Honest AI account.') : t('Sign in to your Honest AI account.')}</p>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                submit(e.currentTarget);
              }}
            >
              {register && (
                <div className="field">
                  <label htmlFor="account-name">{t('Your name')}</label>
                  <input id="account-name" name="name" autoComplete="name" required maxLength={255} />
                </div>
              )}
              <div className="field">
                <label htmlFor="account-email">{t('Email address')}</label>
                <input id="account-email" name="email" type="email" autoComplete="email" required maxLength={255} />
              </div>
              <div className="field">
                <label htmlFor="account-password">{t('Password')}</label>
                <input
                  id="account-password"
                  name="password"
                  type="password"
                  autoComplete={register ? 'new-password' : 'current-password'}
                  required
                  minLength={register ? 6 : 1}
                />
              </div>
              {error && <Feedback message={error} />}
              <button className="button primary full-width" disabled={busy}>
                {busy ? t('Please wait…') : register ? t('Create account') : t('Sign in')}
                <Icon name="arrow" size={17} />
              </button>
            </form>
            <button
              className="text-button auth-switch"
              onClick={() => {
                setRegister(!register);
                setError('');
              }}
            >
              {register ? t('Already have an account? Sign in') : t('New here? Create an account')}
            </button>
          </>
        )}
      </div>
    </dialog>
  );
}

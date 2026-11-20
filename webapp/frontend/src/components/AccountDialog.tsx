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
  const googleBtnRef = useRef<HTMLDivElement>(null);
  const [register, setRegister] = useState(false);
  const [googlePromptOpen, setGooglePromptOpen] = useState(false);
  const [googleClientId, setGoogleClientId] = useState<string>(() => {
    return import.meta.env.VITE_GOOGLE_CLIENT_ID || localStorage.getItem('honest_google_client_id') || '';
  });
  const [clientIdDraft, setClientIdDraft] = useState<string>(googleClientId);
  const [googleEmail, setGoogleEmail] = useState('');
  const [googleName, setGoogleName] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    dialog.current?.showModal();
  }, []);

  async function verifyGoogleCredential(credentialToken: string) {
    setBusy(true);
    setError('');
    try {
      const res = await api.googleAuth({ credential: credentialToken });
      if (res.user) {
        onUserChange(res.user);
        localStorage.setItem('honest_auth_user', JSON.stringify(res.user));
        setToast(res.message || `Signed in with Google as ${res.user.name}.`);
        onClose();
      } else {
        setError(res.detail || res.message || 'Google token verification failed.');
      }
    } catch (err: any) {
      setError(err?.message || 'Could not verify Google credential.');
    } finally {
      setBusy(false);
    }
  }

  // Initialize official Google Identity Services button when a Client ID is configured
  useEffect(() => {
    if (!googleClientId || user) return;
    const g = (window as any).google;
    if (g?.accounts?.id && googleBtnRef.current) {
      try {
        g.accounts.id.initialize({
          client_id: googleClientId,
          callback: (response: { credential?: string }) => {
            if (response.credential) {
              verifyGoogleCredential(response.credential);
            }
          }
        });
        g.accounts.id.renderButton(googleBtnRef.current, {
          theme: 'outline',
          size: 'large',
          width: 320,
          text: register ? 'signup_with' : 'continue_with'
        });
      } catch (e) {
        console.warn('Google Identity Services init error:', e);
      }
    }
  }, [googleClientId, register, user]);

  function handleLaunchRealGooglePopup() {
    setError('');
    const g = (window as any).google;
    if (googleClientId && g?.accounts?.oauth2) {
      try {
        const tokenClient = g.accounts.oauth2.initTokenClient({
          client_id: googleClientId,
          scope: 'openid email profile',
          callback: (tokenResponse: { access_token?: string; error?: string }) => {
            if (tokenResponse?.access_token) {
              verifyGoogleCredential(tokenResponse.access_token);
            } else if (tokenResponse?.error) {
              setError(`Google OAuth error: ${tokenResponse.error}`);
            }
          }
        });
        tokenClient.requestAccessToken();
        return;
      } catch (err: any) {
        setError(err?.message || 'Failed to launch Google OAuth popup.');
      }
    }
    setGooglePromptOpen(!googlePromptOpen);
  }

  function handleSaveClientId(e: React.FormEvent) {
    e.preventDefault();
    const cleaned = clientIdDraft.trim();
    localStorage.setItem('honest_google_client_id', cleaned);
    setGoogleClientId(cleaned);
    if (cleaned) {
      setToast('Google OAuth Client ID saved! Click Continue with Google to launch the popup.');
    }
  }

  async function handleGoogleContinue(e?: React.FormEvent) {
    if (e) e.preventDefault();
    if (!googleEmail.trim()) return;

    setBusy(true);
    setError('');
    try {
      const res = await api.googleAuth({
        email: googleEmail.trim(),
        name: googleName.trim() || undefined
      });
      if (res.user) {
        onUserChange(res.user);
        localStorage.setItem('honest_auth_user', JSON.stringify(res.user));
        setToast(res.message || `Connected with Google as ${res.user.name}.`);
        onClose();
      } else {
        setError(res.detail || res.message || 'Google authentication failed.');
      }
    } catch (err: any) {
      setError(err?.message || 'Could not complete Google Sign-In.');
    } finally {
      setBusy(false);
    }
  }

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

            {/* Google Sign-In / Sign-Up Button & Real GIS OAuth / Dev Fallback */}
            <div style={{ marginBottom: 14 }}>
              {googleClientId && (
                <div
                  ref={googleBtnRef}
                  style={{ display: 'flex', justifyContent: 'center', marginBottom: 8 }}
                />
              )}

              <button
                type="button"
                className="button secondary full-width"
                disabled={busy}
                onClick={handleLaunchRealGooglePopup}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 10,
                  fontWeight: 600
                }}
              >
                <svg width="18" height="18" viewBox="0 0 48 48" aria-hidden="true">
                  <path
                    fill="#EA4335"
                    d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"
                  />
                  <path
                    fill="#4285F4"
                    d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"
                  />
                  <path
                    fill="#34A853"
                    d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"
                  />
                </svg>
                <span>{register ? t('Sign up with Google') : t('Continue with Google')}</span>
              </button>

              {googlePromptOpen && (
                <div
                  style={{
                    marginTop: 10,
                    padding: 12,
                    borderRadius: 12,
                    border: '1px solid rgba(99, 102, 241, 0.25)',
                    background: 'rgba(99, 102, 241, 0.05)',
                    textAlign: 'left'
                  }}
                >
                  <form onSubmit={handleSaveClientId} style={{ marginBottom: 12 }}>
                    <div className="field" style={{ marginBottom: 6 }}>
                      <label htmlFor="google-client-id" style={{ fontSize: '0.76rem', fontWeight: 700 }}>
                        🔑 Real Google OAuth Client ID (Google Cloud Console)
                      </label>
                      <input
                        id="google-client-id"
                        type="text"
                        placeholder="xxxx-xxxx.apps.googleusercontent.com"
                        value={clientIdDraft}
                        onChange={(e) => setClientIdDraft(e.target.value)}
                        style={{ fontSize: '0.78rem' }}
                      />
                    </div>
                    <div style={{ fontSize: '0.71rem', opacity: 0.78, marginBottom: 8, lineHeight: 1.35 }}>
                      Add <code>http://localhost:5173</code> &amp; <code>http://127.0.0.1:5173</code> to{' '}
                      <strong>Authorized JavaScript origins</strong> in Google Cloud Console &rarr; Credentials, then paste your Client ID above.
                    </div>
                    <button type="submit" className="button secondary full-width" style={{ fontSize: '0.78rem', padding: '6px 10px' }}>
                      {googleClientId ? 'Update OAuth Client ID' : 'Enable Real Google OAuth Popup'}
                    </button>
                  </form>

                  <details>
                    <summary style={{ fontSize: '0.75rem', cursor: 'pointer', fontWeight: 600, opacity: 0.85 }}>
                      🧪 Or use Local Dev Sandbox (No Google Console needed)
                    </summary>
                    <form onSubmit={handleGoogleContinue} style={{ marginTop: 8 }}>
                      <div className="field" style={{ marginBottom: 8 }}>
                        <label htmlFor="google-email">{t('Google Email')}</label>
                        <input
                          id="google-email"
                          type="email"
                          placeholder="you@gmail.com"
                          value={googleEmail}
                          onChange={(e) => setGoogleEmail(e.target.value)}
                          required
                        />
                      </div>
                      <div className="field" style={{ marginBottom: 10 }}>
                        <label htmlFor="google-name">
                          {t('Your name')} <span>{t('(optional)')}</span>
                        </label>
                        <input
                          id="google-name"
                          type="text"
                          placeholder="Google Account Name"
                          value={googleName}
                          onChange={(e) => setGoogleName(e.target.value)}
                        />
                      </div>
                      <button type="submit" className="button primary full-width" disabled={busy || !googleEmail.trim()}>
                        {busy ? t('Please wait…') : t('Connect Google Account')}
                      </button>
                    </form>
                  </details>
                </div>
              )}

              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                  margin: '12px 0 4px 0',
                  fontSize: '0.78rem',
                  opacity: 0.7
                }}
              >
                <span style={{ flex: 1, height: 1, background: 'currentColor', opacity: 0.2 }} />
                <span>{t('or continue with email')}</span>
                <span style={{ flex: 1, height: 1, background: 'currentColor', opacity: 0.2 }} />
              </div>
            </div>

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

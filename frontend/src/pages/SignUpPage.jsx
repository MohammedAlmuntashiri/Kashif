// Sign-up / create-account page (mock auth — see AuthContext.jsx).

import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { useAuth } from '../auth/AuthContext.jsx';
import { useLang } from '../i18n/LanguageContext.jsx';

export default function SignUpPage() {
  const { t } = useLang();
  const { signUp } = useAuth();
  const navigate = useNavigate();

  const [name,     setName]     = useState('');
  const [email,    setEmail]    = useState('');
  const [password, setPassword] = useState('');
  const [confirm,  setConfirm]  = useState('');
  const [busy,     setBusy]     = useState(false);
  const [error,    setError]    = useState(null);

  const errToKey = (code) => ({
    NAME_REQUIRED:       'auth.err.nameRequired',
    INVALID_EMAIL:       'auth.err.invalidEmail',
    PASSWORD_TOO_SHORT:  'auth.err.passwordTooShort',
    EMAIL_TAKEN:         'auth.err.emailTaken',
  }[code] || 'auth.err.generic');

  const onSubmit = async (e) => {
    e.preventDefault();
    if (busy) return;
    if (password !== confirm) {
      setError(t('auth.err.passwordsMismatch'));
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const u = await signUp({ name, email, password });
      toast.success(t('auth.toast.welcome', { name: u?.name || name }));
      navigate('/', { replace: true });
    } catch (err) {
      const msg = t(errToKey(err.message));
      setError(msg);
      toast.error(msg);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="max-w-md mx-auto px-6 py-12">
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm p-8">
        <h1 className="font-display text-2xl sm:text-3xl font-bold text-slate-900 dark:text-slate-100 tracking-tight mb-1">
          {t('auth.signUp.title')}
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">
          {t('auth.signUp.subtitle')}
        </p>

        <form onSubmit={onSubmit} className="space-y-4">
          <Field
            label={t('auth.field.name')}
            type="text"
            value={name}
            onChange={setName}
            autoComplete="name"
            required
          />
          <Field
            label={t('auth.field.email')}
            type="email"
            value={email}
            onChange={setEmail}
            autoComplete="email"
            required
          />
          <Field
            label={t('auth.field.password')}
            type="password"
            value={password}
            onChange={setPassword}
            autoComplete="new-password"
            hint={t('auth.field.passwordHint')}
            required
          />
          <Field
            label={t('auth.field.confirm')}
            type="password"
            value={confirm}
            onChange={setConfirm}
            autoComplete="new-password"
            required
          />

          {error && (
            <div className="text-sm text-rose-700 dark:text-rose-300 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/50 px-3 py-2 rounded-lg">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={busy}
            className="w-full px-4 py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-sm font-semibold disabled:bg-slate-300 dark:disabled:bg-slate-700 dark:disabled:text-slate-500 disabled:cursor-not-allowed transition"
          >
            {busy ? t('auth.signUp.busy') : t('auth.signUp.submit')}
          </button>
        </form>

        <div className="text-sm text-slate-500 dark:text-slate-400 mt-6 text-center">
          {t('auth.signUp.haveAccount')}{' '}
          <Link
            to="/signin"
            className="text-brand-600 dark:text-brand-400 hover:underline font-medium"
          >
            {t('auth.signUp.signInLink')}
          </Link>
        </div>
      </div>
    </div>
  );
}

function Field({ label, type, value, onChange, autoComplete, hint, required }) {
  return (
    <label className="block">
      <span className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
        {label}
      </span>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        autoComplete={autoComplete}
        required={required}
        dir={type === 'text' ? 'auto' : 'ltr'}
        className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 placeholder:text-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
      />
      {hint && (
        <span className="block text-xs text-slate-400 dark:text-slate-500 mt-1">{hint}</span>
      )}
    </label>
  );
}

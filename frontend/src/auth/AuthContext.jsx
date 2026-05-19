// Auth context — backed by the Flask /api/auth/* endpoints.
//
// On sign-in/sign-up the server returns a JWT + a public user object.
// The token is stored in localStorage under `kashif.token` and the
// session under `kashif.session` so the UI rehydrates instantly on
// reload. On first mount we also call /api/auth/me to confirm the
// token is still valid; if the server rejects it (expired, deleted
// user), we sign out automatically.
//
// Public shape consumed by SignInPage, SignUpPage, UserMenu:
//   { user, ready, signIn, signUp, signOut }
// Error codes returned from the backend (NO_ACCOUNT, WRONG_PASSWORD,
// EMAIL_TAKEN, INVALID_EMAIL, PASSWORD_TOO_SHORT, NAME_REQUIRED) are
// thrown verbatim so the existing i18n keys keep working unchanged.

import React, { createContext, useContext, useEffect, useState } from 'react';

import { apiSignIn, apiSignUp, apiFetchMe } from '../services/api.js';

const TOKEN_KEY   = 'kashif.token';
const SESSION_KEY = 'kashif.session';

const AuthContext = createContext(null);

// One-shot cleanup of the old localStorage-mock account store (passwords
// hashed client-side). Real accounts live in Postgres now — sweep the
// stale keys away so the browser's storage doesn't hold a dead password
// hash forever.
(function wipeLegacyMockUsers() {
  try { localStorage.removeItem('kashif.users'); } catch (_) {}
})();

const readSession = () => {
  try   { return JSON.parse(localStorage.getItem(SESSION_KEY) || 'null'); }
  catch { return null; }
};
const writeSession = (s) =>
  s ? localStorage.setItem(SESSION_KEY, JSON.stringify(s))
    : localStorage.removeItem(SESSION_KEY);
const writeToken = (t) =>
  t ? localStorage.setItem(TOKEN_KEY, t)
    : localStorage.removeItem(TOKEN_KEY);

export function AuthProvider({ children }) {
  // Show the cached session immediately for a snappier first paint;
  // the /me call below will overwrite or clear it.
  const [user,  setUser]  = useState(readSession);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let token = null;
    try { token = localStorage.getItem(TOKEN_KEY); } catch (_) {}
    if (!token) {
      setReady(true);
      return;
    }
    apiFetchMe()
      .then(({ user: fresh }) => {
        setUser(fresh);
        writeSession(fresh);
      })
      .catch(() => {
        // Token rejected — clear local state silently.
        writeToken(null);
        writeSession(null);
        setUser(null);
      })
      .finally(() => setReady(true));
  }, []);

  const signUp = async ({ name, email, password }) => {
    const { token, user: u } = await apiSignUp({ name, email, password });
    writeToken(token);
    writeSession(u);
    setUser(u);
    return u;
  };

  const signIn = async ({ email, password }) => {
    const { token, user: u } = await apiSignIn({ email, password });
    writeToken(token);
    writeSession(u);
    setUser(u);
    return u;
  };

  const signOut = () => {
    writeToken(null);
    writeSession(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, ready, signIn, signUp, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
};

// Mock auth context — frontend-only, localStorage-backed.
//
// Accounts live in localStorage under `kashif.users` and the current
// session under `kashif.session`. Passwords are SHA-256 hashed via
// window.crypto.subtle before being stored — not a real security
// guarantee (an attacker with localStorage access can replay the hash),
// but at least we don't keep plain text.
//
// SWAP-OUT POINT: when the backend grows real auth, replace the body of
// signIn / signUp / signOut with API calls. The shape returned by useAuth
// (user, signIn, signUp, signOut, ready) should stay the same so no
// pages need touching.

import React, { createContext, useContext, useEffect, useState } from 'react';

const USERS_KEY   = 'kashif.users';
const SESSION_KEY = 'kashif.session';

const AuthContext = createContext(null);

// ── Helpers ──────────────────────────────────────────────────────────
const loadUsers = () => {
  try   { return JSON.parse(localStorage.getItem(USERS_KEY) || '{}'); }
  catch { return {}; }
};
const saveUsers = (u) => localStorage.setItem(USERS_KEY, JSON.stringify(u));

const loadSession = () => {
  try   { return JSON.parse(localStorage.getItem(SESSION_KEY) || 'null'); }
  catch { return null; }
};
const saveSession = (s) =>
  s ? localStorage.setItem(SESSION_KEY, JSON.stringify(s))
    : localStorage.removeItem(SESSION_KEY);

// SHA-256 hex digest via SubtleCrypto. Good enough for our mock-only
// store; not a substitute for server-side bcrypt/argon2.
async function hashPassword(password) {
  const bytes = new TextEncoder().encode(password);
  const buf   = await crypto.subtle.digest('SHA-256', bytes);
  return Array.from(new Uint8Array(buf))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

const normalizeEmail = (e) => (e || '').trim().toLowerCase();

// ── Provider ─────────────────────────────────────────────────────────
export function AuthProvider({ children }) {
  const [user,  setUser]  = useState(null);
  const [ready, setReady] = useState(false);

  // Rehydrate session on first mount.
  useEffect(() => {
    setUser(loadSession());
    setReady(true);
  }, []);

  const signUp = async ({ name, email, password }) => {
    const cleanEmail = normalizeEmail(email);
    if (!name?.trim())                throw new Error('NAME_REQUIRED');
    if (!cleanEmail.includes('@'))    throw new Error('INVALID_EMAIL');
    if (!password || password.length < 6) throw new Error('PASSWORD_TOO_SHORT');

    const users = loadUsers();
    if (users[cleanEmail]) throw new Error('EMAIL_TAKEN');

    const hash = await hashPassword(password);
    users[cleanEmail] = {
      name:       name.trim(),
      email:      cleanEmail,
      passHash:   hash,
      createdAt:  new Date().toISOString(),
    };
    saveUsers(users);

    const session = { name: name.trim(), email: cleanEmail };
    saveSession(session);
    setUser(session);
    return session;
  };

  const signIn = async ({ email, password }) => {
    const cleanEmail = normalizeEmail(email);
    const users = loadUsers();
    const record = users[cleanEmail];
    if (!record) throw new Error('NO_ACCOUNT');

    const hash = await hashPassword(password || '');
    if (hash !== record.passHash) throw new Error('WRONG_PASSWORD');

    const session = { name: record.name, email: record.email };
    saveSession(session);
    setUser(session);
    return session;
  };

  const signOut = () => {
    saveSession(null);
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

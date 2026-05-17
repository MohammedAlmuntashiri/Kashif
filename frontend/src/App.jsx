// Top-level component.
// Sets up LanguageProvider, AuthProvider, BrowserRouter, the persistent
// Navbar, and routes.

import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

import { LanguageProvider } from './i18n/LanguageContext.jsx';
import { AuthProvider } from './auth/AuthContext.jsx';
import Navbar from './components/common/Navbar.jsx';
import Footer from './components/common/Footer.jsx';
import HomePage from './pages/HomePage.jsx';
import StockDetailPage from './pages/StockDetailPage.jsx';
import SectorPage from './pages/SectorPage.jsx';
import ComparePage from './pages/ComparePage.jsx';
import SignInPage from './pages/SignInPage.jsx';
import SignUpPage from './pages/SignUpPage.jsx';
import AboutPage from './pages/AboutPage.jsx';

export default function App() {
  return (
    // Providers wrap everything so every component can use useLang()/useAuth().
    <LanguageProvider>
      <AuthProvider>
        <BrowserRouter>
          {/* min-h-screen + flex so the footer stays at the bottom on short pages. */}
          <div className="min-h-screen flex flex-col">
            <Navbar />
            <main className="flex-1">
              <Routes>
                <Route path="/"               element={<HomePage />} />
                <Route path="/stock/:ticker"  element={<StockDetailPage />} />
                <Route path="/sector/:name"   element={<SectorPage />} />
                <Route path="/compare"        element={<ComparePage />} />
                <Route path="/signin"         element={<SignInPage />} />
                <Route path="/signup"         element={<SignUpPage />} />
                <Route path="/about"          element={<AboutPage />} />
                <Route path="*"               element={<HomePage />} />
              </Routes>
            </main>
            <Footer />
          </div>
        </BrowserRouter>
      </AuthProvider>
    </LanguageProvider>
  );
}

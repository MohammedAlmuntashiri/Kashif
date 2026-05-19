// Top-level component.
// Sets up LanguageProvider, AuthProvider, BrowserRouter, the persistent
// Navbar, page transitions, the global toast surface, and routes.

import React from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { Toaster } from 'sonner';

import { LanguageProvider } from './i18n/LanguageContext.jsx';
import { AuthProvider } from './auth/AuthContext.jsx';
import Navbar from './components/common/Navbar.jsx';
import Footer from './components/common/Footer.jsx';
import PageTransition from './components/common/PageTransition.jsx';
import HomePage from './pages/HomePage.jsx';
import StockDetailPage from './pages/StockDetailPage.jsx';
import SectorPage from './pages/SectorPage.jsx';
import ComparePage from './pages/ComparePage.jsx';
import SignInPage from './pages/SignInPage.jsx';
import SignUpPage from './pages/SignUpPage.jsx';
import AboutPage from './pages/AboutPage.jsx';
import WatchlistPage from './pages/WatchlistPage.jsx';

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
              <AnimatedRoutes />
            </main>
            <Footer />
          </div>
          <Toaster
            position="top-center"
            richColors
            theme="system"
            toastOptions={{
              className: 'font-sans',
            }}
          />
        </BrowserRouter>
      </AuthProvider>
    </LanguageProvider>
  );
}

// Splits out so we can key <Routes> on pathname for AnimatePresence exits.
function AnimatedRoutes() {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/"               element={<PageTransition><HomePage /></PageTransition>} />
        <Route path="/stock/:ticker"  element={<PageTransition><StockDetailPage /></PageTransition>} />
        <Route path="/sector/:name"   element={<PageTransition><SectorPage /></PageTransition>} />
        <Route path="/compare"        element={<PageTransition><ComparePage /></PageTransition>} />
        <Route path="/watchlist"      element={<PageTransition><WatchlistPage /></PageTransition>} />
        <Route path="/signin"         element={<PageTransition><SignInPage /></PageTransition>} />
        <Route path="/signup"         element={<PageTransition><SignUpPage /></PageTransition>} />
        <Route path="/about"          element={<PageTransition><AboutPage /></PageTransition>} />
        <Route path="*"               element={<PageTransition><HomePage /></PageTransition>} />
      </Routes>
    </AnimatePresence>
  );
}

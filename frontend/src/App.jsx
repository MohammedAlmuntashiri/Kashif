// Top-level component.
// Sets up LanguageProvider, BrowserRouter, the persistent Navbar, and routes.

import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

import { LanguageProvider } from './i18n/LanguageContext.jsx';
import Navbar from './components/common/Navbar.jsx';
import HomePage from './pages/HomePage.jsx';
import StockDetailPage from './pages/StockDetailPage.jsx';
import SectorPage from './pages/SectorPage.jsx';
import ComparePage from './pages/ComparePage.jsx';

export default function App() {
  return (
    // LanguageProvider wraps everything so every component can use useLang().
    <LanguageProvider>
      <BrowserRouter>
        <Navbar />
        <main>
          <Routes>
            <Route path="/"               element={<HomePage />} />
            <Route path="/stock/:ticker"  element={<StockDetailPage />} />
            <Route path="/sector/:name"   element={<SectorPage />} />
            <Route path="/compare"        element={<ComparePage />} />
            <Route path="*"               element={<HomePage />} />
          </Routes>
        </main>
      </BrowserRouter>
    </LanguageProvider>
  );
}

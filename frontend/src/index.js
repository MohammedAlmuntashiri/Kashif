// React entry point — mounts the <App /> root into #root.
//
// We use React 18's createRoot API (the post-legacy mode that enables
// concurrent features). StrictMode is on so dev-mode double-renders
// surface side-effect bugs early; it has no effect on production builds.

import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';                      // Tailwind directives live here
import App from './App.jsx';

// Grab the <div id="root"></div> from public/index.html and create a root.
const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

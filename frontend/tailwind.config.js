/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx}"],

  // 'class' mode: dark styles apply when a `dark` class is present on
  // any ancestor of the element. We toggle it on <html> from the
  // ThemeToggle component (and from an inline script in index.html
  // that runs before React, to avoid flash-of-light-mode on reload).
  darkMode: 'class',

  theme: {
    extend: {
      // Two font stacks — `font-sans` is the default body face, `font-display`
      // is for page titles, hero headlines, brand mark, and ticker symbols.
      fontFamily: {
        sans:    ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        display: ['"Space Grotesk"', 'Inter', 'system-ui', 'sans-serif'],
      },

      // Brand color tokens — emerald primary, mapped so we can reference
      // `bg-brand-600` etc. across the app and re-theme in one place.
      colors: {
        brand: {
          50:  '#ecfdf5',
          100: '#d1fae5',
          200: '#a7f3d0',
          300: '#6ee7b7',
          400: '#34d399',
          500: '#10b981',
          600: '#059669',   // primary action
          700: '#047857',
          800: '#065f46',
          900: '#064e3b',
          950: '#022c22',
        },
      },

      // Subtle shadow used on interactive cards in dark mode (emerald glow).
      boxShadow: {
        'brand-glow':      '0 0 0 1px rgba(16, 185, 129, 0.25), 0 8px 24px -8px rgba(16, 185, 129, 0.35)',
      },
    },
  },

  plugins: [],
};

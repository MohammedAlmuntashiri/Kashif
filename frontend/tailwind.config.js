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
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
    },
  },

  plugins: [],
};

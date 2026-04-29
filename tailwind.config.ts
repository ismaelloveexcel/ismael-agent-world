import type { Config } from 'tailwindcss';

// Tailwind v4 moves theme tokens to CSS @theme in globals.css.
// This file is kept for tooling compatibility and plugin registration.
const config: Config = {
  darkMode: 'class',
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './lib/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        teal: {
          DEFAULT: '#0abf9f',
          50:  '#edfaf7',
          100: '#d2f4ec',
          200: '#a8e9d9',
          300: '#6fd9c4',
          400: '#35c4aa',
          500: '#0abf9f',
          600: '#019980',
          700: '#027a67',
          800: '#046152',
          900: '#054f44',
        },
        blue: {
          DEFAULT: '#3b82f6',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
        },
        slate: {
          900: '#0f172a',
          950: '#020817',
        },
      },
      fontFamily: {
        sans: ['var(--font-geist-sans)', 'system-ui', 'sans-serif'],
        mono: ['var(--font-geist-mono)', 'monospace'],
      },
      borderRadius: {
        DEFAULT: '0.5rem',
        sm: '0.375rem',
        md: '0.5rem',
        lg: '0.75rem',
        xl: '1rem',
      },
      animation: {
        'pulse-teal': 'pulse-teal 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow':       'glow 3s ease-in-out infinite alternate',
      },
      keyframes: {
        'pulse-teal': {
          '0%, 100%': { opacity: '1' },
          '50%':      { opacity: '0.4' },
        },
        'glow': {
          from: { boxShadow: '0 0 8px #0abf9f40' },
          to:   { boxShadow: '0 0 24px #0abf9f90' },
        },
      },
    },
  },
  plugins: [],
};

export default config;

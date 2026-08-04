/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        // Role-based tokens backed by CSS variables (see :root / [data-theme="light"]
        // in index.css) so the same class names adapt to both themes automatically.
        ink: 'rgb(var(--c-ink) / <alpha-value>)',
        surface: 'rgb(var(--c-surface) / <alpha-value>)',
        surfaceRaised: 'rgb(var(--c-surface-raised) / <alpha-value>)',
        bone: 'rgb(var(--c-text) / <alpha-value>)',
        muted: 'rgb(var(--c-muted) / <alpha-value>)',
        line: 'rgb(var(--c-line) / <alpha-value>)',
        veil: 'rgb(var(--c-veil) / <alpha-value>)',
        // Semantic + category accents stay fixed across themes — they're already
        // saturated enough to read clearly on both a dark and a light surface.
        verified: '#22C55E',
        warn: '#F59E0B',
        danger: '#F43F5E',
        catDp: '#7C9EFF',
        catBacktrack: '#FB7185',
        catGreedy: '#2DD4BF',
        catDc: '#C084FC',
        catTwoPointers: '#22D3EE',
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', 'monospace'],
        sans: ['Poppins', 'sans-serif'],
        display: ['Poppins', 'sans-serif'],
      },
      borderRadius: {
        '4xl': '1.75rem',
        '5xl': '2.25rem',
      },
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'slide-up': {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-in-right': {
          '0%': { transform: 'translateX(100%)' },
          '100%': { transform: 'translateX(0)' },
        },
        'scale-in': {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        'pop-in': {
          '0%': { opacity: '0', transform: 'scale(0.9) translateY(6px)' },
          '60%': { opacity: '1', transform: 'scale(1.015) translateY(0)' },
          '100%': { opacity: '1', transform: 'scale(1) translateY(0)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        'glow-pulse': {
          '0%, 100%': { opacity: '0.4' },
          '50%': { opacity: '1' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-6px)' },
        },
        'bar-fill': {
          '0%': { width: '0%' },
        },
        'counter-up': {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'theme-fade': {
          '0%': { opacity: '0.6' },
          '100%': { opacity: '1' },
        },
      },
      transitionTimingFunction: {
        spring: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
        smooth: 'cubic-bezier(0.16, 1, 0.3, 1)',
      },
      animation: {
        'fade-in': 'fade-in 0.5s cubic-bezier(0.16,1,0.3,1) forwards',
        'slide-up': 'slide-up 0.6s cubic-bezier(0.16,1,0.3,1) forwards',
        'slide-up-delay-1': 'slide-up 0.6s cubic-bezier(0.16,1,0.3,1) 0.1s forwards',
        'slide-up-delay-2': 'slide-up 0.6s cubic-bezier(0.16,1,0.3,1) 0.2s forwards',
        'slide-up-delay-3': 'slide-up 0.6s cubic-bezier(0.16,1,0.3,1) 0.3s forwards',
        'slide-in-right': 'slide-in-right 0.4s cubic-bezier(0.16,1,0.3,1) forwards',
        'scale-in': 'scale-in 0.35s cubic-bezier(0.16,1,0.3,1) forwards',
        'pop-in': 'pop-in 0.45s cubic-bezier(0.16,1,0.3,1) forwards',
        shimmer: 'shimmer 1.5s ease-in-out infinite',
        'glow-pulse': 'glow-pulse 2.2s ease-in-out infinite',
        float: 'float 3.4s ease-in-out infinite',
        'bar-fill': 'bar-fill 0.9s cubic-bezier(0.16,1,0.3,1) forwards',
        'counter-up': 'counter-up 0.5s cubic-bezier(0.16,1,0.3,1) forwards',
        'theme-fade': 'theme-fade 0.4s ease-out',
      },
      backdropBlur: {
        xs: '2px',
      },
      boxShadow: {
        glow: '0 0 20px rgba(124,158,255,0.2)',
        'glow-violet': '0 0 25px rgba(192,132,252,0.25)',
        'glow-emerald': '0 0 25px rgba(45,212,191,0.2)',
        glass: '0 8px 32px rgba(0,0,0,0.3)',
      },
    },
  },
  plugins: [],
}

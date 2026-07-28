/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#12141A',
        surface: '#1B1E2A',
        surfaceRaised: '#22252F',
        bone: '#E9E6DE',
        muted: '#8B8E9C',
        verified: '#4ADE80',
        warn: '#F5B942',
        danger: '#F87171',
        catDp: '#7C9EFF',
        catBacktrack: '#F0806B',
        catGreedy: '#34D399',
        catDc: '#C084FC',
        catTwoPointers: '#38BDF8',
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', 'monospace'],
        sans: ['Inter', 'sans-serif'],
        display: ['Outfit', 'Inter', 'sans-serif'],
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
      },
      animation: {
        'fade-in': 'fade-in 0.5s ease-out forwards',
        'slide-up': 'slide-up 0.5s ease-out forwards',
        'slide-up-delay-1': 'slide-up 0.5s ease-out 0.1s forwards',
        'slide-up-delay-2': 'slide-up 0.5s ease-out 0.2s forwards',
        'slide-up-delay-3': 'slide-up 0.5s ease-out 0.3s forwards',
        'slide-in-right': 'slide-in-right 0.35s cubic-bezier(0.16,1,0.3,1) forwards',
        'scale-in': 'scale-in 0.3s ease-out forwards',
        shimmer: 'shimmer 1.5s ease-in-out infinite',
        'glow-pulse': 'glow-pulse 2s ease-in-out infinite',
        float: 'float 3s ease-in-out infinite',
        'bar-fill': 'bar-fill 0.8s ease-out forwards',
        'counter-up': 'counter-up 0.4s ease-out forwards',
      },
      backdropBlur: {
        xs: '2px',
      },
      boxShadow: {
        glow: '0 0 20px rgba(124,158,255,0.15)',
        'glow-violet': '0 0 25px rgba(139,92,246,0.2)',
        'glow-emerald': '0 0 25px rgba(52,211,153,0.15)',
        glass: '0 8px 32px rgba(0,0,0,0.3)',
      },
    },
  },
  plugins: [],
}

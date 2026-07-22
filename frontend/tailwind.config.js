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
      },
    },
  },
  plugins: [],
}

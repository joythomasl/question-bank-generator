import { useTheme } from '../hooks/useTheme.js'
import { SunIcon, MoonIcon } from './icons.jsx'

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()
  const isLight = theme === 'light'

  return (
    <button
      id="theme-toggle-btn"
      onClick={toggleTheme}
      aria-label={isLight ? 'Switch to dark mode' : 'Switch to light mode'}
      title={isLight ? 'Switch to dark mode' : 'Switch to light mode'}
      className="theme-toggle-btn"
    >
      {isLight ? <MoonIcon /> : <SunIcon />}
    </button>
  )
}

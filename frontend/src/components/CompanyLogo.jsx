import { getCompanyColor, getBrandIcon } from '../utils/colors.js'

// Real brand mark when we have one bundled locally (see brandIcons.json);
// otherwise a colored monogram stand-in. No external logo fetching — that's
// either a trademark/hotlinking risk or a runtime dependency on a network
// call that shouldn't gate rendering a badge.
export default function CompanyLogo({ name, color, size = 18 }) {
  const icon = getBrandIcon(name)
  const bg = color || getCompanyColor(name)

  if (icon) {
    return (
      <span
        className="inline-flex items-center justify-center rounded-full shrink-0"
        style={{
          width: size,
          height: size,
          background: 'rgba(255,255,255,0.94)',
          boxShadow: `0 0 0 1px rgb(var(--c-veil) / 0.12), 0 2px 6px -1px ${icon.hex}66`,
        }}
        aria-hidden="true"
      >
        <svg viewBox="0 0 24 24" width={Math.round(size * 0.62)} height={Math.round(size * 0.62)}>
          <path d={icon.path} fill={icon.hex} />
        </svg>
      </span>
    )
  }

  const letter = (name || '?').trim().charAt(0).toUpperCase()
  return (
    <span
      className="inline-flex items-center justify-center rounded-full font-bold shrink-0 leading-none"
      style={{
        width: size,
        height: size,
        fontSize: Math.round(size * 0.52),
        backgroundColor: bg,
        color: '#fff',
        textShadow: '0 1px 1px rgba(0,0,0,0.25)',
        boxShadow: `0 0 0 1px rgb(var(--c-veil) / 0.1), 0 2px 6px -1px ${bg}66`,
      }}
      aria-hidden="true"
    >
      {letter}
    </span>
  )
}

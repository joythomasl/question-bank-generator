const FILL = { Easy: 0.34, Medium: 0.67, Hard: 1 }
const COLOR = { Easy: '#22C55E', Medium: '#F59E0B', Hard: '#F43F5E' }

// A small radial "charge level" gauge standing in for the flat difficulty
// text badge — reads at a glance and fits the technical-readout aesthetic.
export default function DifficultyGauge({ difficulty, size = 28 }) {
  const r = (size - 5) / 2
  const circumference = 2 * Math.PI * r
  const pct = FILL[difficulty] ?? 0.5
  const color = COLOR[difficulty] ?? '#8B8E9C'
  const offset = circumference * (1 - pct)

  return (
    <span className="relative inline-flex items-center justify-center shrink-0" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="-rotate-90 absolute inset-0">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="rgb(var(--c-veil))" strokeOpacity="0.12" strokeWidth="2.5" />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 0.7s cubic-bezier(0.16,1,0.3,1)', filter: `drop-shadow(0 0 3px ${color}99)` }}
        />
      </svg>
      <span className="data-readout text-[9px] font-bold" style={{ color }}>
        {(difficulty || '?').charAt(0)}
      </span>
    </span>
  )
}

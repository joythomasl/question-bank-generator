// Small L-shaped bracket accents for the two corners a .hud-tile's clip-path
// doesn't cut — reinforces the "scanner/viewfinder" read on every tile.
export default function HudCorners({ color }) {
  return (
    <>
      <span className="hud-bracket hud-bracket-tl" style={color ? { '--bracket-color': color } : undefined} />
      <span className="hud-bracket hud-bracket-br" style={color ? { '--bracket-color': color } : undefined} />
    </>
  )
}

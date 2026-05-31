import { useState, useEffect, useRef } from "react";
import countries from "./countries_seed.json";

const graph = Object.fromEntries(countries.map(c => [c.id, c.borders]));
const nameById = Object.fromEntries(countries.map(c => [c.id, c.name]));
const flagById = Object.fromEntries(countries.map(c => [c.id, c.flag]));
const idByName = Object.fromEntries(countries.map(c => [c.name.toLowerCase(), c.id]));
const countryNames = countries.map(c => c.name).sort();

function bfs(startId, endId) {
  if (startId === endId) return [startId];
  const queue = [[startId]];
  const visited = new Set([startId]);
  while (queue.length) {
    const path = queue.shift();
    const current = path.at(-1);
    for (const neighbor of graph[current] ?? []) {
      if (!visited.has(neighbor)) {
        if (neighbor === endId) return [...path, neighbor];
        visited.add(neighbor);
        queue.push([...path, neighbor]);
      }
    }
  }
  return null;
}

const EXAMPLES = [
  ["Portugal", "China"],
  ["India", "France"],
  ["Brazil", "Argentina"],
  ["Norway", "Iran"],
];

export default function App() {
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [userPath, setUserPath] = useState([]);
  const [guess, setGuess] = useState("");
  const [mode, setMode] = useState("auto");
  const [won, setWon] = useState(false);
  const [animating, setAnimating] = useState(false);
  const [revealedSteps, setRevealedSteps] = useState(0);
  const [shake, setShake] = useState(false);
  const [timer, setTimer] = useState(0);
  const [timerActive, setTimerActive] = useState(false);
  const timerRef = useRef(null);
  const guessRef = useRef(null);

  useEffect(() => {
    if (timerActive) {
      timerRef.current = setInterval(() => setTimer(t => t + 1), 1000);
    } else {
      clearInterval(timerRef.current);
    }
    return () => clearInterval(timerRef.current);
  }, [timerActive]);

  function getIds() {
    const sId = idByName[start.trim().toLowerCase()];
    const eId = idByName[end.trim().toLowerCase()];
    return { sId, eId };
  }

  function handleSolve() {
    setError(""); setResult(null); setUserPath([]); setWon(false); setRevealedSteps(0);
    const { sId, eId } = getIds();
    if (!sId) return triggerError(`Can't find "${start}"`);
    if (!eId) return triggerError(`Can't find "${end}"`);
    const path = bfs(sId, eId);
    if (!path) return triggerError("No land path exists between these countries.");
    setResult(path);
    setAnimating(true);
    let i = 0;
    const reveal = setInterval(() => {
      i++;
      setRevealedSteps(i);
      if (i >= path.length) { clearInterval(reveal); setAnimating(false); }
    }, 300);
  }

  function handleStartManual() {
    setError(""); setResult(null); setWon(false); setTimer(0);
    const { sId, eId } = getIds();
    if (!sId) return triggerError(`Can't find "${start}"`);
    if (!eId) return triggerError(`Can't find "${end}"`);
    setUserPath([sId]);
    setTimerActive(true);
    setTimeout(() => guessRef.current?.focus(), 100);
  }

  function handleGuess() {
    const gId = idByName[guess.trim().toLowerCase()];
    if (!gId) return triggerError(`Can't find "${guess}"`);
    setError("");
    const current = userPath.at(-1);
    if (!graph[current]?.includes(gId)) {
      triggerError(`${nameById[gId]} doesn't border ${nameById[current]}`);
      setShake(true);
      setTimeout(() => setShake(false), 500);
      return;
    }
    const newPath = [...userPath, gId];
    setUserPath(newPath);
    setGuess("");
    guessRef.current?.focus();
    const { eId } = getIds();
    if (gId === eId) {
      const optimal = bfs(idByName[start.trim().toLowerCase()], eId);
      setTimerActive(false);
      setWon(true);
      setResult({ userPath: newPath, optimal });
    }
  }

  function triggerError(msg) {
    setError(msg);
    setTimeout(() => setError(""), 3000);
  }

  function loadExample(s, e) {
    setStart(s); setEnd(e);
    setResult(null); setUserPath([]); setWon(false); setError("");
  }

  function reset() {
    setResult(null); setUserPath([]); setWon(false);
    setStart(""); setEnd(""); setError(""); setTimer(0); setTimerActive(false);
  }

  const isManualActive = mode === "manual" && userPath.length > 0 && !won;
  const formatTime = s => `${String(Math.floor(s/60)).padStart(2,"0")}:${String(s%60).padStart(2,"0")}`;

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        :root {
          --bg: #080c14;
          --surface: #0d1524;
          --surface2: #111d30;
          --border: rgba(255,255,255,0.07);
          --border-bright: rgba(99,179,237,0.3);
          --text: #e8f0fe;
          --text-muted: #5a7499;
          --text-dim: #3d5473;
          --accent: #3b9eff;
          --accent-glow: rgba(59,158,255,0.15);
          --accent2: #00d4aa;
          --accent2-glow: rgba(0,212,170,0.15);
          --danger: #ff6b6b;
          --gold: #f5c842;
          --gold-glow: rgba(245,200,66,0.15);
        }

        body {
          background: var(--bg);
          min-height: 100vh;
          font-family: 'DM Sans', sans-serif;
          color: var(--text);
          overflow-x: hidden;
        }

        /* Starfield */
        body::before {
          content: '';
          position: fixed;
          inset: 0;
          background-image:
            radial-gradient(1px 1px at 10% 20%, rgba(255,255,255,0.4) 0%, transparent 100%),
            radial-gradient(1px 1px at 30% 60%, rgba(255,255,255,0.3) 0%, transparent 100%),
            radial-gradient(1px 1px at 50% 10%, rgba(255,255,255,0.5) 0%, transparent 100%),
            radial-gradient(1px 1px at 70% 80%, rgba(255,255,255,0.3) 0%, transparent 100%),
            radial-gradient(1px 1px at 85% 35%, rgba(255,255,255,0.4) 0%, transparent 100%),
            radial-gradient(1px 1px at 20% 90%, rgba(255,255,255,0.2) 0%, transparent 100%),
            radial-gradient(1px 1px at 60% 50%, rgba(255,255,255,0.3) 0%, transparent 100%),
            radial-gradient(1px 1px at 90% 70%, rgba(255,255,255,0.4) 0%, transparent 100%),
            radial-gradient(1px 1px at 45% 75%, rgba(255,255,255,0.2) 0%, transparent 100%),
            radial-gradient(1px 1px at 75% 15%, rgba(255,255,255,0.3) 0%, transparent 100%);
          pointer-events: none;
          z-index: 0;
        }

        .app {
          position: relative;
          z-index: 1;
          min-height: 100vh;
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 48px 24px 80px;
        }

        /* Header */
        .header {
          text-align: center;
          margin-bottom: 48px;
          animation: fadeDown 0.6s ease both;
        }

        .logo-row {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 14px;
          margin-bottom: 10px;
        }

        .logo-icon {
          width: 48px; height: 48px;
          background: linear-gradient(135deg, var(--accent), var(--accent2));
          border-radius: 14px;
          display: flex; align-items: center; justify-content: center;
          font-size: 24px;
          box-shadow: 0 0 24px var(--accent-glow);
        }

        h1 {
          font-family: 'Syne', sans-serif;
          font-size: 2.6rem;
          font-weight: 800;
          letter-spacing: -0.02em;
          background: linear-gradient(135deg, #e8f0fe 0%, var(--accent) 60%, var(--accent2) 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .subtitle {
          color: var(--text-muted);
          font-size: 0.95rem;
          font-weight: 300;
          letter-spacing: 0.02em;
        }

        /* Card */
        .card {
          width: 100%;
          max-width: 660px;
          background: var(--surface);
          border: 1px solid var(--border);
          border-radius: 20px;
          padding: 32px;
          box-shadow: 0 32px 64px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.05);
          animation: fadeUp 0.6s ease 0.1s both;
        }

        /* Mode toggle */
        .mode-toggle {
          display: flex;
          background: var(--bg);
          border: 1px solid var(--border);
          border-radius: 12px;
          padding: 4px;
          margin-bottom: 28px;
          gap: 4px;
        }

        .mode-btn {
          flex: 1;
          padding: 10px;
          border: none;
          border-radius: 9px;
          font-family: 'DM Sans', sans-serif;
          font-size: 0.9rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s ease;
          background: transparent;
          color: var(--text-muted);
        }

        .mode-btn.active {
          background: var(--surface2);
          color: var(--text);
          box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }

        /* Inputs section */
        .inputs-grid {
          display: grid;
          grid-template-columns: 1fr 40px 1fr;
          align-items: end;
          gap: 8px;
          margin-bottom: 20px;
        }

        .input-group { display: flex; flex-direction: column; gap: 8px; }

        .input-label {
          font-size: 0.75rem;
          font-weight: 500;
          letter-spacing: 0.08em;
          text-transform: uppercase;
          color: var(--text-dim);
        }

        .country-input {
          background: var(--bg);
          border: 1px solid var(--border);
          border-radius: 10px;
          color: var(--text);
          padding: 12px 16px;
          font-family: 'DM Sans', sans-serif;
          font-size: 1rem;
          font-weight: 500;
          outline: none;
          width: 100%;
          transition: border-color 0.2s, box-shadow 0.2s;
        }

        .country-input:focus {
          border-color: var(--accent);
          box-shadow: 0 0 0 3px var(--accent-glow);
        }

        .arrow-divider {
          display: flex;
          align-items: center;
          justify-content: center;
          padding-bottom: 2px;
          color: var(--text-dim);
          font-size: 1.2rem;
        }

        /* Examples */
        .examples {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
          margin-bottom: 20px;
        }

        .example-label {
          font-size: 0.72rem;
          color: var(--text-dim);
          letter-spacing: 0.06em;
          text-transform: uppercase;
          width: 100%;
          margin-bottom: 2px;
        }

        .example-chip {
          background: var(--bg);
          border: 1px solid var(--border);
          border-radius: 20px;
          padding: 5px 12px;
          font-size: 0.8rem;
          color: var(--text-muted);
          cursor: pointer;
          transition: all 0.15s ease;
          font-family: 'DM Sans', sans-serif;
        }

        .example-chip:hover {
          border-color: var(--accent);
          color: var(--accent);
          background: var(--accent-glow);
        }

        /* Action button */
        .action-btn {
          width: 100%;
          padding: 14px;
          border: none;
          border-radius: 12px;
          font-family: 'Syne', sans-serif;
          font-size: 1rem;
          font-weight: 700;
          letter-spacing: 0.04em;
          cursor: pointer;
          transition: all 0.2s ease;
          position: relative;
          overflow: hidden;
        }

        .action-btn.primary {
          background: linear-gradient(135deg, var(--accent), #1a6fd4);
          color: white;
          box-shadow: 0 4px 20px rgba(59,158,255,0.3);
        }

        .action-btn.primary:hover {
          transform: translateY(-1px);
          box-shadow: 0 8px 28px rgba(59,158,255,0.4);
        }

        .action-btn.primary:active { transform: translateY(0); }

        /* Error */
        .error-msg {
          margin-top: 14px;
          padding: 10px 16px;
          background: rgba(255,107,107,0.1);
          border: 1px solid rgba(255,107,107,0.25);
          border-radius: 8px;
          color: var(--danger);
          font-size: 0.875rem;
          animation: fadeIn 0.2s ease;
        }

        /* Result box */
        .result-box {
          margin-top: 24px;
          background: var(--bg);
          border: 1px solid var(--border);
          border-radius: 14px;
          padding: 24px;
          animation: fadeUp 0.3s ease both;
        }

        .result-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 20px;
        }

        .result-title {
          font-family: 'Syne', sans-serif;
          font-size: 0.8rem;
          font-weight: 600;
          letter-spacing: 0.1em;
          text-transform: uppercase;
          color: var(--text-dim);
        }

        .hop-badge {
          background: var(--accent-glow);
          border: 1px solid var(--border-bright);
          color: var(--accent);
          padding: 4px 12px;
          border-radius: 20px;
          font-size: 0.8rem;
          font-weight: 500;
        }

        /* Path display */
        .path-row {
          display: flex;
          flex-wrap: wrap;
          align-items: center;
          gap: 8px;
        }

        .path-step {
          display: flex;
          align-items: center;
          gap: 8px;
          animation: popIn 0.3s ease both;
        }

        .country-chip {
          display: flex;
          align-items: center;
          gap: 6px;
          background: var(--surface2);
          border: 1px solid var(--border);
          border-radius: 24px;
          padding: 7px 14px;
          font-size: 0.875rem;
          font-weight: 500;
          color: var(--text);
          transition: all 0.2s;
        }

        .country-chip.start {
          border-color: var(--accent);
          color: var(--accent);
          background: var(--accent-glow);
        }

        .country-chip.end {
          border-color: var(--accent2);
          color: var(--accent2);
          background: var(--accent2-glow);
        }

        .country-chip.won {
          border-color: #22c55e;
          color: #22c55e;
          background: rgba(34,197,94,0.1);
        }

        .country-chip.unknown {
          border-color: var(--border-bright);
          color: var(--accent);
          background: var(--accent-glow);
          animation: pulse 1.5s ease infinite;
        }

        .chip-flag { font-size: 1.1rem; }

        .path-arrow {
          color: var(--text-dim);
          font-size: 0.9rem;
        }

        /* Borders hint */
        .borders-hint {
          margin-top: 18px;
          padding: 14px 16px;
          background: var(--surface2);
          border-radius: 10px;
          border: 1px solid var(--border);
        }

        .borders-hint-label {
          font-size: 0.72rem;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          color: var(--text-dim);
          margin-bottom: 8px;
        }

        .borders-list {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
        }

        .border-tag {
          background: var(--bg);
          border: 1px solid var(--border);
          border-radius: 16px;
          padding: 4px 10px;
          font-size: 0.8rem;
          color: var(--text-muted);
          cursor: pointer;
          transition: all 0.15s;
        }

        .border-tag:hover {
          border-color: var(--accent);
          color: var(--accent);
        }

        /* Guess input row */
        .guess-row {
          display: flex;
          gap: 10px;
          margin-top: 16px;
        }

        .guess-input {
          flex: 1;
          background: var(--bg);
          border: 1px solid var(--border);
          border-radius: 10px;
          color: var(--text);
          padding: 12px 16px;
          font-family: 'DM Sans', sans-serif;
          font-size: 0.95rem;
          font-weight: 500;
          outline: none;
          transition: border-color 0.2s, box-shadow 0.2s;
        }

        .guess-input:focus {
          border-color: var(--accent2);
          box-shadow: 0 0 0 3px var(--accent2-glow);
        }

        .guess-input.shake {
          animation: shake 0.4s ease;
        }

        .go-btn {
          background: linear-gradient(135deg, var(--accent2), #00a882);
          border: none;
          border-radius: 10px;
          color: white;
          padding: 12px 22px;
          font-family: 'Syne', sans-serif;
          font-weight: 700;
          font-size: 0.9rem;
          cursor: pointer;
          transition: all 0.2s;
          box-shadow: 0 4px 14px rgba(0,212,170,0.25);
        }

        .go-btn:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(0,212,170,0.35); }

        /* Timer */
        .timer {
          font-family: 'Syne', sans-serif;
          font-size: 0.85rem;
          color: var(--text-dim);
          display: flex;
          align-items: center;
          gap: 6px;
        }

        .timer.active { color: var(--accent2); }

        /* Won state */
        .won-box {
          margin-top: 24px;
          background: var(--bg);
          border: 1px solid rgba(34,197,94,0.25);
          border-radius: 14px;
          padding: 28px;
          animation: fadeUp 0.4s ease both;
          text-align: center;
        }

        .won-emoji { font-size: 2.5rem; margin-bottom: 8px; }

        .won-title {
          font-family: 'Syne', sans-serif;
          font-size: 1.4rem;
          font-weight: 800;
          color: #22c55e;
          margin-bottom: 4px;
        }

        .won-stats {
          display: flex;
          justify-content: center;
          gap: 24px;
          margin: 20px 0;
        }

        .stat {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 4px;
        }

        .stat-value {
          font-family: 'Syne', sans-serif;
          font-size: 1.8rem;
          font-weight: 800;
          color: var(--text);
        }

        .stat-label {
          font-size: 0.72rem;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          color: var(--text-dim);
        }

        .optimal-badge {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          background: var(--gold-glow);
          border: 1px solid rgba(245,200,66,0.3);
          color: var(--gold);
          padding: 6px 14px;
          border-radius: 20px;
          font-size: 0.82rem;
          font-weight: 500;
          margin-bottom: 20px;
        }

        .play-again-btn {
          background: var(--surface2);
          border: 1px solid var(--border);
          border-radius: 10px;
          color: var(--text-muted);
          padding: 11px 28px;
          font-family: 'Syne', sans-serif;
          font-weight: 600;
          font-size: 0.9rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .play-again-btn:hover {
          border-color: var(--accent);
          color: var(--accent);
        }

        /* Animations */
        @keyframes fadeDown {
          from { opacity: 0; transform: translateY(-16px); }
          to   { opacity: 1; transform: translateY(0); }
        }

        @keyframes fadeUp {
          from { opacity: 0; transform: translateY(16px); }
          to   { opacity: 1; transform: translateY(0); }
        }

        @keyframes fadeIn {
          from { opacity: 0; } to { opacity: 1; }
        }

        @keyframes popIn {
          0%   { opacity: 0; transform: scale(0.7); }
          70%  { transform: scale(1.08); }
          100% { opacity: 1; transform: scale(1); }
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50%       { opacity: 0.5; }
        }

        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          20%       { transform: translateX(-8px); }
          40%       { transform: translateX(8px); }
          60%       { transform: translateX(-5px); }
          80%       { transform: translateX(5px); }
        }
      `}</style>

      <div className="app">

        {/* Header */}
        <div className="header">
          <div className="logo-row">
            <div className="logo-icon">🌍</div>
            <h1>Border Bridge</h1>
          </div>
          <p className="subtitle">Navigate the world through land borders</p>
        </div>

        <div className="card">

          {/* Mode toggle */}
          <div className="mode-toggle">
            <button
              className={`mode-btn ${mode === "auto" ? "active" : ""}`}
              onClick={() => { setMode("auto"); reset(); }}
            >⚡ Auto Solve</button>
            <button
              className={`mode-btn ${mode === "manual" ? "active" : ""}`}
              onClick={() => { setMode("manual"); reset(); }}
            >🧩 Play Yourself</button>
          </div>

          {/* Inputs */}
          <div className="inputs-grid">
            <div className="input-group">
              <label className="input-label">Start</label>
              <input
                className="country-input"
                list="country-list"
                value={start}
                onChange={e => setStart(e.target.value)}
                placeholder="e.g. Portugal"
              />
            </div>
            <div className="arrow-divider">→</div>
            <div className="input-group">
              <label className="input-label">End</label>
              <input
                className="country-input"
                list="country-list"
                value={end}
                onChange={e => setEnd(e.target.value)}
                placeholder="e.g. China"
              />
            </div>
          </div>

          <datalist id="country-list">
            {countryNames.map(n => <option key={n} value={n} />)}
          </datalist>

          {/* Examples */}
          <div className="examples">
            <span className="example-label">Try</span>
            {EXAMPLES.map(([s, e]) => (
              <button key={s+e} className="example-chip" onClick={() => loadExample(s, e)}>
                {s} → {e}
              </button>
            ))}
          </div>

          {/* Action button */}
          {mode === "auto" && (
            <button className="action-btn primary" onClick={handleSolve}>
              Find Shortest Path
            </button>
          )}
          {mode === "manual" && !isManualActive && !won && (
            <button className="action-btn primary" onClick={handleStartManual}>
              Start Puzzle
            </button>
          )}

          {/* Error */}
          {error && <div className="error-msg">⚠ {error}</div>}

          {/* Auto result */}
          {mode === "auto" && result && (
            <div className="result-box">
              <div className="result-header">
                <span className="result-title">Shortest Path</span>
                <span className="hop-badge">{result.length - 1} {result.length - 1 === 1 ? "hop" : "hops"}</span>
              </div>
              <div className="path-row">
                {result.slice(0, revealedSteps).map((id, i) => (
                  <div key={id} className="path-step">
                    <div className={`country-chip ${i === 0 ? "start" : i === result.length - 1 ? "end" : ""}`}>
                      <span className="chip-flag">{flagById[id]}</span>
                      {nameById[id]}
                    </div>
                    {i < result.length - 1 && <span className="path-arrow">→</span>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Manual — active guessing */}
          {isManualActive && (
            <div className="result-box">
              <div className="result-header">
                <span className="result-title">Your Path</span>
                <span className={`timer ${timerActive ? "active" : ""}`}>
                  ⏱ {formatTime(timer)}
                </span>
              </div>
              <div className="path-row">
                {userPath.map((id, i) => (
                  <div key={id} className="path-step">
                    <div className={`country-chip ${i === 0 ? "start" : ""}`}>
                      <span className="chip-flag">{flagById[id]}</span>
                      {nameById[id]}
                    </div>
                    <span className="path-arrow">→</span>
                  </div>
                ))}
                <div className="country-chip unknown">?</div>
              </div>

              {/* Borders hint */}
              <div className="borders-hint">
                <div className="borders-hint-label">
                  Borders of {nameById[userPath.at(-1)]}
                </div>
                <div className="borders-list">
                  {(graph[userPath.at(-1)] ?? []).length === 0
                    ? <span style={{color:"var(--text-dim)",fontSize:"0.85rem"}}>Island nation — no land borders</span>
                    : (graph[userPath.at(-1)] ?? []).map(b => (
                      <span
                        key={b}
                        className="border-tag"
                        onClick={() => { setGuess(nameById[b] ?? b); guessRef.current?.focus(); }}
                      >
                        {flagById[b]} {nameById[b] ?? b}
                      </span>
                    ))
                  }
                </div>
              </div>

              {/* Guess input */}
              <div className="guess-row">
                <input
                  ref={guessRef}
                  className={`guess-input ${shake ? "shake" : ""}`}
                  list="country-list"
                  value={guess}
                  onChange={e => setGuess(e.target.value)}
                  onKeyDown={e => e.key === "Enter" && handleGuess()}
                  placeholder="Type next country or click a border above..."
                />
                <button className="go-btn" onClick={handleGuess}>Go →</button>
              </div>
            </div>
          )}

          {/* Won */}
          {won && result && (
            <div className="won-box">
              <div className="won-emoji">🎉</div>
              <div className="won-title">You made it!</div>

              <div className="won-stats">
                <div className="stat">
                  <span className="stat-value">{result.userPath.length - 1}</span>
                  <span className="stat-label">Your hops</span>
                </div>
                <div className="stat">
                  <span className="stat-value">{result.optimal.length - 1}</span>
                  <span className="stat-label">Optimal</span>
                </div>
                <div className="stat">
                  <span className="stat-value">{formatTime(timer)}</span>
                  <span className="stat-label">Time</span>
                </div>
              </div>

              {result.userPath.length === result.optimal.length
                ? <div className="optimal-badge">✨ Perfect — optimal path!</div>
                : <p style={{color:"var(--text-muted)",fontSize:"0.85rem",marginBottom:"16px"}}>
                    Optimal: {result.optimal.map(id => nameById[id]).join(" → ")}
                  </p>
              }

              <div className="path-row" style={{justifyContent:"center",marginBottom:"20px"}}>
                {result.userPath.map((id, i) => (
                  <div key={id} className="path-step">
                    <div className="country-chip won">
                      <span className="chip-flag">{flagById[id]}</span>
                      {nameById[id]}
                    </div>
                    {i < result.userPath.length - 1 && <span className="path-arrow">→</span>}
                  </div>
                ))}
              </div>

              <button className="play-again-btn" onClick={reset}>Play Again</button>
            </div>
          )}

        </div>
      </div>
    </>
  );
}

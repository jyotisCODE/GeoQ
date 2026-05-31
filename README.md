# Border-Bridge
A World-Geo-Based Game

# Country Data Layer

Foundation dataset for the geo-intelligence platform.
Used by Border Bridge, Flight Focus Mode, and eventually every game mode.

---

## Files

| File | Purpose |
|---|---|
| `build_seed_data.py` | Generates `data/countries_seed.json` — 62 key countries, works offline immediately |
| `build_country_data.py` | Fetches full ~250-country dataset from REST Countries API |
| `data/countries_seed.json` | **Start here.** Auto-generated. Use for Border Bridge development. |
| `data/countries.json` | Full dataset. Generated after running `build_country_data.py`. |
| `data/countries_min.json` | Minified full dataset for production. |

---

## Quick Start

```bash
# Step 1 — seed data (offline, instant)
python3 build_seed_data.py

# Step 2 — full dataset (needs internet)
python3 build_country_data.py
```

---

## Schema

Each country entry looks like this:

```json
{
  "id": "IND",
  "name": "India",
  "officialName": "Republic of India",
  "capital": "New Delhi",
  "coordinates": { "lat": 20.5937, "lng": 78.9629 },
  "capitalCoordinates": { "lat": 28.6139, "lng": 77.209 },
  "borders": ["BGD", "BTN", "CHN", "MMR", "NPL", "PAK"],
  "continent": "Asia",
  "region": "Asia",
  "subregion": "Southern Asia",
  "flag": "🇮🇳",
  "flagUrl": "https://flagcdn.com/in.svg",
  "timezones": ["UTC+05:30"],
  "timezone": "UTC+05:30",
  "utcOffset": "+05:30",
  "area": 3287590,
  "population": 1428627663,
  "gdpUsd": null,
  "internetPenetration": null,
  "flightHoursFrom": {
    "USA": 16.5,
    "GBR": 10.2,
    "DEU": 9.8,
    "CHN": 7.1,
    "AUS": 12.4
  }
}
```

---

## How each game mode uses this

### Border Bridge
Uses `borders[]` as the adjacency graph.
BFS traversal finds shortest land path between any two countries.

```js
import countries from './data/countries_seed.json';

function shortestPath(startId, endId) {
  const graph = Object.fromEntries(countries.map(c => [c.id, c.borders]));
  const queue = [[startId]];
  const visited = new Set([startId]);

  while (queue.length) {
    const path = queue.shift();
    const current = path.at(-1);
    if (current === endId) return path;
    for (const neighbor of graph[current] ?? []) {
      if (!visited.has(neighbor)) {
        visited.add(neighbor);
        queue.push([...path, neighbor]);
      }
    }
  }
  return null; // island or no path
}

shortestPath('PRT', 'CHN')
// → ['PRT', 'ESP', 'FRA', 'DEU', 'POL', 'RUS', 'CHN']  (6 hops)
```

### Flight Focus Mode
Uses `flightHoursFrom` for session duration.
Uses `coordinates` to animate the flight arc.
Uses `timezone` / `utcOffset` to show local time at destination.

```js
const india = countries.find(c => c.id === 'IND');
const sessionMinutes = india.flightHoursFrom['GBR'] * 60; // → 612 mins
```

### Pinpoint (location guessing)
Uses `coordinates` as the answer position.
Haversine distance between guess and answer → score.

### Distance Duel
Uses `capitalCoordinates` for precise city-to-city distances.

### Capital Rush (bonus)
Uses `capital` field. Match country → capital.

### Flag Blitz (bonus)
Uses `flag` (emoji) and `flagUrl` (SVG).

### Timezone Explorer (bonus)
Uses `timezone` and `utcOffset` to show current local time.

### Geo Heatmaps (bonus)
Uses `population`, `gdpUsd`, `internetPenetration`.
Note: `gdpUsd` and `internetPenetration` are null in seed — fill from
World Bank CSV or similar when building that mode.

---

## Extending GDP / Internet data

The REST Countries API doesn't include GDP or internet penetration.
When you need those fields, download from:
- World Bank Open Data: https://data.worldbank.org
- Match on ISO 3166-1 alpha-3 code (same as our `id` field)

```python
# Rough merge example
import json, csv

with open('data/countries.json') as f:
    countries = {c['id']: c for c in json.load(f)}

with open('world_bank_gdp.csv') as f:
    for row in csv.DictReader(f):
        cid = row['Country Code']
        if cid in countries:
            countries[cid]['gdpUsd'] = float(row['2023'] or 0)
```

---

## Notes

- Island nations (Japan, Australia, UK, etc.) have `borders: []` — BFS returns null for cross-ocean paths. This is correct behaviour for Border Bridge.
- `flightHoursFrom` uses great-circle distance ÷ 900 km/h + 1h overhead. It's an estimate, not a real flight schedule.
- All country IDs use ISO 3166-1 alpha-3 (3-letter codes). This is the standard — use it everywhere in your codebase.

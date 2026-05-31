"""
build_country_data.py
---------------------
Fetches all country data from REST Countries API and reshapes it
into the geo-intelligence platform's country data schema.

Run once:  python3 build_country_data.py
Output:    data/countries.json   (full dataset, ~250 countries)
           data/countries_min.json (minified, for production)

Schema per country:
  id, name, capital, coordinates, capitalCoordinates,
  borders, continent, region, flag, flagUrl,
  timezone, utcOffset, area, population,
  gdpUsd (null — not in free API, fill later),
  flightHoursFrom (computed via Haversine from coordinates)
"""

import json
import math
import urllib.request
import urllib.error
import os
import sys

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

API_URL = (
    "https://restcountries.com/v3.1/all"
    "?fields=name,cca3,capital,latlng,capitalInfo,"
    "borders,continents,region,subregion,flag,flags,timezones,area,population"
)

OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "countries.json")
OUTPUT_MIN  = os.path.join(OUTPUT_DIR, "countries_min.json")

# Aviation average cruising speed km/h (used for flight time estimates)
AVG_FLIGHT_SPEED_KMH = 900

# Countries to pre-compute flight hours between (hub cities)
# Extend this list as needed
FLIGHT_HUB_IDS = [
    "USA", "GBR", "DEU", "FRA", "JPN", "CHN", "IND",
    "BRA", "AUS", "ZAF", "ARE", "SGP", "RUS", "CAN", "MEX"
]

# ---------------------------------------------------------------------------
# Haversine distance
# ---------------------------------------------------------------------------

def haversine_km(lat1, lng1, lat2, lng2):
    """Great-circle distance between two lat/lng points in kilometres."""
    R = 6371  # Earth radius km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    return 2 * R * math.asin(math.sqrt(a))


def flight_hours(lat1, lng1, lat2, lng2):
    """Estimated flight duration in hours (great-circle, no wind/routing)."""
    dist = haversine_km(lat1, lng1, lat2, lng2)
    raw = dist / AVG_FLIGHT_SPEED_KMH
    # Add ~1h overhead for taxi/climb/descent on any flight
    return round(raw + 1.0, 1)


# ---------------------------------------------------------------------------
# UTC offset parsing
# ---------------------------------------------------------------------------

def parse_utc_offset(timezone_str):
    """
    Extract a clean UTC offset string from IANA-style timezone entries.
    e.g. "UTC+05:30" -> "+05:30"
         "UTC"       -> "+00:00"
         "UTC-03:00" -> "-03:00"
    Returns None if unparseable.
    """
    if not timezone_str:
        return None
    tz = timezone_str.strip()
    if tz == "UTC":
        return "+00:00"
    if tz.startswith("UTC+"):
        offset = tz[4:]
        if ":" not in offset:
            offset = offset + ":00"
        return "+" + offset
    if tz.startswith("UTC-"):
        offset = tz[4:]
        if ":" not in offset:
            offset = offset + ":00"
        return "-" + offset
    return None


# ---------------------------------------------------------------------------
# Reshape raw API entry → our schema
# ---------------------------------------------------------------------------

def reshape(raw):
    """Convert one REST Countries v3 entry into our schema."""

    cca3 = raw.get("cca3", "")

    # Coordinates (centroid of country)
    latlng = raw.get("latlng", [])
    lat = latlng[0] if len(latlng) >= 1 else None
    lng = latlng[1] if len(latlng) >= 2 else None

    # Capital coordinates
    cap_info = raw.get("capitalInfo", {})
    cap_latlng = cap_info.get("latlng", [])
    cap_lat = cap_latlng[0] if len(cap_latlng) >= 1 else lat
    cap_lng = cap_latlng[1] if len(cap_latlng) >= 2 else lng

    # Capital name
    capitals = raw.get("capital", [])
    capital = capitals[0] if capitals else None

    # Timezones — store all, expose first offset
    timezones = raw.get("timezones", [])
    primary_tz = timezones[0] if timezones else None
    utc_offset = parse_utc_offset(primary_tz)

    # Flag
    flag_emoji = raw.get("flag", "")
    flags_obj  = raw.get("flags", {})
    flag_url   = flags_obj.get("svg") or flags_obj.get("png") or ""

    # Continent
    continents = raw.get("continents", [])
    continent  = continents[0] if continents else None

    return {
        "id":       cca3,
        "name":     raw.get("name", {}).get("common", ""),
        "officialName": raw.get("name", {}).get("official", ""),
        "capital":  capital,
        "coordinates": {
            "lat": lat,
            "lng": lng
        } if lat is not None else None,
        "capitalCoordinates": {
            "lat": cap_lat,
            "lng": cap_lng
        } if cap_lat is not None else None,
        "borders":    raw.get("borders", []),
        "continent":  continent,
        "region":     raw.get("region", ""),
        "subregion":  raw.get("subregion", ""),
        "flag":       flag_emoji,
        "flagUrl":    flag_url,
        "timezones":  timezones,
        "timezone":   primary_tz,
        "utcOffset":  utc_offset,
        "area":       raw.get("area"),
        "population": raw.get("population"),
        # Not in free API — fill from World Bank CSV or similar later
        "gdpUsd":     None,
        "internetPenetration": None,
        # Populated in second pass below
        "flightHoursFrom": {}
    }


# ---------------------------------------------------------------------------
# Second pass: compute flight hours between hub countries
# ---------------------------------------------------------------------------

def add_flight_hours(countries):
    """
    For each country, compute flight hours TO every hub country.
    Stored as flightHoursFrom: { "USA": 14.2, "GBR": 9.1, ... }
    Only hubs that have valid coordinates are included.
    """
    # Build id → entry map
    by_id = {c["id"]: c for c in countries}

    # Build list of valid hub entries
    hubs = []
    for hub_id in FLIGHT_HUB_IDS:
        hub = by_id.get(hub_id)
        if hub and hub["coordinates"]:
            hubs.append(hub)

    for country in countries:
        coords = country.get("coordinates")
        if not coords:
            continue
        flight_map = {}
        for hub in hubs:
            if hub["id"] == country["id"]:
                flight_map[hub["id"]] = 0.0
                continue
            h_coords = hub["coordinates"]
            hours = flight_hours(
                coords["lat"], coords["lng"],
                h_coords["lat"], h_coords["lng"]
            )
            flight_map[hub["id"]] = hours
        country["flightHoursFrom"] = flight_map

    return countries


# ---------------------------------------------------------------------------
# Validation helpers (printed as a report)
# ---------------------------------------------------------------------------

def validate(countries):
    by_id = {c["id"]: c for c in countries}

    missing_coords   = [c["id"] for c in countries if not c["coordinates"]]
    missing_capital  = [c["id"] for c in countries if not c["capital"]]
    dangling_borders = []

    for c in countries:
        for b in c["borders"]:
            if b not in by_id:
                dangling_borders.append((c["id"], b))

    island_nations = [c["id"] for c in countries if not c["borders"]]

    print("\n=== Validation Report ===")
    print(f"  Total countries       : {len(countries)}")
    print(f"  Missing coordinates   : {len(missing_coords)}  {missing_coords[:5]}")
    print(f"  Missing capital name  : {len(missing_capital)} {missing_capital[:5]}")
    print(f"  Dangling border refs  : {len(dangling_borders)}")
    print(f"  Island nations (0 borders): {len(island_nations)}")
    print("=========================\n")


# ---------------------------------------------------------------------------
# BFS shortest path — test with India → Portugal
# ---------------------------------------------------------------------------

def bfs_shortest_path(start_id, end_id, countries):
    by_id = {c["id"]: c for c in countries}
    graph = {c["id"]: c["borders"] for c in countries}

    queue   = [[start_id]]
    visited = {start_id}

    while queue:
        path    = queue.pop(0)
        current = path[-1]

        if current == end_id:
            return path

        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])

    return None  # Islands or disconnected


def test_bfs(countries):
    tests = [
        ("PRT", "CHN"),
        ("IND", "FRA"),
        ("USA", "BRA"),   # Should return None (no land border)
        ("DEU", "POL"),
    ]
    by_id = {c["id"]: c["name"] for c in countries}
    print("=== BFS Shortest Path Tests ===")
    for start, end in tests:
        path = bfs_shortest_path(start, end, countries)
        if path:
            named = " → ".join(by_id.get(p, p) for p in path)
            print(f"  {start} → {end}: {named}  ({len(path)-1} hops)")
        else:
            print(f"  {start} → {end}: No land path (expected for islands/oceans)")
    print("================================\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Fetching country data from REST Countries API...")

    try:
        req = urllib.request.Request(
            API_URL,
            headers={"User-Agent": "geo-intelligence-platform/1.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw_data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        print(f"  Network error: {e}")
        print("  Make sure you have internet access and restcountries.com is reachable.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"  Failed to parse API response: {e}")
        sys.exit(1)

    print(f"  Received {len(raw_data)} entries from API.")

    # Reshape all entries
    print("Reshaping into platform schema...")
    countries = [reshape(entry) for entry in raw_data]

    # Sort alphabetically by name for readability
    countries.sort(key=lambda c: c["name"])

    # Second pass: flight hours
    print("Computing flight hours between hub countries...")
    countries = add_flight_hours(countries)

    # Validate
    validate(countries)

    # BFS smoke test
    test_bfs(countries)

    # Write outputs
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(countries, f, indent=2, ensure_ascii=False)
    print(f"Written: {OUTPUT_FILE}  ({os.path.getsize(OUTPUT_FILE) // 1024} KB)")

    with open(OUTPUT_MIN, "w", encoding="utf-8") as f:
        json.dump(countries, f, separators=(",", ":"), ensure_ascii=False)
    print(f"Written: {OUTPUT_MIN}  ({os.path.getsize(OUTPUT_MIN) // 1024} KB)")

    print("\nDone. Your country data layer is ready.")
    print("Next step: import countries.json into your Border Bridge project.")


if __name__ == "__main__":
    main()

"""
build_seed_data.py
------------------
Generates data/countries_seed.json — a handcrafted dataset of ~60
geopolitically important countries covering all continents.

This lets you run Border Bridge immediately without any API call.
The full build_country_data.py script enriches this later.

Run:  python3 build_seed_data.py
"""

import json
import math
import os

AVG_FLIGHT_SPEED_KMH = 900

SEED = [
    # Europe
    {"id":"PRT","name":"Portugal","capital":"Lisbon","coordinates":{"lat":39.3999,"lng":-8.2245},"capitalCoordinates":{"lat":38.7169,"lng":-9.1395},"borders":["ESP"],"continent":"Europe","region":"Europe","subregion":"Southern Europe","flag":"🇵🇹","timezone":"UTC","utcOffset":"+00:00"},
    {"id":"ESP","name":"Spain","capital":"Madrid","coordinates":{"lat":40.4637,"lng":-3.7492},"capitalCoordinates":{"lat":40.4168,"lng":-3.7038},"borders":["AND","FRA","GIB","MAR","PRT"],"continent":"Europe","region":"Europe","subregion":"Southern Europe","flag":"🇪🇸","timezone":"UTC+01:00","utcOffset":"+01:00"},
    {"id":"FRA","name":"France","capital":"Paris","coordinates":{"lat":46.2276,"lng":2.2137},"capitalCoordinates":{"lat":48.8566,"lng":2.3522},"borders":["AND","BEL","DEU","ITA","LUX","MCO","ESP","CHE"],"continent":"Europe","region":"Europe","subregion":"Western Europe","flag":"🇫🇷","timezone":"UTC+01:00","utcOffset":"+01:00"},
    {"id":"DEU","name":"Germany","capital":"Berlin","coordinates":{"lat":51.1657,"lng":10.4515},"capitalCoordinates":{"lat":52.5200,"lng":13.4050},"borders":["AUT","BEL","CZE","DNK","FRA","LUX","NLD","POL","CHE"],"continent":"Europe","region":"Europe","subregion":"Western Europe","flag":"🇩🇪","timezone":"UTC+01:00","utcOffset":"+01:00"},
    {"id":"POL","name":"Poland","capital":"Warsaw","coordinates":{"lat":51.9194,"lng":19.1451},"capitalCoordinates":{"lat":52.2297,"lng":21.0122},"borders":["BLR","CZE","DEU","LTU","RUS","SVK","UKR"],"continent":"Europe","region":"Europe","subregion":"Central Europe","flag":"🇵🇱","timezone":"UTC+01:00","utcOffset":"+01:00"},
    {"id":"UKR","name":"Ukraine","capital":"Kyiv","coordinates":{"lat":48.3794,"lng":31.1656},"capitalCoordinates":{"lat":50.4501,"lng":30.5234},"borders":["BLR","HUN","MDA","POL","ROU","RUS","SVK"],"continent":"Europe","region":"Europe","subregion":"Eastern Europe","flag":"🇺🇦","timezone":"UTC+02:00","utcOffset":"+02:00"},
    {"id":"RUS","name":"Russia","capital":"Moscow","coordinates":{"lat":61.5240,"lng":105.3188},"capitalCoordinates":{"lat":55.7558,"lng":37.6173},"borders":["AZE","BLR","CHN","EST","FIN","GEO","KAZ","PRK","LVA","LTU","MNG","NOR","POL","UKR"],"continent":"Europe","region":"Europe","subregion":"Eastern Europe","flag":"🇷🇺","timezone":"UTC+03:00","utcOffset":"+03:00"},
    {"id":"ITA","name":"Italy","capital":"Rome","coordinates":{"lat":41.8719,"lng":12.5674},"capitalCoordinates":{"lat":41.9028,"lng":12.4964},"borders":["AUT","FRA","SMR","SVN","CHE","VAT"],"continent":"Europe","region":"Europe","subregion":"Southern Europe","flag":"🇮🇹","timezone":"UTC+01:00","utcOffset":"+01:00"},
    {"id":"GBR","name":"United Kingdom","capital":"London","coordinates":{"lat":55.3781,"lng":-3.4360},"capitalCoordinates":{"lat":51.5074,"lng":-0.1278},"borders":["IRL"],"continent":"Europe","region":"Europe","subregion":"Northern Europe","flag":"🇬🇧","timezone":"UTC","utcOffset":"+00:00"},
    {"id":"NOR","name":"Norway","capital":"Oslo","coordinates":{"lat":60.4720,"lng":8.4689},"capitalCoordinates":{"lat":59.9139,"lng":10.7522},"borders":["FIN","SWE","RUS"],"continent":"Europe","region":"Europe","subregion":"Northern Europe","flag":"🇳🇴","timezone":"UTC+01:00","utcOffset":"+01:00"},
    {"id":"SWE","name":"Sweden","capital":"Stockholm","coordinates":{"lat":60.1282,"lng":18.6435},"capitalCoordinates":{"lat":59.3293,"lng":18.0686},"borders":["FIN","NOR"],"continent":"Europe","region":"Europe","subregion":"Northern Europe","flag":"🇸🇪","timezone":"UTC+01:00","utcOffset":"+01:00"},
    {"id":"FIN","name":"Finland","capital":"Helsinki","coordinates":{"lat":61.9241,"lng":25.7482},"capitalCoordinates":{"lat":60.1699,"lng":24.9384},"borders":["NOR","RUS","SWE"],"continent":"Europe","region":"Europe","subregion":"Northern Europe","flag":"🇫🇮","timezone":"UTC+02:00","utcOffset":"+02:00"},
    {"id":"TUR","name":"Turkey","capital":"Ankara","coordinates":{"lat":38.9637,"lng":35.2433},"capitalCoordinates":{"lat":39.9334,"lng":32.8597},"borders":["ARM","AZE","BGR","GEO","GRC","IRN","IRQ","SYR"],"continent":"Asia","region":"Asia","subregion":"Western Asia","flag":"🇹🇷","timezone":"UTC+03:00","utcOffset":"+03:00"},

    # Asia
    {"id":"CHN","name":"China","capital":"Beijing","coordinates":{"lat":35.8617,"lng":104.1954},"capitalCoordinates":{"lat":39.9042,"lng":116.4074},"borders":["AFG","BTN","IND","KAZ","PRK","KGZ","LAO","MNG","MMR","NEP","PAK","RUS","TJK","VNM"],"continent":"Asia","region":"Asia","subregion":"Eastern Asia","flag":"🇨🇳","timezone":"UTC+08:00","utcOffset":"+08:00"},
    {"id":"IND","name":"India","capital":"New Delhi","coordinates":{"lat":20.5937,"lng":78.9629},"capitalCoordinates":{"lat":28.6139,"lng":77.2090},"borders":["BGD","BTN","CHN","MMR","NPL","PAK"],"continent":"Asia","region":"Asia","subregion":"Southern Asia","flag":"🇮🇳","timezone":"UTC+05:30","utcOffset":"+05:30"},
    {"id":"JPN","name":"Japan","capital":"Tokyo","coordinates":{"lat":36.2048,"lng":138.2529},"capitalCoordinates":{"lat":35.6762,"lng":139.6503},"borders":[],"continent":"Asia","region":"Asia","subregion":"Eastern Asia","flag":"🇯🇵","timezone":"UTC+09:00","utcOffset":"+09:00"},
    {"id":"KOR","name":"South Korea","capital":"Seoul","coordinates":{"lat":35.9078,"lng":127.7669},"capitalCoordinates":{"lat":37.5665,"lng":126.9780},"borders":["PRK"],"continent":"Asia","region":"Asia","subregion":"Eastern Asia","flag":"🇰🇷","timezone":"UTC+09:00","utcOffset":"+09:00"},
    {"id":"IRN","name":"Iran","capital":"Tehran","coordinates":{"lat":32.4279,"lng":53.6880},"capitalCoordinates":{"lat":35.6892,"lng":51.3890},"borders":["AFG","ARM","AZE","IRQ","PAK","TUR","TKM"],"continent":"Asia","region":"Asia","subregion":"Southern Asia","flag":"🇮🇷","timezone":"UTC+03:30","utcOffset":"+03:30"},
    {"id":"IRQ","name":"Iraq","capital":"Baghdad","coordinates":{"lat":33.2232,"lng":43.6793},"capitalCoordinates":{"lat":33.3152,"lng":44.3661},"borders":["IRN","JOR","KWT","SAU","SYR","TUR"],"continent":"Asia","region":"Asia","subregion":"Western Asia","flag":"🇮🇶","timezone":"UTC+03:00","utcOffset":"+03:00"},
    {"id":"SAU","name":"Saudi Arabia","capital":"Riyadh","coordinates":{"lat":23.8859,"lng":45.0792},"capitalCoordinates":{"lat":24.6877,"lng":46.7219},"borders":["IRQ","JOR","KWT","OMN","QAT","UAE","YEM"],"continent":"Asia","region":"Asia","subregion":"Western Asia","flag":"🇸🇦","timezone":"UTC+03:00","utcOffset":"+03:00"},
    {"id":"ARE","name":"United Arab Emirates","capital":"Abu Dhabi","coordinates":{"lat":23.4241,"lng":53.8478},"capitalCoordinates":{"lat":24.4539,"lng":54.3773},"borders":["OMN","SAU"],"continent":"Asia","region":"Asia","subregion":"Western Asia","flag":"🇦🇪","timezone":"UTC+04:00","utcOffset":"+04:00"},
    {"id":"PAK","name":"Pakistan","capital":"Islamabad","coordinates":{"lat":30.3753,"lng":69.3451},"capitalCoordinates":{"lat":33.6844,"lng":73.0479},"borders":["AFG","CHN","IND","IRN"],"continent":"Asia","region":"Asia","subregion":"Southern Asia","flag":"🇵🇰","timezone":"UTC+05:00","utcOffset":"+05:00"},
    {"id":"AFG","name":"Afghanistan","capital":"Kabul","coordinates":{"lat":33.9391,"lng":67.7100},"capitalCoordinates":{"lat":34.5553,"lng":69.2075},"borders":["CHN","IRN","PAK","TJK","TKM","UZB"],"continent":"Asia","region":"Asia","subregion":"Southern Asia","flag":"🇦🇫","timezone":"UTC+04:30","utcOffset":"+04:30"},
    {"id":"KAZ","name":"Kazakhstan","capital":"Astana","coordinates":{"lat":48.0196,"lng":66.9237},"capitalCoordinates":{"lat":51.1801,"lng":71.4460},"borders":["CHN","KGZ","RUS","TKM","UZB"],"continent":"Asia","region":"Asia","subregion":"Central Asia","flag":"🇰🇿","timezone":"UTC+06:00","utcOffset":"+06:00"},
    {"id":"MNG","name":"Mongolia","capital":"Ulaanbaatar","coordinates":{"lat":46.8625,"lng":103.8467},"capitalCoordinates":{"lat":47.8864,"lng":106.9057},"borders":["CHN","RUS"],"continent":"Asia","region":"Asia","subregion":"Eastern Asia","flag":"🇲🇳","timezone":"UTC+08:00","utcOffset":"+08:00"},
    {"id":"SGP","name":"Singapore","capital":"Singapore","coordinates":{"lat":1.3521,"lng":103.8198},"capitalCoordinates":{"lat":1.3521,"lng":103.8198},"borders":[],"continent":"Asia","region":"Asia","subregion":"South-Eastern Asia","flag":"🇸🇬","timezone":"UTC+08:00","utcOffset":"+08:00"},
    {"id":"THA","name":"Thailand","capital":"Bangkok","coordinates":{"lat":15.8700,"lng":100.9925},"capitalCoordinates":{"lat":13.7563,"lng":100.5018},"borders":["KHM","LAO","MYS","MMR"],"continent":"Asia","region":"Asia","subregion":"South-Eastern Asia","flag":"🇹🇭","timezone":"UTC+07:00","utcOffset":"+07:00"},
    {"id":"VNM","name":"Vietnam","capital":"Hanoi","coordinates":{"lat":14.0583,"lng":108.2772},"capitalCoordinates":{"lat":21.0285,"lng":105.8542},"borders":["KHM","CHN","LAO"],"continent":"Asia","region":"Asia","subregion":"South-Eastern Asia","flag":"🇻🇳","timezone":"UTC+07:00","utcOffset":"+07:00"},
    {"id":"MMR","name":"Myanmar","capital":"Naypyidaw","coordinates":{"lat":21.9162,"lng":95.9560},"capitalCoordinates":{"lat":19.7633,"lng":96.0785},"borders":["BGD","CHN","IND","LAO","THA"],"continent":"Asia","region":"Asia","subregion":"South-Eastern Asia","flag":"🇲🇲","timezone":"UTC+06:30","utcOffset":"+06:30"},

    # Africa
    {"id":"ZAF","name":"South Africa","capital":"Pretoria","coordinates":{"lat":-30.5595,"lng":22.9375},"capitalCoordinates":{"lat":-25.7479,"lng":28.2293},"borders":["BWA","LSO","MOZ","NAM","SWZ","ZWE"],"continent":"Africa","region":"Africa","subregion":"Southern Africa","flag":"🇿🇦","timezone":"UTC+02:00","utcOffset":"+02:00"},
    {"id":"EGY","name":"Egypt","capital":"Cairo","coordinates":{"lat":26.8206,"lng":30.8025},"capitalCoordinates":{"lat":30.0444,"lng":31.2357},"borders":["ISR","LBY","SDN"],"continent":"Africa","region":"Africa","subregion":"Northern Africa","flag":"🇪🇬","timezone":"UTC+02:00","utcOffset":"+02:00"},
    {"id":"NGA","name":"Nigeria","capital":"Abuja","coordinates":{"lat":9.0820,"lng":8.6753},"capitalCoordinates":{"lat":9.0765,"lng":7.3986},"borders":["BEN","CMR","TCD","NER"],"continent":"Africa","region":"Africa","subregion":"Western Africa","flag":"🇳🇬","timezone":"UTC+01:00","utcOffset":"+01:00"},
    {"id":"ETH","name":"Ethiopia","capital":"Addis Ababa","coordinates":{"lat":9.1450,"lng":40.4897},"capitalCoordinates":{"lat":9.0320,"lng":38.7469},"borders":["DJI","ERI","KEN","SOM","SSD","SDN"],"continent":"Africa","region":"Africa","subregion":"Eastern Africa","flag":"🇪🇹","timezone":"UTC+03:00","utcOffset":"+03:00"},
    {"id":"KEN","name":"Kenya","capital":"Nairobi","coordinates":{"lat":-0.0236,"lng":37.9062},"capitalCoordinates":{"lat":-1.2921,"lng":36.8219},"borders":["ETH","SOM","SSD","TZA","UGA"],"continent":"Africa","region":"Africa","subregion":"Eastern Africa","flag":"🇰🇪","timezone":"UTC+03:00","utcOffset":"+03:00"},
    {"id":"TZA","name":"Tanzania","capital":"Dodoma","coordinates":{"lat":-6.3690,"lng":34.8888},"capitalCoordinates":{"lat":-6.1630,"lng":35.7516},"borders":["BDI","COD","KEN","MWI","MOZ","RWA","UGA","ZMB"],"continent":"Africa","region":"Africa","subregion":"Eastern Africa","flag":"🇹🇿","timezone":"UTC+03:00","utcOffset":"+03:00"},
    {"id":"DZA","name":"Algeria","capital":"Algiers","coordinates":{"lat":28.0339,"lng":1.6596},"capitalCoordinates":{"lat":36.7372,"lng":3.0865},"borders":["LBY","MLI","MRT","MAR","NER","TUN","ESH"],"continent":"Africa","region":"Africa","subregion":"Northern Africa","flag":"🇩🇿","timezone":"UTC+01:00","utcOffset":"+01:00"},
    {"id":"MAR","name":"Morocco","capital":"Rabat","coordinates":{"lat":31.7917,"lng":-7.0926},"capitalCoordinates":{"lat":33.9716,"lng":-6.8498},"borders":["DZA","ESP","MRT","ESH"],"continent":"Africa","region":"Africa","subregion":"Northern Africa","flag":"🇲🇦","timezone":"UTC+01:00","utcOffset":"+01:00"},

    # Americas
    {"id":"USA","name":"United States","capital":"Washington, D.C.","coordinates":{"lat":37.0902,"lng":-95.7129},"capitalCoordinates":{"lat":38.9072,"lng":-77.0369},"borders":["CAN","MEX"],"continent":"North America","region":"Americas","subregion":"Northern America","flag":"🇺🇸","timezone":"UTC-05:00","utcOffset":"-05:00"},
    {"id":"CAN","name":"Canada","capital":"Ottawa","coordinates":{"lat":56.1304,"lng":-106.3468},"capitalCoordinates":{"lat":45.4215,"lng":-75.6972},"borders":["USA"],"continent":"North America","region":"Americas","subregion":"Northern America","flag":"🇨🇦","timezone":"UTC-05:00","utcOffset":"-05:00"},
    {"id":"MEX","name":"Mexico","capital":"Mexico City","coordinates":{"lat":23.6345,"lng":-102.5528},"capitalCoordinates":{"lat":19.4326,"lng":-99.1332},"borders":["BLZ","GTM","USA"],"continent":"North America","region":"Americas","subregion":"Central America","flag":"🇲🇽","timezone":"UTC-06:00","utcOffset":"-06:00"},
    {"id":"BRA","name":"Brazil","capital":"Brasília","coordinates":{"lat":-14.2350,"lng":-51.9253},"capitalCoordinates":{"lat":-15.7797,"lng":-47.9297},"borders":["ARG","BOL","COL","GUF","GUY","PRY","PER","SUR","URY","VEN"],"continent":"South America","region":"Americas","subregion":"South America","flag":"🇧🇷","timezone":"UTC-03:00","utcOffset":"-03:00"},
    {"id":"ARG","name":"Argentina","capital":"Buenos Aires","coordinates":{"lat":-38.4161,"lng":-63.6167},"capitalCoordinates":{"lat":-34.6037,"lng":-58.3816},"borders":["BOL","BRA","CHL","PRY","URY"],"continent":"South America","region":"Americas","subregion":"South America","flag":"🇦🇷","timezone":"UTC-03:00","utcOffset":"-03:00"},
    {"id":"CHL","name":"Chile","capital":"Santiago","coordinates":{"lat":-35.6751,"lng":-71.5430},"capitalCoordinates":{"lat":-33.4489,"lng":-70.6693},"borders":["ARG","BOL","PER"],"continent":"South America","region":"Americas","subregion":"South America","flag":"🇨🇱","timezone":"UTC-04:00","utcOffset":"-04:00"},
    {"id":"COL","name":"Colombia","capital":"Bogotá","coordinates":{"lat":4.5709,"lng":-74.2973},"capitalCoordinates":{"lat":4.7110,"lng":-74.0721},"borders":["BRA","ECU","PAN","PER","VEN"],"continent":"South America","region":"Americas","subregion":"South America","flag":"🇨🇴","timezone":"UTC-05:00","utcOffset":"-05:00"},
    {"id":"PER","name":"Peru","capital":"Lima","coordinates":{"lat":-9.1900,"lng":-75.0152},"capitalCoordinates":{"lat":-12.0464,"lng":-77.0428},"borders":["BOL","BRA","CHL","COL","ECU"],"continent":"South America","region":"Americas","subregion":"South America","flag":"🇵🇪","timezone":"UTC-05:00","utcOffset":"-05:00"},
    {"id":"VEN","name":"Venezuela","capital":"Caracas","coordinates":{"lat":6.4238,"lng":-66.5897},"capitalCoordinates":{"lat":10.4806,"lng":-66.9036},"borders":["BRA","COL","GUY"],"continent":"South America","region":"Americas","subregion":"South America","flag":"🇻🇪","timezone":"UTC-04:00","utcOffset":"-04:00"},

    # Oceania
    {"id":"AUS","name":"Australia","capital":"Canberra","coordinates":{"lat":-25.2744,"lng":133.7751},"capitalCoordinates":{"lat":-35.2809,"lng":149.1300},"borders":[],"continent":"Oceania","region":"Oceania","subregion":"Australia and New Zealand","flag":"🇦🇺","timezone":"UTC+10:00","utcOffset":"+10:00"},
    {"id":"NZL","name":"New Zealand","capital":"Wellington","coordinates":{"lat":-40.9006,"lng":174.8860},"capitalCoordinates":{"lat":-41.2865,"lng":174.7762},"borders":[],"continent":"Oceania","region":"Oceania","subregion":"Australia and New Zealand","flag":"🇳🇿","timezone":"UTC+12:00","utcOffset":"+12:00"},

    # Additional key connectors for BFS routing
    {"id":"BLR","name":"Belarus","capital":"Minsk","coordinates":{"lat":53.7098,"lng":27.9534},"capitalCoordinates":{"lat":53.9045,"lng":27.5615},"borders":["LVA","LTU","POL","RUS","UKR"],"continent":"Europe","region":"Europe","subregion":"Eastern Europe","flag":"🇧🇾","timezone":"UTC+03:00","utcOffset":"+03:00"},
    {"id":"GEO","name":"Georgia","capital":"Tbilisi","coordinates":{"lat":42.3154,"lng":43.3569},"capitalCoordinates":{"lat":41.6938,"lng":44.8015},"borders":["ARM","AZE","RUS","TUR"],"continent":"Asia","region":"Asia","subregion":"Western Asia","flag":"🇬🇪","timezone":"UTC+04:00","utcOffset":"+04:00"},
    {"id":"AZE","name":"Azerbaijan","capital":"Baku","coordinates":{"lat":40.1431,"lng":47.5769},"capitalCoordinates":{"lat":40.4093,"lng":49.8671},"borders":["ARM","GEO","IRN","RUS","TUR"],"continent":"Asia","region":"Asia","subregion":"Western Asia","flag":"🇦🇿","timezone":"UTC+04:00","utcOffset":"+04:00"},
    {"id":"ARM","name":"Armenia","capital":"Yerevan","coordinates":{"lat":40.0691,"lng":45.0382},"capitalCoordinates":{"lat":40.1872,"lng":44.5152},"borders":["AZE","GEO","IRN","TUR"],"continent":"Asia","region":"Asia","subregion":"Western Asia","flag":"🇦🇲","timezone":"UTC+04:00","utcOffset":"+04:00"},
    {"id":"UZB","name":"Uzbekistan","capital":"Tashkent","coordinates":{"lat":41.3775,"lng":64.5853},"capitalCoordinates":{"lat":41.2995,"lng":69.2401},"borders":["AFG","KAZ","KGZ","TJK","TKM"],"continent":"Asia","region":"Asia","subregion":"Central Asia","flag":"🇺🇿","timezone":"UTC+05:00","utcOffset":"+05:00"},
    {"id":"TKM","name":"Turkmenistan","capital":"Ashgabat","coordinates":{"lat":38.9697,"lng":59.5563},"capitalCoordinates":{"lat":37.9601,"lng":58.3261},"borders":["AFG","IRN","KAZ","UZB"],"continent":"Asia","region":"Asia","subregion":"Central Asia","flag":"🇹🇲","timezone":"UTC+05:00","utcOffset":"+05:00"},
    {"id":"TJK","name":"Tajikistan","capital":"Dushanbe","coordinates":{"lat":38.8610,"lng":71.2761},"capitalCoordinates":{"lat":38.5598,"lng":68.7870},"borders":["AFG","CHN","KGZ","UZB"],"continent":"Asia","region":"Asia","subregion":"Central Asia","flag":"🇹🇯","timezone":"UTC+05:00","utcOffset":"+05:00"},
    {"id":"KGZ","name":"Kyrgyzstan","capital":"Bishkek","coordinates":{"lat":41.2044,"lng":74.7661},"capitalCoordinates":{"lat":42.8746,"lng":74.5698},"borders":["CHN","KAZ","TJK","UZB"],"continent":"Asia","region":"Asia","subregion":"Central Asia","flag":"🇰🇬","timezone":"UTC+06:00","utcOffset":"+06:00"},
    {"id":"NPL","name":"Nepal","capital":"Kathmandu","coordinates":{"lat":28.3949,"lng":84.1240},"capitalCoordinates":{"lat":27.7172,"lng":85.3240},"borders":["CHN","IND"],"continent":"Asia","region":"Asia","subregion":"Southern Asia","flag":"🇳🇵","timezone":"UTC+05:45","utcOffset":"+05:45"},
    {"id":"BGD","name":"Bangladesh","capital":"Dhaka","coordinates":{"lat":23.6850,"lng":90.3563},"capitalCoordinates":{"lat":23.8103,"lng":90.4125},"borders":["IND","MMR"],"continent":"Asia","region":"Asia","subregion":"Southern Asia","flag":"🇧🇩","timezone":"UTC+06:00","utcOffset":"+06:00"},
    {"id":"LAO","name":"Laos","capital":"Vientiane","coordinates":{"lat":19.8563,"lng":102.4955},"capitalCoordinates":{"lat":17.9757,"lng":102.6331},"borders":["KHM","CHN","MMR","THA","VNM"],"continent":"Asia","region":"Asia","subregion":"South-Eastern Asia","flag":"🇱🇦","timezone":"UTC+07:00","utcOffset":"+07:00"},
    {"id":"KHM","name":"Cambodia","capital":"Phnom Penh","coordinates":{"lat":12.5657,"lng":104.9910},"capitalCoordinates":{"lat":11.5626,"lng":104.9160},"borders":["LAO","THA","VNM"],"continent":"Asia","region":"Asia","subregion":"South-Eastern Asia","flag":"🇰🇭","timezone":"UTC+07:00","utcOffset":"+07:00"},
    {"id":"MYS","name":"Malaysia","capital":"Kuala Lumpur","coordinates":{"lat":4.2105,"lng":101.9758},"capitalCoordinates":{"lat":3.1390,"lng":101.6869},"borders":["BRN","IDN","THA"],"continent":"Asia","region":"Asia","subregion":"South-Eastern Asia","flag":"🇲🇾","timezone":"UTC+08:00","utcOffset":"+08:00"},
    {"id":"IDN","name":"Indonesia","capital":"Jakarta","coordinates":{"lat":-0.7893,"lng":113.9213},"capitalCoordinates":{"lat":-6.2088,"lng":106.8456},"borders":["TLS","MYS","PNG"],"continent":"Asia","region":"Asia","subregion":"South-Eastern Asia","flag":"🇮🇩","timezone":"UTC+07:00","utcOffset":"+07:00"},
]


def haversine_km(lat1, lng1, lat2, lng2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.asin(math.sqrt(a))


def flight_hours(lat1, lng1, lat2, lng2):
    dist = haversine_km(lat1, lng1, lat2, lng2)
    return round(dist / AVG_FLIGHT_SPEED_KMH + 1.0, 1)


HUB_IDS = ["USA", "GBR", "DEU", "FRA", "JPN", "CHN", "IND", "BRA", "AUS", "ZAF", "ARE", "SGP", "RUS", "CAN", "MEX"]


def add_flight_hours(countries):
    by_id = {c["id"]: c for c in countries}
    hubs = [by_id[h] for h in HUB_IDS if h in by_id]

    for country in countries:
        coords = country.get("coordinates")
        if not coords:
            country["flightHoursFrom"] = {}
            continue
        fmap = {}
        for hub in hubs:
            if hub["id"] == country["id"]:
                fmap[hub["id"]] = 0.0
            else:
                h = hub["coordinates"]
                fmap[hub["id"]] = flight_hours(coords["lat"], coords["lng"], h["lat"], h["lng"])
        country["flightHoursFrom"] = fmap
        # Fields not in seed
        country.setdefault("population", None)
        country.setdefault("area", None)
        country.setdefault("gdpUsd", None)
        country.setdefault("internetPenetration", None)
        country.setdefault("flagUrl", "")
        country.setdefault("officialName", country["name"])

    return countries


def bfs_test(countries):
    by_id = {c["id"]: c["name"] for c in countries}
    graph = {c["id"]: c["borders"] for c in countries}

    def bfs(start, end):
        queue = [[start]]
        visited = {start}
        while queue:
            path = queue.pop(0)
            cur = path[-1]
            if cur == end:
                return path
            for n in graph.get(cur, []):
                if n not in visited:
                    visited.add(n)
                    queue.append(path + [n])
        return None

    tests = [("PRT","CHN"),("IND","FRA"),("BRA","ARG"),("KOR","TUR")]
    print("\n=== BFS Shortest Path (seed data) ===")
    for s, e in tests:
        path = bfs(s, e)
        if path:
            named = " → ".join(by_id.get(p, p) for p in path)
            print(f"  {s}→{e}: {named}  ({len(path)-1} hops)")
        else:
            print(f"  {s}→{e}: No land path found")
    print("======================================\n")


def main():
    countries = add_flight_hours(SEED)

    os.makedirs("data", exist_ok=True)

    with open("data/countries_seed.json", "w", encoding="utf-8") as f:
        json.dump(countries, f, indent=2, ensure_ascii=False)

    bfs_test(countries)

    print(f"Written: data/countries_seed.json  ({len(countries)} countries)")
    print("This seed covers all major BFS routing paths across continents.")
    print("Run build_country_data.py to get the full ~250-country dataset.")


if __name__ == "__main__":
    main()

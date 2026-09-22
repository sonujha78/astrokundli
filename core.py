import swisseph as swe
from datetime import datetime

swe.set_sid_mode(swe.SIDM_LAHIRI)

PLANETS = {
    'Sun': swe.SUN,
    'Moon': swe.MOON,
    'Mars': swe.MARS,
    'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER,
    'Venus': swe.VENUS,
    'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE,
}

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

def get_julian_day(year, month, day, hour, minute, tz_offset):
    ut_hour = hour + minute / 60.0 - tz_offset
    return swe.julday(year, month, day, ut_hour)

def get_planet_positions(jd):
    positions = {}
    for name, planet_id in PLANETS.items():
        lon = swe.calc_ut(jd, planet_id, swe.FLG_SIDEREAL)[0][0]
        sign_index = int(lon / 30)
        degree_in_sign = lon % 30
        positions[name] = {
            'longitude': round(lon, 4),
            'sign': ZODIAC_SIGNS[sign_index],
            'degree': round(degree_in_sign, 2)
        }
    rahu_lon = positions['Rahu']['longitude']
    ketu_lon = (rahu_lon + 180) % 360
    sign_index = int(ketu_lon / 30)
    positions['Ketu'] = {
        'longitude': round(ketu_lon, 4),
        'sign': ZODIAC_SIGNS[sign_index],
        'degree': round(ketu_lon % 30, 2)
    }
    return positions

def get_ascendant(jd, lat, lon):
    houses, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
    asc = ascmc[0]
    sign_index = int(asc / 30)
    return {
        'longitude': round(asc, 4),
        'sign': ZODIAC_SIGNS[sign_index],
        'degree': round(asc % 30, 2)
    }

if __name__ == "__main__":
    year, month, day = 1995, 8, 15
    hour, minute = 14, 30
    tz_offset = 5.5
    lat, lon = 28.6139, 77.2090

    jd = get_julian_day(year, month, day, hour, minute, tz_offset)
    planets = get_planet_positions(jd)
    ascendant = get_ascendant(jd, lat, lon)

    print("Ascendant (Lagna):", ascendant)
    print("\nPlanetary Positions:")
    for planet, data in planets.items():
        print(f"  {planet}: {data['sign']} {data['degree']}° (lon: {data['longitude']})")

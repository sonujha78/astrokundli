import swisseph as swe
from datetime import datetime, timezone
import core

# Classical Chandrabala (Moon transit house from natal Moon) effects
MOON_TRANSIT_EFFECTS = {
    1: "Today your focus turns to yourself and new beginnings. Make decisions carefully.",
    2: "Money and family matters take priority today. Watch your spending.",
    3: "A very favorable day — courage, support from siblings, and a good time to start new work.",
    4: "Your mind may feel a bit restless. Better to postpone major decisions for now.",
    5: "Creativity, studies, and matters related to children are favorable today.",
    6: "Highly favorable — victory over rivals/competition, good health and confidence.",
    7: "Relationships and partnerships take center stage — an important conversation may happen.",
    8: "A caution transit — avoid travel, big investments, or risky undertakings today.",
    9: "Fortune may fluctuate. Spiritual work and support from elders/mentors is favorable.",
    10: "Good progress and recognition likely in career or workplace matters.",
    11: "Most auspicious — gains, fulfillment of desires, and good day for new connections.",
    12: "You may feel expenses, fatigue, or loneliness. Focus on rest and introspection.",
}

SUN_TRANSIT_EFFECTS = {
    1: "This month brings focus on yourself and building your identity.",
    2: "Money and family responsibilities are an important theme this month.",
    3: "A good month for courage and new initiatives — support from siblings likely.",
    4: "Focus needed on home and peace of mind; a somewhat restless month.",
    5: "A good month for creativity, romance, and matters related to children.",
    6: "Hard work pays off — good chances of winning over competition.",
    7: "Partnerships and relationships are in the spotlight this month.",
    8: "A somewhat challenging month — pay attention to health and unexpected changes.",
    9: "Fortune favors you; a good time for dharma/spirituality and higher learning.",
    10: "An excellent month for career — strong chances of recognition and growth.",
    11: "A month of gains and network expansion — new opportunities will arrive.",
    12: "A month of expenses and rest — avoid major decisions this month.",
}

def house_from_reference(natal_sign_index, transit_sign_index):
    """1-indexed house position of transit sign counted from natal sign."""
    return ((transit_sign_index - natal_sign_index) % 12) + 1

def get_natal_moon_sign(jd, lat, lon):
    planets = core.get_planet_positions(jd)
    moon_sign = planets['Moon']['sign']
    return core.ZODIAC_SIGNS.index(moon_sign)

def get_current_jd():
    now = datetime.now(timezone.utc)
    return swe.julday(now.year, now.month, now.day, now.hour + now.minute / 60.0)

def get_daily_rashifal(natal_moon_sign_index):
    jd_now = get_current_jd()
    transit_planets = core.get_planet_positions(jd_now)
    moon_transit_index = core.ZODIAC_SIGNS.index(transit_planets['Moon']['sign'])
    house = house_from_reference(natal_moon_sign_index, moon_transit_index)
    return house, MOON_TRANSIT_EFFECTS[house]

def get_monthly_rashifal(natal_moon_sign_index):
    jd_now = get_current_jd()
    transit_planets = core.get_planet_positions(jd_now)
    sun_transit_index = core.ZODIAC_SIGNS.index(transit_planets['Sun']['sign'])
    house = house_from_reference(natal_moon_sign_index, sun_transit_index)
    return house, SUN_TRANSIT_EFFECTS[house]

if __name__ == "__main__":
    jd = core.get_julian_day(1995, 8, 15, 14, 30, 5.5)
    natal_moon_index = get_natal_moon_sign(jd, 28.6139, 77.2090)
    print("Natal Moon Sign:", core.ZODIAC_SIGNS[natal_moon_index])

    house, text = get_daily_rashifal(natal_moon_index)
    print(f"\nDaily Rashifal (Moon in house {house} from natal Moon):")
    print(text)

    house, text = get_monthly_rashifal(natal_moon_index)
    print(f"\nMonthly Rashifal (Sun in house {house} from natal Moon):")
    print(text)

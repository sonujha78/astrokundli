import core
import milan
from datetime import timedelta

DASHA_YEARS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17
}

DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]

NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
]

NAKSHATRA_SPAN = 360 / 27  # degrees per nakshatra

def get_birth_dasha_balance(moon_longitude):
    nak_index = int(moon_longitude / NAKSHATRA_SPAN) % 27
    lord = NAKSHATRA_LORDS[nak_index]
    position_in_nakshatra = moon_longitude % NAKSHATRA_SPAN
    fraction_elapsed = position_in_nakshatra / NAKSHATRA_SPAN
    total_years = DASHA_YEARS[lord]
    balance_years = total_years * (1 - fraction_elapsed)
    return lord, balance_years

def build_mahadasha_timeline(birth_date, moon_longitude, cycles=2):
    lord, balance_years = get_birth_dasha_balance(moon_longitude)
    timeline = []
    current_date = birth_date
    start_index = DASHA_ORDER.index(lord)

    # First (partial) dasha
    end_date = current_date + timedelta(days=balance_years * 365.25)
    timeline.append((lord, current_date, end_date))
    current_date = end_date

    # Subsequent full dashas
    idx = (start_index + 1) % 9
    for _ in range(9 * cycles):
        planet = DASHA_ORDER[idx]
        years = DASHA_YEARS[planet]
        end_date = current_date + timedelta(days=years * 365.25)
        timeline.append((planet, current_date, end_date))
        current_date = end_date
        idx = (idx + 1) % 9

    return timeline

def get_current_mahadasha(timeline, today):
    for planet, start, end in timeline:
        if start <= today < end:
            return planet, start, end
    return None, None, None

def get_antardasha(mahadasha_planet, maha_start, maha_end, today):
    """Sub-periods within a Mahadasha, proportional to each planet's own years."""
    maha_total_days = (maha_end - maha_start).days
    start_index = DASHA_ORDER.index(mahadasha_planet)
    current = maha_start
    for i in range(9):
        idx = (start_index + i) % 9
        planet = DASHA_ORDER[idx]
        proportion = DASHA_YEARS[planet] / 120
        sub_days = maha_total_days * proportion
        sub_end = current + timedelta(days=sub_days)
        if current <= today < sub_end:
            return planet, current, sub_end
        current = sub_end
    return None, None, None

if __name__ == "__main__":
    from datetime import datetime

    birth_date = datetime(1995, 8, 15, 14, 30)
    jd = core.get_julian_day(1995, 8, 15, 14, 30, 5.5)
    planets = core.get_planet_positions(jd)
    moon_lon = planets['Moon']['longitude']

    lord, balance = get_birth_dasha_balance(moon_lon)
    print(f"Birth Nakshatra Lord: {lord}, Balance at birth: {balance:.2f} years")

    timeline = build_mahadasha_timeline(birth_date, moon_lon)
    print("\nMahadasha Timeline:")
    for planet, start, end in timeline[:9]:
        print(f"  {planet}: {start.date()} to {end.date()}")

    today = datetime.now()
    maha_planet, maha_start, maha_end = get_current_mahadasha(timeline, today)
    print(f"\nCurrent Mahadasha ({today.date()}): {maha_planet} ({maha_start.date()} to {maha_end.date()})")

    if maha_planet:
        antar_planet, antar_start, antar_end = get_antardasha(maha_planet, maha_start, maha_end, today)
        print(f"Current Antardasha: {antar_planet} ({antar_start.date()} to {antar_end.date()})")

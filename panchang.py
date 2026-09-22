import swisseph as swe
from datetime import datetime, timezone
import core

TITHI_NAMES = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima/Amavasya"
]

YOGA_NAMES = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
    "Atiganda", "Sukarma", "Dhriti", "Shoola", "Ganda",
    "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
    "Indra", "Vaidhriti"
]

swe.set_sid_mode(swe.SIDM_LAHIRI)

def get_panchang(year, month, day, hour=12, tz_offset=5.5):
    ut_hour = hour - tz_offset
    jd = swe.julday(year, month, day, ut_hour)

    sun_lon = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)[0][0]
    moon_lon = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]

    # Tithi: angular distance Moon - Sun, each tithi = 12 degrees
    diff = (moon_lon - sun_lon) % 360
    tithi_index = int(diff / 12)
    paksha = "Shukla Paksha" if tithi_index < 15 else "Krishna Paksha"
    tithi_name = TITHI_NAMES[tithi_index % 15]

    # Nakshatra: Moon's position, each nakshatra = 13°20' = 360/27
    nak_index = int(moon_lon / (360 / 27)) % 27
    nakshatra_name = core.ZODIAC_SIGNS  # placeholder avoid unused import warning

    # Yoga: (Sun + Moon longitude) / (360/27)
    yoga_sum = (sun_lon + moon_lon) % 360
    yoga_index = int(yoga_sum / (360 / 27)) % 27
    yoga_name = YOGA_NAMES[yoga_index]

    # Vara (weekday)
    weekday = datetime(year, month, day).strftime("%A")

    return {
        'date': f"{day:02d}-{month:02d}-{year}",
        'vara': weekday,
        'tithi': f"{paksha}, {tithi_name}",
        'nakshatra_index': nak_index,
        'yoga': yoga_name,
        'sun_sign': core.ZODIAC_SIGNS[int(sun_lon / 30)],
        'moon_sign': core.ZODIAC_SIGNS[int(moon_lon / 30)],
    }

if __name__ == "__main__":
    from milan import NAKSHATRAS
    today = datetime.now()
    result = get_panchang(today.year, today.month, today.day)
    nak_name = NAKSHATRAS[result['nakshatra_index']][0]

    print(f"Panchang for {result['date']} ({result['vara']}):")
    print(f"  Tithi: {result['tithi']}")
    print(f"  Nakshatra: {nak_name}")
    print(f"  Yoga: {result['yoga']}")
    print(f"  Sun Sign: {result['sun_sign']}")
    print(f"  Moon Sign: {result['moon_sign']}")

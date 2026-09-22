import core

# Mars in these houses (from Ascendant) causes Manglik Dosha (classical rule)
MANGLIK_HOUSES_FROM_LAGNA = {1, 2, 4, 7, 8, 12}

def check_manglik(jd, lat, lon):
    planets = core.get_planet_positions(jd)
    ascendant = core.get_ascendant(jd, lat, lon)

    mars_sign = planets['Mars']['sign']
    asc_sign = ascendant['sign']

    mars_index = core.ZODIAC_SIGNS.index(mars_sign)
    asc_index = core.ZODIAC_SIGNS.index(asc_sign)

    house_from_lagna = ((mars_index - asc_index) % 12) + 1

    is_manglik = house_from_lagna in MANGLIK_HOUSES_FROM_LAGNA

    return {
        'is_manglik': is_manglik,
        'mars_house': house_from_lagna,
        'mars_sign': mars_sign,
    }

if __name__ == "__main__":
    jd = core.get_julian_day(1995, 8, 15, 14, 30, 5.5)
    result = check_manglik(jd, 28.6139, 77.2090)
    print(f"Mars is in house {result['mars_house']} ({result['mars_sign']})")
    print(f"Manglik Dosha: {'Yes' if result['is_manglik'] else 'No'}")

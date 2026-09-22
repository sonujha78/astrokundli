import core

NAVAMSA_SPAN = 30 / 9  # 3.333... degrees per pada

def get_navamsa_sign(longitude):
    sign_index = int(longitude / 30)
    degree_in_sign = longitude % 30
    pada = int(degree_in_sign / NAVAMSA_SPAN)
    navamsa_index = (sign_index * 9 + pada) % 12
    return core.ZODIAC_SIGNS[navamsa_index]

def get_navamsa_chart(jd, lat, lon):
    planets = core.get_planet_positions(jd)
    ascendant = core.get_ascendant(jd, lat, lon)

    navamsa = {}
    for planet, data in planets.items():
        navamsa[planet] = get_navamsa_sign(data['longitude'])

    navamsa_asc = get_navamsa_sign(ascendant['longitude'])

    return {
        'ascendant': navamsa_asc,
        'planets': navamsa
    }

if __name__ == "__main__":
    jd = core.get_julian_day(1995, 8, 15, 14, 30, 5.5)
    result = get_navamsa_chart(jd, 28.6139, 77.2090)

    print("Navamsa (D9) Ascendant:", result['ascendant'])
    print("\nNavamsa Planetary Positions:")
    for planet, sign in result['planets'].items():
        print(f"  {planet}: {sign}")

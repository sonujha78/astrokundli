import core
import rashifal

def check_sade_sati(natal_moon_sign_index):
    jd_now = rashifal.get_current_jd()
    transit_planets = core.get_planet_positions(jd_now)
    saturn_sign = transit_planets['Saturn']['sign']
    saturn_index = core.ZODIAC_SIGNS.index(saturn_sign)

    # House position of transit Saturn counted from natal Moon
    house = ((saturn_index - natal_moon_sign_index) % 12) + 1

    phase = None
    if house == 12:
        phase = "Rising Phase (1st phase)"
    elif house == 1:
        phase = "Peak Phase (2nd phase)"
    elif house == 2:
        phase = "Setting Phase (3rd phase)"

    is_active = phase is not None

    return {
        'is_active': is_active,
        'phase': phase,
        'saturn_sign': saturn_sign,
        'saturn_house_from_moon': house,
    }

if __name__ == "__main__":
    jd = core.get_julian_day(1995, 8, 15, 14, 30, 5.5)
    natal_moon_index = rashifal.get_natal_moon_sign(jd, 28.6139, 77.2090)
    print("Natal Moon Sign:", core.ZODIAC_SIGNS[natal_moon_index])

    result = check_sade_sati(natal_moon_index)
    print(f"Saturn currently in: {result['saturn_sign']} (house {result['saturn_house_from_moon']} from natal Moon)")
    if result['is_active']:
        print(f"Sade Sati: ACTIVE — {result['phase']}")
    else:
        print("Sade Sati: Not active")

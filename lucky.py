LUCKY_DATA = {
    "Aries": {"number": [1, 9], "color": "Red", "day": "Tuesday"},
    "Taurus": {"number": [6], "color": "White/Pink", "day": "Friday"},
    "Gemini": {"number": [5], "color": "Green", "day": "Wednesday"},
    "Cancer": {"number": [2, 7], "color": "White", "day": "Monday"},
    "Leo": {"number": [1], "color": "Gold/Orange", "day": "Sunday"},
    "Virgo": {"number": [5], "color": "Green", "day": "Wednesday"},
    "Libra": {"number": [6], "color": "White/Pastel", "day": "Friday"},
    "Scorpio": {"number": [9], "color": "Red/Maroon", "day": "Tuesday"},
    "Sagittarius": {"number": [3], "color": "Yellow", "day": "Thursday"},
    "Capricorn": {"number": [8], "color": "Black/Blue", "day": "Saturday"},
    "Aquarius": {"number": [8], "color": "Blue", "day": "Saturday"},
    "Pisces": {"number": [3], "color": "Yellow/Sea Green", "day": "Thursday"},
}

def get_lucky_info(moon_sign):
    return LUCKY_DATA.get(moon_sign, {})

if __name__ == "__main__":
    info = get_lucky_info("Pisces")
    print("Lucky Numbers:", info['number'])
    print("Lucky Color:", info['color'])
    print("Lucky Day:", info['day'])

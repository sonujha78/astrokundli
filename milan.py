import core
import rashifal

NAKSHATRAS = [
    ("Ashwini", "Deva", "Horse", "Aadi"),
    ("Bharani", "Manushya", "Elephant", "Madhya"),
    ("Krittika", "Rakshasa", "Goat", "Antya"),
    ("Rohini", "Manushya", "Serpent", "Antya"),
    ("Mrigashira", "Deva", "Serpent", "Madhya"),
    ("Ardra", "Manushya", "Dog", "Aadi"),
    ("Punarvasu", "Deva", "Cat", "Aadi"),
    ("Pushya", "Deva", "Goat", "Madhya"),
    ("Ashlesha", "Rakshasa", "Cat", "Antya"),
    ("Magha", "Rakshasa", "Rat", "Antya"),
    ("Purva Phalguni", "Manushya", "Rat", "Madhya"),
    ("Uttara Phalguni", "Manushya", "Cow", "Aadi"),
    ("Hasta", "Deva", "Buffalo", "Aadi"),
    ("Chitra", "Rakshasa", "Tiger", "Madhya"),
    ("Swati", "Deva", "Buffalo", "Antya"),
    ("Vishakha", "Rakshasa", "Tiger", "Antya"),
    ("Anuradha", "Deva", "Deer", "Madhya"),
    ("Jyeshtha", "Rakshasa", "Deer", "Aadi"),
    ("Mula", "Rakshasa", "Dog", "Aadi"),
    ("Purva Ashadha", "Manushya", "Monkey", "Madhya"),
    ("Uttara Ashadha", "Manushya", "Mongoose", "Antya"),
    ("Shravana", "Deva", "Monkey", "Antya"),
    ("Dhanishta", "Rakshasa", "Lion", "Madhya"),
    ("Shatabhisha", "Rakshasa", "Horse", "Aadi"),
    ("Purva Bhadrapada", "Manushya", "Lion", "Madhya"),
    ("Uttara Bhadrapada", "Manushya", "Cow", "Antya"),
    ("Revati", "Deva", "Elephant", "Antya"),
]

RASHI_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
}

PLANET_RELATION = {
    "Sun":     {"friends": ["Moon", "Mars", "Jupiter"], "enemies": ["Venus", "Saturn"]},
    "Moon":    {"friends": ["Sun", "Mercury"], "enemies": []},
    "Mars":    {"friends": ["Sun", "Moon", "Jupiter"], "enemies": ["Mercury"]},
    "Mercury": {"friends": ["Sun", "Venus"], "enemies": ["Moon"]},
    "Jupiter": {"friends": ["Sun", "Moon", "Mars"], "enemies": ["Mercury", "Venus"]},
    "Venus":   {"friends": ["Mercury", "Saturn"], "enemies": ["Sun", "Moon"]},
    "Saturn":  {"friends": ["Mercury", "Venus"], "enemies": ["Sun", "Moon", "Mars"]},
}

VARNA = {
    "Cancer": "Brahmin", "Scorpio": "Brahmin", "Pisces": "Brahmin",
    "Aries": "Kshatriya", "Leo": "Kshatriya", "Sagittarius": "Kshatriya",
    "Taurus": "Vaishya", "Virgo": "Vaishya", "Capricorn": "Vaishya",
    "Gemini": "Shudra", "Libra": "Shudra", "Aquarius": "Shudra",
}
VARNA_RANK = {"Brahmin": 4, "Kshatriya": 3, "Vaishya": 2, "Shudra": 1}

VASHYA_GROUP = {
    "Aries": "Chatushpada", "Taurus": "Chatushpada", "Capricorn": "Chatushpada",
    "Gemini": "Manava", "Virgo": "Manava", "Libra": "Manava", "Sagittarius": "Manava", "Aquarius": "Manava",
    "Cancer": "Jalachar", "Pisces": "Jalachar",
    "Leo": "Vanachar",
    "Scorpio": "Keeta",
}
VASHYA_SCORE = {
    ("Chatushpada", "Chatushpada"): 2, ("Manava", "Manava"): 2, ("Jalachar", "Jalachar"): 2,
    ("Vanachar", "Vanachar"): 2, ("Keeta", "Keeta"): 2,
    ("Chatushpada", "Manava"): 1, ("Chatushpada", "Jalachar"): 1, ("Chatushpada", "Vanachar"): 0.5,
    ("Manava", "Jalachar"): 1, ("Manava", "Vanachar"): 0,
    ("Jalachar", "Vanachar"): 0.5,
}

YONI_ENEMIES = {
    frozenset(["Horse", "Buffalo"]), frozenset(["Elephant", "Lion"]),
    frozenset(["Goat", "Monkey"]), frozenset(["Serpent", "Mongoose"]),
    frozenset(["Dog", "Deer"]), frozenset(["Cat", "Rat"]), frozenset(["Cow", "Tiger"]),
}

GANA_SCORE = {
    ("Deva", "Deva"): 6, ("Manushya", "Manushya"): 6, ("Rakshasa", "Rakshasa"): 6,
    ("Deva", "Manushya"): 5, ("Manushya", "Deva"): 5,
    ("Deva", "Rakshasa"): 0, ("Rakshasa", "Deva"): 0,
    ("Manushya", "Rakshasa"): 0, ("Rakshasa", "Manushya"): 0,
}

TARA_GOOD = {2, 4, 6, 8, 9}

def get_nakshatra(moon_longitude):
    index = int(moon_longitude / (360 / 27)) % 27
    return index, NAKSHATRAS[index]

def get_relation(planet_a, planet_b):
    if planet_a == planet_b:
        return "friend"
    if planet_b in PLANET_RELATION[planet_a]["friends"]:
        return "friend"
    if planet_b in PLANET_RELATION[planet_a]["enemies"]:
        return "enemy"
    return "neutral"

GRAHA_MAITRI_TABLE = {
    ("friend", "friend"): 5, ("friend", "neutral"): 4, ("friend", "enemy"): 1,
    ("neutral", "friend"): 4, ("neutral", "neutral"): 3, ("neutral", "enemy"): 2,
    ("enemy", "friend"): 1, ("enemy", "neutral"): 2, ("enemy", "enemy"): 0,
}

def varna_koota(sign1, sign2):
    v1, v2 = VARNA[sign1], VARNA[sign2]
    score = 1 if VARNA_RANK[v1] >= VARNA_RANK[v2] else 0
    return score, f"{v1} & {v2}"

def vashya_koota(sign1, sign2):
    g1, g2 = VASHYA_GROUP[sign1], VASHYA_GROUP[sign2]
    score = VASHYA_SCORE.get((g1, g2)) or VASHYA_SCORE.get((g2, g1)) or 0
    return score, f"{g1} & {g2}"

def tara_koota(nak1_idx, nak2_idx):
    diff1 = ((nak2_idx - nak1_idx) % 27) + 1
    tara1 = ((diff1 - 1) % 9) + 1
    diff2 = ((nak1_idx - nak2_idx) % 27) + 1
    tara2 = ((diff2 - 1) % 9) + 1
    s1 = 3 if tara1 in TARA_GOOD else 0
    s2 = 3 if tara2 in TARA_GOOD else 0
    return round((s1 + s2) / 2, 1), f"Tara {tara1} & {tara2}"

def yoni_koota(nak1, nak2):
    y1, y2 = nak1[2], nak2[2]
    if y1 == y2:
        return 4, f"{y1} & {y2} (same)"
    if frozenset([y1, y2]) in YONI_ENEMIES:
        return 0, f"{y1} & {y2} (enemies)"
    return 2, f"{y1} & {y2} (neutral)"

def graha_maitri_koota(sign1, sign2):
    l1, l2 = RASHI_LORDS[sign1], RASHI_LORDS[sign2]
    rel1 = get_relation(l1, l2)
    rel2 = get_relation(l2, l1)
    score = GRAHA_MAITRI_TABLE[(rel1, rel2)]
    return score, f"{l1} & {l2}"

def gana_koota(nak1, nak2):
    g1, g2 = nak1[1], nak2[1]
    score = GANA_SCORE.get((g1, g2), 3)
    return score, f"{g1} & {g2}"

def bhakoot_koota(sign1, sign2):
    idx1 = core.ZODIAC_SIGNS.index(sign1)
    idx2 = core.ZODIAC_SIGNS.index(sign2)
    count = ((idx2 - idx1) % 12) + 1
    if count in (2, 5, 6, 8, 9, 12):
        return 0, "Bhakoot Dosha present"
    return 7, "No dosha"

def nadi_koota(nak1, nak2):
    n1, n2 = nak1[3], nak2[3]
    if n1 == n2:
        return 0, f"Same Nadi ({n1}) — Nadi Dosha"
    return 8, f"{n1} & {n2}"

def calculate_milan(jd1, lat1, lon1, jd2, lat2, lon2):
    planets1 = core.get_planet_positions(jd1)
    planets2 = core.get_planet_positions(jd2)
    moon_lon1 = planets1['Moon']['longitude']
    moon_lon2 = planets2['Moon']['longitude']
    sign1 = planets1['Moon']['sign']
    sign2 = planets2['Moon']['sign']

    idx1, nak1 = get_nakshatra(moon_lon1)
    idx2, nak2 = get_nakshatra(moon_lon2)

    results = {}
    results['Varna'] = (*varna_koota(sign1, sign2), 1)
    results['Vashya'] = (*vashya_koota(sign1, sign2), 2)
    results['Tara'] = (*tara_koota(idx1, idx2), 3)
    results['Yoni'] = (*yoni_koota(nak1, nak2), 4)
    results['Graha Maitri'] = (*graha_maitri_koota(sign1, sign2), 5)
    results['Gana'] = (*gana_koota(nak1, nak2), 6)
    results['Bhakoot'] = (*bhakoot_koota(sign1, sign2), 7)
    results['Nadi'] = (*nadi_koota(nak1, nak2), 8)

    total = sum(r[0] for r in results.values())
    return {
        'person1_moon_sign': sign1, 'person1_nakshatra': nak1[0],
        'person2_moon_sign': sign2, 'person2_nakshatra': nak2[0],
        'kootas': results, 'total_score': total, 'max_score': 36
    }

if __name__ == "__main__":
    jd1 = core.get_julian_day(1995, 8, 15, 14, 30, 5.5)
    jd2 = core.get_julian_day(1997, 3, 22, 9, 15, 5.5)
    result = calculate_milan(jd1, 28.6139, 77.2090, jd2, 19.0760, 72.8777)

    print(f"Person 1: {result['person1_moon_sign']} ({result['person1_nakshatra']})")
    print(f"Person 2: {result['person2_moon_sign']} ({result['person2_nakshatra']})")
    print()
    for koota, (score, detail, max_score) in result['kootas'].items():
        print(f"{koota} ({max_score}): {score} — {detail}")
    print(f"\nTotal: {result['total_score']}/{result['max_score']}")

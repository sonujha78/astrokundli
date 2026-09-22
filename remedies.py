PLANET_REMEDIES = {
    "Sun": {
        "mantra": "Om Suryaya Namaha (108 times, Sunday sunrise)",
        "upay": "Offer water to the Sun every morning; wear copper if advised by an astrologer.",
    },
    "Moon": {
        "mantra": "Om Chandraya Namaha (108 times, Monday)",
        "upay": "Keep a fast on Mondays; donate white items (rice, milk) on full moon days.",
    },
    "Mars": {
        "mantra": "Om Angarakaya Namaha (108 times, Tuesday)",
        "upay": "Donate red lentils or jaggery on Tuesdays; avoid conflicts on this day.",
    },
    "Mercury": {
        "mantra": "Om Budhaya Namaha (108 times, Wednesday)",
        "upay": "Feed green vegetables to cows; donate green clothes on Wednesdays.",
    },
    "Jupiter": {
        "mantra": "Om Brihaspataye Namaha (108 times, Thursday)",
        "upay": "Respect teachers and elders; donate yellow items or turmeric on Thursdays.",
    },
    "Venus": {
        "mantra": "Om Shukraya Namaha (108 times, Friday)",
        "upay": "Donate white items or perfumes on Fridays; maintain cleanliness and harmony at home.",
    },
    "Saturn": {
        "mantra": "Om Shanicharaya Namaha (108 times, Saturday)",
        "upay": "Help the needy and donate black sesame or mustard oil on Saturdays; avoid harsh words to elders/workers.",
    },
    "Rahu": {
        "mantra": "Om Rahave Namaha (108 times)",
        "upay": "Donate blankets or dark-colored grains; avoid impulsive decisions during Rahu periods.",
    },
    "Ketu": {
        "mantra": "Om Ketave Namaha (108 times)",
        "upay": "Practice meditation; donate to spiritual causes or multi-colored blankets.",
    },
}

MANGLIK_REMEDY = (
    "Traditional remedies for Manglik Dosha include worshipping Lord Hanuman on Tuesdays, "
    "fasting on Tuesdays, and in some traditions performing Kumbh Vivah before marriage. "
    "Consult a qualified astrologer or priest for a remedy suited to your specific chart."
)

SADESATI_REMEDY = (
    "During Sade Sati, chanting the Shani mantra (Om Shanicharaya Namaha) on Saturdays, "
    "donating black sesame seeds or mustard oil, and practicing patience and discipline "
    "are traditionally recommended."
)

def get_dasha_remedy(planet):
    return PLANET_REMEDIES.get(planet, {})

if __name__ == "__main__":
    r = get_dasha_remedy("Saturn")
    print("Mantra:", r['mantra'])
    print("Upay:", r['upay'])

import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ConversationHandler,
    CallbackQueryHandler, ContextTypes, filters
)

from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz

import core
import rashifal
import milan
import dasha
import manglik
import sadesati
import panchang
import remedies
import navamsa
from milan import NAKSHATRAS

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

geolocator = Nominatim(user_agent="astrokundli_bot")
tf = TimezoneFinder()

(NAME, DOB, TOB, POB,
 M1_NAME, M1_DOB, M1_TOB, M1_POB,
 M2_NAME, M2_DOB, M2_TOB, M2_POB) = range(12)

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔮 Kundli (Birth Chart)", callback_data="menu_kundli")],
        [InlineKeyboardButton("🌙 Rashifal (Daily/Weekly/Monthly)", callback_data="menu_rashifal")],
        [InlineKeyboardButton("💑 Kundli Milan (Matching)", callback_data="menu_milan")],
        [InlineKeyboardButton("🪐 Dasha Analysis", callback_data="menu_dasha")],
    ]
    return InlineKeyboardMarkup(keyboard)

def rashifal_period_keyboard():
    keyboard = [
        [InlineKeyboardButton("Daily", callback_data="period_daily")],
        [InlineKeyboardButton("Weekly", callback_data="period_weekly")],
        [InlineKeyboardButton("Monthly", callback_data="period_monthly")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "✨ *Welcome to AstroKundli* ✨\n\n"
        "Get accurate Vedic astrology readings, calculated using precise "
        "astronomical data (Swiss Ephemeris).\n\n"
        "Choose an option below:"
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "*Available commands:*\n"
        "/start - Show main menu\n"
        "/kundli - Generate your birth kundli\n"
        "/panchang - Today's Panchang\n"
        "/cancel - Cancel current operation\n"
        "/help - Show this message"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def panchang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now()
    result = panchang.get_panchang(today.year, today.month, today.day)
    nak_name = NAKSHATRAS[result['nakshatra_index']][0]

    text = f"📅 *Panchang — {result['date']} ({result['vara']})*\n\n"
    text += f"*Tithi:* {result['tithi']}\n"
    text += f"*Nakshatra:* {nak_name}\n"
    text += f"*Yoga:* {result['yoga']}\n"
    text += f"*Sun Sign:* {result['sun_sign']}\n"
    text += f"*Moon Sign:* {result['moon_sign']}\n"

    await update.message.reply_text(text, parse_mode="Markdown")

async def menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "menu_kundli":
        context.user_data['flow'] = 'kundli'
        await query.message.reply_text("Let's begin. First, tell me the name (for the report):")
        return NAME
    elif query.data == "menu_rashifal":
        context.user_data['flow'] = 'rashifal'
        await query.message.reply_text("Let's get your Rashifal. First, tell me your birth date (DD-MM-YYYY, e.g. 15-08-1995):")
        return DOB
    elif query.data == "menu_milan":
        context.user_data['flow'] = 'milan'
        await query.message.reply_text("Let's check compatibility. First, Person 1's name:")
        return M1_NAME
    elif query.data == "menu_dasha":
        context.user_data['flow'] = 'dasha'
        await query.message.reply_text("Let's find your current Dasha. First, tell me the name:")
        return NAME

async def kundli_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['flow'] = 'kundli'
    await update.message.reply_text("Let's begin. First, tell me the name (for the report):")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Tell me the birth date (DD-MM-YYYY format, e.g. 15-08-1995):")
    return DOB

async def get_dob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        dob = datetime.strptime(update.message.text.strip(), "%d-%m-%Y")
        context.user_data['dob'] = dob
    except ValueError:
        await update.message.reply_text("Wrong format. Send again as DD-MM-YYYY (e.g. 15-08-1995):")
        return DOB
    await update.message.reply_text("Tell me the birth time (24-hour HH:MM format, e.g. 14:30):")
    return TOB

async def get_tob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        tob = datetime.strptime(update.message.text.strip(), "%H:%M")
        context.user_data['hour'] = tob.hour
        context.user_data['minute'] = tob.minute
    except ValueError:
        await update.message.reply_text("Wrong format. Send again as HH:MM, 24-hour (e.g. 14:30):")
        return TOB
    await update.message.reply_text("Tell me the birth place (city, country — e.g. Delhi, India):")
    return POB

def resolve_place_and_offset(place, dob, hour, minute):
    location = geolocator.geocode(place, timeout=10)
    if not location:
        return None
    lat, lon = location.latitude, location.longitude
    tz_name = tf.timezone_at(lat=lat, lng=lon)
    if not tz_name:
        return None
    tz = pytz.timezone(tz_name)
    naive_dt = datetime(dob.year, dob.month, dob.day, hour, minute)
    localized_dt = tz.localize(naive_dt)
    tz_offset = localized_dt.utcoffset().total_seconds() / 3600
    return lat, lon, tz_name, tz_offset

async def get_pob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    place = update.message.text.strip()
    await update.message.reply_text("Calculating, please wait...")

    dob = context.user_data['dob']
    hour = context.user_data['hour']
    minute = context.user_data['minute']

    try:
        resolved = resolve_place_and_offset(place, dob, hour, minute)
        if not resolved:
            await update.message.reply_text("Couldn't find that place. Please send a valid city, country:")
            return POB
        lat, lon, tz_name, tz_offset = resolved

        jd = core.get_julian_day(dob.year, dob.month, dob.day, hour, minute, tz_offset)

        if context.user_data['flow'] == 'kundli':
            planets = core.get_planet_positions_with_retrograde(jd)
            ascendant = core.get_ascendant(jd, lat, lon)
            houses = core.get_houses(jd, lat, lon)
            manglik_result = manglik.check_manglik(jd, lat, lon)
            natal_moon_index = core.ZODIAC_SIGNS.index(planets['Moon']['sign'])
            sadesati_result = sadesati.check_sade_sati(natal_moon_index)

            name = context.user_data['name']
            result = f"🔮 *Kundli for {name}*\n"
            result += f"📍 {place} | 🕐 {hour:02d}:{minute:02d} | 📅 {dob.strftime('%d-%m-%Y')}\n"
            result += f"🌐 Timezone: {tz_name} (UTC{tz_offset:+.1f})\n\n"
            result += f"*Ascendant (Lagna):* {ascendant['sign']} {ascendant['degree']}°\n\n"
            result += "*Planetary Positions:*\n"
            for planet, data in planets.items():
                r_marker = " (R)" if data.get('retrograde') else ""
                result += f"  {planet}: {data['sign']} {data['degree']}°{r_marker}\n"
            result += "\n*Houses:*\n"
            for h, data in houses.items():
                result += f"  House {h}: {data['sign']} {data['degree']}°\n"

            navamsa_result = navamsa.get_navamsa_chart(jd, lat, lon)
            result += f"\n*Navamsa (D9) Ascendant:* {navamsa_result['ascendant']}\n"
            result += "*Navamsa Positions:*\n"
            for planet, sign in navamsa_result['planets'].items():
                result += f"  {planet}: {sign}\n"

            result += f"\n*Manglik Dosha:* {'Yes' if manglik_result['is_manglik'] else 'No'} "
            result += f"(Mars in house {manglik_result['mars_house']})\n"

            if sadesati_result['is_active']:
                result += f"*Sade Sati:* Active — {sadesati_result['phase']}\n"
            else:
                result += "*Sade Sati:* Not active\n"

            if manglik_result['is_manglik'] or sadesati_result['is_active']:
                result += "\n*Suggested Remedies:*\n"
                if manglik_result['is_manglik']:
                    result += f"  Manglik: {remedies.MANGLIK_REMEDY}\n"
                if sadesati_result['is_active']:
                    result += f"  Sade Sati: {remedies.SADESATI_REMEDY}\n"

            await update.message.reply_text(result, parse_mode="Markdown")
            return ConversationHandler.END

        elif context.user_data['flow'] == 'rashifal':
            natal_moon_index = rashifal.get_natal_moon_sign(jd, lat, lon)
            context.user_data['natal_moon_index'] = natal_moon_index
            moon_sign_name = core.ZODIAC_SIGNS[natal_moon_index]
            await update.message.reply_text(
                f"Your Moon Sign (Rashi) is *{moon_sign_name}*.\n\nChoose a period:",
                parse_mode="Markdown",
                reply_markup=rashifal_period_keyboard()
            )
            return ConversationHandler.END

        elif context.user_data['flow'] == 'dasha':
            planets = core.get_planet_positions_with_retrograde(jd)
            moon_lon = planets['Moon']['longitude']
            birth_dt = datetime(dob.year, dob.month, dob.day, hour, minute)

            lord, balance = dasha.get_birth_dasha_balance(moon_lon)
            timeline = dasha.build_mahadasha_timeline(birth_dt, moon_lon)
            today = datetime.now()
            maha_planet, maha_start, maha_end = dasha.get_current_mahadasha(timeline, today)

            name = context.user_data['name']
            result = f"🪐 *Dasha Analysis for {name}*\n\n"
            result += f"Birth Nakshatra Lord: {lord} (balance at birth: {balance:.1f} years)\n\n"

            if maha_planet:
                antar_planet, antar_start, antar_end = dasha.get_antardasha(maha_planet, maha_start, maha_end, today)
                result += f"*Current Mahadasha:* {maha_planet}\n"
                result += f"  ({maha_start.strftime('%d-%m-%Y')} to {maha_end.strftime('%d-%m-%Y')})\n\n"
                if antar_planet:
                    result += f"*Current Antardasha:* {antar_planet}\n"
                    result += f"  ({antar_start.strftime('%d-%m-%Y')} to {antar_end.strftime('%d-%m-%Y')})\n\n"

                remedy = remedies.get_dasha_remedy(maha_planet)
                if remedy:
                    result += f"*Remedy for {maha_planet} Mahadasha:*\n"
                    result += f"  Mantra: {remedy['mantra']}\n"
                    result += f"  Upay: {remedy['upay']}\n\n"
            else:
                result += "Could not determine current dasha (date out of calculated range).\n\n"

            result += "*Mahadasha Timeline (first 9 periods):*\n"
            for planet, start, end in timeline[:9]:
                marker = " ← current" if planet == maha_planet else ""
                result += f"  {planet}: {start.strftime('%Y')} - {end.strftime('%Y')}{marker}\n"

            await update.message.reply_text(result, parse_mode="Markdown")
            return ConversationHandler.END

    except Exception as e:
        logger.error(f"Error in get_pob: {e}")
        await update.message.reply_text("Something went wrong. Please try /start again.")
        return ConversationHandler.END

async def rashifal_period_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    natal_moon_index = context.user_data.get('natal_moon_index')
    if natal_moon_index is None:
        await query.message.reply_text("Session expired. Please use /start and select Rashifal again.")
        return

    moon_sign_name = core.ZODIAC_SIGNS[natal_moon_index]

    if query.data == "period_daily":
        house, text = rashifal.get_daily_rashifal(natal_moon_index)
        await query.message.reply_text(f"🌙 *Daily Rashifal — {moon_sign_name}*\n\n{text}", parse_mode="Markdown")
    elif query.data == "period_weekly":
        house, text = rashifal.get_daily_rashifal(natal_moon_index)
        await query.message.reply_text(f"🌙 *Weekly Overview — {moon_sign_name}*\n\n{text}", parse_mode="Markdown")
    elif query.data == "period_monthly":
        house, text = rashifal.get_monthly_rashifal(natal_moon_index)
        await query.message.reply_text(f"🌙 *Monthly Rashifal — {moon_sign_name}*\n\n{text}", parse_mode="Markdown")

# ---- Kundli Milan flow ----

async def m1_get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['p1_name'] = update.message.text
    await update.message.reply_text("Person 1's birth date (DD-MM-YYYY):")
    return M1_DOB

async def m1_get_dob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['p1_dob'] = datetime.strptime(update.message.text.strip(), "%d-%m-%Y")
    except ValueError:
        await update.message.reply_text("Wrong format. Send again as DD-MM-YYYY:")
        return M1_DOB
    await update.message.reply_text("Person 1's birth time (24-hour HH:MM):")
    return M1_TOB

async def m1_get_tob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        t = datetime.strptime(update.message.text.strip(), "%H:%M")
        context.user_data['p1_hour'] = t.hour
        context.user_data['p1_minute'] = t.minute
    except ValueError:
        await update.message.reply_text("Wrong format. Send again as HH:MM:")
        return M1_TOB
    await update.message.reply_text("Person 1's birth place (city, country):")
    return M1_POB

async def m1_get_pob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    place = update.message.text.strip()
    resolved = resolve_place_and_offset(
        place, context.user_data['p1_dob'], context.user_data['p1_hour'], context.user_data['p1_minute']
    )
    if not resolved:
        await update.message.reply_text("Couldn't find that place. Send a valid city, country:")
        return M1_POB
    lat, lon, tz_name, tz_offset = resolved
    dob = context.user_data['p1_dob']
    context.user_data['p1_jd'] = core.get_julian_day(
        dob.year, dob.month, dob.day, context.user_data['p1_hour'], context.user_data['p1_minute'], tz_offset
    )
    context.user_data['p1_lat'] = lat
    context.user_data['p1_lon'] = lon

    await update.message.reply_text("Got it. Now Person 2's name:")
    return M2_NAME

async def m2_get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['p2_name'] = update.message.text
    await update.message.reply_text("Person 2's birth date (DD-MM-YYYY):")
    return M2_DOB

async def m2_get_dob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['p2_dob'] = datetime.strptime(update.message.text.strip(), "%d-%m-%Y")
    except ValueError:
        await update.message.reply_text("Wrong format. Send again as DD-MM-YYYY:")
        return M2_DOB
    await update.message.reply_text("Person 2's birth time (24-hour HH:MM):")
    return M2_TOB

async def m2_get_tob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        t = datetime.strptime(update.message.text.strip(), "%H:%M")
        context.user_data['p2_hour'] = t.hour
        context.user_data['p2_minute'] = t.minute
    except ValueError:
        await update.message.reply_text("Wrong format. Send again as HH:MM:")
        return M2_TOB
    await update.message.reply_text("Person 2's birth place (city, country):")
    return M2_POB

async def m2_get_pob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    place = update.message.text.strip()
    await update.message.reply_text("Calculating compatibility, please wait...")

    resolved = resolve_place_and_offset(
        place, context.user_data['p2_dob'], context.user_data['p2_hour'], context.user_data['p2_minute']
    )
    if not resolved:
        await update.message.reply_text("Couldn't find that place. Send a valid city, country:")
        return M2_POB
    lat2, lon2, tz_name2, tz_offset2 = resolved
    dob2 = context.user_data['p2_dob']
    jd2 = core.get_julian_day(
        dob2.year, dob2.month, dob2.day, context.user_data['p2_hour'], context.user_data['p2_minute'], tz_offset2
    )

    try:
        result = milan.calculate_milan(
            context.user_data['p1_jd'], context.user_data['p1_lat'], context.user_data['p1_lon'],
            jd2, lat2, lon2
        )

        p1_name = context.user_data['p1_name']
        p2_name = context.user_data['p2_name']

        p1_manglik = manglik.check_manglik(context.user_data['p1_jd'], context.user_data['p1_lat'], context.user_data['p1_lon'])
        p2_manglik = manglik.check_manglik(jd2, lat2, lon2)

        text = f"💑 *Kundli Milan: {p1_name} & {p2_name}*\n\n"
        text += f"{p1_name}: {result['person1_moon_sign']} ({result['person1_nakshatra']}) — Manglik: {'Yes' if p1_manglik['is_manglik'] else 'No'}\n"
        text += f"{p2_name}: {result['person2_moon_sign']} ({result['person2_nakshatra']}) — Manglik: {'Yes' if p2_manglik['is_manglik'] else 'No'}\n\n"
        text += "*Ashtakoot Guna Milan:*\n"
        for koota, (score, detail, max_score) in result['kootas'].items():
            text += f"  {koota}: {score}/{max_score}\n"
        text += f"\n*Total Score: {result['total_score']}/{result['max_score']}*\n\n"

        pct = result['total_score'] / result['max_score']
        if pct >= 0.75:
            verdict = "Excellent match."
        elif pct >= 0.55:
            verdict = "Good match."
        elif pct >= 0.40:
            verdict = "Average match — some factors need attention."
        else:
            verdict = "Low compatibility — consult an astrologer before proceeding."

        if p1_manglik['is_manglik'] != p2_manglik['is_manglik']:
            verdict += " Note: Manglik status differs between the two."
            text += f"\n*Remedy note:* {remedies.MANGLIK_REMEDY}\n\n"

        text += verdict

        await update.message.reply_text(text, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error in milan calculation: {e}")
        await update.message.reply_text("Something went wrong. Please try /start again.")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled. Use /start to begin again.")
    return ConversationHandler.END

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("kundli", kundli_start),
            CallbackQueryHandler(menu_router, pattern="^menu_"),
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            DOB: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_dob)],
            TOB: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_tob)],
            POB: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_pob)],
            M1_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, m1_get_name)],
            M1_DOB: [MessageHandler(filters.TEXT & ~filters.COMMAND, m1_get_dob)],
            M1_TOB: [MessageHandler(filters.TEXT & ~filters.COMMAND, m1_get_tob)],
            M1_POB: [MessageHandler(filters.TEXT & ~filters.COMMAND, m1_get_pob)],
            M2_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, m2_get_name)],
            M2_DOB: [MessageHandler(filters.TEXT & ~filters.COMMAND, m2_get_dob)],
            M2_TOB: [MessageHandler(filters.TEXT & ~filters.COMMAND, m2_get_tob)],
            M2_POB: [MessageHandler(filters.TEXT & ~filters.COMMAND, m2_get_pob)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("panchang", panchang_command))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(rashifal_period_router, pattern="^period_"))

    logger.info("Bot starting...")
    app.run_polling()

if __name__ == "__main__":
    main()

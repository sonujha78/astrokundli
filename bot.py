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

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

geolocator = Nominatim(user_agent="astrokundli_bot")
tf = TimezoneFinder()

NAME, DOB, TOB, POB = range(4)

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
        "/cancel - Cancel current operation\n"
        "/help - Show this message"
    )
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
        await query.message.reply_text("💑 Kundli Milan is coming soon!")
        return ConversationHandler.END
    elif query.data == "menu_dasha":
        await query.message.reply_text("🪐 Dasha Analysis is coming soon!")
        return ConversationHandler.END

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
            planets = core.get_planet_positions(jd)
            ascendant = core.get_ascendant(jd, lat, lon)
            houses = core.get_houses(jd, lat, lon)

            name = context.user_data['name']
            result = f"🔮 *Kundli for {name}*\n"
            result += f"📍 {place} | 🕐 {hour:02d}:{minute:02d} | 📅 {dob.strftime('%d-%m-%Y')}\n"
            result += f"🌐 Timezone: {tz_name} (UTC{tz_offset:+.1f})\n\n"
            result += f"*Ascendant (Lagna):* {ascendant['sign']} {ascendant['degree']}°\n\n"
            result += "*Planetary Positions:*\n"
            for planet, data in planets.items():
                result += f"  {planet}: {data['sign']} {data['degree']}°\n"
            result += "\n*Houses:*\n"
            for h, data in houses.items():
                result += f"  House {h}: {data['sign']} {data['degree']}°\n"

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
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(rashifal_period_router, pattern="^period_"))

    logger.info("Bot starting...")
    app.run_polling()

if __name__ == "__main__":
    main()

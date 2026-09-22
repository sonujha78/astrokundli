import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ConversationHandler,
    ContextTypes, filters
)

from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz

import core

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

geolocator = Nominatim(user_agent="astrokundli_bot")
tf = TimezoneFinder()

NAME, DOB, TOB, POB = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🔮 Generate Kundli", callback_data="start_kundli")]]
    text = (
        "✨ *Welcome to AstroKundli* ✨\n\n"
        "Get accurate Vedic astrology readings — birth kundli, planetary positions, "
        "houses, and more, calculated using precise astronomical data (Swiss Ephemeris).\n\n"
        "Use /kundli to generate your birth chart.\n"
        "Use /help to see all commands."
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "*Available commands:*\n"
        "/kundli - Generate your birth kundli\n"
        "/cancel - Cancel current operation\n"
        "/help - Show this message"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def kundli_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Chaliye shuru karte hain. Sabse pehle, naam bataiye (report ke liye):")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Birth date bataiye (DD-MM-YYYY format mein, jaise 15-08-1995):")
    return DOB

async def get_dob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        dob = datetime.strptime(update.message.text.strip(), "%d-%m-%Y")
        context.user_data['dob'] = dob
    except ValueError:
        await update.message.reply_text("Format galat hai. DD-MM-YYYY mein dobara bhejiye (jaise 15-08-1995):")
        return DOB
    await update.message.reply_text("Birth time bataiye (24-hour HH:MM format mein, jaise 14:30):")
    return TOB

async def get_tob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        tob = datetime.strptime(update.message.text.strip(), "%H:%M")
        context.user_data['hour'] = tob.hour
        context.user_data['minute'] = tob.minute
    except ValueError:
        await update.message.reply_text("Format galat hai. HH:MM (24-hour) mein dobara bhejiye (jaise 14:30):")
        return TOB
    await update.message.reply_text("Birth place bataiye (city, country — jaise Delhi, India):")
    return POB

async def get_pob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    place = update.message.text.strip()
    await update.message.reply_text("Calculate kar raha hoon, thoda ruko...")

    try:
        location = geolocator.geocode(place, timeout=10)
        if not location:
            await update.message.reply_text("Ye jagah nahi mil paayi. Dobara sahi naam se bhejiye (jaise Delhi, India):")
            return POB

        lat, lon = location.latitude, location.longitude
        tz_name = tf.timezone_at(lat=lat, lng=lon)
        if not tz_name:
            await update.message.reply_text("Timezone nahi mil paaya is location ke liye. Kisi aur nazdeeki city se try karo:")
            return POB

        tz = pytz.timezone(tz_name)
        dob = context.user_data['dob']
        hour = context.user_data['hour']
        minute = context.user_data['minute']

        naive_dt = datetime(dob.year, dob.month, dob.day, hour, minute)
        localized_dt = tz.localize(naive_dt)
        tz_offset = localized_dt.utcoffset().total_seconds() / 3600

        jd = core.get_julian_day(dob.year, dob.month, dob.day, hour, minute, tz_offset)
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

    except Exception as e:
        logger.error(f"Error calculating kundli: {e}")
        await update.message.reply_text("Kuch error aaya calculation mein. /kundli se dobara try karo.")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancel kar diya. /kundli se dobara shuru kar sakte ho.")
    return ConversationHandler.END

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("kundli", kundli_start)],
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

    logger.info("Bot starting...")
    app.run_polling()

if __name__ == "__main__":
    main()

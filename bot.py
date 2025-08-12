import logging
import pandas as pd
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# --- CONFIG ---
BOT_TOKEN = "8147995763:AAFh94oO54P1MzxP-8pDHJBjI_AYl-_QPDI"  # Replace with new token from BotFather
CSV_FILE = "incidents.csv"

# --- Logging ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# --- Conversation states ---
CHOOSING, DATE, TYPE, LOCATION, DESCRIPTION = range(5)


# --- Start Command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("📢 Incident", callback_data="incident"),
            InlineKeyboardButton("🛡 Vulnerability", callback_data="vulnerability"),
        ],
        [InlineKeyboardButton("💬 Comment", callback_data="comment")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
 "🚨 Welcome to the Incident Reporting Bot!\n\n"
    "You can use this bot to quickly and easily report any incidents or vulnerabilities related to our system.\n\n"
    "How it works:\n"
    "1️⃣ Send /start to begin reporting an incident.\n"
    "2️⃣ The bot will ask you for:\n"
    "   🗓️ The date of the incident (e.g., 2025-08-11)\n"
    "   ⚠️ The type of incident or vulnerability (e.g., SQL injection)\n"
    "   📍 The location or affected system/department\n"
    "   📝 Additional description or details (optional — you can type skip if you have nothing to add)\n\n"
    "3️⃣ After you provide all the details, the bot will save your report and confirm it.\n\n"
    "If you want to cancel ❌at any time, just send /cancel.\n\n"
    "Your reports help us keep the system secure and respond quickly. Thank you for your cooperation! 🙌\n\n"
   "🙌Addispay Security Department\n\n"

        "🚨 Welcome to the Reporting Bot!\n\n"
        "Please choose the type of report you want to make:",
        reply_markup=reply_markup,
    )
    return CHOOSING


# --- Choice handler ---
async def choose_report_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    choice = query.data
    context.user_data["report_type"] = choice
    await query.edit_message_text(
        text=f"✅ You selected: {choice.capitalize()}\n\nPlease enter the date (YYYY-MM-DD):"
    )
    return DATE


# --- Handlers for each step ---
async def date_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_date = update.message.text
    context.user_data["date"] = user_date
    await update.message.reply_text("Please enter the type (e.g., SQL injection, System outage):")
    return TYPE


async def type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["type"] = update.message.text
    await update.message.reply_text("Please enter the location (system, department, etc.):")
    return LOCATION


async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["location"] = update.message.text
    await update.message.reply_text(
        "Optional: Enter additional description or details (or type 'skip'):"
    )
    return DESCRIPTION


async def description_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    desc = update.message.text
    if desc.lower() == "skip":
        desc = ""
    context.user_data["description"] = desc

    user = (
        f"{update.message.from_user.first_name or ''} {update.message.from_user.last_name or ''}"
    ).strip() or "Unknown"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["timestamp", "user", "report_type", "date", "type", "location", "description"])

    new_row = {
        "timestamp": timestamp,
        "user": user,
        "report_type": context.user_data["report_type"],
        "date": context.user_data["date"],
        "type": context.user_data["type"],
        "location": context.user_data["location"],
        "description": context.user_data["description"],
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

    await update.message.reply_text("✅ Report saved successfully! Thank you.")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Reporting cancelled.")
    return ConversationHandler.END


# --- Main ---
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [CallbackQueryHandler(choose_report_type)],
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, date_handler)],
            TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, type_handler)],
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, location_handler)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, description_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()



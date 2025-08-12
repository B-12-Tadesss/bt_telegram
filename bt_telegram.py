
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "YOUR_BOT_TOKEN"
YOUTUBE_LINK = "https://www.youtube.com/@YourChannelName"  # Replace with your channel or video link

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(
            f"👋 Welcome {member.full_name}!\n"
            f"እንኳን ደህና መጡ፣ በዚህ ቻናልTechnology courses and solutions. like network & system administration, wireless communication, internet programming, programming language ,database system, and other Network technology,  data science, artificial technology.ከታች የሚገኘው ቁልፍ በመጫን የዩቲዩብ ቻናላችንን ሰብስክራይብ በማድረግ ቤተሰብ ይሁኑ. 🎉\n"
            f"📺 Check out our YouTube: {YOUTUBE_LINK}"
        )

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

print("🤖 Bot is running...")
app.run_polling()

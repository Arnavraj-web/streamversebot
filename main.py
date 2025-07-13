from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputTextMessageContent, InlineQueryResultArticle
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, InlineQueryHandler, ContextTypes, filters
)
from uuid import uuid4
import json, os

# ====== CONFIGURATION =======
BOT_TOKEN = "7926543026:AAGR-fO2MXEj6el-KtXrKWl6aQAJoOaldqc"
ADMIN_ID = 8029898604
CHANNEL_CHAT_ID = -1002333915468
MOD_MESSAGE_ID = 4
VIP_FILE = "vip_users.json"
UPI_ID = "952590273"

# ====== FILE SETUP ==========
if not os.path.exists(VIP_FILE):
    with open(VIP_FILE, "w") as f:
        json.dump([], f)

def load_vips():
    with open(VIP_FILE, "r") as f:
        return json.load(f)

def save_vips(vips):
    with open(VIP_FILE, "w") as f:
        json.dump(vips, f)

# ====== COMMANDS ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to *StreamVerse AI Bot!*\n\n🔎 Type any app/game name\n💎 Use /mod for Mod APKs (VIP only)\n💰 Use /vip to become VIP",
        parse_mode="Markdown"
    )

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    search = query.replace(" ", "+")
    name_display = query.title()

    keyboard = [
        [InlineKeyboardButton("📱 Play Store", url=f"https://play.google.com/store/search?q={search}&c=apps")],
        [InlineKeyboardButton("📥 APKPure", url=f"https://apkpure.com/search?q={search}")],
        [InlineKeyboardButton("🧨 Mod Combo", url=f"https://modcombo.com/search.html?q={search}")],
        [InlineKeyboardButton("💎 Get VIP Access", callback_data="get_vip")]
    ]
    await update.message.reply_text(
        f"📲 *{name_display}* — Choose your source below 👇",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query.strip()
    if not query:
        return

    search = query.replace(" ", "+")
    title = query.title()
    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title=f"📲 {title}",
            description="Links: Play Store, APKPure, ModCombo",
            input_message_content=InputTextMessageContent(
                f"🔗 [Play Store](https://play.google.com/store/search?q={search}&c=apps)\n"
                f"🔗 [APKPure](https://apkpure.com/search?q={search})\n"
                f"🔗 [ModCombo](https://modcombo.com/search.html?q={search})",
                parse_mode="Markdown"
            )
        )
    ]
    await update.inline_query.answer(results, cache_time=0)

async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"💸 *VIP Access – ₹49 only!*\n\nSend payment to:\n`{UPI_ID}` via any UPI app.\n📤 After payment, send screenshot here.\nWe'll approve you in 1–3 minutes.",
        parse_mode="Markdown"
    )

async def mod(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    vips = load_vips()
    if user_id in vips:
        await update.message.reply_text("📦 Sending your Mod APK...")
        await context.bot.forward_message(
            chat_id=update.effective_chat.id,
            from_chat_id=CHANNEL_CHAT_ID,
            message_id=MOD_MESSAGE_ID
        )
    else:
        await update.message.reply_text("🚫 You are not a VIP. Use /vip to get access.", parse_mode="Markdown")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    caption = f"🧾 Payment screenshot from: {user.first_name}\n🆔 User ID: `{user.id}`\n\nApprove via:\n/addvip {user.id}"
    await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=update.message.chat_id, message_id=update.message.message_id)
    await context.bot.send_message(chat_id=ADMIN_ID, text=caption, parse_mode="Markdown")
    await update.message.reply_text("🕐 Screenshot sent to admin. Please wait for approval.")

async def addvip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if context.args:
        new_vip = int(context.args[0])
        vips = load_vips()
        if new_vip not in vips:
            vips.append(new_vip)
            save_vips(vips)
            await update.message.reply_text(f"✅ Added {new_vip} as VIP.")
            await context.bot.send_message(chat_id=new_vip, text="🎉 You're now a VIP! Use /mod to access Mod APKs.")
        else:
            await update.message.reply_text("ℹ️ Already VIP.")
    else:
        await update.message.reply_text("Usage: /addvip <user_id>")

async def removevip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if context.args:
        remove_id = int(context.args[0])
        vips = load_vips()
        if remove_id in vips:
            vips.remove(remove_id)
            save_vips(vips)
            await update.message.reply_text(f"❌ Removed {remove_id} from VIP.")
        else:
            await update.message.reply_text("⚠️ Not in VIP list.")
    else:
        await update.message.reply_text("Usage: /removevip <user_id>")

# ========== Bot Setup =============
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("mod", mod))
app.add_handler(CommandHandler("vip", vip))
app.add_handler(CommandHandler("addvip", addvip))
app.add_handler(CommandHandler("removevip", removevip))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
app.add_handler(InlineQueryHandler(inline_query))

print("✅ StreamVerse AI Bot is Live...")
app.run_polling()
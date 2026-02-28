import logging
import os
from collections import defaultdict, deque
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

import gateio_api
import market_context
import deepseek_ai
from config import TELEGRAM_TOKEN

# Setup logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# History percakapan per user
user_conversations = {}
MAX_HISTORY = 10
user_last_message = defaultdict(float)
RATE_LIMIT = 1

# ========== HANDLER PERINTAH ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "📈 *Selamat datang di AI Trading Assistant!*\n\n"
        "Saya adalah asisten trading kripto dengan data real-time dari **Gate.io** "
        "dan kecerdasan **DeepSeek AI**.\n\n"
        "✨ *Yang bisa saya lakukan:*\n"
        "• 💰 Cek harga crypto (contoh: *harga btc*)\n"
        "• 📚 Lihat order book (contoh: *order book eth*)\n"
        "• 📊 Analisis pasar (contoh: *analisis btc*)\n"
        "• 💬 Tanya apa pun tentang kripto\n\n"
        "🔍 *Cara penggunaan:*\n"
        "Langsung chat saja dengan saya, atau gunakan tombol menu di bawah."
    )
    keyboard = [
        [InlineKeyboardButton("💰 Harga Crypto", callback_data="menu_prices")],
        [InlineKeyboardButton("📚 Order Book", callback_data="menu_orderbook")],
        [InlineKeyboardButton("📊 Ringkasan Pasar", callback_data="menu_summary")],
        [InlineKeyboardButton("🔐 Cek Saldo", callback_data="menu_balance")],
        [InlineKeyboardButton("🧹 Hapus Riwayat", callback_data="menu_clear")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🆘 *Bantuan Penggunaan*\n\n"
        "• *Cek harga*: ketik 'harga btc' atau 'price eth'\n"
        "• *Order book*: ketik 'order book btc'\n"
        "• *Analisis*: ketik 'analisis btc' atau 'analysis eth'\n"
        "• *Ringkasan pasar*: ketik 'ringkasan' atau 'summary'\n"
        "• *Tanya AI*: tanya apa saja tentang kripto\n\n"
        "Gunakan /clear untuk menghapus riwayat percakapan."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_conversations:
        user_conversations[user_id].clear()
    await update.message.reply_text("✅ Riwayat percakapan telah dihapus.")

# ========== HANDLER PESAN ==========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text

    # Rate limiting
    now = time.time()
    if now - user_last_message[user_id] < RATE_LIMIT:
        await update.message.reply_text("⏳ Tolong tunggu sebentar sebelum mengirim pesan lagi.")
        return
    user_last_message[user_id] = now

    await update.message.chat.send_action(action="typing")

    if user_id not in user_conversations:
        user_conversations[user_id] = deque(maxlen=MAX_HISTORY)
    user_conversations[user_id].append({"role": "user", "content": user_message})

    # Deteksi intent
    lower_msg = user_message.lower()
    market_context_data = ""

    if any(word in lower_msg for word in ["harga", "price"]):
        symbols = ["btc", "eth", "bnb", "sol", "xrp", "ada", "doge", "dot"]
        for symbol in symbols:
            if symbol in lower_msg:
                ctx = market_context.get_price_context(symbol.upper())
                if ctx:
                    market_context_data = f"Data real-time:\n{ctx}\n"
                break
        if not market_context_data:
            market_context_data = f"Data pasar:\n{market_context.get_general_market_summary()}"
    elif any(word in lower_msg for word in ["order book", "depth", "buku order"]):
        symbols = ["btc", "eth", "bnb", "sol", "xrp"]
        for symbol in symbols:
            if symbol in lower_msg:
                ctx = market_context.get_orderbook_context(symbol.upper())
                if ctx:
                    market_context_data = ctx
                break
    elif any(word in lower_msg for word in ["ringkasan", "summary", "pasar"]):
        market_context_data = market_context.get_general_market_summary()
    else:
        market_context_data = market_context.get_general_market_summary()

    history = list(user_conversations[user_id])[-5:]
    ai_response = deepseek_ai.chat_with_ai(history, market_context=market_context_data)
    user_conversations[user_id].append({"role": "assistant", "content": ai_response})
    await update.message.reply_text(ai_response, parse_mode="Markdown")

# ========== HANDLER TOMBOL ==========
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu_prices":
        await show_prices_menu(query)
    elif data == "menu_orderbook":
        await show_orderbook_menu(query)
    elif data == "menu_summary":
        await show_summary(query)
    elif data == "menu_balance":
        await show_balance(query)
    elif data == "menu_clear":
        user_id = query.from_user.id
        if user_id in user_conversations:
            user_conversations[user_id].clear()
        await query.edit_message_text("✅ Riwayat percakapan telah dihapus.")
    elif data.startswith("ob_"):
        await show_orderbook_detail(query, data.replace("ob_", ""))
    elif data == "back_to_main":
        await start(query, context)

async def show_prices_menu(query):
    await query.edit_message_text("🔍 Mengambil data harga...")
    pairs = ["BTC_USDT", "ETH_USDT", "BNB_USDT", "SOL_USDT", "XRP_USDT"]
    lines = ["💰 *Harga Crypto (Gate.io)*\n"]
    for pair in pairs:
        ticker = gateio_api.get_ticker(pair)
        if ticker and isinstance(ticker, list) and len(ticker) > 0:
            t = ticker[0]
            last = t.get('last', 'N/A')
            change = t.get('change_percentage', '0')
            change_display = f"+{change}%" if float(change) > 0 else f"{change}%"
            pair_display = pair.replace('_', '/')
            lines.append(f"• *{pair_display}*: ${last} ({change_display})")
        else:
            lines.append(f"• {pair.replace('_', '/')}: Data tidak tersedia")
    keyboard = [[InlineKeyboardButton("◀️ Kembali", callback_data="back_to_main")]]
    await query.edit_message_text("\n".join(lines), parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_orderbook_menu(query):
    text = "📚 *Pilih Pair untuk Lihat Order Book:*"
    keyboard = [
        [InlineKeyboardButton("BTC/USDT", callback_data="ob_BTC")],
        [InlineKeyboardButton("ETH/USDT", callback_data="ob_ETH")],
        [InlineKeyboardButton("BNB/USDT", callback_data="ob_BNB")],
        [InlineKeyboardButton("SOL/USDT", callback_data="ob_SOL")],
        [InlineKeyboardButton("◀️ Kembali", callback_data="back_to_main")]
    ]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_orderbook_detail(query, symbol):
    await query.edit_message_text(f"🔍 Mengambil order book {symbol}/USDT...")
    ob = gateio_api.get_order_book(f"{symbol}_USDT", limit=5)
    if 'bids' in ob and 'asks' in ob and ob['bids'] and ob['asks']:
        lines = [f"📚 *Order Book {symbol}/USDT*"]
        lines.append("\n🔵 *Bids (Beli)*")
        for bid in ob['bids'][:5]:
            lines.append(f"   {bid[0]} — {bid[1]}")
        lines.append("\n🔴 *Asks (Jual)*")
        for ask in ob['asks'][:5]:
            lines.append(f"   {ask[0]} — {ask[1]}")
    else:
        lines = [f"❌ Gagal mengambil data order book {symbol}/USDT"]
    keyboard = [[InlineKeyboardButton("◀️ Kembali", callback_data="menu_orderbook")]]
    await query.edit_message_text("\n".join(lines), parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_summary(query):
    await query.edit_message_text("🔍 Menyusun ringkasan pasar...")
    summary = market_context.get_general_market_summary()
    keyboard = [[InlineKeyboardButton("◀️ Kembali", callback_data="back_to_main")]]
    await query.edit_message_text(summary, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_balance(query):
    await query.edit_message_text("🔐 Mengakses saldo akun...")
    if not os.getenv("GATEIO_API_KEY") or not os.getenv("GATEIO_API_SECRET"):
        text = "⚠️ *Fitur ini memerlukan API Key Gate.io*\n\nTambahkan GATEIO_API_KEY dan GATEIO_API_SECRET di environment variables untuk mengaktifkan fitur ini."
        keyboard = [[InlineKeyboardButton("◀️ Kembali", callback_data="back_to_main")]]
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    accounts = gateio_api.get_spot_accounts()
    if isinstance(accounts, list):
        lines = ["🔐 *Saldo Spot Gate.io:*\n"]
        has_balance = False
        for acc in accounts:
            currency = acc['currency']
            available = acc['available']
            locked = acc.get('locked', '0')
            if float(available) > 0 or float(locked) > 0:
                lines.append(f"• *{currency}*: {available} (terkunci: {locked})")
                has_balance = True
        if not has_balance:
            lines.append("Tidak ada saldo.")
    else:
        lines = [f"❌ Gagal mengambil saldo: {accounts}"]
    keyboard = [[InlineKeyboardButton("◀️ Kembali", callback_data="back_to_main")]]
    await query.edit_message_text("\n".join(lines), parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== MAIN ==========
def main():
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN tidak ditemukan!")
        return
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(menu_|ob_|back_to_main)"))
    logger.info("Bot started. Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()
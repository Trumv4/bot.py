import os
import re
import subprocess
import requests
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters

BOT_TOKEN = '7661562599:AAG5AvXpwl87M5up34-nj9AvMiJu-jYuWlA'  # 🔁 Thay bằng token thật
proxy_file = 'proxy.txt'
vps_file = 'vps.txt'

def tail(text):
    return f"{text}\n\nProxy By Phạm Anh Tú"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(tail("🤖 Bot đã sẵn sàng! Gửi lệnh hoặc proxy."))

async def check_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(proxy_file):
        await update.message.reply_text(tail("⚠️ Không có file proxy.txt"))
        return

    live, die = [], []
    with open(proxy_file) as f:
        proxies = [line.strip() for line in f if line.strip()]

    for proxy in proxies:
        try:
            parts = proxy.split(":")
            if len(parts) == 4:
                ip, port, user, pw = parts
                proxy_url = f"socks5h://{user}:{pw}@{ip}:{port}"
            else:
                ip, port = parts
                proxy_url = f"socks5h://{ip}:{port}"

            res = requests.get("http://ifconfig.me", proxies={"http": proxy_url, "https": proxy_url}, timeout=3)
            live.append(proxy) if res.status_code == 200 else die.append(proxy)
        except:
            die.append(proxy)

    msg = f"✅ Proxy Live: {len(live)}\n❌ Proxy Die: {len(die)}"
    await update.message.reply_text(tail(msg))

async def check_vps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(vps_file):
        await update.message.reply_text(tail("⚠️ Không có file vps.txt"))
        return

    live, die = [], []
    with open(vps_file) as f:
        ips = [line.strip() for line in f if line.strip()]

    for ip in ips:
        result = subprocess.run(["ping", "-c", "1", "-W", "1", ip],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        live.append(ip) if result.returncode == 0 else die.append(ip)

    msg = f"🖥️ VPS Live: {len(live)}\n❌ VPS Die: {len(die)}"
    await update.message.reply_text(tail(msg))

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    proxy_total = sum(1 for _ in open(proxy_file)) if os.path.exists(proxy_file) else 0
    vps_total = sum(1 for _ in open(vps_file)) if os.path.exists(vps_file) else 0

    msg = f"""📊 Thống kê hệ thống:
🔹 VPS: {vps_total}
🔹 Proxy: {proxy_total}"""
    await update.message.reply_text(tail(msg))

async def parse_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    pattern = r"➡️ ([\d\.]+:\d+)\n👤 ([^\n]+)\n🔑 ([^\n]+)"
    matches = re.findall(pattern, text)
    if not matches:
        return

    result = ""
    for i, (ip_port, user, pw) in enumerate(matches, 1):
        result += f"{i}. {ip_port}:{user}:{pw}\n"

    with open("proxy_buffer.txt", "w") as f:
        f.write(result.strip())

async def loc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists("proxy_buffer.txt"):
        await update.message.reply_text(tail("❌ Chưa có proxy nào được lọc."))
        return

    with open("proxy_buffer.txt", "r") as f:
        content = f.read().strip()

    await update.message.reply_text(tail(content))

    keyboard = [
        [InlineKeyboardButton("🗑️ Xoá file proxy_buffer.txt", callback_data="delete_buffer")]
    ]
    await update.message.reply_text("❓ Bạn có muốn xoá danh sách đã gửi không?", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "delete_buffer":
        try:
            os.remove("proxy_buffer.txt")
            await query.edit_message_text("✅ Đã xoá proxy_buffer.txt\n\nProxy By Phạm Anh Tú")
        except:
            await query.edit_message_text("❌ Không thể xoá file.\n\nProxy By Phạm Anh Tú")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check_proxy", check_proxy))
    app.add_handler(CommandHandler("check_vps", check_vps))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("loc", loc))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), parse_proxy))
    app.add_handler(CallbackQueryHandler(handle_button))
    print("🤖 Bot đang chạy...")
    app.run_polling()

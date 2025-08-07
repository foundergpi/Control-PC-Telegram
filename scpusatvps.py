import os
import paramiko
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from dotenv import load_dotenv

# === Load .env ===
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_USER = int(os.getenv("USER_ID"))
COMMAND_FILE = "/root/controlpctelegram/command.txt"
STATUS_FILE = "/root/controlpctelegram/status.txt"
TERMUX_COMMAND_FILE = "/root/controlpctelegram/poweron/command.txt"

# === Konfigurasi SFTP untuk Termux ===
VPS_HOST = "localhost"
VPS_PORT = 22
VPS_USERNAME = "root"
VPS_PASSWORD = "servergpi"

# === Autentikasi User ===
def is_authorized(user_id):
    return user_id == ALLOWED_USER

def restricted(func):
    def wrapper(update: Update, context: CallbackContext):
        if not is_authorized(update.effective_user.id):
            update.message.reply_text("❌ Akses ditolak.")
            return
        return func(update, context)
    return wrapper

# === Menu Telegram ===
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("🔌 Shutdown", callback_data='confirm_shutdown')],
        [InlineKeyboardButton("🔁 Restart", callback_data='confirm_restart')],
        [InlineKeyboardButton("⚡ Power On", callback_data='nyalakan')],
        [InlineKeyboardButton("📡 Cek Status", callback_data='cek_status')],
        [InlineKeyboardButton("❌ Batal", callback_data='cancel')],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Kembali ke Menu", callback_data='back')]])

def get_confirm_menu(command):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Ya", callback_data=f"do_{command}"),
         InlineKeyboardButton("❌ Batal", callback_data='back')]
    ])

# === Command /start ===
@restricted
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Silakan pilih perintah:", reply_markup=get_main_menu())

# === Handler Tombol Inline ===
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    if not is_authorized(user_id):
        query.answer("❌ Tidak diizinkan.", show_alert=True)
        return

    query.answer()

    if data == "confirm_shutdown":
        query.edit_message_text("⚠️ Yakin ingin mematikan komputer?", reply_markup=get_confirm_menu("shutdown"))

    elif data == "confirm_restart":
        query.edit_message_text("⚠️ Yakin ingin merestart komputer?", reply_markup=get_confirm_menu("restart"))

    elif data == "do_shutdown":
        write_local_command("shutdown")
        query.edit_message_text("✅ Perintah *shutdown* dikirim.", parse_mode="Markdown", reply_markup=get_back_menu())

    elif data == "do_restart":
        write_local_command("restart")
        query.edit_message_text("✅ Perintah *restart* dikirim.", parse_mode="Markdown", reply_markup=get_back_menu())

    elif data == "nyalakan":
        result = send_command_to_termux("poweron")
        if result:
            query.edit_message_text("✅ Perintah *poweron* dikirim ke Termux.", parse_mode="Markdown", reply_markup=get_back_menu())
        else:
            query.edit_message_text("❌ Gagal kirim perintah ke Termux.", parse_mode="Markdown", reply_markup=get_back_menu())

    elif data == "cek_status":
        status = read_status()
        status_text = "🟢 Komputer *ONLINE* dan listener aktif." if status == "ONLINE" else "🔴 Komputer *OFFLINE* atau listener tidak aktif."
        query.edit_message_text(status_text, parse_mode="Markdown", reply_markup=get_back_menu())

    elif data == "back":
        query.edit_message_text("🔄 Kembali ke menu:", reply_markup=get_main_menu())

    elif data == "cancel":
        query.edit_message_text("❌ Dibatalkan oleh pengguna.")

    else:
        query.edit_message_text("⚠️ Perintah tidak dikenali.")

# === Fungsi Tambahan ===
def write_local_command(command):
    try:
        with open(COMMAND_FILE, "w") as f:
            f.write(command)
    except Exception as e:
        print(f"❌ Gagal menulis command.txt lokal: {e}")

def send_command_to_termux(command):
    try:
        transport = paramiko.Transport((VPS_HOST, VPS_PORT))
        transport.connect(username=VPS_USERNAME, password=VPS_PASSWORD)
        sftp = paramiko.SFTPClient.from_transport(transport)

        with sftp.file(TERMUX_COMMAND_FILE, 'w') as f:
            f.write(command)

        sftp.close()
        transport.close()
        print(f"✅ Perintah '{command}' dikirim ke Termux listener.")
        return True
    except Exception as e:
        print(f"❌ Gagal kirim ke Termux: {e}")
        return False

def read_status():
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r") as f:
                return f.read().strip()
        except:
            return "ERROR"
    return "OFF"

# === Jalankan Bot ===
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Bot Telegram aktif.")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

import paramiko
import os
import time
import requests

# === KONFIGURASI VPS ===
VPS_HOST = "#"
VPS_PORT = 22
VPS_USERNAME = "root"
VPS_PASSWORD = "#"
REMOTE_COMMAND_FILE = "/root/controlpctelegram/command.txt"
REMOTE_STATUS_FILE = "/root/controlpctelegram/status.txt"

# === KONFIGURASI TELEGRAM ===
TELEGRAM_TOKEN = "#"
CHAT_ID = 12345678  # Ganti dengan ID Telegram kamu (INT)

# === Kirim pesan Telegram ===
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"❌ Gagal kirim ke Telegram: {e}")

# === Upload status ONLINE ke VPS ===
def upload_status_to_vps():
    try:
        transport = paramiko.Transport((VPS_HOST, VPS_PORT))
        transport.connect(username=VPS_USERNAME, password=VPS_PASSWORD)
        sftp = paramiko.SFTPClient.from_transport(transport)

        with sftp.file(REMOTE_STATUS_FILE, 'w') as f:
            f.write('ONLINE')

        sftp.close()
        transport.close()
        print("✅ Status ONLINE dikirim ke VPS")
    except Exception as e:
        print(f"❌ Gagal upload status ke VPS: {e}")

# === Ambil perintah dari VPS ===
def get_remote_command():
    try:
        transport = paramiko.Transport((VPS_HOST, VPS_PORT))
        transport.connect(username=VPS_USERNAME, password=VPS_PASSWORD)
        sftp = paramiko.SFTPClient.from_transport(transport)

        if file_exists(sftp, REMOTE_COMMAND_FILE):
            with sftp.file(REMOTE_COMMAND_FILE, "r") as remote_file:
                command = remote_file.read().decode("utf-8").strip()
            sftp.remove(REMOTE_COMMAND_FILE)
            print(f"📥 Dapat perintah: {command}")
            return command
        else:
            return None
    except Exception as e:
        print(f"❌ Gagal konek ke VPS: {e}")
        return None
    finally:
        try:
            sftp.close()
            transport.close()
        except:
            pass

# === Cek apakah file ada di VPS ===
def file_exists(sftp, path):
    try:
        sftp.stat(path)
        return True
    except FileNotFoundError:
        return False

# === Jalankan perintah dari VPS ===
def execute_command(command):
    if command == "shutdown":
        print("🔌 Menjalankan shutdown...")
        send_telegram_message("🔌 Komputer dimatikan via bot.")
        os.system("shutdown /s /t 1")
    elif command == "restart":
        print("🔁 Menjalankan restart...")
        send_telegram_message("🔁 Komputer direstart via bot.")
        os.system("shutdown /r /t 1")
    else:
        print("⚠️ Perintah tidak dikenali.")

# === MAIN ===
def main():
    print("🖥️ Listener aktif... menunggu perintah dari VPS...")
    send_telegram_message("✅ Listener PC lokal aktif. Komputer sudah menyala.")
    upload_status_to_vps()  # Upload status ONLINE ke VPS

    while True:
        command = get_remote_command()
        if command:
            execute_command(command)
        time.sleep(5)

if __name__ == "__main__":
    main()


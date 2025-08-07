
# 🖥️ Telegram PC Control – Wake-on-LAN & Remote Shutdown System

Sistem ini memungkinkan kamu **menghidupkan, mematikan, atau me-restart PC dari jarak jauh** menggunakan **Telegram Bot**, dengan bantuan **VPS sebagai relay**, serta **PC lokal dan HP Android (Termux)** sebagai listener.

---

## 🔧 Komponen Sistem

| Komponen | Deskripsi |
|----------|-----------|
| `scpusatvps.py` | Bot Telegram yang dijalankan di VPS untuk menerima perintah dan mengirimkannya ke PC lokal atau HP Android |
| `pclokal.py` | Listener di PC lokal (Windows/Linux) yang mengeksekusi perintah `shutdown` atau `restart` |
| `termux.sh` | Listener di HP Android (Termux) untuk mengirim magic packet (Wake-On-LAN) ke PC |
| `command.txt` & `status.txt` | File kontrol yang digunakan untuk komunikasi antar komponen melalui SFTP |

---

## 🧩 Arsitektur Sistem

```mermaid
graph TD
  User[🧑 Telegram User] -->|Perintah| Bot[🤖 Bot Telegram di VPS]
  Bot -->|command.txt| PC[💻 PC Lokal - Listener Python]
  Bot -->|command.txt (poweron)| Termux[📱 Termux - Wake-on-LAN]
  Termux -->|Magic Packet| PC
  PC -->|status.txt| VPS
  PC -->|Notifikasi| Telegram
```

---

## 📦 Persiapan

### 1. VPS (Virtual Private Server)
- Sudah terinstall Python, `paramiko`, dan `python-telegram-bot`
- Sudah punya akses root
- File yang dibutuhkan: `scpusatvps.py`, `.env` (untuk menyimpan token & user ID), folder `/root/controlpctelegram/`

### 2. PC Lokal
- Windows/Linux
- Sudah terinstall Python dan `paramiko`
- File yang dibutuhkan: `pclokal.py`

### 3. HP Android (opsional, untuk fitur *Power On*)
- Install **Termux**
- Sudah install `nc`, `openssh`, `xxd`
- File yang dibutuhkan: `termux.sh`

---

## 📁 Struktur Folder yang Dibutuhkan di VPS

```
/root/controlpctelegram/
├── command.txt        ← berisi perintah dari bot
├── status.txt         ← diisi "ONLINE" oleh PC lokal saat aktif
└── poweron/
    └── command.txt    ← dikirim perintah "poweron" ke Termux
```

---

## 🚀 Langkah Instalasi & Menjalankan

### A. Jalankan Bot Telegram di VPS

1. Buat file `.env`:
    ```
    BOT_TOKEN=token_bot_kamu
    USER_ID=1234567890
    ```

2. Install dependency:
    ```bash
    pip install python-telegram-bot python-dotenv paramiko
    ```

3. Jalankan bot:
    ```bash
    python3 scpusatvps.py
    ```

---

### B. Jalankan Listener di PC Lokal

1. Install dependency:
    ```bash
    pip install paramiko requests
    ```

2. Edit `pclokal.py`:
    - Ganti `VPS_HOST`, `VPS_PASSWORD`, `TELEGRAM_TOKEN`, dan `CHAT_ID`

3. Jalankan:
    ```bash
    python3 pclokal.py
    ```

> Komputer akan otomatis mengirim status `ONLINE` dan notifikasi Telegram saat listener aktif.

---

### C. Jalankan Listener Wake-on-LAN di Termux

1. Install dependency:
    ```bash
    pkg install openssh netcat xxd
    ```

2. Edit `termux.sh`:
    - Ganti `VPS_IP`, `MAC`, `BROADCAST_IP`, dan `DIRECT_IP` sesuai jaringanmu

3. Jalankan:
    ```bash
    bash termux.sh
    ```

---

## 📱 Cara Menggunakan

1. Buka chat Telegram dengan bot
2. Ketik `/start`
3. Gunakan tombol:
    - 🔌 Shutdown
    - 🔁 Restart
    - ⚡ Power On
    - 📡 Cek Status
4. Bot akan meminta konfirmasi sebelum mengirim perintah

---

## 🔐 Keamanan

- Bot hanya menerima perintah dari ID Telegram tertentu (`USER_ID`)
- File perintah akan dihapus setelah dibaca untuk mencegah eksekusi ulang
- Hindari menyimpan token dan password langsung di script — gunakan `.env` jika memungkinkan

---

## 📌 Catatan Tambahan

- Pastikan **PC mendukung Wake-On-LAN** dan sudah diaktifkan di BIOS/UEFI
- **WOL hanya bisa dijalankan dari jaringan lokal**, jadi HP dan PC harus terhubung ke WiFi yang sama
- Gunakan VPS yang stabil agar komunikasi lancar

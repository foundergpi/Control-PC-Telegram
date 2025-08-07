#!/data/data/com.termux/files/usr/bin/bash

# === KONFIGURASI VPS ===
VPS_IP="143.198.194.25"
VPS_USER="root"
REMOTE_COMMAND_FILE="/root/controlpctelegram/command.txt"

# === KONFIGURASI WAKE-ON-LAN ===
MAC="8C:16:45:86:39:0B"
BROADCAST_IP="192.168.1.255"     # Broadcast IP
DIRECT_IP="192.168.1.17"         # IP langsung ke PC
PORT=9                           # Port WOL umum

# Fungsi untuk mengirim magic packet
send_magic_packet() {
    local mac_clean=$(echo "$MAC" | tr -d ':' | tr 'a-f' 'A-F')
    local packet=$(printf 'FF%.0s' {1..6}; printf "$mac_clean%.0s" {1..16})
    
    echo "📡 Kirim broadcast ke $BROADCAST_IP:$PORT"
    echo "$packet" | xxd -r -p | nc -w1 -u "$BROADCAST_IP" "$PORT"

    echo "🎯 Kirim direct ke $DIRECT_IP:$PORT"
    echo "$packet" | xxd -r -p | nc -w1 -u "$DIRECT_IP" "$PORT"

    echo "✅ Magic packet dikirim ke MAC $MAC (broadcast + direct)"
}

# Fungsi cek perintah dari VPS
while true; do
    echo "🔍 Mengecek perintah dari VPS..."
    command=$(ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_IP" "cat $REMOTE_COMMAND_FILE 2>/dev/null && rm -f $REMOTE_COMMAND_FILE")

    if [[ "$command" == "poweron" ]]; then
        echo "📥 Perintah 'poweron' diterima!"
        send_magic_packet
    fi

    sleep 5
done

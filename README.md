# 🎙️ CodeAssistantKU

![Version](https://img.shields.io/badge/version-v1-blue?style=for-the-badge&logo=python)
![Mode](https://img.shields.io/badge/mode-HYBRID-red?style=for-the-badge&logo=shazam)
![Powered By](https://img.shields.io/badge/powered%20by-GROQ-orange?style=for-the-badge&logo=ai)
![Author](https://img.shields.io/badge/creator-SMALM-violet?style=for-the-badge&logo=github)

> **Asisten Coding AI Canggih dengan Dual Mode (Suara & Teks).**  
> Dibuat untuk programmer malas mengetik. Kirim perintah ke AI Chat tanpa mengangkat jari dari keyboard atau mouse.

---

## ⚡ Fitur Utama

1.  **🎤 Voice Mode (`Ctrl + Alt + X`)**
    - Rekam suara Anda secara instan.
    - Konversi ke teks menggunakan **Groq Whisper** (Super Cepat & Akurat).
    - Otomatis dikirim ke Chat AI (Antigravity/VS Code) secara **Invisible**.

2.  **📝 Text Mode (`Ctrl + Alt + Q`)**
    - Malas bicara? Atau koneksi lemot?
    - Tulis perintah di editor kode Anda, awali dengan `//`.
    - Contoh: `// buatkan fungsi login`
    - Blok teks tersebut, tekan shortcut, dan *boom*! Terkirim.

3.  **🥷 Ninja Technology**
    - Tidak perlu Virtual Desktop lagi!
    - Menggunakan teknik **Window Transparency Abuse**.
    - Window AI akan dibawa ke depan secara **transparan (invisible)**, dipaste, lalu dikembalikan. Layar kerja Anda tetap bersih!

4.  **👻 Ghost Mode (`Ctrl + Alt + D` / `W`)**
    - Sembunyikan window Antigravity/VS Code sepenuhnya dari layar, Taskbar, dan Alt+Tab.
    - Munculkan kembali kapan saja dengan shortcut Wake Up (`Ctrl + Alt + W`).

---

## ⚠️ PERINGATAN KERAS & DISCLAIMER

> 🛑 **BACA DENGAN TELITI SEBELUM MENGGUNAKAN**

1.  **Jangan Gunakan Sembarangan**: Penggunaan alat ini untuk merekam percakapan orang lain tanpa izin adalah **ILEGAL**.
2.  **Tanggung Jawab**: Saya, **smalm**, selaku pembuat, **TIDAK BERTANGGUNG JAWAB** atas penyalahgunaan alat ini.
3.  **Use at Your Own Risk**: Risiko ditanggung penumpang.

**DENGAN MENGGUNAKAN TOOLS INI, ANDA SETUJU UNTUK BERTANGGUNG JAWAB PENUH.**

---

## 🛠️ Instalasi

1.  **Requirements**:
    - Windows 10/11
    - Python 3.8+
    - Mic yang berfungsi

2.  **Install Library**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Setup API Key**:
    - Buat file `config.txt`.
    - Isi dengan: `GROQ_API_KEY=gsk_kunci_rahasia_anda_disini`

---

## 🎮 Cara Penggunaan

### 🎤 Cara 1: Voice Mode (Suara)
1.  Pastikan VS Code (Antigravity) sudah terbuka (boleh di belakang layar).
2.  Tekan **`Ctrl + Alt + X`**.
3.  Bicara perintah Anda (misal: *"Ubah warna tombol jadi merah"*).
4.  Tekan **`Ctrl + Alt + X`** lagi untuk stop.
5.  Tunggu notifikasi terminal. Selesai.

### 📝 Cara 2: Text Mode (Ketik & Kirim)
1.  Di text editor (NetBeans/Notepad/Apapun), ketik perintah dengan awalan `//`.
    ```
    // buatkan saya landing page warna biru
    ```
2.  **Blok / Highlight** teks tersebut.
3.  Tekan **`Ctrl + Alt + Q`**.
4.  Tool akan otomatis:
    - Copy teks.
    - Bersihkan tanda `//`.
    - Kirim ke AI Chat secara diam-diam.

### 👻 Cara 3: Ghost Mode (Hide & Seek)
1.  **Hide**: Tekan **`Ctrl + Alt + D`** (Disappear) untuk menyembunyikan window Antigravity/VS Code dari Taskbar dan Alt+Tab secara total.
2.  **Show**: Tekan **`Ctrl + Alt + W`** (Wake Up) untuk memunculkannya kembali.
    > *Berguna jika ingin layar benar-benar bersih atau menyembunyikan "rahasia" seketika.*

---

## 💡 Troubleshooting

- **Gagal Paste?**: Pastikan VS Code tidak diminimize ke tray. Biarkan dia "Restored" di belakang window lain.
- **Window Menghilang?**: Jika VS Code jadi invisible dan tidak balik lagi, tekan **`F9`** (Tombol Darurat).
- **"Clipboard Kosong"?**: Saat tekan `Ctrl+Alt+Q`, **segera lepas** tombolnya agar tidak mengganggu proses copy otomatis.

---

## 👤 Credits

**Dibuat oleh smalm**  

---
*2026 © smalm. All rights reserved.*

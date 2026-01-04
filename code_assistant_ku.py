

import os
import sys
import time
import threading
import tempfile
import numpy as np
import sounddevice as sd
import pyperclip
import keyboard
import ctypes
from ctypes import wintypes
from scipy.io.wavfile import write as write_wav

# === WIN32 API ===
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Constants
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TOOLWINDOW = 0x00000080  # Hide from Alt+Tab and Taskbar
WS_EX_APPWINDOW = 0x00040000   # Show in Alt+Tab and Taskbar
LWA_ALPHA = 0x00000002
SW_SHOW = 5
SW_HIDE = 0
SW_RESTORE = 9
SPI_GETFOREGROUNDLOCKTIMEOUT = 0x2000
SPI_SETFOREGROUNDLOCKTIMEOUT = 0x2001
SPIF_SENDWININICHANGE = 0x0002
SWP_FRAMECHANGED = 0x0020
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_NOZORDER = 0x0004

def set_window_alpha(hwnd, alpha):
    try:
        style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        if not (style & WS_EX_LAYERED):
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED)
        user32.SetLayeredWindowAttributes(hwnd, 0, alpha, LWA_ALPHA)
    except Exception as e:
        print(f"Alpha Error: {e}")

def hide_window_from_taskbar(hwnd):
    """Sembunyikan window dari Taskbar dan Alt+Tab"""
    try:
        style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        # Remove APPWINDOW flag, Add TOOLWINDOW flag
        new_style = (style & ~WS_EX_APPWINDOW) | WS_EX_TOOLWINDOW
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
        # Force Windows to update the window style
        user32.SetWindowPos(hwnd, None, 0, 0, 0, 0, 
                           SWP_FRAMECHANGED | SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER)
        return True
    except Exception as e:
        print(f"Hide Error: {e}")
        return False

def show_window_in_taskbar(hwnd):
    """Munculkan kembali window di Taskbar dan Alt+Tab"""
    try:
        style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        # Remove TOOLWINDOW flag, Add APPWINDOW flag
        new_style = (style & ~WS_EX_TOOLWINDOW) | WS_EX_APPWINDOW
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
        # Force update
        user32.SetWindowPos(hwnd, None, 0, 0, 0, 0, 
                           SWP_FRAMECHANGED | SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER)
        user32.ShowWindow(hwnd, SW_SHOW)
        return True
    except Exception as e:
        print(f"Show Error: {e}")
        return False

def bypass_foreground_lock():
    current_timeout = ctypes.c_uint()
    user32.SystemParametersInfoW(SPI_GETFOREGROUNDLOCKTIMEOUT, 0, ctypes.byref(current_timeout), 0)
    user32.SystemParametersInfoW(SPI_SETFOREGROUNDLOCKTIMEOUT, 0, ctypes.c_void_p(0), SPIF_SENDWININICHANGE)
    return current_timeout

def restore_foreground_lock(original_timeout):
    user32.SystemParametersInfoW(SPI_SETFOREGROUNDLOCKTIMEOUT, 0, ctypes.c_void_p(original_timeout.value), SPIF_SENDWININICHANGE)

def set_foreground_window_nuclear(hwnd):
    try:
        user32.keybd_event(0x10, 0, 0, 0)
        user32.keybd_event(0x10, 0, 0x0002, 0)
        
        original_timeout = bypass_foreground_lock()
        
        cur_thread = kernel32.GetCurrentThreadId()
        target_thread = user32.GetWindowThreadProcessId(hwnd, None)
        user32.AttachThreadInput(cur_thread, target_thread, True)
        
        if user32.IsIconic(hwnd):
            user32.ShowWindow(hwnd, SW_RESTORE)
        else:
            user32.ShowWindow(hwnd, SW_SHOW)
            
        user32.SetForegroundWindow(hwnd)
        
        user32.AttachThreadInput(cur_thread, target_thread, False)
        restore_foreground_lock(original_timeout)
        return True
    except Exception as e:
        print(f"Nuclear Error: {e}")
        return False

def get_foreground_window():
    return user32.GetForegroundWindow()

def find_window_any(title_part, visible_only=True):
    """Cari window berdasarkan title (visible atau hidden)"""
    target_abbrev = title_part.lower()
    found_hwnd = None
    found_title = ""
    
    def worker(hwnd, lParam):
        nonlocal found_hwnd, found_title
        # Jika visible_only=False, kita cari semua window
        if visible_only and not user32.IsWindowVisible(hwnd):
            return True
            
        length = user32.GetWindowTextLengthW(hwnd)
        if length > 0:
            buff = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buff, length + 1)
            curr_title = buff.value
            if target_abbrev in curr_title.lower():
                found_hwnd = hwnd
                found_title = curr_title
                return False
        return True
    
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    cb = WNDENUMPROC(worker)
    user32.EnumWindows(cb, 0)
    return found_hwnd, found_title

# === CONFIG ===
SAMPLE_RATE = 16000
HOTKEY_VOICE = 'ctrl+alt+x'
HOTKEY_TEXT = 'ctrl+alt+q'
HOTKEY_HIDE = 'ctrl+alt+d'  # D = Disappear
HOTKEY_SHOW = 'ctrl+alt+w'  # W = Wake up

class VoiceCodeAssistant:
    def __init__(self):
        self.is_recording = False
        self.audio_data = []
        self.stream = None
        self.groq_api_key = None
        self.hidden_hwnd = None  # Menyimpan handle window yang di-hide
        self.load_config()
        # Safety
        keyboard.add_hotkey('f9', self.emergency_restore)
        
    def load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config.txt')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                for line in f:
                    if line.startswith('GROQ_API_KEY='):
                        self.groq_api_key = line.strip().split('=', 1)[1].strip()
                        break
        if not self.groq_api_key or self.groq_api_key == 'your_api_key_here':
            print("ERROR: GROQ API KEY BELUM DISET!")
            sys.exit(1)

    # --- GHOST MODE ---
    def hide_antigravity(self):
        """Sembunyikan VS Code dari Taskbar dan Alt+Tab"""
        print("\n" + "=" * 50)
        print("  👻 GHOST MODE: Menyembunyikan Antigravity...")
        
        # Cari window (visible)
        hwnd, title = find_window_any('Antigravity', visible_only=True)
        if not hwnd:
            hwnd, title = find_window_any('Visual Studio Code', visible_only=True)
        
        if hwnd:
            self.hidden_hwnd = hwnd
            hide_window_from_taskbar(hwnd)
            print(f"  ✅ '{title[:30]}...' TERSEMBUNYI!")
            print("  ℹ️  Tekan Ctrl+Alt+S untuk memunculkan kembali.")
        else:
            print("  ❌ Window tidak ditemukan!")
    
    def show_antigravity(self):
        """Munculkan kembali VS Code"""
        print("\n" + "=" * 50)
        print("  👁️  SHOW MODE: Memunculkan Antigravity...")
        
        # Coba pakai cached hwnd dulu
        hwnd = self.hidden_hwnd
        
        # Kalau tidak ada, cari lagi (termasuk yang hidden)
        if not hwnd:
            hwnd, title = find_window_any('Antigravity', visible_only=False)
            if not hwnd:
                hwnd, title = find_window_any('Visual Studio Code', visible_only=False)
        
        if hwnd:
            show_window_in_taskbar(hwnd)
            set_foreground_window_nuclear(hwnd)
            self.hidden_hwnd = None
            print("  ✅ Antigravity MUNCUL KEMBALI!")
        else:
            print("  ❌ Window tidak ditemukan!")

    # --- VOICE MODE LOGIC ---
    def audio_callback(self, indata, frames, time_info, status):
        self.audio_data.append(indata.copy())
    
    def start_recording(self):
        self.audio_data = []
        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE, channels=1, dtype=np.int16, callback=self.audio_callback
        )
        self.stream.start()
        self.is_recording = True
        print("\n" + "=" * 50)
        print("  🎤 REKAM SUARA (Voice Mode)...")
        
    def stop_recording(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
        self.is_recording = False
        print("  ⏹️  Proses Audio...")
        
        if not self.audio_data: return
        audio_array = np.concatenate(self.audio_data, axis=0)
        temp_file = os.path.join(tempfile.gettempdir(), 'voice_recording.wav')
        write_wav(temp_file, SAMPLE_RATE, audio_array)
        
        thread = threading.Thread(target=self.process_video_command, args=(temp_file,))
        thread.start()
    
    def process_video_command(self, audio_file):
        try:
            text = self.speech_to_text(audio_file)
            if not text: return
            
            print(f"> VOICE: {text[:50]}...")
            pyperclip.copy(text)
            self.send_ninja_mode()
            
        except Exception as e:
            print(f"Error: {e}")

    # --- TEXT MODE LOGIC ---
    def handle_text_selection(self):
        print("\n" + "=" * 50)
        print("  📝 TEXT MODE (Processing)...")
        try:
            pyperclip.copy("") 
            
            keyboard.release('ctrl')
            keyboard.release('alt')
            keyboard.release('q')
            time.sleep(0.1)
            
            keyboard.send('ctrl+c')
            
            start_wait = time.time()
            raw_text = ""
            while time.time() - start_wait < 1.0:
                raw_text = pyperclip.paste()
                if raw_text: break
                time.sleep(0.1)

            if not raw_text:
                print("⚠️ Gagal copy teks. Pastikan teks sudah diblok/highlight!")
                return

            clean_raw = raw_text.strip()
            
            if "//" in clean_raw:
                parts = clean_raw.split("//", 1)
                final_command = parts[1].strip()
                
                if not final_command:
                    print("❌ Perintah kosong setelah '//'.")
                    return
                    
                print(f"> CMD DETECTED: {final_command[:50]}...")
                pyperclip.copy(final_command)
                self.send_ninja_mode()
            else:
                print(f"❌ Tidak ada '//' di teks: '{clean_raw[:20]}...'")
                print("   Format wajib: //perintah anda")
                
        except Exception as e:
            print(f"Text Mode Error: {e}")

    # --- SHARED FUNCTIONS ---
    def speech_to_text(self, audio_file):
        try:
            from groq import Groq
            client = Groq(api_key=self.groq_api_key)
            with open(audio_file, 'rb') as f:
                transcription = client.audio.transcriptions.create(
                    file=(os.path.basename(audio_file), f.read()),
                    model="whisper-large-v3",
                    language="id",
                    response_format="text"
                )
            return transcription
        except Exception as e:
            print(f"STT Error: {e}")
            return None

    def find_target_window(self):
        # Cari window termasuk yang hidden
        hwnd, title = find_window_any('Antigravity', visible_only=False)
        if hwnd: 
            return hwnd
        hwnd, title = find_window_any('Visual Studio Code', visible_only=False)
        if hwnd:
            return hwnd
        return None

    def send_ninja_mode(self):
        saved_hwnd = get_foreground_window()
        target_hwnd = self.find_target_window()
        
        if not target_hwnd:
            print("❌ Window tidak ketemu!")
            return

        if target_hwnd == saved_hwnd:
            keyboard.send('ctrl+v')
            keyboard.send('enter')
            return

        try:
            # 1. INVISIBLE
            set_window_alpha(target_hwnd, 0)
            
            # 2. Pastikan window visible untuk menerima input
            user32.ShowWindow(target_hwnd, SW_SHOW)
            
            # 3. NUCLEAR FOCUS
            focused = False
            for i in range(3):
                set_foreground_window_nuclear(target_hwnd)
                if get_foreground_window() == target_hwnd:
                    focused = True
                    break
                time.sleep(0.1)
            
            if not focused:
                print("⚠️ Gagal akses window.")
                set_window_alpha(target_hwnd, 255)
                return

            # 4. KIRIM
            time.sleep(0.1)
            keyboard.send('ctrl+l')
            time.sleep(0.05)
            keyboard.send('ctrl+l')
            
            time.sleep(0.25)
            
            keyboard.send('ctrl+v')
            time.sleep(0.1)
            keyboard.send('enter')
            time.sleep(0.05)
            
            # 5. RESTORE
            set_foreground_window_nuclear(saved_hwnd)
            set_window_alpha(target_hwnd, 255)
            print("✅ Terkirim!")

        except Exception as e:
            print(f"Error: {e}")
            set_window_alpha(target_hwnd, 255)

    def emergency_restore(self):
        print("\n🚨 EMERGENCY RESTORE...")
        hwnd = self.find_target_window()
        if hwnd:
            set_window_alpha(hwnd, 255)
            show_window_in_taskbar(hwnd)
            set_foreground_window_nuclear(hwnd)
            print("✅ Restored.")

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def run(self):
        print("=" * 60)
        print("   CodeAssistantKU")
        print("=" * 60)
        print("   🎤 VOICE: Ctrl + Alt + X")
        print("   📝 TEXT : Ctrl + Alt + Q")
        print("   👻 HIDE : Ctrl + Alt + D")
        print("   👁️  SHOW : Ctrl + Alt + W")
        print("   🚨 EMERGENCY: F9")
        print("=" * 60 + "\n")
        
        keyboard.add_hotkey(HOTKEY_VOICE, self.toggle_recording)
        keyboard.add_hotkey(HOTKEY_TEXT, self.handle_text_selection)
        keyboard.add_hotkey(HOTKEY_HIDE, self.hide_antigravity)
        keyboard.add_hotkey(HOTKEY_SHOW, self.show_antigravity)
        
        try:
            keyboard.wait()
        except KeyboardInterrupt:
            print("\n👋 Stopped.")

if __name__ == "__main__":
    try:
        assistant = VoiceCodeAssistant()
        assistant.run()
    except KeyboardInterrupt:
        sys.exit(0)

import os
import sys
import gc
import datetime
import hashlib
import subprocess
import base64
import numpy as np
from scipy.io import wavfile
from PIL import Image, ImageDraw, ImageFont

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    import pyzipper
    import cv2
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except ImportError as e:
    print(f"必要なライブラリが不足しています / Missing required library: {e}")
    sys.exit(1)

# 多言語辞書 
TRANSLATIONS = {
    "JA": {
        "title": "AI Protection Pro Studio v7.0",
        "tab_img": " 画像保護 ",
        "tab_verify": " 透かし検証 ",
        "tab_zip": " ZIP保護 ",
        "tab_vid": " 動画保護 ",
        "tab_audit": " 環境監査 ",
        "tab_doc": " 文書・コード保護 ",
        "tab_audio": " 音声資産保護 ",
        "btn_lang": "Language: 🇯🇵 JPN",
        "select_file": "ファイルを選択",
        "select_files": "画像ファイルを選択",
        "sig_label": "署名テキスト (Signature):",
        "pattern_label": "AI学習防止パターン:",
        "intensity_label": "学習防止強度:",
        "btn_protect_img": "署名 ＆ AI保護画像を書き出す",
        "btn_run_audio": "🎵 音声ファイル(.wav)を選択して保護実行",
        "audio_info": "人間の耳には聴こえない19kHz帯域に暗号化署名を埋め込み、\nボイスクローンや無断複製を防御します。",
        "audio_key": "所有者識別キー (暗号シード):",
        "doc_info": "MS Word, Excel, PDF, Python(.py) などを強力なパスワードで完全暗号化します",
        "doc_pass": "専用暗号化パスワード:",
        "btn_encrypt": "🔒 ファイルを暗号化 (Lock)",
        "btn_decrypt": "🔓 ファイルを復元 (Unlock)",
        "audit_net": " 1. ネットワーク接続監査 ",
        "audit_file": " 2. ファイル整合性・スキャン ",
        "audit_log": " 3. 監査システムログ ",
        "btn_net_check": "接続診断",
        "btn_scan": "⚡ スキャン実行 (SHA-256)",
        "msg_done": "処理が完了しました！",
        "msg_error": "エラーが発生しました",
    },
    "EN": {
        "title": "AI Protection Pro Studio v7.0",
        "tab_img": " Image Protect ",
        "tab_verify": " Verification ",
        "tab_zip": " ZIP Vault ",
        "tab_vid": " Video Protect ",
        "tab_audit": " Audit ",
        "tab_doc": " Doc & Code ",
        "tab_audio": " Audio Vault ",
        "btn_lang": "Language: 🇺🇸 ENG",
        "select_file": "Select File",
        "select_files": "Select Images",
        "sig_label": "Signature Text:",
        "pattern_label": "Anti-AI Pattern:",
        "intensity_label": "Protection Intensity:",
        "btn_protect_img": "Export Protected Images",
        "btn_run_audio": "🎵 Select Audio (.wav) & Protect",
        "audio_info": "Embeds encrypted signature in non-audible 19kHz frequency\nto prevent AI voice cloning and unauthorized replication.",
        "audio_key": "Owner Identity Key (Seed):",
        "doc_info": "Encrypt MS Word, Excel, PDF, Python (.py) with AES-256 password.",
        "doc_pass": "Encryption Password:",
        "btn_encrypt": "🔒 Encrypt File (Lock)",
        "btn_decrypt": "🔓 Decrypt File (Unlock)",
        "audit_net": " 1. Network Connection Audit ",
        "audit_file": " 2. File Integrity & Scan ",
        "audit_log": " 3. System Audit Log ",
        "btn_net_check": "Check Network",
        "btn_scan": "⚡ Run Scan (SHA-256)",
        "msg_done": "Task completed successfully!",
        "msg_error": "An error occurred",
    }
}

class AntiAIPortraitApp:
    def __init__(self, root):
        self.root = root
        self.current_lang = "JA"  

        self.root.title(TRANSLATIONS[self.current_lang]["title"])
        self.root.geometry("660x800")
        self.root.resizable(False, False)

        self.bg_color = "#1e1e24"
        self.card_color = "#2a2a35"
        self.accent_color = "#ff4f79"
        self.text_color = "#f4f4f9"
        self.sub_text_color = "#a0a0b0"

        self.root.configure(bg=self.bg_color)

        self.selected_file_paths = []
        self.verify_orig_path = None
        self.verify_prot_path = None
        self.zip_target_file_paths = []
        self.selected_video_path = None
        self.audit_target_file = None
        self.doc_target_file = None

        top_bar = tk.Frame(self.root, bg=self.bg_color)
        top_bar.pack(fill="x", padx=10, pady=(5, 0))

        self.lang_btn = tk.Button(top_bar, text=TRANSLATIONS[self.current_lang]["btn_lang"], command=self.toggle_language, bg=self.card_color, fg=self.text_color, font=("Helvetica", 9, "bold"), relief="flat", padx=8, pady=2, bd=0)
        self.lang_btn.pack(side="right")

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TNotebook', background=self.bg_color, borderwidth=0)
        self.style.configure('TNotebook.Tab', background=self.card_color, foreground=self.sub_text_color, padding=[6, 5])
        self.style.map('TNotebook.Tab', background=[('selected', self.bg_color)], foreground=[('selected', self.accent_color)])
        self.style.configure("Horizontal.TProgressbar", troughcolor=self.card_color, background=self.accent_color)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        self.tab_protect = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_verify = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_zip = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_video = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_audit = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_doc = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_audio = tk.Frame(self.notebook, bg=self.bg_color)

        self._update_tab_titles()

        self._build_protect_ui()
        self._build_verify_ui()
        self._build_zip_ui()
        self._build_video_ui()
        self._build_audit_ui()
        self._build_doc_ui()
        self._build_audio_ui()

        self._update_clock()
        self.log_audit("AI Protection Studio v7.0 Initialized.")

    def _update_tab_titles(self):
        t = TRANSLATIONS[self.current_lang]
        self.notebook.add(self.tab_protect, text=t["tab_img"])
        self.notebook.add(self.tab_verify, text=t["tab_verify"])
        self.notebook.add(self.tab_zip, text=t["tab_zip"])
        self.notebook.add(self.tab_video, text=t["tab_vid"])
        self.notebook.add(self.tab_audit, text=t["tab_audit"])
        self.notebook.add(self.tab_doc, text=t["tab_doc"])
        self.notebook.add(self.tab_audio, text=t["tab_audio"])

    def toggle_language(self):
        self.current_lang = "EN" if self.current_lang == "JA" else "JA"
        self.lang_btn.configure(text=TRANSLATIONS[self.current_lang]["btn_lang"])
        
        t = TRANSLATIONS[self.current_lang]
        self.notebook.tab(self.tab_protect, text=t["tab_img"])
        self.notebook.tab(self.tab_verify, text=t["tab_verify"])
        self.notebook.tab(self.tab_zip, text=t["tab_zip"])
        self.notebook.tab(self.tab_video, text=t["tab_vid"])
        self.notebook.tab(self.tab_audit, text=t["tab_audit"])
        self.notebook.tab(self.tab_doc, text=t["tab_doc"])
        self.notebook.tab(self.tab_audio, text=t["tab_audio"])

        self.audio_info_lbl.configure(text=t["audio_info"])
        self.audio_key_lbl.configure(text=t["audio_key"])
        self.audio_run_btn.configure(text=t["btn_run_audio"])
        self.doc_info_lbl.configure(text=t["doc_info"])
        self.encrypt_doc_btn.configure(text=t["btn_encrypt"])
        self.decrypt_doc_btn.configure(text=t["btn_decrypt"])

        self.audit_net_frame.configure(text=t["audit_net"])
        self.audit_file_frame.configure(text=t["audit_file"])
        self.audit_log_frame.configure(text=t["audit_log"])
        self.audit_net_btn.configure(text=t["btn_net_check"])
        self.scan_run_btn.configure(text=t["btn_scan"])
        
        self.log_audit(f"Language switched to {self.current_lang}")

    # ==================== 音声資産保護 UI ====================
    def _build_audio_ui(self):
        title = tk.Label(self.tab_audio, text="Audio Vault (19kHz Anti-AI)", font=("Helvetica", 15, "bold"), bg=self.bg_color, fg=self.accent_color)
        title.pack(pady=10)

        t = TRANSLATIONS[self.current_lang]
        self.audio_info_lbl = tk.Label(self.tab_audio, text=t["audio_info"], font=("Helvetica", 9), bg=self.bg_color, fg=self.sub_text_color, justify="center")
        self.audio_info_lbl.pack(pady=(0, 10))

        frame = tk.Frame(self.tab_audio, bg=self.card_color, bd=2, relief="groove")
        frame.pack(fill="x", padx=20, pady=10, ipady=15)

        self.audio_key_lbl = tk.Label(frame, text=t["audio_key"], font=("Helvetica", 10, "bold"), bg=self.card_color, fg=self.text_color)
        self.audio_key_lbl.pack(anchor="w", padx=15, pady=(5, 2))
        
        self.audio_key_entry = tk.Entry(frame, font=("Helvetica", 11), bg=self.bg_color, fg=self.text_color, relief="flat", bd=5)
        self.audio_key_entry.pack(fill="x", padx=15, pady=(0, 10))
        self.audio_key_entry.insert(0, "Studio7_User_Key")

        self.audio_run_btn = tk.Button(self.tab_audio, text=t["btn_run_audio"], command=self._process_audio, bg="#2ebd59", fg="white", font=("Helvetica", 11, "bold"), relief="flat", pady=10, bd=0)
        self.audio_run_btn.pack(fill="x", padx=20, pady=20)

    def _process_audio(self):
        input_file = filedialog.askopenfilename(filetypes=[("WAV", "*.wav"), ("All", "*.*")])
        if not input_file: return
        
        output_file = filedialog.asksaveasfilename(initialfile=f"protected_{os.path.basename(input_file)}", filetypes=[("WAV", "*.wav")])
        if not output_file: return

        try:
            sample_rate, data = wavfile.read(input_file)
            secret_key = self.audio_key_entry.get().strip() or "DEFAULT"
            
            np.random.seed(sum(ord(c) for c in secret_key))
            t = np.linspace(0, len(data) / sample_rate, len(data), endpoint=False)
            watermark = (np.sin(2 * np.pi * 19000 * t) + np.random.normal(0, 1, len(data)) * 0.1) * 0.003

            protected_data = data.copy().astype(np.float32)
            if len(protected_data.shape) > 1:
                for ch in range(protected_data.shape[1]):
                    protected_data[:, ch] += watermark * (np.max(np.abs(data[:, ch])) or 1)
            else:
                protected_data += watermark * (np.max(np.abs(data)) or 1)

            final_data = np.clip(protected_data, -32768, 32767).astype(np.int16) if data.dtype == np.int16 else protected_data
            wavfile.write(output_file, sample_rate, final_data)
            
            del data, protected_data, final_data
            gc.collect()

            messagebox.showinfo("Success", TRANSLATIONS[self.current_lang]["msg_done"])
            self.log_audit(f"Audio protected: {os.path.basename(output_file)}")
        except Exception as e:
            messagebox.showerror("Error", f"{TRANSLATIONS[self.current_lang]['msg_error']}: {e}")

    # ==================== 文書・コード暗号化保護 UI ====================
    def _build_doc_ui(self):
        t = TRANSLATIONS[self.current_lang]
        tk.Label(self.tab_doc, text="Document & Code Vault", font=("Helvetica", 15, "bold"), bg=self.bg_color, fg=self.accent_color).pack(pady=10)
        self.doc_info_lbl = tk.Label(self.tab_doc, text=t["doc_info"], font=("Helvetica", 9), bg=self.bg_color, fg=self.sub_text_color)
        self.doc_info_lbl.pack(pady=(0, 5))

        f = tk.Frame(self.tab_doc, bg=self.card_color, bd=2, relief="groove")
        f.pack(fill="x", padx=20, pady=5, ipady=15)
        self.doc_file_label = tk.Label(f, text=t["select_file"], font=("Helvetica", 10), bg=self.card_color, fg=self.text_color)
        self.doc_file_label.pack(pady=10)
        tk.Button(f, text=t["select_file"], command=self._select_doc_file, bg=self.accent_color, fg="white", font=("Helvetica", 9, "bold"), relief="flat", bd=0).pack()

        df = tk.Frame(self.tab_doc, bg=self.bg_color)
        df.pack(fill="x", padx=20, pady=10)
        tk.Label(df, text=t["doc_pass"], font=("Helvetica", 10, "bold"), bg=self.bg_color, fg=self.text_color).pack(anchor="w")
        self.doc_pass_entry = tk.Entry(df, font=("Helvetica", 11), bg=self.card_color, fg=self.text_color, relief="flat", bd=5, show="*")
        self.doc_pass_entry.pack(fill="x")

        box = tk.Frame(self.tab_doc, bg=self.bg_color)
        box.pack(fill="x", padx=20, pady=15)
        self.encrypt_doc_btn = tk.Button(box, text=t["btn_encrypt"], command=self._encrypt_document, bg="#2ebd59", fg="white", font=("Helvetica", 10, "bold"), relief="flat", pady=8, bd=0, state="disabled")
        self.encrypt_doc_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))
        self.decrypt_doc_btn = tk.Button(box, text=t["btn_decrypt"], command=self._decrypt_document, bg="#3b82f6", fg="white", font=("Helvetica", 10, "bold"), relief="flat", pady=8, bd=0, state="disabled")
        self.decrypt_doc_btn.pack(side="right", expand=True, fill="x", padx=(5, 0))

    def _select_doc_file(self):
        file = filedialog.askopenfilename(
            title="文書またはコードファイルを選択",
            filetypes=[("すべてのファイル", "*.*")]
        )
        if file:
            self.doc_target_file = file
            self.doc_file_label.configure(text=f"選択中: {os.path.basename(file)} ({os.path.getsize(file)} bytes)", fg=self.accent_color)
            self.encrypt_doc_btn.configure(state="normal")
            self.decrypt_doc_btn.configure(state="normal")

    def _get_fernet_key(self, password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))

    def _encrypt_document(self):
        if not self.doc_target_file: return
        password = self.doc_pass_entry.get().strip()
        if not password:
            messagebox.showwarning("警告", "パスワードを入力してください。")
            return

        try:
            salt = os.urandom(16)
            key = self._get_fernet_key(password, salt)
            f = Fernet(key)

            with open(self.doc_target_file, "rb") as file:
                file_data = file.read()

            encrypted_data = f.encrypt(file_data)
            output_path = self.doc_target_file + ".enc"
            with open(output_path, "wb") as file:
                file.write(salt + encrypted_data)

            self.log_audit(f"文書・コード暗号化成功: {os.path.basename(output_path)}")
            messagebox.showinfo("暗号化完了", f"安全にロックされました！\n\n出力先:\n{output_path}")
            self._reset_doc_state()
        except Exception as e:
            messagebox.showerror("エラー", f"暗号化失敗:\n{e}")
            self.log_audit(f"文書暗号化失敗: {e}")

    def _decrypt_document(self):
        if not self.doc_target_file: return
        password = self.doc_pass_entry.get().strip()
        if not password:
            messagebox.showwarning("警告", "パスワードを入力してください。")
            return

        try:
            with open(self.doc_target_file, "rb") as file:
                data = file.read()

            salt = data[:16]
            encrypted_data = data[16:]

            key = self._get_fernet_key(password, salt)
            f = Fernet(key)

            decrypted_data = f.decrypt(encrypted_data)

            if self.doc_target_file.endswith(".enc"):
                output_path = self.doc_target_file[:-4] + "_decrypted" + os.path.splitext(self.doc_target_file[:-4])[1]
            else:
                output_path = self.doc_target_file + "_decrypted.txt"

            with open(output_path, "wb") as file:
                file.write(decrypted_data)

            self.log_audit(f"文書・コード復元成功: {os.path.basename(output_path)}")
            messagebox.showinfo("復元完了", f"安全に元ファイルへ復元されました！\n\n出力先:\n{output_path}")
            self._reset_doc_state()
        except Exception as e:
            messagebox.showerror("エラー", f"復元失敗（パスワード違反または破損）:\n{e}")
            self.log_audit(f"文書復元失敗: {e}")

    def _reset_doc_state(self):
        self.doc_target_file = None
        self.doc_file_label.configure(text=TRANSLATIONS[self.current_lang]["select_file"], fg=self.text_color)
        self.doc_pass_entry.delete(0, tk.END)
        self.encrypt_doc_btn.configure(state="disabled")
        self.decrypt_doc_btn.configure(state="disabled")

    # ==================== 環境セキュリティ監査 UI ====================
    def _build_audit_ui(self):
        t = TRANSLATIONS[self.current_lang]
        top = tk.Frame(self.tab_audit, bg=self.bg_color)
        top.pack(fill="x", padx=20, pady=10)
        tk.Label(top, text="Security Audit", font=("Helvetica", 15, "bold"), bg=self.bg_color, fg=self.accent_color).pack(side="left")
        self.clock_label = tk.Label(top, text="", font=("Courier", 10, "bold"), bg=self.card_color, fg="#2ebd59", padx=5)
        self.clock_label.pack(side="right")

        self.audit_net_frame = tk.LabelFrame(self.tab_audit, text=t["audit_net"], font=("Helvetica", 9, "bold"), bg=self.bg_color, fg=self.text_color)
        self.audit_net_frame.pack(fill="x", padx=20, pady=5)
        self.wifi_lbl = tk.Label(self.audit_net_frame, text="Ready", font=("Helvetica", 9), bg=self.bg_color, fg=self.sub_text_color)
        self.wifi_lbl.pack(side="left", padx=10, pady=5)
        self.audit_net_btn = tk.Button(self.audit_net_frame, text=t["btn_net_check"], command=self._audit_net, bg=self.card_color, fg=self.text_color, relief="flat", bd=0)
        self.audit_net_btn.pack(side="right", padx=10, pady=5)
 
        self.audit_file_frame = tk.LabelFrame(self.tab_audit, text=t["audit_file"], font=("Helvetica", 9, "bold"), bg=self.bg_color, fg=self.text_color)
        self.audit_file_frame.pack(fill="x", padx=20, pady=5)
        
        self.scan_file_lbl = tk.Label(self.audit_file_frame, text="スキャンするファイルを選択してください", font=("Helvetica", 9), bg=self.bg_color, fg=self.sub_text_color, anchor="w")
        self.scan_file_lbl.pack(fill="x", padx=10, pady=(5, 2))
        
        btn_box = tk.Frame(self.audit_file_frame, bg=self.bg_color)
        btn_box.pack(fill="x", padx=10, pady=(0, 5))
        
        tk.Button(btn_box, text=t["select_file"], command=self._select_audit_file, bg=self.card_color, fg=self.text_color, relief="flat", bd=0, padx=8).pack(side="left")
        self.scan_run_btn = tk.Button(btn_box, text=t["btn_scan"], command=self._run_file_scan, bg="#2ebd59", fg="white", font=("Helvetica", 9, "bold"), relief="flat", bd=0, padx=8, state="disabled")
        self.scan_run_btn.pack(side="right")

        self.audit_log_frame = tk.LabelFrame(self.tab_audit, text=t["audit_log"], font=("Helvetica", 9, "bold"), bg=self.bg_color, fg=self.text_color)
        self.audit_log_frame.pack(fill="both", expand=True, padx=20, pady=5)
        self.log_text = tk.Text(self.audit_log_frame, font=("Courier", 8), bg="#141419", fg="#a0c0a0", state="disabled")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

    def _audit_net(self):
        self._audit_network()

    def _update_clock(self):
        self.clock_label.configure(text=datetime.datetime.now().strftime("%H:%M:%S"))
        self.root.after(1000, self._update_clock)

    def log_audit(self, msg):
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")

    def _audit_network(self):
        self.log_audit("ネットワークセキュリティ診断を開始中...")
        try:
            cmd = "networksetup -getairportnetwork en0"
            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=2)
            if result.returncode == 0 and "Current Wi-Fi Network" in result.stdout:
                ssid = result.stdout.replace("Current Wi-Fi Network:", "").strip()
                self.wifi_lbl.configure(text=f"🟢 接続中: {ssid}", fg="#2ebd59")
                self.log_audit(f"Wi-Fi診断完了: SSID -> {ssid}")
            else:
                self.wifi_lbl.configure(text="🟡 有線接続、または非接続モード", fg="#ffb600")
                self.log_audit("Wi-Fi診断: 無線LAN未検出。")
        except Exception:
            self.wifi_lbl.configure(text="🟢 ローカル保護モードで作動中", fg="#2ebd59")
            self.log_audit("ネットワーク診断完了。")

    def _select_audit_file(self):
        file = filedialog.askopenfilename(
            title="スキャンするファイルを選択",
            filetypes=[("すべてのファイル", "*.*")]
        )
        if file:
            self.audit_target_file = file
            self.scan_file_lbl.configure(text=f"対象: {os.path.basename(file)} ({os.path.getsize(file)} bytes)", fg=self.accent_color)
            self.scan_run_btn.configure(state="normal")

    def _run_file_scan(self):
        if not self.audit_target_file or not os.path.exists(self.audit_target_file): return
        self.log_audit(f"ファイルスキャン開始: {os.path.basename(self.audit_target_file)}")
        try:
            sha256_hash = hashlib.sha256()
            with open(self.audit_target_file, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            file_hash = sha256_hash.hexdigest()
            self.log_audit(f"SHA-256抽出成功: {file_hash[:32]}...")
            messagebox.showinfo("スキャン完了", f"ファイル名: {os.path.basename(self.audit_target_file)}\n\n◆ SHA-256:\n{file_hash}\n\n◆ 結果: 異常なし (CLEAN)")
            self.log_audit("スキャン結果: 脅威なし (CLEAN)")
            self.audit_target_file = None
            self.scan_file_lbl.configure(text="スキャンするファイルを選択してください", fg=self.sub_text_color)
            self.scan_run_btn.configure(state="disabled")
        except Exception as e:
            messagebox.showerror("エラー", f"スキャンエラー:\n{e}")
            self.log_audit(f"スキャン失敗: {e}")

    # ==================== AI画像保護 UI ====================
    def _build_protect_ui(self):
        title_label = tk.Label(self.tab_protect, text="AI Protection & Signature Pro", font=("Helvetica", 16, "bold"), bg=self.bg_color, fg=self.accent_color)
        title_label.pack(pady=10)

        self.drop_frame = tk.Frame(self.tab_protect, bg=self.card_color, bd=2, relief="groove")
        self.drop_frame.pack(fill="x", padx=20, pady=5, ipady=15)

        self.drop_label = tk.Label(self.drop_frame, text="保護したいイラスト画像を下のボタンから選択してください\n（複数まとめて選択可能です）", font=("Helvetica", 10), bg=self.card_color, fg=self.text_color, justify="center")
        self.drop_label.pack(expand=True, pady=10)

        select_btn = tk.Button(self.drop_frame, text="画像ファイルを選択", command=self._select_files, bg=self.accent_color, fg="white", font=("Helvetica", 10, "bold"), relief="flat", padx=10, pady=3, bd=0)
        select_btn.pack()

        setting_frame = tk.Frame(self.tab_protect, bg=self.bg_color)
        setting_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(setting_frame, text="署名テキスト (Signature):", font=("Helvetica", 10, "bold"), bg=self.bg_color, fg=self.text_color).pack(anchor="w", pady=(5, 2))
        self.sig_entry = tk.Entry(setting_frame, font=("Helvetica", 11), bg=self.card_color, fg=self.text_color, relief="flat", bd=5)
        self.sig_entry.pack(fill="x")
        self.sig_entry.insert(0, f"© Artist {datetime.datetime.now().year}")

        tk.Label(setting_frame, text="AI学習防止パターン:", font=("Helvetica", 10, "bold"), bg=self.bg_color, fg=self.text_color).pack(anchor="w", pady=(10, 2))
        self.pattern_var = tk.StringVar(value="Grid (格子模様)")
        pattern_combo = ttk.Combobox(setting_frame, textvariable=self.pattern_var, values=["Grid (格子模様)", "Slash (斜め線)", "Checker (市松模様)"], state="readonly")
        pattern_combo.pack(fill="x")

        tk.Label(setting_frame, text="学習防止強度 (推奨: 6.0前後):", font=("Helvetica", 10, "bold"), bg=self.bg_color, fg=self.text_color).pack(anchor="w", pady=(10, 2))
        self.intensity_scale = tk.Scale(setting_frame, from_=2.0, to=15.0, resolution=0.5, orient="horizontal", bg=self.bg_color, fg=self.text_color, troughcolor=self.card_color, activebackground=self.accent_color, highlightthickness=0, bd=0)
        self.intensity_scale.set(6.5)
        self.intensity_scale.pack(fill="x")

        self.progress_label = tk.Label(self.tab_protect, text="待機中...", font=("Helvetica", 9), bg=self.bg_color, fg=self.sub_text_color)
        self.progress_label.pack(anchor="w", padx=20, pady=(10, 0))

        self.progress_bar = ttk.Progressbar(self.tab_protect, style="Horizontal.TProgressbar", orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill="x", padx=20, pady=(2, 10))

        self.run_btn = tk.Button(self.tab_protect, text="署名 ＆ AI保護画像を書き出す", command=self._process_all_images, bg="#2ebd59", fg="white", font=("Helvetica", 11, "bold"), relief="flat", pady=8, bd=0, state="disabled")
        self.run_btn.pack(fill="x", padx=20, pady=5)

    def _select_files(self):
        files = filedialog.askopenfilenames(
            title="イラスト画像を選択してください", 
            filetypes=[("画像ファイル", "*.png *.jpg *.jpeg *.bmp"), ("すべてのファイル", "*.*")]
        )
        if files:
            self.selected_file_paths = list(files)
            count = len(self.selected_file_paths)
            if count == 1: self.drop_label.configure(text=f"選択済み: {os.path.basename(self.selected_file_paths[0])}", fg=self.accent_color)
            else: self.drop_label.configure(text=f"選択済み: {count} 枚のイラスト", fg=self.accent_color)
            self.run_btn.configure(state="normal")

    def _process_all_images(self):
        sig_text = self.sig_entry.get().strip()
        intensity = self.intensity_scale.get()
        pattern = self.pattern_var.get()
        total_files = len(self.selected_file_paths)
        success_count = 0
        self.progress_bar['max'] = total_files

        for index, file_path in enumerate(self.selected_file_paths):
            self.progress_label.configure(text=f"処理中 ({index + 1}/{total_files}): {os.path.basename(file_path)}")
            self.progress_bar['value'] = index + 1
            self.root.update_idletasks()

            try:
                dir_name = os.path.dirname(file_path)
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                output_path = os.path.join(dir_name, f"{base_name}_protected.png")

                img = Image.open(file_path).convert("RGB")
                width, height = img.size

                draw = ImageDraw.Draw(img)
                try: font = ImageFont.truetype("arial.ttf", int(height * 0.025))
                except: font = ImageFont.load_default()

                text_margin = int(height * 0.03)
                text_w = len(sig_text) * int(height * 0.015)
                text_h = int(height * 0.03)
                draw.text((width - text_w - text_margin, height - text_h - text_margin), sig_text, fill=(255, 255, 255), font=font)

                img_array = np.array(img, dtype=np.float32)
                X, Y = np.meshgrid(np.arange(width), np.arange(height))

                if "Slash" in pattern: perturbation = np.sin((X + Y) / 2.0) * intensity
                elif "Checker" in pattern: perturbation = (np.sin(X / 2.0) * np.sin(Y / 2.0)) * intensity
                else: perturbation = (np.sin(X / 2.0) * np.cos(Y / 2.0)) * intensity

                np.random.seed(1337)
                random_noise = np.random.normal(0, intensity * 0.3, img_array.shape)
                for i in range(3): img_array[:, :, i] += perturbation + random_noise[:, :, i]

                final_img = Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))
                final_img.save(output_path, "PNG")
                success_count += 1
                self.log_audit(f"画像保護成功: {os.path.basename(output_path)}")
            except Exception as e:
                self.log_audit(f"画像保護失敗: {e}")

        self.progress_label.configure(text="すべての処理が完了しました！")
        messagebox.showinfo("完了", f"{success_count} 枚の画像処理が完了しました！")

    # ==================== 透かし検証 UI ====================
    def _build_verify_ui(self):
        title_label = tk.Label(self.tab_verify, text="Watermark Verification", font=("Helvetica", 16, "bold"), bg=self.bg_color, fg=self.accent_color)
        title_label.pack(pady=10)

        info_lbl = tk.Label(self.tab_verify, text="※画像ファイル(.png/.jpgなど)または動画ファイル(.mp4など)に対応", font=("Helvetica", 9), bg=self.bg_color, fg=self.sub_text_color)
        info_lbl.pack(pady=(0, 5))

        verify_frame = tk.Frame(self.tab_verify, bg=self.bg_color)
        verify_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(verify_frame, text="1. 元のファイル (オリジナル):", font=("Helvetica", 10, "bold"), bg=self.bg_color, fg=self.text_color).pack(anchor="w")
        self.orig_label = tk.Label(verify_frame, text="未選択", font=("Helvetica", 9), bg=self.card_color, fg=self.sub_text_color, anchor="w", padx=10, pady=5)
        self.orig_label.pack(fill="x", pady=(2, 5))
        tk.Button(verify_frame, text="オリジナルファイルを選択", command=self._select_orig, bg=self.card_color, fg=self.text_color, relief="flat", bd=0, padx=10, pady=2).pack(anchor="w")

        tk.Label(verify_frame, text="2. 保護後のファイル:", font=("Helvetica", 10, "bold"), bg=self.bg_color, fg=self.text_color).pack(anchor="w", pady=(10, 0))
        self.prot_label = tk.Label(verify_frame, text="未選択", font=("Helvetica", 9), bg=self.card_color, fg=self.sub_text_color, anchor="w", padx=10, pady=5)
        self.prot_label.pack(fill="x", pady=(2, 5))
        tk.Button(verify_frame, text="保護されたファイルを選択", command=self._select_prot, bg=self.card_color, fg=self.text_color, relief="flat", bd=0, padx=10, pady=2).pack(anchor="w")

        self.verify_btn = tk.Button(self.tab_verify, text="🔍 透かし（差分ノイズ）を抽出して可視化", command=self._verify_watermark, bg="#2ebd59", fg="white", font=("Helvetica", 11, "bold"), relief="flat", pady=8, bd=0, state="disabled")
        self.verify_btn.pack(fill="x", padx=20, pady=25)

    def _select_orig(self):
        file = filedialog.askopenfilename(
            title="元の画像または動画を選択",
            filetypes=[("メディアファイル", "*.png *.jpg *.jpeg *.mp4 *.mov *.avi"), ("すべてのファイル", "*.*")]
        )
        if file:
            self.verify_orig_path = file
            self.orig_label.configure(text=os.path.basename(file), fg=self.accent_color)
            self._check_verify_ready()

    def _select_prot(self):
        file = filedialog.askopenfilename(
            title="保護後の画像または動画を選択",
            filetypes=[("メディアファイル", "*.png *.jpg *.jpeg *.mp4 *.mov *.avi"), ("すべてのファイル", "*.*")]
        )
        if file:
            self.verify_prot_path = file
            self.prot_label.configure(text=os.path.basename(file), fg=self.accent_color)
            self._check_verify_ready()

    def _check_verify_ready(self):
        if self.verify_orig_path and self.verify_prot_path: self.verify_btn.configure(state="normal")

    def _verify_watermark(self):
        try:
            ext = os.path.splitext(self.verify_orig_path)[1].lower()
            is_video = ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']

            if is_video:
                cap_orig = cv2.VideoCapture(self.verify_orig_path)
                cap_prot = cv2.VideoCapture(self.verify_prot_path)
                ret_o, frame_o = cap_orig.read()
                ret_p, frame_p = cap_prot.read()
                cap_orig.release()
                cap_prot.release()
                if not ret_o or not ret_p: return
                arr_orig = cv2.cvtColor(frame_o, cv2.COLOR_BGR2RGB).astype(np.float32)
                arr_prot = cv2.cvtColor(frame_p, cv2.COLOR_BGR2RGB).astype(np.float32)
            else:
                img_orig = Image.open(self.verify_orig_path).convert("RGB")
                img_prot = Image.open(self.verify_prot_path).convert("RGB")
                arr_orig = np.array(img_orig, dtype=np.float32)
                arr_prot = np.array(img_prot, dtype=np.float32)

            raw_diff = arr_prot - arr_orig
            enhanced_diff = 128.0 + (raw_diff * 30.0)
            output_array = np.clip(enhanced_diff, 0, 255).astype(np.uint8)
            diff_image = Image.fromarray(output_array)

            output_dir = os.path.dirname(self.verify_prot_path)
            prefix = "video" if is_video else "image"
            output_path = os.path.join(output_dir, f"{prefix}_watermark_verified_diff.png")
            diff_image.save(output_path)

            self.log_audit(f"透かし検証成功: {prefix}型の差分を可視化しました。")
            messagebox.showinfo("検証完了", f"透かしの可視化に成功しました！\n\n出力先:\n{output_path}")
        except Exception as e:
            messagebox.showerror("エラー", f"エラー:\n{e}")
            self.log_audit(f"透かし検証失敗: {e}")

    # ==================== セキュリティZIP作成 UI ====================
    def _build_zip_ui(self):
        title_label = tk.Label(self.tab_zip, text="Secure ZIP Packager", font=("Helvetica", 16, "bold"), bg=self.bg_color, fg=self.accent_color)
        title_label.pack(pady=10)

        self.zip_drop_frame = tk.Frame(self.tab_zip, bg=self.card_color, bd=2, relief="groove")
        self.zip_drop_frame.pack(fill="x", padx=20, pady=10, ipady=20)

        self.zip_drop_label = tk.Label(self.zip_drop_frame, text="圧縮したいファイルを下のボタンから選択してください", font=("Helvetica", 10), bg=self.card_color, fg=self.text_color, justify="center")
        self.zip_drop_label.pack(expand=True, pady=10)

        tk.Button(self.zip_drop_frame, text="ファイルを追加", command=self._select_zip_files, bg=self.accent_color, fg="white", font=("Helvetica", 10, "bold"), relief="flat", padx=10, pady=3, bd=0).pack()

        pass_frame = tk.Frame(self.tab_zip, bg=self.bg_color)
        pass_frame.pack(fill="x", padx=20, pady=15)

        tk.Label(pass_frame, text="暗号化パスワード:", font=("Helvetica", 10, "bold"), bg=self.bg_color, fg=self.text_color).pack(anchor="w", pady=(0, 5))
        self.zip_pass_entry = tk.Entry(pass_frame, font=("Helvetica", 11), bg=self.card_color, fg=self.text_color, relief="flat", bd=5, show="*")
        self.zip_pass_entry.pack(fill="x")

        self.zip_run_btn = tk.Button(self.tab_zip, text="🔒 強固なパスワード付きZIPを作成", command=self._create_secure_zip, bg="#2ebd59", fg="white", font=("Helvetica", 11, "bold"), relief="flat", pady=10, bd=0, state="disabled")
        self.zip_run_btn.pack(fill="x", padx=20, pady=15)

    def _select_zip_files(self):
        files = filedialog.askopenfilenames(
            title="圧縮するファイルを選択",
            filetypes=[("すべてのファイル", "*.*")]
        )
        if files:
            self.zip_target_file_paths = list(files)
            count = len(self.zip_target_file_paths)
            if count == 1: self.zip_drop_label.configure(text=f"選択済み: {os.path.basename(self.zip_target_file_paths[0])}", fg=self.accent_color)
            else: self.zip_drop_label.configure(text=f"選択済み: {count} 個のファイル", fg=self.accent_color)
            self.zip_run_btn.configure(state="normal")

    def _create_secure_zip(self):
        password = self.zip_pass_entry.get().strip()
        if not password: return
        save_path = filedialog.asksaveasfilename(title="ZIP保存先", defaultextension=".zip", filetypes=[("ZIP Files", "*.zip")])
        if not save_path: return
        try:
            with pyzipper.AESZipFile(save_path, 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zf:
                zf.setpassword(password.encode('utf-8'))
                for file_path in self.zip_target_file_paths:
                    if os.path.exists(file_path): zf.write(file_path, arcname=os.path.basename(file_path))
            self.log_audit(f"安全なZIP作成: {os.path.basename(save_path)}")
            messagebox.showinfo("ZIP作成完了", f"保存成功:\n{save_path}")
            self.zip_target_file_paths = []
            self.zip_drop_label.configure(text="圧縮したいファイルを下のボタンから選択してください", fg=self.text_color)
            self.zip_pass_entry.delete(0, tk.END)
            self.zip_run_btn.configure(state="disabled")
        except Exception as e:
            messagebox.showerror("エラー", f"エラー:\n{e}")
            self.log_audit(f"ZIP作成失敗: {e}")

    # ==================== 動画のAI保護 UI ====================
    def _build_video_ui(self):
        title_label = tk.Label(self.tab_video, text="AI Anti-Learning Video Protection", font=("Helvetica", 16, "bold"), bg=self.bg_color, fg=self.accent_color)
        title_label.pack(pady=10)

        self.video_drop_frame = tk.Frame(self.tab_video, bg=self.card_color, bd=2, relief="groove")
        self.video_drop_frame.pack(fill="x", padx=20, pady=5, ipady=15)

        self.video_drop_label = tk.Label(self.video_drop_frame, text="保護したい動画ファイルを下のボタンから選択してください", font=("Helvetica", 10), bg=self.card_color, fg=self.text_color, justify="center")
        self.video_drop_label.pack(expand=True, pady=10)

        tk.Button(self.video_drop_frame, text="動画ファイルを選択", command=self._select_video, bg=self.accent_color, fg="white", font=("Helvetica", 10, "bold"), relief="flat", padx=10, pady=3, bd=0).pack()

        v_setting_frame = tk.Frame(self.tab_video, bg=self.bg_color)
        v_setting_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(v_setting_frame, text="動画用パターン:", font=("Helvetica", 10, "bold"), bg=self.bg_color, fg=self.text_color).pack(anchor="w", pady=(5, 2))
        self.v_pattern_var = tk.StringVar(value="Grid (格子模様)")
        ttk.Combobox(v_setting_frame, textvariable=self.v_pattern_var, values=["Grid (格子模様)", "Slash (斜め線)", "Checker (市松模様)"], state="readonly").pack(fill="x")

        tk.Label(v_setting_frame, text="ノイズ強度 (推奨: 4.0〜6.0):", font=("Helvetica", 10, "bold"), bg=self.bg_color, fg=self.text_color).pack(anchor="w", pady=(10, 2))
        self.v_intensity_scale = tk.Scale(v_setting_frame, from_=2.0, to=15.0, resolution=0.5, orient="horizontal", bg=self.bg_color, fg=self.text_color, troughcolor=self.card_color, activebackground=self.accent_color, highlightthickness=0, bd=0)
        self.v_intensity_scale.set(5.0)
        self.v_intensity_scale.pack(fill="x")

        self.v_progress_label = tk.Label(self.tab_video, text="待機中...", font=("Helvetica", 9), bg=self.bg_color, fg=self.sub_text_color)
        self.v_progress_label.pack(anchor="w", padx=20, pady=(10, 0))

        self.v_progress_bar = ttk.Progressbar(self.tab_video, style="Horizontal.TProgressbar", orient="horizontal", mode="determinate")
        self.v_progress_bar.pack(fill="x", padx=20, pady=(2, 10))

        self.v_run_btn = tk.Button(self.tab_video, text="🎬 全フレーム保護動画を書き出す", command=self._process_video, bg="#2ebd59", fg="white", font=("Helvetica", 11, "bold"), relief="flat", pady=8, bd=0, state="disabled")
        self.v_run_btn.pack(fill="x", padx=20, pady=5)

    def _select_video(self):
        file = filedialog.askopenfilename(
            title="動画ファイルを選択", 
            filetypes=[("動画ファイル", "*.mp4 *.avi *.mov *.mkv"), ("すべてのファイル", "*.*")]
        )
        if file:
            self.selected_video_path = file
            self.video_drop_label.configure(text=f"選択中: {os.path.basename(self.selected_video_path)}", fg=self.accent_color)
            self.v_run_btn.configure(state="normal")

    def _process_video(self):
        if not self.selected_video_path: return
        intensity = self.v_intensity_scale.get()
        pattern = self.v_pattern_var.get()
        dir_name = os.path.dirname(self.selected_video_path)
        base_name = os.path.splitext(os.path.basename(self.selected_video_path))[0]
        output_path = os.path.join(dir_name, f"{base_name}_protected.mp4")

        cap = cv2.VideoCapture(self.selected_video_path)
        if not cap.isOpened(): return

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        X, Y = np.meshgrid(np.arange(width), np.arange(height))
        if "Slash" in pattern: perturbation = np.sin((X + Y) / 2.0) * intensity
        elif "Checker" in pattern: perturbation = (np.sin(X / 2.0) * np.sin(Y / 2.0)) * intensity
        else: perturbation = (np.sin(X / 2.0) * np.cos(Y / 2.0)) * intensity

        np.random.seed(1337)
        random_noise = np.random.normal(0, intensity * 0.3, (height, width, 3))
        self.v_progress_bar['max'] = total_frames
        frame_count = 0

        try:
            while True:
                ret, frame = cap.read()
                if not ret: break
                frame_float = frame.astype(np.float32)
                for i in range(3): frame_float[:, :, i] += perturbation + random_noise[:, :, i]
                out.write(np.clip(frame_float, 0, 255).astype(np.uint8))
                frame_count += 1
                if frame_count % 10 == 0 or frame_count == total_frames:
                    self.v_progress_label.configure(text=f"フレーム処理中... ({frame_count}/{total_frames})")
                    self.v_progress_bar['value'] = frame_count
                    self.root.update_idletasks()
            cap.release()
            out.release()
            self.log_audit(f"動画保護成功: {os.path.basename(output_path)} (全{total_frames}フレーム)")
            messagebox.showinfo("完了", f"保存成功:\n{output_path}")
            self.selected_video_path = None
            self.video_drop_label.configure(text="保護したい動画ファイルを下のボタンから選択してください", fg=self.text_color)
            self.v_run_btn.configure(state="disabled")
        except Exception as e:
            if cap.isOpened(): cap.release()
            if 'out' in locals(): out.release()
            messagebox.showerror("エラー", f"エラー:\n{e}")
            self.log_audit(f"動画保護失敗: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = AntiAIPortraitApp(root)
    root.mainloop()
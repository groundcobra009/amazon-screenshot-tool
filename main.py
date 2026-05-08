import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pathlib import Path

from config import Config
from kindle_controller import (
    find_kindle_window,
    activate_kindle,
    enter_fullscreen,
    send_page_key,
    exit_fullscreen,
)
from screenshot import capture_kindle_window, get_screenshot_path
from page_compare import images_are_same
from pdf_generator import generate_pdf


class KindleScreenshotApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Kindle Screenshot Tool")
        self.root.resizable(False, False)

        # 常に最前面に表示（Kindleの上にフローティング）
        self.root.attributes("-topmost", True)

        # ウィンドウを画面右上に配置（邪魔にならない位置）
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        self.root.geometry(f"+{screen_w - 480}+30")

        self.running = False
        self.stop_requested = False

        self._build_ui()
        self.root.mainloop()

    def _build_ui(self):
        frame = ttk.Frame(self.root, padding=20)
        frame.grid(row=0, column=0, sticky="nsew")

        # タイトル
        title = ttk.Label(frame, text="Kindle Screenshot Tool", font=("Helvetica", 16, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=(0, 15))

        # 画面サイズ
        ttk.Label(frame, text="Mac画面サイズ:").grid(row=1, column=0, sticky="w", pady=5)
        self.screen_var = tk.StringVar(value="14インチ")
        screen_combo = ttk.Combobox(
            frame, textvariable=self.screen_var, state="readonly", width=15,
            values=["13インチ", "14インチ", "15インチ", "16インチ"]
        )
        screen_combo.grid(row=1, column=1, sticky="w", pady=5)

        # めくり方向
        ttk.Label(frame, text="めくり方向:").grid(row=2, column=0, sticky="w", pady=5)
        self.direction_var = tk.StringVar(value="右めくり（← で次ページ）")
        dir_combo = ttk.Combobox(
            frame, textvariable=self.direction_var, state="readonly", width=22,
            values=["右めくり（← で次ページ）", "左めくり（→ で次ページ）"]
        )
        dir_combo.grid(row=2, column=1, sticky="w", pady=5)

        # 本の名前
        ttk.Label(frame, text="本の名前:").grid(row=3, column=0, sticky="w", pady=5)
        self.book_name_var = tk.StringVar()
        book_entry = ttk.Entry(frame, textvariable=self.book_name_var, width=25)
        book_entry.grid(row=3, column=1, sticky="w", pady=5)
        ttk.Label(frame, text="（空欄で自動命名）", font=("Helvetica", 10)).grid(
            row=4, column=1, sticky="w"
        )

        # 撮影ページ数
        ttk.Label(frame, text="撮影ページ数:").grid(row=5, column=0, sticky="w", pady=5)
        page_frame = ttk.Frame(frame)
        page_frame.grid(row=5, column=1, sticky="w", pady=5)
        self.max_pages_var = tk.StringVar(value="100")
        max_pages_entry = ttk.Entry(page_frame, textvariable=self.max_pages_var, width=8)
        max_pages_entry.pack(side="left")
        ttk.Label(page_frame, text=" ページ（0=自動停止）", font=("Helvetica", 10)).pack(side="left")

        # 待機時間
        ttk.Label(frame, text="ページ送り待機(秒):").grid(row=6, column=0, sticky="w", pady=5)
        self.wait_var = tk.StringVar(value="1.5")
        wait_entry = ttk.Entry(frame, textvariable=self.wait_var, width=8)
        wait_entry.grid(row=6, column=1, sticky="w", pady=5)

        # テスト撮影モード
        self.test_mode_var = tk.BooleanVar(value=False)
        test_check = ttk.Checkbutton(frame, text="テスト撮影（5枚のみ）", variable=self.test_mode_var)
        test_check.grid(row=7, column=0, columnspan=2, sticky="w", pady=5)

        # ボタン
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=8, column=0, columnspan=2, pady=10)

        self.start_btn = ttk.Button(btn_frame, text="撮影開始", command=self._on_start)
        self.start_btn.pack(side="left", padx=5)

        self.stop_btn = ttk.Button(btn_frame, text="停止", command=self._on_stop, state="disabled")
        self.stop_btn.pack(side="left", padx=5)

        # 使い方ガイド
        guide_sep = ttk.Separator(frame, orient="horizontal")
        guide_sep.grid(row=9, column=0, columnspan=2, sticky="ew", pady=5)

        guide_toggle = ttk.Button(frame, text="使い方ガイド ▼", command=self._toggle_guide)
        guide_toggle.grid(row=10, column=0, columnspan=2, sticky="w")
        self.guide_toggle_btn = guide_toggle

        self.guide_frame = ttk.Frame(frame)
        self.guide_frame.grid(row=11, column=0, columnspan=2, sticky="ew")
        self.guide_visible = False

        guide_text = (
            "【準備】\n"
            "  1. Amazon Kindleで本を開く\n"
            "  2. Kindleをフルスクリーンにする\n"
            "     (メニュー「表示」→「フルスクリーン」\n"
            "      または Cmd+Ctrl+F)\n"
            "  3. 最初のページ（表紙）に移動\n"
            "\n"
            "【設定のコツ】\n"
            "  ・横書き本 → 左めくり（→で次ページ）\n"
            "  ・縦書き本 → 右めくり（←で次ページ）\n"
            "  ・画像多めの本 → 待機時間を2〜3秒に\n"
            "  ・ページ数不明 → 0で自動停止\n"
            "\n"
            "【初回は必ずテスト撮影で確認！】\n"
            "  「テスト撮影」にチェック → 5枚で停止\n"
            "  screenshots/フォルダで画像を確認\n"
            "\n"
            "【権限エラーの場合】\n"
            "  システム設定 → プライバシーとセキュリティ\n"
            "  → アクセシビリティ & 画面収録\n"
            "  → ターミナルを許可（変更後は再起動）"
        )
        self.guide_label = tk.Text(
            self.guide_frame, width=42, height=20,
            font=("Menlo", 10), bg="#2a2a2a", fg="#cccccc",
            relief="flat", padx=8, pady=8, wrap="word"
        )
        self.guide_label.insert("1.0", guide_text)
        self.guide_label.config(state="disabled")
        # 初期は非表示
        self.guide_frame.grid_remove()

        # ステータス
        status_sep = ttk.Separator(frame, orient="horizontal")
        status_sep.grid(row=12, column=0, columnspan=2, sticky="ew", pady=5)

        self.status_var = tk.StringVar(value="待機中")
        ttk.Label(frame, text="状態:").grid(row=13, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.status_var, font=("Helvetica", 11, "bold")).grid(
            row=13, column=1, sticky="w"
        )

        self.page_var = tk.StringVar(value="0")
        ttk.Label(frame, text="ページ数:").grid(row=14, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.page_var).grid(row=14, column=1, sticky="w")

        # ログ
        ttk.Label(frame, text="ログ:").grid(row=15, column=0, sticky="nw", pady=(10, 0))
        self.log_text = tk.Text(frame, width=40, height=10, state="disabled", font=("Menlo", 10))
        self.log_text.grid(row=15, column=1, pady=(10, 0), sticky="w")

    def _toggle_guide(self):
        if self.guide_visible:
            self.guide_frame.grid_remove()
            self.guide_toggle_btn.config(text="使い方ガイド ▼")
        else:
            self.guide_frame.grid()
            self.guide_toggle_btn.config(text="使い方ガイド ▲")
        self.guide_visible = not self.guide_visible

    def _log(self, msg: str):
        self.root.after(0, self._append_log, msg)

    def _append_log(self, msg: str):
        self.log_text.config(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def _set_status(self, status: str):
        self.root.after(0, self.status_var.set, status)

    def _set_page(self, count: int):
        self.root.after(0, self.page_var.set, str(count))

    def _on_start(self):
        if self.running:
            return

        # Kindle確認
        if not find_kindle_window():
            messagebox.showerror("エラー", "Kindleアプリが起動していません。\nKindleを起動し、撮影したい本を開いてください。")
            return

        # 設定
        book_name = self.book_name_var.get().strip()
        if not book_name:
            book_name = datetime.now().strftime("book_%Y%m%d_%H%M%S")
        book_name = book_name.replace("/", "_").replace("\\", "_").replace(":", "_")

        direction = "left" if "右めくり" in self.direction_var.get() else "right"

        try:
            page_wait = float(self.wait_var.get())
        except ValueError:
            page_wait = 1.5

        screen_inch = int(self.screen_var.get().replace("インチ", ""))

        self.config = Config(
            page_direction=direction,
            mac_screen_inch=screen_inch,
            book_name=book_name,
            page_wait=page_wait,
        )
        self.config.book_screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

        self.test_mode = self.test_mode_var.get()

        try:
            self.max_pages = int(self.max_pages_var.get())
        except ValueError:
            self.max_pages = 0

        # UI状態変更
        self.running = True
        self.stop_requested = False
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

        # バックグラウンドで撮影開始
        thread = threading.Thread(target=self._capture_loop, daemon=True)
        thread.start()

    def _on_stop(self):
        self.stop_requested = True
        self._set_status("停止中...")
        self._log("停止リクエスト...")

    def _capture_loop(self):
        config = self.config

        try:
            self._set_status("Kindle準備中...")
            self._log("Kindleをアクティブ化...")
            activate_kindle()
            time.sleep(0.5)

            self._set_status("3秒後に撮影開始...")
            self._log("3秒後に撮影開始（Kindleを最大化しておいてください）...")
            time.sleep(3.0)

            self._set_status("撮影中")
            page_num = 1
            no_change_count = 0
            prev_path = None

            # ページ上限を決定
            if self.test_mode:
                page_limit = 5
                self._log("テスト撮影モード（5枚）")
            elif self.max_pages > 0:
                page_limit = self.max_pages
                self._log(f"撮影上限: {page_limit}ページ")
            else:
                page_limit = 0  # 0=無制限（自動停止のみ）
                self._log("自動停止モード（変化なしで停止）")

            while not self.stop_requested:
                # ページ上限チェック
                if page_limit > 0 and page_num > page_limit:
                    self._log(f"指定ページ数({page_limit})に到達。撮影完了。")
                    break

                current_path = get_screenshot_path(config.book_screenshot_dir, page_num)
                capture_kindle_window(current_path)
                self._log(f"[{page_num:04d}] {current_path.name}")
                self._set_page(page_num)

                if prev_path and prev_path.exists():
                    if images_are_same(prev_path, current_path, config.change_threshold):
                        # 描画が間に合っていない可能性 → 待ってから再撮影
                        self._log("  変化なし → 再確認中...")
                        time.sleep(1.5)
                        capture_kindle_window(current_path)

                        if images_are_same(prev_path, current_path, config.change_threshold):
                            no_change_count += 1
                            self._log(f"  変化なし確定 ({no_change_count}/{config.no_change_limit})")
                            if no_change_count >= config.no_change_limit:
                                for i in range(no_change_count):
                                    dup = get_screenshot_path(config.book_screenshot_dir, page_num - i)
                                    if dup.exists():
                                        dup.unlink()
                                self._log("最終ページ検出。撮影完了。")
                                break
                        else:
                            self._log("  ページ描画完了 → 続行")
                            no_change_count = 0
                    else:
                        no_change_count = 0

                prev_path = current_path
                page_num += 1

                # Kindleをアクティブにしてからキー送信
                activate_kindle()
                time.sleep(0.3)
                send_page_key(config.next_page_key())
                time.sleep(config.page_wait)

            total_pages = page_num - 1 - no_change_count
            self._set_page(total_pages)

            if total_pages > 0:
                self._set_status("PDF生成中...")
                self._log("PDF生成中...")
                output_path = generate_pdf(config.book_screenshot_dir, config.output_pdf_path)
                self._log(f"PDF完了: {output_path}")
                self._set_status("完了!")
                self.root.after(0, lambda: messagebox.showinfo(
                    "完了", f"撮影完了: {total_pages}ページ\nPDF: {output_path}"
                ))
            else:
                self._set_status("画像なし")
                self._log("撮影された画像がありません。")

        except Exception as e:
            self._log(f"エラー: {e}")
            self._set_status("エラー")
            self.root.after(0, lambda: messagebox.showerror("エラー", str(e)))

        finally:
            self.running = False
            self.root.after(0, lambda: self.start_btn.config(state="normal"))
            self.root.after(0, lambda: self.stop_btn.config(state="disabled"))


if __name__ == "__main__":
    KindleScreenshotApp()

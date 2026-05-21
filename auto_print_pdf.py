import os
import sys
import glob
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import win32print


def get_resource_path(filename):
    """取得資源檔案的正確路徑（支援 PyInstaller 打包後執行）"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


def get_printers():
    """取得系統中安裝的所有印表機清單"""
    printers = win32print.EnumPrinters(
        win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
    )
    return [printer[2] for printer in printers]


def build_print_settings(page_mode, custom_pages_str, duplex_mode):
    """
    組合 SumatraPDF 的 -print-settings 參數字串。

    page_mode:
        "all"    → 全部頁數
        "custom" → 自訂頁數（由 custom_pages_str 指定）

    duplex_mode:
        "simplex"      → 單面
        "duplex_long"  → 長邊雙面
        "duplex_short" → 短邊雙面

    回傳值為字串，例如 "1-3,5,duplexlong"；若無需任何設定則回傳空字串。
    """
    parts = []

    # 頁數部分
    if page_mode == "custom":
        pages = custom_pages_str.strip()
        if pages:
            parts.append(pages)
        # 若使用者留白，等同全部頁數，不加頁數參數

    # 雙面列印部分
    duplex_map = {
        "simplex": "",
        "duplex_long": "duplexlong",
        "duplex_short": "duplexshort",
    }
    duplex_param = duplex_map.get(duplex_mode, "")
    if duplex_param:
        parts.append(duplex_param)

    return ",".join(parts)


def print_pdfs(printer_name, pdf_folder, page_mode, custom_pages_str, duplex_mode):
    """將資料夾內所有 PDF 逐一發送至 SumatraPDF 進行列印"""
    pdf_files = sorted(glob.glob(os.path.join(pdf_folder, "*.pdf")))

    if not pdf_files:
        messagebox.showinfo("提示", "在所選資料夾內找不到任何 PDF 檔案。")
        return

    sumatra_path = get_resource_path("SumatraPDF.exe")
    if not os.path.exists(sumatra_path):
        messagebox.showerror(
            "錯誤",
            "找不到 SumatraPDF.exe！\n請確認程式完整性後重新下載。"
        )
        return

    print_settings = build_print_settings(page_mode, custom_pages_str, duplex_mode)

    success_count = 0
    failed_files = []

    for pdf in pdf_files:
        command = [sumatra_path, "-print-to", printer_name, "-silent"]
        if print_settings:
            command.extend(["-print-settings", print_settings])
        command.append(pdf)

        try:
            result = subprocess.run(
                command,
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=30
            )
            if result.returncode == 0:
                success_count += 1
            else:
                failed_files.append(os.path.basename(pdf))
        except subprocess.TimeoutExpired:
            failed_files.append(os.path.basename(pdf) + "（逾時）")
        except Exception as e:
            failed_files.append(f"{os.path.basename(pdf)}（{e}）")

    # 結果報告
    msg = f"已成功發送 {success_count} 個檔案至印表機：\n{printer_name}"
    if print_settings:
        msg += f"\n列印設定：{print_settings}"
    if failed_files:
        msg += f"\n\n以下 {len(failed_files)} 個檔案失敗：\n" + "\n".join(failed_files)
        messagebox.showwarning("部分完成", msg)
    else:
        messagebox.showinfo("完成", msg)


def main():
    printers = get_printers()
    if not printers:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("錯誤", "找不到任何印表機，請確認印表機已安裝。")
        root.destroy()
        return

    # ── 主視窗 ──────────────────────────────────────────
    root = tk.Tk()
    root.title("PDF 批次列印工具")
    root.geometry("460x400")
    root.resizable(False, False)
    root.eval('tk::PlaceWindow . center')

    FONT_NORMAL = ("微軟正黑體", 10)
    FONT_LABEL  = ("微軟正黑體", 11)

    # ── 印表機選擇 ───────────────────────────────────────
    tk.Label(root, text="印表機", font=FONT_LABEL).grid(
        row=0, column=0, sticky="w", padx=20, pady=(20, 4)
    )
    printer_var = tk.StringVar(value=win32print.GetDefaultPrinter())
    printer_cb = ttk.Combobox(
        root, textvariable=printer_var, values=printers,
        state="readonly", width=42, font=FONT_NORMAL
    )
    printer_cb.grid(row=1, column=0, columnspan=2, padx=20, sticky="w")

    # ── PDF 資料夾選擇 ────────────────────────────────────
    tk.Label(root, text="PDF 來源資料夾", font=FONT_LABEL).grid(
        row=2, column=0, sticky="w", padx=20, pady=(16, 4)
    )
    folder_frame = tk.Frame(root)
    folder_frame.grid(row=3, column=0, columnspan=2, padx=20, sticky="ew")

    folder_var = tk.StringVar(value=os.path.dirname(os.path.abspath(sys.argv[0])))
    folder_entry = tk.Entry(
        folder_frame, textvariable=folder_var,
        width=36, font=FONT_NORMAL, state="readonly"
    )
    folder_entry.pack(side="left")

    def browse_folder():
        chosen = filedialog.askdirectory(title="選擇 PDF 所在資料夾")
        if chosen:
            folder_var.set(chosen)

    tk.Button(
        folder_frame, text="瀏覽…", command=browse_folder,
        font=FONT_NORMAL
    ).pack(side="left", padx=(6, 0))

    # ── 列印頁數設定 ──────────────────────────────────────
    page_frame = tk.LabelFrame(
        root, text="列印頁數", font=FONT_LABEL, padx=10, pady=8
    )
    page_frame.grid(row=4, column=0, columnspan=2, padx=20, pady=(16, 0), sticky="ew")

    page_mode_var = tk.StringVar(value="all")

    def toggle_custom_entry():
        state = "normal" if page_mode_var.get() == "custom" else "disabled"
        custom_entry.config(state=state)

    tk.Radiobutton(
        page_frame, text="全部頁數", variable=page_mode_var,
        value="all", command=toggle_custom_entry, font=FONT_NORMAL
    ).grid(row=0, column=0, sticky="w")

    custom_row = tk.Frame(page_frame)
    custom_row.grid(row=1, column=0, sticky="w", pady=(4, 0))

    tk.Radiobutton(
        custom_row, text="自訂頁數：", variable=page_mode_var,
        value="custom", command=toggle_custom_entry, font=FONT_NORMAL
    ).pack(side="left")

    custom_entry = tk.Entry(custom_row, width=14, state="disabled", font=FONT_NORMAL)
    custom_entry.pack(side="left", padx=(0, 6))

    tk.Label(
        custom_row, text="（例：1-3,5）",
        font=("微軟正黑體", 9), fg="gray"
    ).pack(side="left")

    # ── 雙面列印設定 ──────────────────────────────────────
    duplex_frame = tk.LabelFrame(
        root, text="雙面列印", font=FONT_LABEL, padx=10, pady=8
    )
    duplex_frame.grid(row=5, column=0, columnspan=2, padx=20, pady=(10, 0), sticky="ew")

    duplex_options = [
        ("單面列印",    "simplex"),
        ("雙面－長邊翻頁（常用）", "duplex_long"),
        ("雙面－短邊翻頁",        "duplex_short"),
    ]
    duplex_var = tk.StringVar(value="simplex")
    duplex_cb = ttk.Combobox(
        duplex_frame,
        textvariable=duplex_var,
        values=[label for label, _ in duplex_options],
        state="readonly",
        width=30,
        font=FONT_NORMAL,
    )
    duplex_cb.current(0)
    duplex_cb.pack(anchor="w")

    def get_duplex_key():
        label = duplex_var.get()
        for lbl, key in duplex_options:
            if lbl == label:
                return key
        return "simplex"

    # ── 確認按鈕 ──────────────────────────────────────────
    def on_confirm():
        selected_printer = printer_var.get()
        pdf_folder = folder_var.get()
        if not selected_printer:
            messagebox.showwarning("警告", "請先選擇印表機。")
            return
        if not os.path.isdir(pdf_folder):
            messagebox.showwarning("警告", "請選擇有效的 PDF 資料夾。")
            return

        root.destroy()
        print_pdfs(
            printer_name=selected_printer,
            pdf_folder=pdf_folder,
            page_mode=page_mode_var.get(),
            custom_pages_str=custom_entry.get(),
            duplex_mode=get_duplex_key(),
        )

    tk.Button(
        root,
        text="▶  開始列印所有 PDF",
        command=on_confirm,
        font=("微軟正黑體", 12, "bold"),
        bg="#2e7d32", fg="white",
        activebackground="#1b5e20", activeforeground="white",
        relief="flat", padx=16, pady=8,
    ).grid(row=6, column=0, columnspan=2, pady=20)

    root.mainloop()


if __name__ == "__main__":
    main()

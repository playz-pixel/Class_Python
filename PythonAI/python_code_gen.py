import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import re
 
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
 
# Danh sach model uu tien — tu dong thu model tiep theo neu het quota
MODEL_LIST = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-2.5-flash",
    "gemini-1.5-flash-8b",
]
 
SYSTEM_PROMPT = """Ban la chuyen gia lap trinh Python.
Nhiem vu: Nhan yeu cau va tra ve DUNG MOT DOAN CODE PYTHON chay duoc.
Quy tac bat buoc:
- CHI tra ve code Python thuan tuy
- KHONG giai thich, KHONG markdown, KHONG backtick, KHONG ```python
- Code phai chay duoc ngay, dung input() neu can nhap lieu
- Code gon gang, ro rang, phu hop nguoi hoc
- Bat dau ngay bang dong code dau tien"""
 
 
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Code Generator - Gemini AI")
        self.root.geometry("960x760")
        self.root.configure(bg="#0f0f1a")
        self.root.resizable(True, True)
        self.client = None
        self._build_ui()
 
    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#0f0f1a")
        header.pack(fill="x", padx=20, pady=(16, 0))
        tk.Label(header, text="Python Code Generator",
                 font=("Consolas", 16, "bold"),
                 fg="#a9dc76", bg="#0f0f1a").pack(side="left")
        tk.Label(header, text="powered by Gemini AI",
                 font=("Consolas", 9),
                 fg="#585b70", bg="#0f0f1a").pack(side="left", padx=10, pady=4)
 
        # API Key
        key_frame = tk.Frame(self.root, bg="#1e1e2e", padx=12, pady=8)
        key_frame.pack(fill="x", padx=20, pady=(12, 0))
        tk.Label(key_frame, text="API Key:",
                 font=("Consolas", 10), fg="#cdd6f4",
                 bg="#1e1e2e").pack(side="left")
        self.api_var = tk.StringVar()
        self.api_entry = tk.Entry(
            key_frame, textvariable=self.api_var, show="*",
            font=("Consolas", 10), bg="#313244", fg="#cdd6f4",
            insertbackground="#a9dc76", relief="flat", width=42)
        self.api_entry.pack(side="left", padx=(8, 4), ipady=5)
        tk.Button(key_frame, text="Hien/An",
                  font=("Consolas", 9), bg="#313244", fg="#cdd6f4",
                  relief="flat", cursor="hand2",
                  command=self._toggle_key).pack(side="left", padx=(0, 8))
        tk.Button(key_frame, text=" Ket noi ",
                  font=("Consolas", 10, "bold"),
                  bg="#a9dc76", fg="#1e1e2e", relief="flat",
                  cursor="hand2", pady=4,
                  command=self._connect).pack(side="left")
        self.status_lbl = tk.Label(
            key_frame, text="Chua ket noi",
            font=("Consolas", 9), fg="#585b70", bg="#1e1e2e")
        self.status_lbl.pack(side="left", padx=10)
 
        # Model selector
        model_frame = tk.Frame(self.root, bg="#181825", padx=12, pady=6)
        model_frame.pack(fill="x", padx=20, pady=(4, 0))
        tk.Label(model_frame, text="Model:",
                 font=("Consolas", 9), fg="#a6adc8",
                 bg="#181825").pack(side="left")
        self.model_var = tk.StringVar(value=MODEL_LIST[0])
        model_menu = ttk.Combobox(
            model_frame, textvariable=self.model_var,
            values=MODEL_LIST, state="readonly",
            font=("Consolas", 9), width=28)
        model_menu.pack(side="left", padx=8)
        tk.Label(model_frame,
                 text="Neu loi 429: doi sang gemini-1.5-flash",
                 font=("Consolas", 8), fg="#585b70",
                 bg="#181825").pack(side="left", padx=8)
 
        # Divider
        tk.Frame(self.root, bg="#313244", height=1).pack(
            fill="x", padx=20, pady=10)
 
        # Input
        tk.Label(self.root, text="Nhap yeu cau bai lap trinh:",
                 font=("Consolas", 10, "bold"),
                 fg="#89b4fa", bg="#0f0f1a").pack(anchor="w", padx=22)
        self.inp = scrolledtext.ScrolledText(
            self.root, height=5,
            font=("Consolas", 11), bg="#1e1e2e", fg="#cdd6f4",
            insertbackground="#a9dc76", relief="flat",
            wrap="word", padx=12, pady=10)
        self.inp.pack(fill="x", padx=20, pady=(5, 0))
        self._placeholder_on()
        self.inp.bind("<FocusIn>",  self._ph_off)
        self.inp.bind("<FocusOut>", self._ph_on_if_empty)
 
        # Buttons
        btn_frame = tk.Frame(self.root, bg="#0f0f1a")
        btn_frame.pack(fill="x", padx=20, pady=10)
        self.gen_btn = tk.Button(
            btn_frame, text="Tao Code",
            font=("Consolas", 12, "bold"),
            bg="#cba6f7", fg="#1e1e2e", relief="flat",
            cursor="hand2", padx=22, pady=7,
            command=self._generate)
        self.gen_btn.pack(side="left")
        tk.Button(btn_frame, text="Xoa",
                  font=("Consolas", 10),
                  bg="#45475a", fg="#cdd6f4", relief="flat",
                  cursor="hand2", padx=14, pady=7,
                  command=self._clear).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Copy Code",
                  font=("Consolas", 10),
                  bg="#45475a", fg="#cdd6f4", relief="flat",
                  cursor="hand2", padx=14, pady=7,
                  command=self._copy).pack(side="left")
        self.info_lbl = tk.Label(
            btn_frame, text="",
            font=("Consolas", 10), fg="#f38ba8", bg="#0f0f1a")
        self.info_lbl.pack(side="left", padx=14)
 
        # Output
        tk.Label(self.root, text="Code Python tra ve:",
                 font=("Consolas", 10, "bold"),
                 fg="#a9dc76", bg="#0f0f1a").pack(anchor="w", padx=22)
        self.out = scrolledtext.ScrolledText(
            self.root, height=14,
            font=("Consolas", 11), bg="#181825", fg="#a9dc76",
            insertbackground="#a9dc76", relief="flat",
            wrap="none", padx=12, pady=10)
        self.out.pack(fill="both", expand=True, padx=20, pady=(5, 0))
 
        # Help bar
        help_bar = tk.Frame(self.root, bg="#11111b", padx=12, pady=4)
        help_bar.pack(fill="x", padx=20, pady=(4, 12))
        tk.Label(
            help_bar,
            text="Loi 429 = het quota  |  Doi model o tren  "
                 "|  Tao key moi: aistudio.google.com/apikey  "
                 "|  gemini-1.5-flash co 1500 req/ngay",
            font=("Consolas", 8), fg="#585b70", bg="#11111b"
        ).pack(side="left")
 
        if not GENAI_AVAILABLE:
            self._show_out(
                "Chua cai thu vien!\n\n"
                "Mo CMD / Terminal va chay lenh:\n\n"
                "    pip install google-genai\n\n"
                "Sau do khoi dong lai chuong trinh.")
 
    PH = "Vi du: Chuong trinh tinh tong tu 1 den n..."
 
    def _placeholder_on(self, _=None):
        self.inp.config(fg="#585b70")
        self.inp.delete("1.0", "end")
        self.inp.insert("1.0", self.PH)
 
    def _ph_off(self, _=None):
        if self.inp.get("1.0", "end-1c") == self.PH:
            self.inp.config(fg="#cdd6f4")
            self.inp.delete("1.0", "end")
 
    def _ph_on_if_empty(self, _=None):
        if not self.inp.get("1.0", "end-1c").strip():
            self._placeholder_on()
 
    def _toggle_key(self):
        self.api_entry.config(
            show="" if self.api_entry.cget("show") == "*" else "*")
 
    def _connect(self):
        key = self.api_var.get().strip()
        if not key:
            self._set_status("Nhap API key!", "#f38ba8")
            return
        if not GENAI_AVAILABLE:
            self._set_status("Chay: pip install google-genai", "#f38ba8")
            return
        try:
            self.client = genai.Client(api_key=key)
            self._set_status("Da ket noi Gemini", "#a9dc76")
        except Exception as e:
            self._set_status(f"Loi: {e}", "#f38ba8")
 
    def _set_status(self, msg, color):
        self.status_lbl.config(text=msg, fg=color)
 
    def _generate(self):
        if not self.client:
            self._show_out("Hay nhap API key va bam [Ket noi] truoc!")
            return
        req = self.inp.get("1.0", "end-1c").strip()
        if not req or req == self.PH:
            self._show_info("Nhap yeu cau truoc!", "#f9e2af")
            return
        model = self.model_var.get()
        self.gen_btn.config(state="disabled")
        self._show_info(f"Dang goi {model}...", "#89dceb")
        self.out.delete("1.0", "end")
        threading.Thread(
            target=self._call_api, args=(req, model), daemon=True).start()
 
    def _call_api(self, req, model):
        try:
            prompt = f"{SYSTEM_PROMPT}\n\nYeu cau: {req}"
            resp = self.client.models.generate_content(
                model=model, contents=prompt)
            code = resp.text.strip()
            code = re.sub(r"^```(?:python)?\s*", "", code, flags=re.M)
            code = re.sub(r"```\s*$", "", code, flags=re.M).strip()
            self.root.after(0, self._done_ok, code, model)
        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err:
                self.root.after(0, self._try_fallback, req, model, err)
            else:
                self.root.after(0, self._done_err, err)
 
    def _try_fallback(self, req, failed_model, original_err):
        try:
            idx = MODEL_LIST.index(failed_model)
            next_models = MODEL_LIST[idx + 1:]
        except ValueError:
            next_models = []
 
        if not next_models:
            msg = (
                "Loi 429 - Het quota tat ca model!\n\n"
                "Cach khac phuc:\n"
                "  1. Doi den 0h gio My PST (quota reset moi ngay)\n"
                "  2. Tao API key moi tai: aistudio.google.com/apikey\n"
                "  3. Bat billing trong AI Studio (Tier 1 = nhieu quota hon)\n\n"
                f"Da thu: {', '.join(MODEL_LIST)}\n\n"
                f"Chi tiet loi:\n{original_err[:400]}"
            )
            self.root.after(0, self._done_err, msg)
            return
 
        next_model = next_models[0]
        self.root.after(
            0, lambda: self._show_info(
                f"{failed_model} het quota → thu {next_model}...", "#f9e2af"))
        self.root.after(0, lambda: self.model_var.set(next_model))
        threading.Thread(
            target=self._call_api, args=(req, next_model), daemon=True).start()
 
    def _done_ok(self, code, model):
        self._show_out(code)
        self.gen_btn.config(state="normal")
        self._show_info(f"Hoan thanh! (model: {model})", "#a9dc76")
        self.root.after(4000, lambda: self._show_info("", ""))
 
    def _done_err(self, err):
        if "429" in err or "RESOURCE_EXHAUSTED" in err or "Het quota" in err:
            msg = (
                "Loi 429 - Het quota mien phi!\n\n"
                "Cach khac phuc:\n"
                "  * Chon model khac trong o 'Model' o tren\n"
                "    -> gemini-1.5-flash co gioi han cao nhat (1500 req/ngay)\n"
                "  * Tao API key moi: aistudio.google.com/apikey\n"
                "  * Doi reset luc 0h gio My (PST)\n\n"
                f"Chi tiet:\n{err[:400]}"
            )
        elif "API_KEY" in err or "401" in err:
            msg = (
                "API key khong hop le!\n\n"
                "Kiem tra lai key tai: aistudio.google.com/apikey\n\n"
                f"Chi tiet: {err}"
            )
        else:
            msg = f"Loi ket noi:\n\n{err}"
        self._show_out(msg)
        self.gen_btn.config(state="normal")
        self._show_info("", "")
 
    def _show_out(self, text):
        self.out.delete("1.0", "end")
        self.out.insert("1.0", text)
 
    def _show_info(self, text, color="#f38ba8"):
        self.info_lbl.config(text=text, fg=color)
 
    def _clear(self):
        self._placeholder_on()
        self.out.delete("1.0", "end")
        self._show_info("", "")
 
    def _copy(self):
        code = self.out.get("1.0", "end-1c").strip()
        if code:
            self.root.clipboard_clear()
            self.root.clipboard_append(code)
            self._show_info("Da copy!", "#a9dc76")
            self.root.after(2500, lambda: self._show_info("", ""))
 
 
if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
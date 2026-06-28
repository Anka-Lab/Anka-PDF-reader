import tkinter as tk
from tkinter import filedialog, messagebox
import fitz  # PyMuPDF
from PIL import Image, ImageTk

class AnkaPDF:
    def __init__(self, root):
        self.root = root
        self.root.title("Anka PDF Görüntüleyici v1.0.0")
        self.root.geometry("1000x700")
        self.root.configure(bg="#2f3640")

        # PDF Değişkenleri
        self.pdf_doc = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_factor = 1.5
        self.dark_mode = False
        self.tk_img = None

        self.create_widgets()

    def create_widgets(self):
        # --- Yan Panel (Sidebar) ---
        self.sidebar = tk.Frame(self.root, bg="#1e272e", width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # İstenen değişiklik burada yapıldı: "Anka Araçları" -> "Anka PDF Reader"
        tk.Label(self.sidebar, text="Anka PDF Reader", bg="#1e272e", fg="#d2dae2", font=("Arial", 12, "bold")).pack(pady=20)

        # Sayfaya Git
        tk.Label(self.sidebar, text="Sayfaya Git:", bg="#1e272e", fg="white").pack(pady=5)
        self.entry_page = tk.Entry(self.sidebar, width=10, justify="center")
        self.entry_page.pack(pady=5)
        self.btn_go = tk.Button(self.sidebar, text="Git", command=self.go_to_page, bg="#0fb9b1", fg="white", bd=0, padx=10, pady=5)
        self.btn_go.pack(pady=5)

        # Karanlık Mod Butonu
        self.btn_dark = tk.Button(self.sidebar, text="🌙 Gece Modu", command=self.toggle_dark_mode, bg="#4b6584", fg="white", bd=0, padx=10, pady=5)
        self.btn_dark.pack(pady=30)

        # --- Ana İçerik Alanı ---
        self.main_frame = tk.Frame(self.root, bg="#2f3640")
        self.main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Üst Menü / Kontrol Paneli
        self.top_bar = tk.Frame(self.main_frame, bg="#353b48", height=50)
        self.top_bar.pack(fill=tk.X, side=tk.TOP)

        # Dosya Aç
        self.btn_open = tk.Button(self.top_bar, text="📁 Dosya Aç", command=self.open_pdf, bg="#fc5c65", fg="white", bd=0, padx=10, pady=5)
        self.btn_open.pack(side=tk.LEFT, padx=10, pady=10)

        # Gezinme
        self.btn_prev = tk.Button(self.top_bar, text="◀ Geri", command=self.prev_page, state=tk.DISABLED, bg="#718093", fg="white", bd=0, padx=10, pady=5)
        self.btn_prev.pack(side=tk.LEFT, padx=5, pady=10)

        self.lbl_page = tk.Label(self.top_bar, text="Sayfa: 0 / 0", bg="#353b48", fg="white", font=("Arial", 10, "bold"))
        self.lbl_page.pack(side=tk.LEFT, padx=10)

        self.btn_next = tk.Button(self.top_bar, text="İleri ▶", command=self.next_page, state=tk.DISABLED, bg="#718093", fg="white", bd=0, padx=10, pady=5)
        self.btn_next.pack(side=tk.LEFT, padx=5, pady=10)

        # Yakınlaştırma
        self.btn_zoom_out = tk.Button(self.top_bar, text="➖", command=self.zoom_out, state=tk.DISABLED, bg="#718093", fg="white", bd=0, padx=10, pady=5)
        self.btn_zoom_out.pack(side=tk.RIGHT, padx=5, pady=10)

        self.lbl_zoom = tk.Label(self.top_bar, text="150%", bg="#353b48", fg="white")
        self.lbl_zoom.pack(side=tk.RIGHT, padx=5)

        self.btn_zoom_in = tk.Button(self.top_bar, text="➕", command=self.zoom_in, state=tk.DISABLED, bg="#718093", fg="white", bd=0, padx=10, pady=5)
        self.btn_zoom_in.pack(side=tk.RIGHT, padx=10, pady=10)

        # --- PDF Gösterim Alanı (Canvas + Scrollbars) ---
        self.canvas_frame = tk.Frame(self.main_frame, bg="#2f3640")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.v_scroll = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.h_scroll = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas = tk.Canvas(self.canvas_frame, bg="#808e9b", yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.v_scroll.config(command=self.canvas.yview)
        self.h_scroll.config(command=self.canvas.xview)
        
        # Fare tekerleği ile kaydırma desteği
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def open_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Dosyaları", "*.pdf")])
        if file_path:
            try:
                self.pdf_doc = fitz.open(file_path)
                self.total_pages = len(self.pdf_doc)
                self.current_page = 0
                self.zoom_factor = 1.5
                self.show_page()
                self.update_controls()
            except Exception as e:
                messagebox.showerror("Hata", f"PDF yüklenirken bir hata oluştu:\n{e}")

    def show_page(self):
        if not self.pdf_doc:
            return

        page = self.pdf_doc.load_page(self.current_page)
        mat = fitz.Matrix(self.zoom_factor, self.zoom_factor)
        pix = page.get_pixmap(matrix=mat)

        if self.dark_mode:
            pix.invert_irect(pix.irect)
        
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        self.tk_img = ImageTk.PhotoImage(img)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        
        self.lbl_page.config(text=f"Sayfa: {self.current_page + 1} / {self.total_pages}")
        self.lbl_zoom.config(text=f"{int(self.zoom_factor * 100)}%")

    def update_controls(self):
        state = tk.NORMAL if self.pdf_doc else tk.DISABLED
        
        self.btn_zoom_in.config(state=state)
        self.btn_zoom_out.config(state=state)

        if self.current_page > 0:
            self.btn_prev.config(state=tk.NORMAL)
        else:
            self.btn_prev.config(state=tk.DISABLED)

        if self.current_page < self.total_pages - 1:
            self.btn_next.config(state=tk.NORMAL)
        else:
            self.btn_next.config(state=tk.DISABLED)

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.show_page()
            self.update_controls()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.show_page()
            self.update_controls()

    def zoom_in(self):
        if self.zoom_factor < 5.0:
            self.zoom_factor += 0.25
            self.show_page()

    def zoom_out(self):
        if self.zoom_factor > 0.5:
            self.zoom_factor -= 0.25
            self.show_page()

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.btn_dark.config(text="☀️ Gündüz Modu", bg="#f1c40f", fg="black")
        else:
            self.btn_dark.config(text="🌙 Gece Modu", bg="#4b6584", fg="white")
        
        if self.pdf_doc:
            self.show_page()

    def go_to_page(self):
        if not self.pdf_doc:
            return
        try:
            target = int(self.entry_page.get()) - 1
            if 0 <= target < self.total_pages:
                self.current_page = target
                self.show_page()
                self.update_controls()
            else:
                messagebox.showwarning("Geçersiz Sayfa", f"Lütfen 1 ile {self.total_pages} arasında bir sayı girin.")
        except ValueError:
            messagebox.showwarning("Hata", "Lütfen geçerli bir sayfa numarası girin.")

    def on_mousewheel(self, event):
        if self.pdf_doc:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

if __name__ == "__main__":
    root = tk.Tk()
    app = AnkaPDF(root)
    root.mainloop()
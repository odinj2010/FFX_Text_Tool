import os
import sys
import csv
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import struct

# Add current folder to sys.path to load ffx_codec
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

try:
    from ffx_codec import FFXCodec, FILE_RECORD_SIZES
except ImportError:
    # Fallback to copy the record size dictionary locally if import fails
    FILE_RECORD_SIZES = {
        "item_txt.bin": 16, "arms_txt.bin": 16, "status_txt.bin": 16, "summon_txt.bin": 16,
        "config_txt.bin": 16, "menu_txt.bin": 16, "mmain_txt.bin": 16, "name_txt.bin": 16,
        "save_txt.bin": 16, "btlend_txt.bin": 16, "btl_txt.bin": 16, "build_txt.bin": 16,
        "help_txt.bin": 16, "item.bin": 92, "command.bin": 92, "monmagic1.bin": 92,
        "monmagic2.bin": 92, "important.bin": 20, "panel.bin": 16, "a_ability.bin": 16,
        "monster1.bin": 128, "monster2.bin": 128, "monster3.bin": 128,
    }

CONFIG_FILE = os.path.join(script_dir, "ffx_text_tool_recent_files.json")

DAMAGE_FORMULAS = [
    (0x00, "None"),
    (0x01, "STR vs DEF"),
    (0x02, "STR ignore DEF"),
    (0x03, "MAG vs MDF"),
    (0x04, "MAG ignore MDF"),
    (0x05, "Ratio (Current/16)"),
    (0x06, "Fixed x50"),
    (0x07, "Healing"),
    (0x08, "Max/16"),
    (0x09, "Fixed x46~53"),
    (0x0D, "Ticks/16"),
    (0x0F, "Special MAG (ignore MDF)"),
    (0x10, "Fixed x User HP / 10"),
    (0x11, "Celestial HP-based"),
    (0x12, "Celestial MP-based"),
    (0x13, "Celestial Auron"),
    (0x15, "Fixed x Gil chosen / 10"),
    (0x16, "Fixed xKills"),
    (0x17, "Fixed x9999"),
]


class FFXTextToolGUI:
    def __init__(self, parent, is_embedded=False):
        self.parent = parent
        self.is_embedded = is_embedded
        self.root = parent.winfo_toplevel() if is_embedded else parent
        
        # Dark Theme Palette
        self.bg_color = "#121212"
        self.card_color = "#1e1e1e"
        self.accent_color = "#3b82f6"
        self.accent_hover = "#2563eb"
        self.text_color = "#e5e7eb"
        self.text_dim = "#9ca3af"
        self.border_color = "#374151"
        self.success_color = "#10b981"
        self.error_color = "#ef4444"
        
        if not is_embedded:
            self.root.title("FFX Text & Dialogue Editor")
            self.root.geometry("1100x680")
            self.root.minsize(900, 580)
            self.root.configure(bg=self.bg_color)
            
            # Apply TTK styles
            self.style = ttk.Style()
            self.style.theme_use("clam")
            
            self.style.configure(".", background=self.bg_color, foreground=self.text_color)
            self.style.configure("TFrame", background=self.bg_color)
            self.style.configure("TLabel", background=self.bg_color, foreground=self.text_color, font=("Segoe UI", 10))
            self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground=self.accent_color)
            self.style.configure("SubHeader.TLabel", font=("Segoe UI", 10, "italic"), foreground=self.text_dim)
            self.style.configure("TEntry", fieldbackground=self.card_color, foreground=self.text_color, 
                                 bordercolor=self.border_color, lightcolor=self.border_color, darkcolor=self.border_color)
            self.style.configure("TCombobox", fieldbackground=self.card_color, background=self.card_color, 
                                 foreground=self.text_color, arrowcolor=self.accent_color, bordercolor=self.border_color)
            self.style.map("TCombobox",
                           fieldbackground=[("readonly", self.card_color), ("disabled", self.card_color)],
                           foreground=[("readonly", self.text_color), ("disabled", self.text_dim)],
                           background=[("readonly", self.card_color), ("disabled", self.card_color), ("active", self.border_color)],
                           arrowcolor=[("disabled", self.text_dim), ("!disabled", self.accent_color)],
                           bordercolor=[("focus", self.accent_color), ("!focus", self.border_color)])
            
            # Notebook tabs
            self.style.configure("TNotebook", background=self.bg_color, borderwidth=0)
            self.style.configure("TNotebook.Tab", background=self.card_color, foreground=self.text_dim, 
                                 padding=[15, 6], font=("Segoe UI", 9, "bold"), borderwidth=1, bordercolor=self.border_color)
            self.style.map("TNotebook.Tab", 
                           background=[("selected", self.accent_color), ("active", self.border_color), ("", self.card_color)],
                           foreground=[("selected", "#ffffff"), ("active", self.text_color), ("", self.text_dim)])
            
            # Scrollbar Styling
            self.style.configure("Vertical.TScrollbar", background=self.card_color, troughcolor=self.bg_color, 
                                 bordercolor=self.border_color, arrowcolor=self.accent_color,
                                 lightcolor=self.border_color, darkcolor=self.border_color)
            self.style.map("Vertical.TScrollbar",
                           background=[("active", self.accent_color), ("pressed", self.accent_color), ("", self.card_color)],
                           arrowcolor=[("active", "#ffffff"), ("", self.accent_color)])
            self.style.configure("Horizontal.TScrollbar", background=self.card_color, troughcolor=self.bg_color, 
                                 bordercolor=self.border_color, arrowcolor=self.accent_color,
                                 lightcolor=self.border_color, darkcolor=self.border_color)
            self.style.map("Horizontal.TScrollbar",
                           background=[("active", self.accent_color), ("pressed", self.accent_color), ("", self.card_color)],
                           arrowcolor=[("active", "#ffffff"), ("", self.accent_color)])

            # Treeview Styling
            self.style.configure("Treeview", background=self.card_color, fieldbackground=self.card_color, 
                                 foreground=self.text_color, borderwidth=1, bordercolor=self.border_color,
                                 font=("Segoe UI", 9), rowheight=24)
            self.style.configure("Treeview.Heading", background=self.bg_color, foreground=self.accent_color,
                                 font=("Segoe UI", 9, "bold"), borderwidth=1, bordercolor=self.border_color)
            self.style.map("Treeview", 
                           background=[("selected", self.accent_color), ("!selected", self.card_color)],
                           foreground=[("selected", "#ffffff"), ("!selected", self.text_color)])

        # Active Data State
        self.codec = FFXCodec()
        self.records = []
        
        # Style the dropdown Listbox popup globally (white background, black text for high visibility on Windows)
        self.root.option_add("*TCombobox*Listbox.background", "#ffffff")
        self.root.option_add("*TCombobox*Listbox.foreground", "#000000")
        self.root.option_add("*TCombobox*Listbox.selectBackground", self.accent_color)
        self.root.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")
        self.root.option_add("*TCombobox*Listbox.font", ("Segoe UI", 10))

        # Safeguard bind to force dropdown Listbox colors (white background, black text) on Windows
        def on_combobox_click(event):
            def configure_listbox(retries=0):
                try:
                    popdown = str(event.widget) + ".popdown"
                    listbox = popdown + ".f.l"
                    if event.widget.tk.call("winfo", "exists", listbox):
                        event.widget.tk.call(
                            listbox, "configure",
                            "-background", "#ffffff",
                            "-foreground", "#000000",
                            "-selectbackground", self.accent_color,
                            "-selectforeground", "#ffffff",
                            "-font", "{Segoe UI} 10"
                        )
                    elif retries < 10:
                        event.widget.after(20, lambda: configure_listbox(retries + 1))
                except Exception:
                    if retries < 10:
                        event.widget.after(20, lambda: configure_listbox(retries + 1))
            event.widget.after(5, configure_listbox)

        self.root.bind_class("TCombobox", "<ButtonPress-1>", on_combobox_click, add="+")
        self.root.bind_class("TCombobox", "<Down>", on_combobox_click, add="+")
        self.min_idx = 0
        self.max_idx = 0
        self.magic_part = b""
        self.active_file_path = None
        self.active_file_name = None
        
        # Load Config
        self.config = self.load_config()
        
        self.create_widgets()
        
        # Auto-detect game directory
        self.auto_detect_directory()

    def load_config(self):
        config = {"recent_files": []}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    loaded = json.load(f)
                    config.update(loaded)
            except Exception:
                pass
        return config

    def save_config(self):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass

    def auto_detect_directory(self):
        # 1. Check saved config first
        config_path = self.config.get("master_path", "")
        if config_path and os.path.exists(config_path):
            self.ent_master_path.delete(0, tk.END)
            self.ent_master_path.insert(0, config_path)
            self.codec.ffx_master_path = config_path
            self.log(f"Loaded master folder from config: {config_path}")
            self.scan_localizations()
            return

        # 2. Fallback to auto-detect relative to script
        detected_path = os.path.abspath(os.path.join(script_dir, "..", "VBF Browser", "extracted", "ffx_ps2", "ffx", "master"))
        if os.path.exists(detected_path):
            self.ent_master_path.delete(0, tk.END)
            self.ent_master_path.insert(0, detected_path)
            self.codec.ffx_master_path = detected_path
            self.log(f"Auto-detected FFX extracted data folder: {detected_path}")
            self.scan_localizations()

    def log(self, text, tag=None):
        if self.is_embedded and hasattr(self.parent, "log"):
            # Redirect to unified toolbox log console
            self.parent.log(text, tag)
        else:
            # Standalone logger console print
            if hasattr(self, "txt_log") and self.txt_log:
                msg = str(text) + "\n"
                self.txt_log.insert(tk.END, msg, tag or "default")
                self.txt_log.see(tk.END)
            else:
                print(text)

    def clear_log(self):
        if self.is_embedded and hasattr(self.parent, "clear_log"):
            self.parent.clear_log()
        else:
            if hasattr(self, "txt_log") and self.txt_log:
                self.txt_log.delete("1.0", tk.END)

    def create_widgets(self):
        # Main Layout
        self.main_container = ttk.Frame(self.parent, padding=10)
        self.main_container.pack(fill="both", expand=True)
        
        # Grid layout: Top Bar, Middle Body, Bottom Console
        self.top_panel = ttk.LabelFrame(self.main_container, text=" FFX Game Directory Configuration ", padding=10)
        self.top_panel.pack(fill="x", side="top", pady=(0, 10))
        self.build_top_panel(self.top_panel)
        
        # Middle Body split into Left Panel (Selection & Settings) and Right Panel (Treeview & Editors)
        self.body_paned = ttk.PanedWindow(self.main_container, orient="horizontal")
        self.body_paned.pack(fill="both", expand=True, side="top")
        
        self.left_panel = ttk.Frame(self.body_paned, width=320, padding=(0, 0, 10, 0))
        self.body_paned.add(self.left_panel, weight=1)
        self.build_left_panel(self.left_panel)
        
        self.right_panel = ttk.Frame(self.body_paned, padding=(10, 0, 0, 0))
        self.body_paned.add(self.right_panel, weight=4)
        self.build_right_panel(self.right_panel)
        
        # Bottom Console (visible only if standalone)
        if not self.is_embedded:
            self.console_panel = ttk.LabelFrame(self.main_container, text=" Process Logs ", padding=5)
            self.console_panel.pack(fill="x", side="bottom", pady=(10, 0))
            
            self.txt_log = tk.Text(self.console_panel, bg="#0d0d0d", fg="#e5e7eb", font=("Consolas", 9), 
                                   height=6, wrap="word", relief="flat", highlightthickness=1, highlightbackground=self.border_color)
            self.txt_log.pack(fill="both", expand=True, side="left")
            
            # Tags
            self.txt_log.tag_config("success", foreground=self.success_color, font=("Consolas", 9, "bold"))
            self.txt_log.tag_config("error", foreground=self.error_color, font=("Consolas", 9, "bold"))
            self.txt_log.tag_config("info", foreground=self.accent_color, font=("Consolas", 9, "bold"))
            self.txt_log.tag_config("default", foreground="#e5e7eb")
            
            log_scroll = ttk.Scrollbar(self.console_panel, command=self.txt_log.yview)
            log_scroll.pack(fill="y", side="right")
            self.txt_log.config(yscrollcommand=log_scroll.set)

    def build_top_panel(self, frame):
        lbl = ttk.Label(frame, text="Master Folder:")
        lbl.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        self.ent_master_path = ttk.Entry(frame, width=70)
        self.ent_master_path.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        frame.columnconfigure(1, weight=1)
        
        btn_browse = tk.Button(frame, text="Browse...", command=self.browse_master_folder, bg=self.card_color, 
                               fg=self.text_color, relief="flat", activebackground=self.border_color, activeforeground=self.text_color)
        btn_browse.grid(row=0, column=2, padx=(0, 10))
        self.bind_hover(btn_browse)
        
        btn_scan = tk.Button(frame, text="Scan Directory", command=self.scan_localizations, bg=self.accent_color, 
                              fg="white", font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.accent_hover, activeforeground="white")
        btn_scan.grid(row=0, column=3)
        self.bind_hover(btn_scan, is_primary=True)

    def build_left_panel(self, frame):
        # Group 1: Localization & Charset
        lbl_group = ttk.LabelFrame(frame, text=" Localization Settings ", padding=10)
        lbl_group.pack(fill="x", side="top", pady=(0, 15))
        
        ttk.Label(lbl_group, text="Localization Folder:").pack(anchor="w", pady=(0, 5))
        self.cmb_local = ttk.Combobox(lbl_group, state="readonly")
        self.cmb_local.pack(fill="x", pady=(0, 10))
        self.cmb_local.bind("<<ComboboxSelected>>", self.on_localization_changed)
        
        ttk.Label(lbl_group, text="Charset Table:").pack(anchor="w", pady=(0, 5))
        self.cmb_charset = ttk.Combobox(lbl_group, state="readonly", values=["us", "jp", "ch", "kr"])
        self.cmb_charset.pack(fill="x", pady=(0, 5))
        self.cmb_charset.set("us")
        
        # Group 2: Binary Text File
        lbl_file_group = ttk.LabelFrame(frame, text=" Select Table File ", padding=10)
        lbl_file_group.pack(fill="both", expand=True, side="top")
        
        ttk.Label(lbl_file_group, text="Text Bin File:").pack(anchor="w", pady=(0, 5))
        self.cmb_bin_file = ttk.Combobox(lbl_file_group, state="readonly")
        self.cmb_bin_file.pack(fill="x", pady=(0, 15))
        self.cmb_bin_file.bind("<<ComboboxSelected>>", self.on_bin_file_selected)
        
        # Bulk Operations Buttons
        lbl_bulk = ttk.Label(lbl_file_group, text="Bulk Utilities:")
        lbl_bulk.pack(anchor="w", pady=(0, 5))
        
        btn_exp_csv = tk.Button(lbl_file_group, text="📥 Export CSV (Single/Batch)", command=self.export_csv, bg=self.card_color, 
                                 fg=self.text_color, font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.border_color, activeforeground=self.text_color)
        btn_exp_csv.pack(fill="x", pady=4)
        self.bind_hover(btn_exp_csv)
        
        btn_imp_csv = tk.Button(lbl_file_group, text="📤 Import CSV (Single/Batch)", command=self.import_csv, bg=self.card_color, 
                                 fg=self.text_color, font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.border_color, activeforeground=self.text_color)
        btn_imp_csv.pack(fill="x", pady=4)
        self.bind_hover(btn_imp_csv)

        btn_sr = tk.Button(lbl_file_group, text="🔍 Global Search & Replace", command=self.open_search_replace_dialog, bg=self.card_color, 
                                 fg=self.text_color, font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.border_color, activeforeground=self.text_color)
        btn_sr.pack(fill="x", pady=4)
        self.bind_hover(btn_sr)
        
        # Repack & Save Button
        btn_save = tk.Button(lbl_file_group, text="💾 Repack & Save .bin File", command=self.save_bin_file, bg=self.accent_color, 
                              fg="white", font=("Segoe UI", 10, "bold"), relief="flat", activebackground=self.accent_hover, activeforeground="white")
        btn_save.pack(fill="x", pady=(20, 0))
        self.bind_hover(btn_save, is_primary=True)

    def build_right_panel(self, frame):
        # Top Row: Search Filtering
        self.right_paned = ttk.PanedWindow(frame, orient="horizontal")
        self.right_paned.pack(fill="both", expand=True)
        
        # Left Pane: list and search
        self.list_pane = ttk.Frame(self.right_paned, padding=(0, 0, 5, 0))
        self.right_paned.add(self.list_pane, weight=1)
        
        search_frame = ttk.Frame(self.list_pane)
        search_frame.pack(fill="x", side="top", pady=(0, 10))
        
        ttk.Label(search_frame, text="🔍 Filter:").pack(side="left", padx=(0, 5))
        self.ent_search = ttk.Entry(search_frame)
        self.ent_search.pack(fill="x", expand=True, side="left")
        self.ent_search.bind("<KeyRelease>", self.filter_treeview)
        
        # Treeview list
        tree_frame = ttk.Frame(self.list_pane)
        tree_frame.pack(fill="both", expand=True, side="top")
        
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Description"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Description", text="Description")
        
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Name", width=120, anchor="w")
        self.tree.column("Description", width=220, anchor="w")
        
        self.tree.pack(fill="both", expand=True, side="left")
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_row_selected)
        
        tree_scroll = ttk.Scrollbar(tree_frame, command=self.tree.yview)
        tree_scroll.pack(fill="y", side="right")
        self.tree.config(yscrollcommand=tree_scroll.set)
        
        # Right Pane: Editor Notebook
        self.editor_pane = ttk.Frame(self.right_paned, padding=(5, 0, 0, 0))
        self.right_paned.add(self.editor_pane, weight=2)
        
        self.editor_notebook = ttk.Notebook(self.editor_pane)
        self.editor_notebook.pack(fill="both", expand=True)
        
        # Tab 1: Dialogue Text
        self.text_tab = ttk.Frame(self.editor_notebook, padding=10)
        self.editor_notebook.add(self.text_tab, text=" Dialogue Text ")
        self.build_text_tab(self.text_tab)
        
        # Tab 2: Gameplay Stats
        self.stats_tab = ttk.Frame(self.editor_notebook, padding=10)
        self.editor_notebook.add(self.stats_tab, text=" Gameplay Stats ")
        self.build_stats_tab(self.stats_tab)

    def build_text_tab(self, frame):
        frame.columnconfigure(1, weight=1)
        
        # Name
        ttk.Label(frame, text="Name:").grid(row=0, column=0, sticky="w", pady=5, padx=(0, 5))
        self.ent_name = ttk.Entry(frame)
        self.ent_name.grid(row=0, column=1, sticky="ew", pady=5)
        self.ent_name.bind("<KeyRelease>", lambda e: self.update_length_label())
        
        # S. Name
        ttk.Label(frame, text="Simplified Name:").grid(row=1, column=0, sticky="w", pady=5, padx=(0, 5))
        self.ent_sname = ttk.Entry(frame)
        self.ent_sname.grid(row=1, column=1, sticky="ew", pady=5)
        self.ent_sname.bind("<KeyRelease>", lambda e: self.update_length_label())
        
        # Desc
        ttk.Label(frame, text="Description:").grid(row=2, column=0, sticky="w", pady=5, padx=(0, 5))
        self.ent_desc = ttk.Entry(frame)
        self.ent_desc.grid(row=2, column=1, sticky="ew", pady=5)
        self.ent_desc.bind("<KeyRelease>", lambda e: self.update_length_label())
        
        # S. Desc
        ttk.Label(frame, text="Simplified Description:").grid(row=3, column=0, sticky="w", pady=5, padx=(0, 5))
        self.ent_sdesc = ttk.Entry(frame)
        self.ent_sdesc.grid(row=3, column=1, sticky="ew", pady=5)
        self.ent_sdesc.bind("<KeyRelease>", lambda e: self.update_length_label())
        
        # Spacer
        frame.rowconfigure(4, weight=1)
        
        # Bottom apply & length label
        bottom_row = ttk.Frame(frame)
        bottom_row.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        self.lbl_len_warn = ttk.Label(bottom_row, text="Bytes used: Name: 0 | Desc: 0", font=("Segoe UI", 9, "italic"), foreground=self.text_dim)
        self.lbl_len_warn.pack(side="left")
        
        btn_apply = tk.Button(bottom_row, text="Apply Dialogue Edits", command=self.apply_row_edits, bg=self.accent_color, 
                              fg="white", font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.accent_hover, activeforeground="white", padx=15, pady=4)
        btn_apply.pack(side="right")
        self.bind_hover(btn_apply, is_primary=True)

    def build_stats_tab(self, frame):
        self.stats_canvas = tk.Canvas(frame, borderwidth=0, highlightthickness=0, bg=self.bg_color)
        self.stats_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.stats_canvas.yview)
        self.stats_scroll_frame = ttk.Frame(self.stats_canvas)
        
        self.stats_scroll_frame.bind(
            "<Configure>",
            lambda e: self.stats_canvas.configure(scrollregion=self.stats_canvas.bbox("all"))
        )
        
        self.stats_canvas.create_window((0, 0), window=self.stats_scroll_frame, anchor="nw")
        self.stats_canvas.configure(yscrollcommand=self.stats_scrollbar.set)
        
        self.stats_canvas.pack(side="left", fill="both", expand=True)
        self.stats_scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel(event):
            self.stats_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.stats_scroll_frame.bind("<Enter>", lambda e: self.stats_canvas.bind_all("<MouseWheel>", _on_mousewheel))
        self.stats_scroll_frame.bind("<Leave>", lambda e: self.stats_canvas.unbind_all("<MouseWheel>"))

        self.build_stats_fields(self.stats_scroll_frame)

    def build_stats_fields(self, frame):
        self.stat_vars = {}
        
        # No stats label
        self.stats_none_label = ttk.Label(frame, text="No gameplay stats available for this file type.", font=("Segoe UI", 10, "italic"), foreground=self.text_dim)
        self.stats_none_label.pack(pady=20, padx=10)
        
        # Key Item Group
        self.grp_key_item = ttk.LabelFrame(frame, text=" Key Item Configuration ", padding=10)
        
        self.stat_vars["primer"] = tk.IntVar()
        ttk.Checkbutton(self.grp_key_item, text="Is Al Bhed Primer", variable=self.stat_vars["primer"]).grid(row=0, column=0, columnspan=2, sticky="w", pady=5)
        
        ttk.Label(self.grp_key_item, text="Ordering Index:").grid(row=1, column=0, sticky="w", pady=5)
        self.stat_vars["ordering"] = tk.StringVar(value="0")
        tk.Spinbox(self.grp_key_item, from_=0, to=255, textvariable=self.stat_vars["ordering"], width=10, bg=self.card_color, fg=self.text_color, buttonbackground=self.card_color).grid(row=1, column=1, sticky="w", pady=5, padx=5)
        
        ttk.Label(self.grp_key_item, text="Unknown Byte 12:").grid(row=2, column=0, sticky="w", pady=5)
        self.stat_vars["unk12"] = tk.StringVar(value="0")
        tk.Spinbox(self.grp_key_item, from_=0, to=255, textvariable=self.stat_vars["unk12"], width=10, bg=self.card_color, fg=self.text_color, buttonbackground=self.card_color).grid(row=2, column=1, sticky="w", pady=5, padx=5)
        
        # Ability / Item Group
        self.grp_ability = ttk.LabelFrame(frame, text=" Ability / Item Stats ", padding=10)
        
        ttk.Label(self.grp_ability, text="MP Cost:").grid(row=0, column=0, sticky="w", pady=5)
        self.stat_vars["mp_cost"] = tk.StringVar(value="0")
        tk.Spinbox(self.grp_ability, from_=0, to=255, textvariable=self.stat_vars["mp_cost"], width=8, bg=self.card_color, fg=self.text_color).grid(row=0, column=1, sticky="w", pady=5, padx=5)
        
        ttk.Label(self.grp_ability, text="OD Cost:").grid(row=0, column=2, sticky="w", pady=5, padx=(10, 0))
        self.stat_vars["od_cost"] = tk.StringVar(value="0")
        tk.Spinbox(self.grp_ability, from_=0, to=255, textvariable=self.stat_vars["od_cost"], width=8, bg=self.card_color, fg=self.text_color).grid(row=0, column=3, sticky="w", pady=5, padx=5)
        
        ttk.Label(self.grp_ability, text="Power:").grid(row=1, column=0, sticky="w", pady=5)
        self.stat_vars["power"] = tk.StringVar(value="0")
        tk.Spinbox(self.grp_ability, from_=0, to=255, textvariable=self.stat_vars["power"], width=8, bg=self.card_color, fg=self.text_color).grid(row=1, column=1, sticky="w", pady=5, padx=5)
        
        ttk.Label(self.grp_ability, text="Accuracy:").grid(row=1, column=2, sticky="w", pady=5, padx=(10, 0))
        self.stat_vars["accuracy"] = tk.StringVar(value="0")
        tk.Spinbox(self.grp_ability, from_=0, to=255, textvariable=self.stat_vars["accuracy"], width=8, bg=self.card_color, fg=self.text_color).grid(row=1, column=3, sticky="w", pady=5, padx=5)
        
        ttk.Label(self.grp_ability, text="Hit Count:").grid(row=2, column=0, sticky="w", pady=5)
        self.stat_vars["hit_count"] = tk.StringVar(value="1")
        tk.Spinbox(self.grp_ability, from_=0, to=255, textvariable=self.stat_vars["hit_count"], width=8, bg=self.card_color, fg=self.text_color).grid(row=2, column=1, sticky="w", pady=5, padx=5)
        
        ttk.Label(self.grp_ability, text="Formula:").grid(row=2, column=2, sticky="w", pady=5, padx=(10, 0))
        self.stat_vars["formula"] = tk.StringVar()
        self.cmb_formula = ttk.Combobox(self.grp_ability, textvariable=self.stat_vars["formula"], state="readonly", width=15)
        self.cmb_formula["values"] = [f"{name} ({hex(code)})" for code, name in DAMAGE_FORMULAS]
        self.cmb_formula.grid(row=2, column=3, sticky="w", pady=5, padx=5)
        
        # Elements Group
        self.grp_elements = ttk.LabelFrame(frame, text=" Elements ", padding=10)
        self.stat_vars["elem_fire"] = tk.IntVar()
        self.stat_vars["elem_ice"] = tk.IntVar()
        self.stat_vars["elem_thunder"] = tk.IntVar()
        self.stat_vars["elem_water"] = tk.IntVar()
        self.stat_vars["elem_holy"] = tk.IntVar()
        
        ttk.Checkbutton(self.grp_elements, text="Fire", variable=self.stat_vars["elem_fire"]).grid(row=0, column=0, sticky="w", padx=5)
        ttk.Checkbutton(self.grp_elements, text="Ice", variable=self.stat_vars["elem_ice"]).grid(row=0, column=1, sticky="w", padx=5)
        ttk.Checkbutton(self.grp_elements, text="Thunder", variable=self.stat_vars["elem_thunder"]).grid(row=0, column=2, sticky="w", padx=5)
        ttk.Checkbutton(self.grp_elements, text="Water", variable=self.stat_vars["elem_water"]).grid(row=0, column=3, sticky="w", padx=5)
        ttk.Checkbutton(self.grp_elements, text="Holy", variable=self.stat_vars["elem_holy"]).grid(row=0, column=4, sticky="w", padx=5)
        
        # Targeting Group
        self.grp_targeting = ttk.LabelFrame(frame, text=" Targeting ", padding=10)
        self.stat_vars["tgt_enabled"] = tk.IntVar()
        self.stat_vars["tgt_enemies"] = tk.IntVar()
        self.stat_vars["tgt_multi"] = tk.IntVar()
        self.stat_vars["tgt_self"] = tk.IntVar()
        self.stat_vars["tgt_either"] = tk.IntVar()
        self.stat_vars["tgt_dead"] = tk.IntVar()
        self.stat_vars["tgt_ranged"] = tk.IntVar()
        
        ttk.Checkbutton(self.grp_targeting, text="Enabled", variable=self.stat_vars["tgt_enabled"]).grid(row=0, column=0, sticky="w", padx=5)
        ttk.Checkbutton(self.grp_targeting, text="Enemies", variable=self.stat_vars["tgt_enemies"]).grid(row=0, column=1, sticky="w", padx=5)
        ttk.Checkbutton(self.grp_targeting, text="Multi-target", variable=self.stat_vars["tgt_multi"]).grid(row=0, column=2, sticky="w", padx=5)
        ttk.Checkbutton(self.grp_targeting, text="Self Only", variable=self.stat_vars["tgt_self"]).grid(row=0, column=3, sticky="w", padx=5)
        ttk.Checkbutton(self.grp_targeting, text="Either Team", variable=self.stat_vars["tgt_either"]).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Checkbutton(self.grp_targeting, text="Dead Only", variable=self.stat_vars["tgt_dead"]).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        ttk.Checkbutton(self.grp_targeting, text="Ranged", variable=self.stat_vars["tgt_ranged"]).grid(row=1, column=2, sticky="w", padx=5, pady=5)
        
        # Status Group
        self.grp_status = ttk.LabelFrame(frame, text=" Status Infliction Chances (0-255) ", padding=10)
        status_list = [
            ("Death", "st_death"), ("Zombie", "st_zombie"), ("Petrify", "st_petrify"), 
            ("Poison", "st_poison"), ("Confuse", "st_confuse"), ("Berserk", "st_berserk"), 
            ("Provoke", "st_provoke"), ("Threaten", "st_threaten"), ("Sleep", "st_sleep"), 
            ("Silence", "st_silence"), ("Darkness", "st_darkness"), ("Slow", "st_slow"), 
            ("Haste", "st_haste")
        ]
        for idx, (lbl, key) in enumerate(status_list):
            r = idx // 3
            c = (idx % 3) * 2
            ttk.Label(self.grp_status, text=f"{lbl}:").grid(row=r, column=c, sticky="w", pady=5, padx=(5 if c > 0 else 0, 0))
            self.stat_vars[key] = tk.StringVar(value="0")
            tk.Spinbox(self.grp_status, from_=0, to=255, textvariable=self.stat_vars[key], width=5, bg=self.card_color, fg=self.text_color).grid(row=r, column=c+1, sticky="w", pady=5, padx=5)
            
        # Unified Apply Button for Stats
        self.btn_apply_stats = tk.Button(frame, text="Apply Stats Changes", command=self.apply_stats_edits, bg=self.accent_color,
                                         fg="white", font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.accent_hover, activeforeground="white", padx=15, pady=4)

    def show_stats_group(self, file_name):
        self.stats_none_label.pack_forget()
        self.grp_key_item.pack_forget()
        self.grp_ability.pack_forget()
        self.grp_elements.pack_forget()
        self.grp_targeting.pack_forget()
        self.grp_status.pack_forget()
        self.btn_apply_stats.pack_forget()
        
        if file_name == "important.bin":
            self.grp_key_item.pack(fill="x", pady=5, padx=5)
            self.btn_apply_stats.pack(pady=10, padx=5, anchor="e")
        elif file_name in ["item.bin", "command.bin", "monmagic1.bin", "monmagic2.bin"]:
            self.grp_ability.pack(fill="x", pady=5, padx=5)
            self.grp_elements.pack(fill="x", pady=5, padx=5)
            self.grp_targeting.pack(fill="x", pady=5, padx=5)
            self.grp_status.pack(fill="x", pady=5, padx=5)
            self.btn_apply_stats.pack(pady=10, padx=5, anchor="e")
        else:
            self.stats_none_label.pack(pady=20, padx=10)

    def apply_stats_edits(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "No entry selected.")
            return
            
        entry_id = int(sel[0])
        record = next((r for r in self.records if r['id'] == entry_id), None)
        if not record:
            return
            
        file_name = self.active_file_name
        extra_bytes = bytearray(record.get('extra_bytes', b''))
        
        if file_name == "important.bin" and len(extra_bytes) >= 4:
            extra_bytes[0] = 1 if self.stat_vars["primer"].get() else 0
            extra_bytes[2] = max(0, min(255, int(self.stat_vars["unk12"].get() or 0)))
            extra_bytes[3] = max(0, min(255, int(self.stat_vars["ordering"].get() or 0)))
            record['extra_bytes'] = bytes(extra_bytes)
            self.log(f"Applied stats edits in-memory to Key Item ID {entry_id}.")
            
        elif file_name in ["item.bin", "command.bin", "monmagic1.bin", "monmagic2.bin"] and len(extra_bytes) >= 76:
            def set_b(offset, val):
                extra_bytes[offset - 0x10] = max(0, min(255, int(val)))
                
            set_b(0x25, self.stat_vars["mp_cost"].get() or 0)
            set_b(0x26, self.stat_vars["od_cost"].get() or 0)
            set_b(0x2A, self.stat_vars["power"].get() or 0)
            set_b(0x29, self.stat_vars["accuracy"].get() or 0)
            set_b(0x2B, self.stat_vars["hit_count"].get() or 0)
            
            f_str = self.cmb_formula.get()
            f_code = 0
            for code, name in DAMAGE_FORMULAS:
                if f"{name} ({hex(code)})" == f_str:
                    f_code = code
                    break
            set_b(0x28, f_code)
            
            elem = 0
            if self.stat_vars["elem_fire"].get(): elem |= 0x01
            if self.stat_vars["elem_ice"].get(): elem |= 0x02
            if self.stat_vars["elem_thunder"].get(): elem |= 0x04
            if self.stat_vars["elem_water"].get(): elem |= 0x08
            if self.stat_vars["elem_holy"].get(): elem |= 0x10
            set_b(0x2D, elem)
            
            tgt = 0
            if self.stat_vars["tgt_enabled"].get(): tgt |= 0x01
            if self.stat_vars["tgt_enemies"].get(): tgt |= 0x02
            if self.stat_vars["tgt_multi"].get(): tgt |= 0x04
            if self.stat_vars["tgt_self"].get(): tgt |= 0x08
            if self.stat_vars["tgt_either"].get(): tgt |= 0x20
            if self.stat_vars["tgt_dead"].get(): tgt |= 0x40
            if self.stat_vars["tgt_ranged"].get(): tgt |= 0x80
            set_b(0x1A, tgt)
            
            set_b(0x2E, self.stat_vars["st_death"].get() or 0)
            set_b(0x2F, self.stat_vars["st_zombie"].get() or 0)
            set_b(0x30, self.stat_vars["st_petrify"].get() or 0)
            set_b(0x31, self.stat_vars["st_poison"].get() or 0)
            set_b(0x36, self.stat_vars["st_confuse"].get() or 0)
            set_b(0x37, self.stat_vars["st_berserk"].get() or 0)
            set_b(0x38, self.stat_vars["st_provoke"].get() or 0)
            set_b(0x39, self.stat_vars["st_threaten"].get() or 0)
            set_b(0x3A, self.stat_vars["st_sleep"].get() or 0)
            set_b(0x3B, self.stat_vars["st_silence"].get() or 0)
            set_b(0x3C, self.stat_vars["st_darkness"].get() or 0)
            set_b(0x46, self.stat_vars["st_slow"].get() or 0)
            set_b(0x45, self.stat_vars["st_haste"].get() or 0)
            
            record['extra_bytes'] = bytes(extra_bytes)
            self.log(f"Applied stats edits in-memory to Ability/Item ID {entry_id}.")


    def browse_master_folder(self):
        folder = filedialog.askdirectory(title="Select Extracted FFX Master Folder")
        if folder:
            path = os.path.abspath(folder)
            self.config["master_path"] = path
            self.save_config()
            if hasattr(self, "parent") and self.parent and hasattr(self.parent, "update_global_master_path"):
                self.parent.update_global_master_path(path)
            else:
                self.ent_master_path.delete(0, tk.END)
                self.ent_master_path.insert(0, path)
                self.codec.ffx_master_path = path
                self.log(f"Set FFX Master folder: {path}")
                self.scan_localizations()

    def scan_localizations(self):
        path = self.ent_master_path.get().strip()
        if not path or not os.path.exists(path):
            messagebox.showerror("Error", "Invalid master folder path. Make sure it exists.")
            return
            
        self.codec.ffx_master_path = path
        # Look for localization folders
        locs = []
        for name in os.listdir(path):
            d = os.path.join(path, name)
            if os.path.isdir(d):
                kernel_path = os.path.join(d, "battle", "kernel")
                if os.path.exists(kernel_path):
                    locs.append(name)
                    
        if not locs:
            # Maybe the path entered was already the localization subfolder (e.g. jppc)
            parent_dir = os.path.dirname(path)
            kernel_dir = os.path.join(path, "battle", "kernel")
            if os.path.exists(kernel_dir):
                loc_name = os.path.basename(path)
                self.ent_master_path.delete(0, tk.END)
                self.ent_master_path.insert(0, parent_dir)
                self.codec.ffx_master_path = parent_dir
                locs = [loc_name]
                
        if locs:
            # Sort localizations (prefer uspc / new_uspc first for default)
            preferred = ["new_uspc", "uspc", "jppc", "new_jppc"]
            locs = sorted(locs, key=lambda x: preferred.index(x) if x in preferred else 99)
            self.cmb_local.config(values=locs)
            self.cmb_local.set(locs[0])
            self.log(f"Found {len(locs)} localizations: {', '.join(locs)}")
            self.on_localization_changed()
        else:
            self.cmb_local.config(values=[])
            self.cmb_local.set("")
            self.cmb_bin_file.config(values=[])
            self.cmb_bin_file.set("")
            messagebox.showwarning("Warning", "Could not find any 'battle/kernel' subfolders inside the master folder.")

    def on_localization_changed(self, event=None):
        loc = self.cmb_local.get()
        if not loc:
            return
            
        # Auto-detect charset mapping
        if "jp" in loc.lower():
            self.cmb_charset.set("jp")
        elif "ch" in loc.lower() or "cn" in loc.lower():
            self.cmb_charset.set("ch")
        elif "kr" in loc.lower():
            self.cmb_charset.set("kr")
        else:
            self.cmb_charset.set("us")
            
        self.log(f"Switched localization to '{loc}'. Auto-set charset to '{self.cmb_charset.get()}'.")
        
        # Scan for bin files in battle/kernel
        kernel_path = os.path.join(self.codec.ffx_master_path, loc, "battle", "kernel")
        if os.path.exists(kernel_path):
            bins = []
            for name in os.listdir(kernel_path):
                if name.endswith(".bin") and name in FILE_RECORD_SIZES:
                    bins.append(name)
            bins.sort()
            self.cmb_bin_file.config(values=bins)
            if bins:
                # Select item_txt.bin or similar if present
                default_file = "item_txt.bin" if "item_txt.bin" in bins else bins[0]
                self.cmb_bin_file.set(default_file)
                self.on_bin_file_selected()
            else:
                self.cmb_bin_file.set("")
                self.clear_table()
        else:
            self.cmb_bin_file.config(values=[])
            self.cmb_bin_file.set("")
            self.clear_table()

    def clear_table(self):
        self.records = []
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.clear_editor_fields()

    def clear_editor_fields(self):
        self.ent_name.delete(0, tk.END)
        self.ent_sname.delete(0, tk.END)
        self.ent_desc.delete(0, tk.END)
        self.ent_sdesc.delete(0, tk.END)
        self.lbl_len_warn.config(text="Bytes used: Name: 0 | Desc: 0", foreground=self.text_dim)

    def on_bin_file_selected(self, event=None):
        loc = self.cmb_local.get()
        bin_file = self.cmb_bin_file.get()
        if not loc or not bin_file:
            return
            
        filepath = os.path.join(self.codec.ffx_master_path, loc, "battle", "kernel", bin_file)
        if not os.path.exists(filepath):
            messagebox.showerror("Error", f"File not found: {filepath}")
            return
            
        self.active_file_path = filepath
        self.active_file_name = bin_file
        
        record_len = FILE_RECORD_SIZES.get(bin_file, 16)
        charset = self.cmb_charset.get()
        
        self.log(f"Reading file '{bin_file}' (Record length: {record_len})...")
        try:
            records, min_idx, max_idx, magic_part = self.codec.read_ffx_text_bin(filepath, record_len, charset)
            self.records = records
            self.min_idx = min_idx
            self.max_idx = max_idx
            self.magic_part = magic_part
            self.log(f"Successfully loaded {len(records)} entries (IDs {min_idx} to {max_idx}).", "success")
            
            # Update Dashboard Recent Files Config
            self.add_recent_file(filepath)
            
            self.filter_treeview()
        except Exception as e:
            self.log(f"Failed to read file: {e}", "error")
            messagebox.showerror("Read Error", f"Failed to parse binary file:\n{str(e)}")
            self.clear_table()

    def add_recent_file(self, path):
        recent = self.config.get("recent_files", [])
        if path in recent:
            recent.remove(path)
        recent.insert(0, path)
        self.config["recent_files"] = recent[:10]
        self.save_config()

    def load_from_absolute_path(self, filepath):
        filepath = os.path.abspath(filepath)
        if not os.path.exists(filepath):
            return
            
        norm_path = filepath.replace("\\", "/")
        parts = norm_path.split("/")
        
        try:
            if "battle" in parts and "kernel" in parts:
                b_idx = parts.index("battle")
                if parts[b_idx + 1] == "kernel":
                    loc = parts[b_idx - 1]
                    master_path = "/".join(parts[:b_idx - 1])
                    filename = parts[-1]
                    
                    self.ent_master_path.delete(0, tk.END)
                    self.ent_master_path.insert(0, os.path.abspath(master_path))
                    self.codec.ffx_master_path = os.path.abspath(master_path)
                    
                    # Scan localizations
                    self.scan_localizations()
                    
                    self.cmb_local.set(loc)
                    self.on_localization_changed()
                    
                    self.cmb_bin_file.set(filename)
                    self.on_bin_file_selected()
                    
                    self.log(f"Successfully loaded file: {filename}")
        except Exception as e:
            self.log(f"Error loading file: {e}", "error")

    def filter_treeview(self, event=None):
        query = self.ent_search.get().strip().lower()
        
        # Clear Treeview
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        for r in self.records:
            name = r['name']
            sname = r['sname']
            desc = r['desc']
            sdesc = r['sdesc']
            # For files like monster1-3.bin, desc is usually '-' while sname/sdesc contain the Sensor/Scan text
            display_desc = desc if desc and desc != "-" else (sname if sname else sdesc)
            if not query or query in str(r['id']) or query in name.lower() or query in desc.lower() or query in sname.lower() or query in sdesc.lower():
                # Format displaying bracket commands or multi-lines cleanly
                name_clean = name.replace("\n", " ")
                desc_clean = display_desc.replace("\n", " ")
                self.tree.insert("", tk.END, iid=r['id'], values=(r['id'], name_clean, desc_clean))

    def on_tree_row_selected(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        entry_id = int(sel[0])
        # Find record in memory
        record = next((r for r in self.records if r['id'] == entry_id), None)
        if not record:
            return
            
        self.clear_editor_fields()
        self.ent_name.insert(0, record['name'])
        self.ent_sname.insert(0, record['sname'])
        self.ent_desc.insert(0, record['desc'])
        self.ent_sdesc.insert(0, record['sdesc'])
        
        self.update_length_label()

        # Populate Stats tab if applicable
        file_name = self.active_file_name
        extra_bytes = record.get('extra_bytes', b'')
        
        self.show_stats_group(file_name)
        
        if file_name == "important.bin" and len(extra_bytes) >= 4:
            self.stat_vars["primer"].set(1 if extra_bytes[0] > 0 else 0)
            self.stat_vars["unk12"].set(str(extra_bytes[2]))
            self.stat_vars["ordering"].set(str(extra_bytes[3]))
            
        elif file_name in ["item.bin", "command.bin", "monmagic1.bin", "monmagic2.bin"] and len(extra_bytes) >= 76:
            def get_b(offset):
                return extra_bytes[offset - 0x10]
                
            self.stat_vars["mp_cost"].set(str(get_b(0x25)))
            self.stat_vars["od_cost"].set(str(get_b(0x26)))
            self.stat_vars["power"].set(str(get_b(0x2A)))
            self.stat_vars["accuracy"].set(str(get_b(0x29)))
            self.stat_vars["hit_count"].set(str(get_b(0x2B)))
            
            formula_val = get_b(0x28)
            formula_str = "None (0x0)"
            for code, name in DAMAGE_FORMULAS:
                if code == formula_val:
                    formula_str = f"{name} ({hex(code)})"
                    break
            self.cmb_formula.set(formula_str)
            
            elem = get_b(0x2D)
            self.stat_vars["elem_fire"].set(1 if elem & 0x01 else 0)
            self.stat_vars["elem_ice"].set(1 if elem & 0x02 else 0)
            self.stat_vars["elem_thunder"].set(1 if elem & 0x04 else 0)
            self.stat_vars["elem_water"].set(1 if elem & 0x08 else 0)
            self.stat_vars["elem_holy"].set(1 if elem & 0x10 else 0)
            
            tgt = get_b(0x1A)
            self.stat_vars["tgt_enabled"].set(1 if tgt & 0x01 else 0)
            self.stat_vars["tgt_enemies"].set(1 if tgt & 0x02 else 0)
            self.stat_vars["tgt_multi"].set(1 if tgt & 0x04 else 0)
            self.stat_vars["tgt_self"].set(1 if tgt & 0x08 else 0)
            self.stat_vars["tgt_either"].set(1 if tgt & 0x20 else 0)
            self.stat_vars["tgt_dead"].set(1 if tgt & 0x40 else 0)
            self.stat_vars["tgt_ranged"].set(1 if tgt & 0x80 else 0)
            
            self.stat_vars["st_death"].set(str(get_b(0x2E)))
            self.stat_vars["st_zombie"].set(str(get_b(0x2F)))
            self.stat_vars["st_petrify"].set(str(get_b(0x30)))
            self.stat_vars["st_poison"].set(str(get_b(0x31)))
            self.stat_vars["st_confuse"].set(str(get_b(0x36)))
            self.stat_vars["st_berserk"].set(str(get_b(0x37)))
            self.stat_vars["st_provoke"].set(str(get_b(0x38)))
            self.stat_vars["st_threaten"].set(str(get_b(0x39)))
            self.stat_vars["st_sleep"].set(str(get_b(0x3A)))
            self.stat_vars["st_silence"].set(str(get_b(0x3B)))
            self.stat_vars["st_darkness"].set(str(get_b(0x3C)))
            self.stat_vars["st_slow"].set(str(get_b(0x46)))
            self.stat_vars["st_haste"].set(str(get_b(0x45)))

    def update_length_label(self):
        charset = self.cmb_charset.get()
        name_bytes = len(self.codec.encode_ffx_string(self.ent_name.get(), charset))
        sname_bytes = len(self.codec.encode_ffx_string(self.ent_sname.get(), charset))
        desc_bytes = len(self.codec.encode_ffx_string(self.ent_desc.get(), charset))
        sdesc_bytes = len(self.codec.encode_ffx_string(self.ent_sdesc.get(), charset))
        
        total_rec_bytes = name_bytes + sname_bytes + desc_bytes + sdesc_bytes + 4 # Null terminators
        
        # Calculate current total pool size in memory
        unique_strings = set()
        for r in self.records:
            sel = self.tree.selection()
            is_current = sel and (int(sel[0]) == r['id'])
            if is_current:
                unique_strings.update([self.ent_name.get(), self.ent_sname.get(), self.ent_desc.get(), self.ent_sdesc.get()])
            else:
                unique_strings.update([r['name'], r['sname'], r['desc'], r['sdesc']])
        
        total_pool_size = sum(len(self.codec.encode_ffx_string(s, charset)) + 1 for s in unique_strings)
        
        msg = f"Current entry: {total_rec_bytes} bytes | Total Pool: {total_pool_size} / 65535 bytes"
        self.lbl_len_warn.config(text=msg)
        
        if total_pool_size > 65535 or total_rec_bytes > 800:
            self.lbl_len_warn.config(foreground=self.error_color)
        elif total_pool_size > 60000:
            self.lbl_len_warn.config(foreground="orange")
        else:
            self.lbl_len_warn.config(foreground=self.text_dim)

    def apply_row_edits(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "No entry selected. Double-click or select an entry in the table first.")
            return
            
        entry_id = int(sel[0])
        record = next((r for r in self.records if r['id'] == entry_id), None)
        if not record:
            return
            
        # Check safeguards
        charset = self.cmb_charset.get()
        name_bytes = len(self.codec.encode_ffx_string(self.ent_name.get(), charset))
        sname_bytes = len(self.codec.encode_ffx_string(self.ent_sname.get(), charset))
        desc_bytes = len(self.codec.encode_ffx_string(self.ent_desc.get(), charset))
        sdesc_bytes = len(self.codec.encode_ffx_string(self.ent_sdesc.get(), charset))
        total_rec_bytes = name_bytes + sname_bytes + desc_bytes + sdesc_bytes + 4
        
        if total_rec_bytes > 1000:
            ans = messagebox.askyesno("Length Warning", 
                f"This entry is extremely long ({total_rec_bytes} bytes).\n"
                "In-game text buffers might overflow, causing text cutoff or crashes.\n\n"
                "Do you want to apply it anyway?")
            if not ans:
                return

        # Update records in memory
        record['name'] = self.ent_name.get()
        record['sname'] = self.ent_sname.get()
        record['desc'] = self.ent_desc.get()
        record['sdesc'] = self.ent_sdesc.get()
        
        # Update tree row display
        name_clean = record['name'].replace("\n", " ")
        desc_clean = record['desc'].replace("\n", " ")
        self.tree.item(entry_id, values=(record['id'], name_clean, desc_clean))
        self.log(f"Applied modifications in-memory to entry ID {entry_id}.")
        self.update_length_label()

    def export_csv(self):
        if not self.records:
            messagebox.showwarning("Warning", "No active table loaded. Load a file first.")
            return
            
        # Ask user for Single vs Batch mode
        ans = messagebox.askyesnocancel("Export CSV Mode",
            "Do you want to export ALL localization table files in one batch?\n\n"
            "Select 'Yes' to batch export all tables to a folder.\n"
            "Select 'No' to export only the currently active table to a single CSV file.")
            
        if ans is None:
            return
            
        if ans is True:
            # Batch mode
            target_dir = filedialog.askdirectory(title="Select Target Folder for Batch CSV Export")
            if not target_dir:
                return
                
            loc = self.cmb_local.get()
            kernel_path = os.path.join(self.codec.ffx_master_path, loc, "battle", "kernel")
            charset = self.cmb_charset.get()
            
            exported = []
            for filename in os.listdir(kernel_path):
                if filename.endswith(".bin") and filename in FILE_RECORD_SIZES:
                    fpath = os.path.join(kernel_path, filename)
                    rec_len = FILE_RECORD_SIZES[filename]
                    csv_path = os.path.join(target_dir, f"{os.path.splitext(filename)[0]}.csv")
                    try:
                        recs, min_id, max_id, magic = self.codec.read_ffx_text_bin(fpath, rec_len, charset)
                        with open(csv_path, "w", encoding="utf-8", newline="") as f:
                            writer = csv.writer(f)
                            writer.writerow(["ID", "Name", "SimplifiedName", "Description", "SimplifiedDescription"])
                            for r in recs:
                                writer.writerow([r['id'], r['name'], r['sname'], r['desc'], r['sdesc']])
                        exported.append(filename)
                    except Exception as e:
                        self.log(f"Failed to batch export '{filename}': {e}", "error")
            
            if exported:
                self.log(f"Successfully batch exported {len(exported)} files to CSV in: {target_dir}", "success")
                messagebox.showinfo("Export Successful", f"Batch export completed successfully!\n\nExported {len(exported)} files.")
            else:
                messagebox.showerror("Export Error", "No tables were successfully exported.")
        else:
            # Single file mode
            save_path = filedialog.asksaveasfilename(
                title="Export Table to CSV",
                filetypes=[("CSV Files", "*.csv")],
                defaultextension=".csv",
                initialfile=f"{self.active_file_name.replace('.bin', '')}_export.csv"
            )
            if not save_path:
                return
                
            self.log(f"Exporting entries to CSV: {save_path}...")
            try:
                with open(save_path, "w", encoding="utf-8", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["ID", "Name", "SimplifiedName", "Description", "SimplifiedDescription"])
                    for r in self.records:
                        writer.writerow([r['id'], r['name'], r['sname'], r['desc'], r['sdesc']])
                self.log(f"Successfully exported {len(self.records)} rows to CSV.", "success")
                messagebox.showinfo("Export Successful", f"Successfully exported all records to:\n{save_path}")
            except Exception as e:
                self.log(f"CSV Export failed: {e}", "error")
                messagebox.showerror("Export Error", f"Failed to save CSV file:\n{str(e)}")

    def import_csv(self):
        if not self.records:
            messagebox.showwarning("Warning", "Load the target table file in the editor first.")
            return
            
        # Ask user for Single vs Batch mode
        ans = messagebox.askyesnocancel("Import CSV Mode",
            "Do you want to batch import all CSV translation files from a folder?\n\n"
            "Select 'Yes' to batch import/update all tables in the localization directory.\n"
            "Select 'No' to import into the currently active table from a single CSV file.")
            
        if ans is None:
            return
            
        if ans is True:
            # Batch import mode
            source_dir = filedialog.askdirectory(title="Select Folder containing CSV Files")
            if not source_dir:
                return
                
            loc = self.cmb_local.get()
            kernel_path = os.path.join(self.codec.ffx_master_path, loc, "battle", "kernel")
            charset = self.cmb_charset.get()
            
            imported = []
            for csv_name in os.listdir(source_dir):
                if csv_name.lower().endswith(".csv"):
                    bin_base = os.path.splitext(csv_name)[0]
                    # Handle files with _export suffix
                    if bin_base.endswith("_export"):
                        bin_base = bin_base[:-7]
                    bin_name = f"{bin_base}.bin"
                    
                    if bin_name in FILE_RECORD_SIZES:
                        fpath = os.path.join(kernel_path, bin_name)
                        csv_path = os.path.join(source_dir, csv_name)
                        if os.path.exists(fpath):
                            rec_len = FILE_RECORD_SIZES[bin_name]
                            try:
                                recs, min_id, max_id, magic = self.codec.read_ffx_text_bin(fpath, rec_len, charset)
                                imported_count = 0
                                
                                with open(csv_path, "r", encoding="utf-8") as f:
                                    reader = csv.reader(f)
                                    header = next(reader, None)
                                    if not header or len(header) < 5:
                                        self.log(f"Skipping CSV '{csv_name}': Invalid header format.", "error")
                                        continue
                                        
                                    for row in reader:
                                        if not row: continue
                                        try:
                                            rid = int(row[0])
                                            record = next((r for r in recs if r['id'] == rid), None)
                                            if record:
                                                record['name'] = row[1]
                                                record['sname'] = row[2]
                                                record['desc'] = row[3]
                                                record['sdesc'] = row[4]
                                                imported_count += 1
                                        except ValueError:
                                            continue
                                
                                if imported_count > 0:
                                    unique_strings = set()
                                    for r in recs:
                                        unique_strings.update([r['name'], r['sname'], r['desc'], r['sdesc']])
                                    total_pool_size = sum(len(self.codec.encode_ffx_string(s, charset)) + 1 for s in unique_strings)
                                    
                                    if total_pool_size > 65535:
                                        self.log(f"Batch Import Blocked for '{bin_name}': String pool size ({total_pool_size} bytes) exceeds 65535 byte limit.", "error")
                                        continue
                                        
                                    bak_path = fpath + ".bak"
                                    if not os.path.exists(bak_path):
                                        import shutil
                                        shutil.copy2(fpath, bak_path)
                                        
                                    self.codec.write_ffx_text_bin(fpath, recs, min_id, max_id, magic, charset)
                                    imported.append((bin_name, imported_count))
                            except Exception as e:
                                self.log(f"Failed to batch import '{csv_name}': {e}", "error")
            
            if imported:
                summary_msg = "\n".join(f"- {name}: {count} rows" for name, count in imported)
                self.log(f"Successfully batch imported updates for {len(imported)} files from: {source_dir}", "success")
                self.on_bin_file_selected()
                messagebox.showinfo("Import Successful", f"Batch import completed successfully!\n\nImported updates:\n{summary_msg}")
            else:
                messagebox.showerror("Import Error", "No tables were successfully updated.")
                
        else:
            # Single file mode
            open_path = filedialog.askopenfilename(
                title="Import Table from CSV",
                filetypes=[("CSV Files", "*.csv")]
            )
            if not open_path:
                return
                
            self.log(f"Importing entries from CSV: {open_path}...")
            try:
                imported_count = 0
                with open(open_path, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    header = next(reader, None)
                    if not header or len(header) < 5:
                        raise ValueError("CSV header format is invalid. Must have: ID, Name, SimplifiedName, Description, SimplifiedDescription")
                        
                    for row in reader:
                        if not row: continue
                        try:
                            rid = int(row[0])
                            record = next((r for r in self.records if r['id'] == rid), None)
                            if record:
                                record['name'] = row[1]
                                record['sname'] = row[2]
                                record['desc'] = row[3]
                                record['sdesc'] = row[4]
                                imported_count += 1
                        except ValueError:
                            continue
                            
                self.log(f"Successfully imported {imported_count} updates from CSV. Refreshing table view...", "success")
                self.filter_treeview()
                self.clear_editor_fields()
                messagebox.showinfo("Import Successful", f"Successfully imported {imported_count} translations from CSV.")
            except Exception as e:
                self.log(f"CSV Import failed: {e}", "error")
                messagebox.showerror("Import Error", f"Failed to load CSV file:\n{str(e)}")

    def open_search_replace_dialog(self):
        if not self.records:
            messagebox.showwarning("Warning", "Load the target table file in the editor first.")
            return
            
        dialog = tk.Toplevel(self.root)
        dialog.title("Global Search & Replace")
        dialog.geometry("450x250")
        dialog.resizable(False, False)
        dialog.configure(bg=self.bg_color)
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog.columnconfigure(1, weight=1)
        
        ttk.Label(dialog, text="Find Text:").grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        ent_find = ttk.Entry(dialog, width=40)
        ent_find.grid(row=0, column=1, sticky="ew", padx=15, pady=(15, 5))
        
        ttk.Label(dialog, text="Replace With:").grid(row=1, column=0, sticky="w", padx=15, pady=5)
        ent_replace = ttk.Entry(dialog, width=40)
        ent_replace.grid(row=1, column=1, sticky="ew", padx=15, pady=5)
        
        ttk.Label(dialog, text="Scope:").grid(row=2, column=0, sticky="w", padx=15, pady=5)
        cmb_scope = ttk.Combobox(dialog, state="readonly", values=["Current File only", "All Files in Localization"])
        cmb_scope.grid(row=2, column=1, sticky="w", padx=15, pady=5)
        cmb_scope.set("Current File only")
        
        var_case = tk.BooleanVar(value=False)
        chk_case = ttk.Checkbutton(dialog, text="Case Sensitive", variable=var_case)
        chk_case.grid(row=3, column=1, sticky="w", padx=15, pady=5)
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=15, pady=15)
        
        def run_replace():
            find_txt = ent_find.get()
            replace_txt = ent_replace.get()
            scope = cmb_scope.get()
            case_sens = var_case.get()
            
            if not find_txt:
                messagebox.showwarning("Warning", "Please enter text to find.")
                return
                
            if scope == "Current File only":
                count = 0
                for r in self.records:
                    for field in ['name', 'sname', 'desc', 'sdesc']:
                        orig = r[field]
                        if not case_sens:
                            import re
                            pattern = re.compile(re.escape(find_txt), re.IGNORECASE)
                            new_val, sub_count = pattern.subn(replace_txt, orig)
                        else:
                            new_val = orig.replace(find_txt, replace_txt)
                            sub_count = orig.count(find_txt)
                        if sub_count > 0:
                            r[field] = new_val
                            count += sub_count
                if count > 0:
                    self.log(f"Search & Replace: Replaced {count} occurrences of '{find_txt}' with '{replace_txt}' in current file memory.", "success")
                    self.filter_treeview()
                    self.clear_editor_fields()
                    messagebox.showinfo("Success", f"Replaced {count} occurrences in the current file.\n\nNote: Changes are in-memory. Click 'Repack & Save' to write them to disk.")
                    dialog.destroy()
                else:
                    messagebox.showinfo("Search & Replace", "No occurrences found.")
            else:
                ans = messagebox.askyesno("Confirm Global Action",
                    "This will read, modify, and save ALL .bin files in the active localization folder.\n"
                    "Automatic backup files (.bak) will be created for any modified files.\n\n"
                    "Are you sure you want to perform this global replacement?")
                if not ans:
                    return
                    
                loc = self.cmb_local.get()
                kernel_path = os.path.join(self.codec.ffx_master_path, loc, "battle", "kernel")
                charset = self.cmb_charset.get()
                
                modified_files = []
                total_replaced = 0
                
                for filename in os.listdir(kernel_path):
                    if filename.endswith(".bin") and filename in FILE_RECORD_SIZES:
                        fpath = os.path.join(kernel_path, filename)
                        rec_len = FILE_RECORD_SIZES[filename]
                        try:
                            recs, min_id, max_id, magic = self.codec.read_ffx_text_bin(fpath, rec_len, charset)
                            file_mod = False
                            file_replaced = 0
                            for r in recs:
                                for field in ['name', 'sname', 'desc', 'sdesc']:
                                    orig = r[field]
                                    if not case_sens:
                                        import re
                                        pattern = re.compile(re.escape(find_txt), re.IGNORECASE)
                                        new_val, sub_count = pattern.subn(replace_txt, orig)
                                    else:
                                        new_val = orig.replace(find_txt, replace_txt)
                                        sub_count = orig.count(find_txt)
                                    if sub_count > 0:
                                        r[field] = new_val
                                        file_replaced += sub_count
                                        file_mod = True
                            if file_mod:
                                bak_path = fpath + ".bak"
                                if not os.path.exists(bak_path):
                                    import shutil
                                    shutil.copy2(fpath, bak_path)
                                self.codec.write_ffx_text_bin(fpath, recs, min_id, max_id, magic, charset)
                                modified_files.append(filename)
                                total_replaced += file_replaced
                        except Exception as e:
                            self.log(f"Failed to process '{filename}' for replacement: {e}", "error")
                            
                if total_replaced > 0:
                    self.log(f"Global Search & Replace: Replaced {total_replaced} occurrences across files: {', '.join(modified_files)}", "success")
                    self.on_bin_file_selected()
                    messagebox.showinfo("Success", f"Replaced {total_replaced} occurrences across {len(modified_files)} files:\n\n" + "\n".join(modified_files))
                    dialog.destroy()
                else:
                    messagebox.showinfo("Search & Replace", "No occurrences found in any files.")
        
        btn_run = tk.Button(btn_frame, text="Run Replace", command=run_replace, bg=self.accent_color, fg="white",
                             font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.accent_hover, activeforeground="white", padx=15, pady=4)
        btn_run.pack(side="right")
        self.bind_hover(btn_run, is_primary=True)
        
        btn_cancel = tk.Button(btn_frame, text="Cancel", command=dialog.destroy, bg=self.card_color, fg=self.text_color,
                               font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.border_color, activeforeground=self.text_color, padx=15, pady=4)
        btn_cancel.pack(side="left")
        self.bind_hover(btn_cancel)

    def save_bin_file(self):
        if not self.records or not self.active_file_path:
            messagebox.showwarning("Warning", "No active file loaded to save.")
            return
            
        # Double check if any editing is unsaved in entry boxes
        sel = self.tree.selection()
        if sel:
            entry_id = int(sel[0])
            record = next((r for r in self.records if r['id'] == entry_id), None)
            if record:
                if (record['name'] != self.ent_name.get() or 
                    record['sname'] != self.ent_sname.get() or 
                    record['desc'] != self.ent_desc.get() or 
                    record['sdesc'] != self.ent_sdesc.get()):
                    ans = messagebox.askyesnocancel("Unapplied Edits", 
                        f"Entry ID {entry_id} has modifications in the editor boxes that haven't been applied to the table.\n\n"
                        "Do you want to apply these modifications before saving?")
                    if ans is True:
                        self.apply_row_edits()
                    elif ans is None:
                        return
                        
        charset = self.cmb_charset.get()
        
        # Verify safeguard on total pool size
        unique_strings = set()
        for r in self.records:
            unique_strings.update([r['name'], r['sname'], r['desc'], r['sdesc']])
        total_pool_size = sum(len(self.codec.encode_ffx_string(s, charset)) + 1 for s in unique_strings)
        
        if total_pool_size > 65535:
            messagebox.showerror("Save Blocked", 
                f"The total unique string pool size is {total_pool_size} bytes, which exceeds the 16-bit offset limit of 65,535 bytes.\n\n"
                "Saving now would corrupt the binary file and crash the game.\n"
                "Please shorten your dialogue edits before saving.")
            return

        self.log(f"Repacking binary file to {self.active_file_path} (Charset: {charset})...")
        
        try:
            bak_path = self.active_file_path + ".bak"
            if not os.path.exists(bak_path):
                import shutil
                shutil.copy2(self.active_file_path, bak_path)
                self.log(f"Created a backup copy of the original file at {bak_path}")
                
            written_size = self.codec.write_ffx_text_bin(
                self.active_file_path,
                self.records,
                self.min_idx,
                self.max_idx,
                self.magic_part,
                charset
            )
            
            self.log(f"Repack complete! Successfully saved {written_size} bytes to '{self.active_file_name}'.", "success")
            messagebox.showinfo("Save Successful", f"Table repacked successfully!\n\nFile: {self.active_file_name}\nBytes: {written_size}")
        except Exception as e:
            self.log(f"Repack failed: {e}", "error")
            messagebox.showerror("Save Error", f"Failed to repack and save binary file:\n{str(e)}")

    def bind_hover(self, btn, is_primary=False):
        if is_primary:
            btn.bind("<Enter>", lambda e: btn.config(bg=self.accent_hover))
            btn.bind("<Leave>", lambda e: btn.config(bg=self.accent_color))
        else:
            btn.bind("<Enter>", lambda e: btn.config(bg=self.border_color))
            btn.bind("<Leave>", lambda e: btn.config(bg=self.card_color))

def main():
    root = tk.Tk()
    # Apply dark mode window border coloring on modern Windows if possible
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
        
    app = FFXTextToolGUI(root, is_embedded=False)
    root.mainloop()

if __name__ == "__main__":
    main()

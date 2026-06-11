import os
import shutil
import random
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.scrollable_frame.bind('<Enter>', lambda e: canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units")))
        self.scrollable_frame.bind('<Leave>', lambda e: canvas.unbind_all("<MouseWheel>"))

class FileOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart File Organizer")
        self.root.geometry("850x650") 
        self.root.minsize(750, 500)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1) 

        self.source_path = tk.StringVar()
        self.target_path = tk.StringVar()
        self.operation = tk.StringVar(value="copy")
        self.amount_type = tk.StringVar(value="all") 
        self.amount_value = tk.StringVar(value="")
        self.selection_method = tk.StringVar(value="top")
        self.auto_sort = tk.BooleanVar(value=False) 
        
        self.total_source_files = tk.IntVar(value=0)
        self.total_ready_files = tk.StringVar(value="Ready to Process: 0 files")
        self.dynamic_ext_vars = {} 
        
        self.categories = {
            "Images": {"exts": ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'], "var": tk.BooleanVar(value=False), "count_label": tk.StringVar(value="")},
            "Movies/Video": {"exts": ['.mp4', '.mkv', '.avi', '.mov', '.wmv'], "var": tk.BooleanVar(value=False), "count_label": tk.StringVar(value="")},
            "Sounds/Audio": {"exts": ['.mp3', '.wav', '.aac', '.flac'], "var": tk.BooleanVar(value=False), "count_label": tk.StringVar(value="")},
            "Documents": {"exts": ['.pdf', '.docx', '.doc', '.xlsx', '.pptx', '.csv'], "var": tk.BooleanVar(value=False), "count_label": tk.StringVar(value="")},
            "Text Only (.txt)": {"exts": ['.txt'], "var": tk.BooleanVar(value=False), "count_label": tk.StringVar(value="")},
            "Archives": {"exts": ['.zip', '.rar', '.7z', '.tar', '.gz'], "var": tk.BooleanVar(value=False), "count_label": tk.StringVar(value="")}
        }

        # dynamic listeners
        self.source_path.trace_add("write", self.update_directory_stats)
        self.amount_type.trace_add("write", self.toggle_amount_entry)
        
        self.setup_ui()
        self.toggle_amount_entry() # Run once 

    def setup_ui(self):
        # ---  Top ---
        dir_frame = ttk.LabelFrame(self.root, text="1. Select Directories", padding=(10, 5))
        dir_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        dir_frame.columnconfigure(1, weight=1) 

        ttk.Label(dir_frame, text="Source:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(dir_frame, textvariable=self.source_path).grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(dir_frame, text="Browse", command=self.browse_source).grid(row=0, column=2)
        ttk.Label(dir_frame, text="Total:").grid(row=0, column=3, padx=(10,2))
        ttk.Label(dir_frame, textvariable=self.total_source_files, font=("", 10, "bold")).grid(row=0, column=4)

        ttk.Label(dir_frame, text="Target:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(dir_frame, textvariable=self.target_path).grid(row=1, column=1, sticky="ew", padx=5)
        ttk.Button(dir_frame, text="Browse", command=self.browse_target).grid(row=1, column=2)

        # ---  Middle  ---
        cat_frame = ttk.LabelFrame(self.root, text="2. Select Formats", padding=(10, 5))
        cat_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        cat_frame.columnconfigure(1, weight=2) 
        cat_frame.rowconfigure(1, weight=1)

        ttk.Label(cat_frame, text="Pre-defined Categories:", font=("", 9, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(cat_frame, text="Specific Extensions (Auto-detected):", font=("", 9, "bold")).grid(row=0, column=1, sticky="w", padx=10)

        left_panel = ttk.Frame(cat_frame)
        left_panel.grid(row=1, column=0, sticky="nsew", padx=5)
        for cat_name, data in self.categories.items():
            frame = ttk.Frame(left_panel)
            frame.pack(fill="x", pady=2)
            ttk.Checkbutton(frame, text=cat_name, variable=data["var"], command=lambda c=cat_name: self.toggle_category(c)).pack(side="left")
            ttk.Label(frame, textvariable=data["count_label"], foreground="blue").pack(side="left", padx=5)

        right_panel = ttk.Frame(cat_frame)
        right_panel.grid(row=1, column=1, sticky="nsew", padx=10)
        self.ext_scroll_frame = ScrollableFrame(right_panel)
        self.ext_scroll_frame.pack(fill="both", expand=True)

        for i in range(3):
            self.ext_scroll_frame.scrollable_frame.columnconfigure(i, weight=1)

        # ---  Bottom  ---
        control_frame = ttk.LabelFrame(self.root, text="3. Operation Settings & Execution", padding=(10, 5))
        control_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        
        filter_frame = ttk.Frame(control_frame)
        filter_frame.pack(fill="x", pady=2)
        
        ttk.Label(filter_frame, text="Amount:").pack(side="left")
        ttk.Combobox(filter_frame, textvariable=self.amount_type, values=["all", "percent", "number"], state="readonly", width=8).pack(side="left", padx=5)
        
        # saved to a variable 
        self.amount_entry = ttk.Entry(filter_frame, textvariable=self.amount_value, width=6)
        self.amount_entry.pack(side="left", padx=5)
        
        ttk.Label(filter_frame, text=" | Priority:").pack(side="left", padx=5)
        ttk.Combobox(filter_frame, textvariable=self.selection_method, values=["top", "bottom", "random"], state="readonly", width=8).pack(side="left", padx=5)
        ttk.Label(filter_frame, text=" | Action:").pack(side="left", padx=5)
        ttk.Combobox(filter_frame, textvariable=self.operation, values=["copy", "move"], state="readonly", width=8).pack(side="left", padx=5)
        ttk.Checkbutton(filter_frame, text="Auto-sort into subfolders", variable=self.auto_sort).pack(side="right", padx=10)

        exec_frame = ttk.Frame(control_frame)
        exec_frame.pack(fill="x", pady=10)
        ttk.Label(exec_frame, textvariable=self.total_ready_files, font=("", 10, "bold"), foreground="green").pack(side="left")
        ttk.Button(exec_frame, text="EXECUTE OPERATION", command=self.execute_operation, style="Accent.TButton", width=25).pack(side="right")

    # --- sync logic methods ---
    def toggle_amount_entry(self, *args):
        """Disables the number input box if 'All' is selected."""
        if hasattr(self, 'amount_entry'):
            if self.amount_type.get() == "all":
                self.amount_entry.config(state="disabled")
            else:
                self.amount_entry.config(state="normal")

                if not self.amount_value.get():
                    self.amount_value.set("10") 

    def toggle_category(self, cat_name):
        is_checked = self.categories[cat_name]["var"].get()
        exts = self.categories[cat_name]["exts"]
        for ext in exts:
            if ext in self.dynamic_ext_vars:
                self.dynamic_ext_vars[ext]["var"].set(is_checked)
        self.refresh_ui_counts()

    def toggle_specific(self, ext):
        is_checked = self.dynamic_ext_vars[ext]["var"].get()
        for cat_name, cat_data in self.categories.items():
            if ext in cat_data["exts"]:
                if not is_checked:
                    cat_data["var"].set(False)
                else:
                    all_ticked = True
                    for e in cat_data["exts"]:
                        if e in self.dynamic_ext_vars and not self.dynamic_ext_vars[e]["var"].get():
                            all_ticked = False
                            break
                    if all_ticked:
                        cat_data["var"].set(True)
        self.refresh_ui_counts()

    def browse_source(self):
        folder = filedialog.askdirectory(title="Select Source", initialdir=self.source_path.get() if os.path.isdir(self.source_path.get()) else "/")
        if folder: self.source_path.set(folder)

    def browse_target(self):
        folder = filedialog.askdirectory(title="Select Target", initialdir=self.target_path.get() if os.path.isdir(self.target_path.get()) else "/")
        if folder: self.target_path.set(folder)

    def update_directory_stats(self, *args):
        source = self.source_path.get()
        for widget in self.ext_scroll_frame.scrollable_frame.winfo_children(): widget.destroy()
        self.dynamic_ext_vars.clear()
        
        if not os.path.isdir(source):
            self.total_source_files.set(0)
            self.refresh_ui_counts()
            return

        try:
            total_files, found_extensions = 0, {}
            for filename in os.listdir(source):
                file_path = os.path.join(source, filename)
                if os.path.isfile(file_path):
                    total_files += 1
                    ext = os.path.splitext(filename)[1].lower()
                    if ext: found_extensions[ext] = found_extensions.get(ext, 0) + 1
            
            self.total_source_files.set(total_files)

            row, col = 0, 0
            max_cols = 3 
            
            for ext, count in sorted(found_extensions.items()):
                var = tk.BooleanVar(value=False)
                self.dynamic_ext_vars[ext] = {"var": var, "count": count}
                
                frame = ttk.Frame(self.ext_scroll_frame.scrollable_frame)
                frame.grid(row=row, column=col, sticky="w", padx=5, pady=2)
                
                ttk.Checkbutton(frame, text=ext, variable=var, command=lambda e=ext: self.toggle_specific(e)).pack(side="left")
                # The fixed line:
                lbl = ttk.Label(frame, text="", foreground="blue")
                lbl.pack(side="left")
                self.dynamic_ext_vars[ext]["label_widget"] = lbl

                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

            self.refresh_ui_counts()
        except Exception: pass

    def refresh_ui_counts(self):
        source = self.source_path.get()
        target_exts = set()

        if os.path.isdir(source):
            for data in self.categories.values():
                if data["var"].get():
                    count = sum(1 for f in os.listdir(source) if os.path.isfile(os.path.join(source, f)) and os.path.splitext(f)[1].lower() in data["exts"])
                    data["count_label"].set(f"({count})")
                    target_exts.update(data["exts"])
                else: data["count_label"].set("")

            for ext, ext_data in self.dynamic_ext_vars.items():
                if ext_data["var"].get():
                    ext_data["label_widget"].config(text=f"({ext_data['count']})")
                    target_exts.add(ext)
                else: ext_data["label_widget"].config(text="")
            
            total_selected = sum(1 for f in os.listdir(source) if os.path.isfile(os.path.join(source, f)) and os.path.splitext(f)[1].lower() in target_exts)
            self.total_ready_files.set(f"Ready to Process: {total_selected} files")
        else:
            self.total_ready_files.set("Ready to Process: 0 files")

    def execute_operation(self):
        source, target = self.source_path.get(), self.target_path.get()
        op, amt_type, method = self.operation.get(), self.amount_type.get(), self.selection_method.get()

        if not os.path.isdir(source) or not os.path.isdir(target) or source == target:
            messagebox.showerror("Error", "Invalid Source or Target directory.")
            return

        try:
            amt_val = float(self.amount_value.get())
            if amt_val <= 0 and amt_type != "all": raise ValueError
        except:
            if amt_type != "all":
                messagebox.showerror("Error", "Invalid Amount value.")
                return

        target_exts = set() 
        for d in self.categories.values():
            if d["var"].get(): target_exts.update(d["exts"])
        for e, d in self.dynamic_ext_vars.items():
            if d["var"].get(): target_exts.add(e)

        if not target_exts:
            messagebox.showwarning("Warning", "Select at least one format.")
            return

        try:
            matching_files = [f for f in os.listdir(source) if os.path.isfile(os.path.join(source, f)) and os.path.splitext(f)[1].lower() in target_exts]
            total_found = len(matching_files)

            if method == "top": matching_files.sort()
            elif method == "bottom": matching_files.sort(reverse=True)
            elif method == "random": random.shuffle(matching_files)

            if amt_type == "percent": limit = max(1, int(total_found * (amt_val / 100.0)))
            elif amt_type == "number": limit = min(total_found, int(amt_val))
            else: limit = total_found

            files_to_process = matching_files[:limit]
            processed_count = 0

            for filename in files_to_process:
                file_path = os.path.join(source, filename)
                ext = os.path.splitext(filename)[1].lower()
                
                if self.auto_sort.get():
                    folder_name = ext.replace(".", "").upper() + "_Files"
                    dest_dir = os.path.join(target, folder_name)
                    if not os.path.exists(dest_dir): os.makedirs(dest_dir)
                else:
                    dest_dir = target

                dest_path = os.path.join(dest_dir, filename)
                if os.path.exists(dest_path):
                    base = os.path.splitext(filename)[0]
                    dest_path = os.path.join(dest_dir, f"{base}_copy{ext}")

                if op == "copy": shutil.copy2(file_path, dest_path)
                elif op == "move": shutil.move(file_path, dest_path)
                processed_count += 1
                
            self.update_directory_stats()
            messagebox.showinfo("Success", f"Processed {processed_count} files successfully!")

        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    if "clam" in ttk.Style().theme_names(): ttk.Style().theme_use("clam")
    app = FileOrganizerApp(root)
    root.mainloop()

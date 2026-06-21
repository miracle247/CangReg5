import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import hashlib
import threading

class CanReg5PIIProcessor:
    def __init__(self):
        self.available_pii_columns = [
            'Patient Name',
            'Hospital Number',
            'Medical Record Number (MRN)',
            'National Identification Number (NIN)',
            'Passport Number',
            'Phone Number',
            'Email Address',
            'Home Address',
            'Date of Birth',
            'Next of Kin Information', 'Pathology Report Id'

        ]
        self.selected_columns = []
        self.input_file = None
        self.output_file = None
        self.df = None
        
        # 1. CRYPTOGRAPHIC SALTING IMPLEMENTATION
        # In a production environment, this could be loaded from an environment variable
        self.secret_salt = "CANREG5_SECURE_SALT_99382" 

    def generate_sha256_token(self, value):
        if pd.isna(value):
            return value
        # Append the salt to the value before hashing for enterprise-grade security
        salted_value = str(value) + self.secret_salt
        return hashlib.sha256(salted_value.encode('utf-8')).hexdigest()

    def load_excel_file(self, input_path):
        try:
            self.df = pd.read_excel(input_path)
            self.input_file = input_path
            return list(self.df.columns)
        except Exception as e:
            raise Exception(f"Could not load Excel file: {str(e)}")

    def find_matching_columns(self, df_columns):
        matching = {}
        df_cols_lower = {col.lower(): col for col in df_columns}

        for pii_col in self.available_pii_columns:
            pii_col_lower = pii_col.lower()
            if pii_col_lower in df_cols_lower:
                matching[pii_col] = df_cols_lower[pii_col_lower]

        return matching

    def process_file(self, progress_callback, completion_callback, error_callback):
        """Processes the file and communicates with the GUI thread via callbacks"""
        try:
            total_selected = len(self.selected_columns)
            
            for index, selected in enumerate(self.selected_columns):
                selected_lower = selected.lower()
                for actual_col in self.df.columns:
                    if actual_col.lower() == selected_lower:
                        self.df[actual_col] = self.df[actual_col].apply(self.generate_sha256_token)
                        break
                
                # Update progress bar after each column is processed
                progress_percentage = int(((index + 1) / total_selected) * 100)
                progress_callback(progress_percentage)

            self.df.to_excel(self.output_file, index=False)
            completion_callback()

        except Exception as e:
            error_callback(str(e))


class CanReg5PIITokenizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CanReg5 PII Tokenizer")
        self.root.geometry("500x750")
        self.processor = CanReg5PIIProcessor()

        self.input_file_label = None
        self.output_file_label = None
        self.checkboxes = {}
        self.columns_frame = None
        
        # 2. UI THREADING VARIABLES
        self.hash_btn = None
        self.progress_bar = None
        self.progress_frame = None

        self.create_widgets()

    def create_widgets(self):
        title_label = tk.Label(
            self.root, text="CanReg5 PII Tokenizer", font=("Arial", 14, "bold"), pady=10
        )
        title_label.pack()

        # Step 1: Input File
        file_frame = tk.LabelFrame(self.root, text="Step 1: Select Input File", font=("Arial", 10, "bold"), padx=10, pady=10)
        file_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(file_frame, text="Browse & Load Excel File", command=self.select_input_file, bg="#2c3e50", fg="white", font=("Arial", 9, "bold"), width=30).pack(pady=5)
        self.input_file_label = tk.Label(file_frame, text="No file selected", font=("Arial", 9), fg="gray")
        self.input_file_label.pack()

        # Step 2: Columns Selection
        columns_label_frame = tk.LabelFrame(self.root, text="Step 2: Select Columns to Hash", font=("Arial", 10, "bold"), padx=10, pady=10)
        columns_label_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.columns_frame = tk.Frame(columns_label_frame)
        self.columns_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(columns_label_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas = tk.Canvas(columns_label_frame, yscrollcommand=scrollbar.set, highlightthickness=0, height=180)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=canvas.yview)

        self.inner_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=self.inner_frame, anchor=tk.NW)

        self.display_available_columns(self.processor.available_pii_columns, enabled=False)

        def on_frame_configure(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        self.inner_frame.bind("<Configure>", on_frame_configure)

        # Step 3: Output File
        output_frame = tk.LabelFrame(self.root, text="Step 3: Select Output Location", font=("Arial", 10, "bold"), padx=10, pady=10)
        output_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(output_frame, text="Choose Output Location", command=self.select_output_file, bg="#2c3e50", fg="white", font=("Arial", 9, "bold"), width=30).pack(pady=5)
        self.output_file_label = tk.Label(output_frame, text="No output location selected", font=("Arial", 9), fg="gray")
        self.output_file_label.pack()

        # Progress Bar Section (Hidden by default)
        self.progress_frame = tk.Frame(self.root)
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress_bar.pack(pady=5)

        # Action Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        self.hash_btn = tk.Button(button_frame, text="Start Hashing Process", command=self.start_hashing, bg="#27ae60", fg="white", font=("Arial", 10, "bold"), height=2, width=25)
        self.hash_btn.pack(side=tk.LEFT, padx=5)

        tk.Button(button_frame, text="Reset", command=self.reset_form, bg="#95a5a6", fg="white", font=("Arial", 10, "bold"), height=2, width=10).pack(side=tk.LEFT, padx=5)

    def display_available_columns(self, columns, enabled=True):
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
        self.checkboxes.clear()

        for col in columns:
            var = tk.BooleanVar()
            checkbox = tk.Checkbutton(
                self.inner_frame, text=col, variable=var,
                state=tk.NORMAL if enabled else tk.DISABLED,
                font=("Arial", 9), fg="black" if enabled else "gray"
            )
            checkbox.pack(anchor=tk.W, pady=3)
            self.checkboxes[col] = var

    def select_input_file(self):
        input_file = filedialog.askopenfilename(title="Select CanReg5 Excel File", filetypes=[("Excel Files", "*.xlsx;*.xls")])
        if not input_file:
            return

        try:
            available_cols = self.processor.load_excel_file(input_file)
            self.input_file_label.config(text=f"Loaded: {input_file.split('/')[-1]}", fg="green")
            
            matching_columns = self.processor.find_matching_columns(available_cols)
            if matching_columns:
                self.display_available_columns(list(matching_columns.keys()), enabled=True)
            else:
                messagebox.showwarning("No Matching Columns", "No standard PII columns found.")
                self.display_available_columns(self.processor.available_pii_columns, enabled=False)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def select_output_file(self):
        output_file = filedialog.asksaveasfilename(title="Save Anonymized Excel File", defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if output_file:
            self.processor.output_file = output_file
            self.output_file_label.config(text=f"Output: {output_file.split('/')[-1]}", fg="green")

    def start_hashing(self):
        if not self.processor.input_file:
            messagebox.showwarning("Input Error", "Please select an input Excel file first.")
            return
        if not self.processor.output_file:
            messagebox.showwarning("Output Error", "Please select an output location first.")
            return

        selected = [col for col, var in self.checkboxes.items() if var.get()]
        if not selected:
            messagebox.showwarning("Selection Error", "Please select at least one column to hash.")
            return

        self.processor.selected_columns = selected
        
        # Prepare UI for background processing
        self.hash_btn.config(state=tk.DISABLED)
        self.progress_frame.pack(fill=tk.X, padx=10, pady=5)
        self.progress_bar['value'] = 0
        
        # Launch the hashing in a separate background thread to keep GUI responsive
        processing_thread = threading.Thread(target=self._run_hashing_thread)
        processing_thread.daemon = True
        processing_thread.start()

    def _run_hashing_thread(self):
        """This runs entirely in the background so the Tkinter window doesn't freeze"""
        self.processor.process_file(
            progress_callback=self.update_progress,
            completion_callback=self.hashing_complete,
            error_callback=self.hashing_error
        )

    def update_progress(self, percentage):
        # Safely schedule GUI updates from the background thread
        self.root.after(0, lambda: self.progress_bar.config(value=percentage))

    def hashing_complete(self):
        def _complete_ui_updates():
            self.hash_btn.config(state=tk.NORMAL)
            self.progress_bar['value'] = 100
            messagebox.showinfo("Success", "Data successfully tokenized via salted SHA-256.")
            self.progress_frame.pack_forget()
        self.root.after(0, _complete_ui_updates)

    def hashing_error(self, error_msg):
        def _error_ui_updates():
            self.hash_btn.config(state=tk.NORMAL)
            self.progress_frame.pack_forget()
            messagebox.showerror("Processing Error", f"Error processing file: {error_msg}")
        self.root.after(0, _error_ui_updates)

    def reset_form(self):
        self.processor = CanReg5PIIProcessor()
        self.input_file_label.config(text="No file selected", fg="gray")
        self.output_file_label.config(text="No output location selected", fg="gray")
        self.display_available_columns(self.processor.available_pii_columns, enabled=False)
        self.progress_frame.pack_forget()
        if self.hash_btn:
            self.hash_btn.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    gui = CanReg5PIITokenizerGUI(root)
    root.mainloop()

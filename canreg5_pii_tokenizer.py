import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import hashlib

class CanReg5PIIProcessor:
    def __init__(self):
        # The comprehensive list of PII columns that can be hashed
        # These are the standard CanReg5 column names
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
            'Next of Kin Information'
        ]
        self.selected_columns = []
        self.input_file = None
        self.output_file = None
        self.df = None

    def generate_sha256_token(self, value):
        if pd.isna(value):
            return value
        # Generate the SHA-256 hash token
        return hashlib.sha256(str(value).encode('utf-8')).hexdigest()

    def load_excel_file(self, input_path):
        """Load the Excel file and return available columns"""
        try:
            self.df = pd.read_excel(input_path)
            self.input_file = input_path
            return list(self.df.columns)
        except Exception as e:
            messagebox.showerror("File Loading Error", f"Could not load Excel file: {str(e)}")
            return []

    def find_matching_columns(self, df_columns):
        """Find which PII columns exist in the DataFrame (case-insensitive)"""
        matching = {}
        df_cols_lower = {col.lower(): col for col in df_columns}
        
        for pii_col in self.available_pii_columns:
            pii_col_lower = pii_col.lower()
            if pii_col_lower in df_cols_lower:
                matching[pii_col] = df_cols_lower[pii_col_lower]
        
        return matching

    def process_file(self):
        """Hash the selected PII columns and save to output file"""
        if not self.selected_columns:
            messagebox.showwarning("Selection Error", "Please select at least one column to hash.")
            return

        if not self.input_file or not self.output_file or self.df is None:
            messagebox.showerror("Processing Error", "File information is missing.")
            return

        try:
            # Find actual column names in the DataFrame
            df_cols_lower = {col.lower(): col for col in self.df.columns}
            
            # Hash the selected columns
            for selected in self.selected_columns:
                selected_lower = selected.lower()
                for actual_col in self.df.columns:
                    if actual_col.lower() == selected_lower:
                        self.df[actual_col] = self.df[actual_col].apply(self.generate_sha256_token)
                        break

            # Save the anonymized data
            self.df.to_excel(self.output_file, index=False)
            messagebox.showinfo("Success", 
                f"CanReg5 data successfully tokenized via SHA-256.\n\nColumns hashed:\n" + 
                "\n".join([f"• {col}" for col in self.selected_columns]))
            
        except Exception as e:
            messagebox.showerror("Processing Error", f"Error processing file: {str(e)}")


class CanReg5PIITokenizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CanReg5 PII Tokenizer")
        self.root.geometry("500x700")
        self.processor = CanReg5PIIProcessor()
        
        self.input_file_label = None
        self.checkboxes = {}
        self.columns_frame = None
        
        self.create_widgets()

    def create_widgets(self):
        """Create the GUI components"""
        # Title
        title_label = tk.Label(
            self.root,
            text="CanReg5 PII Tokenizer",
            font=("Arial", 14, "bold"),
            pady=10
        )
        title_label.pack()

        # File Selection Section
        file_frame = tk.LabelFrame(
            self.root,
            text="Step 1: Select Input File",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        file_frame.pack(fill=tk.X, padx=10, pady=5)

        select_btn = tk.Button(
            file_frame,
            text="Browse & Load Excel File",
            command=self.select_input_file,
            bg="#2c3e50",
            fg="white",
            font=("Arial", 9, "bold"),
            width=30
        )
        select_btn.pack(pady=5)

        self.input_file_label = tk.Label(
            file_frame,
            text="No file selected",
            font=("Arial", 9),
            fg="gray"
        )
        self.input_file_label.pack()

        # PII Columns Selection Section
        columns_label_frame = tk.LabelFrame(
            self.root,
            text="Step 2: Select Columns to Hash",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        columns_label_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Scrollable frame for checkboxes
        self.columns_frame = tk.Frame(columns_label_frame)
        self.columns_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(columns_label_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas = tk.Canvas(
            columns_label_frame,
            yscrollcommand=scrollbar.set,
            highlightthickness=0,
            height=200
        )
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=canvas.yview)

        # Frame inside canvas for checkboxes
        self.inner_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=self.inner_frame, anchor=tk.NW)

        # Initially show all available columns (greyed out)
        self.display_available_columns(self.processor.available_pii_columns, enabled=False)

        def on_frame_configure(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        self.inner_frame.bind("<Configure>", on_frame_configure)

        # Output File Selection Section
        output_frame = tk.LabelFrame(
            self.root,
            text="Step 3: Select Output Location",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        output_frame.pack(fill=tk.X, padx=10, pady=5)

        output_btn = tk.Button(
            output_frame,
            text="Choose Output Location",
            command=self.select_output_file,
            bg="#2c3e50",
            fg="white",
            font=("Arial", 9, "bold"),
            width=30
        )
        output_btn.pack(pady=5)

        self.output_file_label = tk.Label(
            output_frame,
            text="No output location selected",
            font=("Arial", 9),
            fg="gray"
        )
        self.output_file_label.pack()

        # Action Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        hash_btn = tk.Button(
            button_frame,
            text="Start Hashing Process",
            command=self.start_hashing,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            height=2,
            width=25
        )
        hash_btn.pack(side=tk.LEFT, padx=5)

        reset_btn = tk.Button(
            button_frame,
            text="Reset",
            command=self.reset_form,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 10, "bold"),
            height=2,
            width=10
        )
        reset_btn.pack(side=tk.LEFT, padx=5)

    def display_available_columns(self, columns, enabled=True):
        """Display the available PII columns as checkboxes"""
        # Clear existing checkboxes
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
        self.checkboxes.clear()

        for col in columns:
            var = tk.BooleanVar()
            checkbox = tk.Checkbutton(
                self.inner_frame,
                text=col,
                variable=var,
                state=tk.NORMAL if enabled else tk.DISABLED,
                font=("Arial", 9),
                fg="black" if enabled else "gray"
            )
            checkbox.pack(anchor=tk.W, pady=3)
            self.checkboxes[col] = var

    def select_input_file(self):
        """Handle input file selection"""
        input_file = filedialog.askopenfilename(
            title="Select CanReg5 Excel File",
            filetypes=[("Excel Files", "*.xlsx;*.xls")]
        )

        if not input_file:
            return

        # Load the file and check available columns
        available_cols = self.processor.load_excel_file(input_file)
        
        if not available_cols:
            return

        self.input_file_label.config(
            text=f"Loaded: {input_file.split('/')[-1]}",
            fg="green"
        )

        # Find which PII columns exist in this file
        matching_columns = self.processor.find_matching_columns(available_cols)
        
        if matching_columns:
            # Display only the columns that exist in the file
            self.display_available_columns(list(matching_columns.keys()), enabled=True)
        else:
            messagebox.showwarning(
                "No Matching Columns",
                "No standard PII columns found in the Excel file.\n\n"
                f"File columns: {', '.join(available_cols[:5])}{'...' if len(available_cols) > 5 else ''}\n\n"
                "Please ensure your file has standard CanReg5 PII column names."
            )
            self.display_available_columns(self.processor.available_pii_columns, enabled=False)

    def select_output_file(self):
        """Handle output file selection"""
        output_file = filedialog.asksaveasfilename(
            title="Save Anonymized Excel File",
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")]
        )

        if output_file:
            self.processor.output_file = output_file
            self.output_file_label.config(
                text=f"Output: {output_file.split('/')[-1]}",
                fg="green"
            )

    def start_hashing(self):
        """Start the hashing process with selected columns"""
        if not self.processor.input_file:
            messagebox.showwarning("Input Error", "Please select an input Excel file first.")
            return

        if not self.processor.output_file:
            messagebox.showwarning("Output Error", "Please select an output location first.")
            return

        # Get selected columns
        selected = [col for col, var in self.checkboxes.items() if var.get()]
        
        if not selected:
            messagebox.showwarning("Selection Error", "Please select at least one column to hash.")
            return

        self.processor.selected_columns = selected
        self.processor.process_file()

    def reset_form(self):
        """Reset the form to initial state"""
        self.processor = CanReg5PIIProcessor()
        self.input_file_label.config(text="No file selected", fg="gray")
        self.output_file_label.config(text="No output location selected", fg="gray")
        self.display_available_columns(self.processor.available_pii_columns, enabled=False)


# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    gui = CanReg5PIITokenizerGUI(root)
    root.mainloop()

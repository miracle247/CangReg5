import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import hashlib

class CanReg5PIIProcessor:
    def __init__(self):
        # The specific PII columns to target from the CanReg5 export
        # You can easily add more to this list if needed
        self.pii_columns = ['name', 'reg. no']

    def generate_sha256_token(self, value):
        if pd.isna(value):
            return value
        # Generate the SHA-256 hash token
        return hashlib.sha256(str(value).encode('utf-8')).hexdigest()

    def process_file(self, input_path, output_path):
        # Read the CanReg5 Excel file
        df = pd.read_excel(input_path)

        # Hash the specified PII columns
        for col in self.pii_columns:
            # Case-insensitive check to catch slight variations in column names (e.g., 'Name' vs 'name')
            matching_cols = [c for c in df.columns if str(c).strip().lower() == col.lower()]
            for match in matching_cols:
                df[match] = df[match].apply(self.generate_sha256_token)

        # Save the anonymized data with tokens to a new Excel file
        df.to_excel(output_path, index=False)

# Initialize the processor
processor = CanReg5PIIProcessor()

def run_hashing_process():
    # 1. Prompt the user to select the downloaded CanReg5 Excel file
    input_file = filedialog.askopenfilename(
        title="Select CanReg5 Excel File",
        filetypes=[("Excel Files", "*.xlsx;*.xls")]
    )
    if not input_file:
        return

    # 2. Prompt the user to choose where to save the anonymized output
    output_file = filedialog.asksaveasfilename(
        title="Save Anonymized Excel File",
        defaultextension=".xlsx",
        filetypes=[("Excel Files", "*.xlsx")]
    )
    if not output_file:
        return

    # 3. Execute the hashing process
    try:
        processor.process_file(input_file, output_file)
        messagebox.showinfo("Success", "CanReg5 data successfully tokenized via SHA-256.")
    except Exception as e:
        messagebox.showerror("Processing Error", str(e))

# Build the simple Desktop Interface
root = tk.Tk()
root.title("CanReg5 PII Tokenizer")
root.geometry("350x150")

# The single button the user interacts with
btn = tk.Button(
    root,
    text="Upload & Hash Excel Dataset",
    command=run_hashing_process,
    height=2,
    width=30,
    bg="#2c3e50",
    fg="white",
    font=("Arial", 10, "bold")
)
btn.pack(expand=True)

root.mainloop()

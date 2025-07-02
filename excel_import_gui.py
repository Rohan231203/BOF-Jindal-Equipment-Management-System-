import pandas as pd
import json
import qrcode
import os
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

class ExcelImporter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Motor QR System - Excel Import Tool")
        self.root.geometry("800x600")
        
        # Configuration
        self.excel_file = None
        self.json_file = "motor_data.json"
        self.qr_folder = "qr_codes"
        self.base_url = "http://localhost:8000/motor?id="
        
        # Create GUI
        self.create_gui()
        
    def create_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Motor QR System - Excel Import", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # File selection
        ttk.Label(main_frame, text="1. Select Excel File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.file_label = ttk.Label(main_frame, text="No file selected", 
                                   foreground="gray")
        self.file_label.grid(row=2, column=0, sticky=tk.W, padx=(20, 0))
        
        ttk.Button(main_frame, text="Browse Excel File", 
                  command=self.browse_file).grid(row=1, column=1, sticky=tk.E, pady=5)
        
        # Sheet selection
        ttk.Label(main_frame, text="2. Select Sheet:").grid(row=3, column=0, sticky=tk.W, pady=(20, 5))
        self.sheet_var = tk.StringVar()
        self.sheet_combo = ttk.Combobox(main_frame, textvariable=self.sheet_var, state="readonly")
        self.sheet_combo.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Motor ID column selection
        ttk.Label(main_frame, text="3. Select Motor ID Column:").grid(row=5, column=0, sticky=tk.W, pady=(20, 5))
        self.id_column_var = tk.StringVar()
        self.id_column_combo = ttk.Combobox(main_frame, textvariable=self.id_column_var, state="readonly")
        self.id_column_combo.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Preview area
        ttk.Label(main_frame, text="4. Preview Data:").grid(row=7, column=0, sticky=tk.W, pady=(20, 5))
        
        # Create treeview for preview
        self.tree = ttk.Treeview(main_frame, height=8)
        self.tree.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Scrollbars for treeview
        v_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.tree.yview)
        v_scrollbar.grid(row=8, column=2, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(main_frame, orient="horizontal", command=self.tree.xview)
        h_scrollbar.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E))
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Progress bar
        self.progress_var = tk.StringVar(value="Ready to import")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=10, column=0, columnspan=2, pady=(20, 5))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate')
        self.progress_bar.grid(row=11, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=12, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="Preview", 
                  command=self.preview_data).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Import Data", 
                  command=self.start_import).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Clear", 
                  command=self.clear_data).pack(side=tk.LEFT)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(8, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        
        if file_path:
            self.excel_file = file_path
            self.file_label.config(text=os.path.basename(file_path), foreground="black")
            self.load_sheets()
            
    def load_sheets(self):
        try:
            # Read sheet names
            xl_file = pd.ExcelFile(self.excel_file)
            sheets = xl_file.sheet_names
            
            self.sheet_combo['values'] = sheets
            if sheets:
                self.sheet_combo.set(sheets[0])  # Select first sheet by default
                self.load_columns()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sheets: {str(e)}")
            
    def load_columns(self):
        try:
            if not self.sheet_var.get():
                return
                
            # Read first few rows to get column names
            df = pd.read_excel(self.excel_file, sheet_name=self.sheet_var.get(), nrows=5)
            columns = df.columns.tolist()
            
            self.id_column_combo['values'] = columns
            
            # Try to auto-detect motor ID column
            id_candidates = [col for col in columns if any(keyword in col.lower() 
                           for keyword in ['id', 'motor', 'sl', 'serial', 'no'])]
            
            if id_candidates:
                self.id_column_combo.set(id_candidates[0])
            elif columns:
                self.id_column_combo.set(columns[0])
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load columns: {str(e)}")
            
    def preview_data(self):
        try:
            if not self.excel_file or not self.sheet_var.get():
                messagebox.showwarning("Warning", "Please select an Excel file and sheet first.")
                return
                
            # Read data
            df = pd.read_excel(self.excel_file, sheet_name=self.sheet_var.get())
            
            # Clear existing data
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            # Set up columns
            columns = df.columns.tolist()
            self.tree['columns'] = columns
            self.tree['show'] = 'headings'
            
            # Configure column headings
            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=100)
                
            # Add data (first 100 rows for preview)
            for index, row in df.head(100).iterrows():
                values = [str(row[col]) if pd.notna(row[col]) else '' for col in columns]
                self.tree.insert('', 'end', values=values)
                
            self.progress_var.set(f"Preview: {len(df)} rows found")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview data: {str(e)}")
            
    def start_import(self):
        if not self.excel_file or not self.sheet_var.get() or not self.id_column_var.get():
            messagebox.showwarning("Warning", "Please select file, sheet, and motor ID column.")
            return
            
        # Start import in separate thread
        thread = threading.Thread(target=self.import_data)
        thread.daemon = True
        thread.start()
        
    def import_data(self):
        try:
            # Create QR folder
            os.makedirs(self.qr_folder, exist_ok=True)
            
            # Read Excel data
            self.progress_var.set("Reading Excel file...")
            df = pd.read_excel(self.excel_file, sheet_name=self.sheet_var.get())
            
            total_rows = len(df)
            self.progress_bar['maximum'] = total_rows
            
            motor_data = {}
            id_column = self.id_column_var.get()
            
            for index, row in df.iterrows():
                # Update progress
                self.progress_bar['value'] = index + 1
                self.progress_var.set(f"Processing row {index + 1} of {total_rows}")
                self.root.update_idletasks()
                
                # Get motor ID
                motor_id = str(row[id_column]).strip()
                if not motor_id or motor_id.lower() in ['nan', 'none', '']:
                    motor_id = f"MTR{index+1:03d}"
                
                # Process other columns
                motor_info = {}
                for col in df.columns:
                    if col == id_column:
                        continue
                        
                    value = row[col]
                    if pd.notna(value) and str(value).strip():
                        # Clean field name
                        clean_col = self.clean_field_name(col)
                        
                        # Handle date fields
                        if 'date' in clean_col.lower():
                            value = self.convert_date(value)
                        
                        motor_info[clean_col] = str(value).strip()
                
                motor_data[motor_id] = motor_info
                
                # Generate QR code
                self.generate_qr_code(motor_id)
            
            # Save to JSON
            self.progress_var.set("Saving data...")
            with open(self.json_file, 'w') as f:
                json.dump(motor_data, f, indent=4)
            
            self.progress_var.set(f"✅ Successfully imported {len(motor_data)} motors!")
            messagebox.showinfo("Success", f"Successfully imported {len(motor_data)} motors!\n\n"
                                         f"Data saved to: {self.json_file}\n"
                                         f"QR codes generated in: {self.qr_folder}/")
            
        except Exception as e:
            self.progress_var.set("❌ Import failed!")
            messagebox.showerror("Error", f"Import failed: {str(e)}")
            
    def clean_field_name(self, field):
        """Clean field names to match the system format"""
        field_mapping = {
            'sl_no': 'Sl. No.',
            'serial_no': 'Sl. No.',
            'area': 'Area / Equipment',
            'equipment': 'Area / Equipment',
            'motor_used_in': 'Motor used in',
            'application': 'Motor used in',
            'description': 'Description of Process',
            'voltage': 'Voltage (V)',
            'frequency': 'Frequency (HZ)',
            'rating_kw': 'Rating( KW)',
            'kw': 'Rating( KW)',
            'rating_hp': 'Rating (HP)',
            'hp': 'Rating (HP)',
            'flc': 'FLC',
            'frame_size': 'FRAME SIZE',
            'poles': 'Poles',
            'rpm': 'RPM',
            'duty': 'Duty',
            'connection': 'Connection',
            'insulation_class': 'Insulation class',
            'motor_type': 'Type of Motor (SQ cage, Slippring)',
            'mounting': 'Mounting (Flange, Foot, Geared, Flange cum Foot)',
            'de_bearing': 'DE bearing no',
            'nde_bearing': 'NDE bearing no',
            'make': 'Make',
            'manufacturer': 'Make',
            'serial_no_nameplate': 'Serial No as per Name plate',
            'standby': 'If Standby please mark  " Y "',
            'spare_in_hand': 'Spare in Hand',
            'spare_kept_at': 'Spare kept at',
            'last_po': 'last PO number',
            'material_code': 'Material Code',
            'pr_pending': 'Any PR pending / Date',
            'po_pending': 'Any PO pending / Date',
            'last_maintenance': 'Last Maintenance Date',
            'next_maintenance': 'Next Maintenance Date',
            'remarks': 'REMARKS'
        }
        
        # Clean the field name
        clean_field = str(field).lower().strip().replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '')
        
        # Return mapped field name or original if not found
        return field_mapping.get(clean_field, field)
        
    def convert_date(self, date_value):
        """Convert various date formats to YYYY-MM-DD"""
        if pd.isna(date_value) or date_value == '':
            return ''
        
        try:
            if isinstance(date_value, datetime):
                return date_value.strftime('%Y-%m-%d')
            
            if isinstance(date_value, str):
                for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%m-%d-%Y']:
                    try:
                        return datetime.strptime(date_value, fmt).strftime('%Y-%m-%d')
                    except ValueError:
                        continue
            
            return pd.to_datetime(date_value).strftime('%Y-%m-%d')
        except:
            return str(date_value)
            
    def generate_qr_code(self, motor_id):
        """Generate QR code for a motor"""
        qr_path = os.path.join(self.qr_folder, f"{motor_id}.png")
        if not os.path.exists(qr_path):
            qr = qrcode.make(self.base_url + motor_id)
            qr.save(qr_path)
            
    def clear_data(self):
        """Clear all data and reset form"""
        self.excel_file = None
        self.file_label.config(text="No file selected", foreground="gray")
        self.sheet_combo.set('')
        self.id_column_combo.set('')
        
        # Clear treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.progress_var.set("Ready to import")
        self.progress_bar['value'] = 0
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = ExcelImporter()
        app.run()
    except Exception as e:
        print(f"Error starting GUI: {e}")
        print("Falling back to command line version...")
        
        # Fallback to command line version
        excel_file = input("Enter Excel file path: ").strip()
        if os.path.exists(excel_file):
            # Simple command line import
            df = pd.read_excel(excel_file)
            motor_data = {}
            
            for index, row in df.iterrows():
                motor_id = f"MTR{index+1:03d}"
                motor_info = {}
                
                for col in df.columns:
                    value = row[col]
                    if pd.notna(value) and str(value).strip():
                        motor_info[col] = str(value).strip()
                
                motor_data[motor_id] = motor_info
            
            with open('motor_data.json', 'w') as f:
                json.dump(motor_data, f, indent=4)
            
            print(f"Imported {len(motor_data)} motors to motor_data.json")
        else:
            print("File not found!")

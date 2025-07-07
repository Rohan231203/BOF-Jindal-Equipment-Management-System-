import pandas as pd
import json
import os
import qrcode
from datetime import datetime

# --- Configuration ---
# The name of your Excel file. Make sure it's in the same folder as this script.
EXCEL_FILE = "MASTER MOTOR LIST OF SMS AND CASTER.xlsx"

# --- Do not change below this line ---
OUTPUT_JSON = "motor_data.json"
QR_FOLDER = "qr_codes"
BASE_URL = "https://bof-jindal-equipment-management-system.onrender.com/motor?id="  # Render deployment URL

# Labels or keywords that indicate a row should be skipped
SKIP_LABELS = {
    "x", "X", "skip", "Skip", "DELETE", "Delete", "remove", "REMOVE",
    "N/A", "na", "Na", "NULL", "null", "Null", "none", "None", "NONE",
    "0", 0, "", None
}

# These are the target field names we want in our final output
TARGET_FIELDS = [
    "Equipment", "kw", "RPM", "FLC", "V", "IP", "duty", "Insu. CL.", "PF", "%Eff",
    "Frame", "Make", "Bearing DE/NDE", "Machine Sl.no.", "Remark", "Item code", 
    "PR Number", "PO Number"
]

# Column name mappings - each target field can be found in Excel under any of these variations
COLUMN_MAPPINGS = {
    "Equipment": ["Equipment", "Motor used in", "Location", "Area", "Equipment Name"],
    "kw": ["kw", "KW", "Power", "Rating", "Rating (KW)", "Rating( KW)", "Power (kW)"],
    "RPM": ["RPM", "Speed", "Motor Speed"],
    "FLC": ["FLC", "Current", "Full Load Current", "Amps", "A", "Full Load Amps"],
    "V": ["V", "Voltage", "Supply", "Volts"],
    "IP": ["IP", "IP Rating", "Protection", "Protection Class"],
    "duty": ["Duty", "duty", "Duty Type", "Service"],
    "Insu. CL.": ["Insulation Class", "Insu. CL.", "Insulation", "Class"],
    "PF": ["PF", "Power Factor", "Cos Phi"],
    "%Eff": ["%Eff", "Efficiency", "% Efficiency", "Eff"],
    "Frame": ["Frame", "Frame Size", "Frame No"],
    "Make": ["Make", "Manufacturer", "Brand", "Company", "OEM"],
    "Bearing DE/NDE": ["Bearing DE/NDE", "DE/NDE", "Bearings", "Bearing Numbers", "DE Bearing", "NDE Bearing"],
    "Machine Sl.no.": ["Machine Sl.no.", "Serial Number", "Serial No", "Sl.No.", "Sr. No."],
    "Remark": ["Remark", "Remarks", "Comments", "Notes", "Description", "Additional Info"],
    "Item code": ["Item code", "Item Code", "Item No", "Material Code", "Part No"],
    "PR Number": ["PR Number", "PR No", "Purchase Req", "Requisition", "PR"],
    "PO Number": ["PO Number", "PO No", "Purchase Order", "Order No", "PO"]
}

def convert_to_str(value):
    """Helper to convert values to string, handling dates and empty values."""
    if pd.isna(value) or value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d')
    return str(value).strip()

def import_from_excel():
    """
    Reads the Excel file, creates motor_data.json, and generates QR codes for motors.
    """
    print(f"--- Starting Simple Excel Import ---")

    # 1. Check for the Excel file
    if not os.path.exists(EXCEL_FILE):
        print(f"\n❌ ERROR: Excel file not found!")
        print(f"Please make sure the file named '{EXCEL_FILE}' is in the same directory as this script.")
        return

    print(f"✅ Found Excel file: {EXCEL_FILE}")

    try:
        # 2. Read only the "BOF" sheet
        df = pd.read_excel(EXCEL_FILE, sheet_name="BOF")
        print(f"📄 Read {len(df)} total rows from the 'BOF' sheet.")
        
        # Print column names to help with debugging
        print(f"📊 Actual columns in BOF sheet: {list(df.columns)}")

        print(f"⚙️ Processing and cleaning rows...")

        # 3. Create the QR code folder if it doesn't exist
        os.makedirs(QR_FOLDER, exist_ok=True)
        print(f"📁 QR code folder is ready at '{QR_FOLDER}/'")

        # 4. Process and clean all rows
        motor_database = {}
        qr_generated_count = 0
        cleaned_rows = []
        
        # Create column name mapping dictionary for this specific Excel file
        col_map = {}
        for target_field, possible_names in COLUMN_MAPPINGS.items():
            for col in df.columns:
                col_str = str(col).strip()
                # Check if this column name matches any of our possible field names
                if col_str.lower() in [name.lower() for name in possible_names]:
                    col_map[target_field] = col
                    print(f"✓ Found column for {target_field}: '{col}'")
                    break
        
        # Print fields we couldn't find
        missing_fields = [f for f in TARGET_FIELDS if f not in col_map]
        if missing_fields:
            print(f"⚠️ Warning: Could not find columns for: {missing_fields}")
        
        # Process each row
        for idx, row in df.iterrows():
            # Skip section headers or empty rows
            first_val = str(row.iloc[0]).strip().lower() if not pd.isna(row.iloc[0]) else ""
            if any(keyword in first_val for keyword in ["header", "section", "title", "motor no", "ladle", "thrustor"]):
                continue
                
            # Check if the row has at least some data
            if all(pd.isna(val) for val in row):
                continue
            
            # Extract values using our column mappings
            motor_data = {}
            has_required_fields = True
            
            for target_field in TARGET_FIELDS:
                if target_field in col_map:
                    value = convert_to_str(row[col_map[target_field]])
                    motor_data[target_field] = value if value else "Nil"
                else:
                    motor_data[target_field] = "Nil"
            
            # Check for required fields
            required_fields = ["kw", "RPM", "FLC", "V", "IP"]
            for field in required_fields:
                if field in motor_data and motor_data[field] == "Nil":
                    has_required_fields = False
                    break
            
            if has_required_fields:
                # Generate unique motor ID if needed
                if "motor_id" not in motor_data or not motor_data.get("motor_id") or motor_data.get("motor_id") == "Nil":
                    motor_data["motor_id"] = f"MTR_{len(cleaned_rows) + 1:03d}"
                
                # Add standard fields expected by the site
                motor_data["motor_used_in"] = motor_data.get("Equipment", "Nil")
                motor_data["area_equipment"] = motor_data.get("Equipment", "Nil")
                motor_data["description"] = motor_data.get("Remark", "Nil")
                motor_data["critical"] = "NO"  # Default value
                
                # Add fields with names expected by the frontend/backend
                motor_data["Motor used in"] = motor_data.get("Equipment", "Nil")
                motor_data["Area / Equipment"] = motor_data.get("Equipment", "Nil") 
                motor_data["Description of Process"] = motor_data.get("Remark", "Nil")
                motor_data["Voltage (V)"] = motor_data.get("V", "Nil")
                motor_data["Rating( KW)"] = motor_data.get("kw", "Nil")
                motor_data["Frequency (HZ)"] = motor_data.get("Hz", "Nil")
                motor_data["Critical"] = "NO"  # Default value
                
                cleaned_rows.append(motor_data)
        
        print(f"✅ Found {len(cleaned_rows)} valid motors after cleaning.")
        
        # Build final database
        for i, motor_data in enumerate(cleaned_rows):
            motor_id = motor_data.get("motor_id", f"MTR_{i+1:03d}")
            
            # Generate QR code for the motor
            qr_path = os.path.join(QR_FOLDER, f"{motor_id}.png")
            if not os.path.exists(qr_path):
                qr_code = qrcode.make(BASE_URL + motor_id)
                qr_code.save(qr_path)
                qr_generated_count += 1
                
            # Store in database
            motor_database[motor_id] = motor_data
        
        print(f"⚙️ Processed {len(motor_database)} unique motors with valid data.")
        if qr_generated_count > 0:
            print(f"📱 Generated {qr_generated_count} new QR codes.")
        else:
            print("✔️ All QR codes already existed.")

        # 5. Save the processed data to the JSON file
        with open(OUTPUT_JSON, "w") as f:
            json.dump(motor_database, f, indent=4)

        print(f"💾 Database successfully created at '{OUTPUT_JSON}'")
        print("\n--- ✅ Import Complete! ---")
        print("You can now start the web server by running the 'start_server.bat' file.")

    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        print("Please check that your Excel file is not corrupted and the BOF sheet exists.")

if __name__ == "__main__":
    # This allows the script to be run directly from the command line.
    import_from_excel()

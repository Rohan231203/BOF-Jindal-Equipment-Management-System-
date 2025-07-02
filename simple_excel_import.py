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
BASE_URL = "https://your-railway-app-name.up.railway.app/motor?id="  # Update with your actual Railway URL

def convert_to_str(value):
    """Helper to convert values to string, handling dates and empty values."""
    if pd.isna(value) or value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d')
    return str(value).strip()

def import_from_excel():
    """
    Reads the Excel file, creates motor_data.json, and generates QR codes for the first 100 motors.
    A unique motor ID will be generated for each entry (e.g., MTR_001, MTR_002).
    """
    print(f"--- Starting Simple Excel Import ---")

    # 1. Check for the Excel file
    if not os.path.exists(EXCEL_FILE):
        print(f"\n❌ ERROR: Excel file not found!")
        print(f"Please make sure the file named '{EXCEL_FILE}' is in the same directory as this script.")
        return

    print(f"✅ Found Excel file: {EXCEL_FILE}")

    try:
        # 2. Read the Excel file
        df = pd.read_excel(EXCEL_FILE, sheet_name=0) # Read the first sheet
        print(f"📄 Read {len(df)} total rows from the Excel file.")

        # Limit to the first 100 rows
        if len(df) > 100:
            print("⚠️ Processing only the first 100 motors as requested.")
            df = df.head(100)
        
        print(f"⚙️ Processing {len(df)} rows.")

        # 3. Create the QR code folder if it doesn't exist
        os.makedirs(QR_FOLDER, exist_ok=True)
        print(f"📁 QR code folder is ready at '{QR_FOLDER}/'")

        # 4. Process all rows
        motor_database = {}
        qr_generated_count = 0

        for index, row in df.iterrows():
            # Generate a new unique ID for every motor, e.g., MTR_001, MTR_002
            motor_id = f"MTR_{index + 1:03d}"
            
            # Create a dictionary for the motor's data, ensuring all values are strings
            motor_details = {header: convert_to_str(row.get(header)) for header in df.columns}
            
            # Add the generated motor ID to the details as well, for reference
            motor_details["Generated Motor ID"] = motor_id
            # Ensure 'Critical' field exists and defaults to 'NO' if missing or empty
            if not motor_details.get("Critical"):
                motor_details["Critical"] = "NO"
            
            motor_database[motor_id] = motor_details

            # Generate a QR code for the motor
            qr_path = os.path.join(QR_FOLDER, f"{motor_id}.png")
            if not os.path.exists(qr_path):
                qr_code = qrcode.make(BASE_URL + motor_id)
                qr_code.save(qr_path)
                qr_generated_count += 1
        
        print(f"⚙️ Processed {len(motor_database)} unique motors with generated IDs.")
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
        print("Please check that your Excel file is not corrupted and the column names are correct.")

if __name__ == "__main__":
    # This allows the script to be run directly from the command line.
    import_from_excel()

import pandas as pd
import json
import qrcode
import os
from datetime import datetime

# Configuration
EXCEL_FILE = "motor_data.xlsx"  # Change this to your Excel file name
JSON_FILE = "motor_data.json"
QR_FOLDER = "qr_codes"
BASE_URL = "http://localhost:8000/motor?id="

# Create QR folder if it doesn't exist
os.makedirs(QR_FOLDER, exist_ok=True)

def clean_field_name(field):
    """Clean field names to match the system format"""
    field_mapping = {
        'sl_no': 'Sl. No.',
        'serial_no': 'Sl. No.',
        'sl.no': 'Sl. No.',
        'sl no': 'Sl. No.',
        'area': 'Area / Equipment',
        'equipment': 'Area / Equipment',
        'area_equipment': 'Area / Equipment',
        'motor_used_in': 'Motor used in',
        'used_in': 'Motor used in',
        'application': 'Motor used in',
        'description': 'Description of Process',
        'process_description': 'Description of Process',
        'voltage': 'Voltage (V)',
        'voltage_v': 'Voltage (V)',
        'frequency': 'Frequency (HZ)',
        'frequency_hz': 'Frequency (HZ)',
        'rating_kw': 'Rating( KW)',
        'power_kw': 'Rating( KW)',
        'kw': 'Rating( KW)',
        'rating_hp': 'Rating (HP)',
        'power_hp': 'Rating (HP)',
        'hp': 'Rating (HP)',
        'flc': 'FLC',
        'full_load_current': 'FLC',
        'frame_size': 'FRAME SIZE',
        'poles': 'Poles',
        'rpm': 'RPM',
        'duty': 'Duty',
        'connection': 'Connection',
        'insulation_class': 'Insulation class',
        'motor_type': 'Type of Motor (SQ cage, Slippring)',
        'type': 'Type of Motor (SQ cage, Slippring)',
        'mounting': 'Mounting (Flange, Foot, Geared, Flange cum Foot)',
        'de_bearing': 'DE bearing no',
        'de_bearing_no': 'DE bearing no',
        'nde_bearing': 'NDE bearing no',
        'nde_bearing_no': 'NDE bearing no',
        'make': 'Make',
        'manufacturer': 'Make',
        'serial_no_nameplate': 'Serial No as per Name plate',
        'nameplate_serial': 'Serial No as per Name plate',
        'standby': 'If Standby please mark  " Y "',
        'is_standby': 'If Standby please mark  " Y "',
        'spare_in_hand': 'Spare in Hand',
        'spare_location': 'Spare kept at',
        'spare_kept_at': 'Spare kept at',
        'last_po': 'last PO number',
        'po_number': 'last PO number',
        'material_code': 'Material Code',
        'pr_pending': 'Any PR pending / Date',
        'po_pending': 'Any PO pending / Date',
        'last_maintenance': 'Last Maintenance Date',
        'last_maintenance_date': 'Last Maintenance Date',
        'next_maintenance': 'Next Maintenance Date',
        'next_maintenance_date': 'Next Maintenance Date',
        'remarks': 'REMARKS',
        'comments': 'REMARKS'
    }
    
    # Clean the field name
    clean_field = str(field).lower().strip().replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '')
    
    # Return mapped field name or original if not found
    return field_mapping.get(clean_field, field)

def generate_qr_code(motor_id):
    """Generate QR code for a motor"""
    qr_path = os.path.join(QR_FOLDER, f"{motor_id}.png")
    if not os.path.exists(qr_path):
        qr = qrcode.make(BASE_URL + motor_id)
        qr.save(qr_path)
        print(f"✅ Generated QR code for {motor_id}")

def convert_date(date_value):
    """Convert various date formats to YYYY-MM-DD"""
    if pd.isna(date_value) or date_value == '':
        return ''
    
    try:
        # If it's already a datetime object
        if isinstance(date_value, datetime):
            return date_value.strftime('%Y-%m-%d')
        
        # Try to parse string dates
        if isinstance(date_value, str):
            # Common date formats
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%m-%d-%Y']:
                try:
                    return datetime.strptime(date_value, fmt).strftime('%Y-%m-%d')
                except ValueError:
                    continue
        
        # If it's a pandas timestamp
        return pd.to_datetime(date_value).strftime('%Y-%m-%d')
    except:
        return str(date_value)

def import_from_excel():
    """Import motor data from Excel file"""
    
    print("🔄 Starting Excel import process...")
    
    # Check if Excel file exists
    if not os.path.exists(EXCEL_FILE):
        print(f"❌ Error: Excel file '{EXCEL_FILE}' not found!")
        print("Please make sure your Excel file is in the same folder as this script.")
        return False
    
    try:
        # Read Excel file
        print(f"📖 Reading Excel file: {EXCEL_FILE}")
        df = pd.read_excel(EXCEL_FILE)
        
        print(f"📊 Found {len(df)} rows in Excel file")
        print(f"📋 Columns found: {list(df.columns)}")
        
        # Initialize motor data dictionary
        motor_data = {}
        
        # Process each row
        for index, row in df.iterrows():
            motor_id = None
            motor_info = {}
            
            # Process each column
            for col in df.columns:
                value = row[col]
                
                # Skip empty values
                if pd.isna(value) or value == '':
                    continue
                
                # Clean field name
                clean_col = clean_field_name(col)
                
                # Check if this could be a motor ID
                if motor_id is None and ('id' in col.lower() or 'motor' in col.lower() or col.lower() in ['sl. no.', 'sl_no', 'serial']):
                    motor_id = str(value).strip()
                    continue
                
                # Handle date fields
                if 'date' in clean_col.lower():
                    value = convert_date(value)
                
                # Store the cleaned value
                motor_info[clean_col] = str(value).strip()
            
            # If no motor ID found, use row number
            if motor_id is None or motor_id == '':
                motor_id = f"MTR{index+1:03d}"
            
            # Store motor data
            motor_data[motor_id] = motor_info
            
            # Generate QR code
            generate_qr_code(motor_id)
            
            print(f"✅ Processed motor: {motor_id}")
        
        # Save to JSON file
        with open(JSON_FILE, 'w') as f:
            json.dump(motor_data, f, indent=4)
        
        print(f"🎉 Successfully imported {len(motor_data)} motors!")
        print(f"💾 Data saved to: {JSON_FILE}")
        print(f"📱 QR codes generated in: {QR_FOLDER}/")
        
        # Show sample data
        print("\n📋 Sample imported data:")
        for i, (motor_id, data) in enumerate(motor_data.items()):
            if i >= 3:  # Show only first 3 entries
                break
            print(f"  {motor_id}: {len(data)} fields")
            for key, value in list(data.items())[:5]:  # Show first 5 fields
                print(f"    {key}: {value}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error during import: {str(e)}")
        return False

def show_field_mapping():
    """Show available field mappings"""
    print("\n🗺️  Field Mapping Guide:")
    print("Your Excel columns will be automatically mapped to system fields.")
    print("Common mappings include:")
    print("  - 'Motor ID', 'ID', 'Sl No' → Motor ID")
    print("  - 'Area', 'Equipment' → Area / Equipment")
    print("  - 'Voltage' → Voltage (V)")
    print("  - 'KW', 'Power KW' → Rating( KW)")
    print("  - 'HP', 'Power HP' → Rating (HP)")
    print("  - 'Make', 'Manufacturer' → Make")
    print("  - 'Last Maintenance' → Last Maintenance Date")
    print("  - 'Next Maintenance' → Next Maintenance Date")
    print("  - etc.")

if __name__ == "__main__":
    print("🔧 Motor QR System - Excel Import Tool")
    print("=" * 50)
    
    # Show instructions
    print("📋 Instructions:")
    print("1. Place your Excel file in this folder")
    print("2. Rename it to 'motor_data.xlsx' or update EXCEL_FILE variable")
    print("3. Run this script")
    print()
    
    # Show field mapping guide
    show_field_mapping()
    print()
    
    # Get Excel file name from user
    excel_file = input(f"📁 Enter Excel file name (default: {EXCEL_FILE}): ").strip()
    if excel_file:
        EXCEL_FILE = excel_file
    
    # Start import process
    success = import_from_excel()
    
    if success:
        print("\n🎯 Next Steps:")
        print("1. Start your FastAPI server: uvicorn main:app --reload")
        print("2. Open http://localhost:8000")
        print("3. Check your imported motors")
        print("4. Print QR codes from the qr_codes folder")
    else:
        print("\n❌ Import failed. Please check your Excel file and try again.")
    
    input("\nPress Enter to exit...")

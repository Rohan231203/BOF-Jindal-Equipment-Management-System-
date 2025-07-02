# 📊 Excel to Motor Database Import Guide

## 🚀 Quick Start (3 Methods Available)

### Method 1: GUI Import Tool (Recommended) 🖱️
```cmd
python excel_import_gui.py
```
- User-friendly interface
- Preview your data before import
- Select specific sheets and columns
- Real-time progress tracking

### Method 2: Command Line Import 💻
```cmd
python excel_import.py
```
- Automatic field mapping
- Batch processing
- Command line interface

### Method 3: One-Click Import 🎯
```cmd
import_excel.bat
```
- Double-click to run
- Installs dependencies automatically
- Runs command line version

---

## 📋 Preparing Your Excel File

### Required Setup:
1. **Motor ID Column**: Must have a unique identifier for each motor
   - Examples: "Motor ID", "Sl. No.", "Serial No.", "ID"
   - Should contain unique values like: MTR001, PUMP001, FAN001

2. **Supported Column Names** (auto-detected):
   ```
   Basic Information:
   - Motor ID, ID, Sl. No., Serial No.
   - Area, Equipment, Area/Equipment
   - Motor Used In, Application, Usage
   - Description, Process Description
   
   Electrical Specifications:
   - Voltage, Voltage (V)
   - Frequency, Frequency (HZ)
   - Rating KW, Power KW, KW
   - Rating HP, Power HP, HP
   - FLC, Full Load Current
   - Connection
   
   Mechanical Specifications:
   - Frame Size
   - Poles
   - RPM
   - Duty
   - Insulation Class
   - Motor Type, Type
   - Mounting
   
   Bearings:
   - DE Bearing, DE Bearing No
   - NDE Bearing, NDE Bearing No
   
   Manufacturer:
   - Make, Manufacturer
   - Serial No Nameplate
   - Standby, Is Standby
   
   Inventory:
   - Spare in Hand
   - Spare Location, Spare Kept At
   - Last PO, PO Number
   - Material Code
   - PR Pending
   - PO Pending
   
   Maintenance:
   - Last Maintenance, Last Maintenance Date
   - Next Maintenance, Next Maintenance Date
   - Remarks, Comments
   ```

### Excel File Format:
- **Supported**: .xlsx, .xls
- **Structure**: First row should contain column headers
- **Data**: Each row represents one motor
- **Dates**: Use format YYYY-MM-DD, DD/MM/YYYY, or MM/DD/YYYY

---

## 🔧 Step-by-Step Import Process

### Step 1: Prepare Your Excel File
```
Motor ID | Area/Equipment | Voltage | Rating KW | Make | Last Maintenance
---------|----------------|---------|-----------|------|------------------
MTR001   | Pump House     | 415V    | 5.5       | ABB  | 2024-01-15
MTR002   | Compressor     | 415V    | 15        | WEG  | 2024-02-10
```

### Step 2: Run Import Tool
```cmd
# For GUI version (recommended)
python excel_import_gui.py

# For command line version
python excel_import.py
```

### Step 3: Select Your File
- Browse and select your Excel file
- Choose the correct sheet (if multiple sheets exist)
- Select the Motor ID column
- Preview your data

### Step 4: Import Data
- Click "Import Data" button
- Wait for processing to complete
- QR codes will be generated automatically

### Step 5: Verify Import
- Check `motor_data.json` file created
- Verify QR codes in `qr_codes/` folder
- Start your FastAPI server to view data

---

## 🎯 Import Results

After successful import, you'll get:

1. **motor_data.json**: All motor data in JSON format
2. **qr_codes/*.png**: QR code for each motor
3. **Import log**: Shows number of motors processed

### Example Output:
```
✅ Successfully imported 150 motors!
💾 Data saved to: motor_data.json
📱 QR codes generated in: qr_codes/
```

---

## 🔍 Field Mapping Examples

The system automatically maps your Excel columns to the database fields:

| Excel Column | → | Database Field |
|--------------|---|----------------|
| Motor ID | → | Motor ID (primary key) |
| Area | → | Area / Equipment |
| Voltage | → | Voltage (V) |
| KW | → | Rating( KW) |
| HP | → | Rating (HP) |
| Make | → | Make |
| Last Service | → | Last Maintenance Date |
| Next Service | → | Next Maintenance Date |

---

## ⚠️ Common Issues & Solutions

### Issue 1: "File not found"
**Solution**: Make sure Excel file is in the same folder as the import script

### Issue 2: "No Motor ID column detected"
**Solution**: 
- Ensure you have a column with motor identifiers
- Use column names like: "Motor ID", "ID", "Sl. No."
- Each motor must have a unique identifier

### Issue 3: "Import failed"
**Solution**:
- Check Excel file for corruption
- Ensure file is not open in Excel
- Verify file permissions

### Issue 4: "Date format error"
**Solution**:
- Use standard date formats: YYYY-MM-DD, DD/MM/YYYY
- Ensure date cells are formatted as dates in Excel

---

## 🚀 After Import

1. **Start your server**:
   ```cmd
   uvicorn main:app --reload
   ```

2. **Access your system**:
   - Open: http://localhost:8000
   - Check imported motors
   - Verify data accuracy

3. **Print QR codes**:
   - QR codes are in `qr_codes/` folder
   - Print and attach to physical motors
   - Each QR links directly to motor details

4. **Set up maintenance schedule**:
   - Update "Next Maintenance Date" for each motor
   - Use dashboard to monitor upcoming maintenance

---

## 📞 Need Help?

If you encounter issues:
1. Check this guide first
2. Verify your Excel file format
3. Try the GUI version for better error messages
4. Ensure all dependencies are installed:
   ```cmd
   pip install -r requirements.txt
   ```

Happy importing! 🎉

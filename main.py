import os
import json
import qrcode
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional

app = FastAPI()

# Constants
DATA_FILE = "motor_data.json"
QR_FOLDER = "qr_codes"
TEMPLATES_DIR = "templates"
PASSWORD = "admin123"
PASSWORD2=""
BASE_URL = "https://your-railway-app-name.up.railway.app/motor?id="  # Update with your actual Railway URL

# Setup folders
os.makedirs(QR_FOLDER, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/qr_codes", StaticFiles(directory=QR_FOLDER), name="qr_codes")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Helper functions
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_motors_needing_maintenance():
    """Get motors that need maintenance within the next 7 days or are overdue."""
    data = load_data()
    critical_motors_due = []
    motors_due = []
    today = datetime.now()
    
    for motor_id, motor_data in data.items():
        next_maintenance = motor_data.get("Next Maintenance Date")
        if next_maintenance:
            try:
                maintenance_date = datetime.strptime(next_maintenance, "%Y-%m-%d")
                days_until = (maintenance_date - today).days
                if days_until <= 7: # Show overdue and upcoming maintenance
                    motor_info = {
                        "motor_id": motor_id,
                        "days_until": days_until,
                        "maintenance_date": next_maintenance,
                        "area_equipment": motor_data.get("Area / Equipment", "N/A"),
                        "motor_used_in": motor_data.get("Motor used in", "N/A"),
                        "description": motor_data.get("Description of Process", "N/A"),
                        "voltage": motor_data.get("Voltage (V)", "N/A"),
                        "rating_kw": motor_data.get("Rating( KW)", "N/A"),
                        "last_maintenance": motor_data.get("Last Maintenance Date", "N/A"),
                        "Critical": motor_data.get("Critical", "NO")
                    }
                    if motor_info["Critical"] == "YES":
                        critical_motors_due.append(motor_info)
                    else:
                        motors_due.append(motor_info)
            except ValueError:
                continue
    
    return (
        sorted(critical_motors_due, key=lambda x: x["days_until"]),
        sorted(motors_due, key=lambda x: x["days_until"])
    )

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    data = load_data()
    # Create a list of motor info for better display
    motor_info_list = []
    for motor_id in data.keys():
        motor_data = data[motor_id]
        motor_info = {
            "motor_id": motor_id,
            "motor_used_in": motor_data.get("Motor used in", "N/A"),
            "description": motor_data.get("Description of Process", "N/A"),
            "area_equipment": motor_data.get("Area / Equipment", "N/A"),
            "critical": motor_data.get("Critical", "NO")
        }
        motor_info_list.append(motor_info)
    
    return templates.TemplateResponse("home.html", {
        "request": request, 
        "motor_list": data.keys(),
        "motor_info_list": motor_info_list
    })

@app.get("/dashboard", response_class=HTMLResponse)
async def maintenance_dashboard(request: Request):
    motors_due = get_motors_needing_maintenance()
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "motors_due": motors_due,
        "total_motors": len(load_data())
    })

@app.post("/add_motor")
async def add_motor(request: Request, motor_id: str = Form(...)):
    data = load_data()

    if motor_id in data:
        return HTMLResponse("<h3>Motor ID already exists!</h3>", status_code=400)

    data[motor_id] = {}
    save_data(data)

    # Generate QR only if not exists
    qr_path = os.path.join(QR_FOLDER, f"{motor_id}.png")
    if not os.path.exists(qr_path):
        qr = qrcode.make(BASE_URL + motor_id)
        qr.save(qr_path)

    return RedirectResponse(f"/motor?id={motor_id}", status_code=302)

@app.get("/motor", response_class=HTMLResponse)
async def view_motor(request: Request, id: str):
    data = load_data()
    motor_data = data.get(id, {})
    return templates.TemplateResponse("motor.html", {
        "request": request,
        "motor_id": id,
        "motor_data": motor_data
    })

@app.post("/update")
async def update_motor(request: Request):
    form_data = await request.form()
    motor_id = form_data.get("motor_id")
    password = form_data.get("password")

    if not motor_id or not password:
        return HTMLResponse("<h2>❌ Missing Motor ID or Password</h2>", status_code=422)

    if password != PASSWORD:
        return HTMLResponse("<h2>❌ Unauthorized - Incorrect Password</h2>", status_code=401)

    data = load_data()
    
    if motor_id not in data:
        return HTMLResponse("<h2>❌ Motor ID not found in database</h2>", status_code=404)

    # Get the existing data for the motor
    motor_data = data.get(motor_id, {})
    
    # Iterate through all submitted form fields and update the data
    for key, value in form_data.items():
        # Skip the fields we handle separately
        if key in ["motor_id", "password"]:
            continue
        motor_data[key] = value.strip()
    
    # Save the updated motor data back to the main dictionary
    data[motor_id] = motor_data
    save_data(data)

    return RedirectResponse(f"/motor?id={motor_id}", status_code=302)

@app.get("/issues", response_class=HTMLResponse)
async def issues_dashboard(request: Request):
    """Dashboard to view all motor issues and their status"""
    data = load_data()
    motors_with_issues = []
    
    for motor_id, motor_data in data.items():
        issue_description = motor_data.get("Issue Description", "").strip()
        if issue_description:  # Only include motors that have issues recorded
            motor_info = {
                "motor_id": motor_id,
                "motor_used_in": motor_data.get("Motor used in", "N/A"),
                "area_equipment": motor_data.get("Area / Equipment", "N/A"),
                "issue_description": issue_description,
                "issue_date": motor_data.get("Issue Date", "N/A"),
                "issue_raised_by": motor_data.get("Issue Raised By", "N/A"),
                "solved_by": motor_data.get("Solved By", "N/A"),
                "date_solved": motor_data.get("Date Solved", "N/A"),
                "solution_description": motor_data.get("Solution Description", "N/A"),
                "issue_status": motor_data.get("Issue Status", "Open"),
                "critical": motor_data.get("Critical", "NO")
            }
            motors_with_issues.append(motor_info)
    
    # Sort by issue date (newest first), then by status
    motors_with_issues.sort(key=lambda x: (x["issue_status"] != "Open", x["issue_date"]), reverse=True)
    
    return templates.TemplateResponse("issues.html", {
        "request": request,
        "motors_with_issues": motors_with_issues,
        "total_issues": len(motors_with_issues),
        "open_issues": len([m for m in motors_with_issues if m["issue_status"] == "Open"]),
        "resolved_issues": len([m for m in motors_with_issues if m["issue_status"] in ["Resolved", "Closed"]])
    })

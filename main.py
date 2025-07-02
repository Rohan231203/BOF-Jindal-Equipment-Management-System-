import os
import json
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
import uuid

# Constants
DATA_FILE = "motor_data.json"
QR_FOLDER = "qr_codes"
TEMPLATES_DIR = "templates"
PASSWORD = os.environ.get("MOTOR_ADMIN_PASSWORD", "admin123")  # Use environment variable in production
PASSWORD2=""
BASE_URL = "https://bof-jindal-equipment-management-system.onrender.com/motor?id="  # Render deployment URL

# Try to import qrcode, but don't fail if it's not available
try:
    import qrcode
    QR_CODE_AVAILABLE = True
except ImportError:
    QR_CODE_AVAILABLE = False
    print("Warning: QR code functionality is disabled - qrcode package not available")

app = FastAPI()

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
    motor_info_list = []
    for motor_id, motor_data in data.items():
        motor_info_list.append({
            "motor_id": motor_id,
            "motor_used_in": motor_data.get("Motor Used In", "N/A"),
            "area_equipment": motor_data.get("Area/Equipment", "N/A"),
            "description": motor_data.get("Motor Description", ""),
            "critical": motor_data.get("Critical", "NO")
        })
    
    return templates.TemplateResponse("home.html", {
        "request": request, 
        "motor_info_list": motor_info_list
    })

@app.get("/dashboard", response_class=HTMLResponse)
async def maintenance_dashboard(request: Request):
    motors_due = get_motors_needing_maintenance()
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "critical_motors_due": motors_due[0],
        "other_motors_due": motors_due[1],
        "total_motors": len(load_data())
    })

@app.post("/add_motor")
async def add_motor(request: Request, motor_id: str = Form(...)):
    data = load_data()

    if motor_id in data:
        return HTMLResponse("<h3>Motor ID already exists!</h3>", status_code=400)

    data[motor_id] = {}
    save_data(data)

    # Generate QR only if not exists and QR code library is available
    qr_path = os.path.join(QR_FOLDER, f"{motor_id}.png")
    if not os.path.exists(qr_path) and QR_CODE_AVAILABLE:
        qr_code = qrcode.make(BASE_URL + motor_id)
        qr_code.save(qr_path)

    return RedirectResponse(f"/motor?id={motor_id}", status_code=302)

@app.get("/motor", response_class=HTMLResponse)
async def view_motor(request: Request, id: str):
    data = load_data()
    motor_data = data.get(id, {})
    return templates.TemplateResponse("motor.html", {
        "request": request,
        "motor_id": id,
        "motor_data": motor_data,
        "issues": motor_data.get("issues", []),
        "maintenance_records": motor_data.get("maintenance_records", [])
    })

@app.post("/update_motor_details")
async def update_motor_details(request: Request):
    form_data = await request.form()
    motor_id = form_data.get("motor_id")
    password = form_data.get("password")

    if not motor_id or not password:
        raise HTTPException(status_code=400, detail="Motor ID and password are required.")

    if password != PASSWORD:
        raise HTTPException(status_code=403, detail="Invalid password.")

    data = load_data()
    
    if motor_id not in data:
        raise HTTPException(status_code=404, detail="Motor not found.")

    motor_data = data.get(motor_id, {})
    
    # Exclude issue and maintenance fields from this update
    excluded_keys = [
        "issue_description", "issue_date", "issue_raised_by", "issue_status", 
        "issue_solved_by", "issue_solution_date", "password", "motor_id"
    ]

    for key, value in form_data.items():
        if key not in excluded_keys:
            motor_data[key] = value
    
    data[motor_id] = motor_data
    save_data(data)

    return RedirectResponse(f"/motor?id={motor_id}", status_code=302)

@app.post("/add_issue/{motor_id}")
async def add_issue(request: Request, motor_id: str):
    form_data = await request.form()
    data = load_data()

    if motor_id not in data:
        raise HTTPException(status_code=404, detail="Motor not found.")

    new_issue = {
        "id": str(uuid.uuid4()),
        "description": form_data.get("issue_description"),
        "date_raised": datetime.now().strftime("%Y-%m-%d"),
        "raised_by": form_data.get("issue_raised_by"),
        "status": "Open"
    }

    if "issues" not in data[motor_id]:
        data[motor_id]["issues"] = []
    
    data[motor_id]["issues"].append(new_issue)
    save_data(data)

    return RedirectResponse(f"/motor?id={motor_id}", status_code=303)

@app.post("/update_issue/{motor_id}/{issue_id}")
async def update_issue(request: Request, motor_id: str, issue_id: str):
    form_data = await request.form()
    data = load_data()

    if motor_id not in data or "issues" not in data[motor_id]:
        raise HTTPException(status_code=404, detail="Motor or issue list not found.")

    issue_to_update = next((issue for issue in data[motor_id]["issues"] if issue["id"] == issue_id), None)

    if not issue_to_update:
        raise HTTPException(status_code=404, detail="Issue not found.")

    issue_to_update["status"] = form_data.get("status")
    if form_data.get("status") in ["InProgress", "Resolved"]:
        issue_to_update["solved_by"] = form_data.get("solved_by")
        if form_data.get("status") == "Resolved":
            issue_to_update["solution_date"] = datetime.now().strftime("%Y-%m-%d")

    save_data(data)
    return RedirectResponse(f"/motor?id={motor_id}", status_code=303)

@app.post("/add_maintenance/{motor_id}")
async def add_maintenance(request: Request, motor_id: str):
    form_data = await request.form()
    data = load_data()

    if motor_id not in data:
        raise HTTPException(status_code=404, detail="Motor not found.")

    new_record = {
        "id": str(uuid.uuid4()),
        "description": form_data.get("maintenance_description"),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "performed_by": form_data.get("performed_by")
    }

    if "maintenance_records" not in data[motor_id]:
        data[motor_id]["maintenance_records"] = []

    data[motor_id]["maintenance_records"].append(new_record)
    save_data(data)

    return RedirectResponse(f"/motor?id={motor_id}", status_code=303)

@app.get("/issues", response_class=HTMLResponse)
async def issues_dashboard(request: Request):
    """Dashboard to view all motor issues and their status"""
    data = load_data()
    motors_with_issues = []
    
    for motor_id, motor_data in data.items():
        if "issues" in motor_data:
            for issue in motor_data["issues"]:
                motors_with_issues.append({
                    "motor_id": motor_id,
                    "motor_used_in": motor_data.get("Motor Used In"),
                    "area_equipment": motor_data.get("Area/Equipment"),
                    "issue_description": issue.get("description"),
                    "issue_date": issue.get("date_raised"),
                    "issue_raised_by": issue.get("raised_by"),
                    "issue_status": issue.get("status"),
                    "issue_solved_by": issue.get("solved_by"),
                    "issue_solution_date": issue.get("solution_date"),
                    "critical": motor_data.get("Critical", "NO")
                })
    
    # Sort by issue date (newest first), then by status
    motors_with_issues.sort(key=lambda x: (x["issue_status"] != "Open", x.get("issue_date", "")), reverse=True)

    return templates.TemplateResponse("issues.html", {
        "request": request,
        "motors_with_issues": motors_with_issues
    })

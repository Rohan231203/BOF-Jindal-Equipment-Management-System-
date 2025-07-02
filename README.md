# Motor QR Management System

A comprehensive web-based motor management and maintenance tracking system with QR code integration for industrial environments.

## 📋 Project Overview

The Motor QR Management System is a FastAPI-based application designed to streamline the management, maintenance, and troubleshooting of industrial motors. By assigning each motor a unique QR code, technicians can quickly access detailed information, maintenance schedules, and issue tracking for any motor in the facility using their mobile devices.

## ✨ Key Features

- **QR Code Integration**: Scan QR codes to instantly access motor details
- **Comprehensive Motor Database**: Store extensive details including electrical specifications, mechanical data, and maintenance history
- **Maintenance Dashboard**: View motors due for maintenance with critical/non-critical classification
- **Issues Tracking**: Document and track motor problems, resolutions, and maintenance history
- **Mobile-Friendly Interface**: Responsive design for easy access on mobile devices in industrial environments
- **Excel Import**: Bulk import motor data from Excel spreadsheets
- **Critical Equipment Tracking**: Separate tracking for critical vs. non-critical equipment

## 🛠️ Technical Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML, CSS, JavaScript with Jinja2 Templates
- **Data Storage**: JSON file-based storage
- **QR Technology**: Python qrcode library
- **Data Import**: Pandas for Excel processing

## 📱 Use Cases

1. **Maintenance Technicians**: Scan motor QR codes to view specifications and history
2. **Maintenance Planners**: Use the dashboard to plan preventive maintenance activities
3. **Engineers**: Track issues and solutions to identify recurring problems
4. **Management**: Get an overview of critical equipment status and maintenance compliance

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Excel file with motor data (for initial import)

### Local Installation

1. Clone this repository
2. Install requirements: `pip install -r requirements.txt`
3. Import motor data: `python simple_excel_import.py`
4. Start the server: `uvicorn main:app --reload`
5. Access the application at `http://localhost:8000`

### Deployment

See the [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions on deploying to Railway.app.

## 📱 Mobile Experience

The application is designed with industrial environments in mind:
- Compact navigation with icon-based menus
- Responsive forms that work well on smaller screens
- Quick access to critical information with minimal scrolling
- Clear visual indicators for maintenance status and critical equipment

## 📊 Dashboards

- **Maintenance Dashboard**: Shows motors due for maintenance in the next 7 days, separated into critical and non-critical categories
- **Issues Dashboard**: Displays all motors with reported issues, filterable by status and priority

## 📄 License

[MIT License](LICENSE)

## 🙏 Acknowledgments

- Built with FastAPI and Jinja2
- QR code generation using qrcode library
- Excel processing with pandas

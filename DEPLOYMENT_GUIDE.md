# Motor QR Management System - Deployment Guide

This guide will walk you through the steps to deploy your FastAPI Motor QR management application on Render.com.

## Prerequisites

- GitHub account
- Railway.app account (can sign up with GitHub)
- Git installed on your computer

## Step 1: Prepare Your Project for GitHub

1. Create a new GitHub repository
2. Initialize Git in your project folder:

```
cd c:\Users\HP\Desktop\Motor_qr
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

## Step 2: Deploy to Render

1. Go to [Render.com](https://render.com/) and log in with your GitHub account
2. Click "New" > "Web Service"
3. Select your repository from the list
4. Configure as follows:
   - **Name**: `BOF-Jindal-Equipment-Management-System`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`
5. Add Environment Variable for security:
   - Click on "Environment" tab
   - Add a key-value pair: `MOTOR_ADMIN_PASSWORD` = `your-secure-password`
   - This will override the default password in the code for better security
6. Click "Create Web Service" and wait for the deployment to complete
7. Once deployed, Render will provide you with a URL for your app (e.g., https://your-app-name.onrender.com)

## Step 3: Update BASE_URL in your code

After deployment, you need to update your BASE_URL in both main.py and simple_excel_import.py with your actual Render URL:

```python
BASE_URL = "https://bof-jindal-equipment-management-system.onrender.com/motor?id="
```

Commit and push these changes:

```
git add .
git commit -m "Update BASE_URL for production"
git push
```

Railway will automatically redeploy with the changes.

## Step 4: QR Code Management

You have two options for QR code management:

### Option 1: Generate QR codes locally, then deploy

1. Set the correct BASE_URL in simple_excel_import.py to your Railway URL
2. Run the Excel import script locally:
   ```
   python simple_excel_import.py
   ```
3. Add the generated QR codes to your git repository:
   ```
   git add qr_codes/*.png
   git commit -m "Add generated QR codes"
   git push
   ```

### Option 2: Generate QR codes after deployment

1. After deploying to Render, get shell access:
   - Go to your project in Render dashboard
   - Click on the "Shell" tab
   - Run your Excel import script:
     ```
     python simple_excel_import.py
     ```

   Note: This option may be limited on Render's free tier, so Option 1 (generating QR codes locally) is recommended.

## Step 5: Print and Distribute QR Codes

1. Once QR codes are generated, you can access them via the `/qr_codes/` path on your deployed app
2. Download and print the QR codes for each motor
3. Attach the QR codes to the physical motors

## Troubleshooting

- If QR codes don't work, double-check that the BASE_URL is correctly set and updated
- Make sure the 'qr_codes' directory exists and is accessible in your deployed app
- Check Render logs for any errors during deployment or runtime
- If you're having issues with dependencies, try using specific older versions in requirements.txt

## Maintenance

- To update your application, make changes locally, commit to git, and push to GitHub
- Render will automatically redeploy your application with the new changes
- Remember that Render's free tier has limitations - your service may go to sleep after periods of inactivity

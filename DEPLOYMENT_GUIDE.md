# Motor QR Management System - Deployment Guide

This guide will walk you through the steps to deploy your FastAPI Motor QR management application on Railway.app.

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

## Step 2: Deploy to Railway

1. Go to [Railway.app](https://railway.app/) and log in with your GitHub account
2. Click "New Project" > "Deploy from GitHub repo"
3. Select your repository from the list
4. Railway will automatically detect your Procfile and requirements.txt
5. Wait for the deployment to complete
6. Once deployed, go to Settings and find your domain (e.g., https://your-app-name.up.railway.app)

## Step 3: Update BASE_URL in your code

After deployment, you need to update your BASE_URL in both main.py and simple_excel_import.py with your actual Railway URL:

```python
BASE_URL = "https://your-app-name.up.railway.app/motor?id="
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

1. After deploying to Railway, get shell access:
   - Go to your project in Railway dashboard
   - Click on the "Shell" tab
   - Run your Excel import script:
     ```
     python simple_excel_import.py
     ```

## Step 5: Print and Distribute QR Codes

1. Once QR codes are generated, you can access them via the `/qr_codes/` path on your deployed app
2. Download and print the QR codes for each motor
3. Attach the QR codes to the physical motors

## Troubleshooting

- If QR codes don't work, double-check that the BASE_URL is correctly set and updated
- Make sure the 'qr_codes' directory exists and is accessible in your deployed app
- Check Railway logs for any errors during deployment or runtime

## Maintenance

- To update your application, make changes locally, commit to git, and push to GitHub
- Railway will automatically redeploy your application with the new changes

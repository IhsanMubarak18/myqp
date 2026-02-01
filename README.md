# 📘 Question Paper Generator

## Local Development Setup Guide (Code Version)

This guide explains how to **run the project locally using source code** (NOT the installer).

## 🧰 1. SYSTEM REQUIREMENTS (MUST HAVE)

Ask your group members to install these **before anything else**.

### ✅ Required Versions (Important)

Tool			->		Version

Python		->	 3.10.x

Node.js   -> 	18.x (LTS)

npm       -> 	Comes with Node

Git       -> Latest

⚠️ Node **12 is NOT supported** for Electron.


🧑‍💻 2. CLONE THE PROJECT

git clone <YOUR_GIT_REPO_URL>
cd question_paper_app


(Replace repo URL with your actual one.)




## 🐍 3. PYTHON VIRTUAL ENVIRONMENT

### Create virtual environment

python3 -m venv app_env

### Activate it
Linux / macOS
#### Windows
app_env\Scripts\activate

## 📦 4. INSTALL PYTHON DEPENDENCIES

pip install --upgrade pip
pip install -r requirements.txt

Verify:
python -m django --version

Expected:
5.2.5

## 🗄️ 5. DATABASE SETUP
python manage.py migrate

## 📁 6. MEDIA & STATIC FOLDERS (IMPORTANT)

Create these folders manually if not present:

mkdir -p media/generated
mkdir -p static

## 🧪 7. TEST DJANGO ALONE (VERY IMPORTANT)
python manage.py runserver
Open browser:

http://127.0.0.1:8000 

Admin:

http://127.0.0.1:8000/admin 

⚠️ **Do NOT continue if this doesn’t work**

Press `Ctrl + C` to stop.

## ⚡ 8. NODE + ELECTRON SETUP

### Go to Electron root (where package.json is)

cd Question-_paper_new 

### Install Node dependencies

npm install 

⚠️ If errors → check Node version:

node -v 

Must be **v18.x**

## 🖥️ 9. RUN DESKTOP APP (DEVELOPMENT MODE)

npm run dev 

What happens:

1.  Electron starts
    
2.  Django server auto-starts
    
3.  Loading screen appears
    
4.  App UI opens
    

✅ This is the **desktop app running with code**

## 🛠️ 10. COMMON COMMANDS (CHEAT SHEET)

Purpose

Command

Run Django only    ->    python manage.py runserver

Run Desktop app    ->    npm run dev

Build installer    ->    npm run build

Activate venv      ->    source app_env/bin/activate


## 👨‍💼 11. ADMIN ACCESS (IMPORTANT)

Admin panel:

`http://127.0.0.1:8000/admin` 

-   Admin manages dropdowns
    
-   Users do not login
    
-   All data stored **locally per system**


## 📦 12. BUILD INSTALLER (OPTIONAL)

npm run build 

Generated file:

dist/
 └── Question  Paper  Generator-1.0.0.AppImage
Send **ONLY that file** to users.

----------

## 🚨 13. COMMON ERRORS & FIXES

### ❌ Node version too old

sudo apt remove nodejs sudo apt install nodejs npm 

Or use **nvm (recommended)**.

----------

### ❌ Media file not found

Ensure:

media/generated/ 

exists.

----------

### ❌ App stuck on loading

-   Django failed to start
    
-   Run `python manage.py runserver` manually to see error
    

----------## 🧠 IMPORTANT DESIGN NOTES (FOR YOUR TEAM)

✔ Offline desktop app  
✔ No hosting required  
✔ Each system has its own data  
✔ Admin settings are local  
✔ No internet needed after install

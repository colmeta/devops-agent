@echo off
REM DevOps Agent Windows Setup Script
echo ╔══════════════════════════════════════════════════════════════╗
echo ║  DevOps Automation Agent - Windows Quick Start              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+
    pause
    exit /b 1
)
echo ✅ Python found

REM Create virtual environment if not exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ⚠️ Virtual environment exists, skipping...
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate

REM Install requirements
echo 📥 Installing dependencies...
pip install playwright aiohttp python-dotenv requests flask authlib psycopg2-binary sqlalchemy python-dateutil pydantic colorlog gunicorn

REM Install Playwright browsers
echo 🌐 Installing Playwright browsers...
playwright install chromium

REM Create .gitignore
echo 📝 Creating .gitignore...
(
echo # Environment
echo venv/
echo .env
echo credentials.json
echo *.log
echo.
echo # Python
echo __pycache__/
echo *.py[cod]
echo *$py.class
echo *.so
echo .Python
echo build/
echo dist/
echo *.egg-info/
echo.
echo # IDE
echo .vscode/
echo .idea/
echo *.swp
echo.
echo # OS
echo .DS_Store
echo Thumbs.db
) > .gitignore

REM Create .env.example
echo 📝 Creating .env.example...
(
echo # Meta WhatsApp Business API
echo META_APP_ID=your_app_id
echo META_APP_SECRET=your_app_secret
echo META_ACCESS_TOKEN=your_access_token
echo META_VERIFY_TOKEN=your_verify_token
echo META_PHONE_NUMBER_ID=your_phone_number_id
echo META_PORT=3000
echo.
echo # Google OAuth
echo GOOGLE_OAUTH_CLIENT_ID=your_client_id
echo GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret
echo.
echo # Microsoft OAuth
echo MICROSOFT_OAUTH_CLIENT_ID=your_client_id
echo MICROSOFT_OAUTH_CLIENT_SECRET=your_client_secret
echo.
echo # Flowise
echo FLOWISE_API_KEY=your_api_key
echo FLOWISE_URL=http://localhost:3000
echo.
echo # Render
echo RENDER_API_KEY=your_render_api_key
echo RENDER_SERVICE_ID=your_service_id
echo.
echo # GitHub
echo GITHUB_USERNAME=colmeta
echo GITHUB_REPO=clarity-pearl-production
echo GITHUB_TOKEN=your_github_personal_access_token
) > .env.example

REM Create README
echo 📝 Creating README...
(
echo # DevOps Automation Agent
echo.
echo Automates service setup, credential extraction, and deployment.
echo.
echo ## Quick Start
echo.
echo ```bash
echo # Run setup
echo setup.bat
echo.
echo # Start the agent
echo python devops_agent.py
echo ```
echo.
echo ## Features
echo.
echo - ✅ Meta WhatsApp Business API setup
echo - ✅ Google OAuth ^(Sign In with Google^)
echo - ✅ Microsoft OAuth ^(Sign In with Outlook^)
echo - ✅ Automatic credential storage
echo - ✅ GitHub integration and auto-push
echo - ✅ One-click Render deployment
echo.
echo ## Costs
echo.
echo - **Playwright**: $0 ^(runs locally^)
echo - **WhatsApp**: First 1,000 messages FREE
echo - **OAuth**: $0 ^(unlimited^)
) > README.md

REM Create Procfile
echo 📝 Creating Procfile...
echo web: gunicorn whatsapp_webhook:app > Procfile

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║  🎉 Setup Complete!                                          ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo ✅ Virtual environment: venv\
echo ✅ Dependencies: installed
echo ✅ Playwright: ready
echo ✅ Project files: created
echo.
echo 📋 Next steps:
echo    1. python devops_agent.py
echo    2. Follow the interactive menu
echo.
echo 💰 Costs:
echo    • Playwright: $0 ^(runs on your machine^)
echo    • WhatsApp: First 1,000 messages FREE
echo    • OAuth: $0 ^(unlimited authentications^)
echo.
pause
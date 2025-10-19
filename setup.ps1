# VAMedRec - Complete Setup Script
# Run this from the project root directory

Write-Host "`n🏥 VAMedRec - VA Medication Reconciliation System - Complete Setup" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

$projectRoot = "C:\Users\VHAWRJDRESCF\OneDrive - Department of Veterans Affairs\Documents\GitHub\med-reconciliation"

# Check if we're in the right directory
if (-not (Test-Path "$projectRoot\config.py")) {
    Write-Host "❌ Error: Please run this script from the project root directory" -ForegroundColor Red
    Write-Host "Expected: $projectRoot" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n✅ Project directory confirmed" -ForegroundColor Green

# Step 1: Check Python
Write-Host "`n📦 Step 1: Checking Python installation..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Python not found. Please install Python 3.9+" -ForegroundColor Red
    exit 1
}

# Step 2: Create virtual environment
Write-Host "`n📦 Step 2: Creating virtual environment..." -ForegroundColor Cyan
if (Test-Path "venv") {
    Write-Host "  ⚠ Virtual environment already exists" -ForegroundColor Yellow
    $recreate = Read-Host "  Recreate it? (y/N)"
    if ($recreate -eq 'y' -or $recreate -eq 'Y') {
        Remove-Item -Recurse -Force venv
        python -m venv venv
        Write-Host "  ✓ Virtual environment recreated" -ForegroundColor Green
    }
} else {
    python -m venv venv
    Write-Host "  ✓ Virtual environment created" -ForegroundColor Green
}

# Step 3: Activate and install dependencies
Write-Host "`n📦 Step 3: Installing dependencies..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"
pip install --upgrade pip | Out-Null
pip install -r requirements.txt
Write-Host "  ✓ Dependencies installed" -ForegroundColor Green

# Step 4: Create .env file
Write-Host "`n📦 Step 4: Setting up environment file..." -ForegroundColor Cyan
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "  ✓ Created .env file from template" -ForegroundColor Green
    Write-Host "  ⚠ IMPORTANT: Edit .env and add your OPENAI_API_KEY" -ForegroundColor Yellow
} else {
    Write-Host "  ⚠ .env file already exists" -ForegroundColor Yellow
}

# Step 5: Create remaining Python files (if they don't exist)
Write-Host "`n📦 Step 5: Checking for missing files..." -ForegroundColor Cyan

$filesToCheck = @(
    "core\reconciler.py",
    "tools\safety_checks.py",
    "tools\ledger.py",
    "tools\formulary.py",
    "main.py"
)

$missingFiles = @()
foreach ($file in $filesToCheck) {
    if (-not (Test-Path $file)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "  ⚠ Missing files detected:" -ForegroundColor Yellow
    foreach ($file in $missingFiles) {
        Write-Host "    - $file" -ForegroundColor Yellow
    }
    Write-Host "`n  Please ensure all Python files are created." -ForegroundColor Yellow
} else {
    Write-Host "  ✓ All core files present" -ForegroundColor Green
}

# Summary
Write-Host "`n" + ("=" * 70) -ForegroundColor Cyan
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host ("=" * 70) -ForegroundColor Cyan

Write-Host "`n📋 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Edit .env file and add your OpenAI API key:" -ForegroundColor White
Write-Host "     notepad .env" -ForegroundColor Yellow
Write-Host "`n  2. Activate virtual environment:" -ForegroundColor White
Write-Host "     .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host "`n  3. Run the application:" -ForegroundColor White
Write-Host "     python main.py" -ForegroundColor Yellow
Write-Host "`n  4. Open browser to:" -ForegroundColor White
Write-Host "     http://localhost:5000" -ForegroundColor Yellow

Write-Host "`n💡 For testing, see examples\example_request.json" -ForegroundColor Cyan
Write-Host ""

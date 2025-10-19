# VAMedRec - Test Script - Verify Installation

Write-Host "`n🧪 Testing VAMedRec - VA Medication Reconciliation System" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

$projectRoot = "C:\Users\VHAWRJDRESCF\OneDrive - Department of Veterans Affairs\Documents\GitHub\med-reconciliation"
cd $projectRoot

# Test 1: Check all required files
Write-Host "`n✅ Test 1: Checking required files..." -ForegroundColor Cyan
$requiredFiles = @(
    "config.py",
    "main.py",
    "requirements.txt",
    ".env.example",
    "core\__init__.py",
    "core\normalizer.py",
    "core\model_engine.py",
    "core\reconciler.py",
    "tools\safety_checks.py",
    "tools\ledger.py",
    "tools\formulary.py",
    "prompts\simple_prompt.txt",
    "prompts\comprehensive_prompt.txt"
)

$allFilesPresent = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file (MISSING)" -ForegroundColor Red
        $allFilesPresent = $false
    }
}

if ($allFilesPresent) {
    Write-Host "`n✅ All required files present!" -ForegroundColor Green
} else {
    Write-Host "`n❌ Some files are missing!" -ForegroundColor Red
    exit 1
}

# Test 2: Check Python
Write-Host "`n✅ Test 2: Checking Python..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found" -ForegroundColor Red
    exit 1
}

# Test 3: Check virtual environment
Write-Host "`n✅ Test 3: Checking virtual environment..." -ForegroundColor Cyan
if (Test-Path "venv\Scripts\python.exe") {
    Write-Host "  ✓ Virtual environment exists" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Virtual environment not found. Run setup.ps1 first." -ForegroundColor Yellow
}

# Test 4: Check .env file
Write-Host "`n✅ Test 4: Checking environment configuration..." -ForegroundColor Cyan
if (Test-Path ".env") {
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "OPENAI_API_KEY=sk-") {
        Write-Host "  ✓ .env file configured with API key" -ForegroundColor Green
    } elseif ($envContent -match "OPENAI_API_KEY=your-api-key-here") {
        Write-Host "  ⚠ .env file exists but API key not set" -ForegroundColor Yellow
        Write-Host "    Edit .env and add your OpenAI API key" -ForegroundColor Yellow
    } else {
        Write-Host "  ⚠ .env file exists but may need configuration" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⚠ .env file not found. Copy from .env.example" -ForegroundColor Yellow
}

# Test 5: Python syntax check
Write-Host "`n✅ Test 5: Checking Python syntax..." -ForegroundColor Cyan
$pythonFiles = Get-ChildItem -Path . -Filter "*.py" -Recurse
$syntaxErrors = $false
foreach ($file in $pythonFiles) {
    $result = python -m py_compile $file.FullName 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ✗ Syntax error in $($file.Name)" -ForegroundColor Red
        $syntaxErrors = $true
    }
}
if (-not $syntaxErrors) {
    Write-Host "  ✓ All Python files have valid syntax" -ForegroundColor Green
}

# Summary
Write-Host "`n" + ("=" * 70) -ForegroundColor Cyan
Write-Host "📊 Test Summary" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan

if ($allFilesPresent -and -not $syntaxErrors) {
    Write-Host "`n✅ All tests passed! System is ready." -ForegroundColor Green
    Write-Host "`n📋 Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Configure .env with your API key" -ForegroundColor White
    Write-Host "  2. Run: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host "  3. Run: python main.py" -ForegroundColor Yellow
    Write-Host "  4. Open: http://localhost:5000" -ForegroundColor Yellow
} else {
    Write-Host "`n⚠️ Some issues found. Please review above." -ForegroundColor Yellow
}

Write-Host ""

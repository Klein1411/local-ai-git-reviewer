# Script cai dat moi truong cho git-ai va Ollama
Write-Host "Bat dau thiet lap moi truong cho git-ai..." -ForegroundColor Cyan

# 1. Thiet lap bien moi truong OLLAMA_MODELS sang o D vinh vien
$envVarName = "OLLAMA_MODELS"
$envVarValue = "D:\OllamaModels"

Write-Host "Dang cau hinh $envVarName thanh $envVarValue ..."
[System.Environment]::SetEnvironmentVariable($envVarName, $envVarValue, [System.EnvironmentVariableTarget]::User)

# Tao thu muc neu chua co
if (-Not (Test-Path $envVarValue)) {
    New-Item -ItemType Directory -Force -Path $envVarValue | Out-Null
    Write-Host "Da tao thu muc chua model tai $envVarValue" -ForegroundColor Green
} else {
    Write-Host "Thu muc $envVarValue da ton tai." -ForegroundColor Yellow
}

# 2. Huong dan cai dat Ollama
Write-Host "`n--- HUONG DAN CAI DAT OLLAMA ---" -ForegroundColor Cyan
Write-Host "1. Tai Ollama cho Windows tai: https://ollama.com/download/OllamaSetup.exe"
Write-Host "2. Chay file cai dat."
Write-Host "3. Sau khi cai xong, mo mot cua so Terminal MOI (de nhan bien moi truong)."
Write-Host "4. Chay lenh sau de tai model (Vua van 4GB VRAM cua RTX 3050):" -ForegroundColor Yellow
Write-Host "   ollama run qwen2.5:3b" -ForegroundColor Green
Write-Host "--------------------------------" -ForegroundColor Cyan

# 3. Huong dan cai dat project
Write-Host "`n--- HUONG DAN CAI DAT GIT-AI ---" -ForegroundColor Cyan
Write-Host "1. Chuyen vao thu muc du an: cd D:\local-ai-git-reviewer"
Write-Host "2. Cai dat cac goi phu thuoc bang Pip hoac Poetry:"
Write-Host "   pip install -e ."
Write-Host "   hoac"
Write-Host "   poetry install"
Write-Host "3. Su dung lenh 'git-ai' de chay cong cu." -ForegroundColor Green
Write-Host "Hoan tat thiet lap co ban!" -ForegroundColor Magenta

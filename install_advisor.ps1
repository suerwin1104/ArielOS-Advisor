# Ariel OS v1.5 Advisor 雲端大腦部署腳本
Write-Host "🧬 正在依照 v1.5 規範部署「專業顧問」系統..." -ForegroundColor Cyan

# 1. 建立符合規範的物理目錄 (文件第 1 章)
$Root = "$HOME\ArielOS_Advisor"
$Dirs = @("backups", "plugins", "memory", "credentials")
foreach ($d in $Dirs) { 
    $path = Join-Path $Root $d
    if (!(Test-Path $path)) { New-Item -ItemType Directory -Path $path | Out-Null } 
}
Set-Location $Root

# 2. 寫入環境變數 (Discord Token)
$Token = Read-Host "👉 請輸入您的 Discord Token"
"DISCORD_TOKEN=$Token" | Out-File -FilePath .env -Encoding utf8

# 3. 從您的 Advisor 倉庫下載檔案 (這裡假設您已上傳)
# 注意：這裡要改成您 GitHub 上的 Advisor 分支網址
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/suerwin1104/ArielOS_Advisor/main/ariel_main.py" -OutFile "ariel_main.py"
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/suerwin1104/ArielOS_Advisor/main/evolver.py" -OutFile "evolver.py"
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/suerwin1104/ArielOS/main/ariel_launcher.py" -OutFile "ariel_launcher.py"

# 4. 啟動容器
docker-compose up -d
Write-Host "✅ Advisor 系統已啟動。請進入 Discord 輸入 !系統初始化 開啟 28 歲成人禮。" -ForegroundColor Green
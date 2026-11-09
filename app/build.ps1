# 打包學習精靈（階段 1 第四批，Owner 決定 1A 壓縮檔）
#
# 在 app 資料夾執行：
#   powershell -ExecutionPolicy Bypass -File .\build.ps1
#
# 會做：跑測試（沒過就停）→ 產生圖示 → PyInstaller 打包 → 放入使用說明 → 壓縮成 dist\學習精靈-版本.zip
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

$version = & $py -c "import leveling; print(leveling.__version__)"
Write-Host "== 學習精靈 $version"

Write-Host "== 1/4 跑測試"
& $py -m pytest -q -p no:cacheprovider
if ($LASTEXITCODE -ne 0) { throw "測試沒通過，不打包" }

Write-Host "== 2/4 產生圖示"
$icon = Join-Path $PSScriptRoot "build\icon.ico"
& $py tools\make_icon.py $icon
if ($LASTEXITCODE -ne 0) { throw "圖示產生失敗" }

Write-Host "== 3/4 PyInstaller 打包"
$data = Join-Path $PSScriptRoot "data"
& $py -m PyInstaller --noconfirm --clean --windowed `
    --name "學習精靈" `
    --icon $icon `
    --add-data "$data;data" `
    --distpath (Join-Path $PSScriptRoot "dist") `
    --workpath (Join-Path $PSScriptRoot "build\pyinstaller") `
    --specpath (Join-Path $PSScriptRoot "build") `
    main.py
if ($LASTEXITCODE -ne 0) { throw "PyInstaller 打包失敗" }

Write-Host "== 4/4 放入使用說明、壓縮"
$out = Join-Path $PSScriptRoot "dist\學習精靈"
Copy-Item "packaging\使用說明.txt" $out -Force
$zip = Join-Path $PSScriptRoot "dist\學習精靈-$version.zip"
if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path $out -DestinationPath $zip

$mb = [math]::Round((Get-Item $zip).Length / 1MB, 1)
Write-Host "== 完成：$zip（$mb MB）"

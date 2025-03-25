$envName = "lambda_env"
$buildDir = "lambda_build"
$zipFile = "lambda_function.zip"
$reqFile = "requirements.txt"

Write-Host "`n🧼 Cleaning up old build and zip..." -ForegroundColor Yellow
if (Test-Path $buildDir) { Remove-Item $buildDir -Recurse -Force }
if (Test-Path $zipFile) { Remove-Item $zipFile -Force }

Write-Host "`n📁 Creating build directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $buildDir | Out-Null

Write-Host "`n📦 Installing dependencies into build dir..." -ForegroundColor Cyan
pip install -r $reqFile -t $buildDir

Write-Host "`n📄 Copying source files..." -ForegroundColor Cyan

# Explicitly copy folders to preserve directory structure
New-Item -ItemType Directory -Path "$buildDir\APIs" | Out-Null
Copy-Item -Path .\APIs\* -Destination "$buildDir\APIs" -Recurse

New-Item -ItemType Directory -Path "$buildDir\DB" | Out-Null
Copy-Item -Path .\DB\* -Destination "$buildDir\DB" -Recurse

New-Item -ItemType Directory -Path "$buildDir\utils" | Out-Null
Copy-Item -Path .\utils\* -Destination "$buildDir\utils" -Recurse

Copy-Item .\main.py, .\baseAPI.py -Destination $buildDir

Write-Host "`n🗜️ Zipping into $zipFile..." -ForegroundColor Green
Compress-Archive -Path "$buildDir\*" -DestinationPath $zipFile -Force

Write-Host "`n✅ Done! Upload $zipFile to AWS Lambda." -ForegroundColor Green

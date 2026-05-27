# 开发工具安装脚本 - 国内镜像版
Write-Host "========================================" -ForegroundColor Green
Write-Host "开发工具安装脚本 (国内镜像版)" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

$downloadDir = "$env:TEMP\devtools-install"
New-Item -ItemType Directory -Force -Path $downloadDir | Out-Null

# 1. Node.js
Write-Host "`n[1/4] 正在下载 Node.js..." -ForegroundColor Cyan
$nodeUrl = "https://cdn.npmmirror.com/binaries/node/v20.11.1/node-v20.11.1-x64.msi"
$nodePath = "$downloadDir\nodejs.msi"
try {
    Invoke-WebRequest -Uri $nodeUrl -OutFile $nodePath -UseBasicParsing -TimeoutSec 300
    Write-Host "   正在安装..." -ForegroundColor Yellow
    Start-Process msiexec.exe -ArgumentList "/i `"$nodePath`" /quiet /norestart" -Wait
    Write-Host "   Node.js 安装完成!" -ForegroundColor Green
} catch {
    Write-Host "   失败: $_" -ForegroundColor Red
}

# 2. Git
Write-Host "`n[2/4] 正在下载 Git..." -ForegroundColor Cyan
$gitUrl = "https://registry.npmmirror.com/-/binary/git-for-windows/v2.44.0.windows.1/Git-2.44.0-64-bit.exe"
$gitPath = "$downloadDir\git.exe"
try {
    Invoke-WebRequest -Uri $gitUrl -OutFile $gitPath -UseBasicParsing -TimeoutSec 300
    Write-Host "   正在安装..." -ForegroundColor Yellow
    Start-Process $gitPath -ArgumentList "/SILENT" -Wait
    Write-Host "   Git 安装完成!" -ForegroundColor Green
} catch {
    Write-Host "   失败: $_" -ForegroundColor Red
}

# 3. Java
Write-Host "`n[3/4] 正在下载 Java JDK..." -ForegroundColor Cyan
$javaUrl = "https://mirrors.tuna.tsinghua.edu.cn/Adoptium/17/jdk/x64/windows/OpenJDK17U-jdk_x64_windows_hotspot_17.0.10_7.msi"
$javaPath = "$downloadDir\java.msi"
try {
    Invoke-WebRequest -Uri $javaUrl -OutFile $javaPath -UseBasicParsing -TimeoutSec 300
    Write-Host "   正在安装..." -ForegroundColor Yellow
    Start-Process msiexec.exe -ArgumentList "/i `"$javaPath`" /quiet /norestart" -Wait
    Write-Host "   Java JDK 安装完成!" -ForegroundColor Green
} catch {
    Write-Host "   失败: $_" -ForegroundColor Red
}

# 4. .NET
Write-Host "`n[4/4] 正在下载 .NET SDK..." -ForegroundColor Cyan
$dotnetUrl = "https://download.visualstudio.microsoft.com/download/pr/5e6d9578-3876-4f96-8085-1d0594942579/c268a23c29e06c1e6b4279d0f5f5d0a4/dotnet-sdk-8.0.204-win-x64.exe"
$dotnetPath = "$downloadDir\dotnet.exe"
try {
    Invoke-WebRequest -Uri $dotnetUrl -OutFile $dotnetPath -UseBasicParsing -TimeoutSec 300
    Write-Host "   正在安装..." -ForegroundColor Yellow
    Start-Process $dotnetPath -ArgumentList "/install /quiet /norestart" -Wait
    Write-Host "   .NET SDK 安装完成!" -ForegroundColor Green
} catch {
    Write-Host "   失败: $_" -ForegroundColor Red
}

# 清理
Write-Host "`n正在清理临时文件..." -ForegroundColor Yellow
Remove-Item -Path $downloadDir -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "安装完成! 请打开新的PowerShell窗口验证:" -ForegroundColor Yellow
Write-Host "  node --version" -ForegroundColor White
Write-Host "  npm --version" -ForegroundColor White
Write-Host "  git --version" -ForegroundColor White
Write-Host "  java -version" -ForegroundColor White
Write-Host "  dotnet --version" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Green

# 开发工具安装脚本
# 需要管理员权限运行
Write-Host "正在准备安装开发工具..." -ForegroundColor Green

# 创建临时下载目录
$downloadDir = "$env:TEMP\devtools-install"
New-Item -ItemType Directory -Force -Path $downloadDir | Out-Null

Write-Host "`n1. 正在下载 Node.js LTS..." -ForegroundColor Cyan
$nodeUrl = "https://nodejs.org/dist/v20.11.1/node-v20.11.1-x64.msi"
$nodePath = "$downloadDir\nodejs.msi"
try {
    Invoke-WebRequest -Uri $nodeUrl -OutFile $nodePath -UseBasicParsing
    Write-Host "   下载完成,正在安装..." -ForegroundColor Green
    Start-Process msiexec.exe -ArgumentList "/i $nodePath /quiet /norestart" -Wait
    Write-Host "   Node.js 安装完成!" -ForegroundColor Green
} catch {
    Write-Host "   Node.js 下载或安装失败: $_" -ForegroundColor Red
}

Write-Host "`n2. 正在下载 Git..." -ForegroundColor Cyan
$gitUrl = "https://github.com/git-for-windows/git/releases/download/v2.44.0.windows.1/Git-2.44.0-64-bit.exe"
$gitPath = "$downloadDir\git.exe"
try {
    Invoke-WebRequest -Uri $gitUrl -OutFile $gitPath -UseBasicParsing
    Write-Host "   下载完成,正在安装..." -ForegroundColor Green
    Start-Process $gitPath -ArgumentList "/SILENT" -Wait
    Write-Host "   Git 安装完成!" -ForegroundColor Green
} catch {
    Write-Host "   Git 下载或安装失败: $_" -ForegroundColor Red
}

Write-Host "`n3. 正在下载 Java (Eclipse Temurin 17)..." -ForegroundColor Cyan
$javaUrl = "https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.10%2B7/OpenJDK17U-jdk_x64_windows_hotspot_17.0.10_7.msi"
$javaPath = "$downloadDir\java.msi"
try {
    Invoke-WebRequest -Uri $javaUrl -OutFile $javaPath -UseBasicParsing
    Write-Host "   下载完成,正在安装..." -ForegroundColor Green
    Start-Process msiexec.exe -ArgumentList "/i $javaPath /quiet /norestart" -Wait
    Write-Host "   Java 安装完成!" -ForegroundColor Green
} catch {
    Write-Host "   Java 下载或安装失败: $_" -ForegroundColor Red
}

Write-Host "`n4. 正在下载 .NET SDK 8..." -ForegroundColor Cyan
$dotnetUrl = "https://download.visualstudio.microsoft.com/download/pr/5e6d9578-3876-4f96-8085-1d0594942579/c268a23c29e06c1e6b4279d0f5f5d0a4/dotnet-sdk-8.0.204-win-x64.exe"
$dotnetPath = "$downloadDir\dotnet.exe"
try {
    Invoke-WebRequest -Uri $dotnetUrl -OutFile $dotnetPath -UseBasicParsing
    Write-Host "   下载完成,正在安装..." -ForegroundColor Green
    Start-Process $dotnetPath -ArgumentList "/install /quiet /norestart" -Wait
    Write-Host "   .NET SDK 安装完成!" -ForegroundColor Green
} catch {
    Write-Host "   .NET SDK 下载或安装失败: $_" -ForegroundColor Red
}

# 清理临时文件
Write-Host "`n正在清理临时文件..." -ForegroundColor Yellow
Remove-Item -Path $downloadDir -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "安装脚本执行完成!" -ForegroundColor Green
Write-Host "请打开新的 PowerShell 窗口验证安装:" -ForegroundColor Yellow
Write-Host "  node --version" -ForegroundColor White
Write-Host "  npm --version" -ForegroundColor White
Write-Host "  git --version" -ForegroundColor White
Write-Host "  java -version" -ForegroundColor White
Write-Host "  dotnet --version" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Green

# OpenRelay下载脚本
# 自动下载最新版本的OpenRelay Windows可执行文件

$ErrorActionPreference = "Stop"

# 下载URL
$downloadUrl = "https://github.com/romgX/openrelay/releases/latest/download/openrelay-windows-x64.exe"
$outputFile = "openrelay-windows-x64.exe"

Write-Host "正在下载OpenRelay..." -ForegroundColor Yellow
Write-Host "下载URL: $downloadUrl"

try {
    # 使用Invoke-WebRequest下载文件
    Invoke-WebRequest -Uri $downloadUrl -OutFile $outputFile
    
    if (Test-Path $outputFile) {
        $fileSize = (Get-Item $outputFile).Length
        Write-Host "下载成功！" -ForegroundColor Green
        Write-Host "文件: $outputFile ($($fileSize/1MB -as [int]) MB)"
        Write-Host ""
        Write-Host "使用说明:"
        Write-Host "1. 双击 $outputFile 启动OpenRelay"
        Write-Host "2. 或在命令行运行: .\$outputFile"
        Write-Host "3. 浏览器打开: http://localhost:18765"
    } else {
        Write-Host "下载失败，文件不存在" -ForegroundColor Red
    }
} catch {
    Write-Host "下载失败: $_" -ForegroundColor Red
}
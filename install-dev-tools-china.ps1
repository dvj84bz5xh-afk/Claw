# 开发工具安装脚本 - 使用国内镜像
# 需要管理员权限运行

Write-Host "========================================" -ForegroundColor Green
Write-Host "开发工具安装脚本 (国内镜像版)" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# 创建临时下载目录
$downloadDir = "$env:TEMP\devtools-install"
New-Item -ItemType Directory -Force -Path $downloadDir | Out-Null

# 设置进度条样式
$ProgressPreference = 'Continue'

# ==================== 1. Node.js ====================
Write-Host "`n[1/4] 正在下载 Node.js LTS (淘宝镜像)..." -ForegroundColor Cyan
$nodeVersion = "v20.11.1"
$nodeUrl = "https://cdn.npmmirror.com/binaries/node/$nodeVersion/node-$nodeVersion-x64.msi"
$nodePath = "$downloadDir\nodejs.msi"

try {
    Write-Host "   下载地址: $nodeUrl" -ForegroundColor Gray
    Invoke-WebRequest -Uri $nodeUrl -OutFile $nodePath -UseBasicParsing -TimeoutSec 300
    
    if (Test-Path $nodePath) {
        $fileSize = (Get-Item $nodePath).Length / 1MB
        Write-Host "   下载完成: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Green
        Write-Host "   正在安装 Node.js..." -ForegroundColor Yellow
        
        $process = Start-Process msiexec.exe -ArgumentList "/i `"$nodePath`" /quiet /norestart" -Wait -PassThru
        if ($process.ExitCode -eq 0) {
            Write-Host "   ✅ Node.js 安装成功!" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️ 安装可能未完成,退出码: $($process.ExitCode)" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "   ❌ Node.js 下载失败: $_" -ForegroundColor Red
}

# ==================== 2. Git ====================
Write-Host "`n[2/4] 正在下载 Git (淘宝镜像)..." -ForegroundColor Cyan
$gitVersion = "2.44.0"
$gitUrl = "https://registry.npmmirror.com/-/binary/git-for-windows/v$gitVersion.windows.1/Git-$gitVersion-64-bit.exe"
$gitPath = "$downloadDir\git.exe"

try {
    Write-Host "   下载地址: $gitUrl" -ForegroundColor Gray
    Invoke-WebRequest -Uri $gitUrl -OutFile $gitPath -UseBasicParsing -TimeoutSec 300
    
    if (Test-Path $gitPath) {
        $fileSize = (Get-Item $gitPath).Length / 1MB
        Write-Host "   下载完成: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Green
        Write-Host "   正在安装 Git..." -ForegroundColor Yellow
        
        # Git 安装参数: /SILENT = 静默安装, /COMPONENTS = 组件选择
        $process = Start-Process $gitPath -ArgumentList "/SILENT","/COMPONENTS=`"icons,ext,ext\shellhere,ext\guihere,assoc,assoc_sh`"" -Wait -PassThru
        if ($process.ExitCode -eq 0) {
            Write-Host "   ✅ Git 安装成功!" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️ 安装可能未完成,退出码: $($process.ExitCode)" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "   ❌ Git 下载失败: $_" -ForegroundColor Red
}

# ==================== 3. Java JDK ====================
Write-Host "`n[3/4] 正在下载 Java JDK 17 (清华镜像)..." -ForegroundColor Cyan
$javaVersion = "17.0.10_7"
$javaUrl = "https://mirrors.tuna.tsinghua.edu.cn/Adoptium/17/jdk/x64/windows/OpenJDK17U-jdk_x64_windows_hotspot_$javaVersion.msi"
$javaPath = "$downloadDir\java.msi"

try {
    Write-Host "   下载地址: $javaUrl" -ForegroundColor Gray
    Invoke-WebRequest -Uri $javaUrl -OutFile $javaPath -UseBasicParsing -TimeoutSec 300
    
    if (Test-Path $javaPath) {
        $fileSize = (Get-Item $javaPath).Length / 1MB
        Write-Host "   下载完成: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Green
        Write-Host "   正在安装 Java JDK..." -ForegroundColor Yellow
        
        $process = Start-Process msiexec.exe -ArgumentList "/i `"$javaPath`" /quiet /norestart" -Wait -PassThru
        if ($process.ExitCode -eq 0) {
            Write-Host "   ✅ Java JDK 安装成功!" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️ 安装可能未完成,退出码: $($process.ExitCode)" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "   ❌ Java JDK 下载失败: $_" -ForegroundColor Red
}

# ==================== 4. .NET SDK ====================
Write-Host "`n[4/4] 正在下载 .NET SDK 8 (微软中国CDN)..." -ForegroundColor Cyan
$dotnetVersion = "8.0.204"
$dotnetUrl = "https://download.visualstudio.microsoft.com/download/pr/5e6d9578-3876-4f96-8085-1d0594942579/c268a23c29e06c1e6b4279d0f5f5d0a4/dotnet-sdk-$dotnetVersion-win-x64.exe"
$dotnetPath = "$downloadDir\dotnet.exe"

try {
    Write-Host "   下载地址: $dotnetUrl" -ForegroundColor Gray
    Invoke-WebRequest -Uri $dotnetUrl -OutFile $dotnetPath -UseBasicParsing -TimeoutSec 300
    
    if (Test-Path $dotnetPath) {
        $fileSize = (Get-Item $dotnetPath).Length / 1MB
        Write-Host "   下载完成: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Green
        Write-Host "   正在安装 .NET SDK..." -ForegroundColor Yellow
        
        $process = Start-Process $dotnetPath -ArgumentList "/install","/quiet","/norestart" -Wait -PassThru
        if ($process.ExitCode -eq 0) {
            Write-Host "   ✅ .NET SDK 安装成功!" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️ 安装可能未完成,退出码: $($process.ExitCode)" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "   ❌ .NET SDK 下载失败: $_" -ForegroundColor Red
}

# ==================== 清理和验证 ====================
Write-Host "`n========================================" -ForegroundColor Yellow
Write-Host "正在清理临时文件..." -ForegroundColor Yellow
Remove-Item -Path $downloadDir -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "清理完成!" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "安装完成! 正在验证..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# 刷新环境变量
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

# 验证安装
Write-Host "`n验证结果:" -ForegroundColor Cyan

# Node.js
try {
    $nodeVer = & node --version 2>$null
    if ($nodeVer) {
        Write-Host "  ✅ Node.js: $nodeVer" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Node.js: 未找到" -ForegroundColor Red
    }
} catch {
    Write-Host "  ❌ Node.js: 未安装" -ForegroundColor Red
}

# npm
try {
    $npmVer = & npm --version 2>$null
    if ($npmVer) {
        Write-Host "  ✅ npm: $npmVer" -ForegroundColor Green
    } else {
        Write-Host "  ❌ npm: 未找到" -ForegroundColor Red
    }
} catch {
    Write-Host "  ❌ npm: 未安装" -ForegroundColor Red
}

# Git
try {
    $gitVer = & git --version 2>$null
    if ($gitVer) {
        Write-Host "  ✅ Git: $gitVer" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Git: 未找到" -ForegroundColor Red
    }
} catch {
    Write-Host "  ❌ Git: 未安装" -ForegroundColor Red
}

# Java
try {
    $javaVer = & java -version 2>&1 | Select-Object -First 1
    if ($javaVer) {
        Write-Host "  ✅ Java: $javaVer" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Java: 未找到" -ForegroundColor Red
    }
} catch {
    Write-Host "  ❌ Java: 未安装" -ForegroundColor Red
}

# .NET
try {
    $dotnetVer = & dotnet --version 2>$null
    if ($dotnetVer) {
        Write-Host "  ✅ .NET SDK: $dotnetVer" -ForegroundColor Green
    } else {
        Write-Host "  ❌ .NET SDK: 未找到" -ForegroundColor Red
    }
} catch {
    Write-Host "  ❌ .NET SDK: 未安装" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "提示: 如果某些工具显示未找到,请:" -ForegroundColor Yellow
Write-Host "  1. 关闭当前 PowerShell 窗口" -ForegroundColor White
Write-Host "  2. 重新打开新的 PowerShell 窗口" -ForegroundColor White
Write-Host "  3. 再次运行验证命令" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Green

Write-Host "`n安装脚本执行完毕!" -ForegroundColor Green

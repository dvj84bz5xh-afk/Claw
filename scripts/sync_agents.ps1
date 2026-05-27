# sync_agents.ps1
# Sync Agency-Agents from repo to ~/.claude/agents/
# Usage: powershell -File scripts/sync_agents.ps1

$RepoDir = "c:\Users\10127\WorkBuddy\Claw\agency-agents"
$AgentDir = "$env:USERPROFILE\.claude\agents"

if (-not (Test-Path $RepoDir)) {
    Write-Host "ERROR: Repo directory not found at $RepoDir" -ForegroundColor Red
    Write-Host "Clone it first: git clone https://github.com/msitarzewski/agency-agents.git"
    exit 1
}

if (-not (Test-Path $AgentDir)) {
    New-Item -ItemType Directory -Force -Path $AgentDir | Out-Null
}

# Agent mappings: SourceFile -> TargetName (shortened)
$Agents = @(
    # Tier 1 - Core Investigation
    @{Source="engineering\engineering-security-engineer.md"; Target="security-engineer.md"},
    @{Source="specialized\blockchain-security-auditor.md"; Target="blockchain-security-auditor.md"},
    @{Source="testing\testing-evidence-collector.md"; Target="evidence-collector.md"},
    @{Source="finance\finance-financial-analyst.md"; Target="financial-analyst.md"},
    @{Source="marketing\marketing-content-creator.md"; Target="content-creator.md"},
    @{Source="testing\testing-reality-checker.md"; Target="reality-checker.md"},
    
    # Tier 2 - Extended
    @{Source="engineering\engineering-data-engineer.md"; Target="data-analyst.md"},
    @{Source="product\product-trend-researcher.md"; Target="trend-researcher.md"},
    # @{Source="support\support-analysis-reporter.md"; Target="analysis-reporter.md"},  # not in this repo version
    @{Source="testing\testing-performance-benchmarker.md"; Target="performance-benchmarker.md"},
    @{Source="marketing\marketing-reddit-community-builder.md"; Target="community-builder.md"},
    @{Source="engineering\engineering-ai-engineer.md"; Target="ai-engineer.md"},
    @{Source="specialized\agents-orchestrator.md"; Target="agents-orchestrator.md"}
)

$Copied = 0
$Errors = 0

foreach ($Agent in $Agents) {
    $SourcePath = Join-Path $RepoDir $Agent.Source
    $TargetPath = Join-Path $AgentDir $Agent.Target
    
    if (Test-Path $SourcePath) {
        Copy-Item $SourcePath $TargetPath -Force
        Write-Host "  [OK] $($Agent.Target)" -ForegroundColor Green
        $Copied++
    } else {
        Write-Host "  [--] $($Agent.Source) (not found)" -ForegroundColor Yellow
        $Errors++
    }
}

Write-Host ""
Write-Host "Sync complete! Copied $Copied agents to $AgentDir" -ForegroundColor Cyan
if ($Errors -gt 0) {
    Write-Host "  ($Errors files not found - they may not exist in this repo version)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Available agents:"
Get-ChildItem $AgentDir -Filter "*.md" | Sort-Object Name | ForEach-Object {
    Write-Host "  @$($_.BaseName)"
}

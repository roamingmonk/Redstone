# Redstone → docs\Repository_Structure.md  (Windows / PowerShell)
#RUN using this code in the terminal
#pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\generate_repo_structure.ps1
#powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\generate_repo_structure.ps1


# OPTIONAL: add git-tracked list (disabled by default)
# $lines += ""
# $lines += "## Git-tracked files"
# $lines += "${ticks}text"
# $lines += (git ls-files)
# $lines += $ticks


$ErrorActionPreference = 'Stop'

# 1) Ensure docs/ exists and pick output path
New-Item -ItemType Directory -Force -Path "docs" | Out-Null
$out = Join-Path "docs" "Repository_Structure.md"

# 2) Exclude junk from the ASCII tree output
$regex = '\\\.git($|\\)|\\__pycache__\\|\\\.venv\\|\\venv\\|node_modules\\|dist\\|build|\.mypy_cache|\.pytest_cache|\.idea|\.gitignore$|\.gitattributes$|\.gitmodules$|Thumbs\.db$|\.DS_Store$'

# 3) Build the markdown (no fragile backticks-in-pipeline)
$ticks = '```'
$lines = @()
$lines += "## Repository Structure (generated $(Get-Date -Format 'yyyy-MM-dd HH:mm'))"
$lines += "${ticks}text"

$tree = (cmd /c "tree /A /F")
$filtered = $tree | Select-String -NotMatch $regex | ForEach-Object { $_.ToString() }
$lines += $filtered

$lines += $ticks

# 4) Write file
$lines | Set-Content -Encoding UTF8 $out
Write-Host "✅ Wrote $out"




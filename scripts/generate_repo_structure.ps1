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


# Redstone → docs\Repository_Structure.md  (Windows / PowerShell)
$ErrorActionPreference = 'Stop'

# 1) Ensure docs/ exists and pick output path
New-Item -ItemType Directory -Force -Path "docs" | Out-Null
$out = Join-Path "docs" "Repository_Structure.md"

# 2) Build a case-insensitive pattern that matches anywhere in the line
#    Note: 'tree' output uses ASCII connectors, not backslashes, so just match names.
$tokens = @(
  "__pycache__", ".pyc", ".pyo", ".pyd",          
  ".git", ".venv", "venv", "node_modules",
  "dist", "build", ".mypy_cache", ".pytest_cache", ".idea",
  ".gitignore", ".gitattributes", ".gitmodules", "Thumbs.db", ".DS_Store"
)
$regex = '(?i)' + (($tokens | ForEach-Object { [regex]::Escape($_) }) -join '|')

# 3) Build the markdown (no fragile backticks-in-pipeline)
$ticks  = '```'
$lines  = @()
$lines += "## Repository Structure (generated $(Get-Date -Format 'yyyy-MM-dd HH:mm'))"
$lines += "${ticks}text"

# 4) Run tree, filter lines that contain any excluded token
# if you want folder tree only
#$tree = (cmd /c "tree /A")   # no files listed

$tree     = (cmd /c "tree /A /F")
$filtered = $tree | Where-Object { $_ -notmatch $regex } | ForEach-Object { $_.ToString() }
$lines   += $filtered

# 5) Close code fence and write file
$lines += $ticks
$lines | Set-Content -Encoding UTF8 $out
Write-Host "✅ Wrote $out"



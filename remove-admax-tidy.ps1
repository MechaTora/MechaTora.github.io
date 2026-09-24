# =============================================================
#  Remove the unlabeled Ninja AdMax block from tidy-data-science chapters
#
#  Usage:
#    cd "C:\Users\USER\Documents\...\mechatora-pages"
#    powershell -ExecutionPolicy Bypass -File .\remove-admax-tidy.ps1
#
#  Why: every chapter carried an AdMax unit with no "ad" label,
#       including 19 noindexed generic chapters. During AdSense
#       re-review we only want AdSense code on pages we stand behind.
#
#  Target block (same in all chapters):
#      <!-- admax -->
#      <div style="text-align: center; margin: 2rem 0;">
#          <script src="https://adm.shinobi.jp/s/9436cefd..."></script>
#      </div>
#      <!-- admax -->
#
#  ASCII-only on purpose (Windows PowerShell 5.1 reads BOM-less .ps1 as ANSI).
#  Idempotent: running twice changes nothing the second time.
# =============================================================

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
if (-not $root) { $root = (Get-Location).Path }
$dir = Join-Path $root 'tidy-data-science'

$enc = New-Object System.Text.UTF8Encoding $false
# From the first "<!-- admax -->" to the matching one, plus surrounding whitespace/newline.
$re = '(?s)[ \t]*<!-- admax -->.*?<!-- admax -->[ \t]*\r?\n?'

$total = 0
Get-ChildItem -Path $dir -Filter *.html -File | ForEach-Object {
  $p = $_.FullName
  $t = [System.IO.File]::ReadAllText($p, $enc)
  $m = [regex]::Matches($t, $re)
  if ($m.Count -gt 0) {
    # safety: only remove blocks that really contain the shinobi script
    $ok = $true
    foreach ($x in $m) { if ($x.Value -notmatch 'adm\.shinobi\.jp') { $ok = $false } }
    if (-not $ok) { Write-Host ("  [skip] unexpected block shape: " + $_.Name) -ForegroundColor Yellow; return }
    $t2 = [regex]::Replace($t, $re, '')
    [System.IO.File]::WriteAllText($p, $t2, $enc)
    Write-Host ("  removed {0} block(s): {1}" -f $m.Count, $_.Name)
    $total += $m.Count
  }
}
Write-Host "Removed $total AdMax block(s) in tidy-data-science." -ForegroundColor Green

# Report anything left anywhere in the repo
$left = Get-ChildItem -Path $root -Filter *.html -Recurse -File |
  Where-Object { ([System.IO.File]::ReadAllText($_.FullName, $enc)) -match 'adm\.shinobi\.jp' }
Write-Host "Files still containing AdMax:" -ForegroundColor Cyan
if ($left) { $left | ForEach-Object { Write-Host ("  " + $_.FullName.Substring($root.Length + 1)) } } else { Write-Host "  (none)" }

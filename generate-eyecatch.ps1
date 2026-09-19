# =============================================================
#  Per-article eyecatch SVG generator for mechatora.com
#
#  Usage:
#    cd "C:\Users\USER\Documents\...\mechatora-pages"
#    powershell -ExecutionPolicy Bypass -File .\generate-eyecatch.ps1
#
#  NOTE: This file is intentionally ASCII-only.
#        Windows PowerShell 5.1 reads .ps1 files as the ANSI code page
#        unless they have a UTF-8 BOM, which corrupts Japanese text.
#        All Japanese strings live in eyecatch-data.json instead.
#
#  Output:
#    images/eyecatch/{slug}.svg     - card / article eyecatch (1200x630)
#    images/eyecatch/{slug}-b.svg   - in-body band (1200x300)
#    images/eyecatch/{slug}-c.svg   - in-body band, other pattern
#
#  Colour + pattern are derived deterministically from the slug,
#  so every article gets a different image and re-runs are idempotent.
# =============================================================

$ErrorActionPreference = 'Stop'

$root = $PSScriptRoot
if (-not $root) { $root = (Get-Location).Path }

$dataPath = Join-Path $root 'eyecatch-data.json'
if (-not (Test-Path $dataPath)) { throw "eyecatch-data.json not found next to this script." }

# Always read as UTF-8 explicitly (do not rely on the console code page).
$json = [System.IO.File]::ReadAllText($dataPath, (New-Object System.Text.UTF8Encoding $false))
$data = $json | ConvertFrom-Json

$ELLIPSIS = $data.ellipsis
$NOSTART  = $data.noStart
$articles = $data.articles

$hueBase = @{}
$enLabel = @{}
foreach ($c in $data.categories) {
  $hueBase[$c.name] = [int]$c.hue
  $enLabel[$c.name] = [string]$c.en
}

$outDir = Join-Path $root 'images\eyecatch'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$utf8NoBom = New-Object System.Text.UTF8Encoding $false
function Write-Utf8($path, $text) {
  [System.IO.File]::WriteAllText($path, $text, $utf8NoBom)
}

function Get-Hash([string]$s) {
  $h = 0
  foreach ($ch in $s.ToCharArray()) { $h = ($h * 31 + [int]$ch) % 100000 }
  return $h
}

function Esc([string]$s) {
  return $s.Replace('&', '&amp;').Replace('<', '&lt;').Replace('>', '&gt;')
}

function Get-Width([char]$c) {
  if ([int]$c -ge 32 -and [int]$c -le 126) { return 0.5 } else { return 1.0 }
}

# Wrap a title: full-width counts 1, ASCII 0.5.
# Avoids breaking inside an ASCII word and avoids line-leading small kana.
function Wrap-Title([string]$t, [double]$per, [int]$maxLines) {
  $lines = New-Object System.Collections.ArrayList
  $cur = ''
  $w = 0.0
  $arr = $t.ToCharArray()
  for ($i = 0; $i -lt $arr.Length; $i++) {
    $c  = $arr[$i]
    $cw = Get-Width $c
    if ((($w + $cw) -gt $per) -and ($cur.Length -gt 0)) {
      if ($NOSTART.IndexOf($c) -ge 0) { $cur += $c; $w += $cw; continue }
      if (($c -match '[A-Za-z0-9]') -and ($cur.Substring($cur.Length - 1) -match '[A-Za-z0-9]')) {
        $sp = $cur.LastIndexOf(' ')
        if ($sp -gt ($per * 0.4)) {
          [void]$lines.Add($cur.Substring(0, $sp))
          $cur = $cur.Substring($sp + 1) + $c
          $w = 0.0
          foreach ($ch in $cur.ToCharArray()) { $w += (Get-Width $ch) }
          if ($lines.Count -ge $maxLines) { $cur = ''; break }
          continue
        }
      }
      [void]$lines.Add($cur)
      $cur = [string]$c
      $w = $cw
      if ($lines.Count -ge $maxLines) { $cur = ''; break }
    } else {
      $cur += $c
      $w += $cw
    }
  }
  if (($cur.Length -gt 0) -and ($lines.Count -lt $maxLines)) { [void]$lines.Add($cur) }
  $used = ($lines -join '').Length
  if (($used -lt $t.Length) -and ($lines.Count -gt 0)) {
    $last = $lines[$lines.Count - 1]
    $lines[$lines.Count - 1] = $last.Substring(0, [math]::Max(1, $last.Length - 1)) + $ELLIPSIS
  }
  return $lines
}

# Six geometric patterns so the grid does not look uniform.
function Get-Pattern([int]$kind, [int]$h, [int]$w, [int]$ht) {
  $sb = New-Object System.Text.StringBuilder
  switch ($kind % 6) {
    0 {
        for ($i = 9; $i -ge 1; $i--) {
          $r = 90 * $i + ($h % 40)
          [void]$sb.AppendLine("<circle cx='$($w-120)' cy='$($ht+60)' r='$r' fill='none' stroke='#fff' stroke-opacity='0.10' stroke-width='14'/>")
        }
      }
    1 {
        for ($i = -2; $i -lt 16; $i++) {
          $x = $i * 110 + ($h % 60)
          [void]$sb.AppendLine("<polygon points='$x,0 $($x+52),0 $($x+52-$ht),$ht $($x-$ht),$ht' fill='#fff' fill-opacity='0.07'/>")
        }
      }
    2 {
        for ($y = 0; $y -lt $ht + 60; $y += 62) {
          for ($x = 0; $x -lt $w + 60; $x += 62) {
            $r = 5 + (($x + $y + $h) % 13)
            [void]$sb.AppendLine("<circle cx='$x' cy='$y' r='$r' fill='#fff' fill-opacity='0.09'/>")
          }
        }
      }
    3 {
        for ($i = 0; $i -lt 14; $i++) {
          $x = $i * 95 + ($h % 50)
          if ((($i + $h) % 2) -eq 0) {
            [void]$sb.AppendLine("<polygon points='$x,$ht $($x+95),$ht $($x+47),$($ht-150)' fill='#fff' fill-opacity='0.08'/>")
          } else {
            [void]$sb.AppendLine("<polygon points='$x,0 $($x+95),0 $($x+47),150' fill='#fff' fill-opacity='0.08'/>")
          }
        }
      }
    4 {
        for ($b = 0; $b -lt 5; $b++) {
          $base = 90 + $b * [math]::Max(60, [int]($ht / 6))
          $amp  = 26 + (($h + $b * 17) % 30)
          $d = "M -40 $base"
          for ($x = 0; $x -le $w + 80; $x += 80) {
            if (((($x / 80) % 2)) -eq 0) { $cy = $base - $amp } else { $cy = $base + $amp }
            $d += " Q $($x+40) $cy $($x+80) $base"
          }
          [void]$sb.AppendLine("<path d='$d' fill='none' stroke='#fff' stroke-opacity='0.11' stroke-width='9'/>")
        }
      }
    5 {
        for ($i = 0; $i -lt 8; $i++) {
          $inset = 40 + $i * 58
          $wRect = $w - $inset * 2
          $hRect = $ht - [int]($inset * 0.6)
          if (($wRect -gt 40) -and ($hRect -gt 30)) {
            [void]$sb.AppendLine("<rect x='$inset' y='$([int]($inset*0.3))' width='$wRect' height='$hRect' rx='38' fill='none' stroke='#fff' stroke-opacity='0.09' stroke-width='10'/>")
          }
        }
      }
  }
  return $sb.ToString()
}

$font = "'Hiragino Sans','Yu Gothic UI','Noto Sans JP','Meiryo',sans-serif"

function New-Eyecatch($a) {
  $h   = Get-Hash $a.s
  $hue = ($hueBase[$a.c] + (($h % 44) - 22) + 360) % 360
  $h2  = ($hue + 18 + ($h % 14)) % 360
  $c1  = "hsl($hue,78%,52%)"
  $c2  = "hsl($h2,70%,38%)"
  $pat = Get-Pattern ([int]($h / 7)) $h 1200 630

  $lines = @(Wrap-Title $a.t 15 3)
  $y = 330 - ($lines.Count - 1) * 37
  $tspans = ''
  foreach ($ln in $lines) {
    $tspans += "<tspan x='90' y='$y'>$(Esc $ln)</tspan>"
    $y += 74
  }
  $en = $enLabel[$a.c]

  return @"
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630" role="img" aria-label="$(Esc $a.t)">
  <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="$c1"/><stop offset="100%" stop-color="$c2"/>
  </linearGradient></defs>
  <rect width="1200" height="630" fill="url(#g)"/>
$pat
  <rect x="90" y="150" width="76" height="8" rx="4" fill="#fff" fill-opacity="0.85"/>
  <text x="90" y="212" font-family="$font" font-size="30" font-weight="700" fill="#fff" fill-opacity="0.92">$(Esc $a.c)</text>
  <text font-family="$font" font-size="56" font-weight="800" fill="#fff">$tspans</text>
  <text x="90" y="560" font-family="$font" font-size="26" fill="#fff" fill-opacity="0.75">$en</text>
  <text x="1110" y="560" text-anchor="end" font-family="$font" font-size="26" font-weight="700" fill="#fff" fill-opacity="0.85">mechatora.com</text>
</svg>
"@
}

function New-Band($a, [int]$variant) {
  $h   = (Get-Hash $a.s) + $variant * 977
  $hue = ($hueBase[$a.c] + (($h % 44) - 22) + 360) % 360
  $c1  = "hsl($hue,70%,58%)"
  $c2  = "hsl($((($hue+22)%360)),64%,44%)"
  $pat = Get-Pattern ([int]($h / 5) + $variant * 2) $h 1200 300

  return @"
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 300" width="1200" height="300" role="img" aria-label="$(Esc $a.c)">
  <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="$c1"/><stop offset="100%" stop-color="$c2"/>
  </linearGradient></defs>
  <rect width="1200" height="300" fill="url(#g)"/>
$pat
  <text x="1150" y="270" text-anchor="end" font-family="$font" font-size="22" fill="#fff" fill-opacity="0.6">$(Esc $a.c)</text>
</svg>
"@
}

# ---------- generate SVGs ----------
$made = 0
foreach ($a in $articles) {
  Write-Utf8 (Join-Path $outDir "$($a.s).svg")   (New-Eyecatch $a)
  Write-Utf8 (Join-Path $outDir "$($a.s)-b.svg") (New-Band $a 1)
  Write-Utf8 (Join-Path $outDir "$($a.s)-c.svg") (New-Band $a 2)
  $made += 3
}
Write-Host "Generated $made SVG files -> images\eyecatch\" -ForegroundColor Green

# ---------- rewrite article pages ----------
$defaultRe = '(?:\.\./)?images/(?:tech|career|datascience|misc)-default\.svg'
$changed = 0
$missing = @()

foreach ($a in $articles) {
  $p = Join-Path $root "articles\$($a.s).html"
  if (-not (Test-Path $p)) { $missing += $a.s; continue }
  $text = [System.IO.File]::ReadAllText($p, (New-Object System.Text.UTF8Encoding $false))
  $orig = $text
  $script:cur = $a.s
  $script:n = 0
  $text = [regex]::Replace($text, $defaultRe, {
    param($m)
    $script:n++
    if ($script:n -eq 1) { return "../images/eyecatch/$($script:cur).svg" }
    elseif (($script:n % 2) -eq 0) { return "../images/eyecatch/$($script:cur)-b.svg" }
    else { return "../images/eyecatch/$($script:cur)-c.svg" }
  })
  if ($text -ne $orig) { Write-Utf8 $p $text; $changed++ }
}
Write-Host "Rewrote $changed article files" -ForegroundColor Green
if ($missing.Count -gt 0) {
  Write-Host "Missing article files:" -ForegroundColor Yellow
  $missing | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
}

# ---------- rewrite list pages ----------
foreach ($listFile in @('articles.html', 'index.html')) {
  $p = Join-Path $root $listFile
  if (-not (Test-Path $p)) { continue }
  $text = [System.IO.File]::ReadAllText($p, (New-Object System.Text.UTF8Encoding $false))
  $orig = $text
  foreach ($a in $articles) {
    $script:cur2 = $a.s
    $esc = [regex]::Escape($a.s)
    # image appears before the link
    $text = [regex]::Replace($text, "(?s)images/(?:tech|career|datascience|misc)-default\.svg(.{0,700}?articles/$esc\.html)", {
      param($m) return "images/eyecatch/$($script:cur2).svg" + $m.Groups[1].Value
    }, 1)
    # image appears after the link
    $text = [regex]::Replace($text, "(?s)(articles/$esc\.html.{0,700}?)images/(?:tech|career|datascience|misc)-default\.svg", {
      param($m) return $m.Groups[1].Value + "images/eyecatch/$($script:cur2).svg"
    }, 1)
  }
  if ($text -ne $orig) { Write-Utf8 $p $text; Write-Host "Rewrote $listFile" -ForegroundColor Green }
}

# ---------- report ----------
Write-Host ""
Write-Host "Remaining *-default.svg references:" -ForegroundColor Cyan
$remain = 0
Get-ChildItem -Path $root -Filter *.html -Recurse -File |
  Where-Object { $_.FullName -notmatch '\\node_modules\\' } |
  ForEach-Object {
    $c = ([regex]::Matches([System.IO.File]::ReadAllText($_.FullName, (New-Object System.Text.UTF8Encoding $false)), $defaultRe)).Count
    if ($c -gt 0) {
      Write-Host ("  {0,-60} {1}" -f $_.Name, $c)
      $remain += $c
    }
  }
Write-Host "  TOTAL: $remain" -ForegroundColor Cyan

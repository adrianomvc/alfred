param(
  [string]$Root = ".",
  [switch]$Check
)

$ErrorActionPreference = "Stop"
$rootPath = Resolve-Path -LiteralPath $Root

function Read-TextRaw {
  param([string]$Path)
  return [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
}

function Render-Template {
  param(
    [string]$Template,
    [object]$HostConfig
  )

  $content = $Template
  foreach ($property in $HostConfig.PSObject.Properties) {
    $content = $content.Replace("{{" + $property.Name + "}}", [string]$property.Value)
  }
  if ($content.Contains("{{") -or $content.Contains("}}")) {
    throw "Unresolved template marker in host $($HostConfig.id)"
  }
  while ($content.Contains("`n`n`n")) {
    $content = $content.Replace("`n`n`n", "`n`n")
  }
  return $content.TrimEnd() + "`n"
}

function Compare-OrWrite {
  param(
    [string]$Path,
    [string]$Content
  )

  if ($Check) {
    $current = if (Test-Path -LiteralPath $Path) { Read-TextRaw -Path $Path } else { "" }
    if ($current -ne $Content) {
      throw "Host shim drift: regenerate $($Path.Replace('\', '/'))"
    }
    Write-Output "OK host shim $($Path.Replace('\', '/'))"
    return
  }

  $directory = Split-Path -Parent $Path
  if (-not (Test-Path -LiteralPath $directory)) {
    New-Item -ItemType Directory -Path $directory | Out-Null
  }
  [System.IO.File]::WriteAllText($Path, $Content, [System.Text.UTF8Encoding]::new($false))
  Write-Output "Wrote $($Path.Replace('\', '/'))"
}

$templatePath = Join-Path $rootPath "hosts/_template/shim.md"
$configPath = Join-Path $rootPath "hosts/_template/hosts.json"
$template = Read-TextRaw -Path $templatePath
$config = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json

foreach ($hostConfig in $config.hosts) {
  $outputPath = Join-Path $rootPath $hostConfig.output
  Compare-OrWrite -Path $outputPath -Content (Render-Template -Template $template -HostConfig $hostConfig)
}

Write-Output "Host shim generation completed."

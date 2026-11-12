<#
.SYNOPSIS
Preview or apply the guide's tested Hiddify recovery baseline.
.DESCRIPTION
Read docs/clients.md#advanced-recovery-when-the-normal-settings-are-not-enough
and docs/automation.md#repair-hiddify-preferences-on-windows first.

Preview is the default. -Apply requires Hiddify to be closed and saves a backup.
This script never stops/starts applications or changes Windows proxy/route settings.
The selected service mode takes effect only when you later connect Hiddify.
.EXAMPLE
.\scripts\Repair-Hiddify.ps1
.EXAMPLE
.\scripts\Repair-Hiddify.ps1 -Apply -ServiceMode Manual
.LINK
https://github.com/Vokerlee/VPN-Proxy-in-Russia/blob/master/docs/automation.md#repair-hiddify-preferences-on-windows
#>
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$SettingsPath = (Join-Path $env:APPDATA 'Hiddify\hiddify\shared_preferences.json'),
    [ValidateSet('Manual', 'SystemProxy', 'VPN')]
    [string]$ServiceMode = 'Manual',
    [switch]$Apply
)
$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $SettingsPath -PathType Leaf)) {
    throw 'Hiddify preferences were not found. Open Hiddify once, close it, and check -SettingsPath. Read docs/automation.md.'
}
$item = Get-Item -LiteralPath $SettingsPath
if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
    throw 'Refusing to replace a linked preferences file. Choose the actual preferences file explicitly.'
}
$SettingsPath = $item.FullName
$raw = [IO.File]::ReadAllText($SettingsPath)
$config = $raw | ConvertFrom-Json
if ($null -eq $config -or $config -is [Array] -or $config -isnot [pscustomobject]) {
    throw 'Expected one JSON preferences object. No changes made.'
}
$modeValue = @{Manual='proxy'; SystemProxy='system-proxy'; VPN='vpn'}[$ServiceMode]
$updates = [ordered]@{
    'flutter.region' = 'other'
    'flutter.enable-fake-dns' = $false
    'flutter.independent-dns-cache' = $false
    'flutter.enable-clash-api' = $false
    'flutter.service-mode' = $modeValue
}
Write-Output 'Proposed Hiddify recovery changes (all other preferences are preserved):'
foreach ($key in $updates.Keys) {
    $old = $config.PSObject.Properties[$key]
    $oldText = if ($null -eq $old) { '(default)' } else { [string]$old.Value }
    Write-Output ('  {0}: {1} -> {2}' -f $key, $oldText, $updates[$key])
}
Write-Output 'Read docs/clients.md for the setting explanations and API/monitoring tradeoff.'
Write-Output 'For mobile handshake failures, check docs/handshakes-and-versions.md. Classical mode belongs to the profile TLS/REALITY configuration.'
if (-not $Apply) {
    Write-Output 'Preview only. Close Hiddify yourself, then repeat with -Apply to save a backup and apply.'
    return
}
if (Get-Process -Name 'Hiddify' -ErrorAction SilentlyContinue) {
    throw 'Hiddify is running. Close Hiddify yourself, then retry. No process was stopped and no file was changed.'
}
if (-not $PSCmdlet.ShouldProcess($SettingsPath, 'Back up and apply the documented Hiddify baseline')) {
    return
}
$backup = $SettingsPath + '.backup-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [Guid]::NewGuid().ToString('N').Substring(0,8)
Copy-Item -LiteralPath $SettingsPath -Destination $backup -ErrorAction Stop
foreach ($key in $updates.Keys) {
    $config | Add-Member -NotePropertyName $key -NotePropertyValue $updates[$key] -Force
}
$temporary = $SettingsPath + '.tmp-' + [Guid]::NewGuid().ToString('N')
try {
    [IO.File]::WriteAllText($temporary, ($config | ConvertTo-Json -Depth 64), (New-Object Text.UTF8Encoding($false)))
    [IO.File]::Replace($temporary, $SettingsPath, $null)
} finally {
    if (Test-Path -LiteralPath $temporary) {
        Remove-Item -LiteralPath $temporary
    }
}
Write-Output ('Saved backup: ' + $backup)
Write-Output 'Preferences updated. Open Hiddify, select the intended profile, and Connect.'
Write-Output 'Manual mode leaves Windows proxy selection alone. Test 127.0.0.1:12334 explicitly.'
Write-Output 'This script did not stop any VPN app, start Hiddify, or change Windows networking.'

# Offline checks only. No real Get-Process, SSH, VPN apps or Windows proxy changes.
$ErrorActionPreference='Stop'
$repo=Split-Path -Parent $PSScriptRoot
$tokens=$null
$parseErrors=$null
foreach($file in Get-ChildItem -LiteralPath (Join-Path $repo 'scripts') -Filter '*.ps1') {
    [Management.Automation.Language.Parser]::ParseFile($file.FullName,[ref]$tokens,[ref]$parseErrors)|Out-Null
    if($parseErrors.Count) {throw ($parseErrors|Out-String)}
    Write-Output ('Parsed '+$file.Name)
}
$work=Join-Path $PSScriptRoot ('.artifacts\'+[Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $work -Force|Out-Null
try {
    $fixture=Join-Path $work 'preferences.json'
    $original='{"flutter.region":"ru","flutter.enable-fake-dns":true,"unrelated":"keep me"}'
    [IO.File]::WriteAllText($fixture,$original,(New-Object Text.UTF8Encoding($false)))
    & (Join-Path $repo 'scripts\Repair-Hiddify.ps1') -SettingsPath $fixture|Out-Null
    if([IO.File]::ReadAllText($fixture) -ne $original) {throw 'Preview modified the fixture.'}
    if(@(Get-ChildItem -LiteralPath $work -Filter '*.backup-*').Count) {throw 'Preview created a backup.'}
    Write-Output 'Repair preview leaves preferences untouched.'
    # Mock process discovery in this test's scope: never inspect real VPN apps.
    function Get-Process {
        [CmdletBinding()]param([string]$Name)
        return [pscustomobject]@{ProcessName='Hiddify'}
    }
    $refused=$false
    try {
        & (Join-Path $repo 'scripts\Repair-Hiddify.ps1') -SettingsPath $fixture -Apply|Out-Null
    } catch {
        if($_.Exception.Message -like '*Hiddify is running*') {$refused=$true} else {throw}
    }
    if(-not $refused -or [IO.File]::ReadAllText($fixture) -ne $original) {throw 'Running-app guard did not preserve the fixture.'}
    Write-Output 'Repair refuses a simulated running application without file changes.'
    & (Join-Path $repo 'scripts\Setup-Vpn.ps1') -ServerIp '203.0.113.10'|Out-Null
    Write-Output 'Setup defaults to a plan without SSH or exports.'
    $refused=$false
    try {
        & (Join-Path $repo 'scripts\Setup-Vpn.ps1') -ServerIp '203.0.113.10' -VpnPort 443 -PanelPort 443|Out-Null
    } catch {
        if($_.Exception.Message -like '*ports must be different*') {$refused=$true} else {throw}
    }
    if(-not $refused) {throw 'Conflicting ports were not rejected.'}
    Write-Output 'Setup rejects conflicting ports.'
    $refused=$false
    try {
        & (Join-Path $repo 'scripts\Setup-Vpn.ps1') -ServerIp '203.0.113.10' -VpnPort 38457|Out-Null
    } catch {
        if($_.Exception.Message -like '*VpnPort*') {$refused=$true} else {throw}
    }
    if(-not $refused) {throw 'A public VPN port outside 443/8443 was accepted.'}
    Write-Output 'Setup rejects public VPN ports outside 443 and 8443.'

} finally {
    if(Test-Path -LiteralPath $work) {Remove-Item -LiteralPath $work -Recurse -Force}
}
Write-Output 'PowerShell offline checks passed. No live provisioning or app modification was performed.'

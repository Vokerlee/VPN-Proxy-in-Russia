<#
.SYNOPSIS
Prepare a fresh VPS with its IP and root password, using Windows' OpenSSH client.
.DESCRIPTION
Read docs/quick-start.md. Default is a plan only. -Apply provisions a fresh VPS.
Native ssh.exe prompts for host-key verification and root's password; the script
never reads/saves that password. Existing 3x-ui installations are refused.
No local Python, VPN app restart, Windows proxy or route change is needed.
.EXAMPLE
.\scripts\Setup-Vpn.ps1
.EXAMPLE
.\scripts\Setup-Vpn.ps1 -Apply
.LINK
https://github.com/Vokerlee/VPN-Proxy-in-Russia/blob/master/docs/quick-start.md
#>
[CmdletBinding()]
param(
    [string]$ServerIp,
    [ValidateRange(1,65535)][int]$SshPort=22,
    [ValidateRange(1,65535)][int]$VpnPort=443,
    [ValidateRange(1,65535)][int]$PanelPort=27297,
    [ValidatePattern('^[a-zA-Z0-9][a-zA-Z0-9.-]*$')][string]$Target='www.google.com',
    [ValidatePattern('^(auto|[a-zA-Z]{2})$')][string]$ServerCountry='auto',
    [ValidateSet('auto','chrome','safari','firefox','edge','ios','android','random','randomized','360','qq')][string]$Fingerprint='auto',
    [string]$OutputDirectory,
    [switch]$Apply
)
$ErrorActionPreference='Stop'
if (-not $ServerIp) {$ServerIp=Read-Host 'VPS IPv4 address'}
$address=$null
if (-not [Net.IPAddress]::TryParse($ServerIp,[ref]$address) -or $address.AddressFamily -ne [Net.Sockets.AddressFamily]::InterNetwork) {
    throw 'Enter the VPS IPv4 address, not a URL or hostname.'
}
$ServerIp=$address.ToString()
if (@($SshPort,$VpnPort,$PanelPort | Select-Object -Unique).Count -ne 3) {
    throw 'SSH, VPN and administration ports must be different.'
}
Write-Output 'Plan: pinned official 3x-ui 3.8.5, one REALITY/Vision account, ForceIPv4, loopback panel.'
Write-Output 'Fingerprint policy: US -> Safari; other countries -> Chrome; -Fingerprint overrides.'
Write-Output 'Country lookup runs only during apply; -ServerCountry skips it.'
Write-Output 'Existing installations/listeners are preserved. Windows proxy and running clients are untouched.'
if (-not $Apply) {
    Write-Output 'Plan only; no connection or change made. Repeat with -Apply for a fresh VPS.'
    return
}
$ssh=(Get-Command ssh.exe -ErrorAction Stop).Source
$repo=Split-Path -Parent $PSScriptRoot
$country=if($ServerCountry -eq 'auto'){'auto'}else{$ServerCountry.ToUpperInvariant()}
$options=@{host=$ServerIp;ssh_port=$SshPort;vpn_port=$VpnPort;panel_port=$PanelPort;target=$Target;server_country=$country;fingerprint=$Fingerprint.ToLowerInvariant()}|ConvertTo-Json -Compress
$payload="import json`nBOOTSTRAP_OPTIONS = json.loads('"+$options+"')`n"+[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'provision_remote.py'))
$remoteCommand="if [ -e /usr/local/x-ui/x-ui ] || [ -e /etc/x-ui/x-ui.db ]; then echo 'Existing 3x-ui found; refusing to overwrite it.'; exit 3; fi; command -v python3 >/dev/null || { apt-get update >&2 && DEBIAN_FRONTEND=noninteractive apt-get install -y python3 >&2; }; exec python3 -"
$result=$null
$OutputEncoding=New-Object Text.UTF8Encoding($false)
Write-Output 'SSH will ask you to verify a new host key, then enter root credentials securely.'
Write-Output 'Keep this terminal open; installation can take several minutes.'
$payload | & $ssh -T -o StrictHostKeyChecking=ask -o ConnectTimeout=15 -o ServerAliveInterval=15 -o ServerAliveCountMax=3 -p $SshPort "root@$ServerIp" $remoteCommand | ForEach-Object {
    if ($_.StartsWith('VPN_BOOTSTRAP_RESULT ')) {
        $result=$_.Substring('VPN_BOOTSTRAP_RESULT '.Length)|ConvertFrom-Json
    } else {
        Write-Output $_
    }
}
if ($LASTEXITCODE -ne 0 -or $null -eq $result) {
    throw 'Setup did not report completion. Read docs/quick-start.md. Do not reset an existing installation to retry.'
}
if (-not $OutputDirectory) {
    $OutputDirectory=Join-Path $repo ('.secrets\server-'+$ServerIp+'-'+(Get-Date -Format 'yyyyMMdd-HHmmss'))
}
if (Test-Path -LiteralPath $OutputDirectory) {
    throw 'Output directory already exists. Server result is recoverable at /root/vpn-guide-bootstrap-result.json; choose a new local path.'
}
New-Item -ItemType Directory -Path $OutputDirectory -Force|Out-Null
[IO.File]::WriteAllText((Join-Path $OutputDirectory 'server.json'),($result|ConvertTo-Json -Depth 32),(New-Object Text.UTF8Encoding($false)))
[IO.File]::WriteAllText((Join-Path $OutputDirectory 'hiddify-profile.txt'),($result.client_link+"`n"),(New-Object Text.UTF8Encoding($false)))
Write-Output ('Private panel credentials: '+(Join-Path $OutputDirectory 'server.json'))
Write-Output ('Private Hiddify link: '+(Join-Path $OutputDirectory 'hiddify-profile.txt'))
Write-Output ('VPS country: '+$result.server_country+' | exported client fingerprint: '+$result.fingerprint)
Write-Output $result.firewall
$client=New-Object Net.Sockets.TcpClient
try {
    $pending=$client.BeginConnect($ServerIp,[int]$result.vpn_port,$null,$null)
    if (-not $pending.AsyncWaitHandle.WaitOne(5000)) {throw 'timeout'}
    $client.EndConnect($pending)
    Write-Output 'Public VPN TCP port is reachable. A client still needs to verify authentication.'
} catch {
    Write-Output ('ACTION: allow inbound TCP '+$result.vpn_port+' in the provider firewall/security group and inspect custom host firewall rules.')
} finally {
    $client.Close()
}
Write-Output 'In a second PowerShell terminal, keep this SSH forward running:'
Write-Output ('ssh -N -o ExitOnForwardFailure=yes -p '+$SshPort+' -L 127.0.0.1:18080:127.0.0.1:'+$result.panel_port+' root@'+$ServerIp)
$panelPath=([string]$result.web_path).Trim('/')
$panelUrl='http://127.0.0.1:18080/'
if ($panelPath) {$panelUrl+=$panelPath+'/'}
Write-Output ('Then open '+$panelUrl+' in your browser.')
Write-Output 'Use the generated panel credentials in server.json, not the root password.'
Write-Output 'Next: docs/quick-start.md#bring-the-profile-into-hiddify'

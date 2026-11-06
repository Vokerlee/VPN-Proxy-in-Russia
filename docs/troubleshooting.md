[← Guide index](../README.md) · [Hiddify setup](clients.md) · [Diagnostic helpers](automation.md)

# The server pings, but the VPN does not work

This is the failure that started this update. SSH worked. Ping worked. The server listened on the right port. Yet one client timed out and another printed a REALITY verification error.

Those observations were not contradictory. They described different layers. The quickest way out is to test one layer at a time, keeping a note of what each result actually proves.

![Check the local listener, remote port, account handshake and website request in order](../images/troubleshooting-path.svg)

## First, choose the symptom that matches yours

| What you see | Start here |
|---|---|
| The app says connected, but the browser did not change | [Check the Windows proxy](#the-app-is-green-but-windows-still-uses-the-old-proxy) |
| Connection refused on localhost | [Find the local listener](#connection-refused-on-localhost) |
| The server pings, but the app times out | [Test the VPN TCP port](#ping-works-so-test-the-vpn-port-next) |
| `reality verification failed` or `processed invalid connection` | [Check the handshake and core version](#the-tcp-port-opens-but-reality-fails) |
| The IP check shows IPv6 | [Check the server's egress](force-ipv4.md) |
| HTTPS works, but the app's latency test fails | [Check the test endpoint](#the-latency-test-and-a-real-request-disagree) |
| Hiddify's plain profile works, its full app configuration fails | [Reduce the optional settings](#the-profile-works-but-the-apps-generated-configuration-fails) |

## The app is green, but Windows still uses the old proxy

A manual-mode Hiddify connection does not select its proxy for Windows. Read the current choice in PowerShell:

```powershell
Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings' |
    Select-Object ProxyEnable,ProxyServer
```

If it shows `127.0.0.1:10801` while Hiddify listens on `12334`, Windows still selects the other client. You do not need to stop that client. First test Hiddify explicitly:

```powershell
curl.exe --noproxy localhost,127.0.0.1 --proxy http://127.0.0.1:12334 --connect-timeout 5 --max-time 15 https://www.cloudflare.com/cdn-cgi/trace
```

If that returns the VPS exit IP, use **Hiddify → Settings → Inbound → Service mode → System Proxy** when you intentionally want Windows applications to follow Hiddify. Or keep both clients in their present modes and configure an individual application. See the [illustrated Windows proxy steps](ports-and-modes.md#windows-selects-a-proxy-it-does-not-merge-them).

## Connection refused on localhost

A request to `127.0.0.1:12334` that is refused has not reached the VPS. Hiddify is disconnected, the mixed port is disabled, the port changed, or another process prevented it from starting.

Check **Settings → Inbound → Local proxy** and the [listener command](ports-and-modes.md#check-the-actual-state-in-powershell). Match the curl port to the actual listener. Do not open the VPS firewall to fix a missing localhost listener.

If you see “address already in use,” give the clients different ports. Changing both to 10801 creates a conflict, not compatibility.

## Ping works, so test the VPN port next

An ICMP reply only establishes a limited kind of reachability. It does not prove that TCP 443/8443 is reachable, or that REALITY authentication works.

From Windows, substitute the actual VPN port:

```powershell
Test-NetConnection YOUR_SERVER_IP -Port 443
```

If `TcpTestSucceeded` is false, compare the port in the exported profile, the server listener, the host firewall, and the provider security group. Use a mobile hotspot as a comparison when possible. A successful test from another country or another provider does not prove your current path works.

A TLS-looking response from the REALITY port is also not an authenticated tunnel test. Unauthenticated connections can be forwarded to the configured target website. The next step is a real HTTPS request through a client using the account's parameters.

## The TCP port opens, but REALITY fails

These messages put the investigation at the authentication/transport layer:

```text
REALITY: processed invalid connection
reality verification failed
failed to find an available destination
```

1. Compare IP, VPN port, UUID, Flow, transport, REALITY public key, short ID, SNI, and fingerprint with the panel's export.
2. Check account enablement, expiry, quota, and IP restrictions.
3. Check the VPS clock with `timedatectl status`; check the client clock too. A clock check is relevant, but it is not evidence that clock drift caused this particular failure.
4. Record the **actual client core version**, not just the GUI version.
5. Test the same profile with a known compatible current core, using [the temporary client helper](automation.md#test-a-real-authenticated-tunnel).

The investigation reproduced an Xray **25.1.30** client failing against **26.9.9**, while **26.10.31** connected using the same profile and provider. Invisible Man's upstream 3.2.5 bundled the older core. A broken import and an incompatible TLS handshake can look similar, but reimporting a valid URI does not modernize the core.

Newer REALITY servers have imposed ClientHello/key-share requirements that affected old Xray clients and some sing-box clients. A generic “latest client” label is not a compatibility test. Hiddify 5.5.5's native core succeeded in the final tests; do not generalize older sing-box reports to every Hiddify build. See [the versioned technical explanation](xray-internals.md#why-a-valid-profile-can-stop-working-after-an-update).

## The profile works, but the app's generated configuration fails

A profile carries the account and transport parameters. The app adds DNS, rules, selectors, caches, monitoring, and mode-specific integration. That extra configuration is part of the system you are testing.

In this investigation, the installed Hiddify Windows core repeatedly connected with a small configuration, while the complete generated configuration failed. Rebuilding the app configuration with **Region Other**, **Fake DNS off**, **independent DNS cache off**, and **Clash API off** restored the app's actual proxy. Several settings changed together, so this does not identify one universal culprit.

Use the [Hiddify recovery walkthrough](clients.md#advanced-recovery-when-the-normal-settings-are-not-enough). Start with the visible UI options. For hidden preferences, the repair helper previews changes and saves a backup. Re-enable features individually, testing after each one; note which change reintroduces the symptom.

Do not patch `data/current-config.json` and expect the fix to persist. It is rebuilt on the next connection.

## The latency test and a real request disagree

The app's “ping” may measure a web endpoint through the proxy, not ICMP. That endpoint can be blocked, return a different status, be unavailable, or fail while the tunnel itself works.

In Hiddify, open **Settings → General → Connection test URL**, choose a reachable endpoint, reconnect, and compare with a fresh explicit HTTPS proxy request. A single IP-information API returning HTTP 429 is a rate limit from that API; it is not by itself proof of a failed REALITY handshake.

If websites fail but the port is reachable, read the error from that request rather than treating a successful TCP probe as success for the whole VPN.

## Server checks

Run these **on the VPS**, not on your Windows PC:

```bash
systemctl is-active x-ui
systemctl --failed --no-pager
ss -lntp 'sport = :443'
timedatectl status
journalctl -u x-ui --since '10 minutes ago' --no-pager
```

Use the actual inbound port. No separate `xray.service` may exist when Xray runs under 3x-ui. You can also run the [read-only server check helper](automation.md#check-the-vps-without-changing-it).

Check direct internet access from the VPS separately:

```bash
curl -4 -I --connect-timeout 5 --max-time 15 https://www.google.com/
curl -6 -I --connect-timeout 5 --max-time 15 https://www.google.com/
```

A failed IPv6 test is not a problem if you deliberately use IPv4 only. Inspect host firewall rules with the tool already used by your installation, such as `nft list ruleset` or `ufw status verbose`. Do not flush firewall rules, reset keys, reinstall the server, or restart unrelated applications as a first diagnostic step.

## Read fresh logs, not the last installation's error

On the checked Windows installation, Hiddify's files were under:

```text
%APPDATA%\Hiddify\hiddify\app.log
%APPDATA%\Hiddify\hiddify\box.log
%APPDATA%\Hiddify\hiddify\data\box.log
```

Locations vary by package. Use Hiddify's **Logs** page first. Record the time, reproduce one failed request, and look for new entries from that run. Old errors can remain after an upgrade. `context canceled` during a deliberate disconnect is often cleanup, so find the earlier error that caused the failure.

Temporarily use an informative log level if the app offers it, then restore the normal level after diagnosis. Before sharing logs, remove profile links, UUIDs, credentials, tokens, and sensitive browsing destinations.

## Send a report another person can reproduce

A useful report contains the versions, client OS, selected mode, VPN port, local proxy port, exact error, and results of a direct request and an explicitly proxied request. It also says whether the same profile works with another core or provider.

That small record tells the next person where to start. “Server pings, VPN broken” does not yet separate the seven different systems involved.

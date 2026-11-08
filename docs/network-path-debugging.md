[← Troubleshooting](troubleshooting.md) · [Diagnostic helpers](automation.md)

# Find where the connection stops

Use this investigation when a VPN times out even though its account looks correct, or when it works through another connection. Start with a few controlled comparisons; run a larger settings comparison only when the results justify it.

A **VPS** is your rented server. **3x-ui** is its browser dashboard; **Xray** is the network engine forwarding traffic. **Hiddify** and **Invisible Man - XRay Client** are client applications. A **profile** is the private connection link for one account. **TCP** establishes the underlying connection; **TLS** negotiates the protected session. TLS starts with a **ClientHello** message. A **uTLS fingerprint** changes the shape of that message. **SNI** is the website name sent during TLS setup, and the REALITY **target** is the website endpoint contacted by the VPS.

Addresses below are documentation placeholders. Replace `203.0.113.10` with the VPS address and `198.51.100.20` with your direct public client address. Keep live addresses, account links, keys, passwords and panel paths in private notes.

## 1. Label each path before testing

A running VPN app does not establish which path a particular program uses. Record the application's selected mode, its actual local proxy listener, and the exit address of each request. An existing manual proxy can carry browser traffic while a terminal request goes directly through your ISP, the company providing your internet connection.

On Linux, explicitly bypass inherited proxies:

```bash
curl --proxy '' --noproxy '*' --connect-timeout 5 --max-time 10 https://www.cloudflare.com/cdn-cgi/trace
```

On Windows PowerShell:

```powershell
curl.exe --noproxy '*' --connect-timeout 5 --max-time 10 https://www.cloudflare.com/cdn-cgi/trace
```

Test an existing application proxy separately, substituting its actual port:

```powershell
curl.exe --noproxy does-not-match.invalid --proxy http://127.0.0.1:10801 --connect-timeout 5 --max-time 10 https://www.cloudflare.com/cdn-cgi/trace
```

The response contains `ip=`. Label these results **direct** and **existing proxy**. A route-based VPN can still carry an application-proxy bypass: inspect the route too. Windows PowerShell can lose empty native arguments, so use the nonempty exclusion above for explicitly proxied tests. Leave the working app, its profiles, system proxy and routes unchanged during isolated tests.

## 2. Separate server access from account authentication

Check SSH, the actual VPN TCP port, and the server's local state separately. On Windows, for example:

```powershell
Test-NetConnection 203.0.113.10 -Port 22
Test-NetConnection 203.0.113.10 -Port 443
```

On the VPS, run the [read-only server checks](automation.md#check-the-vps-without-changing-it). Confirm the listener, enabled account, clock, effective configuration and website access. A working panel can coexist with no VPN inbound. A refused port and a timeout are different observations; keep the exact error and duration.

SSH can complete TCP, exchange version banners and then stall during key exchange. Run `ssh -vv -o ConnectTimeout=10 root@203.0.113.10` to identify the last stage. Some post-connect stalls can outlast the initial connection timeout; use a separate process deadline when automating the diagnostic. Preserve normal host-key verification. A failure before the password prompt does not test the password.

Now test the panel's exact account export with an isolated client:

```bash
python3 scripts/vpn_profile.py test --link-file PRIVATE_PROFILE_FILE --xray /path/to/xray --expect-ip 203.0.113.10 --timeout 10
```

This starts a temporary loopback proxy, sends a real HTTPS request, verifies its exit, and terminates its own child. It does not test the app's GUI Connect button, system routing or whole-device UDP. Use fresh logs from that request rather than an old installation error.

## 3. Repeat the same account through a working alternate path

Keep the account, keys, flow, target/SNI, fingerprint and test website unchanged. Change only the path carrying the connection to the VPS. Options include a separate mobile-data network, an existing working proxy, or SSH forwarding through a reachable administration path.

An optional SSH control, with a free local port, is:

```bash
ssh -N -o ExitOnForwardFailure=yes -L 127.0.0.1:18443:127.0.0.1:443 root@203.0.113.10
```

Use the real inbound port on the remote side. Direct SSH must itself work, or use an already authorized alternate SSH path. Generate a disposable client configuration that connects to this loopback forward while preserving the real profile's REALITY credentials and SNI. Keep the original profile unchanged, and close the diagnostic forward afterward.

For an existing local HTTP proxy, a temporary Xray client can instead set its VLESS outbound's `streamSettings.sockopt.dialerProxy` to `existing-proxy` and append this outbound:

```json
{
  "tag": "existing-proxy",
  "protocol": "http",
  "settings": {
    "servers": [{"address": "127.0.0.1", "port": 10801}]
  }
}
```

Use the existing proxy's actual listener. This makes a chain: device → existing proxy → investigated VPS → website. The final website must report the investigated VPS exit address. A request reporting only the existing proxy's address has not authenticated through the investigated VPN.

| Observation | Supported conclusion | Next useful check |
|---|---|---|
| TCP fails directly; alternate path reaches the same endpoint | Reachability depends on the path | Compare access networks and inspect filtering logs |
| Same account authenticates through alternate path but times out directly | Account and tested server setup work over the alternate path | Capture the direct handshake at both ends |
| Both paths reach TCP but authentication fails | TCP reachability alone is insufficient | Compare the canonical export, account restrictions, clocks and engine versions |
| Isolated core works; GUI traffic fails | The app's selected profile or generated settings need inspection | Check actual listeners, routes, DNS and proxy selection |

An alternate-path success verifies that tested path. It does not establish a portable direct phone connection or identify the operator responsible for another path's failure.

## 4. Vary settings without losing the control

Port 443 is optional. A random unused TCP port is valid when the listener, both applicable firewalls and the imported profile agree. Check the port is free before using it. A different port can test a port-specific restriction; it cannot repair every destination or path restriction.

Keep a private table with the endpoint, port, target, SNI, fingerprint, client engine/version, curl error, elapsed time, response body/exit and whether the route was direct or chained. Start by changing one field at a time. Use a broader comparison only after establishing the baseline, and repeat any apparent success with the same settings.

For each candidate target, check from the VPS that its certificate covers the chosen SNI, it supports TLS 1.3 and HTTP/2, and it is reachable. Target and SNI are related fields; the fingerprint is independent. Safari can use a Google target. Country is only an initial automation default. See the [REALITY form](server-inbound.md#3-set-transport-and-security) and [fingerprint explanation](xray-internals.md#what-a-tls-fingerprint-changes-and-why-chrome-can-fail).

Preserve an existing production listener and other people's accounts. Use an isolated temporary listener/account when a comparison would interrupt them; remove it after the test. Re-export through the panel whenever a persistent endpoint or fingerprint changes. Requests to the panel API through loopback may export `localhost`; set the API request's Host to the intended public server address, or configure its supported export setting, then retrieve the actual panel link again. Check the export rather than reconstructing it by hand.

## 5. Compare packet headers at both ends

When TCP opens but the handshake stalls, capture the same attempt on the client and VPS. For example, with `tcpdump` available and the required local privileges:

```bash
# Client: substitute the actual physical interface and VPN port.
sudo tcpdump -ni eth0 -nn -S 'host 203.0.113.10 and tcp port 38457'
# VPS: filter on the client's public address after address translation.
sudo tcpdump -ni any -nn -S 'host 198.51.100.20 and tcp port 38457'
```

Stop each capture after the controlled request. The ordinary summary shows flags, TCP sequence/acknowledgment numbers and payload lengths. Avoid `-A`, `-X` and unrestricted packet files when headers are sufficient. Capturing requires packet-capture privileges; a filesystem permission alone does not supply them. Windows-native and WSL captures observe different parts of the local path.

Correlate flows using sequence and acknowledgment numbers. Address translation can change the client's source IP and port, and clocks can differ. Local network offloading can show one large outgoing buffer while the VPS sees smaller wire packets; that alone is normal. Compare the covered byte ranges and the bytes acknowledged by the receiver.

If the client repeatedly sends a missing range and the VPS never sees it, the loss is before the VPS guest capture point. If the VPS sends a response absent at the client, investigate the reverse path. Capture the complete flow before interpreting an application timeout as a credential rejection.

## 6. Check whether ordinary data fails too

A plain HTTPS request to a REALITY port exercises its unauthenticated fallback rather than the account. To compare ordinary TLS with the same destination and SNI, use a matching target hostname and validate its certificate:

```bash
curl --proxy '' --noproxy '*' --resolve dl.google.com:38457:203.0.113.10 --connect-timeout 5 --max-time 8 -I https://dl.google.com:38457/
curl --proxy '' --noproxy '*' --connect-timeout 5 --max-time 8 -I https://dl.google.com/
```

For deeper diagnosis, an administrator can briefly run an echo listener on a free port, restricted to the participating source addresses and an independent deadline. Send identical random data directly and through the alternate path. Record how many bytes the server receives and how many return; remove the listener afterward. Use harmless test data and no credentials. This is an optional expert experiment, not a permanently exposed service or a setup prerequisite.

If small random messages and ordinary HTTP also disappear directly but arrive through the alternate path, the failure is broader than a REALITY fingerprint or large ClientHello. TCP/TLS fragmentation trials may test a narrower hypothesis, but a failed trial is not a fix and does not identify a filtering operator. A public block-list match is supporting context; no match cannot establish that a path is unfiltered.

## Recorded investigation A: 2026-11-09

This was a separate deployment, called **deployment A** here, with an account represented here by `DEVICE_ACCOUNT`. Live addresses and account exports remain outside the repository. The checked server ran 3x-ui 3.8.5 and Xray 26.9.9; the isolated native Linux client was Xray 26.10.31. Windows tests used the installed Hiddify engine; the previously recorded app baseline was 5.5.5, and a fresh independent engine version was not recorded for this run.

An existing Invisible Man - XRay Client proxy already provided a working alternate exit. Explicit direct curl requests bypassed that application proxy and used the local ISP exit. Administration over the existing proxy succeeded while direct SSH stalled after exchanging version banners. The initial automation was interrupted during installation; the panel was running but had no inbound. The inbound and device account were subsequently created through the supported API. The final saved endpoint used TCP 38457, target `dl.google.com:443`, matching SNI and Safari; direct requests continued to fail in the tests below.

| Experiment | Observation |
|---|---|
| Ports 443, 8443, 38457 and 52741 × six matching target/SNI names × Safari, Chrome and Firefox | 72 combinations in each of native Xray and Windows Hiddify; no successful authenticated trace response |
| Target/SNI candidates | `www.apple.com`, `www.microsoft.com`, `www.google.com`, `dl.google.com`, `ya.ru`, `yastatic.net`; all reached TLS 1.3 and HTTP/2 with certificate validation from the VPS |
| Same account over SSH control | HTTPS succeeded with the deployment A exit |
| Same account chained through the existing proxy | HTTPS succeeded with the deployment A exit |
| Both-end packet comparison | A 1,536-byte TLS record was sent; the VPS received and acknowledged 1,348 bytes; the remaining 188 bytes were retransmitted locally and absent at the VPS |
| Smaller handshakes | Two 517-byte ClientHellos also failed to arrive; size alone did not explain all failures |
| Additional native presets and fragmentation trials | No direct authenticated success; individual core/unsupported-preset failures were not counted as proof of network loss |
| Ordinary TLS to deployment A versus directly to the target | Its fallback timed out; the target completed certificate-verified TLS and returned HTTP 302 |
| Temporary echo listener: random bytes, HTTP and TLS-shaped messages | TCP connected directly, but the server read no test data in these attempts |
| Identical 64-byte echo, direct versus existing proxy | Direct: 0 bytes received back; through the existing proxy: all 64 bytes received back unchanged |
| Public destination block-list checks | No matching address/prefix in the four checked lists; filtering attribution remained unresolved |

The Windows comparison harness returned null native exit-code fields in PowerShell. Those fields were not treated as success; the observations were the absent trace bodies and curl timeout logs. The capture/control experiments provided the stronger diagnosis. No GUI Connect/TUN or whole-device UDP test was established by these isolated requests.

**Conclusion supported by these controls:** the tested deployment A account/server works through the alternate path, while client data disappears before reaching the guest over the direct path. Port, target/SNI and the tested fingerprint changes did not restore direct operation. The experiments did not identify the dropping device, its rule or its operator. Router/host filtering, ISP/transit and destination-provider filtering require additional evidence to distinguish. The final deployment A profile was retained privately for a test on another access network; it was not described as a working standalone direct VPN on the failing network.

## Recorded investigation B: 2026-11-09

A second existing deployment, called **deployment B** here, was checked on the same direct network and through the same working proxy. Its active production inbound and four accounts were preserved. The checked server Xray version was 26.9.9; the native Linux test client was 26.10.31. A fresh panel-generated export for the owner's device account was saved privately.

The live settings differed from the earlier private record: the target was `www.amazon.com:443`, allowed SNI names were `google.com` and `www.google.com`, and the exported fingerprint was Firefox. A certificate-verified TLS request from that VPS to Amazon with either Google SNI failed hostname verification. Nevertheless, the existing REALITY account authenticated through the alternate proxy with Safari, Chrome and Firefox, each returning deployment B's expected exit address. The target/SNI mismatch therefore required separate attention but did not establish the cause of the direct failure. Production settings were left unchanged.

| Experiment | Observation |
|---|---|
| Existing account, native Safari/Chrome/Firefox, direct | All three timed out without an authenticated response |
| Same account and presets through existing proxy | All three HTTPS requests succeeded with deployment B's exit |
| Installed Windows Hiddify engine, direct, same three presets | No authenticated trace response; null native exit-code fields were not interpreted as success |
| Direct TCP probes to SSH 22 and VPN 443 | Both timed out |
| Temporary echo listeners on 8443, 38457 and 52741 | All three failed to establish TCP directly |
| Same three echo endpoints through existing proxy | All connected and returned each identical 64-byte message unchanged |
| Simultaneous captures | Client recorded 15 TCP SYN packets across the five tested ports; VPS recorded none from the direct public source during that capture |
| Cleanup | All three temporary echo listeners closed; original inbound and four accounts retained |
| Public destination block-list checks | No matching address/prefix in the four checked lists |

A **SYN** is the first TCP connection request. Here the direct path failed before TLS could start, whereas deployment A completed TCP and then lost application data. Changing SNI, uTLS or the REALITY target cannot change a SYN that has already failed to reach the guest. The full target/SNI comparison was therefore not repeated against the production listener. A newly working TCP path would justify resuming those tests.

Both cases establish path-dependent failure and a working alternate-path control. Neither identifies a router, access provider, transit network or hosting provider as the dropping operator. The preserved private reports contain exact endpoint/account identities and capture details; these public case labels are intentionally anonymous.

## What to record before stopping

Keep a sanitized report with the date/time zone, versions, exact failures and durations, direct/proxy exit distinction, comparison table, successful control exit, packet byte ranges and unresolved attribution. Record the final listener/profile state and which temporary processes/forwards were removed. Preserve the working existing VPN.

The next discriminating test is the same exact profile on another access network, such as mobile data with Wi-Fi disabled, or actual router/provider filter logs for the destination. Avoid assigning blame from a timeout, server country or public block list alone.

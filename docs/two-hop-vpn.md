[← Guide index](../README.md) · [Single-server setup](quick-start.md) · [Automation](automation.md) · [Connection diagrams](schemes/README.md)

# Two-hop VPN: IPv4 entry, IPv6 between servers, IPv4 exit

Use this setup when you want your devices to connect to a nearby entry server and leave the internet through a different country. A **VPS** is a rented server. **Xray** carries the encrypted connections; **3x-ui** is its browser dashboard. Both legs use **VLESS + REALITY**. Devices use RAW with Vision; the connection between servers uses XHTTP with an empty flow.

```text
Device -- IPv4 --> Moscow -- IPv6 --> foreign server -- IPv4 --> website
           VLESS             VLESS
```

The [single-server path](single-server.md) is the other starting choice in this guide. The relay helper adds a dedicated IPv6 inbound to an existing foreign panel and preserves its old IPv4 inbound and accounts.

## Pick the entry version before linking the panels

The tested mobile path uses **Xray 26.7.28 on Moscow**, **Hiddify 5.5.5 with `keyshare=classical`** on devices, and **Xray 26.9.9 on the foreign exits**. The inter-server transport is **XHTTP + REALITY over IPv6**. Each panel's version number is separate from its core. [Working combinations and handshake sizes](handshakes-and-versions.md)

A Moscow entry can provide a usable domestic first hop when a direct foreign route fails. IPv6 gives the servers another address family to try; our Moscow server reached an exit that was unreachable over IPv4. Both advantages depend on the provider and route. Russian IPs and IPv6 traffic can still be filtered. [Maps and tradeoffs](schemes/README.md)

## Before you start

Get two Linux VPSs and save the SSH login for each. SSH opens a terminal on the server. Use the provider's username, IP address and port when you connect. The commands labeled **on Moscow** run in Moscow’s SSH terminal. Commands labeled **on NL** run in a separate SSH terminal on NL. [Choosing a VPS](choose-server.md) · [Connecting over SSH](server-setup.md#2-connect-over-ssh)

| Where you are | What you need |
|---|---|
| Your computer | A terminal for SSH, a browser for 3x-ui and Hiddify for the final test |
| Moscow | Public IPv4 for devices and working IPv6 for the relay connection |
| NL | An assigned IPv6 address for the relay and working IPv4 for websites |

Keep two browser tabs open when the panels are ready. Label them **Moscow** and **NL**. Save each panel’s full URL and panel credentials separately from its SSH credentials.

## 1. Configure IPv6 yourself using your VPS provider's instructions

**IPv6 configuration is the user's task. The automation never activates IPv6, changes addresses, edits Netplan or installs network routes.** It checks the configuration and stops if the required IPv6 address or default route is missing.

Different VPS providers require different configuration. Do not assume a configuration that works on one VPS works on another:

| Item | What to get from this server's provider |
|---|---|
| Activation | Whether IPv6 must first be enabled in the provider dashboard |
| Address | The exact assigned host address, not only the subnet |
| Prefix | The assigned prefix length, such as /64 or /124 |
| Gateway | The actual gateway; it may be global or link-local |
| Interface | The guest's interface name, such as eth0 or ens3 |
| Network manager | Netplan/networkd, NetworkManager, ifupdown or provider tooling |
| Firewall | IPv6 rules are separate from IPv4 rules in some tools |

A /124 contains **16 addresses**. A subnet allocation is not proof that the guest OS already has an address or route.

Run these commands in each server’s SSH terminal. The last command checks for Netplan on that server.

```bash
ip -br address
ip -6 route
ls /etc/netplan
```

Follow the provider's instructions for that server and operating system. For example, [MVPS's IPv6 instructions](https://www.mvps.net/docs/how-to-enable-ipv6-for-your-mvps-server) describe an assigned /124 and gateway fe80::1. That is a provider-specific example, not a universal gateway.

### Example only: an Ubuntu server using Netplan

Ubuntu 26 and other Netplan-based servers may use /etc/netplan/00-installer-config.yaml, a cloud-init file, or another filename. Inspect the existing configuration and use its actual interface. Preserve its existing IPv4 address, gateway and nameservers.

The following values are documentation placeholders. Replace every address and gateway with the provider's values:

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      dhcp4: false
      dhcp6: false
      accept-ra: false
      addresses:
        - 203.0.113.20/24
        - 2001:db8:2::1/124
      routes:
        - to: default
          via: 203.0.113.1
        - to: "::/0"
          via: fe80::1
      nameservers:
        addresses:
          - 8.8.8.8
          - 2001:4860:4860::8888
```

Back up the current file and keep the provider console available when changing networking. Validate with `sudo netplan generate`. Use `sudo netplan try` for a timed confirmation when supported, or the provider's documented `sudo netplan apply` procedure. These are manual administration steps; the relay helper does not run them. See [Netplan's configuration reference](https://netplan.readthedocs.io/en/latest/netplan-yaml/).

Do not copy this YAML onto an ifupdown or NetworkManager installation. Those need their own configuration.

### Check both IPv6 internet access and the server-to-server route

On both servers:

```bash
curl -6 --noproxy '*' --connect-timeout 5 --max-time 15 https://www.cloudflare.com/cdn-cgi/trace
```

Look for an IPv6 address on the `ip=` line. If the command times out, check the provider’s address, gateway and IPv6 firewall for that server. After you create the NL relay listener, check Moscow’s connection to that listener in the next section.

## 2. Choose the two legs

The starting example uses:

| Leg | Endpoint | Transport and flow | Target/SNI | Client handshake |
|---|---|---|---|---|
| Device → Moscow | Moscow IPv4, TCP 443 | RAW, Vision | yandex.ru | Safari, classical |
| Moscow → foreign | Foreign IPv6, TCP 443 | XHTTP, empty flow | www.google.com | Chrome, hybrid |
| Foreign → website | IPv4 | Direct outbound | Requested destination | Destination connection |

Targets must pass certificate, TLS 1.3 and HTTP/2 checks from the server that uses them. A browser fingerprint is separate from the target's website name. Use the actual network tests before choosing another preset.

**Public VPN inbounds may use only 443 or 8443.** Existing listeners are preserved. SSH and dashboard ports are separate.

The foreign relay inbound accepts authenticated traffic from the configured Moscow IPv6 source. It uses IPv4 for hostname-based destination connections and rejects explicit IPv6 destinations on that relay inbound. Moscow routes the entry inbound to the foreign VLESS outbound; it does not fall back to a direct Moscow exit when the relay fails.

## How the two 3x-ui panels connect

An **inbound** accepts a connection. An **outbound** sends the traffic on to its next stop. The relay account on NL gives Moscow the credentials it needs to connect. Your desktop and phone have their own accounts on Moscow.

For the manual setup, open or install 3x-ui on each server. The installer gives you the panel address and login. Keep the dashboard port separate from the VPN port. If you use the helper in section 3, it can install a missing panel and create the accounts and rules below. [Install and open 3x-ui](server-setup.md#3-install-3x-ui)

### On NL, create the relay account

1. Open **Inbounds → Add Inbound**. Set **Remark** to `Relay nl`, **Listen IP** to the assigned NL IPv6 address, and **Port** to **443**. Use VLESS, **XHTTP**, path **`/relay-nl`**, server mode **auto**, REALITY, target `www.google.com:443`, SNI `www.google.com` and fingerprint `chrome`. In **Listen IP**, enter the address by itself. The exported link will put brackets around it.
2. Generate REALITY keys and a short ID. Add a client named `relay-nl` with **Flow** empty for XHTTP. The account is for Moscow to use. [Inbound form and client fields](server-inbound.md#3-set-transport-and-security)
3. Set **Outbounds → direct → Edit → Strategy → ForceIPv4**. In **Routing**, scope the relay rules to the new NL inbound. Match Moscow’s IPv6 address with `/128` in **Source IP** and select `direct` as **Outbound Tag**. Add a rule below it for the same inbound with **Outbound Tag** set to `blocked`, so traffic from other sources has no exit. To enforce IPv4-only destinations, add a rule above both that matches this inbound and destination IP `::/0` and selects `blocked`. Keep the panel’s API rule. [IPv4 exit settings](force-ipv4.md)
4. Allow TCP 443 over IPv6 from Moscow in any provider or guest firewall that filters incoming traffic. Enable the relay inbound, save, and restart Xray if prompted.
5. Expand **Relay nl** in **Inbounds** and open **Info / Share** for `relay-nl`. Copy the private VLESS link. Check that the address after `@` is the NL IPv6 address in brackets, followed by `:443`. If the panel exports IPv4 instead, open the panel using its IPv6 URL and export again. Check the link before importing.

On Moscow, replace the example address below with the actual NL IPv6 address:

```bash
nc -6 -vz -w 5 2001:db8:2::1 443
```

A successful check shows that Moscow can open the TCP port. If `nc` is unavailable, install the distribution’s Netcat package or use the relay helper’s authenticated test. If the port times out, check the IPv6 route and both firewalls before editing VLESS settings.

### On Moscow, connect the device inbound to NL

1. Open **Outbounds → + Outbounds → JSON**. Paste the NL relay link into the link field and click **Import**. Set **Tag** to `relay-nl`. Check the IPv6 address, port, SNI and Chrome fingerprint. The account flow is empty. Set XHTTP mode to **stream-one** and path to **`/relay-nl`**. In the existing outbound JSON, set top-level `sendThrough` to Moscow's global IPv6 address and `streamSettings.sockopt.domainStrategy` to `ForceIPv6`, then click **Create**. The link import is inside the **+ Outbounds** form. [Outbound form in 3x-ui 3.8.5](https://github.com/MHSanaei/3x-ui/blob/v3.8.5/frontend/src/pages/xray/outbounds/OutboundFormModal.tsx)
2. Open **Inbounds → Add Inbound**. Name this entry `VLESS RU`. Use Moscow’s IPv4 endpoint on **443**, VLESS, TCP or RAW, REALITY, target `yandex.ru:443`, SNI `yandex.ru` and fingerprint `safari`. Generate separate REALITY keys and a short ID for this inbound. Add one client account per device, such as `desktop` and `phone`, with Vision flow. Save the inbound with **Enable** off while you add its route.
3. Open **Routing** and use the **+** button to add a rule. Under **Inbound Tags**, select the new Moscow inbound. Under **Outbound Tag**, select `relay-nl`. Put this rule above general rules that could match the same traffic. Keep the API rule. Save and apply the settings, enable the Moscow inbound, and restart Xray if prompted. [Routing form in 3x-ui 3.8.5](https://github.com/MHSanaei/3x-ui/blob/v3.8.5/frontend/src/pages/xray/routing/RuleFormModal.tsx)
4. Allow TCP 443 over IPv4 in Moscow’s provider and guest firewalls where applicable. In **Inbounds**, open **Info / Share** for the Moscow device account. This link should use Moscow’s public IPv4 address and port 443. Give each device its own link. For the compatible 26.7.28 entry core, append `&keyshare=classical` before the link's `#` name. The helper writes this Hiddify variant and saves the original panel export separately.

[See the connection diagrams](schemes/README.md) · [Which panel screens to capture](../images/README.md#screenshots-to-send-in-order)

## 3. Preview and apply the relay helper

<details>
<summary>Open the commands for the same two-server setup</summary>

This optional helper needs Python 3.8+ and native OpenSSH on your administration computer. The existing Windows single-server launcher still works without local Python. The servers need Python 3, supported Ubuntu/Debian and systemd.

Use placeholders below for the two actual public IPv4 addresses and the foreign server's already-configured IPv6 host address:

```bash
python3 scripts/bootstrap_relay.py \
  --hub-host 203.0.113.10 \
  --exit-host 198.51.100.20 \
  --exit-ipv6 2001:db8:2::1 \
  --route nl \
  --entry-port 443 \
  --exit-port 443 \
  --hub-core-version 26.7.28 \
  --exit-core-version 26.9.9 \
  --entry-key-share classical \
  --relay-transport xhttp \
  --clients desktop,phone \
  --plan
```

Plan mode makes no network requests or changes. Repeat the same command with **--apply** to deploy. On Windows PowerShell, use `py` or `python` and put the arguments on one line.

The helper:

1. Authenticates to both servers through OpenSSH with normal host-key verification and hidden root-password prompts.
2. Checks that IPv6 addresses and default routes already exist.
3. Installs pinned 3x-ui and the selected, checksum-verified Xray core only when that server has no panel. An existing core must match the requested version. Panel-only installation creates no temporary VPN account.
4. Saves private SQLite and routing backups before changing an existing panel.
5. Adds the foreign IPv6 relay inbound and a dedicated relay account; existing direct accounts remain.
6. Tests two consecutive authenticated HTTPS requests from Moscow to the foreign IPv6 endpoint and checks the foreign IPv4 exit. A bounded retry allows the newly restarted listener to settle.
7. Adds the Moscow inbound and routes it to that foreign outbound. New inbounds remain disabled until their routing is ready; setup failures disable the new inbound when possible.
8. Retrieves and saves the panel-generated links. Device files add the requested Hiddify key-share option; `panel-profiles.json` preserves the original exports. Both stay in the ignored `.secrets/` directory.

A fresh panel's generated credentials are in the private relay.json result. Open its printed public HTTP panel URL directly in a browser, as described in the [panel guide](server-setup.md#required-open-the-dashboard-safely-in-your-browser).

The helper's IPv6 preflight does not configure provider networking. If it fails there, complete section 1 manually before retrying.

### Explicit management access through an existing proxy

Default SSH access is direct, with configured ProxyCommand and ProxyJump settings bypassed. Do not silently fall back after a failed direct login.

If the owner explicitly authorizes an existing local HTTP proxy, supply:

```text
--exit-ssh-proxy 127.0.0.1:10801
```

There is a separate `--hub-ssh-proxy` option. These are explicit loopback proxy endpoints, not root-password arguments. The helper keeps its own SSH connections separate from old multiplexed sessions.

**This proxy is for administration only.** After deployment, the running VPN uses Moscow's native IPv6 connection to the foreign server. Phones do not depend on your administration PC, WSL or Invisible Man remaining open.

</details>

## 4. Verify the complete device path

On your phone or computer, copy the full **Moscow device** link. Open Hiddify and choose **+ → Clipboard**, select the new profile, then tap **Connect**. On desktop, choose **Settings → Inbound → Service mode → VPN / TUN** to route ordinary apps. Accept the VPN permission prompt if shown. [Hiddify walkthrough](clients.md)

Open a website and then open the IP check page. The `ip=` line should show **NL’s IPv4 address**. If it shows your usual address or another VPN’s exit, check the selected profile, Hiddify’s service mode and the system proxy. If the page times out, test the device-to-Moscow port and the Moscow-to-NL relay separately. [IP check page](https://www.cloudflare.com/cdn-cgi/trace) · [Troubleshooting](troubleshooting.md)

For an optional command-line check of the classical profile, use an installed Hiddify CLI executable and the private Moscow device export. The relay helper saves that export under `.secrets/`.

Run this on your administration computer, replacing the example paths and expected IPv4 address:

```bash
python3 scripts/vpn_profile.py test \
  --link-file .secrets/YOUR_RELAY_OUTPUT/desktop.txt \
  --engine hiddify --hiddify /path/to/HiddifyCli \
  --expect-ip 198.51.100.20
```

Then test the actual Hiddify connection, the intended websites and DNS. An inter-server success alone does not verify the device-to-Moscow leg or the app's VPN routing. Test UDP separately before claiming full TCP/UDP functionality.

Keep each owner's credentials separate. A desktop and phone can share the same inbound but should have their own client accounts.

## 5. Add a second foreign country to the same Moscow hub

Use route key `fi` and Moscow’s other allowed port, 8443.

```bash
python3 scripts/bootstrap_relay.py \
  --hub-host 203.0.113.10 \
  --exit-host 198.51.100.30 \
  --exit-ipv6 2001:db8:3::1 \
  --route fi \
  --entry-port 8443 \
  --exit-port 8443 \
  --hub-core-version 26.7.28 \
  --exit-core-version 26.9.9 \
  --entry-key-share classical \
  --relay-transport xhttp \
  --clients desktop,phone \
  --plan
```

Apply only after that foreign server's IPv6 is configured. The helper reuses Moscow's panel, attaches existing owner accounts without rotating their UUIDs, and adds a separate inbound-to-outbound rule for the new country. It preserves the first country's route.

With one public IPv4 address and this separate-listener design, 8443 and 443 provide **two country entry points**. More countries can share an existing inbound with [Xray user routing](https://xtls.github.io/en/config/routing#ruleobject). Give each device/country combination a distinct account, such as `desktop` for NL and `FR-desktop` for FR, and route its account label to the corresponding foreign outbound. Put the account-specific rules above the inbound's general rule. The helper supports that layout through `--shared-entry`. For example, use `--route fr --entry-port 443 --shared-entry --clients FR-desktop,FR-phone` with FR's server addresses. It checks the existing RAW entry and SNI, then inserts the account rule before the general NL rule. The new account labels must be distinct. Public entries still use only 443 and 8443.

Reapplying the same route with unchanged settings reuses it. A route key already bound to different settings is refused; do not delete its registry or reinstall the hub to force a change.

## What we verified

From the Moscow server, direct TCP to the foreign IPv4 SSH, VPN and panel ports timed out. The foreign IPv6 ports were reachable, and both the original foreign VPN over IPv6 and the new relay authenticated. The new path returned the foreign IPv4 exit. From a desktop, the complete chain passed six isolated Windows Hiddify HTTPS requests, two requests using Hiddify's actual VPN Connect button, and a separate UDP DNS request. The test watchdog then disconnected Hiddify and restored the previous Windows proxy settings. A second country's live route was not part of this test.

All four NL accounts passed HTTPS checks after moving Moscow’s entry to port 443. Hiddify’s Connect button passed two more checks on port 443. FI was added on port 8443, and all four FI device profiles returned the expected FI exit. FR now shares Moscow port 443 with NL. The FR account rule runs before the general NL rule for that inbound. All four FR profiles returned the expected FR exit in isolated Windows Hiddify checks. The NL and FI desktop profiles also returned their expected exits after FR was added.

A later live test switched the inter-server IPv6 links for NL, FR and FI to XHTTP + REALITY, using `stream-one` on Moscow’s outbounds and `auto` on the foreign inbounds. Each relay kept its existing address, port and account. XHTTP uses an empty client flow on that leg. All twelve device profiles passed isolated Windows Hiddify HTTPS requests through their expected exits, and UDP DNS passed through each XHTTP relay. Device entry uses RAW + REALITY + Vision. The helper defaults to this XHTTP relay. Select `--relay-transport raw` for the older RAW relay mode, whose relay account uses Vision flow.

The owner subsequently reported that the NL phone profile worked over mobile data when Moscow ran Xray 26.7.28 and Hiddify 5.5.5 used `keyshare=classical`. All three saved Windows desktop profiles were then updated to classical mode and each passed two HTTPS checks. Hiddify’s Connect button passed three further NL HTTPS checks. This is a version-specific result: classical key shares require a compatible server, and Xray 26.9.9 rejects them. Check the server version before changing this field. [Hiddify investigation and compatibility caveat](https://github.com/hiddify/hiddify-app/issues/2463#issuecomment-6750196534)

## Recovery and evidence

Private remote backups are under /root/vpn-relay-backups. The ownership registry is /etc/vpn-guide-relay/routes.json. The local relay.json records completed stages and backup locations. An incomplete run is not permission to wipe a panel. Inspect its disabled inbound and backup before resuming.

IPv6 and a two-hop chain do not guarantee that a destination IP or prefix will remain reachable. Distinguish direct, proxy-assisted management, inter-server and final device tests. Record their actual exit addresses and keep live account links and keys out of the repository.

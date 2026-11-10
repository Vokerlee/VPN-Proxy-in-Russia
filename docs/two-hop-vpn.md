[← Guide index](../README.md) · [Single-server setup](quick-start.md) · [Automation](automation.md) · [Connection diagrams](schemes/README.md)

# Two-hop VPN: IPv4 entry, IPv6 between servers, IPv4 exit

Use this setup when you want your devices to connect to a nearby entry server and leave the internet through a different country. A **VPS** is a rented server. **Xray** carries the encrypted connections; **3x-ui** is its browser dashboard. **VLESS + REALITY + Vision** protects each leg separately.

```text
Device -- IPv4 --> Moscow -- IPv6 --> foreign server -- IPv4 --> website
           VLESS             VLESS
```

The [single-server walkthrough](single-server.md) and [its automation](quick-start.md) remain available. The relay helper adds a dedicated IPv6 inbound to an existing foreign panel and preserves its old IPv4 inbound and accounts.

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

On each server, inspect:

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

The response must contain that server's IPv6 exit address. Then verify the foreign IPv6 endpoint is reachable from Moscow. Public IPv6 addresses on both servers do not by themselves prove that route works.

## 2. Choose the two legs

The starting example uses:

| Leg | Endpoint | Target/SNI | Fingerprint |
|---|---|---|---|
| Device → Moscow | Moscow IPv4, TCP 443 | yandex.ru | Safari |
| Moscow → foreign | Foreign IPv6, TCP 443 | www.google.com | Chrome |
| Foreign → website | IPv4 | The requested destination | Ordinary direct outbound |

Targets must pass certificate, TLS 1.3 and HTTP/2 checks from the server that uses them. A browser fingerprint is separate from the target's website name. Use the actual network tests before choosing another preset.

**Public VPN inbounds may use only 443 or 8443.** Existing listeners are preserved. SSH and dashboard ports are separate.

The foreign relay inbound accepts authenticated traffic from the configured Moscow IPv6 source. It uses IPv4 for hostname-based destination connections and rejects explicit IPv6 destinations on that relay inbound. Moscow routes the entry inbound to the foreign VLESS outbound; it does not fall back to a direct Moscow exit when the relay fails.

## How the two 3x-ui panels connect

The **foreign inbound** supplies the link that **Moscow uses as its outbound**. Each panel manages its own Xray instance.

1. In the foreign panel, [create a VLESS/REALITY inbound](server-inbound.md) bound to its assigned **IPv6** address. Use port 443, the foreign target and fingerprint from the table, and a dedicated `relay-nl` account. Keep the previous IPv4 inbound if you use one. Route this relay's traffic through [the IPv4 direct outbound](force-ipv4.md) and restrict it to the Moscow IPv6 source. Open **Inbounds → Relay nl → relay-nl → Info / Share**. Copy the relay account's VLESS URL and check that it uses the foreign IPv6 address in brackets and port 443.
2. In the Moscow panel, open **Outbounds → + Outbounds → JSON**. Paste that URL into the link field and click **Import**. In the resulting form set **Tag** to `relay-nl`, verify the IPv6 endpoint, target/SNI, Chrome fingerprint and Vision flow, then click **Create**. The separate **More → Import Outbounds** action expects JSON, not a VLESS URL. See the [3x-ui 3.8.5 outbound form](https://github.com/MHSanaei/3x-ui/blob/v3.8.5/frontend/src/pages/xray/outbounds/OutboundFormModal.tsx).
3. In Moscow, create the IPv4 entry inbound on 443 with the entry target and device accounts from the table. Keep it disabled until its route is ready. Open **Routing** and add a rule with **Inbound Tags** set to the Moscow entry inbound and **Outbound Tag** set to `relay-nl`. Put the rule before more general traffic rules while preserving the API rule. Save the rule, enable the Moscow inbound, and restart Xray if prompted. See the [routing form](https://github.com/MHSanaei/3x-ui/blob/v3.8.5/frontend/src/pages/xray/routing/RuleFormModal.tsx).
4. Export a **Moscow device account** from Moscow's Inbounds page and import it into Hiddify. Keep the foreign relay account private on the server. Hiddify connects to Moscow; Moscow connects to the foreign relay.

## 3. Preview and apply the relay helper

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
  --clients desktop,phone \
  --plan
```

Plan mode makes no network requests or changes. Repeat the same command with **--apply** to deploy. On Windows PowerShell, use `py` or `python` and put the arguments on one line.

The helper:

1. Authenticates to both servers through OpenSSH with normal host-key verification and hidden root-password prompts.
2. Checks that IPv6 addresses and default routes already exist.
3. Installs pinned 3x-ui only when that server has no panel. Panel-only installation creates no temporary VPN account.
4. Saves private SQLite and routing backups before changing an existing panel.
5. Adds the foreign IPv6 relay inbound and a dedicated relay account; existing direct accounts remain.
6. Tests two consecutive authenticated HTTPS requests from Moscow to the foreign IPv6 endpoint and checks the foreign IPv4 exit. A bounded retry allows the newly restarted listener to settle.
7. Adds the Moscow inbound and routes it to that foreign outbound. New inbounds remain disabled until their routing is ready; setup failures disable the new inbound when possible.
8. Retrieves the exact panel-generated client links and saves them in the ignored .secrets directory.

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

## 4. Verify the complete device path

Import the intended device's exact new panel export into Hiddify. Preserve the panel's account/profile name. A link whose server is still the foreign IPv4 address is the old single-server profile.

First test the generated entry profile with an isolated client:

```bash
python3 scripts/vpn_profile.py test \
  --link-file .secrets/YOUR_RELAY_OUTPUT/desktop.txt \
  --xray /path/to/xray \
  --expect-ip 198.51.100.20
```

Then test the actual Hiddify connection, the intended websites and DNS. An inter-server success alone does not verify the device-to-Moscow leg or the app's VPN routing. Test UDP separately before claiming full TCP/UDP functionality.

Keep each owner's credentials separate. A desktop and phone can share the same inbound but should have their own client accounts.

## 5. Add a second foreign country to the same Moscow hub

Use route key `fr` and Moscow’s other allowed port, 8443.

```bash
python3 scripts/bootstrap_relay.py \
  --hub-host 203.0.113.10 \
  --exit-host 198.51.100.30 \
  --exit-ipv6 2001:db8:3::1 \
  --route fr \
  --entry-port 8443 \
  --exit-port 8443 \
  --clients desktop,phone \
  --plan
```

Apply only after that foreign server's IPv6 is configured. The helper reuses Moscow's panel, attaches existing owner accounts without rotating their UUIDs, and adds a separate inbound-to-outbound rule for the new country. It preserves the first country's route.

With one public IPv4 address and this separate-listener design, 8443 and 443 provide **two country entry points**. More countries can share an existing inbound with [Xray user routing](https://xtls.github.io/en/config/routing#ruleobject). Give each device/country combination a distinct account, such as `FR-desktop` and `FI-desktop`, and route its account label to the corresponding foreign outbound. Put the account-specific rules above the inbound's general rule. This is an advanced configuration separate from the current two-listener helper. Do not invent additional public inbound ports.

Reapplying the same route with unchanged settings reuses it. A route key already bound to different settings is refused; do not delete its registry or reinstall the hub to force a change.

## What we verified

From the Moscow server, direct TCP to the foreign IPv4 SSH, VPN and panel ports timed out. The foreign IPv6 ports were reachable, and both the original foreign VPN over IPv6 and the new relay authenticated. The new path returned the foreign IPv4 exit. From a desktop, the complete chain passed six isolated Windows Hiddify HTTPS requests, two requests using Hiddify's actual VPN Connect button, and a separate UDP DNS request. The test watchdog then disconnected Hiddify and restored the previous Windows proxy settings. A second country's live route was not part of this test.

All four NL accounts passed HTTPS checks after moving Moscow’s entry to port 443. Hiddify’s Connect button passed two more checks on port 443. The old 8443 listener was retired after those tests. FR and FI still require IPv6 configured in their guests before they can use the planned shared 8443 listener.

## Recovery and evidence

Private remote backups are under /root/vpn-relay-backups. The ownership registry is /etc/vpn-guide-relay/routes.json. The local relay.json records completed stages and backup locations. An incomplete run is not permission to wipe a panel. Inspect its disabled inbound and backup before resuming.

IPv6 and a two-hop chain do not guarantee that a destination IP or prefix will remain reachable. Distinguish direct, proxy-assisted management, inter-server and final device tests. Record their actual exit addresses and keep live account links and keys out of the repository.

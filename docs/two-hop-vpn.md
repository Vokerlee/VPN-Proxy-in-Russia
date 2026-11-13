[← Start here](../README.md) · [One-server route](single-server.md)

# Connect through Russia to a server abroad

Here we’ll set up two servers. Your phone connects to the one in Russia. That server passes your traffic to the one abroad, and websites send their replies back along the same route.

```text
Your phone / PC
      |
      | IPv4
      v
Your internet provider
      |
      v
Your server in Russia
      |
      | IPv6, through hosting providers and the internet
      v
Your server abroad
      |
      | IPv4, through its hosting provider and the internet
      v
Website
```

Each arrow can cross other networks too. The VPN uses internet providers just like any other connection; it doesn’t go around them. Your device opens one encrypted connection to the Russian server. That server opens a separate encrypted connection to the foreign server.

**Your devices don’t need IPv6.** They connect to Moscow over IPv4. Only the two servers need working IPv6 for their connection to each other. With a direct connection to a single server’s IPv6 address, your device’s current Wi-Fi or mobile network would need IPv6 too; you can’t arrange that just by changing the VPN app.

The Russian server is the **entry**: the first server your device reaches. The foreign server is the **exit**: the one websites see. Hiddify is the **client** app on your phone or computer. You only add the Moscow device link to Hiddify; you don’t need to connect two apps yourself.

This can help when you can reach a Russian server but can’t reliably reach the foreign one directly. It adds a server rental and another connection to look after. Both servers and the connections between them can still be blocked.

## Before you start

You need a computer for setup, one server in Russia and one abroad. Our example calls them **Moscow** and **NL**. NL means the Netherlands; later examples use FR for France and FI for Finland. Those are example locations, not names you have to use.

**No servers yet?** First [rent the Moscow server from FirstVDS](choose-server.md#rent-the-russian-server-firstvds-example), then [rent the foreign server from HostVDS](choose-server.md#rent-the-foreign-server-hostvds-example). You need **both**, with separate orders and bills. If you already have one, rent only the missing server. Other suitable providers also work; keep the same Russian/foreign roles. Choose plans with a public IPv4 address and IPv6 on both servers. Save each server’s address, login name, password or SSH key, and SSH port separately. SSH is the terminal connection you’ll use to manage a server.

We’ll use **3x-ui**, a browser dashboard, on both servers. It manages **Xray**, the program carrying the VPN traffic. If this is your first setup, follow this order:

1. After **both rentals are complete**, configure IPv6 on each server using its provider’s instructions below.
2. [Install and open a dashboard](server-setup.md) on **Moscow**, then repeat that page on **NL**. The installation page explains which VPN program version to install on each server and how to do it. Save two panel URLs and two panel logins, then return here. Already have dashboards? Keep them and check their versions.
3. [Link the panels](#how-the-two-3x-ui-panels-connect), then test your device.

Prefer scripts? Finish the IPv6 setup first, then use [the folded script instructions](#3-preview-and-apply-the-relay-helper) instead of the manual panel steps. You don’t need to do both.

Keep two browser tabs open and label them Moscow and NL so you don’t edit the wrong server. Keep each panel’s browser login separate from its SSH login.

## 1. Configure IPv6 yourself using your VPS provider's instructions

**IPv6** is another kind of internet address. IPv4 looks like `203.0.113.10`; IPv6 looks like `2001:db8:2::1`. In this route, devices reach Moscow using IPv4 and Moscow reaches NL using IPv6.

Configure IPv6 yourself using each provider’s instructions. The scripts only check it; they don’t activate it or change your server’s network settings. One server’s settings may be wrong for the other.

Moscow needs an IPv6 connection to the foreign server, so arrange IPv6 on **both rented machines** before linking them. You don’t need to enable IPv6 on your phone or PC.

1. In **FirstVDS**, get the assigned IPv6 address for your Moscow server and follow FirstVDS’s instructions to activate it on that server.
2. In **HostVDS**, do the same for the foreign server, using HostVDS’s own instructions.
3. Save the exact IPv6 **host address** for each machine. You’ll enter the foreign address in Moscow’s connection settings and Moscow’s address in the foreign server’s access rule.

Some providers configure IPv6 automatically; others need an operating-system change or help from support. Use that provider’s procedure. The [separate IPv6 reference](ipv6-networking.md) has Netplan examples and diagnostic commands if you need them. The setup scripts check the existing network; they don’t configure it for you.

**IPv6 configured on both servers?** If you’re configuring manually, [install the Moscow dashboard](server-setup.md), repeat on NL, then [continue with the two legs below](#2-choose-the-two-legs). If both dashboards already work, continue below. If you chose automation, skip the manual panel work and [run the relay helper](#3-preview-and-apply-the-relay-helper) instead.

## 2. Choose the two legs

There are two encrypted connections to configure. The names in this table are settings you’ll enter below. You can copy them without learning the protocols first.

| Connection | Address and port | Transport | Security and flow | Target / SNI | Fingerprint |
|---|---|---|---|---|---|
| Your device → Moscow | Moscow IPv4, **443** | **RAW** (also called TCP) | REALITY, **Vision** | `yandex.ru:443` / `yandex.ru` | `safari` |
| Moscow → NL | NL IPv6, **443** | **XHTTP** | REALITY, **empty flow** | `www.google.com:443` / `www.google.com` | `chrome` |

A **port** is a numbered connection entry point. **443 is the standard HTTPS port and 8443 is a common alternative**, so they fit the aim of making REALITY connections resemble encrypted browser traffic. The port alone doesn’t disguise the protocol. We use only **443 or 8443** for public VPN connections. Each server has its own ports, so both can use 443. If that port already belongs to another service, keep that service and use 8443 if free. If both are occupied, resolve that before continuing.

The **target/SNI** settings describe a website used during REALITY connection setup. They aren’t the websites you’re allowed to visit. A **fingerprint** shapes the app’s first connection message; Safari here doesn’t mean you need the Safari browser. [What those settings do](handshakes-and-versions.md#the-opening-message)

## How the two 3x-ui panels connect

An **inbound** accepts a connection. An **outbound** sends the traffic on to its next stop. The relay account on NL gives Moscow the credentials it needs to connect. Your desktop and phone have their own accounts on Moscow.

**Continue here only when both dashboards are ready and show Xray 26.7.28 with Running status.** Use that version on both Moscow/FirstVDS and foreign NL/HostVDS. [Check and install the exact version](server-setup.md#install-the-vpn-program-version-used-in-this-guide). Keep the dashboard port separate from the VPN port. If a dashboard is missing, [install it on that server](server-setup.md), then return here. If you chose the script route instead, [skip to the relay helper](#3-preview-and-apply-the-relay-helper); it can install missing panels and create the accounts and rules for you.

### On NL, create the relay account

Moscow needs credentials before it can open the second VPN connection. We’ll create an account on NL for that purpose, then copy its link into Moscow. Your phone’s account will be created separately on Moscow.

**1. Create the receiving end of VPN 2.** We’ll make NL accept an encrypted connection at its IPv6 address. XHTTP carries the traffic, and REALITY protects that connection. Open **NL’s dashboard → Inbounds → Add Inbound** and enter:

| Field | Value |
|---|---|
| Remark | `Relay nl` |
| Listen IP | NL’s assigned IPv6 address, without brackets or the `/prefix` |
| Port | `443`, if free |
| Protocol | `vless` |
| Transmission / Network | `XHTTP` |
| Path | `/relay-nl` |
| Mode | `auto` |
| Security | `REALITY` |
| Target / Dest | `www.google.com:443` |
| Server Names / SNI | `www.google.com` |
| Fingerprint, if offered | `chrome` |

Generate the REALITY keys and a short ID for this new inbound. Keep their generated values; the exported link will include what Moscow needs. Add a client named **relay-nl** and leave **Flow empty**. XHTTP doesn’t use the Vision flow in this setup. Save the inbound. [Where the fields are](server-inbound.md#3-set-transport-and-security)

**2. Choose how NL reaches websites.** NL receives the VPN over IPv6, but we want its website connections to use IPv4. That gives us the IPv4 exit address used by the checks later. An **outbound** is the path traffic takes when leaving a server. Open **Outbounds → direct → Edit → Strategy**, choose **ForceIPv4**, and save. [The IPv4 setting explained](force-ipv4.md)

**3. Restrict this relay to Moscow.** This account is meant to carry traffic from your Moscow server. We’ll let that IPv6 source reach websites, block other sources, and reject IPv6 website destinations so the relay keeps its IPv4 exit.

In **Routing**, use the **+** button to add these rules. Select only the new relay under **Inbound Tags**. The tag identifies the inbound in routing; keep the tag assigned by your panel.

| Order | Other match fields | Outbound Tag |
|---|---|---|
| First relay rule | Destination IP: `::/0` | `blocked` |
| Second relay rule | Source IP: Moscow’s global IPv6 address followed by `/128` | `direct` |
| Third relay rule | No other match fields | `blocked` |

The first rule rejects explicitly requested IPv6 destinations, so this relay exits through IPv4. The second lets Moscow through. The last blocks other sources from getting an exit through this account. `/128` means exactly one IPv6 address. Keep the panel’s API rule and unrelated rules, and put this group above broader rules that could catch the same traffic. Use the existing blocked/blackhole outbound; if your panel uses another tag for it, select that tag.

**4. Start the receiving connection.** The saved settings don’t accept traffic until the inbound is enabled. Enable the inbound, apply the settings and restart Xray if prompted. Check that it shows **Running**. We’ll test reachability below; if that test fails, use [the connection checks](troubleshooting.md#ping-works-so-test-the-vpn-port-next).

**5. Copy the relay link.** Moscow needs the account and security settings you just created. The link carries them together so you don’t have to retype the keys. In **Inbounds**, expand **Relay nl**, find **relay-nl**, and open **Info / Share**. Copy its VLESS link and keep it private. The address after `@` should be NL’s IPv6 address in brackets, followed by `:443`. If the panel exports IPv4, try opening the dashboard using its IPv6 browser URL, `http://[NL_IPV6]:PANEL_PORT/PANEL_PATH/`, then export again. Use your actual port, path and HTTP/HTTPS scheme. Check that the export now contains IPv6 before continuing.

NL is ready to receive the second VPN connection. Keep its relay link available; we’ll give it to Moscow next.

### On Moscow, connect the device inbound to NL

**1. Create the sending end of VPN 2.** NL is ready to receive a connection. Now Moscow needs to know how to open it. We’ll import the relay link to copy NL’s address, account and keys into a Moscow outbound.

Open **Outbounds → + Outbounds → JSON**. Paste the relay link into the link field and click **Import**. Before saving, check:

| Field | Value |
|---|---|
| Tag | `relay-nl` |
| Server address | NL’s IPv6 address |
| Port | NL’s relay port, `443` in this example |
| Transport | `xhttp` |
| Path | `/relay-nl` |
| Mode | `stream-one` |
| Flow | Empty |
| SNI / fingerprint | `www.google.com` / `chrome` |

NL’s access rule expects Moscow’s assigned IPv6 address. To make the outgoing connection use that same source, we’ll set two fields in the imported outbound. **JSON** is the text form of those settings.

In that outbound’s existing JSON, set top-level **`sendThrough`** to Moscow’s global IPv6 address, and **`streamSettings.sockopt.domainStrategy`** to **`ForceIPv6`**. Merge those fields into the existing objects rather than pasting a second outbound or deleting its imported credentials. `sendThrough` makes the connection use the same Moscow source address allowed by NL’s rule. Save with **Create**.

**2. Create the receiving end of VPN 1.** Your phone needs its own connection to Moscow. This uses IPv4, so your phone’s network doesn’t need IPv6. We’ll create the entry now and keep it disabled until its route to NL is ready. In **Inbounds → Add Inbound**, use these values:

| Field | Value |
|---|---|
| Remark | `VLESS RU` |
| Listen IP | Moscow’s assigned IPv4 address |
| Port | `443`, if free |
| Protocol / transport | `vless` / `RAW` or `TCP` |
| Security | `REALITY` |
| Target / SNI | `yandex.ru:443` / `yandex.ru` |
| Fingerprint | `safari` |

Generate separate REALITY keys and a short ID for this new inbound. Add clients **desktop** and **phone**, each with its own generated UUID and **Flow → xtls-rprx-vision**. Keep **Enable off** while adding the routing rule. Save. [Device fields explained](server-inbound.md#4-set-the-client-account)

**3. Connect VPN 1 to VPN 2.** Moscow now has a device entry and a foreign outbound, but it needs a rule joining them. Without that rule, the new entry isn’t assigned to the intended foreign connection. Open **Routing → +**. Under **Inbound Tags**, select the new **VLESS RU** inbound. Under **Outbound Tag**, select **relay-nl**. Leave the other match fields empty. Put this rule above general rules that could match the same traffic; keep the panel’s API rule. Save and apply.

**4. Start the device connection.** Its route to NL is now saved, so it is ready to accept traffic. Enable **VLESS RU**, apply, and check Xray is **Running**.

**5. Give Hiddify the settings for VPN 1.** Your phone connects to Moscow; Moscow already holds the settings for VPN 2. We’ll export the Moscow device accounts for Hiddify. Expand the Moscow inbound and open **Info / Share** for **phone**, then **desktop**. Each export should use Moscow’s public IPv4 and port 443. Save each original link privately. For this **26.7.28** entry, add **`&keyshare=classical`** immediately before `#` in each link; if `keyshare=` already exists, change its value instead of duplicating it. [Text-edit example](server-inbound.md#5-export-the-connection)

Those adjusted Moscow links go into Hiddify. The NL relay link stays on Moscow. **Manual setup is done:** skip the optional script section and [test your device](#4-verify-the-complete-device-path).

[Connection maps](schemes/README.md) · [Real screenshots to capture](../images/README.md#screenshots-to-send-in-order)

## 3. Preview and apply the relay helper

<details>
<summary>Open the commands for the same two-server setup</summary>

Download the repository and open a terminal in it using [these preparation steps](quick-start.md#before-the-first-command). This optional helper needs Python 3.8+ and native OpenSSH on your computer. The existing Windows single-server launcher still works without local Python. The servers need Python 3, supported Ubuntu/Debian and systemd.

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
  --exit-core-version 26.7.28 \
  --entry-key-share classical \
  --relay-transport xhttp \
  --clients desktop,phone \
  --plan
```

**`--clients desktop,phone` is the list of VPN account names to create on Moscow.** Those are example labels; choose names such as `alex,anna,laptop` for three accounts. Separate them with commas, without spaces. Each gets its own credentials and a link saved as **NAME.txt**, for example **alex.txt**. [Naming rules](automation.md#choose-the-vpn-account-names)

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

A fresh panel's generated credentials are in the private relay.json result. Open its printed public HTTP panel URL directly in a browser, as described in the [panel guide](server-setup.md#open-the-dashboard-in-your-browser).

The helper’s IPv6 check does not configure provider networking. If it fails there, complete section 1 manually before retrying.

### Explicit management access through an existing proxy

The helper normally connects directly to each server over SSH. If you deliberately want to administer one through an existing HTTP proxy on your computer, pass its address explicitly:

```text
--exit-ssh-proxy 127.0.0.1:10801
```

There is a separate `--hub-ssh-proxy` option. These are explicit loopback proxy endpoints, not root-password arguments. The helper keeps its own SSH connections separate from old multiplexed sessions.

**This proxy is only for the setup connection.** After deployment, Moscow talks to the foreign server over its own IPv6 connection. Your phone doesn’t need your computer or its proxy to stay on.

</details>

## 4. Verify the complete device path

On your phone or computer, copy the full **Moscow device** link. Open Hiddify and choose **+ → Clipboard**, select the new profile, then tap **Connect**. On desktop, choose **Settings → Inbound → Service mode → VPN / TUN** to route ordinary apps. Accept the VPN permission prompt if shown. [Hiddify walkthrough](clients.md)

Open a website and then open the IP check page. The `ip=` line should show **NL’s IPv4 address**. If it shows your usual address or another VPN’s exit, check the selected profile, Hiddify’s service mode and the system proxy. If the page times out, test the device-to-Moscow port and the Moscow-to-NL relay separately. [IP check page](https://www.cloudflare.com/cdn-cgi/trace) · [Troubleshooting](troubleshooting.md)

**Your two-server setup is finished when your device opens websites and shows the foreign exit address. You can stop here.** The next section is optional: use it only if you want another exit country and are ready to rent another foreign server.

Keep each owner’s credentials separate. A desktop and phone can share the same inbound but should have their own client accounts.

## 5. Optional: add another exit country

This adds a **third rented server**: a new foreign server in Finland (**FI**). Keep the existing Moscow and NL servers. Rent the FI server, configure its IPv6, then use route key `fi` and Moscow’s other allowed port, 8443.

The command below reuses Moscow and configures the new FI server; run it on your setup computer from the repository folder. It assumes the first country uses **Moscow port 443** and **8443 is free**. If the first country already uses 8443, set `--entry-port 443` instead, only if that port is free. Preserve existing listeners. The foreign server has its own ports; its relay port doesn’t have to equal Moscow’s entry port.

This is a script alternative to repeating the manual foreign-inbound and Moscow-outbound steps.

```bash
python3 scripts/bootstrap_relay.py \
  --hub-host 203.0.113.10 \
  --exit-host 198.51.100.30 \
  --exit-ipv6 2001:db8:3::1 \
  --route fi \
  --entry-port 8443 \
  --exit-port 8443 \
  --hub-core-version 26.7.28 \
  --exit-core-version 26.7.28 \
  --entry-key-share classical \
  --relay-transport xhttp \
  --clients desktop,phone \
  --plan
```

Apply only after that foreign server's IPv6 is configured. The helper reuses Moscow's panel, attaches existing owner accounts without rotating their UUIDs, and adds a separate inbound-to-outbound rule for the new country. It preserves the first country's route.

With one public IPv4 address and this separate-listener design, 8443 and 443 provide **two country entry points**. More countries can share an existing inbound with [Xray user routing](https://xtls.github.io/en/config/routing#ruleobject). Give each device/country combination a distinct account, such as `desktop` for NL and `FR-desktop` for FR, and route its account label to the corresponding foreign outbound. Put the account-specific rules above the inbound's general rule. For FR, first rent another foreign server in France and configure its IPv6. Keep the existing Moscow, NL and FI servers. The helper supports the shared-port layout through `--shared-entry`. For example, use `--route fr --entry-port 443 --shared-entry --clients FR-desktop,FR-phone` with FR's server addresses. It checks the existing RAW entry and SNI, then inserts the account rule before the general NL rule. The new account labels must be distinct. Public entries still use only 443 and 8443.

Reapplying the same route with unchanged settings reuses it. A route key already bound to different settings is refused; do not delete its registry or reinstall the hub to force a change.

## What we verified

<details>
<summary>Read the recorded tests and version results</summary>


From the Moscow server, direct TCP to the foreign IPv4 SSH, VPN and panel ports timed out. The foreign IPv6 ports were reachable, and both the original foreign VPN over IPv6 and the new relay authenticated. The new path returned the foreign IPv4 exit. From a desktop, the complete chain passed six isolated Windows Hiddify HTTPS requests, two requests using Hiddify's actual VPN Connect button, and a separate UDP DNS request. The test watchdog then disconnected Hiddify and restored the previous Windows proxy settings. A second country's live route was not part of this test.

All four NL accounts passed HTTPS checks after moving Moscow’s entry to port 443. Hiddify’s Connect button passed two more checks on port 443. FI was added on port 8443, and all four FI device profiles returned the expected FI exit. FR now shares Moscow port 443 with NL. The FR account rule runs before the general NL rule for that inbound. All four FR profiles returned the expected FR exit in isolated Windows Hiddify checks. The NL and FI desktop profiles also returned their expected exits after FR was added.

A later live test switched the inter-server IPv6 links for NL, FR and FI to XHTTP + REALITY, using `stream-one` on Moscow’s outbounds and `auto` on the foreign inbounds. Each relay kept its existing address, port and account. XHTTP uses an empty client flow on that leg. All twelve device profiles passed isolated Windows Hiddify HTTPS requests through their expected exits, and UDP DNS passed through each XHTTP relay. Device entry uses RAW + REALITY + Vision. The helper defaults to this XHTTP relay. Select `--relay-transport raw` for the older RAW relay mode, whose relay account uses Vision flow.

The owner subsequently reported that the NL phone profile worked over mobile data when Moscow ran Xray 26.7.28 and Hiddify 5.5.5 used `keyshare=classical`. All three saved Windows desktop profiles were then updated to classical mode and each passed two HTTPS checks. Hiddify’s Connect button passed three further NL HTTPS checks. This is a version-specific result: classical key shares require a compatible server, and Xray 26.9.9 rejects them. Check the server version before changing this field. [Hiddify investigation and compatibility caveat](https://github.com/hiddify/hiddify-app/issues/2463#issuecomment-6750196534)

</details>

## Add another phone or computer

For another device using an existing country, make a new **device account on Moscow**. You don’t need another foreign relay account for every device.

Open Moscow’s **Inbounds**, find the device entry, and add a client with its own name and generated UUID. Keep Vision flow for the RAW entry. If that country uses a shared port and a user-specific routing rule, add the new account label to that country’s rule too. An account left out of the FR rule on shared port 443 would follow the general NL rule.

Export the new Moscow account, add the classical option for the compatible entry version, and [import it into Hiddify](clients.md). Test the exit country. Leave other users’ accounts and keys alone.

## Recovery and evidence

If you used the scripts, private server backups are under **/root/vpn-relay-backups**, and the local **relay.json** records completed stages and backup locations. The route registry is **/etc/vpn-guide-relay/routes.json**. If a run stopped, inspect its saved stage and disabled inbound before retrying; don’t erase the panel or registry to force it through.

For a manual change, keep a panel backup before editing an existing route. If the new route fails, disable its new device inbound and restore the settings you changed from that backup. Preserve other countries’ rules and accounts. [Checks for the first failing connection](troubleshooting.md)

IPv6 and a two-hop chain do not guarantee that a destination IP or prefix will remain reachable. Distinguish direct, proxy-assisted management, inter-server and final device tests. Record their actual exit addresses and keep live account links and keys out of the repository.

**Next:** [add your Moscow device link to Hiddify](clients.md).
